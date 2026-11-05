"""Score one held-out TAWOS project at the 50% landmark and flag the top issues per sprint.

Only issues that can still be at risk are ranked and flagged: not done, not cancelled (see research/alert_selection.py).

Offline batch: uses the held-out cross-project dynamic_catboost bundle, so the project was never seen in training.
Usage: python scripts/score_sprints.py IS out.csv [ceil20|floor20|k1|k2|k3]   (default ceil20 of the eligible issues)
"""
import sys

import joblib
import pandas as pd

from research.alert_selection import flag_alerts

from app.services.risk_inference import score_bundle

project, out = sys.argv[1], sys.argv[2]
assert project.isalnum(), 'project key only: it is part of a model file path'
bundle = joblib.load(f'artifacts/_archive_v2_momentum/models/cross_project__{project}__0.5__dynamic_catboost.joblib')
frame = pd.read_parquet('data/processed/snapshots.parquet')
frame = frame[(frame.project == project) & (frame.landmark == 0.5)].reset_index(drop=True)
scores = score_bundle(bundle, frame, 'dynamic_catboost', 0.5)
frame['p'] = scores.p_calibrated
frame = flag_alerts(frame, sys.argv[3] if len(sys.argv) > 3 else 'ceil20')
frame[['project_id', 'sprint_id', 'issue_id', 'dynamic_status', 'p', 'rank', 'alert', 'y']].to_csv(out, index=False)
print(len(frame), 'rows,', int(frame.alert.sum()), 'alerts, run_hash', scores.run_hash[:12])
assert not (frame.alert & (frame.dynamic_is_done == 1)).any(), 'a done issue was alerted'
assert frame.p.between(0, 1).all() and not frame.duplicated(['sprint_id', 'issue_id']).any()
hit = frame[frame.alert].groupby('sprint_id').y.sum().reindex(frame.sprint_id.unique(), fill_value=0)
pos = frame[frame['rank'].notna()].groupby('sprint_id').y.sum().reindex(hit.index, fill_value=0)
print('mean per-sprint recall among eligible issues:', round((hit[pos > 0] / pos[pos > 0]).mean(), 3))
