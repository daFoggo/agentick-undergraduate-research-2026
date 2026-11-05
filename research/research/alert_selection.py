"""Which issues of a sprint may be alerted, and how many. Capacities follow the E1 policy replay (agent_policy.py)."""
import math

import pandas as pd

# Cancelled by a decision: at the 50% mark these end unfinished in 364 of 364 cases, so a high score on them is
# trivially right and an alert is noise ("Done" is excluded through dynamic_is_done).
DEAD_STATUSES = {'invalid', "won't fix"}


def alert_cap(n_eligible, capacity):
    if capacity == 'ceil20':
        return math.ceil(.2 * n_eligible)
    if capacity == 'floor20':
        return math.floor(.2 * n_eligible)
    if capacity in {'k1', 'k2', 'k3'}:
        return min(int(capacity[1:]), n_eligible)
    raise ValueError(f'Unknown capacity {capacity}')


def flag_alerts(frame, capacity='ceil20'):
    """frame: sprint_id, issue_id, dynamic_status, dynamic_is_done, p. Adds `rank` (among eligible issues of the sprint,
    NaN for the others) and `alert` (top `cap` eligible issues by score; ties go to the first row)."""
    out = frame.copy()
    ok = (out.dynamic_is_done == 0) & ~out.dynamic_status.str.lower().isin(DEAD_STATUSES)
    out['rank'] = out.p.where(ok).groupby(out.sprint_id).rank(ascending=False, method='first')
    cap = ok.groupby(out.sprint_id).transform('sum').map(lambda n: alert_cap(int(n), capacity))
    out['alert'] = ok & (out['rank'] <= cap)
    return out
