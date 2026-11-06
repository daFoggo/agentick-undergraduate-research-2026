"""Score one held-out TAWOS project at the 0, 25, 50 and 75% marks and raise alerts with the E10 ledger policy (P2).

Only issues that can still be at risk are ranked and alerted: not done, not cancelled (research/alert_selection.py).
An issue is alerted once per sprint, at the first mark where it scores 0.5 or more and the sprint's budget allows
(research/when_to_alert.py, documents/Protocol_when_to_alert_E10.md). One output row per sprint, issue and mark.

Offline batch: uses the held-out cross-project dynamic_catboost bundles, so the project was never seen in training.
Usage: python scripts/score_sprints.py IS out.csv      (PYTHONPATH=. from research/)
"""
import sys

import joblib
import pandas as pd

from research.alert_selection import flag_alerts
from research.when_to_alert import MARKS, ledger_alerts

from app.services.risk_inference import score_bundle

project, out = sys.argv[1], sys.argv[2]
assert project.isalnum(), 'project key only: it is part of a model file path'
snap = pd.read_parquet('data/processed/snapshots.parquet')
frames, run_hashes = [], set()
for mark in MARKS:
    bundle = joblib.load(
        f'artifacts/_archive_v2_momentum/models/cross_project__{project}__{mark:g}__dynamic_catboost.joblib')
    frame = snap[(snap.project == project) & (snap.landmark == mark)].reset_index(drop=True)
    scores = score_bundle(bundle, frame, 'dynamic_catboost', mark)
    run_hashes.add(scores.run_hash[:12])
    frame['p'] = scores.p_calibrated
    frame = flag_alerts(frame)  # only for `rank` and eligibility; the ledger decides the alerts
    frames.append(frame.assign(mark=mark, elig=frame['rank'].notna()))
frame = pd.concat(frames, ignore_index=True)
long = frame[['sprint_id', 'issue_id', 'mark', 'p', 'y', 'elig']]
picked = set(ledger_alerts(long))
frame['alert'] = [(s, i, m) in picked for s, i, m in zip(frame.sprint_id, frame.issue_id, frame.mark)]
frame[['project_id', 'sprint_id', 'issue_id', 'mark', 'dynamic_status', 'p', 'rank', 'alert', 'y']].to_csv(out, index=False)
print(len(frame), 'rows,', int(frame.alert.sum()), 'alerts, run hashes', sorted(run_hashes))
assert not (frame.alert & ~frame.elig).any(), 'an alert on a done or cancelled issue'
assert frame.p.between(0, 1).all() and not frame.duplicated(['sprint_id', 'issue_id', 'mark']).any()
assert not frame[frame.alert].duplicated(['sprint_id', 'issue_id']).any(), 'an issue was alerted twice in a sprint'
hit = frame[frame.alert].groupby('sprint_id').y.sum()
print('alerts per sprint:', round(frame.alert.sum() / frame.sprint_id.nunique(), 2), '| correct share:',
      round(frame[frame.alert].y.mean(), 3))
