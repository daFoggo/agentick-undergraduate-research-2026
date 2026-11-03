import numpy as np
import pandas as pd
from catboost import CatBoostRanker

from research.train import feature_columns, fit_model, is_ranker, make_model, predict_scores, prepare

CONFIG = {'seed': 1, 'catboost': {'iterations': 30, 'depth': 3, 'learning_rate': .2, 'l2_leaf_reg': 3, 'thread_count': 1}}


def frame(n_sprints=12, per=20, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for s in range(n_sprints):
        shift = rng.normal()  # sprint-level risk, useless for ranking inside a sprint
        for i in range(per):
            signal = rng.normal()
            y = int(signal + shift + rng.normal(scale=.3) > 0)
            rows.append({'sprint_id': s, 'issue_id': s * per + i, 'landmark': 0.0, 'y': y, 'cohort_size': per,
                         'static_age_days': rng.random(), 'dynamic_inactive_days': signal, 'dynamic_status': 'open'})
    return pd.DataFrame(rows).sample(frac=1, random_state=3).reset_index(drop=True)  # shuffled: groups not contiguous


def test_only_rank_models_are_rankers():
    assert is_ranker('dynamic_catboost_rank')
    assert not is_ranker('dynamic_catboost') and not is_ranker('static_catboost')


def test_rank_model_uses_same_features_as_dynamic_catboost():
    data = frame()
    assert feature_columns(data, 'dynamic_catboost_rank') == feature_columns(data, 'dynamic_catboost')


def test_rank_model_is_a_catboost_ranker_with_yetirank():
    data = frame()
    columns = feature_columns(data, 'dynamic_catboost_rank')
    _, categories = prepare(data, columns)
    model = make_model('dynamic_catboost_rank', columns, categories, CONFIG)
    assert isinstance(model, CatBoostRanker) and model.get_params()['loss_function'] == 'YetiRank'


def test_fit_handles_unsorted_groups_and_scores_are_probabilities_that_rank_signal():
    data = frame()  # sprint_ids interleaved: CatBoost requires contiguous groups, fit_model must handle it
    columns = feature_columns(data, 'dynamic_catboost_rank')
    _, categories = prepare(data, columns)
    model = make_model('dynamic_catboost_rank', columns, categories, CONFIG)
    fit_model(model, 'dynamic_catboost_rank', data, columns, categories)
    test = frame(seed=7)
    score = predict_scores(model, 'dynamic_catboost_rank', prepare(test, columns)[0])
    assert ((score > 0) & (score < 1)).all()
    assert np.corrcoef(score, test.dynamic_inactive_days)[0, 1] > .5


def test_classifier_path_unchanged():
    data = frame()
    columns = feature_columns(data, 'dynamic_catboost')
    _, categories = prepare(data, columns)
    model = make_model('dynamic_catboost', columns, categories, CONFIG)
    fit_model(model, 'dynamic_catboost', data, columns, categories)
    score = predict_scores(model, 'dynamic_catboost', prepare(data, columns)[0])
    assert np.allclose(score, model.predict_proba(prepare(data, columns)[0])[:, 1])


def test_static_rank_is_a_ranker_on_static_features_only():
    data = frame()
    assert is_ranker('static_catboost_rank')
    assert feature_columns(data, 'static_catboost_rank') == feature_columns(data, 'static_catboost')
    assert not any(c.startswith('dynamic_') for c in feature_columns(data, 'static_catboost_rank'))
