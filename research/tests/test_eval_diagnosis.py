import pytest

from research.eval_diagnosis import kappa, model_cause, score, shuffled_ids


def row(label, model, model_all=None, label2=''):
    return dict(label=label, model=model, model_all=model_all if model_all is not None else (
        [] if model == 'none' else [model]), label2=label2)


def test_model_cause_is_none_for_an_unknown_card():
    assert model_cause(dict(hypotheses=[], unknown=True)) == 'none'
    assert model_cause(dict(hypotheses=[dict(cause='blocked'), dict(cause='carry_over')])) == 'blocked'


def test_kappa_is_one_for_full_agreement_and_zero_for_chance_level():
    assert kappa([('a', 'a'), ('b', 'b')]) == 1.0
    assert kappa([('a', 'a'), ('a', 'a')]) == 1.0  # a single label on both sides
    assert kappa([('a', 'a'), ('a', 'b'), ('b', 'a'), ('b', 'b')]) == 0.0
    with pytest.raises(ValueError):
        kappa([])


def test_score_counts_agreement_abstention_and_per_cause():
    rows = [row('blocked', 'blocked'), row('carry_over', 'blocked'), row('none', 'none'), row('none', 'carry_over'),
            row('carry_over', 'carry_over', ['carry_over', 'blocked'])]
    s = score(rows)
    assert s['n'] == 5 and s['top1'] == 3 / 5
    assert s['top1_when_both_name_a_cause'] == 2 / 3  # rows 1, 2 and 5
    assert s['model_unknown'] == 1 and s['label_none'] == 2
    assert s['per_cause']['blocked'] == dict(said=2, labelled=1, hit=1, precision=.5, recall=1.0)
    assert s['per_cause']['pulled_away']['precision'] is None
    assert s['confusion']['carry_over->blocked'] == 1


def test_any_match_accepts_the_second_label_and_any_model_cause():
    rows = [row('blocked', 'carry_over', ['carry_over', 'blocked']), row('blocked', 'carry_over', label2='carry_over')]
    assert score(rows)['any_match'] == 1.0


def test_sheet_ids_are_stable_and_hide_the_order():
    keys = ['ISP-3', 'ISP-1', 'ISP-2']
    assert shuffled_ids(keys) == shuffled_ids(reversed(keys))
    assert sorted(shuffled_ids(keys)) == ['A001', 'A002', 'A003'] and set(shuffled_ids(keys).values()) == set(keys)
