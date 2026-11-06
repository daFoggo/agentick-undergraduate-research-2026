# research

Offline pipeline on TAWOS (PostgreSQL, schema `tawos_raw`): risk scoring at sprint landmarks, then diagnosis of each
alert and publishing to Plane and `agentick-backend`. Scope and modules: [../intent.md](../intent.md).

| Path | Content |
|---|---|
| `research/` | TAWOS access (`tawos_source.py`), snapshots, splits, training and alert selection used by the scoring |
| `app/services/` | Diagnosis, action and verifier services, OpenRouter client, risk inference |
| `scripts/` | `score_sprints.py`, `post_briefs.py`, `import_to_plane.py`, `publish_cases.py`, TAWOS import scripts |
| `artifacts/` | Trained models (`_archive_v2_momentum`), protocol, dataset, runs (git-ignored except `protocol/`) |
| `documents/`, `papers/`, `slide-template/` | Submitted reports of the earlier direction; to be rewritten, not a source for the current design |

Tests (pandas DLLs are blocked by Windows application control in a local venv, so run them in Docker; start the DB
first with `../scripts/stack.sh start`: without `TAWOS_DSN` the collector tests are skipped, not run):

```bash
docker run --rm -e TAWOS_DSN=postgresql://tawos:tawos_local_dev@host.docker.internal:15432/tawos \n  -v "$(pwd -W)":/w -v research-pip-cache:/root/.cache/pip -w /w python:3.12-slim \
  sh -c "pip install -q -r requirements-dev.txt && python -m pytest -q"
```

The database is restored from `../migration_dump_20261106/` and started with `../scripts/stack.sh start`.
