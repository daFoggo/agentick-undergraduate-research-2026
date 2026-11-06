from research.sprint_plan import history_rate, make_plan


def test_history_needs_enough_sprints_and_issues():
    assert history_rate([(10, 5), (10, 4)]) is None            # two sprints
    assert history_rate([(2, 1), (3, 1), (4, 2)]) is None      # nine issues
    assert history_rate([(10, 5), (10, 4), (10, 3)]) == 12 / 30


def test_the_riskiest_issues_are_moved_up_to_the_expected_number_unfinished():
    plan = make_plan({'a': .9, 'b': .2, 'c': .6, 'd': .1}, rate=.5)
    assert plan['budget'] == 2 and plan['expected_unfinished'] == 2.0
    assert plan['move'] == [('a', 'risk'), ('c', 'risk')]


def test_an_issue_that_waits_on_a_moved_issue_moves_with_it_even_through_a_chain():
    scores = {'a': .9, 'b': .2, 'c': .1, 'd': .05}
    plan = make_plan(scores, rate=.25, waits_on={'b': {'a'}, 'c': {'b'}, 'd': {'x'}})  # x is not in the sprint
    assert plan['budget'] == 1
    assert plan['move'] == [('a', 'risk'), ('b', 'follows'), ('c', 'follows')]


def test_no_plan_without_history_or_without_anything_to_move():
    assert make_plan({'a': .9}, rate=None) is None
    assert make_plan({}, rate=.5) is None
    assert make_plan({'a': .9, 'b': .8}, rate=.1) is None     # expects 0.2 unfinished: rounds to nothing
