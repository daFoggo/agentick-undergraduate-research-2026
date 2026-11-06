# Project guide

Read `intent.md` first: it is the only source for the problem, scope, architecture and module plan.
`agentick-backend/AGENTS.md` holds the backend conventions. Work smallest-complete-change (ponytail); no new
experiments or method comparisons unless asked.

## Run

Git Bash, from the repo root:

- `scripts/stack.sh start|stop|restart|status|logs [svc]|build|down`: research DB (tawos, `localhost:15432`) and the
  Plane stack with the risk service (`http://localhost:31080`, risk health `http://127.0.0.1:31081/api/v1/health`).
  Never `down -v`: the volumes hold the restored data.
- Backups of databases, volumes, ignored artifacts and `.env` files: `migration_dump_20261106/` (see its `RESTORE.md`).

## Test

- research: in Docker (a local venv is blocked by Windows application control), see `research/README.md`
- backend: see `agentick-backend/README.md` (needs a disposable Postgres, `DATABASE_URL=... pytest`)

## Gotchas

- In Git Bash, `export MSYS_NO_PATHCONV=1` before `docker exec ... /var/run/...` paths.
- TAWOS `issue.assignee_id/priority/status/sprint_id` are final values; rebuild state at time t from `change_log`
  (field names vary in case: use `lower(field)`).
