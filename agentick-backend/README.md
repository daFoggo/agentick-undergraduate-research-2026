# agentick-backend

FastAPI backend (the [Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/) structure, PostgreSQL via SQLAlchemy + Alembic, Docker) that holds the sprint-risk services built for this research. **Plane is the main system; this backend is an external service next to it.** It calls Plane over REST and Plane's web UI calls it through Plane's own proxy at `/risk`. It has no user accounts: a user is whoever Plane says owns the session cookie.

OpenAPI (3.1) is served at `/openapi.json` when `ENVIRONMENT` is `local` or `staging` and validated in CI (`scripts/validate_openapi.py`).

## What it does

| Service | What | Endpoints |
|---|---|---|
| Alerts | Sprint-risk alerts published by the offline research job, and the human decision on each: approve (priority to High), dismiss, undo. Nothing changes in Plane until a person presses a button. | `PUT /alerts`, `GET /alerts/{id}`, `POST /alerts/{id}/decision`, `POST /alerts/{id}/undo` |
| Cases | Finished cases most similar to a work item (small / medium / large, how long they took, and a link to a Plane page). Reference only, no estimate. | `PUT /cases`, `GET /cases/{id}` |

All under `/api/v1`. `{id}` is the Plane work item UUID.

```
research/ (offline job)                 Plane                           this backend
post_briefs.py   --> comment by bot     work items, comments, priority
                 -------------------------------------------------->   PUT /alerts   (bearer INGEST_TOKEN)
publish_cases.py --> project "Past cases"
                 -------------------------------------------------->   PUT /cases    (bearer INGEST_TOKEN)
browser (forked Plane web) --- /risk/api/v1/... --- Plane proxy ------>   session cookie checked against Plane:
                                                                         may this user see this work item?
                           <---- priority change + comment ----------   Plane REST as the bot user
```

Alerts and decisions are PostgreSQL tables (`alerts`, `alert_decisions`, `similar_cases`). `alert_decisions` is append-only; the current state of an alert is its last row. `POST .../decision` and `.../undo` lock the alert row, so two people deciding at once go one after the other.

## Structure

```
app/
  main.py              # FastAPI app, middleware, router wiring
  api_router.py        # aggregates versioned routers
  core/                # config (pydantic-settings), exceptions, bearer check
  db/                  # SQLAlchemy engine/session/declarative base
  models/              # ORM models (Alert, AlertDecision, SimilarCases)
  schemas/             # Pydantic request/response schemas
  routers/             # health, alerts, cases
  integrations/plane.py  # Plane REST client (bot key for writes, user cookie for "who is this / may they see it")
  dependencies.py      # Plane session, ingest token, Plane client
migrations/            # Alembic environment + versions
tests/                 # real Postgres, Plane faked at the httpx transport, OpenAPI contract tests
```

## Configuration (env)

| Variable | Meaning |
|---|---|
| `DATABASE_URL` | PostgreSQL (`postgresql+psycopg://...`) |
| `PLANE_BASE_URL` | Plane API base (in Plane's compose: `http://api:8000`) |
| `PLANE_API_KEY` | API token of the bot user (member of the workspace and projects, not admin) |
| `PLANE_WORKSPACE_SLUG` | default `ript` |
| `INGEST_TOKEN` | bearer token of the offline job that publishes alerts and cases |
| `ENVIRONMENT` | `production` hides `/docs` and `/openapi.json` (the service is reachable through Plane's public proxy) |

## Run inside the Plane stack

`plane/deployments/cli/community/docker-compose.risk.yml` builds this directory, starts its own PostgreSQL (`risk-db`, volume `risk-db-data`, never Plane's database) and routes `/risk/*` to it through Plane's proxy. Secrets live in that directory's git-ignored `.env`: `RISK_BOT_API_KEY`, `RISK_INGEST_TOKEN`, `RISK_DB_PASSWORD`.

```bash
cd plane/deployments/cli/community
docker compose --env-file .env -p plane -f docker-compose.yml -f docker-compose.risk.yml up -d --build
```

Always pass `-p plane`, and never run compose in a shell that has `DATABASE_URL` exported: compose lets a shell variable override `.env` and would recreate Plane's own API container with the wrong database.

On container start `alembic upgrade head` runs before `uvicorn`.

## Standalone development

```bash
python3.12 -m venv .venv && source .venv/bin/activate     # Python 3.12 is required (PEP 695 generics)
pip install -r requirements-dev.txt
cp .env.example .env   # DATABASE_URL points at localhost; set PLANE_* when you want to talk to a Plane
alembic upgrade head
uvicorn app.main:app --reload
```

## Running tests

Tests hit a real Postgres (no mocked DB); point `DATABASE_URL` at any disposable instance:

```bash
docker run -d --rm --name agentick-backend-testdb \
  -e POSTGRES_DB=agentick_test -e POSTGRES_USER=agentick -e POSTGRES_PASSWORD=agentick_test \
  -p 15999:5432 postgres:16-alpine

DATABASE_URL="postgresql+psycopg://agentick:agentick_test@localhost:15999/agentick_test" pytest

docker stop agentick-backend-testdb
```

`tests/conftest.py` creates/drops the schema per session and truncates tables between tests. Plane is faked in `tests/fake_plane.py`.

## Creating a migration

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

## Enforcing OpenAPI / RESTful conventions

OpenAPI itself only describes an API's syntax — it does not mandate REST style (naming,
status-code semantics, error shape). That part needs separate tooling, layered on top of
the schema FastAPI generates:

1. **Schema validity** — `python scripts/validate_openapi.py` validates the generated
   document against the OpenAPI JSON Schema (`openapi-spec-validator`).
2. **RESTful style lint** — `.spectral.yaml` defines rules (operationId required, tags
   required, kebab-case paths, no verbs in paths, error responses must have a schema).
   Run with:
   ```bash
   python scripts/export_openapi.py openapi.json
   npx --yes @stoplight/spectral-cli lint openapi.json --ruleset .spectral.yaml
   ```
3. **Contract tests** — `tests/test_openapi_contract.py` uses `schemathesis` to generate
   requests from the schema and verify the live app's responses actually match what the
   schema promises. Run with `pytest tests/test_openapi_contract.py`.

All three run in CI on every push touching this directory — see
`../.github/workflows/agentick-backend-ci.yml`.
