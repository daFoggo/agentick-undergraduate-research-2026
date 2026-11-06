"""Protocol E10: when to alert (documents/Protocol_when_to_alert_E10.md). Replay on frozen cross-project scores."""
import hashlib
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from research.alert_eval import SEED, load
from research.alert_selection import alert_cap, flag_alerts

OUT = Path(os.environ.get('E10_OUT', 'artifacts/when_to_alert_e10'))
PROTOCOL = Path('documents/Protocol_when_to_alert_E10.md')
AMENDMENT = Path('documents/Protocol_when_to_alert_E10_amendment1.md')
MARKS = (0.0, 0.25, 0.5, 0.75)
FLOOR = 0.5
POLICIES = ('P0', 'P1', 'P2', 'P3')


def policy_alerts(sprint, policy, k):
    """sprint: long frame of ONE sprint (issue_id, mark, p, y, elig). Returns (sprint_id, [(issue_id, mark), ...])."""
    def top(mark, n, skip=(), floor=None):
        d = sprint[(sprint.mark == mark) & sprint.elig & ~sprint.issue_id.isin(skip)]
        if floor is not None:
            d = d[d.p >= floor]
        return list(d.sort_values('p', ascending=False, kind='stable').issue_id[:n])

    if policy in ('P0', 'P1'):
        mark = 0.5 if policy == 'P0' else 0.0
        return sprint.sprint_id.iloc[0], [(i, mark) for i in top(mark, k)]
    picks, remaining = [], k
    for n, mark in enumerate(MARKS):
        new = top(mark, math.ceil(remaining / (len(MARKS) - n)), {i for i, _ in picks}, FLOOR if policy == 'P2' else None)
        picks += [(i, mark) for i in new]
        remaining -= len(new)
    return sprint.sprint_id.iloc[0], picks


def long_frame():
    parts = []
    for mark in MARKS:
        d = flag_alerts(load(mark).assign(p=lambda x: x.dynamic_catboost))
        parts.append(pd.DataFrame(dict(sprint_id=d.sprint_id, issue_id=d.issue_id, mark=mark, p=d.p, y=d.y,
                                       elig=d['rank'].notna())))
    out = pd.concat(parts, ignore_index=True)
    full = out.groupby('sprint_id').mark.nunique() == len(MARKS)
    return out[out.sprint_id.isin(full[full].index)]


def budgets(long):
    """Alerts per sprint: ceil(20%) of the eligible issues at the 50% mark, the number the shipped policy raises."""
    return {s: alert_cap(int(g[(g.mark == 0.5) & g.elig].shape[0]), 'ceil20') for s, g in long.groupby('sprint_id')}


def ledger_alerts(long, policy='P2'):
    """(sprint_id, issue_id, mark) of every alert the chosen policy raises over the whole sprint."""
    k = budgets(long)
    return [(s, i, m) for s, g in long.groupby('sprint_id') for i, m in policy_alerts(g, policy, k[s])[1]]


def run(long):
    k = budgets(long)
    y = long.drop_duplicates(['sprint_id', 'issue_id']).set_index(['sprint_id', 'issue_id']).y
    chance = long[long.elig].groupby(['sprint_id', 'mark']).y.mean()  # random pick among the eligible, same mark
    stats = {}
    for pol in POLICIES:
        rows = []
        for s, g in long.groupby('sprint_id'):
            _, picks = policy_alerts(g, pol, k[s])
            hit = [(1 - m) for i, m in picks if y[(s, i)] == 1]
            excess = sum(y[(s, i)] - chance[(s, m)] for i, m in picks)
            rows.append((len(picks), len(hit), sum(hit), excess))
        stats[pol] = np.array(rows, float)  # per sprint: alerts, correct, lead summed over correct alerts, excess over chance
    return stats


def _boot(stat, n, draws=2000):
    rng = np.random.default_rng(SEED)
    est = np.array([stat(rng.integers(0, n, n)) for _ in range(draws)])
    return float(np.quantile(est, .025)), float(np.quantile(est, .975))


def compare(a, b):
    """a, b per-sprint arrays (alerts, correct, lead sum): paired difference in correct alerts per sprint and in lead."""
    d = a[:, 1] - b[:, 1]
    def lead(x, i):
        return x[i, 2].sum() / x[i, 1].sum()

    e = a[:, 3] - b[:, 3]
    return dict(delta_excess=float(e.mean()), delta_excess_ci=_boot(lambda i: e[i].mean(), len(e)),
                delta_correct=float(d.mean()), delta_correct_ci=_boot(lambda i: d[i].mean(), len(d)),
                delta_lead=float(lead(a, slice(None)) - lead(b, slice(None))),
                delta_lead_ci=_boot(lambda i: lead(a, i) - lead(b, i), len(d)))


def summary(stats):
    out = {}
    for pol, s in stats.items():
        out[pol] = dict(excess_per_sprint=float(s[:, 3].mean()), alerts_per_sprint=float(s[:, 0].mean()), correct_per_sprint=float(s[:, 1].mean()),
                        precision=float(s[:, 1].sum() / s[:, 0].sum()), lead=float(s[:, 2].sum() / s[:, 1].sum()))
    for pol in ('P1', 'P2', 'P3'):
        out[pol]['vs_P0'] = compare(stats[pol], stats['P0'])
    out['P2']['vs_P3'] = compare(stats['P2'], stats['P3'])
    return out


def main():
    if OUT.exists():
        raise SystemExit(f'{OUT} exists; protocol E10 results are not overwritten')
    long = long_frame()
    res = summary(run(long))
    OUT.mkdir(parents=True)
    (OUT / 'summary.json').write_text(json.dumps(res, indent=2), encoding='utf-8')
    (OUT / 'manifest.json').write_text(json.dumps(dict(
        run_at=datetime.now(timezone.utc).isoformat(), protocol_sha256=hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        amendment1_sha256=hashlib.sha256(AMENDMENT.read_bytes()).hexdigest(),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), sprints=int(long.sprint_id.nunique()),
        floor=FLOOR, seed=SEED), indent=2), encoding='utf-8')
    for pol in POLICIES:
        r = res[pol]
        line = (f"{pol}: excess/sprint {r['excess_per_sprint']:.3f} alerts/sprint {r['alerts_per_sprint']:.2f} correct/sprint {r['correct_per_sprint']:.3f} "
                f"precision {r['precision']:.3f} lead {r['lead']:.3f}")
        if 'vs_P0' in r:
            c = r['vs_P0']
            line += (f" | vs P0 excess {c['delta_excess']:+.3f} [{c['delta_excess_ci'][0]:+.3f}, "
                     f"{c['delta_excess_ci'][1]:+.3f}] correct {c['delta_correct']:+.3f} [{c['delta_correct_ci'][0]:+.3f}, "
                     f"{c['delta_correct_ci'][1]:+.3f}] lead {c['delta_lead']:+.3f} [{c['delta_lead_ci'][0]:+.3f}, "
                     f"{c['delta_lead_ci'][1]:+.3f}]")
        print(line)
    c = res['P2']['vs_P3']
    print(f"P2 vs P3: correct {c['delta_correct']:+.3f} [{c['delta_correct_ci'][0]:+.3f}, {c['delta_correct_ci'][1]:+.3f}]"
          f" lead {c['delta_lead']:+.3f} [{c['delta_lead_ci'][0]:+.3f}, {c['delta_lead_ci'][1]:+.3f}]")


if __name__ == '__main__':
    main()
