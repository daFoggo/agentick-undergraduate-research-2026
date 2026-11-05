import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import publish_cases  # noqa: E402


def test_size_follows_the_projects_own_scale():
    every = np.array([1] * 10 + [2] * 10 + [3] * 10 + [5] * 5 + [8] * 5)
    assert publish_cases.size_of(1, every) == 'small'
    assert publish_cases.size_of(3, every) == 'medium'
    assert publish_cases.size_of(8, every) == 'large'


def test_a_project_where_every_case_has_the_same_points_has_no_small_or_large():
    assert publish_cases.size_of(3, np.array([3.0] * 40)) == 'medium'


def test_past_cases_are_created_once_and_linked_inside_plane(monkeypatch):
    posts = []

    def fake_plane(path, body=None, method=None):
        if path == '/projects/':
            return {'results': [{'identifier': 'PCA', 'id': 'pid'}]} if body is None else {'id': 'pid'}
        if path.endswith('/states/'):
            return {'results': [{'name': 'Done', 'id': 'done'}]}
        posts.append(body)
        return {'sequence_id': 9}

    monkeypatch.setattr(publish_cases, 'plane', fake_plane)
    monkeypatch.setattr(publish_cases, 'work_items', lambda project, source: [{'external_id': '1', 'sequence_id': 7}])
    cases = {1: dict(id=1, key='IS-1', title='old', text=''), 2: dict(id=2, key='IS-2', title='new', text='x')}
    paths = publish_cases.history_paths(cases)
    assert [p['external_id'] for p in posts] == ['2']  # case 1 already exists: not created twice
    assert paths == {1: '/ript/browse/PCA-7/', 2: '/ript/browse/PCA-9/'}
