#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Allow overriding host and port to avoid conflicts with other local services (e.g. UAT)
# Usage: PORT=8001 HOST=0.0.0.0 ./scripts/start.sh

# Get default port from Python config if not set in environment
if [ -z "$PORT" ]; then
    # Try to extract PORT from Python config, fallback to 8005 if extraction fails
    PORT=$(poetry run python -c "from app.core.config import settings; print(settings.PORT)" 2>/dev/null || echo "8005")
fi

if [ -z "$HOST" ]; then
    # Try to extract HOST from Python config, fallback to 0.0.0.0 if extraction fails
    HOST=$(poetry run python -c "from app.core.config import settings; print(settings.HOST)" 2>/dev/null || echo "0.0.0.0")
fi

echo "Running database migrations..."
poetry run alembic upgrade head

echo "Starting application on ${HOST}:${PORT}..."
poetry run uvicorn app.main:app --host ${HOST} --port ${PORT}
