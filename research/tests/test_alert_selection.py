import pandas as pd
import pytest

from research.alert_selection import flag_alerts


def sprint(rows):
    return pd.DataFrame(rows, columns=['sprint_id', 'issue_id', 'dynamic_status', 'dynamic_is_done', 'p'])


def test_done_and_cancelled_issues_are_never_alerted_even_with_the_top_score():
    out = flag_alerts(sprint([(1, 1, 'done', 1, .99), (1, 2, 'invalid', 0, .98), (1, 3, "Won't Fix", 0, .97),
                              (1, 4, 'in progress', 0, .5), (1, 5, 'to do', 0, .4)]), 'k2')
    assert out.set_index('issue_id').alert.to_dict() == {1: False, 2: False, 3: False, 4: True, 5: True}


def test_the_cap_counts_only_issues_that_can_still_be_at_risk():
    rows = [(1, i, 'in progress', 0, .1 * i) for i in range(1, 6)] + [(1, i, 'done', 1, .0) for i in range(6, 11)]
    assert flag_alerts(sprint(rows), 'ceil20').alert.sum() == 1       # ceil(.2 * 5 eligible), not ceil(.2 * 10)


def test_alerts_are_the_highest_scores_and_ranked_among_eligible_only():
    out = flag_alerts(sprint([(1, 1, 'in progress', 0, .2), (1, 2, 'in progress', 0, .9), (1, 3, 'done', 1, .95)]), 'k1')
    by = out.set_index('issue_id')
    assert by.alert.to_dict() == {1: False, 2: True, 3: False}
    assert by.loc[2, 'rank'] == 1 and by.loc[1, 'rank'] == 2 and pd.isna(by.loc[3, 'rank'])


def test_each_sprint_has_its_own_cap_and_a_sprint_with_nothing_eligible_has_no_alert():
    out = flag_alerts(sprint([(1, 1, 'in progress', 0, .9), (1, 2, 'in progress', 0, .8),
                              (2, 3, 'done', 1, .9), (2, 4, 'invalid', 0, .9)]), 'k1')
    assert out.groupby('sprint_id').alert.sum().to_dict() == {1: 1, 2: 0}


def test_unknown_capacity_is_refused():
    with pytest.raises(ValueError):
        flag_alerts(sprint([(1, 1, 'in progress', 0, .5)]), 'k9')
