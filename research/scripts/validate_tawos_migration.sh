#!/usr/bin/env bash
# Bash port of validate_tawos_migration.ps1 for Linux hosts without pwsh.
# Compares row counts for all 13 upstream TAWOS tables between the MySQL
# source and the migrated tawos_raw PostgreSQL schema.
set -euo pipefail

SOURCE_CONTAINER="${1:-tawos-source-mysql}"
SOURCE_ROOT_PASSWORD="${2:-${MYSQL_ROOT_PASSWORD:-tawos_mysql_local}}"

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
POSTGRES_DB_V=$(get_setting POSTGRES_DB tawos)
POSTGRES_CONTAINER=$(docker compose ps -q db)
if [ -z "$POSTGRES_CONTAINER" ]; then
  echo "PostgreSQL is not running." >&2
  exit 1
fi

MYSQL_AUTH=(-uroot)
if [ -n "$SOURCE_ROOT_PASSWORD" ]; then
  MYSQL_AUTH+=("-p${SOURCE_ROOT_PASSWORD}")
fi

declare -a SOURCE_TABLES=(Project Sprint Issue Change_Log Comment Repository User Version Component Affected_Version Fix_Version Issue_Component Issue_Link)
declare -a TARGET_TABLES=(project sprint issue change_log comment repository "user" version component affected_version fix_version issue_component issue_link)

declare -a DIFFERENCES=()
for i in "${!SOURCE_TABLES[@]}"; do
  src="${SOURCE_TABLES[$i]}"
  tgt="${TARGET_TABLES[$i]}"
  source_count=$(docker exec "$SOURCE_CONTAINER" mysql "${MYSQL_AUTH[@]}" -Nse "SELECT COUNT(*) FROM TAWOS.\`${src}\`")
  target_count=$(docker exec "$POSTGRES_CONTAINER" psql -U "$POSTGRES_USER_V" -d "$POSTGRES_DB_V" -Atc "SELECT COUNT(*) FROM tawos_raw.\"${tgt}\"")
  printf '%-20s %12s rows\n' "$tgt" "$target_count"
  if [ "$source_count" != "$target_count" ]; then
    DIFFERENCES+=("${src}: MySQL=${source_count} PostgreSQL=${target_count}")
  fi
done

if [ "${#DIFFERENCES[@]}" -gt 0 ]; then
  echo "Row-count mismatches detected:" >&2
  printf '%s\n' "${DIFFERENCES[@]}" >&2
  exit 1
fi

echo "PASS: row counts match for all ${#SOURCE_TABLES[@]} TAWOS tables."
