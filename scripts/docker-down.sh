#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD="docker-compose"
elif docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD="docker compose"
elif [[ -x "${HOME}/.local/bin/docker-compose" ]]; then
  COMPOSE_CMD="${HOME}/.local/bin/docker-compose"
else
  echo "Docker Compose not found." >&2
  exit 1
fi

run_compose() {
  if [[ "$COMPOSE_CMD" == "docker compose" ]]; then
    if docker info >/dev/null 2>&1; then
      docker compose down
    else
      sudo docker compose down
    fi
  else
    if docker info >/dev/null 2>&1; then
      "$COMPOSE_CMD" down
    else
      sudo "$COMPOSE_CMD" down
    fi
  fi
}

run_compose
echo "Containers stopped."
