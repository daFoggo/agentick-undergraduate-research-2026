from datetime import date

from research.alert_actions import choose_action, next_cycle

CYCLES = [
    {'id': 'c1', 'start_date': '2026-10-01T00:00:01Z', 'end_date': '2026-10-14T23:59:00Z'},
    {'id': 'c2', 'start_date': '2026-10-15T00:00:01Z', 'end_date': '2026-10-28T23:59:00Z'},
    {'id': 'c3', 'start_date': '2026-10-29T00:00:01Z', 'end_date': '2026-11-11T23:59:00Z'},
]


def test_a_silent_issue_gets_a_reminder_with_its_facts():
    a = choose_action('IS-7', 'In Progress', 6.2)
    assert a['action_type'] == 'nudge_owner'
    assert 'IS-7' in a['action_text'] and '6 days' in a['action_text'] and 'In Progress' in a['action_text']


def test_an_issue_with_recent_activity_gets_the_priority_bump():
    assert choose_action('IS-7', 'In Progress', 1.0) == {'action_type': 'raise_priority'}


def test_the_threshold_is_three_days_like_the_stagnation_rule():
    assert choose_action('IS-7', 'Todo', 3.0)['action_type'] == 'nudge_owner'
    assert choose_action('IS-7', 'Todo', 2.9)['action_type'] == 'raise_priority'


def test_late_in_the_sprint_the_honest_remedy_is_to_carry_it_over():
    a = choose_action('IS-7', 'In Progress', 6.0, mark=.75, cycle_id='c2', next_cycle_id='c3')
    assert a == {'action_type': 'move_next_cycle', 'cycle_id': 'c2', 'target_cycle_id': 'c3'}


def test_no_move_early_or_without_a_next_cycle():
    assert choose_action('IS-7', 'Todo', 6.0, mark=.5, cycle_id='c2', next_cycle_id='c3')['action_type'] == 'nudge_owner'
    assert choose_action('IS-7', 'Todo', 1.0, mark=.75, cycle_id='c2')['action_type'] == 'raise_priority'


def test_next_cycle_is_the_one_starting_right_after_and_must_not_be_over():
    assert next_cycle(CYCLES, 'c2', date(2026, 10, 20)) == 'c3'
    assert next_cycle(CYCLES, 'c3', date(2026, 10, 20)) is None          # nothing after the last one
    assert next_cycle(CYCLES, 'c1', date(2026, 11, 20)) is None          # the next one has already finished
    assert next_cycle(CYCLES, 'zz', date(2026, 10, 20)) is None


def test_a_reminder_does_not_call_a_missing_status_a_state():
    for status in ('unknown', None, ''):
        text = choose_action('X-1', status, 5)['action_text']
        assert 'unknown' not in text and text.startswith('Hi, X-1 has had no recorded activity for 5 days')
    assert 'X-1 is still in progress' in choose_action('X-1', 'in progress', 5)['action_text']
