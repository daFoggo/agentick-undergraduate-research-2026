# Backlog

Every item is either closed (with the evidence) or a **limitation** of the current research: it cannot be fixed inside
the present scope and is stated in the report. The list of limitations is also in `intent.md`
("Hạn chế nghiên cứu hiện tại").

## Closed

| # | Item | How it was closed (2026-11-06) |
|---|---|---|
| 4 | The model's JSON-schema support was unverified | Replies are validated by pydantic; on the live run 0 of 81 calls failed, so the invalid-reply rate is 0% (the verifier dropped a hypothesis on 3 alerts) |
| 5 | Evidence of other issues showed titles without a per-viewer check | The backend redacts per viewer (M4, tested) |
| 7 | Old modules kept only for scoring | Every module in `research/research` and `app/services` is imported by scoring or the diagnosis path |
| 8 | Spectral lint and `tsc` not run | Spectral: 0 errors (warnings only: missing operation descriptions and `servers`). `tsc` in Docker on the whole web app: 0 errors |
| 12 | A reminder drafted by the model could name an issue of another project | `verify` drops a reminder that contains the key of an issue outside the alert's project; tested |
| 13 | `post_briefs` had no retry | `app/services/http_retry.py`: 3 tries on a dropped connection or 502/503/504; tested |
| 16 | A missing status was worded as "is still unknown" | Reminder text omits the status when it is missing; tested |
| 18 | The Analytics project filter did not reach the Delivery risk tab | `GET /insights/summary?project_ids=` narrows, never widens; tested |

## Limitations of the current research

| # | Limitation | Effect |
|---|---|---|
| 1 | `issue_link` has no creation time | A link added after t cannot be excluded; only blockers created after t are dropped |
| 2 | Sprint membership at t uses `issue.sprint_id` (final value) and creation <= t | Issues added to or removed from the sprint later are miscounted in the sprint-state event |
| 3 | 5-7% of status/assignee at t differ from the final row | The log and the final column use different status words; assignees are anonymised |
| 6 | Cause labels are not checked against human labels | No labelled set: no accuracy figure for the diagnosis |
| 9 | `move_next_cycle` is chosen by the rules, never by the model | Only the rules know the cycles |
| 10 | The diagnosis prompt is tuned on about 11 live cases | Cost is about 0.0001 USD per alert; quality is not measured |
| 11 | `is dependent of` (446 links) and `requires` (52) are left out of the waits-on map | The direction cannot be confirmed from the data (creation order is about 50/50) |
| 14 | `done_not_updated` is a keyword match (done/fixed/merged/... in a comment of the last 3 days, status not done) | About 1 in 3 matches is not a statement that the work is finished; wording says "may already be done" and cites the comment |
| 15 | `sprint_overload` thresholds (>= 50% elapsed, >= 60% open, >= 5 issues) were chosen by eye | Not tuned; no labelled set |
| 17 | Neither M8 note fired on the live alerts of ISP | Alerts are raised at the 0-75% marks, when overload is rare; the card layout was checked with a note written by hand, and both notes fire in the collectors test on random issues |
| 19 | Statistics are summed in Python per request | Fine for thousands of alerts (marked `shortcut:` in `insights.py`); use SQL group-by at the hundred-thousands |
| 20 | 43 of 81 flagged items have "carried over" as the top reason | A weak signal on its own; alerts sort by score only |
| 21 | The view "Flagged by the risk check" was made by hand for project ISP | Plane's public API has no views endpoint; repeat for each scored project |
| 22 | No imported work item has an assignee in Plane | TAWOS assignees are anonymised ids with no Plane user, so "Your work" lists nothing until people are assigned |
| 23 | Tested on one project (IS) with 81 alerts | No cross-project or long-run evidence |
