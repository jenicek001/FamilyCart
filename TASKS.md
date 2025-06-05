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
    * [ ] Initialize FastAPI project with Poetry: `poetry init`, `poetry add fastapi uvicorn[standard] sqlalchemy psycopg2-binary alembic python-dotenv passlib[bcrypt]`
    * [ ] Add `fastapi-users[sqlalchemy]`: `poetry add "fastapi-users[sqlalchemy]"`
    * [ ] Add OAuth/JWT libraries: `poetry add "python-jose[cryptography]" httpx` (check `fastapi-users` docs for specifics, it brings many).
    * [ ] Configure basic FastAPI app structure (`main.py`, `core/config.py`).
    * [ ] Setup PostgreSQL database locally (e.g., via Docker).
    * [ ] Configure database connection in `.env` and `core/config.py`.
    * [ ] Initialize Alembic: `alembic init alembic`. Configure `env.py` and `alembic.ini`.
* **Authentication Implementation:**
    * [ ] Define User model (`models/user.py`) compatible with `fastapi-users` and SQLAlchemy.
    * [ ] Define User Pydantic schemas (`schemas/user.py`) for `fastapi-users`.
    * [ ] Create initial Alembic migration for the user table: `alembic revision -m "create_user_table"` and implement `upgrade/downgrade`.
    * [ ] Apply migration: `alembic upgrade head`.
    * [ ] Integrate `fastapi-users` core components (UserManager, backends, strategies).
    * [ ] Implement email/password registration and login routers using `fastapi-users`.
    * [ ] Setup JWT strategy for authentication.
    * [ ] Configure Google OAuth2 client ID/secret in `.env`.
    * [ ] Add Google OAuth2 router from `fastapi-users`.
    * [ ] Research and configure Apple OAuth2 (this may require more specific steps, like setting up an App ID, Service ID, and private key with Apple Developer).
    * [ ] Add Apple OAuth2 router (custom or via a `fastapi-users` compatible library if available).
    * [ ] Create basic protected endpoint `/api/v1/users/me` to test authentication.
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
    * [ ] Define `ShoppingList` and `Item` SQLAlchemy models (`models/shopping_list.py`, `models/item.py`) with relationships to User and each other.
    * [ ] Define Pydantic schemas for `ShoppingList` and `Item` (`schemas/`).
    * [ ] Create Alembic migrations for these new tables and apply them.
* **Backend - CRUD Operations:**
    * [ ] Implement CRUD functions for `ShoppingList` (`crud/crud_shopping_list.py`).
    * [ ] Implement CRUD functions for `Item` (`crud/crud_item.py`).
* **Backend - API Endpoints (v1):**
    * [ ] Create API router for `shopping_lists.py`.
        * [ ] `POST /shopping-lists/` (create list)
        * [ ] `GET /shopping-lists/` (get user's lists)
        * [ ] `GET /shopping-lists/{list_id}` (get specific list)
        * [ ] `PUT /shopping-lists/{list_id}` (update list details - e.g. name)
        * [ ] `DELETE /shopping-lists/{list_id}` (delete list)
    * [ ] Create API router for `items.py`.
        * [ ] `POST /shopping-lists/{list_id}/items/` (add item to list)
        * [ ] `GET /shopping-lists/{list_id}/items/` (get items for a list)
        * [ ] `PUT /items/{item_id}` (update item - e.g., mark as complete, change name/qty)
        * [ ] `DELETE /items/{item_id}` (delete item)
    * [ ] Ensure all endpoints are protected and operate on data owned by/shared with the authenticated user.
* **Testing:**
    * [ ] Write unit/integration tests for shopping list and item API endpoints.

---
*(Further sprints would cover WebSockets, Sharing, Frontend, etc. as outlined in PLANNING.md)*
