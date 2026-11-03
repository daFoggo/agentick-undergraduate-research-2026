#!/usr/bin/env bash
# Bash port of migrate_tawos_to_postgres.ps1 for Linux hosts without pwsh.
# Mirrors the same guards: refuses to overwrite an existing public/tawos_raw schema,
# verifies source row counts against the locked TAWOS v1.1 totals, and records
# an import manifest row with the archive's SHA-256 after a verified migration.
set -euo pipefail

SOURCE_CONTAINER="${1:-tawos-source-mysql}"
SOURCE_ROOT_PASSWORD="${2:-${MYSQL_ROOT_PASSWORD:-tawos_mysql_local}}"
SKIP_TARGET_EMPTY_CHECK="${SKIP_TARGET_EMPTY_CHECK:-0}"

get_setting() {
  local name="$1" default="$2"
  if [ -f .env ]; then
    local line
    line=$(grep -E "^\s*${name}\s*=" .env | tail -1 || true)
    if [ -n "$line" ]; then
      echo "${line#*=}" | sed -e 's/^["'"'"']//' -e 's/["'"'"']$//' -e 's/^\s*//' -e 's/\s*$//'
      return
    fi
  fi
  echo "$default"
}

POSTGRES_USER_V=$(get_setting POSTGRES_USER tawos)
POSTGRES_PASSWORD_V=$(get_setting POSTGRES_PASSWORD tawos_local_dev)
POSTGRES_DB_V=$(get_setting POSTGRES_DB tawos)

POSTGRES_CONTAINER=$(docker compose ps -q db)
if [ -z "$POSTGRES_CONTAINER" ]; then
  echo "PostgreSQL is not running. Start it with: docker compose up -d db" >&2
  exit 1
fi

SOURCE_STATE=$(docker inspect --format '{{.State.Running}}' "$SOURCE_CONTAINER" 2>/dev/null || true)
if [ "$SOURCE_STATE" != "true" ]; then
  echo "Source MySQL container '$SOURCE_CONTAINER' is not running." >&2
  exit 1
fi

MYSQL_AUTH=(-uroot)
if [ -n "$SOURCE_ROOT_PASSWORD" ]; then
  MYSQL_AUTH+=("-p${SOURCE_ROOT_PASSWORD}")
fi

SOURCE_ISSUE_COUNT=$(docker exec "$SOURCE_CONTAINER" mysql "${MYSQL_AUTH[@]}" -Nse 'SELECT COUNT(*) FROM TAWOS.Issue')
SOURCE_PROJECT_COUNT=$(docker exec "$SOURCE_CONTAINER" mysql "${MYSQL_AUTH[@]}" -Nse 'SELECT COUNT(*) FROM TAWOS.Project')
if [ "$SOURCE_ISSUE_COUNT" != "458232" ] || [ "$SOURCE_PROJECT_COUNT" != "39" ]; then
  echo "Source import is incomplete or not TAWOS v1.1: found $SOURCE_ISSUE_COUNT issues and $SOURCE_PROJECT_COUNT projects; expected 458232 and 39." >&2
  exit 1
fi

if [ "$SKIP_TARGET_EMPTY_CHECK" != "1" ]; then
  EXISTING_TABLES=$(docker exec "$POSTGRES_CONTAINER" psql -U "$POSTGRES_USER_V" -d "$POSTGRES_DB_V" -Atc \
    "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE' AND table_name <> 'alembic_version'")
  if [ "$EXISTING_TABLES" -gt 0 ]; then
    echo "Target database already has $EXISTING_TABLES public tables. Migration stopped to avoid overwriting data." >&2
    exit 1
  fi
  RAW_SCHEMA_COUNT=$(docker exec "$POSTGRES_CONTAINER" psql -U "$POSTGRES_USER_V" -d "$POSTGRES_DB_V" -Atc \
    "SELECT count(*) FROM information_schema.schemata WHERE schema_name IN ('tawos', 'tawos_raw')")
  if [ "$RAW_SCHEMA_COUNT" -gt 0 ]; then
    echo "A tawos/tawos_raw schema already exists. Migration stopped to avoid overwriting data." >&2
    exit 1
  fi
fi

MYSQL_MIGRATION_PASSWORD='tawos_local_migration'
GRANT_SQL="CREATE USER IF NOT EXISTS 'tawos_migrator'@'%' IDENTIFIED WITH mysql_native_password BY '${MYSQL_MIGRATION_PASSWORD}'; GRANT SELECT, SHOW VIEW, LOCK TABLES ON TAWOS.* TO 'tawos_migrator'@'%'; FLUSH PRIVILEGES;"
docker exec "$SOURCE_CONTAINER" mysql "${MYSQL_AUTH[@]}" -e "$GRANT_SQL"

NETWORK=$(docker inspect --format '{{range $name, $config := .NetworkSettings.Networks}}{{$name}}{{end}}' "$POSTGRES_CONTAINER")
if [ -z "$NETWORK" ]; then
  echo "Could not determine the Compose network for PostgreSQL." >&2
  exit 1
fi

SOURCE_NETWORKS=$(docker inspect --format '{{range $name, $config := .NetworkSettings.Networks}}{{$name}} {{end}}' "$SOURCE_CONTAINER")
if [[ "$SOURCE_NETWORKS" != *"$NETWORK"* ]]; then
  docker network connect "$NETWORK" "$SOURCE_CONTAINER"
fi

SOURCE_URL="mysql://tawos_migrator:${MYSQL_MIGRATION_PASSWORD}@${SOURCE_CONTAINER}:3306/TAWOS"
TARGET_URL="postgresql://${POSTGRES_USER_V}:${POSTGRES_PASSWORD_V}@db:5432/${POSTGRES_DB_V}"

echo "Starting one-time TAWOS v1.1 migration with pgloader."
echo "Source container: $SOURCE_CONTAINER"
echo "Destination database: $POSTGRES_DB_V"
LOADER_OUTPUT=$(docker run --rm --network "$NETWORK" \
  ghcr.io/dimitri/pgloader@sha256:a1d4a78e78a64e46cd3fc7dfc57d24eb91ffb1a5520f2b1f55631815e3658d6e \
  pgloader --verbose --on-error-stop --dynamic-space-size 8192 \
  --with 'workers = 2' --with 'concurrency = 1' --with 'prefetch rows = 500' \
  --with 'batch rows = 500' --with 'batch size = 8 MB' \
  "$SOURCE_URL" "$TARGET_URL" 2>&1) || true
echo "$LOADER_OUTPUT"
if echo "$LOADER_OUTPUT" | grep -qiE '^\s*ERROR\b|MYSQL-UNSUPPORTED-AUTHENTICATION|\bFATAL\b'; then
  echo "pgloader migration failed; inspect its output before retrying." >&2
  exit 1
fi

docker exec "$POSTGRES_CONTAINER" psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER_V" -d "$POSTGRES_DB_V" \
  -c 'ALTER SCHEMA tawos RENAME TO tawos_raw'

ZIP_PATH='data/raw/TAWOS-v1.1.sql.zip'
if [ ! -f "$ZIP_PATH" ]; then
  echo "Could not find dataset archive at $ZIP_PATH for the import manifest." >&2
  exit 1
fi
SOURCE_HASH=$(sha256sum "$ZIP_PATH" | awk '{print $1}')
ISSUE_COUNT=$(docker exec "$POSTGRES_CONTAINER" psql -U "$POSTGRES_USER_V" -d "$POSTGRES_DB_V" -Atc 'SELECT COUNT(*) FROM tawos_raw.issue')
PROJECT_COUNT=$(docker exec "$POSTGRES_CONTAINER" psql -U "$POSTGRES_USER_V" -d "$POSTGRES_DB_V" -Atc 'SELECT COUNT(*) FROM tawos_raw.project')
SPRINT_COUNT=$(docker exec "$POSTGRES_CONTAINER" psql -U "$POSTGRES_USER_V" -d "$POSTGRES_DB_V" -Atc 'SELECT COUNT(*) FROM tawos_raw.sprint')

if [ "$ISSUE_COUNT" != "$SOURCE_ISSUE_COUNT" ] || [ "$PROJECT_COUNT" != "$SOURCE_PROJECT_COUNT" ] || [ "$SPRINT_COUNT" -lt 1 ]; then
  echo "Migrated core table counts do not match source: issues $ISSUE_COUNT/$SOURCE_ISSUE_COUNT, projects $PROJECT_COUNT/$SOURCE_PROJECT_COUNT, sprints $SPRINT_COUNT." >&2
  exit 1
fi

MANIFEST_SQL="INSERT INTO research.dataset_imports (dataset_name, dataset_version, source_url, source_sha256, issue_count, project_count, sprint_count) VALUES ('TAWOS', '1.1', 'https://doi.org/10.5522/04/21308124.v1', '${SOURCE_HASH}', ${ISSUE_COUNT}, ${PROJECT_COUNT}, ${SPRINT_COUNT})"
docker exec "$POSTGRES_CONTAINER" psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER_V" -d "$POSTGRES_DB_V" -c "$MANIFEST_SQL"

echo "Migration recorded: SHA-256 $SOURCE_HASH; $ISSUE_COUNT issues; $PROJECT_COUNT projects; $SPRINT_COUNT sprints."
echo "Run scripts/validate_tawos_migration.sh before using the target."
