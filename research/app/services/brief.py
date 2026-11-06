"""Pure pieces of the Plane brief: the "why" block and the final action. Kept apart from post_briefs.py so they are tested."""
import html


def why(card):
    return _why(card) + _notes(card)


def _notes(card):
    items = ''.join(f"<li>{html.escape(n['text'])}</li>" for n in card.get('notes', []))
    return f'<p>Also noted:</p><ul>{items}</ul>' if items else ''


def _why(card):
    if card['unknown']:
        ask = card['missing_info'] or 'Ask the assignee what is holding it up.'
        return f"<p><b>Why it may be late:</b> not clear from the recorded activity. {html.escape(ask)}</p>"
    out = '<p><b>Why it may be late</b> (each point cites what was recorded before the alert)</p><ul>'
    for h in card['hypotheses']:
        cites = ''.join(f"<li><i>{html.escape(e['text'][:300])}</i></li>" for e in h['evidence'][:4])
        out += f"<li><b>{html.escape(h['label'])}</b>: {html.escape(h['reason'])}<ul>{cites}</ul></li>"
    ask = f"<p>Still unknown: {html.escape(card['missing_info'])}</p>" if card['missing_info'] else ''
    return out + '</ul>' + ask


def final_action(rules, card):
    """The rules' action, unless the diagnosis proposes a reminder or a priority raise. A move to the next cycle chosen by
    the rules stays: only they know the cycles, and little of the sprint is left."""
    if rules['action_type'] == 'move_next_cycle':
        return rules
    proposed = card['action']['type']
    if proposed == 'nudge_owner':
        return {'action_type': 'nudge_owner', 'action_text': card['action']['text']}
    if proposed == 'raise_priority':
        return {'action_type': 'raise_priority'}
    return rules
