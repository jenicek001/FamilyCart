# Project Planning: Shared Shopping List App

## Vision

To create a simple, intuitive, and real-time shared shopping list application for families, accessible on any device (mobile, tablet, desktop) via a web browser.
Application will use AI tools to automate the process of creating and managing shopping list items - e.g. classification of items to categories, classification of items to brands,
creating icons and colors for items, translating item names to other languages, etc.

## Purpose of this file

This file is a planning document for the Shared Shopping List App project. It outlines the project's vision, key features, and technical choices.
High-level vision, architecture, constraints, tech stack, tools, etc.
Prompt to AI: “Use the structure and decisions outlined in PLANNING.md.”
Have the LLM reference this file at the beginning of any new conversation.

## Key Features (MVP - Minimum Viable Product)

1.  **User Authentication:**
    * Email/Password registration and login.
    * OAuth 2.0 login with Google.
    * OAuth 2.0 login with Apple.
    * Secure session management (JWT).
2.  **Shopping List Management:**
    * Create new shopping lists.
    * View user's own shopping lists.
    * Rename shopping list.
    * Add items to a list (name, optional quantity, notes). Items can be either new (by typing a name) or existing ones from family shopping history or from database of common items.
    * Test unified search for items (family shopping history, common items, items in the list) or new items (by typing a name), with immediate reaction as user types.
    * Mark items as purchased (put by family member into shopping cart), mark item as temporary unavailable (e.g. out of stock or available only in other store).
    * Visualize family member nickname, who requested item, and who made the last action with item (incl. date and time of the action).
    * Edit item details.
    * Remove items from a list - after a confirmation, item is removed from the list, but it is not deleted from the database.
    * Delete shopping lists.
3.  **Sharing & Collaboration:**
    * Invite other registered users (family members) to a shopping list (by email/username).
    * Shared lists update in real-time for all members when changes are made (via WebSockets).
    * View members of a shared list.
    * Remove members from a shared list.
4.  **Testing strategy:**
    * Unit testing for backend.
    * Integration testing for backend.
    * UI testing for frontend.
    * End-to-end testing for the entire application.
    * DevOps best practice and CI/CD pipeline for continuous integration and delivery.
    * All code changes shall pass automated tests before deployment. For backend Python code - PyLint, PyTest, Black, Isort, Bandit.
    * For frontend code - ESLint, Prettier, Jest.
5.  **Responsive UI:**
    * The application should be usable on mobile phone, tablet, and desktop.
6.  **I8n:**
    * Integrate I8n for multi-language support.
    * Keep English as default language in the database for item category names.
    * Generate translations for item category names and UI components via LLM API calls.
7.  **LLM Integration:**
    * Integrate LLM via API calls for item classification, translation, icons generation, etc.
    * Integrate LLM via API calls for translation of item names, item categories, etc.
    * Integrate LLM via API calls for generation of item icons and category icons.
8.  **Performance goals:**
    * Search for items should be fast as-you-type with minimal response latency (under 200 milliseconds).
    * Updates on list items across users should be fast (under 1 second).
9.  **Security goals:**
    * User authentication should be secure.
    * User data should be protected.
    * Access to services like LLM shall use API-keys.
    * API-keys shall be protected. Use environment variables / .env file to store API-keys.
    * API-keys shall be always manually configured - no auto generation of API-keys.
9.  **Deployment strategy:**
    * The application should be deployed on a self-hosted server.
    * The application shall be fully containerized.
    * The application shall be able to run on a single server.
    * The application should be able to deploy on a cloud platform like Google Cloud/Firebase Hosting for future horizontal scaling.
10. **Scalability goals:**
    * The application should be horizontally scalable.
    * The application should be able to handle a large number of users.
11. **Code and API Documentation:**
    * Keep code under 500 lines of code.
    * The application should have comprehensive documentation for the code and API.
    * Source code shall contain comments and documentation.
    * The documentation should be generated automatically from the code.
    * Use standard tools like Swagger / OpenAPI for API documentation.


## Technology Choices

* **Backend:** FastAPI (Python)
    * Database: PostgreSQL
    * Authentication: `fastapi-users` library, JWT
    * Real-time: WebSockets
    * API: RESTful for CRUD, WebSockets for notifications.
* **Frontend:** To be determined (HTML, CSS, JavaScript).
    * Framework/Libraries: TBD (AI tools like Firebase Studio/Google's AI-assisted tools will be explored).
    * Real-time updates via WebSocket connection to the backend.
* **Hosting:**
    * Start with Self-hosted Linux server, ideally containerized.
    * Keep potential future hosting on Cloud platform like Google Cloud/Firebase Hosting.

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
* [ ] Integrate LLM via API calls for item classification, translation, icons generation, etc.
* [ ] Implement basic ownership and permissions (user can only access their lists).
* [ ] CRUD API endpoints for sharing lists with other users.

### Milestone 3: Basic Frontend Scaffolding (Target: Week A-B)

* [ ] Setup basic frontend project structure.
* [ ] Implement basic UI for login and registration (to test backend auth).
* [ ] Explore AI tools for generating initial UI components.

### Milestone 4: Frontend MVP Features (Target: Week B-C)

* [ ] UI for creating/viewing lists.
* [ ] UI for adding/editing/deleting/marking items.
* [ ] Integrate WebSocket client for real-time list updates.
* [ ] UI for sharing lists.
* [ ] Basic responsive design.

### Milestone 5: Testing, Deployment & Refinement (Target: Week C-D)

* [ ] Write unit and integration tests for backend.
* [ ] Frontend testing.
* [ ] Setup CI/CD pipeline.
* [ ] Deploy to chosen hosting environment.
* [ ] User acceptance testing (family testing!).

### Milestone 6: Real-time & Sharing Backend (Target: Week Z-A)

* [ ] Implement WebSocket endpoint for notifications.
* [ ] Integrate WebSocket manager to broadcast updates.
* [ ] Logic to send notifications on list/item changes to shared users.

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
