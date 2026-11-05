"""Score one held-out TAWOS project at the 50% landmark and flag the top ceil(20%) per sprint.

Offline batch: uses the held-out cross-project dynamic_catboost bundle, so the project was never seen in training.
Usage: python scripts/score_sprints.py IS out.csv
"""
import math
import sys

import joblib
import pandas as pd

from app.services.risk_inference import score_bundle

project, out = sys.argv[1], sys.argv[2]
assert project.isalnum(), 'project key only: it is part of a model file path'
bundle = joblib.load(f'artifacts/_archive_v2_momentum/models/cross_project__{project}__0.5__dynamic_catboost.joblib')
frame = pd.read_parquet('data/processed/snapshots.parquet')
frame = frame[(frame.project == project) & (frame.landmark == 0.5)].reset_index(drop=True)
scores = score_bundle(bundle, frame, 'dynamic_catboost', 0.5)
frame['p'] = scores.p_calibrated
frame['rank'] = frame.groupby('sprint_id').p.rank(ascending=False, method='first')
frame['alert'] = frame['rank'] <= frame.groupby('sprint_id').p.transform('size').map(lambda n: math.ceil(.2 * n))
frame[['project_id', 'sprint_id', 'issue_id', 'dynamic_status', 'p', 'rank', 'alert', 'y']].to_csv(out, index=False)
print(len(frame), 'rows,', int(frame.alert.sum()), 'alerts, run_hash', scores.run_hash[:12])
sizes = frame.groupby('sprint_id').size()
assert (frame.groupby('sprint_id').alert.sum() == sizes.map(lambda n: math.ceil(.2 * n))).all()
assert frame.p.between(0, 1).all() and not frame.duplicated(['sprint_id', 'issue_id']).any()
hit = frame[frame.alert].groupby('sprint_id').y.sum().reindex(sizes.index, fill_value=0)
pos = frame.groupby('sprint_id').y.sum()
print('mean per-sprint recall@ceil(20%):', round((hit[pos > 0] / pos[pos > 0]).mean(), 3))
