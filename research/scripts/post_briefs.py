"""Post a verified, readable brief as a Plane comment on every risk-alert work item of one project.
A work item that scores no longer flag (cancelled, done, or out of the sprint's alert cap) is retired: label removed, the
bot's brief deleted, the stored alert dropped unless a person already decided on it.

Template brief (no LLM, English like the Plane UI). The claim behind each brief is checked by EvidenceVerifier against as-of changelog
events; unverified briefs are not posted. Each verified alert is also published to the risk service, which feeds the
Approve / Dismiss / Undo card on the work item. Re-running replaces earlier briefs (deleted with PLANE_API_KEY, posted
with PLANE_BOT_KEY if set) and overwrites the stored alerts.
An LLM (OPENROUTER_MODEL, default openai/gpt-6-luna, spend capped by AGENT_BUDGET_USD) picks and drafts the action; any
failure falls back to the rules; AGENT=0 turns it off.
Usage: PLANE_API_KEY=... [PLANE_BOT_KEY=...] RISK_INGEST_TOKEN=... TAWOS_PG_PASSWORD=... \
       python scripts/post_briefs.py scores.csv ISP [limit]
"""
import csv
import html
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import date, timezone

import pandas as pd
import psycopg

from app.services.agent_context import AgentContext
from app.services.evidence_verifier import ClaimSchema, EvidenceVerifier
from app.services.openrouter_client import OpenRouterClient
from app.services.stuck_agent import run_agent
from research.tawos_source import TawosSource
from research.alert_actions import choose_action, next_cycle

BASE = os.environ.get('PLANE_URL', 'http://localhost:31080/api/v1/workspaces/ript')
KEY = os.environ['PLANE_API_KEY']
BOT_KEY = os.environ.get('PLANE_BOT_KEY', KEY)
RISK_URL = os.environ.get('RISK_URL', 'http://localhost:31081/api/v1/alerts')
MARK = 'Sprint risk alert'
OLD_MARKS = (MARK, 'Cảnh báo rủi ro sprint', 'Sprint-risk brief')  # earlier briefs are replaced too
scores_csv, identifier = sys.argv[1], sys.argv[2]
limit = int(sys.argv[3]) if len(sys.argv) > 3 else None

# Changelog fields a reader can interpret; the rest (Rank, Workflow, Link, ...) is noise. Assignee values are
# anonymised ids, so only the fact of the change is shown.
FIELDS = {'status': 'Status', 'Sprint': 'Sprint', 'Story Points': 'Story points', 'priority': 'Priority',
          'resolution': 'Resolution', 'assignee': 'Assignee'}


def plane(method, path, body=None, key=None):
    req = urllib.request.Request(BASE + path, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={'X-API-Key': key or KEY, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r) if r.status != 204 else None
    except urllib.error.HTTPError as e:
        sys.exit(f'{method} {path} -> {e.code} {e.read()[:300]}')


def tawos(sql):
    out = subprocess.run(['docker', 'exec', '-e', f"PGPASSWORD={os.environ['TAWOS_PG_PASSWORD']}",
                          os.environ.get('TAWOS_DB_CONTAINER', 'research-db-1'), 'psql', '-U', 'tawos', '-d', 'tawos',
                          '-Atc', f"select coalesce(json_agg(t),'[]') from ({sql}) t"],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


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
        urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as e:
        if e.code != 409:  # 409 = a person already decided on it: the alert stays
            raise
    global retired
    retired += 1


PROPOSED = {'raise_priority': 'raise the priority to High.',
            'nudge_owner': 'post a reminder asking for a status update (its text is on the alert card).',
            'move_next_cycle': 'move it to the next cycle, since little of this one is left.'}


CAUSES = {'waiting_on_person': 'waiting for someone', 'blocked_by_issue': 'blocked by another issue',
          'needs_decision': 'waiting for a decision', 'unclear_scope': 'the scope is unclear',
          'not_started': 'nobody has started it'}


def why(diagnosis):
    if diagnosis['cause'] == 'no_signal':
        return ''
    quote = diagnosis.get('quote') or f"blocked by {diagnosis.get('blocker_key')}"
    return (f"<p><b>According to the comments:</b> {CAUSES[diagnosis['cause']]}. Evidence: "
            f"<i>{html.escape(quote)}</i></p>")


def render(r, size, status, inactive, events, action, diagnosis):
    changes = ''.join(f'<li>{html.escape(change_line(e))}</li>' for e in events) or \
        '<li>No changes were recorded before that point.</li>'
    return (
        f"<p><b>{MARK}</b> — this item is among the ones worth a look early in the sprint.</p>"
        f"<p>Ranked <b>{int(float(r['rank']))} of {size}</b> by risk score among the open items of the sprint "
        f"(score {float(r['p']):.2f}, scale 0–1), measured when {float(r['mark']):.0%} of the sprint had passed. "
        "This is a hint about where to look first, not a statement that the item will be late.</p>"
        f"<p><b>What was observed</b></p><ul><li>Status at that time: {html.escape(status)}</li>"
        f"<li>No recorded activity for {inactive:.1f} days</li></ul>"
        f"{why(diagnosis)}"
        f"<p><b>Latest changes before that point</b></p><ul>{changes}</ul>"
        "<p><b>Suggested check:</b> confirm who owns this item and what the next step is.</p>"
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

posted = failed = retired = 0
published = []
research_db = psycopg.connect(os.environ.get('RESEARCH_DATABASE_URL', 'postgresql://tawos:tawos_local_dev@localhost:15990/tawos'))
try:  # the agent is on by default; without a key, or with AGENT=0, the rules choose
    agent = None if os.environ.get('AGENT') == '0' else OpenRouterClient(
        model=os.environ.get('OPENROUTER_MODEL', 'openai/gpt-6-luna'), budget=float(os.environ.get('AGENT_BUDGET_USD', .5)))
except Exception as exc:
    print('agent off, rules only:', exc)
    agent = None
agent_stats, agent_cost = Counter(), 0.0
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
    ctx = AgentContext(row['project'], sprint_id, cutoff, {issue_id: {
        'project': row['project'], 'status': row['dynamic_status'], 'inactive_days': inactive, 'risk_score': p,
        'events': [{'id': f"cl-{e['id']}", 'timestamp': e['ts']} for e in events]}})
    claim = ClaimSchema(
        issue_id=str(issue_id), cutoff=cutoff.isoformat(), risk_score=p, reported_inactive_days=inactive,
        kind='status_stagnation' if inactive >= 3 else 'general_risk', evidence_ids=[f"cl-{e['id']}" for e in events],
        suggested_checks=['Confirm who owns the next step for this item.'],
        summary=f"Ranked {int(float(r['rank']))} by risk score {p:.2f} in its sprint at the {mark:.0%} mark. Status "
                f"'{row['dynamic_status']}', no recorded activity for {inactive:.1f} days.")
    result = EvidenceVerifier(ctx).verify_claim(claim, strict=False)
    if not result.valid:
        failed += 1
        print('NOT POSTED', issue_id, result.errors[:1])
        continue
    for old in plane('GET', P + f"/work-items/{w['id']}/comments/")['results']:
        if any(m in old['comment_html'] for m in OLD_MARKS):
            plane('DELETE', P + f"/work-items/{w['id']}/comments/{old['id']}/")
    key = w['name'].split(']')[0].lstrip('[')
    cycle_id = cycle_of_sprint.get(r['sprint_id'])
    next_id = next_cycle(cycles, cycle_id, date.today()) if cycle_id else None
    action = choose_action(key, row['dynamic_status'], inactive, mark, cycle_id, next_id)
    diagnosis = {'cause': 'no_signal'}
    if agent:  # the tool agent reads comments and linked issues and says why it looks stuck; failures become no_signal
        facts = dict(
            key=key, status=row['dynamic_status'], inactive_days=inactive,
            links=[dict(key=x['k'], kind='blocked by' if x['n'] == 'Blocks' else 'depends on',
                        resolved=bool(x['rd'] and x['rd'] <= cutoff.isoformat())) for x in tawos(
                f"select l.name n, t.issue_key k, t.resolution_date::text rd from tawos_raw.issue_link l "
                f"join tawos_raw.issue t on t.id=l.target_issue_id where l.issue_id={issue_id} and "
                f"((l.name='Blocks' and l.direction='INBOUND') or (l.name='Depends' and l.direction='OUTBOUND'))")])
        diagnosis, meta = run_agent(agent, facts, TawosSource(research_db.cursor(), cutoff))
        agent_stats[diagnosis['cause']] += 1
        agent_cost += meta['cost']
        if diagnosis['cause'] != 'no_signal' and action['action_type'] != 'move_next_cycle':
            action = {'action_type': 'nudge_owner', 'action_text': diagnosis['action_text']}  # aimed at the cause
    brief = plane('POST', P + f"/work-items/{w['id']}/comments/", {'comment_html': render(
        r, sprint_size[(r['sprint_id'], r['mark'])], row['dynamic_status'], inactive, events, action, diagnosis)}, key=BOT_KEY)
    posted += 1
    published.append({'work_item_id': w['id'], 'project_id': project, 'issue_key': key, 'comment_id': brief['id'],
                      'rank': int(float(r['rank'])), 'size': sprint_size[(r['sprint_id'], r['mark'])], 'mark': mark,
                      'score': p, 'status': row['dynamic_status'], 'inactive_days': inactive,
                      'changes': [change_line(e) for e in events]} | action | (
                          {'cause': diagnosis['cause'], 'evidence_quote': (diagnosis.get('quote') or f"blocked by {diagnosis.get('blocker_key')}")[:500]}
                          if diagnosis['cause'] != 'no_signal' else {}))
if published:
    req = urllib.request.Request(RISK_URL, method='PUT', data=json.dumps(published).encode(), headers={
        'Authorization': f"Bearer {os.environ['RISK_INGEST_TOKEN']}", 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        print('risk service stored', json.load(r)['stored'], 'alerts')
if agent:
    print('diagnoses:', dict(agent_stats), 'cost USD', round(agent_cost, 5))
print('posted', posted, 'not posted', failed, 'retired', retired, 'of', len(items))
