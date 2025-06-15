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

> For detailed user stories and functional requirements, see [User Stories and Functional Requirements](./USER_STORIES.md).

*   **User Authentication:** Email/password and OAuth (Google, Apple).
*   **Shopping List Management:** Create, view, rename, delete lists.
*   **Item Management:**
    *   Add items with quantity, units, and notes.
    *   Search for items (history, global list).
    *   Edit and remove items (soft delete).
    *   Mark items as purchased or unavailable.
    *   View item requester/updater information.
*   **Advanced Item Organization:**
    *   Group and sort items by category.
    *   Reorder items within categories.
    *   Reorder entire categories.
*   **Collaboration & Sharing:**
    *   Invite users to lists.
    *   Manage list members.
*   **Real-time Synchronization:** Instant updates for all shared users via WebSockets.
*   **AI-Powered Features:**
    *   Item classification (category).
    *   Item translation.
    *   Icon generation for items.
*   **Responsive UI & Modern UX:** Accessible on mobile, tablet, and desktop.
*   **Internationalization (I18n):** Support for multiple languages.

## General Requirements, Stacks, Testing, Deployment, and Scalability Goals
1.  **User authentication:**
    * Email/password registration and login.
    * OAuth2 with Google and Apple Sign-In.
    * Secure session management using JWT tokens.
2.  **Responsive UI:**
    * The application should be usable on mobile phone, tablet, and desktop.
3.  **Performance goals:**
    * Search for items should be fast as-you-type with minimal response latency (under 200 milliseconds).
    * Updates on list items across users should be fast (under 1 second).
4.  **I18n:**
    * Integrate I18n for multi-language support.
    * Keep English as default language in the database for item category names.
    * Generate translations for item category names and UI components via LLM API calls.
5.  **Testing strategy:**
    * Unit testing for backend.
    * Integration testing for backend.
    * UI testing for frontend.
    * End-to-end testing for the entire application.
    * DevOps best practice and CI/CD pipeline for continuous integration and delivery.
    * All code changes shall pass automated tests before deployment. For backend Python code - PyLint, PyTest, Black, Isort, Bandit.
    * For frontend code - ESLint, Prettier, Jest.
6.  **Security goals:**
    * User authentication should be secure.
    * Sessions shall use JWT tokens.
    * OAuth2 with Google and Apple Sign-In should be implemented.
    * User data should be protected.
    * Access to services like LLM shall use API-keys.
    * API-keys shall be protected. Use environment variables / .env file to store API-keys.
    * API-keys shall be always manually configured - no auto generation of API-keys.
7.  **Data Privacy & GDPR Compliance:**
    * User data protection and privacy measures.
    * Data retention policies.
    * User consent management.
    * Data export/deletion capabilities.
    * Privacy policy documentation requirements.
8.  **AI Integration Details:**
    * Gemini API for item classification and natural language understanding and generation of translations.
    * Gemini API for item icon generation and color classification.
    * Caching strategy for AI-generated content - keep item categories, translations, and icons in the database to avoid unnecessary API calls.
    * Built-in rate limiting and quota management through Google Cloud.
    * Cost optimization through Google Cloud budgets.
    * Rate limiting and cost optimization measures.
9.  **Technical Architecture Details:**
    * Microservices vs Monolith trade-offs.
    * Database schema design principles.
    * API versioning strategy.
    * Caching strategy (Redis/Memcached).
    * Monitoring and logging setup (Prometheus/Grafana).
10. **Deployment strategy:**
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
    * AI: Google Gemini API for item classification, translation, and icon generation.
* **Frontend:** To be determined (HTML, CSS, JavaScript)
    * Framework/Libraries: TBD (Firebase Studio/Google's AI-assisted tools)
    * Real-time updates via WebSocket connection
    * Client-side AI: Firebase ML SDK
* **Frontend:** To be determined (HTML, CSS, JavaScript).
    * Framework/Libraries: TBD (AI tools like Firebase Studio/Google's AI-assisted tools will be explored).
    * Real-time updates via WebSocket connection to the backend.
* **Hosting:**
    * Start with Self-hosted Linux server, ideally containerized.
    * Keep potential future hosting on Cloud platform like Google Cloud/Firebase Hosting.

## Milestones

### Milestone 1: Backend Core & Authentication (Target: Week X-Y)

* [ ] Setup FastAPI project structure.
* [ ] Implement database models (User, ShoppingList, Item, Category, ItemCategoryLink).
* [ ] Integrate `fastapi-users` for email/password authentication.
* [ ] Setup JWT authentication.
* [ ] Setup PostgreSQL and Alembic migrations.
* [ ] Basic API endpoints for user registration and login.
* [ ] Implement OAuth2 for Google Sign-In.
* [ ] Implement OAuth2 for Apple Sign-In.

### Milestone 2: Core Shopping List API (Target: Week Y-Z)

* [ ] CRUD API endpoints for Shopping Lists.
* [ ] CRUD API endpoints for Items within lists (including quantity, units, notes, status).
* [ ] API endpoints for managing item categories.
* [ ] API endpoints for linking items to categories and managing their order within categories.
* [ ] API endpoints for reordering categories within a list.
* [ ] Integrate LLM via API calls for item classification (to category), translation, icons generation.
* [ ] Implement basic ownership and permissions (user can only access their lists).
* [ ] CRUD API endpoints for sharing lists with other users and managing members.

### Milestone 3: Real-time Backend & Advanced Features (Target: Week Z-A)

* [ ] Implement WebSocket endpoint for real-time notifications.
* [ ] Integrate WebSocket manager to broadcast updates on list/item/category changes.
* [ ] Logic to send notifications for:
    *   Item additions, updates (name, quantity, notes, status, category, order), deletions.
    *   Category additions, updates (name, order), deletions.
    *   List sharing and member changes.
* [ ] API endpoints for item history and search improvements (FR023, FR024).

### Milestone 4: Basic Frontend Scaffolding (Target: Week A-B)

* [ ] Setup basic frontend project structure.
* [ ] Implement basic UI for login and registration (to test backend auth).
* [ ] Explore AI tools for generating initial UI components.

### Milestone 5: Frontend MVP Features (Target: Week B-C)

* [ ] UI for creating/viewing lists.
* [ ] UI for adding/editing/deleting/marking items.
* [ ] UI for managing item categories (viewing items by category, reordering items within categories, reordering categories).
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

## Success Metrics
* User engagement metrics (DAU/MAU)
* Performance metrics (response times, uptime)
* Error rates and bug resolution time
* User satisfaction scores
* AI feature accuracy rates
