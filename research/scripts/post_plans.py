"""Publish the sprint plan of one sprint to the risk service (M14).

The plan (research/sprint_plan.py) says how many of the open issues will probably not finish, from the earlier sprints of
the project, and which ones to move to the next cycle. Each moved issue gets its diagnosis (one model call, verified) as
the reason; an issue that only follows a moved one says so. A person approves the plan in Plane.

Usage: PLANE_API_KEY=... RISK_INGEST_TOKEN=... [OPENROUTER_API_KEY=...] TAWOS_DSN=... \
       python scripts/post_plans.py scores.csv ISP SPRINT_ID [--demo]
By default the sprint's own Plane cycle (same name) and the cycle after it are used, which needs a sprint that has not
finished. --demo replays a past sprint as if it were running now: it makes two current cycles in Plane and puts the
sprint's open items in the first, because Plane refuses to move items into a finished cycle.
"""
import json
import os
import sys
import urllib.request
from datetime import date, timedelta

import pandas as pd
import psycopg

from app.services.diagnosis import diagnose
from app.services.http_retry import send
from app.services.openrouter_client import OpenRouterClient
from app.services.plane_api import plane
from research.alert_actions import next_cycle
from research.collectors import collect
from research.sprint_plan import history_rate, make_plan
from research.tawos_source import waits_on

RISK_URL = os.environ.get('RISK_URL', 'http://localhost:31081/api/v1/plans')
MARK = float(os.environ.get('MARK', .5))
scores_csv, identifier, sprint = sys.argv[1], sys.argv[2], int(sys.argv[3])
demo = '--demo' in sys.argv

db = psycopg.connect(os.environ.get('TAWOS_DSN', 'postgresql://tawos:tawos_local_dev@localhost:15432/tawos'))
scores = pd.read_csv(scores_csv)
scores = scores[(scores['mark'] == MARK) & scores['rank'].notna()]
snap = pd.read_parquet('data/processed/snapshots.parquet')
snap = snap[snap['landmark'] == MARK]
when = snap.groupby('sprint_id').agg(t=('prediction_at', 'first'), end=('end', 'first'))
t = when.loc[sprint, 't']
past = [(len(g), int(g['y'].sum())) for s, g in scores.groupby('sprint_id') if s != sprint and when.loc[s, 'end'] <= t]
rate = history_rate(past)
part = scores[scores['sprint_id'] == sprint]
p = dict(zip(part['issue_id'], part['p']))
blocked = {}
for i in p:
    with db.cursor() as cur:
        blocked[i] = {b['issue_id'] for b in waits_on(cur, int(i), t) if not b['resolved']} & set(p)
plan = make_plan(p, rate, blocked)
if plan is None:
    sys.exit(f'no plan: history {len(past)} sprints, rate {rate}, open {len(p)}')

project = next(x['id'] for x in plane('GET', '/projects/')['results'] if x['identifier'] == identifier)
P = f'/projects/{project}'
items, cursor = {}, None
while True:  # Plane work items by the TAWOS issue id they were imported from
    page = plane('GET', P + '/work-items/?per_page=100' + (f'&cursor={cursor}' if cursor else ''))
    items |= {w['external_id']: w for w in page['results'] if w.get('external_id')}
    if not page['next_page_results']:
        break
    cursor = page['next_cursor']

with db.cursor() as cur:
    cur.execute('select name from tawos_raw.sprint where id=%s', (sprint,))
    name = cur.fetchone()[0]
cycles = plane('GET', P + '/cycles/?per_page=500')['results']
if demo:
    today = date.today()
    live = {}
    for label, start, end in (('now', -5, 5), ('next', 6, 16)):
        cname = f'Replay of {name} ({label})'
        c = next((c for c in cycles if c['name'] == cname), None) or plane('POST', P + '/cycles/', {
            'name': cname, 'start_date': str(today + timedelta(days=start)), 'end_date': str(today + timedelta(days=end))})
        live[label] = c['id']
    plane('POST', P + f"/cycles/{live['now']}/cycle-issues/", {'issues': [items[str(i)]['id'] for i in p if str(i) in items]})
    cycle_id, next_id = live['now'], live['next']
else:
    cycle_id = next((c['id'] for c in cycles if c['name'] == name), None)
    next_id = next_cycle(cycles, cycle_id, date.today()) if cycle_id else None
    if not (cycle_id and next_id):
        sys.exit(f'sprint {name!r} has no Plane cycle that can still be moved from (or no running cycle after it)')

agent = OpenRouterClient(model=os.environ.get('OPENROUTER_MODEL', 'openai/gpt-6-luna'), budget=.5) \
    if os.environ.get('OPENROUTER_API_KEY') else None
row = snap.set_index(['sprint_id', 'issue_id'])
out, keys = [], {}
for issue, why in plan['move']:
    with db.cursor() as cur:
        cur.execute('select issue_key, title from tawos_raw.issue where id=%s', (int(issue),))
        key, title = cur.fetchone()
    keys[issue] = key
    cause = reason = None
    if why == 'risk' and agent:
        r = row.loc[(sprint, int(issue))]
        card, _ = diagnose(agent, key, title or '', r['dynamic_status'], float(r['dynamic_inactive_days']),
                           collect(db.cursor(), int(issue), t))
        if card['hypotheses']:
            cause, reason = card['hypotheses'][0]['cause'], card['hypotheses'][0]['reason']
    elif why == 'follows':
        waits = sorted(keys[b] for b in blocked[issue] if b in keys)
        reason = f"It waits on {', '.join(waits)}, which {'is' if len(waits) == 1 else 'are'} in this plan."
    out.append(dict(work_item_id=items[str(issue)]['id'], issue_key=key, score=float(p[issue]), why=why,
                    cause=cause, reason=reason))
body = dict(project_id=project, cycle_id=cycle_id, next_cycle_id=next_id, sprint_name=name, mark=MARK,
            open_count=len(p), history_sprints=len(past), unfinished_share=rate,
            expected_unfinished=plan['expected_unfinished'], budget=plan['budget'], items=out)
req = urllib.request.Request(RISK_URL, method='PUT', data=json.dumps(body).encode(), headers={
    'Authorization': f"Bearer {os.environ['RISK_INGEST_TOKEN']}", 'Content-Type': 'application/json'})
with send(req) as r:
    print('plan stored:', json.load(r), '| sprint', name, '| open', len(p), '| share', round(rate, 2),
          '| budget', plan['budget'], '| moved', len(out))
if agent:
    print('model cost USD', round(agent.spent, 5))
