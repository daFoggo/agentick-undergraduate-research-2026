from datetime import datetime, timedelta, timezone

from research.tawos_source import WAITS_ON, state_at, waits_on

D = lambda n: datetime(2020, 1, 1, tzinfo=timezone.utc) + timedelta(days=n)


class Cur:
    """Fake cursor: answers the issue row first, then the change_log rows."""
    def __init__(self, issue, changes, links=()):
        self.q, self.issue, self.changes, self.links = None, issue, changes, links

    def execute(self, sql, params=None):
        self.q = sql

    def fetchone(self):
        return self.issue

    def fetchall(self):
        if 'tawos_raw.sprint' in self.q:
            return [(94, 940), (95, 950), (96, 960)]  # jiraid -> sprint.id
        return self.links if 'issue_link' in self.q else self.changes


def test_no_change_keeps_final_values():
    s = state_at(Cur((5, 'Major', 'Done', 9), []), 1, D(3))
    assert s == dict(assignee_id=5, priority='Major', status='Done', sprint_ids=(9,))


def test_value_at_t_comes_from_the_log_not_from_the_final_row():
    ch = [('assignee', D(1), None, None, '7', '7'), ('assignee', D(5), '7', '7', '8', '8'),
          ('Status', D(2), None, 'To Do', None, 'In Progress'), ('status', D(6), None, 'In Progress', None, 'Done'),
          ('priority', D(4), None, 'Minor', None, 'Blocker')]
    s = state_at(Cur((8, 'Blocker', 'Done', None), ch), 1, D(3))
    assert (s['assignee_id'], s['status'], s['priority']) == (7, 'In Progress', 'Minor')  # field case does not matter
    assert state_at(Cur((8, 'Blocker', 'Done', None), ch), 1, D(0))['assignee_id'] is None  # before any change


def test_sprint_move_pair_and_multi_sprint():
    ch = [('sprint', D(1), '', '', '94, 95', 'a'), ('sprint', D(5), '94', 'x', '', ''), ('sprint', D(5), '', '', '96', 'y')]
    cur = lambda: Cur((None, 'P', 'S', 960), ch)
    assert state_at(cur(), 1, D(0))['sprint_ids'] == ()
    assert state_at(cur(), 1, D(2))['sprint_ids'] == (940, 950)
    assert state_at(cur(), 1, D(5))['sprint_ids'] == (960,)


def test_only_waiting_directions_are_in_the_map():
    assert 'is blocked by' in WAITS_ON and 'blocks' not in WAITS_ON and 'required by' not in WAITS_ON


def test_waits_on_marks_resolution_by_t():
    got = waits_on(Cur(None, [], [(2, 'A-2', 'is blocked by', D(2)), (3, 'A-3', 'depends on', D(9)),
                                  (4, 'A-4', 'depends on', None)]), 1, D(5))
    assert [g['resolved'] for g in got] == [True, False, False]


def test_anonymised_assignee_is_assigned_not_unassigned():
    ch = [('assignee', D(1), None, None, '<UNKNOWN_USER>', '<UNKNOWN_USER>')]
    assert state_at(Cur((7, 'P', 'S', None), ch), 1, D(2))['assignee_id'] == -1
