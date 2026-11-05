"""Load one scored TAWOS project into Plane: cycles, work items (state as of the 50% landmark) and an alert label.

Usage: PLANE_API_KEY=... TAWOS_PG_PASSWORD=... python scripts/import_to_plane.py scores.csv "IS heldout pilot" ISP
The outcome column `y` is never sent to Plane. Not idempotent: a failed run leaves a partial Plane project to delete.
Plane project names allow no special characters (no hyphen or parentheses).
"""
import csv
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

from tawos_text import to_html

BASE = os.environ.get('PLANE_URL', 'http://localhost:31080/api/v1/workspaces/ript')
KEY = os.environ['PLANE_API_KEY']
scores_csv, name, identifier = sys.argv[1:4]
STATE = {'done': 'Done', 'complete': 'Done', 'invalid': 'Cancelled', 'to do': 'Todo', 'to develop': 'Todo', 'new': 'Todo',
         'in progress': 'In Progress', 'validate': 'In Progress', 'review': 'In Progress', 'code review': 'In Progress',
         'in review': 'In Progress', 'to test': 'In Progress', 'design': 'In Progress'}  # unknown -> Backlog
PRIO = {'Blocker': 'urgent', 'Critical': 'urgent', 'Major': 'high', 'Minor': 'low', 'Trivial': 'low'}


def call(method, path, body=None):
    req = urllib.request.Request(BASE + path, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={'X-API-Key': KEY, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f'{method} {path} -> {e.code} {e.read()[:300]}')


def tawos(sql):
    out = subprocess.run(['docker', 'exec', '-e', f"PGPASSWORD={os.environ['TAWOS_PG_PASSWORD']}", os.environ.get('TAWOS_DB_CONTAINER', 'research-db-1'), 'psql', '-U', 'tawos',
                          '-d', 'tawos', '-Atc', f'select coalesce(json_agg(t),\'[]\') from ({sql}) t'],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


rows = list(csv.DictReader(open(scores_csv)))
sprints = {str(int(r['sprint_id'])) for r in rows}  # int(): ids reach SQL below
meta = {str(s['id']): s for s in tawos(f"select id,name,start_date::date sd,end_date::date ed from tawos_raw.sprint "
                                       f"where id in ({','.join(sprints)})")}
issues = {str(i['id']): i for i in tawos(f"select id,issue_key,title,type,priority,description_text,url from tawos_raw.issue "
                                         f"where id in ({','.join({str(int(r['issue_id'])) for r in rows})})")}
assert sprints <= meta.keys(), 'sprint ids in scores must exist in TAWOS'

project = call('POST', '/projects/', {'name': name, 'identifier': identifier, 'cycle_view': True})['id']
P = f'/projects/{project}'
states = {s['name']: s['id'] for s in call('GET', P + '/states/')['results']}
label = call('POST', P + '/labels/', {'name': 'risk-alert', 'color': '#e5484d'})['id']
# Plane locks finished cycles: create in the future, attach issues, backdate last.
cycles = {s: call('POST', P + '/cycles/', {'name': meta[s]['name'], 'start_date': '2099-01-01', 'end_date': '2099-02-01',
                                           'external_source': 'tawos', 'external_id': s})['id'] for s in sorted(sprints)}
# shortcut: a work item sits in one Plane cycle, so a carried-over issue keeps only its latest sprint's score.
latest = {}
for r in sorted(rows, key=lambda r: meta[r['sprint_id']]['sd']):
    latest[r['issue_id']] = r
by_cycle = {}
for r in latest.values():
    i = issues[r['issue_id']]
    alert = r['alert'] == 'True'
    note = to_html(i['description_text'], i['issue_key'])
    w = call('POST', P + '/work-items/', {
        'name': f"[{i['issue_key']}] {i['title']}"[:255], 'description_html': note,
        'state': states[STATE.get(r['dynamic_status'], 'Backlog')], 'priority': PRIO.get(i['priority'], 'medium'),
        'labels': [label] if alert else [], 'external_source': 'tawos', 'external_id': r['issue_id']})
    by_cycle.setdefault(cycles[r['sprint_id']], []).append(w['id'])
for cid, ids in by_cycle.items():
    call('POST', P + f'/cycles/{cid}/cycle-issues/', {'issues': ids})
for s, cid in cycles.items():
    call('PATCH', P + f'/cycles/{cid}/', {'start_date': meta[s]['sd'], 'end_date': meta[s]['ed']})
print(len(cycles), 'cycles,', len(latest), 'work items,', sum(r['alert'] == 'True' for r in latest.values()), 'alerted')
