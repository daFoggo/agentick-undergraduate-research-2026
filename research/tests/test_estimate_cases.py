import numpy as np
import pandas as pd

from research.estimate_cases import predict_project, summarize


def frame(n=100):
    t0 = pd.Timestamp('2020-01-01', tz='UTC')
    return pd.DataFrame({
        'creation_date': [t0 + pd.Timedelta(days=i) for i in range(n)],
        'resolution_date': [t0 + pd.Timedelta(days=i + 5) for i in range(n)],
        'story_point': [float(1 + i % 3) for i in range(n)]})


def test_candidates_resolved_before_query_creation_only():
    df = frame()
    emb = np.eye(len(df), 4)[np.arange(len(df)) % 4]
    out = predict_project(df, emb, query_frac=.3, k=5, min_candidates=3)
    # query at day d may only see issues with i+5 < d, i.e. i < d-5
    assert (out.n_candidates == out.query_pos.map(lambda p: max(p - 5, 0))).all()


def test_future_value_does_not_leak():
    df = frame()
    emb = np.eye(len(df), 4)[np.arange(len(df)) % 4]
    base = predict_project(df, emb, query_frac=.3, k=5, min_candidates=3)
    df2 = df.copy()
    df2.loc[df2.index[-1], 'story_point'] = 999.0  # last query itself and its future must not move others
    changed = predict_project(df2, emb, query_frac=.3, k=5, min_candidates=3)
    assert (base.iloc[:-1][['m0', 'm1', 'm2']].to_numpy() == changed.iloc[:-1][['m0', 'm1', 'm2']].to_numpy()).all()


def test_knn_uses_most_similar_candidates():
    df = frame(60)
    df['story_point'] = [8.0 if i % 2 else 1.0 for i in range(60)]
    emb = np.zeros((60, 2))
    emb[::2, 0] = 1  # even issues look alike, odd issues look alike
    emb[1::2, 1] = 1
    out = predict_project(df, emb, query_frac=.3, k=5, min_candidates=3)
    truth = df.story_point.to_numpy()[out.query_pos]
    assert (out.m2 == truth).all()          # kNN recovers the pattern
    assert not (out.m0 == truth).all()      # the project median cannot


def test_summarize_coverage_and_errors():
    out = pd.DataFrame({'project': ['A', 'A', 'B'], 'y': [1., 3., 5.], 'm0': [2., 2., 5.], 'm1': [2., 2., 5.],
                        'm2': [1., 3., 4.], 'lo0': [1., 1., 4.], 'hi0': [2., 2., 6.],
                        'lo2': [1., 3., 5.], 'hi2': [1., 3., 5.]})
    s = summarize(out)
    assert s['M0']['mae'] == (1 + 1 + 0) / 3
    assert s['M2']['mae'] == (0 + 0 + 1) / 3
    assert s['M0']['coverage'] == 2 / 3      # y=3 is outside [1,2]
    assert s['M2']['coverage'] == 1.0        # every y sits on its degenerate interval


def test_queries_without_enough_candidates_are_counted_not_lost():
    df = frame()
    emb = np.eye(len(df), 4)[np.arange(len(df)) % 4]
    out = predict_project(df, emb, query_frac=.3, k=5, min_candidates=1000)
    assert len(out) == 0 and out.attrs['skipped'] == 30
    assert predict_project(df, emb, query_frac=.3, k=5, min_candidates=3).attrs['skipped'] == 0
