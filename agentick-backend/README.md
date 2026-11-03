# agentick-backend

FastAPI backend scaffold following the [Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/) structure, with PostgreSQL via SQLAlchemy + Alembic, served through Docker Compose. OpenAPI document (3.1, FastAPI's default) is served at `/api/v1/openapi.json` and validated in CI — see `scripts/validate_openapi.py`.

## Structure

```
app/
  main.py            # FastAPI app, middleware, router wiring
  api_router.py       # aggregates versioned routers
  core/config.py      # pydantic-settings config
  db/                 # SQLAlchemy engine/session/declarative base
  models/              # ORM models
  schemas/             # Pydantic request/response schemas
  routers/             # public path operations (health, items, auth, /me)
  internal/            # internal/admin-only routers
  core/security.py     # password hashing + JWT issuing/decoding
  dependencies.py       # shared dependencies (X-Token check, get_current_user, require_role)
migrations/            # Alembic environment + versions
```

## Run with Docker

```bash
cp .env.example .env
docker compose up --build
```

- API: http://localhost:11030
- Swagger UI: http://localhost:11030/docs
- OpenAPI schema: http://localhost:11030/api/v1/openapi.json

On container start, `alembic upgrade head` runs automatically before `uvicorn`.

## Local development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # adjust DATABASE_URL to point at localhost
alembic upgrade head
uvicorn app.main:app --reload
```

## Running tests

Tests hit a real Postgres (no mocked DB) — point `DATABASE_URL` at any disposable instance:

```bash
docker run -d --rm --name agentick-backend-testdb \
  -e POSTGRES_DB=agentick_test -e POSTGRES_USER=agentick -e POSTGRES_PASSWORD=agentick_test \
  -p 15999:5432 postgres:16-alpine

DATABASE_URL="postgresql+psycopg://agentick:agentick_test@localhost:15999/agentick_test" \
  pytest

docker stop agentick-backend-testdb
```

`tests/conftest.py` creates/drops the schema per session and truncates tables between tests.

## Auth

OAuth2 password flow + JWT, owned entirely by this backend (see `AGENTS.md` for the
design decisions — HS256, bcrypt, access/refresh token split):

```bash
curl -X POST localhost:11030/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"jane@example.com","password":"correct-password","name":"Jane"}'

curl -X POST localhost:11030/api/v1/auth/token \
  -d 'username=jane@example.com&password=correct-password'

curl localhost:11030/api/v1/me -H "Authorization: Bearer <access_token>"

curl -X POST localhost:11030/api/v1/auth/refresh \
  -H 'Content-Type: application/json' -d '{"refresh_token":"<refresh_token>"}'
```

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
