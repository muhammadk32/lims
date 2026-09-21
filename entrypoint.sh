#!/bin/sh
# ============================================================
# LabMS container entrypoint
# Runs migrations, ensures uploads folder, then execs gunicorn.
# ============================================================
set -e

echo "[entrypoint] Applying database migrations..."
flask --app wsgi:app db upgrade || {
    echo "[entrypoint] Migration failed."
    exit 1
}

echo "[entrypoint] Ensuring upload folders exist..."
mkdir -p /app/static/uploads/branding
mkdir -p /app/logs

echo "[entrypoint] Starting gunicorn on 0.0.0.0:${PORT:-8000}..."
exec gunicorn \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${GUNICORN_WORKERS:-4}" \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    wsgi:app