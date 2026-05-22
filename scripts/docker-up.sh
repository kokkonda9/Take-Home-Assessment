#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

resolve_compose() {
  if command -v docker-compose >/dev/null 2>&1; then
    echo "docker-compose"
  elif docker compose version >/dev/null 2>&1; then
    echo "docker compose"
  elif [[ -x "${HOME}/.local/bin/docker-compose" ]]; then
    echo "${HOME}/.local/bin/docker-compose"
  else
    echo "Docker Compose not found. Install the plugin or run:" >&2
    echo "  curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o ~/.local/bin/docker-compose" >&2
    echo "  chmod +x ~/.local/bin/docker-compose" >&2
    exit 1
  fi
}

run_compose() {
  local compose_cmd="$1"
  shift
  if [[ "$compose_cmd" == "docker compose" ]]; then
    docker compose "$@"
  else
    "$compose_cmd" "$@"
  fi
}

can_use_docker() {
  docker info >/dev/null 2>&1
}

COMPOSE_CMD="$(resolve_compose)"

echo "Stopping local uvicorn processes on 8080/8081 (if any)..."
fuser -k 8080/tcp 8081/tcp 2>/dev/null || true
pkill -f "uvicorn account_service.main:app" 2>/dev/null || true
pkill -f "uvicorn gateway_service.main:app" 2>/dev/null || true

if can_use_docker; then
  echo "Building and starting containers..."
  run_compose "$COMPOSE_CMD" up --build -d
else
  echo "Docker permission denied."
  echo "One-time fix (recommended): sudo usermod -aG docker \"\$USER\" && newgrp docker"
  echo "Or run this script with sudo once: USE_SUDO=1 $0"
  if [[ "${USE_SUDO:-0}" == "1" ]]; then
    echo "Trying with sudo..."
    if [[ "$COMPOSE_CMD" == "docker compose" ]]; then
      sudo docker compose up --build -d
    else
      sudo "$COMPOSE_CMD" up --build -d
    fi
  else
    exit 1
  fi
fi

echo "Waiting for services..."
deadline=$((SECONDS + 60))
until curl -sf http://127.0.0.1:8081/health >/dev/null && curl -sf http://127.0.0.1:8080/health >/dev/null; do
  if (( SECONDS > deadline )); then
    echo "Timed out waiting for services. Logs:"
    run_compose "$COMPOSE_CMD" logs
    exit 1
  fi
  sleep 2
done

echo ""
echo "Services are up."
echo "  Gateway Swagger: http://localhost:8080/docs"
echo "  Account Swagger: http://localhost:8081/docs"
echo ""
curl -s http://127.0.0.1:8080/health | python3 -m json.tool
curl -s http://127.0.0.1:8081/health | python3 -m json.tool
