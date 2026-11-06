"""Template baseline (A0) for the action on an alert: rules only, no LLM. The agent variant is measured against it."""
SILENT_DAYS = 3  # same threshold post_briefs uses to call an issue stagnant
LATE_MARK = .75  # from here on there is little sprint left to finish it: carrying it over is the honest remedy


def next_cycle(cycles, current_id, today):
    """Id of the cycle that starts right after `current_id`, unless it has already finished (Plane would refuse it)."""
    ordered = sorted(cycles, key=lambda c: c['start_date'])
    ids = [c['id'] for c in ordered]
    if current_id not in ids or ids.index(current_id) + 1 >= len(ordered):
        return None
    nxt = ordered[ids.index(current_id) + 1]
    return nxt['id'] if str(nxt['end_date'])[:10] >= today.isoformat() else None


def choose_action(key, status, inactive_days, mark=.5, cycle_id=None, next_cycle_id=None):
    if mark >= LATE_MARK and cycle_id and next_cycle_id:
        return {'action_type': 'move_next_cycle', 'cycle_id': cycle_id, 'target_cycle_id': next_cycle_id}
    if inactive_days >= SILENT_DAYS:
        return {'action_type': 'nudge_owner', 'action_text': (
            f"Hi, {key} is still {status} and has had no recorded activity for {inactive_days:.0f} days. "
            "Could you share where it stands and what, if anything, is blocking it?")}
    return {'action_type': 'raise_priority'}
