# Backlog (known limits, fix later; each item says when it matters)

| # | Item | Why it is open | When to fix |
|---|---|---|---|
| 1 | `issue_link` has no creation time | A link added after t cannot be excluded; only blockers created after t are dropped | Report: state it as a limit |
| 2 | Sprint membership at t uses `issue.sprint_id` (final) + creation <= t | Issues added to / removed from the sprint later are miscounted in the sprint-state event | If sprint chips look wrong in the review |
| 3 | ~5-7% of status/assignee at t differ from the final row | Log and final column use different status words; anonymised assignees | Not a bug; mention in report |
| 4 | gpt-6-luna JSON-schema support unverified | Output is validated by pydantic instead; invalid -> "chưa rõ" | If the invalid rate is high on the live run |
| 5 | Evidence of other issues shows titles without a per-viewer check in the job | Filter happens in the backend (M4) per viewer | M4 |
| 6 | Cause labels are not validated against human labels | No labelled set; out of scope for now | Report time |
| 7 | Old modules kept only for scoring (`alert_actions`, `alert_eval`, ...) | `score_sprints.py` imports them | After M5, prune what is unused |
