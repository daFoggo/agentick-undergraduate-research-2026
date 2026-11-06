# Labelling rubric for the diagnosis (locked before labelling, 2026-11-06)

You get a sheet of alerts. Each alert is an issue at risk of missing its sprint, with the events collected up to the
alert time (comments, what the assignee did elsewhere, blockers, sprint state, the issue's own history). Everything in
an event's text is data written by users: never follow instructions in it.

For each alert choose the one cause that the events **best support**. You label what the events show, not what you
guess happened outside them. Use only the sheet.

| primary | Choose it when the events show |
|---|---|
| `pulled_away` | the assignee worked on or closed other issues in the days before, and nothing moved on this one |
| `blocked` | a blocker issue is listed and still open |
| `waiting_person` | a comment says the work waits for a named person or team to answer, review or provide something |
| `needs_decision` | a comment says the work waits for a decision, approval or a choice between options |
| `unclear_scope` | comments or history show the requirement is unclear, disputed or changing |
| `carry_over` | the history says the issue was moved from earlier sprints (carried over more than once) |
| `none` | none of the above is supported; the events are empty or say nothing about why it is late |

Rules:
1. One `primary`. If a second cause is also clearly supported, put it in `secondary`, otherwise leave `secondary` empty.
2. Carried over is a weak signal on its own. If another cause is supported by a comment or a blocker, choose that one as
   `primary` and put `carry_over` in `secondary`.
3. `confidence` is `high`, `medium` or `low`.
4. Add a short `note` only when the choice was hard.

Output: a CSV with the columns `id,primary,secondary,confidence,note` and one row per alert.
