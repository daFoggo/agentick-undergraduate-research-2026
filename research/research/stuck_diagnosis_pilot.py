"""Small pilot of the stuck-cause agent (app/services/stuck_diagnosis.py) on real alerts that have comments.

Usage: python -m research.stuck_diagnosis_pilot alerts.csv      (env: PILOT_N=30, PILOT_MODEL, PILOT_OUT, PILOT_BUDGET_USD)
Writes artifacts/stuck_diagnosis_pilot/{summary.json,rating_sheet.csv}. No human labels exist for "why it is stuck",
so the sheet is for a person to rate; the summary only reports what a machine can check.
"""
import json
import os
import sys
from collections import Counter
from pathlib import Path

import pandas as pd
import psycopg

from app.services.openrouter_client import OpenRouterClient
from app.services.stuck_agent import run_agent
from research.tawos_source import TawosSource
from app.services.stuck_diagnosis import diagnose, keyword_cause

SEED = 20261105
N = int(os.environ.get('PILOT_N', 30))
MODEL = os.environ.get('PILOT_MODEL', 'openai/gpt-6-luna')
OUT = Path(os.environ.get('PILOT_OUT', 'artifacts/stuck_diagnosis_pilot'))
MODE = os.environ.get('PILOT_MODE', 'single')  # single: one call with the context; agent: tool loop
# assumption, not verified: in the export a link row appears from both sides; these two read as "this issue is blocked"
BLOCKING = {('Blocks', 'INBOUND'): 'blocked by', ('Depends', 'OUTBOUND'): 'depends on'}


def facts_for(cur, r, cut):
    cur.execute("select issue_key, description_text from tawos_raw.issue where id=%s", (r.issue_id,))
    key, desc = cur.fetchone()
    cur.execute("select comment_text from tawos_raw.comment where issue_id=%s and creation_date<=%s "
                "order by creation_date desc limit 5", (r.issue_id, cut))
    comments = [c[0] or '' for c in cur.fetchall()][::-1]
    cur.execute("select l.name, l.direction, t.issue_key, t.resolution_date from tawos_raw.issue_link l "
                "join tawos_raw.issue t on t.id=l.target_issue_id where l.issue_id=%s and l.name in ('Blocks','Depends')",
                (r.issue_id,))
    links = [dict(key=k, kind=BLOCKING[(n, d)], resolved=bool(rd and rd <= cut))
             for n, d, k, rd in cur.fetchall() if (n, d) in BLOCKING]
    return dict(key=key, description=desc or '', comments=comments, links=links)


def main():
    alerts = pd.read_csv(sys.argv[1])
    alerts = alerts[alerts.alert]
    snap = pd.read_parquet('data/processed/snapshots.parquet').set_index(['landmark', 'sprint_id', 'issue_id'])
    rows, items = [], []
    with psycopg.connect(os.environ.get('RESEARCH_DATABASE_URL',
                                        'postgresql://tawos:tawos_local_dev@localhost:15990/tawos')) as con:
        cur = con.cursor()
        for r in alerts.itertuples():
            row = snap.loc[(r.mark, r.sprint_id, r.issue_id)]
            f = facts_for(cur, r, row['prediction_at'])
            if f['comments']:
                items.append(dict(f, status=row['dynamic_status'], inactive_days=float(row['dynamic_inactive_days']),
                                  mark=float(r.mark), cutoff=row['prediction_at']))
    items = pd.DataFrame(items).sample(n=min(N, len(items)), random_state=SEED).to_dict('records')
    client = OpenRouterClient(model=MODEL, budget=float(os.environ.get('PILOT_BUDGET_USD', .05)))
    con2 = psycopg.connect(os.environ.get('RESEARCH_DATABASE_URL', 'postgresql://tawos:tawos_local_dev@localhost:15990/tawos'))
    tool_calls, traces = Counter(), []
    agent_causes, key_causes, cost, ungrounded, graded, agree = Counter(), Counter(), 0.0, 0, 0, 0
    for f in items:
        if MODE == 'agent':
            res, meta = run_agent(client, f, TawosSource(con2.cursor(), f['cutoff']))
            traces.append(dict(issue=f['key'], trace=meta['trace'], incomplete=meta['incomplete'], reason=meta['reason']))
            tool_calls.update(t['tool'] for t in meta['trace'])
        else:
            res, meta = diagnose(client, f)
        base = keyword_cause(f['comments'])
        cost += meta['cost']
        agent_causes[res['cause']] += 1
        key_causes[base] += 1
        agree += res['cause'] == base
        if meta.get('quote_grounded') is not None:
            graded += 1
            ungrounded += not meta['quote_grounded']
        rows.append(dict(issue=f['key'], mark=f['mark'], status=f['status'], inactive=round(f['inactive_days'], 1),
                         comments=' || '.join(c[:200] for c in f['comments']),
                         links='; '.join(f"{x['kind']} {x['key']}{' (resolved)' if x['resolved'] else ''}" for x in f['links']),
                         agent_cause=res['cause'], agent_quote=res.get('quote'), agent_blocker=res.get('blocker_key'),
                         agent_text=res.get('action_text'), source=meta['source'], keyword_cause=base,
                         human_cause_ok='', human_text_ok=''))
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / 'rating_sheet.csv', index=False)
    summary = dict(n=len(items), model=MODEL, cost_usd=cost, agent_causes=dict(agent_causes),
                   keyword_causes=dict(key_causes), agent_coverage=1 - agent_causes['no_signal'] / len(items),
                   keyword_coverage=1 - key_causes['no_signal'] / len(items), same_cause_as_keywords=agree / len(items),
                   quotes_checked=graded, quotes_invented_by_model=ungrounded, mode=MODE,
                   tool_calls=dict(tool_calls), unfinished_runs=sum(t['incomplete'] for t in traces))
    if traces:
        (OUT / 'traces.json').write_text(json.dumps(traces, indent=1), encoding='utf-8')
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
