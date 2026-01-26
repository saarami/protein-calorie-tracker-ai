#!/usr/bin/env bash
set -euo pipefail

echo "Starting API container..."
python -m app.db.wait

echo "Running migrations..."
alembic upgrade head

exec "$@"
