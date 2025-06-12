# FamilyCart API

A shared shopping list application built with FastAPI and PostgreSQL.

## Features

- User authentication with JWT
- OAuth2 with Google and Apple
- Real-time updates with WebSockets
- RESTful API for shopping lists and items
- Database migrations with Alembic

## Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Git

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/FamilyCart.git
cd FamilyCart
```

### 2. Set up environment variables

Copy the example environment file and update the values:

```bash
cp .env.example .env
```

Edit the `.env` file with your configuration.

### 3. Start the database

```bash
docker-compose up -d db
```

### 4. Set up Python environment

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Initialize the database

```bash
# Run migrations
alembic upgrade head

# Or initialize the database directly
python scripts/init_db.py
```

### 6. Run the application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Development

### Running tests

```bash
pytest
```

### Code formatting

```bash
black .
isort .
flake8
```

### Database migrations

To create a new migration:

```bash
alembic revision --autogenerate -m "Your migration message"
```

To apply migrations:

```bash
alembic upgrade head
```

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

MIT
