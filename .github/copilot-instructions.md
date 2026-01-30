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

## 🌿 Git Branch Strategy & Auto-Deployment

### Branch Structure (Established January 2026)
**Primary Branches:**
- **`main`** - Production baseline, always deployable
  - Tagged releases: `v1.0.0`, `v1.1.0`, `v1.2.0`, etc.
  - Deployed to production on merge
  - Protected branch: requires PR reviews
  - Source of truth for production state

- **`develop`** - Integration branch for UAT testing
  - Auto-deploys to UAT on every push (CI/CD pipeline)
  - Merges to `main` weekly (or when stable)
  - All features must pass UAT before production

**Reference Branches (Never Delete):**
- **`baseline/uat-2025-12-05`** - UAT baseline reference
  - Tagged: `v1.0.0-uat-baseline` at commit `d53f33d`
  - Historical reference for recovery
  - Never merge, never delete

**Backup Branches (Delete after 90 days):**
- **`backup/main-pre-cleanup-YYYY-MM-DD`** - Main branch snapshots
- **`backup/develop-pre-cleanup-YYYY-MM-DD`** - Develop branch snapshots
- Created before major restructuring
- Safe to delete after 3 months of stable operation

### Feature Branch Naming Conventions
- **Feature branches**: `feature/brief-description` (e.g., `feature/email-verification`)
- **Hotfix branches**: `hotfix/brief-description` (e.g., `hotfix/ssl-certificate-renewal`)
- **Bug fix branches**: `bugfix/brief-description` (e.g., `bugfix/websocket-timeout`)
- **Chore branches**: `chore/brief-description` (e.g., `chore/update-dependencies`)
- **Documentation branches**: `docs/brief-description` (e.g., `docs/api-update`)
- **Always use lowercase with hyphens** for readability and consistency
- **Keep branch names concise but descriptive** (max 50 characters)
- **Delete feature branches immediately after merge** to keep repository clean

### Auto-Deployment Workflow

#### Development Flow
```bash
# 1. Create feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/my-new-feature

# 2. Develop and test locally (see Pre-Push Checklist)
# ... make changes ...
poetry run pytest  # Backend tests must pass
npm run build      # Frontend must build

# 3. Commit and push
git add .
git commit -m "feat: implement my feature"
git push origin feature/my-new-feature

# 4. Create PR to develop
gh pr create --base develop --title "Feature: My new feature"

# 5. After PR approval and merge to develop:
# ✅ Auto-deploys to UAT (via CI/CD)
# ✅ Monitor: gh run watch
# ✅ Test in UAT: https://uat.familycart.app
```

#### Weekly Release Flow
```bash
# Every Friday (or when develop is stable)
git checkout main
git pull origin main
git merge develop --no-ff -m "release: merge develop to main for v1.x.0"

# Tag the release
git tag -a v1.x.0 -m "Release v1.x.0 - Brief description of changes"
git push origin main --tags

# ✅ Auto-deploys to production (when configured)
# ✅ Creates GitHub Release with changelog
```

#### Hotfix Flow (Emergency Production Fix)
```bash
# 1. Branch from main (not develop)
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug

# 2. Fix and test
# ... make minimal changes ...
poetry run pytest
npm run build

# 3. Merge to both main and develop
git checkout main
git merge hotfix/critical-bug
git tag -a v1.x.1 -m "Hotfix: Critical bug description"
git push origin main --tags

git checkout develop
git merge hotfix/critical-bug
git push origin develop

# 4. Delete hotfix branch
git branch -d hotfix/critical-bug
git push origin --delete hotfix/critical-bug
```

### CI/CD Auto-Deployment Rules

**Triggers:**
- **Push to `develop`** → Auto-deploy to UAT environment
  - UAT URL: https://uat.familycart.app
  - UAT API: http://localhost:8001 (local runner)
  - Monitoring: Prometheus + Grafana

- **Push to `main`** → Auto-deploy to production (when configured)
  - Production URL: https://familycart.app
  - Requires tagged release
  - Blue-green deployment strategy

**Branch Protection:**
- `main`: Requires PR reviews, status checks must pass
- `develop`: Requires status checks (can bypass reviews for maintainers)
- Direct pushes blocked (except for repository admins)

### Branch Lifecycle Management

**Active Branches (Keep):**
- `main`, `develop` - Core branches
- `baseline/*` - Reference branches
- `backup/*` - Recent backups (<90 days)
- `feature/*`, `bugfix/*`, `hotfix/*` - Active work

**Delete Immediately After Merge:**
- All feature branches once merged
- All bugfix branches once merged
- Hotfix branches once merged to both main and develop

**Auto-Deletion:**
- Enable in GitHub: Settings → General → Pull Requests
- ✅ "Automatically delete head branches"
- Reduces branch clutter automatically

### Version Tagging Strategy

**Semantic Versioning (SemVer):**
- `vMAJOR.MINOR.PATCH` (e.g., `v1.2.3`)
- **MAJOR**: Breaking changes, major features
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, hotfixes

**Special Tags:**
- `v1.0.0-uat-baseline` - UAT baseline reference
- `v1.0.0-rc.1` - Release candidates
- `v1.0.0-beta.1` - Beta releases

**Tagging Commands:**
```bash
# Create annotated tag
git tag -a v1.2.0 -m "Release v1.2.0: Email verification + dashboard fixes"

# Push tag
git push origin v1.2.0

# List all tags
git tag -l

# Delete tag (if mistake)
git tag -d v1.2.0
git push origin --delete v1.2.0
```

### Commit Message Format

**Structure:**
```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code formatting (no logic change)
- `refactor:` - Code restructuring
- `test:` - Adding/updating tests
- `chore:` - Build/tool changes

**Examples:**
```bash
git commit -m "feat: implement email verification for user registration

- Add email service with Brevo SMTP integration
- Create verification email template
- Add verification endpoint and UI flow
- Update tests to auto-verify test users

Closes #42"

git commit -m "fix: resolve WebSocket connection timeout in UAT

- Increase connection timeout to 30s
- Add CORS headers for WebSocket handshake
- Update nginx configuration for WebSocket proxy

Fixes #38"
```

## 🚀 CI/CD Workflow - CRITICAL PROCESS RULES

### ⚠️ NEVER Push Without Local Testing - Cost & Time Critical
**Every git push triggers expensive CI/CD pipeline runs. Follow this process religiously:**

### 📋 Pre-Push Checklist (MANDATORY)
**Before ANY `git push`, you MUST complete ALL these steps locally:**

#### 1. Review CI/CD Pipeline Requirements
```bash
# Read the pipeline definition to understand what will be tested
cat .github/workflows/ci-cd.yml
```
**Identify all jobs that will run:** tests, linting, type checking, builds, security scans

#### 2. Backend Local Verification (if backend changes)
```bash
cd backend

# Run ALL tests (must pass 100%)
poetry run pytest -v

# Check code formatting
poetry run black --check app/

# Check import sorting
poetry run isort --check-only app/

# Run linter (must be ≥9.56/10)
poetry run pylint app/

# Run security scan
poetry run bandit -r app/

# Verify migrations (if database changes)
poetry run alembic upgrade head
poetry run alembic downgrade -1
poetry run alembic upgrade head
```

#### 3. Frontend Local Verification (if frontend changes)
```bash
cd frontend

# Install dependencies (if package.json changed)
npm install

# Run linter
npm run lint

# Run type checking
npm run typecheck

# Build for production (CRITICAL - catches build-time errors)
npm run build

# Run tests (if tests exist)
npm test
```

#### 4. Integration Testing (if both backend + frontend changed)
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d
cd backend && poetry run uvicorn app.main:app --reload &
cd frontend && npm run dev &

# Test the actual user flow end-to-end
# Verify API responses, UI behavior, error handling
```

#### 5. Commit Strategy
**MAKE ONE COMPREHENSIVE COMMIT, NOT MULTIPLE SMALL ONES**
```bash
# Stage all related changes together
git add backend/ frontend/ docs/

# Write descriptive commit message
git commit -m "feat: implement email verification enforcement

- Changed all protected endpoints to require verified users
- Added verification UI flow with resend capability
- Updated test fixtures to auto-verify test users
- Fixed Next.js build issues with Suspense wrapper
- All tests passing (71/71 backend tests)
- Frontend build successful
- Security scans passing"

# Only NOW push to remote
git push origin develop
```

### 🚫 FORBIDDEN PRACTICES - NEVER DO THESE

#### ❌ Trial-and-Error Git Pushing
**NEVER:** Push → Watch fail → Fix one thing → Push again → Repeat
```bash
# DON'T DO THIS:
git commit -m "fix test users"          # Push 1
git commit -m "fix imports"             # Push 2
git commit -m "fix typescript"          # Push 3
git commit -m "fix build"               # Push 4
git commit -m "add suspense"            # Push 5
git commit -m "fix another thing"       # Push 6
```

**INSTEAD:** Test everything locally first, make ONE commit with all fixes

#### ❌ Assuming Tests Will Pass
**NEVER:** Skip running tests locally because "it should work"
- CI/CD environment may differ from your assumptions
- Tests may fail due to: unverified test users, import order, TypeScript errors, build config
- **ALWAYS run `poetry run pytest` and `npm run build` locally first**

#### ❌ Ignoring CI/CD Pipeline Definition
**NEVER:** Push without understanding what the pipeline will test
- Read `.github/workflows/ci-cd.yml` to see all checks
- Replicate those checks locally BEFORE pushing
- Don't guess - verify against the actual pipeline requirements

#### ❌ Partial Testing
**NEVER:** Only test the specific feature you changed
- Run the FULL test suite (`poetry run pytest` without filters)
- Run FULL build (`npm run build` not just `npm run dev`)
- Check ALL code quality tools (black, isort, pylint, eslint)

### ✅ CORRECT WORKFLOW EXAMPLE

```bash
# 1. Make your code changes
vim backend/app/api/v1/endpoints/shopping_lists.py

# 2. Review what CI/CD will test
cat .github/workflows/ci-cd.yml | grep -A10 "run:"

# 3. Run ALL checks locally (Backend)
cd backend
poetry run pytest -v                    # Must show 71/71 passing
poetry run black --check app/           # Must show "All done! ✨ 🍰 ✨"
poetry run isort --check-only app/      # Must show no changes needed
poetry run pylint app/                  # Must show ≥9.56/10

# 4. Run ALL checks locally (Frontend)
cd ../frontend
npm run lint                            # Must show no errors
npm run typecheck                       # Must show no type errors
npm run build                           # Must complete successfully

# 5. ONLY if ALL checks pass, commit and push
cd ..
git add backend/ frontend/
git commit -m "feat: comprehensive change description with all fixes"
git push origin develop

# 6. Monitor CI/CD (should succeed on first try)
gh run watch
```

### 💰 Cost & Time Implications
- **Each CI/CD run costs money** (GitHub Actions minutes, runner compute time)
- **Each CI/CD run takes 10-15 minutes** (tests, builds, deployments)
- **Failed runs waste both money and time**
- **Six failed runs = 60-90 minutes wasted + 6x the cost**

**Proper local testing saves:**
- ✅ Money (one successful run vs. multiple failed runs)
- ✅ Time (15 minutes vs. 90+ minutes)
- ✅ Reputation (professional vs. chaotic workflow)
- ✅ CI/CD resources (keeps pipeline fast for urgent fixes)

### 📊 CI/CD Pipeline Monitoring
```bash
# Check recent CI/CD runs
gh run list --branch develop --limit 5

# Watch current run (only AFTER pushing)
gh run watch

# View detailed results
gh run view <run-id>

# View logs for failed jobs
gh run view <run-id> --log-failed
```

### 🎯 Success Criteria
**A git push is ONLY acceptable when:**
1. ✅ All backend tests pass locally (poetry run pytest)
2. ✅ All code quality checks pass locally (black, isort, pylint)
3. ✅ Frontend builds successfully locally (npm run build)
4. ✅ All linting/type checking passes locally (npm run lint, typecheck)
5. ✅ Integration testing completed for user-facing changes
6. ✅ You understand exactly what the CI/CD pipeline will test
7. ✅ ONE comprehensive commit contains all related fixes

**If ANY of the above are not met: DO NOT PUSH**

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
- **CRITICAL: Before ANY `git push`, follow the complete Pre-Push Checklist in the CI/CD Workflow section above.** This is non-negotiable and saves significant time and money.
- **Use documentation and facts, never trial-and-error with git pushes.** Research proper solutions using Context7, Brave Search, or official docs before implementing.
- **When developing new features, adding new modules or libraries or debugging issues** - always use Context7 MCP server to reference up-to-date API documentation and code examples for any libraries or frameworks involved. Add 'use context7' to your prompt or leverage the Context7 MCP server for the most current, version-specific docs.
- **Use Postgres MCP server** to get real, up-to-date database schema (don't assume table structures)
- **Use Brave Search MCP** to find best practices, issue discussions, or articles on the internet
- **Never hallucinate libraries or functions** – only use known, verified Python packages.
- **Always confirm file paths and module names** exist before referencing them in code or tests.
- **Never delete or overwrite existing code** unless explicitly instructed to or if part of a task from `TASKS.md`.
- **Respect the repository structure** - place files in appropriate directories as defined above
- **Test locally BEFORE pushing** - this includes running full test suites, builds, linters, and type checkers. Every push triggers expensive CI/CD runs.

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