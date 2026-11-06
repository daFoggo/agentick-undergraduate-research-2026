"""Agreement between the diagnosis and an independent label. Pure functions; scripts/eval_diagnosis.py does the I/O.

A label says which cause the collected events SUPPORT, not what truly delayed the work: TAWOS holds no ground truth for
that. 'none' means no cause is supported (the diagnosis says 'unknown' then).
"""
import random
from collections import Counter

CAUSES = ('pulled_away', 'blocked', 'waiting_person', 'needs_decision', 'unclear_scope', 'carry_over')
LABELS = CAUSES + ('none',)


def model_cause(card):
    """Top cause of a diagnosis card, 'none' when the card is unknown."""
    return card['hypotheses'][0]['cause'] if card.get('hypotheses') else 'none'


def kappa(pairs):
    """Cohen's kappa of (a, b) label pairs; 1.0 when both sides always agree on a single label."""
    n = len(pairs)
    if n == 0:
        raise ValueError('no pairs')
    agree = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    chance = sum(ca[x] * cb[x] for x in set(ca) | set(cb)) / n ** 2
    return 1.0 if chance == 1 else (agree - chance) / (1 - chance)


def score(rows):
    """rows: dicts with 'model' (top cause), 'model_all' (all causes of the card), 'label', 'label2' (or '').
    Returns the numbers the report quotes."""
    n = len(rows)
    pairs = [(r['label'], r['model']) for r in rows]
    both = [r for r in rows if r['label'] != 'none' and r['model'] != 'none']
    per_cause = {}
    for c in CAUSES:
        tp = sum(1 for r in rows if r['model'] == c and r['label'] == c)
        said, labelled = sum(r['model'] == c for r in rows), sum(r['label'] == c for r in rows)
        per_cause[c] = dict(said=said, labelled=labelled, hit=tp, precision=tp / said if said else None,
                            recall=tp / labelled if labelled else None)
    majority = Counter(r['label'] for r in rows).most_common(1)[0]
    return dict(
        n=n,
        top1=sum(a == b for a, b in pairs) / n,
        top1_when_both_name_a_cause=(sum(r['label'] == r['model'] for r in both) / len(both)) if both else None,
        any_match=(sum(bool({r['label'], r['label2']} & set(r['model_all'])) for r in both) / len(both))
        if both else None,
        kappa=kappa(pairs),
        model_unknown=sum(r['model'] == 'none' for r in rows),
        label_none=sum(r['label'] == 'none' for r in rows),
        majority_label=majority[0], majority_share=majority[1] / n,
        per_cause=per_cause,
        confusion={f'{a}->{b}': k for (a, b), k in sorted(Counter(pairs).items())},
    )


def shuffled_ids(keys, seed=20261106):
    """Anonymous sheet ids in a fixed random order: {'A001': key, ...}. The order must not follow the model's output."""
    order = sorted(keys)
    random.Random(seed).shuffle(order)
    return {f'A{i + 1:03d}': k for i, k in enumerate(order)}
