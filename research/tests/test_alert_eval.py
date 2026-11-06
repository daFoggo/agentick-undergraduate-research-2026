import numpy as np
import pandas as pd

from research.alert_eval import alert_quality, paired_diff


def frame():
    # sprint 1: 5 eligible (cap ceil(.2*5)=1) + 1 cancelled; the model's top eligible issue fails, the rule's succeeds
    rows = [(1, i, 'in progress', 0, .9 - .1 * i, int(i == 2), .1 + .1 * i) for i in range(5)]
    rows.append((1, 9, 'invalid', 0, .99, 1, .99))
    return pd.DataFrame(rows, columns=['sprint_id', 'issue_id', 'dynamic_status', 'dynamic_is_done', 'p', 'y', 'q'])


def test_precision_base_rate_lift_and_recall_use_only_eligible_issues():
    r = alert_quality(frame(), 'p', 'ceil20')
    assert r['alerts'] == 1 and r['tp'] == 0                  # issue 0 has the top eligible score, but y = 0
    assert r['base_rate'] == 1 / 5 and r['recall'] == 0       # the cancelled issue 9 is not counted as a positive
    r2 = alert_quality(frame().assign(p=lambda d: d.q), 'p', 'ceil20')
    assert r2['alerts'] == 1 and r2['tp'] == 0                 # q ranks issue 4 first: also y = 0


def test_paired_difference_is_zero_for_identical_rankings_and_positive_when_one_is_better():
    d = pd.concat([frame().assign(sprint_id=s) for s in range(1, 41)])
    same = paired_diff(d, 'p', 'p')
    assert same['delta'] == 0
    better = paired_diff(d.assign(p=lambda x: (x.y == 1).astype(float) + x.p / 10), 'p', 'q')
    assert better['delta'] > 0 and better['ci_low'] > 0


def test_load_reads_the_requested_landmark(tmp_path, monkeypatch):
    import pandas as pd
    from research import alert_eval
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'data/processed').mkdir(parents=True)
    pd.DataFrame({'sprint_id': [1, 1], 'issue_id': [1, 2], 'landmark': [0.25, 0.5],
                  'dynamic_status': ['To Do', 'Done']}).to_parquet('data/processed/snapshots.parquet')
    pred = tmp_path / 'artifacts/_archive_v2_momentum/predictions'
    pred.mkdir(parents=True)
    for model in alert_eval.MODELS:
        pd.DataFrame({'project': ['P'], 'sprint_id': [1], 'issue_id': [1], 'dynamic_is_done': [0], 'y': [1],
                      'p': [.7]}).to_parquet(pred / f'cross_project__P__0.25__{model}.parquet')
    d = alert_eval.load(0.25)
    assert d.dynamic_status.tolist() == ['To Do'] and len(d) == 1
