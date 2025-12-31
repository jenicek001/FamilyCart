# ============================================
# Builder Stage - Build Python dependencies
# ============================================
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        postgresql-client \
        libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry (only in builder)
RUN pip install --no-cache-dir poetry==2.0.1

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install dependencies directly without virtual environment
ENV POETRY_VIRTUALENVS_CREATE=false
RUN poetry install --only main --no-root --no-interaction --no-ansi && \
    pip list --format=freeze > requirements.txt && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# ============================================
# Development Stage - With hot-reload
# ============================================
FROM python:3.12-slim AS development

WORKDIR /code

# Install runtime dependencies + dev tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
        git && \
    rm -rf /var/lib/apt/lists/*

# Copy wheels and install
COPY --from=builder /build/wheels /wheels
COPY --from=builder /build/requirements.txt .

RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt && \
    pip install --no-cache-dir fastapi-cli && \
    rm -rf /wheels

# Create app user
RUN useradd -m -u 1000 app && \
    chown -R app:app /code

USER app

# Source code will be mounted as volume
# No COPY needed here - enables hot-reload

EXPOSE 8000

# Development server with auto-reload
CMD ["fastapi", "dev", "app/main.py", "--port", "8000", "--reload"]

# ============================================
# Production Stage - Optimized runtime
# ============================================
FROM python:3.12-slim AS production

WORKDIR /code

# Install runtime dependencies only
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq5 \
        curl && \
    rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -m -u 1000 app && \
    chown -R app:app /code

# Copy wheels and install
COPY --from=builder /build/wheels /wheels
COPY --from=builder /build/requirements.txt .

RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt && \
    rm -rf /wheels

# Copy application code
COPY --chown=app:app ./app /code/app
COPY --chown=app:app alembic.ini /code/
COPY --chown=app:app alembic /code/alembic
COPY --chown=app:app scripts /code/scripts

# Make startup script executable
RUN chmod +x /code/scripts/start.sh

USER app

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Production server
CMD ["/code/scripts/start.sh"]
