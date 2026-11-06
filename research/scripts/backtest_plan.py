"""Replay the sprint plan on every past sprint of the scores file and compare it with what happened (M14).

For each sprint, at one mark: the share of unfinished issues comes only from sprints that had already ended by then, the
plan moves the riskiest issues (plus those waiting on them), and the outcome column y says what really happened.
Usage: TAWOS_DSN=... python scripts/backtest_plan.py scores.csv [out.json]   (MARK=0.5 by default)
"""
import json
import os
import sys

import pandas as pd
import psycopg

from research.sprint_plan import history_rate, make_plan
from research.tawos_source import waits_on

MARK = float(os.environ.get('MARK', .5))
scores = pd.read_csv(sys.argv[1])
scores = scores[(scores['mark'] == MARK) & scores['rank'].notna()]  # open, not cancelled
snap = pd.read_parquet('data/processed/snapshots.parquet')
when = snap[snap['landmark'] == MARK].groupby('sprint_id').agg(t=('prediction_at', 'first'), end=('end', 'first'))
rows, history = [], []  # history: (end, open, unfinished) of sprints already replayed
with psycopg.connect(os.environ['TAWOS_DSN']) as db:
    for sprint, t in when['t'].sort_values().items():
        part = scores[scores['sprint_id'] == sprint]
        if part.empty:
            continue
        n, unfinished = len(part), int(part['y'].sum())
        rate = history_rate([(o, u) for end, o, u in history if end <= t])
        history.append((when.loc[sprint, 'end'], n, unfinished))
        if rate is None:
            continue
        p = dict(zip(part['issue_id'], part['p']))
        y = dict(zip(part['issue_id'], part['y']))
        blocked = {}
        for i in p:
            with db.cursor() as cur:
                blocked[i] = {b['issue_id'] for b in waits_on(cur, int(i), t) if not b['resolved']} & set(p)
        plan = make_plan(p, rate, blocked)
        moved = plan['move'] if plan else []
        risk = [i for i, why in moved if why == 'risk']
        rows.append(dict(sprint=int(sprint), open=n, unfinished=unfinished, expected=round(rate * n, 2),
                         moved=len(moved), by_risk=len(risk), follows=len(moved) - len(risk),
                         moved_unfinished=int(sum(y[i] for i, _ in moved)), risk_unfinished=int(sum(y[i] for i in risk)),
                         follows_unfinished=int(sum(y[i] for i, why in moved if why == 'follows'))))
d = pd.DataFrame(rows)
fin = lambda a, b: round(float(a) / float(b), 3) if b else None  # noqa: E731
summary = dict(
    mark=MARK, sprints_replayed=len(d), sprints_with_a_plan=int((d['moved'] > 0).sum()),
    open_issues=int(d['open'].sum()), unfinished=int(d['unfinished'].sum()),
    base_rate=fin(d['unfinished'].sum(), d['open'].sum()),
    expected_vs_actual_mae=round(float((d['expected'] - d['unfinished']).abs().mean()), 3),
    expected_vs_actual_bias=round(float((d['expected'] - d['unfinished']).mean()), 3),
    precision_moved_by_risk=fin(d['risk_unfinished'].sum(), d['by_risk'].sum()),
    precision_followers=fin(d['follows_unfinished'].sum(), d['follows'].sum()),
    recall_of_unfinished=fin(d['moved_unfinished'].sum(), d['unfinished'].sum()),
    moved_issues=int(d['moved'].sum()), followers=int(d['follows'].sum()),
    sprints_moving_more_than_actually_unfinished=int((d['moved'] > d['unfinished']).sum()),
)
print(json.dumps(summary, indent=1))
if len(sys.argv) > 2:
    open(sys.argv[2], 'w').write(json.dumps(dict(summary=summary, sprints=rows), indent=1))
