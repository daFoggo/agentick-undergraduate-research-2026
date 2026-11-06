"""Needs the tawos DB (TAWOS_DSN); skipped without it. Property: no event after t, ids unique and prefixed by kind."""
import os
from datetime import datetime, timezone

import pytest

psycopg = pytest.importorskip('psycopg')
from research.collectors import collect, sprint  # noqa: E402

DSN = os.environ.get('TAWOS_DSN')
PREFIX = dict(discussion='c', owner='o', blockers='b', sprint='s', history='h')


@pytest.fixture(scope='module')
def conn():
    if not DSN:
        pytest.skip('TAWOS_DSN not set')
    return psycopg.connect(DSN)


def test_nothing_after_t_and_ids_unique(conn):
    cur = conn.cursor()
    cur.execute("select i.id, i.creation_date + (s.end_date - i.creation_date) * .4 from tawos_raw.issue i join "
                "tawos_raw.sprint s on s.id=i.sprint_id where s.end_date > i.creation_date order by random() limit 60")
    kinds = set()
    for issue_id, t in cur.fetchall():
        events = collect(conn.cursor(), issue_id, t)
        ids = [e['id'] for e in events]
        assert len(ids) == len(set(ids)), ids
        for e in events:
            kinds.add(e['kind'])
            assert e['ts'] <= t, (issue_id, e)
            assert e['text'] and e['id'].startswith(PREFIX[e['kind']] + '-')
            assert '""' not in e['text'] or e['kind'] == 'discussion'  # titles are not double-quoted
    assert {'sprint', 'history'} <= kinds


def test_sprint_without_dates_does_not_crash_and_claims_no_progress(conn):
    cur = conn.cursor()
    cur.execute("select i.id, s.id from tawos_raw.issue i join tawos_raw.sprint s on s.id=i.sprint_id where "
                "s.start_date is null or s.end_date is null limit 40")
    for issue_id, sid in cur.fetchall():
        for e in sprint(conn.cursor(), issue_id, datetime(2100, 1, 1, tzinfo=timezone.utc)):
            if e['id'] == f's-{sid}':
                assert 'elapsed' not in e['text']


def test_issues_with_blockers_give_ordered_levels_and_unique_ids(conn):
    cur = conn.cursor()
    cur.execute("select i.id, i.creation_date + interval '40 days' from tawos_raw.issue i where i.sprint_id is not null and "
                "exists (select 1 from tawos_raw.issue_link l where l.issue_id=i.id and l.description='is blocked by') "
                "order by random() limit 40")
    seen = 0
    for issue_id, t in cur.fetchall():
        events = collect(conn.cursor(), issue_id, t)
        blockers = [e for e in events if e['kind'] == 'blockers']
        seen += bool(blockers)
        assert len({e['id'] for e in events}) == len(events)
        assert all(e['ts'] <= t and e['ref_key'] and e['safe_text'] for e in blockers)
        assert all(('level 1' in e['text'] or 'level 2' in e['text']) for e in blockers)
    assert seen > 0
