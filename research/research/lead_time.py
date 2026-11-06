"""Protocol E9: alert quality at the 0, 25, 50 and 75% marks of a sprint (documents/Protocol_lead_time_E9.md)."""
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from research.alert_eval import MODELS, alert_quality, lift_ci, load, paired_diff

OUT = Path(os.environ.get('E9_OUT', 'artifacts/lead_time_e9'))
PROTOCOL = Path('documents/Protocol_lead_time_E9.md')
LANDMARKS = (0.0, 0.25, 0.5, 0.75)


def at_landmark(d):
    res = {m: alert_quality(d, m, 'ceil20') | {'lift_ci': lift_ci(d, m)} for m in MODELS}
    res['model_minus_rule'] = paired_diff(d, 'dynamic_catboost', 'business_rule')
    res['rows'], res['sprints'] = len(d), int(d.sprint_id.nunique())
    return res


def earliest_useful(summary):
    """Earliest mark where the model's lift CI is above 1 and it beats the rule (both CIs above their null)."""
    for mark in sorted(summary, key=float):
        s = summary[mark]
        if s['dynamic_catboost']['lift_ci'][0] > 1 and s['model_minus_rule']['ci_low'] > 0:
            return float(mark)
    return None


def main():
    if OUT.exists():
        raise SystemExit(f'{OUT} exists; protocol E9 results are not overwritten')
    summary = {str(m): at_landmark(load(m)) for m in LANDMARKS}
    OUT.mkdir(parents=True)
    out = dict(by_landmark=summary, earliest_useful=earliest_useful(summary))
    (OUT / 'summary.json').write_text(json.dumps(out, indent=2, default=float), encoding='utf-8')
    (OUT / 'manifest.json').write_text(json.dumps(dict(
        run_at=datetime.now(timezone.utc).isoformat(), protocol_sha256=hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()), indent=2), encoding='utf-8')
    for m, r in summary.items():
        c, x = r['dynamic_catboost'], r['model_minus_rule']
        print(f"mark {m:>4}: sprints {r['sprints']:4d} alerts {c['alerts']:5d} precision {c['precision']:.3f} "
              f"base {c['base_rate']:.3f} lift {c['lift']:.2f} [{c['lift_ci'][0]:.2f}, {c['lift_ci'][1]:.2f}] "
              f"recall {c['recall']:.3f} | model-rule {x['delta']:+.3f} [{x['ci_low']:+.3f}, {x['ci_high']:+.3f}]")
    print('earliest useful mark:', out['earliest_useful'])


if __name__ == '__main__':
    main()
