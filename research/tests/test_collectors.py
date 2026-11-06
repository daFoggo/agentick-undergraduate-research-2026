"""Needs the tawos DB (TAWOS_DSN); skipped without it. Property: no event after t, ids unique and prefixed by kind."""
import os

import pytest

psycopg = pytest.importorskip('psycopg')
from research.collectors import collect  # noqa: E402

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
    assert {'sprint', 'history'} <= kinds
