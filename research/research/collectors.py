"""Five fixed SQL collectors. Each returns events {id, kind, ts, text}, none later than t; the LLM may only cite these ids.
Titles and comments are user text: the caller passes them as data."""
import re
from datetime import timedelta

from research.replay import DONE
from research.tawos_source import state_at, waits_on

KINDS = ('discussion', 'owner', 'blockers', 'sprint', 'history')
FIELDS = ('status', 'priority', 'assignee', 'sprint', 'story points')


def _title(title):
    """TAWOS titles arrive CSV-escaped: wrapped in quotes, inner quotes doubled."""
    return (title or '').strip('"').replace('""', '"')[:120]


def _ev(id, kind, ts, text, ref_key=None, safe_text=None):
    """ref_key/safe_text: set when the event is about ANOTHER issue; the backend shows safe_text to viewers outside its project."""
    return dict(id=id, kind=kind, ts=ts, text=text, ref_key=ref_key, safe_text=safe_text)


def discussion(cur, issue_id, t, n=8):
    cur.execute("select id, creation_date, author_id, coalesce(comment_text, comment, '') from tawos_raw.comment where "
                "issue_id=%s and creation_date<=%s order by creation_date desc limit %s", (issue_id, t, n))
    return [_ev(f'c-{i}', 'discussion', ts, f'user#{a}: {x[:400]}') for i, ts, a, x in reversed(cur.fetchall())]


def owner(cur, issue_id, t, days=7, n=5):
    """What the current assignee did on OTHER issues in the days before t."""
    a = state_at(cur, issue_id, t)['assignee_id']
    if not a or a < 0:
        return []
    cur.execute("select c.id, c.creation_date, i.id, i.issue_key, i.title, c.from_string, c.to_string from "
                "tawos_raw.change_log c join tawos_raw.issue i on i.id=c.issue_id where c.author_id=%s and "
                "c.issue_id<>%s and lower(c.field)='status' and c.creation_date<=%s and c.creation_date>%s::timestamptz-"
                "make_interval(days=>%s) order by c.creation_date desc limit %s", (a, issue_id, t, t, days, n))
    out = []
    for cid, ts, oid, key, title, f, to in cur.fetchall():
        prio = state_at(cur, oid, t)['priority']  # fetchall above is done, so the cursor is reusable
        out.append(_ev(f'o-{cid}', 'owner', ts, f'assignee user#{a} moved {key} "{_title(title)}" (priority {prio or "unknown"}) {f} -> {to}',
                       key, f'another issue of the assignee, priority {prio}, {f} -> {to}'))
    return out[::-1]


def blockers(cur, issue_id, t, depth=2):
    out, seen, todo = [], {issue_id}, [(issue_id, 1)]
    while todo:
        cur_id, d = todo.pop(0)
        for b in waits_on(cur, cur_id, t):
            if b['issue_id'] in seen:
                continue
            seen.add(b['issue_id'])
            st = state_at(cur, b['issue_id'], t)
            cur.execute("select title, creation_date from tawos_raw.issue where id=%s", (b['issue_id'],))
            title, created = cur.fetchone()
            out.append(_ev(f"b-{b['issue_id']}", 'blockers', created,
                           f"level {d}: {b['key']} \"{_title(title)}\" ({b['link']}) is "
                           f"{'resolved' if b['resolved'] else 'open'}, status {st['status']}, priority {st['priority']}",
                           b['key'], f"a linked issue, {'resolved' if b['resolved'] else 'open'}, priority {st['priority']}"))
            if d < depth and not b['resolved']:
                todo.append((b['issue_id'], d + 1))
    return out


def _sprint_stats(cur, issue_id, t):
    """The sprint the issue was in at t (from the log, not the final column) and how far along it is; dates may be missing."""
    ids = state_at(cur, issue_id, t)['sprint_ids']
    if not ids:
        return None
    cur.execute("select id, name, start_date, end_date from tawos_raw.sprint where id=any(%s) "
                "order by start_date desc nulls last limit 1", (list(ids),))
    sid, name, start, end = cur.fetchone()
    cur.execute("select count(*), count(*) filter (where resolution_date<=%s) from tawos_raw.issue where sprint_id=%s "
                "and creation_date<=%s", (t, sid, t))  # shortcut: final membership, see BACKLOG #2
    total, done = cur.fetchone()
    span = (end - start).total_seconds() if start and end else 0
    frac = min(max((t - start).total_seconds() / span, 0), 1) if span > 0 else None
    return dict(sid=sid, name=name, start=start, total=total, done=done, frac=frac)


def sprint(cur, issue_id, t):
    st = _sprint_stats(cur, issue_id, t)
    if not st:
        return []
    elapsed = f"{st['frac']:.0%} of the sprint elapsed, " if st['frac'] is not None else ''
    return [_ev(f"s-{st['sid']}", 'sprint', min(st['start'], t) if st['start'] else t,
                f"{st['name']}: {elapsed}{st['done']} of {st['total']} issues resolved, {st['total'] - st['done']} still open")]


def history(cur, issue_id, t, n=8):
    cur.execute("select id, creation_date, field, from_string, to_string from tawos_raw.change_log where issue_id=%s "
                "and creation_date<=%s and lower(field)=any(%s) order by creation_date desc limit %s",
                (issue_id, t, list(FIELDS), n))
    out = [_ev(f'h-{i}', 'history', ts, f'{f}: {a or "(empty)"} -> {b or "(empty)"}') for i, ts, f, a, b in cur.fetchall()]
    cur.execute("select count(*) from tawos_raw.change_log where issue_id=%s and creation_date<=%s and "
                "field='Sprint' and coalesce(to_string,'')<>''", (issue_id, t))
    moves = cur.fetchone()[0]
    if moves and moves > 1:
        out.append(_ev(f'h-carry-{issue_id}', 'history', t, f'added to a sprint {moves} times before now (carried over)'))
    return out[::-1]


def collect(cur, issue_id, t):
    """All events for one issue at time t, oldest first inside each kind."""
    return [e for f in (discussion, owner, blockers, sprint, history) for e in f(cur, issue_id, t)]


DONE_WORDS = re.compile(r'\b(done|fixed|merged|completed|resolved|deployed|released)\b', re.I)
# shortcuts, tuned by eye: an overloaded sprint is >= half over with >= 60% still open; a comment counts as "done" when it
# says so within 3 days of t. Both are notes next to the diagnosis, never causes of this issue.
OVERLOAD_AFTER, OVERLOAD_OPEN, DONE_WITHIN = .5, .6, timedelta(days=3)


def notes(cur, issue_id, t, events):
    """Two states shown beside the diagnosis (not causes of the issue): [{kind, text, event_ids}], all from events <= t."""
    out, st = [], _sprint_stats(cur, issue_id, t)
    if st and st['frac'] is not None and st['total'] >= 5 and st['frac'] >= OVERLOAD_AFTER             and (st['total'] - st['done']) / st['total'] >= OVERLOAD_OPEN:
        out.append(dict(kind='sprint_overload', event_ids=[f"s-{st['sid']}"],
                        text=f"{st['total'] - st['done']} of {st['total']} issues of {st['name']} are still open with "
                             f"{st['frac']:.0%} of the sprint elapsed"))
    if (state_at(cur, issue_id, t)['status'] or '').lower() not in DONE:
        said = [e for e in events if e['kind'] == 'discussion' and t - e['ts'] <= DONE_WITHIN and DONE_WORDS.search(e['text'])]
        if said:
            word = DONE_WORDS.search(said[-1]['text']).group(1).lower()
            out.append(dict(kind='done_not_updated', event_ids=[said[-1]['id']],  # a keyword, not a verdict: wording says "may"
                            text=f'it may already be done: a comment in the last 3 days says "{word}" and the status is still open'))
    return out
