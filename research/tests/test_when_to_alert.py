import pandas as pd

from research.when_to_alert import MARKS, policy_alerts


def long_frame():
    """One sprint. Open issues a..e; scores per mark; y fixed."""
    rows = []
    scores = {0.0: dict(a=.9, b=.8, c=.7, d=.6, e=.4), 0.25: dict(a=.9, b=.3, c=.7, d=.6, e=.4),
              0.5: dict(a=.9, b=.3, c=.7, d=.65, e=.4), 0.75: dict(a=.9, b=.3, c=.7, d=.65, e=.95)}
    y = dict(a=1, b=0, c=1, d=1, e=1)
    for m in MARKS:
        for i, s in scores[m].items():
            rows.append(dict(sprint_id=1, issue_id=i, mark=m, p=s, y=y[i], elig=True))
    return pd.DataFrame(rows)


def picks(policy, k, **kw):
    return policy_alerts(long_frame(), policy, k, **kw)[1]  # {sprint: [(issue, mark), ...]}


def test_p0_takes_the_top_k_at_the_middle_mark_only():
    assert picks('P0', 2) == [('a', 0.5), ('c', 0.5)]


def test_p1_takes_the_top_k_at_the_start():
    assert picks('P1', 2) == [('a', 0.0), ('b', 0.0)]


def test_ledger_never_alerts_an_issue_twice_and_respects_the_budget():
    got = picks('P3', 3)
    assert len({i for i, _ in got}) == len(got) <= 3


def test_threshold_blocks_low_scores_even_when_budget_is_left():
    got = picks('P2', 5)
    assert all(dict(a=.9, b=.8, c=.7, d=.65, e=.95)[i] >= .5 for i, _ in got)
    assert 'e' in [i for i, m in got if m == 0.75]  # a late riser is caught when it rises


def test_ledger_spreads_the_budget_over_the_marks():
    got = picks('P3', 4)
    assert [m for _, m in got].count(0.0) == 1  # ceil(4 / 4) at the first mark


def test_compare_of_a_policy_with_itself_is_zero_and_a_better_one_is_positive():
    import numpy as np
    from research.when_to_alert import compare
    a = np.array([[2, 1, .5, .1], [2, 2, 1.0, .2], [2, 1, .75, .3]])
    assert compare(a, a)['delta_correct'] == 0
    better = a + np.array([0, 1, .5, .4])
    assert compare(better, a)['delta_correct'] == 1 and abs(compare(better, a)['delta_excess'] - .4) < 1e-9


def test_ledger_alerts_lists_every_pick_with_its_sprint():
    from research.when_to_alert import ledger_alerts
    got = ledger_alerts(long_frame(), 'P2')
    assert got and all(s == 1 for s, _, _ in got) and len({i for _, i, _ in got}) == len(got)
    assert len(got) <= 1  # budget = ceil(20% of 5 eligible issues at the middle mark)


def test_excess_over_chance_is_zero_for_a_random_looking_pick():
    from research.when_to_alert import run
    long = long_frame()
    long['y'] = 1  # every issue ends unfinished: any alert is right, and chance is 1, so nothing is gained
    stats = run(long)
    assert all(abs(s[:, 3]).max() < 1e-9 for s in stats.values())
