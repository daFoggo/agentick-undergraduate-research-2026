"""Protocol E8: quality of the alerts as they run on Plane (documents/Protocol_alert_quality_E8.md). Replay only."""
import glob
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from research.alert_selection import flag_alerts

OUT = Path(os.environ.get('E8_OUT', 'artifacts/alert_quality_e8'))
PROTOCOL = Path('documents/Protocol_alert_quality_E8.md')
SEED = 20261105
MODELS = ('dynamic_catboost', 'business_rule')


def _flag(frame, col, capacity):
    return flag_alerts(frame.assign(p=frame[col]), capacity)


def alert_quality(frame, col, capacity):
    d = _flag(frame, col, capacity)
    eligible, hit = d['rank'].notna(), d.alert & (d.y == 1)
    alerts, tp, positives = int(d.alert.sum()), int(hit.sum()), int(d.y[eligible].sum())
    base = float(d.y[eligible].mean()) if eligible.any() else np.nan
    precision = tp / alerts if alerts else np.nan
    return dict(alerts=alerts, tp=tp, eligible=int(eligible.sum()), positives=positives, precision=precision,
                base_rate=base, lift=precision / base if alerts and base else np.nan,
                recall=tp / positives if positives else np.nan)


def _per_sprint(frame, col, capacity):
    d = _flag(frame, col, capacity)
    g = d.assign(hit=d.alert & (d.y == 1), el=d['rank'].notna(), pos=d['rank'].notna() & (d.y == 1)).groupby('sprint_id')
    return g.agg(alerts=('alert', 'sum'), tp=('hit', 'sum'), eligible=('el', 'sum'), positives=('pos', 'sum'))


def _boot(stat, n, draws=2000):
    rng = np.random.default_rng(SEED)
    est = np.array([stat(rng.integers(0, n, n)) for _ in range(draws)])
    return float(np.quantile(est, .025)), float(np.quantile(est, .975))


def paired_diff(frame, col_a, col_b, capacity='ceil20'):
    """Mean correct alerts per sprint, a minus b (both pick the same number of alerts), bootstrap over sprints."""
    a, b = _per_sprint(frame, col_a, capacity), _per_sprint(frame, col_b, capacity)
    diff = (a.tp - b.tp).to_numpy(float)
    lo, hi = _boot(lambda i: diff[i].mean(), len(diff))
    return dict(delta=float(diff.mean()), ci_low=lo, ci_high=hi, n_sprints=len(diff),
                alerts_per_sprint=float(a.alerts.mean()))


def lift_ci(frame, col, capacity='ceil20'):
    s = _per_sprint(frame, col, capacity).to_numpy(float)
    stat = lambda i: (s[i, 1].sum() / s[i, 0].sum()) / (s[i, 3].sum() / s[i, 2].sum())
    return _boot(stat, len(s))


def load():
    snap = pd.read_parquet('data/processed/snapshots.parquet')
    snap = snap[snap.landmark == 0.5][['sprint_id', 'issue_id', 'dynamic_status']]
    out = None
    for model in MODELS:
        d = pd.concat([pd.read_parquet(f) for f in sorted(glob.glob(
            f'artifacts/_archive_v2_momentum/predictions/cross_project__*__0.5__{model}.parquet'))])
        d = d[['project', 'sprint_id', 'issue_id', 'dynamic_is_done', 'y', 'p']].rename(columns={'p': model})
        out = d if out is None else out.merge(d[['sprint_id', 'issue_id', model]], on=['sprint_id', 'issue_id'],
                                              validate='one_to_one')
    return out.merge(snap, on=['sprint_id', 'issue_id'], how='left', validate='one_to_one')


def main():
    if OUT.exists():
        raise SystemExit(f'{OUT} exists; protocol E8 results are not overwritten')
    d = load()
    summary = {}
    for capacity in ('ceil20', 'k2'):
        res = {m: alert_quality(d, m, capacity) for m in MODELS}
        for m in MODELS:
            res[m]['lift_ci'] = lift_ci(d, m, capacity)
            res[m]['per_project'] = {str(p): alert_quality(g, m, capacity) for p, g in d.groupby('project')}
        res['model_minus_rule'] = paired_diff(d, 'dynamic_catboost', 'business_rule', capacity)
        summary[capacity] = res
    OUT.mkdir(parents=True)
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2, default=float), encoding='utf-8')
    (OUT / 'manifest.json').write_text(json.dumps(dict(
        run_at=datetime.now(timezone.utc).isoformat(), protocol_sha256=hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), seed=SEED, rows=len(d),
        projects=int(d.project.nunique()), sprints=int(d.sprint_id.nunique())), indent=2), encoding='utf-8')
    for capacity, res in summary.items():
        print(f'--- {capacity}')
        for m in MODELS:
            r = res[m]
            print(f"{m:17s} alerts {r['alerts']:5d} precision {r['precision']:.3f} base {r['base_rate']:.3f} "
                  f"lift {r['lift']:.2f} [{r['lift_ci'][0]:.2f}, {r['lift_ci'][1]:.2f}] recall {r['recall']:.3f}")
        x = res['model_minus_rule']
        print(f"model - rule: {x['delta']:+.3f} correct alerts per sprint [{x['ci_low']:+.3f}, {x['ci_high']:+.3f}] "
              f"over {x['n_sprints']} sprints ({x['alerts_per_sprint']:.2f} alerts per sprint)")


if __name__ == '__main__':
    main()
