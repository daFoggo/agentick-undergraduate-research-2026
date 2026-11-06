"""Read-only view of the TAWOS database for the stuck-cause agent's tools, cut at the time of the alert."""


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
