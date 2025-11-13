````instructions
# GitHub Copilot Instructions for FamilyCart

## 📁 Repository Structure (Updated October 2025)

### Root Directory (Essential Files Only)
- **Project Files**: `README.md` (main documentation), `TASKS.md` (active tasks), `USER_STORIES.md` (requirements), `PLANNING.md` (roadmap)
- **Docker Compose Files**:
  - `docker-compose.dev.yml` - Local development (PostgreSQL port 5434, Redis port 6381)
  - `docker-compose.uat.yml` - UAT environment deployment (used by CI/CD pipeline)
  - `docker-compose.uat-monitoring.yml` - UAT monitoring stack (Prometheus, Grafana)
  - `docker-compose.runners.yml` - GitHub self-hosted runners (3 active runners)
  - `docker-compose.ci-infrastructure.yml` - CI services (PostgreSQL port 5432, Redis port 6379)

### Organized Documentation Structure
- **`docs/deployment/`** - Deployment guides, infrastructure setup, Cloudflare configuration
- **`docs/github/`** - CI/CD setup, GitHub runners, environment configuration
- **`docs/development/`** - Development workflow, coding standards
- **`docs/features/`** - Feature specifications and implementation guides
- **`docs/archives/`** - Historical documentation (sprints, fixes, ci-cd, test-reports)

**IMPORTANT FILE PLACEMENT RULES:**
- ✅ **Planning documents** → `docs/` (e.g., `docs/EMAIL_SERVICE_IMPLEMENTATION_PLAN.md`)
- ✅ **Feature specifications** → `docs/features/` (e.g., `docs/features/websocket-implementation.md`)
- ✅ **Sprint reports** → `docs/archives/sprints/` (e.g., `docs/archives/sprints/SPRINT_7_REPORT.md`)
- ✅ **Bug fix documentation** → `docs/archives/fixes/` (e.g., `docs/archives/fixes/websocket-connection-fix.md`)
- ✅ **Deployment guides** → `docs/deployment/` (e.g., `docs/deployment/DEPLOY_SELF_HOSTED_UAT.md`)
- ✅ **Analysis documents** → `docs/` (e.g., `docs/CZECH_CATEGORIZATION_ANALYSIS.md`)
- ❌ **NEVER create new .md files in repository root** except for the 4 essential files listed above

**Note:** Nginx reverse proxy runs from a separate repository on the host machine. This repo contains only nginx configuration templates.

### Scripts Organization
- **`scripts/`** - Main operational scripts (push-docker-images.sh, update-github-token.sh)
- **`scripts/uat/`** - UAT-specific scripts (setup-cloudflare-monitoring.sh, test-uat-nginx.sh)
- **`scripts/testing/`** - Test and debug scripts

### Backend & Frontend
- **`backend/`** - FastAPI backend with Poetry 2.x (use `poetry run`, never `python` directly)
- **`frontend/`** - React/TypeScript frontend

### Infrastructure Directories
- **`deploy/`** - Deployment scripts and configuration templates
- **`monitoring/`** - Active UAT monitoring stack (Prometheus, Grafana, Alertmanager)
- **`nginx/`** - Nginx configuration templates (actual nginx runs from separate repo on host machine)

## 🔄 Project Awareness & Context
- **Always read `PLANNING.md`** at the start of a new conversation to understand the project's architecture, goals, style, and constraints.
- **Check `TASKS.md`** before starting a new task. If the task isn't listed, add it with a brief description and today's date.
- **Use consistent naming conventions, file structure, and architecture patterns** as described in `PLANNING.md`.
- **For deployment information**, check `docs/deployment/` directory
- **For CI/CD setup**, check `docs/github/` directory
- **For development workflow**, check `docs/development/` directory
- **For feature specs**, check `docs/features/` directory

## 🌿 Git Branch Naming Conventions
- **Feature branches**: `feature/sprint-N-brief-description` (e.g., `feature/sprint-7-visual-identity`)
- **Hotfix branches**: `hotfix/brief-description` (e.g., `hotfix/ssl-certificate-renewal`)
- **Release branches**: `release/vN.N.N` (e.g., `release/v2.0.0`)
- **Bug fix branches**: `bugfix/brief-description` (e.g., `bugfix/websocket-connection-timeout`)
- **Chore branches**: `chore/brief-description` (e.g., `chore/update-dependencies`)
- **Documentation branches**: `docs/brief-description` (e.g., `docs/api-documentation-update`)
- **Always use lowercase with hyphens** for readability and consistency
- **Keep branch names concise but descriptive** (max 50 characters recommended)
- **Delete feature branches** after successful merge to keep repository clean
- **Use `develop` branch** for integration of completed features before production release

## 🧱 Code Structure & Modularity Rules for AI IDE
- **Never create a file longer than 500 lines of code.** If a file approaches this limit, refactor by splitting it into modules or helper files.
- **Organize code into clearly separated modules**, grouped by feature or responsibility.
- **Use clear, consistent imports** (prefer relative imports within packages).

## ✅ Task Completion & Documentation
- **Mark completed tasks in `TASKS.md`** immediately after finishing them.
- Add new sub-tasks or TODOs discovered during development to `TASKS.md` under a "Discovered During Work" section.
- **Sprint summaries** should be placed in `docs/archives/sprints/` (not root directory)
- **Fix documentation** should go in `docs/archives/fixes/`
- **New features** should be documented in `docs/features/` with comprehensive specifications
- **Planning documents** (implementation plans, analysis, technical design) should go in `docs/` or appropriate subdirectory
- **CRITICAL: NEVER create new markdown files in the repository root directory** - the root should ONLY contain:
  - `README.md` - Main project documentation
  - `TASKS.md` - Active task tracking
  - `USER_STORIES.md` - Requirements and user stories
  - `PLANNING.md` - High-level roadmap and vision
  - Docker compose files (dev, uat, ci, runners, monitoring)
- **All other documentation MUST go in the `docs/` directory hierarchy**

## 📚 Documentation & Explainability
- **Update `README.md`** when new features are added, dependencies change, or setup steps are modified.
- **Comment non-obvious code** and ensure everything is understandable to a mid-level developer.
- When writing complex logic, **add an inline `# Reason:` comment** explaining the why, not just the what.

## 🧠 AI Behavior Rules
- **Never assume missing context. Ask questions if uncertain.**
- **When developing new features, adding new modules or libraries or debugging issues** - always use Context7 MCP server to reference up-to-date API documentation and code examples for any libraries or frameworks involved. Add 'use context7' to your prompt or leverage the Context7 MCP server for the most current, version-specific docs.
- **Use Postgres MCP server** to get real, up-to-date database schema (don't assume table structures)
- **Use Brave Search MCP** to find best practices, issue discussions, or articles on the internet
- **Never hallucinate libraries or functions** – only use known, verified Python packages.
- **Always confirm file paths and module names** exist before referencing them in code or tests.
- **Never delete or overwrite existing code** unless explicitly instructed to or if part of a task from `TASKS.md`.
- **Respect the repository structure** - place files in appropriate directories as defined above

## Backend-specific rules

### 🧪 Testing & Reliability
- **Always create Pytest unit tests for new features** (functions, classes, routes, etc).
- **After updating any logic**, check whether existing unit tests need to be updated. If so, do it.
- **Tests should live in a `/tests` folder** mirroring the main app structure.
  - Include at least:
    - 1 test for expected use
    - 1 edge case
    - 1 failure case


### 📎 Style & Conventions
- **Use Python 3.12+** as the primary language for Backend.
- **Use Poetry 2.x** for dependency management - always use `poetry run` commands, NEVER `python` directly
- **Follow PEP8**, use type hints, and format with `black`.
- **Use `pydantic` for data validation**.
- **Use `FastAPI`** for APIs and **`SQLAlchemy` (async)** for ORM.
- **Database migrations** via Alembic (see `alembic.ini` in root and `backend/alembic/`)
- Write **docstrings for every function** using the Google style:
  ```python
  def example():
      """
      Brief summary.

      Args:
          param1 (type): Description.

      Returns:
          type: Description.
      """
  ```

### 🔧 Backend Development Environment
- **Development database**: Use `docker-compose.dev.yml` (PostgreSQL port 5434, Redis port 6381)
- **CI infrastructure**: Runs on ports 5432 (PostgreSQL) and 6379 (Redis) - don't conflict
- **UAT environment**: Deployed to `/opt/familycart-uat/` via CI/CD pipeline
- **Migrations**: `cd backend && poetry run alembic upgrade head`
- **Run server**: `cd backend && poetry run uvicorn app.main:app --reload`
- **Run tests**: `cd backend && poetry run pytest`
- **Code quality**: 
  - `poetry run black app/`
  - `poetry run isort app/`
  - `poetry run pylint app/` (target: ≥9.56/10)
  - `poetry run bandit -r app/`

## Frontend-specific rules

### General Code Style & Formatting
- **Use TypeScript** as the primary language for Frontend.
- **Follow Prettier** for code formatting.
- Use functional and declarative programming patterns; avoid classes.
- Prefer iteration and modularization over code duplication.
- Use descriptive variable names with auxiliary verbs (e.g., isLoading, hasError).
- Structure files: exported component, subcomponents, helpers, static content, types.
- Follow Expo's official documentation for setting up and configuring projects.

### Naming Conventions
- Use lowercase with dashes for directories (e.g., components/auth-wizard).
- Favor named exports for components.

### TypeScript Best Practices
- Use TypeScript for all code; prefer interfaces over types.
- Avoid any and enums; use explicit types and maps instead.
- Use functional components with TypeScript interfaces.
- Enable strict mode in TypeScript for better type safety.

### Syntax & Formatting
- Use the function keyword for pure functions.
- Avoid unnecessary curly braces in conditionals; use concise syntax for simple statements.
- Use declarative JSX.
- Use Prettier for consistent code formatting.

### Styling & UI
- Use Expo's built-in components for common UI patterns and layouts.
- Implement responsive design with Flexbox and useWindowDimensions.
- Use styled-components or Tailwind CSS for styling.
- Implement dark mode support using Expo's useColorScheme.
- Ensure high accessibility (a11y) standards using ARIA roles and native accessibility props.
- Use react-native-reanimated and react-native-gesture-handler for performant animations and gestures.