# FamilyCart Backend

This is the backend component of the FamilyCart application, built with FastAPI, SQLAlchemy, and PostgreSQL.

## Getting Started

### Prerequisites

- Python 3.12+
- Poetry package manager
- PostgreSQL database (can be run using Docker)

### Environment Setup

1. Create a `.env` file in the `backend` directory with the following variables:
   ```
   # Database
   POSTGRES_SERVER=localhost
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=familycart
   POSTGRES_PORT=5432
   
   # JWT Authentication
   SECRET_KEY=your-secret-key
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   
   # FastAPI Users
   USER_MANAGER_RESET_PASSWORD_TOKEN_LIFETIME_SECONDS=3600
   USER_MANAGER_VERIFICATION_TOKEN_LIFETIME_SECONDS=3600
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

### Starting the Backend

Always start the backend using the provided script:

```bash
# From the backend directory
./scripts/start.sh
```

This script will:
1. Run all pending database migrations using Alembic
2. Start the FastAPI application using Uvicorn

**Important:** Do not start the application directly with `uvicorn app.main:app` as this will skip the necessary database migrations.

## Development Workflow

### Creating New Migrations

When you make changes to the database models, create a new migration:

```bash
poetry run alembic revision -m "description_of_changes"
```

Then implement the `upgrade()` and `downgrade()` functions in the generated migration file.

### Running Tests

```bash
poetry run pytest
```

### API Documentation

Once the application is running, you can access the auto-generated API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
