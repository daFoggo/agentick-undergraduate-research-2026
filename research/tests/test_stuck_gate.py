import numpy as np
import pandas as pd

from research.stuck_gate import comment_features, loo_auc_delta

AT = pd.Timestamp('2020-03-10', tz='UTC')


def c(day, text):
    return pd.Timestamp(f'2020-03-{day:02d}', tz='UTC'), text


def test_comments_after_the_mark_are_never_seen():
    f = comment_features([c(5, 'looks fine'), c(12, 'blocked by IS-9')], AT, has_block_link=False)
    assert f['n_comments'] == 1 and f['any_blocked'] == 0


def test_days_since_last_comment_and_last_comment_keywords():
    f = comment_features([c(1, 'waiting for the reviewer'), c(8, 'merged, thanks')], AT, False)
    assert f['days_since_last_comment'] == 2 and f['last_waiting'] == 0 and f['any_waiting'] == 1
    assert f['last_review'] == 1  # "merged"


def test_keywords_match_whole_words_and_ignore_case():
    assert comment_features([c(2, 'This is BLOCKED')], AT, False)['last_blocked'] == 1
    assert comment_features([c(2, 'unblockedness')], AT, False)['last_blocked'] == 0
    assert comment_features([c(2, 'can you check?')], AT, False)['last_question'] == 1


def test_no_comments_gives_empty_but_valid_features():
    f = comment_features([], AT, has_block_link=True)
    assert f['has_comment'] == 0 and f['n_comments'] == 0 and np.isnan(f['days_since_last_comment'])
    assert f['has_block_link'] == 1


def test_a_feature_that_carries_the_label_gives_positive_delta_and_noise_gives_none():
    rng = np.random.default_rng(0)
    rows = []
    for project in range(6):
        for _ in range(200):
            y = int(rng.random() < .5)
            rows.append(dict(project=project, y=y, p=float(np.clip(.5 + .05 * (y - .5) + rng.normal(0, .15), .01, .99)),
                             f_signal=float(y), f_noise=float(rng.normal())))
    d = pd.DataFrame(rows)
    good = loo_auc_delta(d, ['f_signal'])
    bad = loo_auc_delta(d, ['f_noise'])
    assert good['delta'] > .2 and good['ci_low'] > 0
    assert bad['ci_low'] <= 0 <= bad['ci_high']
