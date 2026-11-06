# Backlog (known limits, fix later; each item says when it matters)

| # | Item | Why it is open | When to fix |
|---|---|---|---|
| 1 | `issue_link` has no creation time | A link added after t cannot be excluded; only blockers created after t are dropped | Report: state it as a limit |
| 2 | Sprint membership at t uses `issue.sprint_id` (final) + creation <= t | Issues added to / removed from the sprint later are miscounted in the sprint-state event | If sprint chips look wrong in the review |
| 3 | ~5-7% of status/assignee at t differ from the final row | Log and final column use different status words; anonymised assignees | Not a bug; mention in report |
| 4 | gpt-6-luna JSON-schema support unverified | Output is validated by pydantic instead; invalid -> "chưa rõ" | If the invalid rate is high on the live run |
| 5 | Evidence of other issues shows titles without a per-viewer check in the job | Filter happens in the backend (M4) per viewer | M4 |
| 6 | Cause labels are not validated against human labels | No labelled set; out of scope for now | Report time |
| 7 | ~~Old modules kept only for scoring~~ closed 2026-11-06: every module in `research/research` and `app/services` is imported by scoring or the diagnosis path | - | - |
| 8 | Spectral lint run 2026-11-06: 0 errors, 8 warnings (missing operation descriptions and `servers`, on all routes). `tsc` for the web file not run: `plane/` has no `node_modules`, a typecheck needs a full pnpm install; the card was checked in the browser instead | Warnings: if CI turns them into errors. tsc: when the web app is built from source | 
| 9 | `move_next_cycle` is never proposed by the model's card | The rules know the cycles; the model's choice is only used for `nudge_owner` / `raise_priority` | If the card should explain a move |
| 10 | The diagnosis prompt is tuned on 5 + 6 live cases only | No labelled set (see 6); cost ~0.0001 USD per alert | Report time |
| 11 | `is dependent of` (446 links) and `requires` (52) left out of the waits-on map | Direction not confirmable from data (creation order is ~50/50) | Only if blockers look incomplete on the live run |
| 12 | Redaction hides other-project text but not the nudge text the model drafts | The nudge is posted on this issue for people who can see it | If cross-project links ever appear (0 of 9159 now) |
| 13 | ~~post_briefs has no retry~~ closed 2026-11-06: `app/services/http_retry.py` (3 tries on dropped connection or 502/503/504), tested | - | - |
| 14 | The `done_not_updated` note is a keyword match (done/fixed/merged/... in a comment of the last 3 days, status not done); about 1 in 3 matches is not a statement that the work is finished | Wording says "may already be done" and cites the comment; precision is not measured | Report time, or if the note looks noisy in review |
| 15 | `sprint_overload` thresholds (>= 50% elapsed, >= 60% open, >= 5 issues) chosen by eye, not tuned | No labelled set | Report time |
| 16 | When the status at t is unknown, the rule-written reminder says "IS-1365 is still unknown" (seen on ISP-449) | `choose_action` puts the status word into the text without a case for "unknown" | Next pass on `alert_actions.py` |
| 17 | M8 notes never fired on the 30 live alerts of ISP (alerts come at the 0-75% marks); the card layout was checked with a note written by hand into the risk DB, and both kinds fire in the collectors test on random issues | Sprint overload is rare early in a sprint | Report time |
