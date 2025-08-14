# TASKS.md
## Purpose of this file: Tracks current tasks, backlog, and sub-tasks.
* Tracks current tasks, backlog, and sub-tasks.
* Includes: Bullet list of active work, milestones, and anything discovered mid-process.
* Prompt to AI: "Update TASK.md to mark XYZ as done and add ABC as a new task."
* Prompt for Copilot: "Analyze tasks for next sprint and start with sprint implementation. Always use context7 MCP to get up to date documentation. Use Poetry 2.x and poetry run, not python directly. Use postgres MCP server to get real up to date database schema. Use MCP servers search and fetch to find best practice or issue discussions or articles on the internet."

# Sprint Overview & Status

## Completed Sprints ✅

### Sprint 1: Backend Foundation & Authentication ✅ COMPLETED
**Duration**: May 2025  
**Key Deliverables**: FastAPI setup, PostgreSQL integration, JWT authentication, user management  
**Status**: Production ready  
**Details**: See detailed sprint reports in `/sprints/` folder

### Sprint 2: Core Shopping List API ✅ COMPLETED
**Duration**: June 2025  
**Key Deliverables**: CRUD operations, Stitch UI redesign, enhanced dashboard, list management  
**Status**: Production ready  
**Report**: [SPRINT_2_REPORT.md](./sprints/SPRINT_2_REPORT.md)

### Sprint 3: Item Completion & UI Enhancement ✅ COMPLETED
**Duration**: June 2025  
**Key Deliverables**: Item completion system, category-based sorting, nickname support, timezone fixes  
**Status**: Production ready  
**Report**: [SPRINT_3_REPORT.md](./sprints/SPRINT_3_REPORT.md)

### Sprint 4: AI-Powered Features Implementation ✅ COMPLETED
**Duration**: June-July 2025  
**Key Deliverables**: Automatic categorization, AI icons, Czech language support, 92x performance improvement  
**Status**: Production ready  
**Report**: [SPRINT_4_REPORT.md](./sprints/SPRINT_4_REPORT.md)

### Sprint 5: List Sharing & Collaboration ✅ COMPLETED
**Duration**: July 2025  
**Key Deliverables**: Basic sharing functionality, member management, invitation system foundation  
**Status**: Core features complete, advanced features moved to Sprint 7  
**Report**: [SPRINT_5_REPORT.md](./sprints/SPRINT_5_REPORT.md)

### Sprint 6: Real-time Synchronization ✅ COMPLETED 🎉
**Duration**: July 2025  
**Key Deliverables**: JWT-authenticated WebSockets, real-time updates, connection management  
**Status**: Production ready  
**Report**: [SPRINT_6_REPORT.md](./sprints/SPRINT_6_REPORT.md)

### Sprint 8: AI Enhancement and Ollama Integration ✅ COMPLETED
**Duration**: January-July 2025  
**Key Deliverables**: Multi-provider AI system, automatic fallback, comprehensive benchmarking  
**Status**: Production ready  
**Report**: [SPRINT_8_REPORT.md](./sprints/SPRINT_8_REPORT.md)

## Current Sprint 🔄

## Sprint 7: Enhanced Collaboration & Advanced Organization

### User Stories:
* As a user, I want to send professional invitation emails to non-existent users so they can join my shopping lists.
* As a user, I want to see the status of my sent invitations and manage them.
* As a new user, I want to automatically gain access to lists I was invited to when I register.
* As a user, I want to reorder items within categories so I can organize my shopping.
* As a user, I want to reorder entire categories so I can arrange the list according to my shopping route.
* As a user, I want better permission controls for shared lists (owner vs member permissions).

### Tasks:

* **Backend - Email Service Integration:**
    * [ ] Configure production email service (SendGrid, AWS SES, or SMTP)
    * [ ] Create professional HTML email templates for list invitations
    * [ ] Implement invitation tracking database model (`Invitation` table)
    * [ ] Add invitation expiration and cleanup logic (7-day expiry)
    * [ ] Create email verification for new registrations
    * [ ] Integrate with real email service (replace console logging)

* **Backend - Enhanced Invitation Management:**
    * [ ] Add permission system for shared lists (owner vs member permissions)
    * [ ] Endpoint to list pending invitations sent by user (`GET /invitations/sent`)
    * [ ] Endpoint to list pending invitations received by email (`GET /invitations/received`)
    * [ ] Auto-accept invitations during user registration (email matching)
    * [ ] Resend invitation functionality (`POST /invitations/{id}/resend`)
    * [ ] Cancel invitation functionality (`DELETE /invitations/{id}`)
    * [ ] Track invitation status (pending, accepted, expired, cancelled)

* **Backend - Advanced Item Organization:**
    * [ ] Add ordering fields to Item and Category models (`sort_order` columns)
    * [ ] Implement endpoints for reordering items within categories
        * `PUT /shopping-lists/{list_id}/items/reorder` (bulk reorder within categories)
        * `PUT /items/{item_id}/position` (move single item position)
    * [ ] Implement endpoints for reordering categories
        * `PUT /shopping-lists/{list_id}/categories/reorder` (category order)
    * [ ] Add validation for ordering operations (prevent conflicts)
    * [ ] Create migration for ordering system

* **Frontend - Enhanced Collaboration UI:**
    * [ ] Pending invitations section in ShareDialog with status indicators
    * [ ] Invitation status indicators (sent, pending, expired, accepted)
    * [ ] Resend/cancel invitation buttons with confirmation dialogs
    * [ ] Email validation improvements in invite form (real-time validation)
    * [ ] Display pending invitations count in ShareDialog header
    * [ ] Auto-accept invitations interface for new users
    * [ ] Permission-based UI controls (owner vs member actions)

* **Frontend - Drag & Drop Interface:**
    * [ ] Install and configure `react-beautiful-dnd` or `@dnd-kit/core` for drag and drop
    * [ ] Implement drag and drop for reordering items within categories
        * Visual feedback during drag operations
        * Drop zones between items within same category
        * Prevent dragging across categories (separate feature)
    * [ ] Implement drag and drop for reordering categories
        * Category header drag handles
        * Visual feedback for category reordering
        * Collapsible/expandable category sections
    * [ ] Add visual feedback during drag operations (ghost items, drop indicators)
    * [ ] Group items by category in the UI (already implemented)
    * [ ] Add category headers and collapsible sections
    * [ ] Persist reorder changes immediately (optimistic updates + API calls)

* **Testing:**
    * [ ] Email service integration tests (mock SMTP, SendGrid)
    * [ ] Invitation lifecycle tests (create, send, accept, expire workflow)
    * [ ] UI tests for invitation management (Playwright tests)
    * [ ] Unit tests for ordering logic (backend)
    * [ ] UI tests for drag and drop functionality (Playwright drag tests)
    * [ ] Integration tests for order persistence
    * [ ] End-to-end invitation workflow tests

### 📊 SPRINT 7 PROGRESS: 🔄 0% Complete - Enhanced Collaboration & Advanced Organization
**STATUS**: Ready to begin with comprehensive task list combining email invitations, permission system, and drag & drop organization features.

### **Sprint 7 Success Criteria:**
- [ ] Professional invitation emails sent to non-existent users
- [ ] Users can view and manage pending invitations
- [ ] New users automatically added to lists they were invited to
- [ ] Intuitive drag and drop reordering for items and categories
- [ ] Order changes persist across sessions and sync in real-time
- [ ] Permission system distinguishes owner vs member capabilities
- [ ] All collaboration features have proper error handling and feedback

### **Technical Priorities:**
1. **Email System** (High Priority): Complete invitation workflow for better collaboration
2. **Permission System** (High Priority): Proper role-based access control
3. **Drag & Drop** (Medium Priority): Enhanced user experience for organization
4. **UI Polish** (Medium Priority): Professional invitation management interface

### **Dependencies & Notes:**
- Email service configuration needs environment variables and provider selection
- Drag and drop library selection should prioritize accessibility and mobile support
- Permission system should be backward compatible with existing shared lists
- Real-time updates should work with reordering (WebSocket integration)

## Future Sprints (Planned)

### Sprint 9: OAuth2 Authentication
* Google OAuth2 integration
* Apple ID authentication
* Social login UI improvements

### Sprint 10: Search & History Features
* Item search with autocomplete
* Shopping history tracking
* Personalized suggestions

### Sprint 11: Internationalization (I18n)
* Multi-language support
* Category translation system
* Locale-specific formatting

## Future Sprints (Post-MVP)

### Sprint 12: Performance Optimization & Monitoring
* Caching strategy implementation
* Monitoring and logging setup
* Database query optimization
* Frontend performance optimization

### Sprint 13: Security & Compliance
* GDPR compliance features
* Data export/deletion capabilities
* Security audit and penetration testing
* Privacy policy implementation

### Sprint 14: Advanced Features
* Push notifications (PWA)
* Offline support and sync
* Recipe integration
* Price tracking and budget features

# Critical Bug Fixes & Issues 🐛

For detailed documentation of major bug fixes and debugging sessions, see:
**[BUG_FIXES_REPORT.md](./sprints/BUG_FIXES_REPORT.md)**

## Recent Major Fixes (July 2025):
* **Backend Serialization**: Fixed shared user access issues
* **WebSocket Stability**: Eliminated connection errors and loops  
* **AI Performance**: 92x improvement (25s → 0.27s)
* **Czech Language**: 100% categorization accuracy
* **Timezone Handling**: Systematic UTC/local time fixes

# Sprint Timeline & Priorities

## Current Status (July 2025)
- ✅ **Sprints 1-6**: Core functionality complete and production ready
- ✅ **Sprint 8**: AI enhancements and multi-provider system complete
- 🔄 **Sprint 7**: Enhanced collaboration and organization (current focus)

## Success Metrics by Sprint

### Sprint 7 Success Criteria:
- [ ] Professional invitation email system operational
- [ ] Drag and drop reordering works smoothly on all devices
- [ ] Permission system distinguishes owner vs member capabilities
- [ ] Order changes persist correctly across sessions
- [ ] All collaboration features have proper error handling

## Risk Assessment & Mitigation

### Current Sprint 7 Risks:
1. **Email Service Integration**: Choose reliable provider and implement fallbacks
2. **Drag & Drop Complexity**: Select accessibility-friendly library with mobile support
3. **Permission System**: Ensure backward compatibility with existing shared lists
4. **Real-time Integration**: Coordinate ordering changes with WebSocket updates

### Mitigation Strategies:
* Use established email service providers (SendGrid, AWS SES)
* Comprehensive testing for drag and drop across devices
* Gradual permission system rollout with existing list support
* Thorough integration testing for real-time order synchronization

---

*Updated: July 6, 2025*  
*Next Review: July 13, 2025*  
*Current Sprint: Sprint 7 - Enhanced Collaboration & Advanced Organization*
