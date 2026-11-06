"""Smoke test of M1 on the tawos DB: state_at(far future) must equal the final row; waits_on counts."""
import os, sys, psycopg
from datetime import datetime, timezone
from research.tawos_source import state_at, waits_on

T = datetime(2100, 1, 1, tzinfo=timezone.utc)
with psycopg.connect(os.environ.get('TAWOS_DSN', 'postgresql://tawos:tawos_local_dev@host.docker.internal:15432/tawos')) as c:
    cur = c.cursor()
    cur.execute("select id, assignee_id, priority, status, sprint_id from tawos_raw.issue where sprint_id is not null "
                "order by random() limit 300")
    bad = {'assignee': 0, 'priority': 0, 'status': 0, 'sprint': 0}
    for i, a, p, s, sp in cur.fetchall():
        st = state_at(c.cursor(), i, T)
        bad['assignee'] += st['assignee_id'] != a
        bad['priority'] += st['priority'] != p
        bad['status'] += st['status'] != s
        bad['sprint'] += sp not in st['sprint_ids']
    print('mismatch of 300 vs final row:', bad)
    cur.execute("select id, creation_date from tawos_raw.issue where sprint_id is not null order by random() limit 2000")
    n = sum(bool(waits_on(c.cursor(), i, d)) for i, d in cur.fetchall())
    print('sprint issues with a wait-on link at creation time (of 2000):', n)
