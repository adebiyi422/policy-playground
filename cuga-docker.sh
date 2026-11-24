#!/usr/bin/env bash
# Run a command inside the CUGA container with this folder mounted at /app
# and .env loaded before CUGA is imported.
#   ./cuga-docker.sh python llm_smoke.py
#   PORT=7860 ./cuga-docker.sh cuga start manager
#   ./cuga-docker.sh --rebuild python llm_smoke.py   # after changing deps
set -euo pipefail
cd "$(dirname "$0")"
IMAGE=policy-playground:latest
DOCKER=${DOCKER:-docker}
command -v "$DOCKER" >/dev/null || DOCKER="$HOME/.rd/bin/docker"

if [[ "${1:-}" == "--rebuild" ]] || ! "$DOCKER" image inspect "$IMAGE" >/dev/null 2>&1; then
  [[ "${1:-}" == "--rebuild" ]] && shift
  "$DOCKER" build -t "$IMAGE" .
fi
[[ -f .env ]] || { echo "Missing .env (see docs/cuga-env-api-keys.md)" >&2; exit 1; }

tty=(-i)
[[ -t 0 && -t 1 ]] && tty=(-it)
ports=()
[[ -n "${PORT:-}" ]] && ports=(-p "${PORT}:${PORT}")

exec "$DOCKER" run --rm ${tty[@]+"${tty[@]}"} ${ports[@]+"${ports[@]}"} -v "$PWD":/app -w /app "$IMAGE" \
  uv run --no-sync --env-file .env "$@"
