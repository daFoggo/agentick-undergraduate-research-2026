#!/usr/bin/env bash
# Usage: scripts/stack.sh start|stop|restart|status|logs [service]|build|down
# start: research DB (tawos, :15432) + Plane stack with risk service (http://localhost:31080). Data is kept in Docker volumes.
# down removes containers but NOT volumes. Never add -v.
set -euo pipefail
export MSYS_NO_PATHCONV=1
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && { pwd -W 2>/dev/null || pwd; })"
PLANE="$ROOT/plane/deployments/cli/community"
RESEARCH="$ROOT/research"
unset DATABASE_URL  # a shell DATABASE_URL would override Plane's .env (see agentick-backend/README)

plane() { (cd "$PLANE" && docker compose --env-file .env -p plane -f docker-compose.yml -f docker-compose.risk.yml "$@"); }
research() { (cd "$RESEARCH" && docker compose -f compose.yaml -f "$ROOT/scripts/research-db.override.yml" "$@"); }

case "${1:-}" in
  start)   research up -d db; plane up -d; echo "Plane: http://localhost:31080  risk: http://127.0.0.1:31081/api/v1/health  tawos: localhost:15432" ;;
  stop)    plane stop; research stop ;;
  restart) plane restart; research restart db ;;
  down)    plane down; research down ;;
  build)   (cd "$ROOT/plane" && docker build -f apps/web/Dockerfile.web -t plane-web-risk:dev .); plane up -d --build ;;
  status)  plane ps; research ps ;;
  logs)    plane logs -f --tail 100 "${@:2}" ;;
  *) echo "usage: $0 start|stop|restart|down|build|status|logs [service]"; exit 1 ;;
esac
