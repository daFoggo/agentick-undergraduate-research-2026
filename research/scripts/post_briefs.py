"""Post a verified, readable brief as a Plane comment on every risk-alert work item of one project.
A work item that scores no longer flag (cancelled, done, or out of the sprint's alert cap) is retired: label removed, the
bot's brief deleted, the stored alert dropped unless a person already decided on it.

Template brief (no LLM, Vietnamese). The claim behind each brief is checked by EvidenceVerifier against as-of changelog
events; unverified briefs are not posted. Each verified alert is also published to the risk service, which feeds the
Approve / Dismiss / Undo card on the work item. Re-running replaces earlier briefs (deleted with PLANE_API_KEY, posted
with PLANE_BOT_KEY if set) and overwrites the stored alerts.
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
from datetime import timezone

import pandas as pd

from app.services.agent_context import AgentContext
from app.services.evidence_verifier import ClaimSchema, EvidenceVerifier

BASE = os.environ.get('PLANE_URL', 'http://localhost:31080/api/v1/workspaces/ript')
KEY = os.environ['PLANE_API_KEY']
BOT_KEY = os.environ.get('PLANE_BOT_KEY', KEY)
RISK_URL = os.environ.get('RISK_URL', 'http://localhost:31081/api/v1/alerts')
MARK = 'Cảnh báo rủi ro sprint'
scores_csv, identifier = sys.argv[1], sys.argv[2]
limit = int(sys.argv[3]) if len(sys.argv) > 3 else None

# Changelog fields a reader can interpret; the rest (Rank, Workflow, Link, ...) is noise. Assignee values are
# anonymised ids, so only the fact of the change is shown.
FIELDS = {'status': 'Trạng thái', 'Sprint': 'Sprint', 'Story Points': 'Story points', 'priority': 'Độ ưu tiên',
          'resolution': 'Kết quả xử lý', 'assignee': 'Người phụ trách'}


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
    when = pd.Timestamp(e['ts']).strftime('%d/%m/%Y %H:%M')
    if e['field'] == 'assignee':
        return f"{when} — Đổi người phụ trách"
    before, after = e['from_string'] or '(trống)', e['to_string'] or '(trống)'
    return f"{when} — {FIELDS[e['field']]}: {before} → {after}"


def retire(w, label_id):
    """The latest scores no longer flag this work item: drop the label and the bot's brief, then the stored alert."""
    if not w['labels'] or label_id not in w['labels']:
        return
    for old in plane('GET', P + f"/work-items/{w['id']}/comments/")['results']:
        if MARK in old['comment_html'] or 'Sprint-risk brief' in old['comment_html']:
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


def render(r, size, status, inactive, events):
    changes = ''.join(f'<li>{html.escape(change_line(e))}</li>' for e in events) or \
        '<li>Chưa có thay đổi nào được ghi nhận trước thời điểm này.</li>'
    return (
        f"<p><b>{MARK}</b> — issue này được dự báo có nguy cơ không hoàn thành trong sprint.</p>"
        f"<p>Xếp <b>thứ {int(float(r['rank']))}/{size}</b> về điểm rủi ro trong các issue còn đang làm của sprint "
        f"(điểm {float(r['p']):.2f}, thang 0–1, càng cao càng dễ không hoàn thành). "
        "Tính tại mốc 50% thời gian sprint; đây là ước lượng của mô hình, không phải kết luận chắc chắn.</p>"
        f"<p><b>Dấu hiệu quan sát được</b></p><ul><li>Trạng thái lúc đó: {html.escape(status)}</li>"
        f"<li>Không có hoạt động nào được ghi nhận trong {inactive:.1f} ngày</li></ul>"
        f"<p><b>Thay đổi gần nhất trước thời điểm đó</b></p><ul>{changes}</ul>"
        "<p><b>Nên làm:</b> xác nhận ai đang phụ trách và bước tiếp theo.</p>"
        "<p><b>Đề xuất:</b> nâng độ ưu tiên lên High. Dùng nút <b>Duyệt</b> hoặc <b>Bỏ qua</b> ở thẻ cảnh báo trên "
        "đầu issue; có thể hoàn tác. Chưa có gì thay đổi cho đến khi bạn bấm.</p>")


project = next(p['id'] for p in plane('GET', '/projects/')['results'] if p['identifier'] == identifier)
P = f'/projects/{project}'
label = next(label['id'] for label in plane('GET', P + '/labels/')['results'] if label['name'] == 'risk-alert')
rows = list(csv.DictReader(open(scores_csv)))
sprint_end = {str(s['id']): s['ed'] for s in tawos(
    "select id,end_date::date ed from tawos_raw.sprint where id in (%s)" % ','.join(
        str(int(x)) for x in {r['sprint_id'] for r in rows}))}
sprint_size = Counter(r['sprint_id'] for r in rows if r['rank'])  # ranked = still open and not cancelled
# same "latest sprint wins" rule as import_to_plane.py: a Plane work item sits in one cycle.
latest = {}
for r in sorted(rows, key=lambda r: sprint_end[r['sprint_id']]):
    latest[r['issue_id']] = r
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
snap = snap[snap.landmark == 0.5].set_index(['sprint_id', 'issue_id'])
field_list = ','.join(f"'{f}'" for f in FIELDS)

posted = failed = retired = 0
published = []
for w in items:
    r = latest[w['external_id']]
    if r['alert'] != 'True':
        retire(w, label)
        continue
    if label not in w['labels']:  # newly flagged: the cap now reaches it because ineligible issues left the ranking
        plane('PATCH', P + f"/work-items/{w['id']}/", {'labels': w['labels'] + [label]})
    sprint_id, issue_id = int(r['sprint_id']), int(r['issue_id'])
    row = snap.loc[(sprint_id, issue_id)]
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
        summary=f"Ranked {int(float(r['rank']))} by risk score {p:.2f} in its sprint at the 50% mark. Status "
                f"'{row['dynamic_status']}', no recorded activity for {inactive:.1f} days.")
    result = EvidenceVerifier(ctx).verify_claim(claim, strict=False)
    if not result.valid:
        failed += 1
        print('NOT POSTED', issue_id, result.errors[:1])
        continue
    for old in plane('GET', P + f"/work-items/{w['id']}/comments/")['results']:
        if MARK in old['comment_html'] or 'Sprint-risk brief' in old['comment_html']:  # also the English v1 brief
            plane('DELETE', P + f"/work-items/{w['id']}/comments/{old['id']}/")
    brief = plane('POST', P + f"/work-items/{w['id']}/comments/", {'comment_html': render(
        r, sprint_size[r['sprint_id']], row['dynamic_status'], inactive, events)}, key=BOT_KEY)
    posted += 1
    published.append({'work_item_id': w['id'], 'project_id': project, 'issue_key': w['name'].split(']')[0].lstrip('['), 'comment_id': brief['id'],
                      'rank': int(float(r['rank'])), 'size': sprint_size[r['sprint_id']],
                      'score': p, 'status': row['dynamic_status'], 'inactive_days': inactive,
                      'changes': [change_line(e) for e in events]})
if published:
    req = urllib.request.Request(RISK_URL, method='PUT', data=json.dumps(published).encode(), headers={
        'Authorization': f"Bearer {os.environ['RISK_INGEST_TOKEN']}", 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        print('risk service stored', json.load(r)['stored'], 'alerts')
print('posted', posted, 'not posted', failed, 'retired', retired, 'of', len(items))
