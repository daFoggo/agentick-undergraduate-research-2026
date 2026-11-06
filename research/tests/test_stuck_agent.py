import json

from app.services.stuck_agent import MAX_STEPS, run_agent

FACTS = dict(key='IS-7', status='In Progress', inactive_days=6.2,
             links=[dict(key='IS-9', kind='blocked by', resolved=False)])


class Source:
    """What the tools can read (as of the alert): comments by issue key, plus one linked issue's state."""
    def __init__(self):
        self.calls = []

    def comments(self, key):
        self.calls.append(('comments', key))
        return {'IS-7': ['Patch is ready, waiting for review from the QA team.'],
                'IS-9': ['Still stuck on the vendor answer.']}.get(key, [])

    def linked(self, key):
        self.calls.append(('linked', key))
        return {'key': key, 'resolved': False, 'inactive_days': 12.0, 'last_comment': 'Still stuck on the vendor answer.'}


def call(name, **args):
    return {'id': f'c{abs(hash((name, json.dumps(args))))}', 'type': 'function',
            'function': {'name': name, 'arguments': json.dumps(args)}}


class Client:
    """Replays scripted assistant turns, each a list of tool calls."""
    def __init__(self, turns):
        self.turns, self.seen = list(turns), []

    def complete(self, messages, tools=None, tool_choice=None, **kw):
        self.seen.append(messages)
        calls = self.turns.pop(0) if self.turns else []
        return {'choices': [{'message': {'role': 'assistant', 'content': None, 'tool_calls': calls}}],
                'usage': {'cost': .0002, 'prompt_tokens': 100, 'completion_tokens': 20}}


TEXT = 'Hi, IS-7 has had no activity for 6 days and looks stuck. Is the QA review done?'
SUBMIT = call('submit_diagnosis', cause='waiting_on_person', quote='waiting for review from the QA team', action_text=TEXT)


def test_the_agent_reads_comments_then_submits_a_grounded_diagnosis():
    src = Source()
    result, meta = run_agent(Client([[call('get_comments', issue_key='IS-7')], [SUBMIT]]), FACTS, src)
    assert result['cause'] == 'waiting_on_person' and meta['source'] == 'agent'
    assert [t['tool'] for t in meta['trace']] == ['get_comments', 'submit_diagnosis'] and src.calls == [('comments', 'IS-7')]


def test_it_can_follow_a_blocker_and_quote_what_it_found_there():
    text = 'Hi, IS-7 is blocked by IS-9 and has been idle for 6 days. Any news on the vendor answer?'
    submit = call('submit_diagnosis', cause='blocked_by_issue', blocker_key='IS-9', quote='Still stuck on the vendor answer.',
                  action_text=text)
    src = Source()
    result, _ = run_agent(Client([[call('get_linked_issue', issue_key='IS-9')], [submit]]), FACTS, src)
    assert result['cause'] == 'blocked_by_issue' and result['blocker_key'] == 'IS-9'


def test_a_tool_cannot_reach_an_issue_that_is_not_the_alerted_one_or_linked_to_it():
    src = Source()
    client = Client([[call('get_linked_issue', issue_key='IS-999')], [call('get_comments', issue_key='ZZ-1')], []])
    result, meta = run_agent(client, FACTS, src)
    assert src.calls == [] and result['cause'] == 'no_signal'
    assert all(t['error'] for t in meta['trace'] if t['tool'] != 'submit_diagnosis')


def test_a_quote_that_no_tool_returned_is_refused():
    bad = call('submit_diagnosis', cause='waiting_on_person', quote='the reviewer said it is fine', action_text=TEXT)
    result, meta = run_agent(Client([[call('get_comments', issue_key='IS-7')], [bad]]), FACTS, Source())
    assert result['cause'] == 'no_signal' and meta['source'] == 'rules'


def test_the_loop_is_bounded_and_an_unfinished_run_is_no_signal():
    turns = [[call('get_comments', issue_key='IS-7')]] * (MAX_STEPS + 3)
    client = Client(turns)
    result, meta = run_agent(client, FACTS, Source())
    assert result['cause'] == 'no_signal' and len(client.seen) == MAX_STEPS and meta['incomplete'] is True


def test_a_tool_result_is_data_and_is_capped():
    class Long(Source):
        def comments(self, key):
            return ['x' * 5000] * 20

    client = Client([[call('get_comments', issue_key='IS-7')], []])
    run_agent(client, FACTS, Long())
    tool_msg = next(m for m in client.seen[-1] if m.get('role') == 'tool')
    assert len(tool_msg['content']) < 4000


def test_no_tool_call_and_client_errors_fall_back_to_the_rules():
    assert run_agent(Client([[]]), FACTS, Source())[0]['cause'] == 'no_signal'

    class Broken:
        def complete(self, *a, **k):
            raise RuntimeError('down')

    result, meta = run_agent(Broken(), FACTS, Source())
    assert result['cause'] == 'no_signal' and meta['source'] == 'rules'
