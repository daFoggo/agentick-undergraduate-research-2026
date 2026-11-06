from app.services.brief import final_action, why

NUDGE = {'hypotheses': [], 'unknown': True, 'missing_info': None, 'action': {'type': 'nudge_owner', 'text': 'Hi X-1, update?'}}
RAISE = {'action_type': 'raise_priority'}
MOVE = {'action_type': 'move_next_cycle', 'cycle_id': 'a', 'target_cycle_id': 'b'}


def test_the_model_can_replace_a_priority_raise_but_never_a_move_chosen_by_the_rules():
    assert final_action(RAISE, NUDGE) == {'action_type': 'nudge_owner', 'action_text': 'Hi X-1, update?'}
    assert final_action(MOVE, NUDGE) == MOVE
    none = {**NUDGE, 'action': {'type': None, 'text': None}}
    assert final_action(RAISE, none) == RAISE


def test_user_text_is_escaped_in_the_why_block():
    card = {'unknown': False, 'missing_info': '<b>ask</b>', 'hypotheses': [
        {'label': 'L', 'reason': '<script>x</script>', 'evidence': [{'text': '<img src=x onerror=alert(1)>'}]}]}
    out = why(card)
    assert '<script>' not in out and '<img' not in out and '<b>ask</b>' not in out and '&lt;script&gt;' in out


def test_unknown_card_asks_instead_of_claiming():
    out = why({'unknown': True, 'missing_info': 'Ask QA', 'hypotheses': []})
    assert 'not clear' in out and 'Ask QA' in out
