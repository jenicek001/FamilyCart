# Purpose of this file: Tracks current tasks, backlog, and sub-tasks.
# Includes: Bullet list of active work, milestones, and anything discovered mid-process.
# Prompt to AI: "Update TASK.md to mark XYZ as done and add ABC as a new task."

## Documentation & Process Improvements
* [x] Document the correct backend startup procedure (2023-06-25)
  * Backend should be started using the `backend/scripts/start.sh` script, which runs database migrations before starting the application
  * Avoid running `uvicorn` directly as it skips necessary setup stepss file
Tracks current tasks, backlog, and sub-tasks.
Includes: Bullet list of active work, milestones, and anything discovered mid-process.
Prompt to AI: "Update TASK.md to mark XYZ as done and add ABC as a new task."
Can prompt the LLM to automatically update and create tasks as well (through global rules).

# Current Tasks

## Documentation & Process Improvements
* [x] Document the correct backend startup procedure (2023-06-25)
  * Backend should be started using the `backend/scripts/start.sh` script, which runs database migrations before starting the application
  * Avoid running `uvicorn` directly as it skips necessary setup stepspose of this file
Tracks current tasks, backlog, and sub-tasks.
Includes: Bullet list of active work, milestones, and anything discovered mid-process.
Prompt to AI: “Update TASK.md to mark XYZ as done and add ABC as a new task.”
Can prompt the LLM to automatically update and create tasks as well (through global rules).

# Initial Development Tasks (MVP Focus)

## Sprint 1: Backend Foundation & Authentication

### User Stories:
* As a user, I want to register for a new account using my email and password so I can access the application.
* As a user, I want to log in with my email and password.
* As a user, I want to log in/register using my Google account.
* As a user, I want to log in/register using my Apple ID.
* As a developer, I need a secure way to manage user sessions (JWT).

### Tasks:

* **Backend Setup:**
    * [x] Initialize FastAPI project with Poetry: `poetry init`, `poetry add fastapi uvicorn[standard] sqlalchemy psycopg2-binary alembic python-dotenv passlib[bcrypt]`
    * [x] Add `fastapi-users[sqlalchemy]`: `poetry add "fastapi-users[sqlalchemy]"`
    * [x] Add OAuth/JWT libraries: `poetry add "python-jose[cryptography]" httpx` (check `fastapi-users` docs for specifics, it brings many).
    * [x] Configure basic FastAPI app structure (`main.py`, `core/config.py`).
    * [x] Setup PostgreSQL database locally (e.g., via Docker).
    * [x] Configure database connection in `backend/.env` and `core/config.py`.
    * [x] Initialize Alembic: `alembic init alembic`. Configure `env.py` and `alembic.ini`.
* **Authentication Implementation:**
    * [x] Define User model (`models/user.py`) compatible with `fastapi-users` and SQLAlchemy.
    * [x] Define User Pydantic schemas (`schemas/user.py`) for `fastapi-users`.
    * [x] Create initial Alembic migration for the user table: `alembic revision -m "create_user_table"` and implement `upgrade/downgrade`.
    * [x] Apply migration: `alembic upgrade head`.
    * [x] Integrate `fastapi-users` core components (UserManager, backends, strategies).
    * [x] Implement email/password registration and login routers using `fastapi-users`.
    * [x] Setup JWT strategy for authentication.
    * [x] Fix authentication router paths for proper frontend integration (2025-06-23)
    * [x] Fix user name handling during registration (2025-06-23)
    * [x] Fix authentication consistency between different API routers (2025-06-24)
    * [x] Fix user profile name display on profile page (2025-06-23)
    * [x] Create basic protected endpoint `/api/v1/users/me` to test authentication. (2025-06-24)
* **Documentation & Testing:**
    * [ ] Ensure OpenAPI docs (`/docs`) reflect auth endpoints.
    * [ ] Write basic unit tests for user creation/login.

## Sprint 2: Core Shopping List API

### User Stories:
* As an authenticated user, I want to create a new shopping list.
* As an authenticated user, I want to view all my shopping lists.
* As an authenticated user, I want to add items (name, quantity) to a specific shopping list.
* As an authenticated user, I want to mark an item as purchased.
* As an authenticated user, I want to remove an item from a list.

### Tasks:
* **Backend - Models & Schemas:**
    * [x] Define `ShoppingList` and `Item` SQLAlchemy models (`models/shopping_list.py`, `models/item.py`) with relationships to User and each other.
    * [x] Define Pydantic schemas for `ShoppingList` and `Item` (`schemas/`).
    * [x] Create Alembic migrations for these new tables and apply them.
* **Backend - CRUD Operations:**
    * [x] Implement CRUD functions for `ShoppingList` (`crud/crud_shopping_list.py`). (Implemented directly in router instead)
    * [x] Implement CRUD functions for `Item` (`crud/crud_item.py`). (Implemented directly in router instead)
* **Backend - API Endpoints (v1):**
    * [x] Create API router for `shopping_lists.py`.
        * [x] `POST /shopping-lists/` (create list)
        * [x] `GET /shopping-lists/` (get user's lists)
        * [x] `GET /shopping-lists/{list_id}` (get specific list)
        * [x] `PUT /shopping-lists/{list_id}` (update list details - e.g. name)
        * [x] `DELETE /shopping-lists/{list_id}` (delete list)
    * [x] Create API router for `items.py`.
        * [x] `POST /shopping-lists/{list_id}/items/` (add item to list)
        * [x] `GET /shopping-lists/{list_id}/items/` (get items for a list)
        * [x] `PUT /items/{item_id}` (update item - e.g., mark as complete, change name/qty)
        * [x] `DELETE /items/{item_id}` (delete item)
    * [x] Ensure all endpoints are protected and operate on data owned by/shared with the authenticated user.
* **Testing:**
    * [x] Write unit/integration tests for shopping list and item API endpoints.
* [x] Implement functionality to create a new shopping cart (2025-06-24)
    * Implemented as `POST /shopping-lists/` in `backend/app/api/v1/endpoints/shopping_lists.py`.
* [x] Add confirmation dialog when a shopping list delete icon is clicked (2025-06-24)
    * [x] Fix dashboard handler bug: define handleAddItem and handleToggleItem so dashboard renders and all handlers work (2025-06-24)

## Sprint 3: Add Authentication using OAuth2
* As a user, I want to log in using my Google account.
* As a user, I want to log in using my Apple ID.

### Tasks:
* **Backend - OAuth2 Integration:**
    * [ ] Add OAuth2 support to `fastapi-users` for Google authentication.
    * [ ] Configure Google OAuth2 client ID/secret in `.env`.
    * [ ] Research and configure Apple OAuth2 (this may require more specific steps, like setting up an App ID, Service ID, and private key with Apple Developer).
    * [ ] Add OAuth2 support to `fastapi-users` for Apple ID authentication.
    * [ ] Add Apple OAuth2 router (custom or via a `fastapi-users` compatible library if available).
    * [ ] Configure OAuth2 clients in `core/config.py` (client IDs)
* **Frontend - OAuth2 Login:**
    * [ ] Update frontend login page to include buttons for Google login.
    * [ ] Update frontend login page to include buttons for Apple ID login.
    * [ ] Add Google OAuth2 router from `fastapi-users`.
* **Testing:**
    * [ ] Write tests for OAuth2 login flows.

---
*(Further sprints would cover WebSockets, Sharing, Frontend, etc. as outlined in PLANNING.md)*
