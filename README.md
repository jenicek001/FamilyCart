# FamilyCart - Mobile Web application for real-time family shopping lists

This project is a responsive web application that allows family members to share and manage shopping lists in real-time.

## Tech Stack

* **Backend:** Python, FastAPI, PostgreSQL, WebSockets
* **Frontend:** To be developed (potentially with AI tools like Firebase Studio/Google's AI tools), communicating via REST API and WebSockets.
* **Authentication:** Email/Password, Google Sign-In, Apple Sign-In.

## Project Structure

## Development

### Project Structure

* `/backend`: Contains the FastAPI application.
* `/frontend`: Contains the frontend application.
* `/PLANNING.md`: High-level project planning and milestones.
* `/TASKS.md`: Initial development tasks.

### Detailed Project Structure
```
shared-shopping-list/
├── .github/                      # Optional: GitHub specific files like issue templates, workflows
│   └── WORKFLOWS/
│       └── ci.yml                # Basic CI pipeline placeholder
├── .gitignore
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py               # Common dependencies (e.g., get_current_active_user)
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── routers/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── auth.py         # Handles login, registration, social auth callbacks
│   │   │       │   ├── users.py        # User related endpoints (e.g., get me)
│   │   │       │   ├── shopping_lists.py
│   │   │       │   └── items.py
│   │   │       └── ws_v1.py            # WebSocket endpoints for v1 notifications
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py             # Application configuration (settings)
│   │   │   └── security.py           # Password hashing, OAuth2 schemes (can be part of fastapi-users)
│   │   ├── crud/
│   │   │   ├── __init__.py
│   │   │   ├── base.py               # Base CRUD utilities
│   │   │   ├── crud_user.py
│   │   │   ├── crud_shopping_list.py
│   │   │   └── crud_item.py
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── base.py               # SQLAlchemy Base and UserBase for fastapi-users
│   │   │   ├── database.py           # Engine and session setup
│   │   │   └── init_db.py            # Script to initialize DB (create tables, first superuser) - or use Alembic
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py               # SQLAlchemy User model (integrates with fastapi-users)
│   │   │   ├── shopping_list.py
│   │   │   └── item.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py               # Pydantic schemas for User (integrates with fastapi-users)
│   │   │   ├── token.py              # Token schemas (for JWT)
│   │   │   ├── shopping_list.py
│   │   │   └── item.py
│   │   ├── services/                 # For business logic beyond simple CRUD
│   │   │   ├── __init__.py
│   │   │   └── websocket_manager.py  # Manages active WebSocket connections
│   │   └── main.py                 # FastAPI application instance and router setup
│   ├── alembic/                      # Alembic configuration for migrations
│   │   ├── versions/                 # Migration scripts
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── alembic.ini
│   ├── pyproject.toml                # For Poetry (or requirements.txt for pip)
│   ├── poetry.lock                   # (or requirements.txt for pip)
│   └── tests/                        # Unit and integration tests
│       ├── __init__.py
│       ├── conftest.py               # Pytest fixtures
│       └── ...                       # Test modules mirroring app structure
├── frontend/
│   ├── public/
│   │   ├── index.html                # Main HTML file
│   │   ├── favicon.ico
│   │   └── assets/                   # Static assets like images, fonts
│   ├── src/
│   │   ├── App.jsx                   # Main application component (example if using React/Vue)
│   │   ├── index.js                  # Main JS entry point
│   │   ├── components/               # Reusable UI components
│   │   ├── services/
│   │   │   ├── apiService.js         # Functions to interact with the backend REST API
│   │   │   └── websocketService.js   # Functions to manage WebSocket connection
│   │   ├── store/                    # State management (e.g., Redux, Zustand, Pinia)
│   │   ├── views/                    # Page components
│   │   └── styles/
│   │       └── main.css              # Global styles
│   ├── .firebaserc                 # If using Firebase CLI for hosting/emulators
│   ├── firebase.json               # Firebase hosting rules, etc.
│   ├── package.json                # Frontend dependencies and scripts
│   ├── vite.config.js              # Example if using Vite as a build tool (or similar for Webpack/Parcel)
│   └── README.md                   # Frontend specific instructions
├── PLANNING.md
├── README.md
└── TASKS.md
```

## Setup and Installation

### Backend

1.  Navigate to the `backend` directory: `cd backend`
2.  Create a virtual environment: `python -m venv venv`
3.  Activate the virtual environment:
    * macOS/Linux: `source venv/bin/activate`
    * Windows: `.\venv\Scripts\activate.bat`
4.  Install dependencies using Poetry: `poetry install` (or `pip install -r requirements.txt` if not using Poetry).
5.  Set up environment variables: Create a `.env` file from `.env.example` (to be created) and fill in your PostgreSQL connection details, JWT secrets, OAuth client IDs/secrets.
6.  Initialize the database and apply migrations:
    * `alembic upgrade head`
7.  Run the development server: `uvicorn app.main:app --reload` (from within the `backend/app` or configured path)

### Frontend

(Instructions to be added once the frontend development approach is finalized. Generally, it will involve `npm install` and `npm run dev` or similar commands.)

## API Documentation

Once the backend server is running, API documentation (Swagger UI) will be available at `http://localhost:8000/docs`.

## Contributing

(Details to be added)
