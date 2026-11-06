"""Post a readable brief as a Plane comment on every risk-alert work item of one project.
A work item that scores no longer flag (cancelled, done, or out of the sprint's alert cap) is retired: label removed, the
bot's brief deleted, the stored alert dropped unless a person already decided on it.

The brief is a template over a diagnosis card: hypotheses about why the item is at risk, each with the events that back
it (collected up to the alert time, research/collectors.py), what is still unknown, and one proposed action. One LLM call
(OPENROUTER_MODEL, default openai/gpt-6-luna, spend capped by AGENT_BUDGET_USD) writes the hypotheses; code drops those
without real event ids (app/services/diagnosis.py). Without a key or with AGENT=0 the card says "unknown" and the rules
choose the action. Each alert is also published to the risk service, which feeds the Approve / Dismiss / Undo card.
Re-running replaces earlier briefs (deleted with PLANE_API_KEY, posted with PLANE_BOT_KEY if set) and overwrites the alerts.
DUMP_INPUTS=path.jsonl also writes, per alert, the events the model saw and the card it returned (see eval_diagnosis.py).
Usage: PLANE_API_KEY=... [PLANE_BOT_KEY=...] RISK_INGEST_TOKEN=... [RESEARCH_DATABASE_URL=...] \
       python scripts/post_briefs.py scores.csv ISP [limit]
"""
import csv
import html
import json
import os
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import date, timezone

import pandas as pd
import psycopg

from app.services.brief import final_action, why
from app.services.diagnosis import diagnose
from app.services.http_retry import send
from app.services.openrouter_client import OpenRouterClient
from app.services.plane_api import plane
from research.alert_actions import choose_action, next_cycle
from research.collectors import collect, notes

KEY = os.environ['PLANE_API_KEY']
BOT_KEY = os.environ.get('PLANE_BOT_KEY', KEY)
RISK_URL = os.environ.get('RISK_URL', 'http://localhost:31081/api/v1/alerts')
MARK = 'Sprint risk alert'
OLD_MARKS = (MARK, 'Cảnh báo rủi ro sprint', 'Sprint-risk brief')  # earlier briefs are replaced too
research_db = psycopg.connect(os.environ.get('RESEARCH_DATABASE_URL', 'postgresql://tawos:tawos_local_dev@localhost:15432/tawos'))
scores_csv, identifier = sys.argv[1], sys.argv[2]
limit = int(sys.argv[3]) if len(sys.argv) > 3 else None

# Changelog fields a reader can interpret; the rest (Rank, Workflow, Link, ...) is noise. Assignee values are
# anonymised ids, so only the fact of the change is shown.
FIELDS = {'status': 'Status', 'Sprint': 'Sprint', 'Story Points': 'Story points', 'priority': 'Priority',
          'resolution': 'Resolution', 'assignee': 'Assignee'}


def tawos(sql):
    cur = research_db.cursor()
    cur.execute(sql)
    cols = [d.name for d in cur.description]
    return [dict(zip(cols, row)) for row in cur.fetchall()]


def change_line(e):
    when = pd.Timestamp(e['ts']).strftime('%Y-%m-%d %H:%M')
    if e['field'] == 'assignee':
        return f"{when} — Assignee changed"
    before, after = e['from_string'] or '(empty)', e['to_string'] or '(empty)'
    return f"{when} — {FIELDS[e['field']]}: {before} → {after}"


def retire(w, label_id):
    """The latest scores no longer flag this work item: drop the label and the bot's brief, then the stored alert."""
    if not w['labels'] or label_id not in w['labels']:
        return
    for old in plane('GET', P + f"/work-items/{w['id']}/comments/")['results']:
        if any(m in old['comment_html'] for m in OLD_MARKS):
            plane('DELETE', P + f"/work-items/{w['id']}/comments/{old['id']}/")
    plane('PATCH', P + f"/work-items/{w['id']}/", {'labels': [x for x in w['labels'] if x != label_id]})
    req = urllib.request.Request(f"{RISK_URL}/{w['id']}", method='DELETE',
                                 headers={'Authorization': f"Bearer {os.environ['RISK_INGEST_TOKEN']}"})
    try:
        send(req)
    except urllib.error.HTTPError as e:
        if e.code != 409:  # 409 = a person already decided on it: the alert stays
            raise
    global retired
    retired += 1


PROPOSED = {'raise_priority': 'raise the priority to High.',
            'nudge_owner': 'post a reminder asking for a status update (its text is on the alert card).',
            'move_next_cycle': 'move it to the next cycle, since little of this one is left.'}


def render(r, size, status, inactive, events, action, card, sprint_note):
    changes = ''.join(f'<li>{html.escape(change_line(e))}</li>' for e in events) or \
        '<li>No changes were recorded before that point.</li>'
    sprint = f'<li>Sprint: {html.escape(sprint_note)}</li>' if sprint_note else ''
    return (
        f"<p><b>{MARK}</b> — this item is among the ones worth a look early in the sprint.</p>"
        f"<p>Ranked <b>{int(float(r['rank']))} of {size}</b> by risk score among the open items of the sprint "
        f"(score {float(r['p']):.2f}, scale 0–1), measured when {float(r['mark']):.0%} of the sprint had passed. "
        "This is a hint about where to look first, not a statement that the item will be late.</p>"
        f"<p><b>What was observed</b></p><ul><li>Status at that time: {html.escape(status)}</li>"
        f"<li>No recorded activity for {inactive:.1f} days</li>{sprint}</ul>"
        f"{why(card)}"
        f"<p><b>Latest changes before that point</b></p><ul>{changes}</ul>"
        f"<p><b>Proposed action:</b> {PROPOSED[action['action_type']]} Use <b>Approve</b> or <b>Dismiss</b> on the "
        "alert card at the top of the item; it can be undone. Nothing changes until you click.</p>")


project = next(p['id'] for p in plane('GET', '/projects/')['results'] if p['identifier'] == identifier)
P = f'/projects/{project}'
label = next(label['id'] for label in plane('GET', P + '/labels/')['results'] if label['name'] == 'risk-alert')
rows = list(csv.DictReader(open(scores_csv)))
sprints = tawos("select id,name,end_date::date ed from tawos_raw.sprint where id in (%s)" % ','.join(
    str(int(x)) for x in {r['sprint_id'] for r in rows}))
sprint_end = {str(s['id']): s['ed'] for s in sprints}
cycles = plane('GET', P + '/cycles/?per_page=500')['results']  # a sprint is a Plane cycle of the same name
cycle_of_sprint = {str(s['id']): next((c['id'] for c in cycles if c['name'] == s['name']), None) for s in sprints}
sprint_size = Counter((r['sprint_id'], r['mark']) for r in rows if r['rank'])  # ranked = open and not cancelled
# same "latest sprint wins" rule as import_to_plane.py: a Plane work item sits in one cycle.
latest = {}
for r in sorted(rows, key=lambda r: (sprint_end[r['sprint_id']], r['alert'] == 'True')):
    latest[r['issue_id']] = r  # within one sprint the row that raised the alert wins
# every work item that now scores as an alert, plus every one that still carries the label (to retire it)
items, cursor = [], None
while True:
    page = plane('GET', P + '/work-items/?per_page=100' + (f'&cursor={cursor}' if cursor else ''))
    items += [w for w in page['results']
              if label in w['labels'] or latest.get(w.get('external_id'), {}).get('alert') == 'True']
    if not page['next_page_results']:
        break
    cursor = page['next_cursor']
items = items[:limit]
snap = pd.read_parquet('data/processed/snapshots.parquet')
snap = snap.set_index(['landmark', 'sprint_id', 'issue_id'])
field_list = ','.join(f"'{f}'" for f in FIELDS)

posted = retired = 0
published = []
MODEL = os.environ.get('OPENROUTER_MODEL', 'openai/gpt-6-luna')
try:  # the model is on by default; without a key, or with AGENT=0, the card says unknown and the rules choose
    agent = None if os.environ.get('AGENT') == '0' else OpenRouterClient(
        model=MODEL, budget=float(os.environ.get('AGENT_BUDGET_USD', .5)))
except Exception as exc:
    print('agent off, rules only:', exc)
    agent = None
agent_stats, agent_cost = Counter(), 0.0
DUMP = open(os.environ['DUMP_INPUTS'], 'w', encoding='utf-8') if os.environ.get('DUMP_INPUTS') else None
for w in items:
    r = latest[w['external_id']]
    if r['alert'] != 'True':
        retire(w, label)
        continue
    if label not in w['labels']:  # newly flagged: the cap now reaches it because ineligible issues left the ranking
        plane('PATCH', P + f"/work-items/{w['id']}/", {'labels': w['labels'] + [label]})
    sprint_id, issue_id = int(r['sprint_id']), int(r['issue_id'])
    mark = float(r['mark'])
    row = snap.loc[(mark, sprint_id, issue_id)]
    cutoff = row['prediction_at'].tz_convert(timezone.utc) if row['prediction_at'].tzinfo else row['prediction_at']
    events = tawos(
        f"select id,field,from_string,to_string,creation_date as ts from tawos_raw.change_log where issue_id={issue_id} "
        f"and field in ({field_list}) and creation_date <= '{cutoff.isoformat()}' order by creation_date desc limit 3")
    inactive, p = float(row['dynamic_inactive_days']), float(r['p'])
    for old in plane('GET', P + f"/work-items/{w['id']}/comments/")['results']:
        if any(m in old['comment_html'] for m in OLD_MARKS):
            plane('DELETE', P + f"/work-items/{w['id']}/comments/{old['id']}/")
    key = w['name'].split(']')[0].lstrip('[')
    cycle_id = cycle_of_sprint.get(r['sprint_id'])
    next_id = next_cycle(cycles, cycle_id, date.today()) if cycle_id else None
    action = choose_action(key, row['dynamic_status'], inactive, mark, cycle_id, next_id)
    card = dict(hypotheses=[], dropped=0, unknown=True, missing_info=None, action=dict(type=None, text=None))
    evidence = collect(research_db.cursor(), issue_id, cutoff)
    card['notes'] = notes(research_db.cursor(), issue_id, cutoff, evidence)
    if agent:
        title = tawos(f"select title from tawos_raw.issue where id={issue_id}")[0]['title'] or ''
        card, meta = diagnose(agent, key, title, row['dynamic_status'], inactive, evidence, can_move=bool(next_id))
        card['meta'] = dict(model=MODEL, cost=meta['cost'], error=meta['error'])
        agent_stats['unknown' if card['unknown'] else card['hypotheses'][0]['cause']] += 1
        agent_cost += meta['cost']
        if meta['error']:
            print('diagnosis failed', key, meta['error'])
        action = final_action(action, card)
        if DUMP:  # exactly what the model saw and what it answered, for scripts/eval_diagnosis.py
            DUMP.write(json.dumps(dict(key=key, title=title, status=row['dynamic_status'], inactive=inactive,
                                       events=evidence, card=card), default=str, ensure_ascii=False) + '\n')
    sprint_note = next((e['text'] for e in evidence if e['kind'] == 'sprint'), '')
    brief = plane('POST', P + f"/work-items/{w['id']}/comments/", {'comment_html': render(
        r, sprint_size[(r['sprint_id'], r['mark'])], row['dynamic_status'], inactive, events, action, card,
        sprint_note)}, key=BOT_KEY)
    posted += 1
    published.append({'work_item_id': w['id'], 'project_id': project, 'issue_key': key, 'comment_id': brief['id'],
                      'rank': int(float(r['rank'])), 'size': sprint_size[(r['sprint_id'], r['mark'])], 'mark': mark,
                      'score': p, 'assignee_ids': w.get('assignees') or [], 'status': row['dynamic_status'], 'inactive_days': inactive,
                      'changes': [change_line(e) for e in events], 'diagnosis': card} | action | (
                          {'cause': card['hypotheses'][0]['cause']} if card['hypotheses'] else {}))
if published:
    req = urllib.request.Request(RISK_URL, method='PUT', data=json.dumps(published, default=str).encode(), headers={
        'Authorization': f"Bearer {os.environ['RISK_INGEST_TOKEN']}", 'Content-Type': 'application/json'})
    with send(req) as r:
        print('risk service stored', json.load(r)['stored'], 'alerts')
if agent:
    print('causes:', dict(agent_stats), 'cost USD', round(agent_cost, 5))
print('posted', posted, 'retired', retired, 'of', len(items))
