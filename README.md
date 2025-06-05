# FamilyCart - Mobile Web application for real-time family shopping lists

This project is a responsive web application that allows family members to share and manage shopping lists in real-time.

## Tech Stack

* **Backend:** Python, FastAPI, PostgreSQL, WebSockets
* **Frontend:** To be developed (potentially with AI tools like Firebase Studio/Google's AI tools), communicating via REST API and WebSockets.
* **Authentication:** Email/Password, Google Sign-In, Apple Sign-In.

## Project Structure

* `/backend`: Contains the FastAPI application.
* `/frontend`: Contains the frontend application.
* `/PLANNING.md`: High-level project planning and milestones.
* `/TASKS.md`: Initial development tasks.

## Setup and Installation

### Backend

1.  Navigate to the `backend` directory: `cd backend`
2.  Create a virtual environment: `python -m venv venv`
3.  Activate the virtual environment:
    * macOS/Linux: `source venv/bin/activate`
    * Windows: `.\venv\Scripts\activate`
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
