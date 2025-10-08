#!/usr/bin/env bash
set -euo pipefail

# Generate a strong SECRET_KEY at runtime if not provided
if [ -z "${SECRET_KEY:-}" ] || [[ "$SECRET_KEY" == dev-secret-key* ]]; then
  export SECRET_KEY="$(python - <<'PY'
import secrets
print(secrets.token_urlsafe(64))
PY
)"
fi

# Default workers/threads can be overridden via env
GUNICORN_WORKERS=${GUNICORN_WORKERS:-2}
GUNICORN_THREADS=${GUNICORN_THREADS:-4}
GUNICORN_TIMEOUT=${GUNICORN_TIMEOUT:-60}
GUNICORN_BIND=0.0.0.0:${PORT:-3000}

exec gunicorn -w "$GUNICORN_WORKERS" --threads "$GUNICORN_THREADS" --timeout "$GUNICORN_TIMEOUT" -b "$GUNICORN_BIND" wsgi:application

