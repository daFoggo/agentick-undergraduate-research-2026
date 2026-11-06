import json

from app.services.stuck_diagnosis import diagnose, keyword_cause

FACTS = dict(
    key='IS-7', status='In Progress', inactive_days=6.2,
    description='Add retry to the pool config loader.',
    comments=['Patch is ready, waiting for review from the QA team.', 'Still failing on windows.'],
    links=[dict(key='IS-9', kind='Blocked by', resolved=False), dict(key='IS-3', kind='Blocked by', resolved=True)])


class Client:
    def __init__(self, reply=None, error=None):
        self.reply, self.error = reply, error

    def complete(self, messages, **kw):
        if self.error:
            raise self.error
        return {'choices': [{'message': {'content': self.reply}}], 'usage': {'cost': .0002}}


def run(**d):
    return diagnose(Client(json.dumps(d)), FACTS)


TEXT = 'Hi, IS-7 has had no activity for 6 days and looks stuck. Is the QA review done?'


def test_a_cause_with_a_verbatim_quote_is_accepted():
    r, meta = run(cause='waiting_on_person', quote='waiting for review from the QA team', action_text=TEXT)
    assert r['cause'] == 'waiting_on_person' and meta['source'] == 'agent' and meta['quote_grounded'] is True


def test_the_quote_is_matched_loosely_on_case_and_spaces_but_never_invented():
    ok, _ = run(cause='waiting_on_person', quote='Waiting  for REVIEW from the qa team', action_text=TEXT)
    assert ok['cause'] == 'waiting_on_person'
    bad, meta = run(cause='waiting_on_person', quote='the reviewer said it is fine', action_text=TEXT)
    assert bad['cause'] == 'no_signal' and meta['quote_grounded'] is False and meta['source'] == 'rules'


def test_a_blocker_must_be_a_real_open_link():
    text = 'Hi, IS-7 is blocked by IS-9 and has been idle 6 days. When will IS-9 land?'
    ok, _ = run(cause='blocked_by_issue', blocker_key='IS-9', action_text=text)
    assert ok['cause'] == 'blocked_by_issue' and ok['blocker_key'] == 'IS-9'
    for key in ('IS-3', 'IS-99'):  # already resolved, or not linked at all
        r, _ = run(cause='blocked_by_issue', blocker_key=key, action_text=text.replace('IS-9', key))
        assert r['cause'] == 'no_signal'


def test_text_with_a_link_a_mention_or_a_wrong_issue_is_refused():
    for text in ('Hi IS-7, see http://x.io, 6 days idle', 'Hi @qa, IS-7 is idle for 6 days, review?', 'Is it done yet?'):
        r, _ = run(cause='waiting_on_person', quote='waiting for review', action_text=text)
        assert r['cause'] == 'no_signal'


def test_no_signal_is_a_valid_answer_and_errors_fall_back_to_it():
    r, meta = run(cause='no_signal')
    assert r['cause'] == 'no_signal' and meta['source'] == 'agent'
    r, meta = diagnose(Client(error=RuntimeError('x')), FACTS)
    assert r['cause'] == 'no_signal' and meta['source'] == 'rules'


def test_keyword_baseline():
    assert keyword_cause(['it is blocked by the other patch']) == 'blocked_by_issue'
    assert keyword_cause(['waiting for review']) == 'waiting_on_person'
    assert keyword_cause(['should we do A or B?']) == 'needs_decision'
    assert keyword_cause(['done on my side']) == 'no_signal'
