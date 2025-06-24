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
    * [x] Fix 500 error when renaming shopping cart (PUT /shopping-lists/{id}) by eagerly loading relationships in update endpoint (2025-06-24)
* [ ] Add UI control (checkbox/button) to mark an item as purchased/unpurchased in the shopping list (Frontend)
* [ ] Visually distinguish purchased items (e.g., strikethrough, faded color) (Frontend)
* [ ] Show a toast or feedback when an item is marked as purchased/unpurchased (Frontend)
* [ ] Ensure the PUT /items/{item_id} endpoint correctly updates the is_completed status and returns the updated item (Backend)
* [ ] Add/Update tests for marking items as purchased/unpurchased (API and UI)
* [ ] Write/expand unit and integration tests for toggling item completion (backend and frontend)
* [ ] Add edge case tests (e.g., toggling an item that doesn’t exist, or that the user doesn’t own)
* [ ] Display item quantities in the shopping list UI (Frontend)
* [ ] Implement editing of items in the shopping list (allow users to update name, quantity, category, icon, etc.) (2025-06-24)

## Sprint 2 Extension: UI Migration to Stitch Style

### Goal:
Migrate the FamilyCart app UI to use the Stitch/layout.html style for shopping list and all main app screens, ensuring consistency in layout, color, icons, and interactivity.

### Tasks:
* **Audit & Planning:**
    * [ ] Inventory all current UI screens and components (shopping list, item details, user profile, etc.)
    * [ ] Identify migration priorities (start with shopping list UI)
    * [ ] Document current vs. target UI structure for each screen
* **Design Tokens & Global Styles:**
    * [ ] Extract color palette, font families, and spacing from Stitch/layout.html
    * [ ] Update Tailwind config (or CSS framework) to match Stitch tokens
    * [ ] Set global font to "Plus Jakarta Sans" and "Noto Sans"
    * [ ] Standardize border radius, box shadows, and spacing utilities
* **Layout & Structure:**
    * [ ] Refactor main layout to use centered, max-width container and sticky header
    * [ ] Apply section headers and consistent spacing to all main pages
    * [ ] Update navigation/header to match Stitch style (logo, title, user menu)
* **Component Refactoring:**
    * [ ] Refactor shopping list items to card-based design (icon, colored background, item/category, metadata, checkbox, drag handle)
    * [ ] Assign category colors and icons as in Stitch sample
    * [ ] Move checked items to faded, line-through section at the bottom
    * [ ] Implement dropdown filter menu and search bar with leading icon
    * [ ] Refactor all buttons to rounded, colored/outlined style
* **Icons & Visuals:**
    * [ ] Use Material Icons for all UI elements
    * [ ] Map each category to a unique icon and color
* **Accessibility & Responsiveness:**
    * [ ] Ensure all interactive elements have ARIA labels and visible focus states
    * [ ] Use Tailwind’s responsive classes for all layouts and components
* **Reusable Components:**
    * [ ] Abstract repeated UI patterns (cards, buttons, dropdowns, etc.) into reusable components
* **Testing & QA:**
    * [ ] Test new UI on all target devices and browsers
    * [ ] Check accessibility (keyboard navigation, screen reader support)
* **Documentation:**
    * [ ] Update README.md with new setup instructions, design tokens, and component usage
    * [ ] Document any new or changed components
* **Iterative Rollout:**
    * [ ] Migrate one feature/page at a time, starting with shopping list
    * [ ] Get user feedback after each major migration step

### Success Criteria:
- [ ] All main screens use Stitch layout, color, and icon style
- [ ] Shopping list UI matches Stitch sample (cards, icons, checked items, etc.)
- [ ] All components are responsive and accessible
- [ ] Design tokens and reusable components are documented
- [ ] User feedback is positive on new UI


## Sprint 3: Item Completion & UI Enhancement

### User Stories:
* As a user, I want to mark items as purchased/unpurchased in the shopping list UI.
* As a user, I want to see visually distinguished purchased items.
* As a user, I want to see item quantities in the shopping list UI.
* As a user, I want to edit items in the shopping list.

### Tasks:
* **Frontend - Item Management UI:**
    * [ ] Add UI control (checkbox/button) to mark an item as purchased/unpurchased in the shopping list
    * [ ] Visually distinguish purchased items (e.g., strikethrough, faded color)
    * [ ] Show a toast or feedback when an item is marked as purchased/unpurchased
    * [ ] Display item quantities in the shopping list UI
    * [ ] Implement editing of items in the shopping list (allow users to update name, quantity, category, icon, etc.)
* **Backend - Item Status Management:**
    * [ ] Ensure the PUT /items/{item_id} endpoint correctly updates the is_completed status and returns the updated item
    * [ ] Add validation for item update permissions (user owns list or has access to shared list)
    * [ ] Add audit logging for item status changes
* **Testing:**
    * [ ] Add/Update tests for marking items as purchased/unpurchased (API and UI)
    * [ ] Write/expand unit and integration tests for toggling item completion (backend and frontend)
    * [ ] Add edge case tests (e.g., toggling an item that doesn't exist, or that the user doesn't own)

## Sprint 4: AI-Powered Features Implementation

### User Stories:
* As a user, I want items to be automatically categorized so I don't have to manually select categories.
* As a user, I want items to have appropriate icons automatically generated.
* As a user, I want item category names to be standardized in English language and translated to language based on user settings.

### Tasks:
* **Backend - AI Integration Setup:**
    * [ ] Set up Google Gemini API integration in `core/config.py`
    * [ ] Create AI service layer (`services/ai_service.py`) for LLM interactions
    * [ ] Implement item categorization using AI LLM (category inferred from item name/description)
    * [ ] Implement automated icon selection/generation for items using AI LLM
    * [ ] Add AI-powered item name standardization and translation support
    * [ ] Create caching mechanism for AI-generated content to avoid unnecessary API calls
    * [ ] Implement rate limiting and cost optimization for AI API calls
* **Backend - Category System:**
    * [ ] Create `Category` model with support for translations
    * [ ] Implement category management endpoints (CRUD)
    * [ ] Add relationship between items and categories
    * [ ] Create migration for category system
* **Frontend - AI Features UI:**
    * [ ] Display AI-generated categories for items
    * [ ] Show AI-generated icons for items
    * [ ] Add UI feedback for AI processing (loading indicators)
    * [ ] Allow manual override of AI-generated categories and icons
* **Testing:**
    * [ ] Unit tests for AI service integration
    * [ ] Integration tests for category assignment
    * [ ] Mock tests for AI API calls to avoid costs during testing
    * [ ] Performance tests for AI response times

## Sprint 5: List Sharing & Collaboration

### User Stories:
* As a user, I want to invite family members to a shopping list so we can collaborate.
* As a user, I want to see who added or updated items in shared lists.
* As a user, I want to manage members of shared lists.

### Tasks:
* **Backend - Sharing System:**
    * [ ] Create `ListMember` model for managing list access
    * [ ] Implement list sharing endpoints (invite, accept, remove members)
    * [ ] Add permission system for shared lists (owner vs member permissions)
    * [ ] Track item changes with user attribution (who added/updated items)
    * [ ] Create migration for sharing system
* **Backend - User Management:**
    * [ ] Enhance user lookup by email for invitations
    * [ ] Add user profile endpoints for member display
    * [ ] Implement notification system for list invitations
* **Frontend - Collaboration UI:**
    * [ ] Create list sharing interface (invite by email)
    * [ ] Display list members and their roles
    * [ ] Show item attribution (who added/updated each item)
    * [ ] Add member management interface (remove members, transfer ownership)
    * [ ] Display pending invitations
* **Testing:**
    * [ ] Unit tests for sharing permissions
    * [ ] Integration tests for invitation flow
    * [ ] UI tests for collaboration features

## Sprint 6: Real-time Synchronization

### User Stories:
* As a user, I want to see real-time updates on shared lists so everyone sees changes instantly.
* As a user, I want to be notified when someone makes changes to shared lists.

### Tasks:
* **Backend - WebSocket Implementation:**
    * [ ] Implement WebSocket endpoint for real-time notifications
    * [ ] Create WebSocket manager to broadcast updates on list/item changes
    * [ ] Add logic to send notifications for item additions, updates, deletions
    * [ ] Add logic to send notifications for list sharing and member changes
    * [ ] Add logic to send notifications for category changes and reordering
    * [ ] Implement connection management and user session tracking
* **Frontend - Real-time Client:**
    * [ ] Integrate WebSocket client for real-time list updates
    * [ ] Handle real-time updates for item changes
    * [ ] Handle real-time updates for list membership changes
    * [ ] Add connection status indicators
    * [ ] Implement offline handling and sync when reconnected
* **Testing:**
    * [ ] Unit tests for WebSocket functionality
    * [ ] Integration tests for real-time synchronization
    * [ ] Load tests for multiple concurrent connections

## Sprint 7: Advanced Item Organization

### User Stories:
* As a user, I want to reorder items within categories so I can organize my shopping.
* As a user, I want to reorder entire categories so I can arrange the list according to my shopping route.
* As a user, I want items to be grouped by category for easier shopping.

### Tasks:
* **Backend - Ordering System:**
    * [ ] Add ordering fields to Item and Category models
    * [ ] Implement endpoints for reordering items within categories
    * [ ] Implement endpoints for reordering categories
    * [ ] Add validation for ordering operations
    * [ ] Create migration for ordering system
* **Frontend - Drag & Drop Interface:**
    * [ ] Implement drag and drop for reordering items within categories
    * [ ] Implement drag and drop for reordering categories
    * [ ] Add visual feedback during drag operations
    * [ ] Group items by category in the UI
    * [ ] Add category headers and collapsible sections
* **Testing:**
    * [ ] Unit tests for ordering logic
    * [ ] UI tests for drag and drop functionality
    * [ ] Integration tests for order persistence

## Sprint 8: OAuth2 Authentication

### User Stories:
* As a user, I want to log in using my Google account.
* As a user, I want to log in using my Apple ID.

### Tasks:
* **Backend - OAuth2 Integration:**
    * [ ] Add OAuth2 support to `fastapi-users` for Google authentication
    * [ ] Configure Google OAuth2 client ID/secret in `.env`
    * [ ] Research and configure Apple OAuth2 (App ID, Service ID, private key setup)
    * [ ] Add OAuth2 support to `fastapi-users` for Apple ID authentication
    * [ ] Add Apple OAuth2 router (custom or via `fastapi-users` compatible library)
    * [ ] Configure OAuth2 clients in `core/config.py`
* **Frontend - OAuth2 Login:**
    * [ ] Update frontend login page to include buttons for Google login
    * [ ] Update frontend login page to include buttons for Apple ID login
    * [ ] Handle OAuth2 callback flows
    * [ ] Add social login error handling
* **Testing:**
    * [ ] Write tests for OAuth2 login flows
    * [ ] Integration tests for OAuth2 callbacks
    * [ ] UI tests for social login buttons

## Sprint 9: Search & History Features

### User Stories:
* As a user, I want to search for items using my shopping history so I can quickly add frequently bought items.
* As a user, I want to see my shopping history so I can track what I have purchased.
* As a user, I want search results to be fast and relevant.

### Tasks:
* **Backend - Search & History:**
    * [ ] Implement item history tracking system
    * [ ] Create search endpoints with history integration
    * [ ] Add search indexing for fast as-you-type search (under 200ms)
    * [ ] Implement retention period for search results (limit to recent items)
    * [ ] Add shopping history endpoints
    * [ ] Create migration for history tracking
* **Frontend - Search & History UI:**
    * [ ] Implement as-you-type search with autocomplete
    * [ ] Display search results from history and global items
    * [ ] Create shopping history view
    * [ ] Add search result highlighting and ranking
    * [ ] Implement search filters and sorting options
* **Testing:**
    * [ ] Performance tests for search functionality (sub-200ms requirement)
    * [ ] Unit tests for history tracking
    * [ ] UI tests for search interface

## Sprint 10: Internationalization (I18n)

### User Stories:
* As a user, I want the application to support multiple languages so I can use it in my preferred language.
* As a user, I want item categories to be translated automatically.

### Tasks:
* **Backend - I18n Support:**
    * [ ] Set up i18n framework for backend
    * [ ] Implement category translation using LLM APIs
    * [ ] Add language preference to user model
    * [ ] Create translation caching system
    * [ ] Add API endpoints for language switching
* **Frontend - I18n Implementation:**
    * [ ] Set up frontend i18n framework
    * [ ] Implement language switching interface
    * [ ] Add translation keys for all UI components
    * [ ] Implement RTL language support if needed
    * [ ] Add locale-specific formatting (dates, numbers)
* **Testing:**
    * [ ] Unit tests for translation functionality
    * [ ] UI tests for language switching
    * [ ] Integration tests for LLM translation calls

## Future Sprints (Post-MVP)

### Sprint 11: Performance Optimization & Monitoring
* [ ] Implement caching strategy (Redis/Memcached)
* [ ] Set up monitoring and logging (Prometheus/Grafana)
* [ ] Database query optimization
* [ ] Frontend performance optimization
* [ ] Load testing and scalability improvements

### Sprint 12: Security & Compliance
* [ ] Implement GDPR compliance features
* [ ] Add data export/deletion capabilities
* [ ] Security audit and penetration testing
* [ ] Privacy policy implementation
* [ ] User consent management

### Sprint 13: Advanced Features
* [ ] Push notifications (PWA)
* [ ] Offline support and sync
* [ ] Recipe integration
* [ ] Price tracking and budget features
* [ ] Admin panel for system management

# Discovered During Work
* [x] Need to fix authentication router paths for proper frontend integration (2025-06-23)
* [x] User name handling during registration needs improvement (2025-06-23)
* [x] Authentication consistency between different API routers needs fixing (2025-06-24)
* [x] User profile name display needs fixing (2025-06-23)
* [x] Dashboard handler bug needs fixing (2025-06-24)
* [x] 500 error when renaming shopping cart needs fixing (2025-06-24)

# Sprint Timeline & Priorities

## Current Status (2025-06-24)
- ✅ **Sprint 1: Backend Foundation & Authentication** - COMPLETED
- ✅ **Sprint 2: Core Shopping List API** - COMPLETED
- 🔄 **Sprint 3: Item Completion & UI Enhancement** - IN PROGRESS

## Recommended Sprint Order & Timeline

### High Priority (Next 4-6 weeks)
1. **Sprint 3: Item Completion & UI Enhancement** (Week 1-2)
   - Critical for basic user experience
   - Completes core shopping list functionality
   
2. **Sprint 4: AI-Powered Features Implementation** (Week 3-4)
   - Key differentiator for the application
   - Automates user experience significantly
   
3. **Sprint 5: List Sharing & Collaboration** (Week 5-6)
   - Core family collaboration feature
   - Essential for multi-user functionality

### Medium Priority (Next 6-10 weeks)
4. **Sprint 6: Real-time Synchronization** (Week 7-8)
   - Enhanced user experience for shared lists
   - Technical foundation for real-time features
   
5. **Sprint 7: Advanced Item Organization** (Week 9-10)
   - Improves usability and shopping efficiency
   - Visual and UX enhancements

### Lower Priority (Post-MVP)
6. **Sprint 8: OAuth2 Authentication** (Week 11-12)
   - Nice-to-have for user convenience
   - Can be added after core features are solid
   
7. **Sprint 9: Search & History Features** (Week 13-14)
   - Performance and convenience improvements
   - Advanced user experience features
   
8. **Sprint 10: Internationalization (I18n)** (Week 15-16)
   - Expansion feature for broader user base
   - Can be implemented once core features are stable

## Success Metrics by Sprint

### Sprint 3 Success Criteria:
- [ ] Users can mark items as purchased/unpurchased with visual feedback
- [ ] Item quantities are clearly displayed in the UI
- [ ] Users can edit item details inline
- [ ] All item management operations work smoothly

### Sprint 4 Success Criteria:
- [ ] 90% of items are automatically categorized correctly
- [ ] Items have appropriate icons generated automatically
- [ ] AI processing time is under 2 seconds per item
- [ ] Manual override of AI suggestions works properly

### Sprint 5 Success Criteria:
- [ ] Users can successfully invite and manage list members
- [ ] Shared lists display proper attribution for item changes
- [ ] Permission system prevents unauthorized access
- [ ] Invitation flow is intuitive and reliable

### Sprint 6 Success Criteria:
- [ ] Real-time updates appear within 1 second across all clients
- [ ] WebSocket connections are stable and reconnect properly
- [ ] No data loss during connection interruptions
- [ ] Multiple users can collaborate simultaneously without conflicts

### Sprint 7 Success Criteria:
- [ ] Drag and drop reordering works smoothly on all devices
- [ ] Category grouping improves shopping efficiency
- [ ] Order changes persist correctly across sessions
- [ ] Visual feedback during reordering is clear and responsive

## Risk Assessment & Mitigation

### High Risk Items:
1. **AI API Integration (Sprint 4)**
   - Risk: API costs, rate limits, response quality
   - Mitigation: Implement caching, fallback mechanisms, cost monitoring
   
2. **Real-time Synchronization (Sprint 6)**
   - Risk: Connection management complexity, data consistency
   - Mitigation: Use proven WebSocket libraries, implement conflict resolution
   
3. **OAuth2 Implementation (Sprint 8)**
   - Risk: Apple OAuth complexity, security vulnerabilities
   - Mitigation: Use established libraries, thorough security testing

### Medium Risk Items:
1. **Performance Requirements (Sprint 9)**
   - Risk: Search latency exceeding 200ms target
   - Mitigation: Database indexing, search optimization, caching
   
2. **Frontend Complexity**
   - Risk: Complex UI interactions, mobile responsiveness
   - Mitigation: Progressive enhancement, thorough testing on multiple devices

## Next Steps Recommendation

### Immediate Actions (This Week):
1. Complete remaining Sprint 3 tasks
2. Set up development environment for AI integration
3. Research Google Gemini API documentation and pricing
4. Plan database schema changes for categories and AI features

### Week 2 Priorities:
1. Begin Sprint 4 AI integration work
2. Create comprehensive test cases for item completion features
3. Start frontend work for visual item status indicators
4. Document API endpoints for frontend team

### Dependencies to Address:
- Google Gemini API access and configuration
- Frontend framework decision and setup
- Testing strategy for AI features (mocking vs real API calls)
- Database migration strategy for new features

---

*Updated: 2025-06-24*
*Next Review: 2025-07-01*
