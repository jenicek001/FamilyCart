# Project Planning: Shared Shopping List App

## Vision

To create a simple, intuitive, and real-time shared shopping list application for families, accessible on any device via a web browser.

## Key Features (MVP - Minimum Viable Product)

1.  **User Authentication:**
    * Email/Password registration and login.
    * OAuth 2.0 login with Google.
    * OAuth 2.0 login with Apple.
    * Secure session management (JWT).
2.  **Shopping List Management:**
    * Create new shopping lists.
    * View user's own shopping lists.
    * Add items to a list (name, optional quantity, notes).
    * Mark items as purchased/unpurchased.
    * Edit item details.
    * Remove items from a list.
    * Delete shopping lists.
3.  **Sharing & Collaboration:**
    * Invite other registered users (family members) to a shopping list (by email/username).
    * Shared lists update in real-time for all members when changes are made (via WebSockets).
    * View members of a shared list.
4.  **Responsive UI:**
    * The application should be usable on desktop, tablet, and mobile browsers.

## Technology Choices

* **Backend:** FastAPI (Python)
    * Database: PostgreSQL
    * Authentication: `fastapi-users` library, JWT
    * Real-time: WebSockets
    * API: RESTful for CRUD, WebSockets for notifications.
* **Frontend:** To be determined (HTML, CSS, JavaScript).
    * Framework/Libraries: TBD (AI tools like Firebase Studio/Google's AI-assisted tools will be explored).
    * Real-time updates via WebSocket connection to the backend.
* **Hosting:** TBD (Self-hosted Linux server or Cloud platform like Google Cloud/Firebase Hosting).

## Milestones

### Milestone 1: Backend Core & Authentication (Target: Week X-Y)

* [ ] Setup FastAPI project structure.
* [ ] Implement database models (User, ShoppingList, Item).
* [ ] Integrate `fastapi-users` for email/password authentication.
* [ ] Setup JWT authentication.
* [ ] Setup PostgreSQL and Alembic migrations.
* [ ] Basic API endpoints for user registration and login.
* [ ] Implement OAuth2 for Google Sign-In.
* [ ] Implement OAuth2 for Apple Sign-In.

### Milestone 2: Core Shopping List API (Target: Week Y-Z)

* [ ] CRUD API endpoints for Shopping Lists.
* [ ] CRUD API endpoints for Items within lists.
* [ ] Implement basic ownership and permissions (user can only access their lists).

### Milestone 3: Real-time & Sharing Backend (Target: Week Z-A)

* [ ] Implement WebSocket endpoint for notifications.
* [ ] Integrate WebSocket manager to broadcast updates.
* [ ] API endpoints for sharing lists with other users.
* [ ] Logic to send notifications on list/item changes to shared users.

### Milestone 4: Basic Frontend Scaffolding (Target: Week A-B)

* [ ] Setup basic frontend project structure.
* [ ] Implement basic UI for login and registration (to test backend auth).
* [ ] Explore AI tools for generating initial UI components.

### Milestone 5: Frontend MVP Features (Target: Week B-C)

* [ ] UI for creating/viewing lists.
* [ ] UI for adding/editing/deleting/marking items.
* [ ] Integrate WebSocket client for real-time list updates.
* [ ] UI for sharing lists.
* [ ] Basic responsive design.

### Milestone 6: Testing, Deployment & Refinement (Target: Week C-D)

* [ ] Write unit and integration tests for backend.
* [ ] Frontend testing.
* [ ] Setup CI/CD pipeline.
* [ ] Deploy to chosen hosting environment.
* [ ] User acceptance testing (family testing!).

## Future Considerations / Post-MVP

* Push Notifications (native if PWA, or email).
* List categories/sorting.
* Recipe integration (add all ingredients from a recipe).
* Price tracking / budget features.
* Offline support (PWA features).
* Admin panel.

## Risks

* **Learning Curve for Apple Sign-In:** Apple's OAuth can be more complex to set up than Google's.
* **Frontend AI Tool Limitations:** Reliance on AI tools for frontend might hit limitations requiring manual JS/CSS work.
* **Real-time Complexity:** Ensuring reliable and efficient real-time updates across all clients.
* **Scope Creep:** Adding too many features before MVP is solid.
