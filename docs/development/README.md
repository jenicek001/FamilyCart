# Development Workflow Documentation

**Purpose:** Development processes, coding standards, and workflow guidelines

---

## 📁 Files in this Directory

### Workflow Proposal
- **`DEVELOPMENT_WORKFLOW_PROPOSAL.md`** (372 lines) - Comprehensive development workflow
  - Git branching strategy
  - Code review process
  - Testing requirements
  - Deployment pipeline
  - Quality standards

---

## 🎯 Development Philosophy

### Core Principles
1. **Poetry 2.x for Python** - Modern dependency management
2. **Docker for Everything** - Consistent environments
3. **Test-Driven Development** - Tests first, code second
4. **Code Quality Standards** - Black, isort, pylint, bandit
5. **MCP Servers** - Use Context7, GitHub MCP for best practices

### AI Development Guidelines
```
Always use:
- Context7 MCP for up-to-date documentation
- Poetry 2.x and `poetry run`, not python directly
- Postgres MCP server for real database schema
- MCP servers to search and fetch best practices
```

---

## 🔄 Git Workflow

### Branch Strategy
```
main (protected)
  ↓
feature/feature-name
bugfix/issue-description
hotfix/critical-fix
```

### Commit Convention
```bash
feat: Add new feature
fix: Fix bug
chore: Maintenance tasks
docs: Documentation updates
test: Add or update tests
refactor: Code refactoring
```

---

## 🛠️ Development Tools

### Backend (Python)
- **Poetry 2.x** - Dependency management
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **Pytest** - Testing framework

### Frontend
- **React** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Material-UI** - Component library

### Code Quality
- **Black** - Code formatting
- **isort** - Import sorting
- **Pylint** - Code linting (target: 9.56/10)
- **Bandit** - Security scanning
- **ESLint** - JavaScript/TypeScript linting

---

## 📋 Development Environment Setup

### Prerequisites
```bash
# 1. Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# 2. Install Docker
# See: ../deployment/docker_installation_ubuntu.md

# 3. Clone repository
git clone https://github.com/jenicek001/FamilyCart.git
cd FamilyCart
```

### Backend Setup
```bash
cd backend
poetry install
poetry run alembic upgrade head

# Run development server
poetry run uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Development Database
```bash
# Start development PostgreSQL + Redis
docker compose -f docker-compose.dev.yml up -d

# Database on port 5434 (avoids UAT/CI conflicts)
# Redis on port 6381
```

---

## ✅ Quality Standards

### Code Quality Targets
- **Black** - 100% formatted
- **isort** - 100% organized imports
- **Pylint** - ≥ 9.56/10 score
- **Bandit** - No high/medium security issues
- **Test Coverage** - ≥ 80%

### Pre-Commit Checks
```bash
# Format code
poetry run black backend/app
poetry run isort backend/app

# Check quality
poetry run pylint backend/app
poetry run bandit -r backend/app

# Run tests
poetry run pytest
```

---

## 🧪 Testing

### Test Structure
```
backend/app/tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
└── conftest.py     # Test fixtures
```

### Running Tests
```bash
# All tests
poetry run pytest

# With coverage
poetry run pytest --cov=app --cov-report=html

# Specific test file
poetry run pytest app/tests/test_auth.py

# Watch mode (auto-rerun on changes)
poetry run pytest-watch
```

---

## 🚀 Development Workflow

### 1. Start New Feature
```bash
git checkout main
git pull origin main
git checkout -b feature/my-feature
```

### 2. Develop with Quality Checks
```bash
# Make changes
# Run formatters
poetry run black .
poetry run isort .

# Check quality
poetry run pylint app
poetry run bandit -r app

# Run tests
poetry run pytest
```

### 3. Commit and Push
```bash
git add .
git commit -m "feat: implement my feature"
git push origin feature/my-feature
```

### 4. Create Pull Request
- GitHub automatically runs CI checks
- Code review by team
- Merge after approval

---

## 📊 CI/CD Integration

### Automatic Checks on PR
- ✅ Code formatting (Black, isort)
- ✅ Linting (Pylint ≥ 9.56/10)
- ✅ Security scan (Bandit)
- ✅ Tests (Pytest)
- ✅ Build (Docker images)

### Deployment Pipeline
- **PR merged to main** → Build images
- **Images pushed** → ghcr.io registry
- **Auto-deploy** → UAT environment
- **Manual approval** → Production (future)

---

## 🔧 Troubleshooting

### Database Issues
```bash
# Reset development database
docker compose -f docker-compose.dev.yml down -v
docker compose -f docker-compose.dev.yml up -d

# Run migrations
cd backend
poetry run alembic upgrade head
```

### Dependency Issues
```bash
# Update dependencies
poetry update

# Lock file issues
poetry lock --no-update

# Clean install
rm -rf poetry.lock .venv
poetry install
```

---

## 📚 Related Documentation

- **Deployment:** `../deployment/` - Environment setup guides
- **GitHub/CI:** `../github/` - CI/CD and runner configuration
- **Features:** `../features/` - Feature specifications
- **Archives:** `../archives/` - Historical development docs

---

## 💡 Tips & Best Practices

### AI-Assisted Development
- Use Context7 MCP for library documentation
- Use GitHub MCP for issue discussions
- Use Postgres MCP for schema inspection
- Always verify AI suggestions with tests

### Performance
- Profile before optimizing
- Use database indexes appropriately
- Cache expensive operations
- Monitor with Prometheus/Grafana

### Security
- Never commit secrets
- Use environment variables
- Run Bandit on all code
- Keep dependencies updated

---

**For coding standards, see:** `../../global_rules.md`  
**For task management, see:** `../../TASKS.md`  
**For user stories, see:** `../../USER_STORIES.md`
