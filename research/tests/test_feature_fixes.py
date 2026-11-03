"""Regression tests: story points read from text value; static baseline never sees momentum columns."""
from datetime import datetime, timedelta

import pandas as pd

from research.replay import Event, Timeline
from research.train import feature_columns

T0 = datetime(2024, 1, 1)


def test_story_points_come_from_after_text_not_null_value():
    event = Event(1, T0 + timedelta(days=1), 'Story Points', None, None, '3', '5')
    features = Timeline([event]).features(T0, T0 + timedelta(days=1), T0 + timedelta(days=14), T0 + timedelta(days=2))
    assert features['estimate'] == 5.0


def test_story_points_missing_text_is_none():
    event = Event(1, T0 + timedelta(days=1), 'Story Points', None, None, None, None)
    features = Timeline([event]).features(T0, T0 + timedelta(days=1), T0 + timedelta(days=14), T0 + timedelta(days=2))
    assert features['estimate'] is None


def _frame():
    cols = ['static_age_days', 'static_events_3d', 'static_events_7d', 'static_status_changes_3d', 'static_status_changes_7d',
            'dynamic_age_days', 'dynamic_events_3d', 'dynamic_events_7d', 'dynamic_status_changes_3d', 'dynamic_status_changes_7d',
            'cohort_size']
    return pd.DataFrame(columns=cols)


def test_static_momentum_columns_excluded_for_every_model():
    for model in ('static_catboost', 'dynamic_catboost', 'dynamic_catboost_v2'):
        columns = feature_columns(_frame(), model)
        assert not [c for c in columns if c.startswith('static_') and c.endswith(('_3d', '_7d'))], model


def test_only_v2_gets_dynamic_momentum_columns():
    momentum = lambda cols: sorted(c for c in cols if c.startswith('dynamic_') and c.endswith(('_3d', '_7d')))
    assert momentum(feature_columns(_frame(), 'dynamic_catboost')) == []
    assert len(momentum(feature_columns(_frame(), 'dynamic_catboost_v2'))) == 4
