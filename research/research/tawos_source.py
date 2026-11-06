"""Read-only view of the TAWOS database, cut at the time t of the alert.

`issue.assignee_id/priority/status/sprint_id` are FINAL values, so state at t is rebuilt from `change_log`.
"""

# issue_link.description (not name: names are inconsistent) read from the row's own issue_id, meaning "this issue waits
# on target_issue_id". Symmetric rows ("Blocked", "Dependent") carry no direction and are left out.
WAITS_ON = frozenset({
    'is blocked by', 'depends on', 'depends upon', 'is dependent of', 'requires',
    'fs-depends on', 'ff-depends on', 'ss-depends on', 'has to be done after', 'is triggered by'})
_FIELDS = ('assignee', 'priority', 'status', 'sprint')


def _ids(text):
    return tuple(int(x) for x in (text or '').replace(' ', '').split(',') if x.isdigit())


def state_at(cur, issue_id, t):
    """assignee_id, priority, status, sprint_ids of an issue at time t, rebuilt from the change log."""
    cur.execute("select assignee_id, priority, status, sprint_id from tawos_raw.issue where id=%s", (issue_id,))
    a, p, st, sp = cur.fetchone()
    out = dict(assignee_id=a, priority=p, status=st, sprint_ids=(sp,) if sp else ())  # no change ever: final = at t
    cur.execute("select lower(field), creation_date, from_value, from_string, to_value, to_string from "
                "tawos_raw.change_log where issue_id=%s and lower(field)=any(%s) order by creation_date, id",
                (issue_id, list(_FIELDS)))
    rows = cur.fetchall()
    # assignee text that is not an id ("<UNKNOWN_USER>", anonymised projects) still means "assigned": -1
    one = lambda x: _ids(x)[0] if _ids(x) else (-1 if x else None)
    for f, key, before, after in (('assignee', 'assignee_id', lambda r: one(r[2]), lambda r: one(r[4])),
                                  ('priority', 'priority', lambda r: r[3] or None, lambda r: r[5] or None),
                                  ('status', 'status', lambda r: r[3] or None, lambda r: r[5] or None)):
        ch = [r for r in rows if r[0] == f]
        if ch:
            out[key] = before(ch[0])  # until the first change the value was that change's "from"
            for r in ch:
                if r[1] <= t:
                    out[key] = after(r)
    ch = [r for r in rows if r[0] == 'sprint']
    if ch:  # change_log holds Jira sprint ids; map them to sprint.id within the issue's project
        cur.execute("select jiraid, id from tawos_raw.sprint where project_id=(select project_id from tawos_raw.issue "
                    "where id=%s)", (issue_id,))
        internal = dict(cur.fetchall())
        jira = _ids(ch[0][2])
        for ts in sorted({r[1] for r in ch if r[1] <= t}):  # a move is a pair of rows at one timestamp
            jira = {i for r in ch if r[1] == ts for i in _ids(r[4])}
        out['sprint_ids'] = tuple(sorted(internal[j] for j in jira if j in internal))
    return out


def waits_on(cur, issue_id, t):
    """Issues this one waits on that already existed at t, with whether each was resolved by t."""
    cur.execute("select b.id, b.issue_key, il.description, b.resolution_date from tawos_raw.issue_link il join "
                "tawos_raw.issue b on b.id=il.target_issue_id where il.issue_id=%s and lower(il.description)=any(%s) "
                "and b.creation_date<=%s", (issue_id, sorted(WAITS_ON), t))
    return [dict(issue_id=i, key=k, link=d, resolved=bool(r and r <= t)) for i, k, d, r in cur.fetchall()]


class TawosSource:
    """What the agent's tools may read: everything is cut at `cutoff`, the time of the alert."""

    def __init__(self, cur, cutoff):
        self.cur, self.cutoff = cur, cutoff

    def _id(self, key):
        self.cur.execute("select id, resolution_date, creation_date from tawos_raw.issue where issue_key=%s", (key,))
        return self.cur.fetchone()

    def comments(self, key):
        row = self._id(key)
        self.cur.execute("select comment_text from tawos_raw.comment where issue_id=%s and creation_date<=%s "
                         "order by creation_date desc limit 5", (row[0], self.cutoff))
        return [c[0] or '' for c in self.cur.fetchall()][::-1]

    def linked(self, key):
        issue, resolved_at, created = self._id(key)
        self.cur.execute("select max(d) from (select max(creation_date) d from tawos_raw.comment where issue_id=%s and "
                         "creation_date<=%s union all select max(creation_date) from tawos_raw.change_log where "
                         "issue_id=%s and creation_date<=%s) t", (issue, self.cutoff, issue, self.cutoff))
        last = self.cur.fetchone()[0] or created
        text = (self.comments(key) or [''])[-1]
        return dict(key=key, resolved=bool(resolved_at and resolved_at <= self.cutoff),
                    inactive_days=round((self.cutoff - last).total_seconds() / 86400, 1), last_comment=text[:300])
