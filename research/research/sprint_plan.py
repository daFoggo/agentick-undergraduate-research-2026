"""Sprint-level plan (M14): how many of the open issues will probably not finish, and which ones to move to the next cycle.

All numbers come from code, never from a model: the share comes from earlier sprints of the same project at the same point
of the sprint, the ranking from the risk scores, and an issue that waits on a moved issue moves with it.
"""
MIN_SPRINTS = 3   # fewer earlier sprints than this and a share would be noise
MIN_OPEN = 15     # same, counted in issues


def history_rate(past):
    """Share of the issues still open at this point that were not finished, over earlier sprints [(open, unfinished)].
    None when the history is too short to trust."""
    total = sum(o for o, _ in past)
    if len(past) < MIN_SPRINTS or total < MIN_OPEN:
        return None
    return sum(u for _, u in past) / total


def make_plan(scores, rate, waits_on=None):
    """scores {issue: risk score} for the open issues of one sprint; rate from history_rate; waits_on {issue: issues it waits on}.
    Returns None when there is nothing to move, else {budget, expected_unfinished, move: [(issue, 'risk'|'follows')]}.

    The budget is the expected number of unfinished issues. The riskiest `budget` issues are moved; then every issue that
    waits on a moved one follows, because it cannot finish either, so the plan can exceed the budget."""
    if rate is None or not scores:
        return None
    expected = rate * len(scores)
    budget = round(expected)
    if budget == 0:
        return None
    order = sorted(scores, key=lambda i: -scores[i])
    chosen = order[:budget]
    follows, waits_on = [], waits_on or {}
    grew = True
    while grew:  # shortcut: a quadratic fixpoint, fine for a sprint of tens of issues; use a graph walk beyond thousands
        grew = False
        for i in order:
            if i not in chosen and i not in follows and any(b in chosen or b in follows for b in waits_on.get(i, ())):
                follows.append(i)
                grew = True
    return dict(budget=budget, expected_unfinished=expected,
                move=[(i, 'risk') for i in chosen] + [(i, 'follows') for i in follows])
