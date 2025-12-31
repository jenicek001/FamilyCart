# Docker-Based Development Guide

## Quick Start

### Prerequisites
- Docker Desktop installed and running
- Git
- 8GB+ RAM available for Docker

### Setup (First Time)

```bash
# 1. Clone the repository (if not already done)
git clone <repository-url>
cd FamilyCart

# 2. Start the development environment
./scripts/dev.sh start

# 3. Run initial database migrations
./scripts/dev.sh migrate

# 4. Open your browser
# Frontend: http://localhost:3000
# Backend API Docs: http://localhost:8000/docs
```

That's it! 🎉

## Development Workflow

### Daily Usage

```bash
# Start your day
./scripts/dev.sh start

# View logs while developing
./scripts/dev.sh logs backend    # Backend logs
./scripts/dev.sh logs frontend   # Frontend logs

# End your day
./scripts/dev.sh stop
```

### Common Tasks

#### Running Database Migrations

```bash
# Apply migrations
./scripts/dev.sh migrate

# Create new migration
./scripts/dev.sh migrate:create "add_user_preferences"
```

#### Running Tests

```bash
# Run all tests
./scripts/dev.sh test

# Run specific tests
./scripts/dev.sh test tests/unit/test_auth.py
./scripts/dev.sh test tests/integration/
```

#### Debugging

```bash
# Open shell in backend container
./scripts/dev.sh shell backend

# Open shell in frontend container
./scripts/dev.sh shell frontend

# View real-time logs
./scripts/dev.sh logs backend
./scripts/dev.sh logs frontend
```

#### Restarting Services

```bash
# Restart all services
./scripts/dev.sh restart

# Restart specific service
./scripts/dev.sh restart backend
./scripts/dev.sh restart frontend
```

#### Rebuilding After Dependency Changes

```bash
# Rebuild all services
./scripts/dev.sh rebuild

# Rebuild specific service
./scripts/dev.sh rebuild backend
./scripts/dev.sh rebuild frontend
```

#### Clean Slate

```bash
# Remove all containers and volumes (fresh start)
./scripts/dev.sh clean
```

## Hot-Reload

Both frontend and backend support hot-reload:

- **Backend**: Edit files in `backend/app/` - changes apply immediately
- **Frontend**: Edit files in `frontend/src/` - browser auto-refreshes

No need to restart containers! 🔥

## Services

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Next.js application |
| Backend API | http://localhost:8000 | FastAPI application |
| API Docs | http://localhost:8000/docs | Swagger UI |
| PostgreSQL | localhost:5432 | Database |
| Redis | localhost:6379 | Cache |

## Architecture

```
┌─────────────────────────────────────────────────┐
│           Development Environment               │
│  docker-compose -f docker-compose.dev.yml up    │
├─────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Frontend │  │ Backend  │  │ Runner-1 │      │
│  │ Next.js  │  │ FastAPI  │  │ Worker   │      │
│  │ :3000    │  │ :8000    │  │          │      │
│  │ HOT      │  │ HOT      │  │          │      │
│  │ RELOAD   │  │ RELOAD   │  │          │      │
│  └──────────┘  └──────────┘  └──────────┘      │
│       │              │              │           │
│       └──────────────┴──────────────┘           │
│                      │                          │
│  ┌───────────────────┴──────────────────┐      │
│  │  PostgreSQL 15  │  Redis 8.0         │      │
│  │  :5432          │  :6379             │      │
│  └────────────────────────────────────────┘     │
└─────────────────────────────────────────────────┘
```

## Configuration

Environment variables are managed through `config/.env.development`. This file is loaded by docker-compose.dev.yml.

**Key Variables**:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `NEXT_PUBLIC_API_URL` - Backend URL (for frontend)
- `DEBUG` - Enable debug mode
- `LOG_LEVEL` - Logging level

See `config/.env.development` for full list.

## Troubleshooting

### "Port already in use"

```bash
# Check what's using the port
lsof -i :3000
lsof -i :8000
lsof -i :5432

# Stop the conflicting service or change ports in docker-compose.dev.yml
```

### "Cannot connect to database"

```bash
# Check PostgreSQL is healthy
./scripts/dev.sh status

# If not healthy, restart
./scripts/dev.sh restart postgres

# View logs
./scripts/dev.sh logs postgres
```

### "Module not found" errors

```bash
# Backend - rebuild after dependency changes
./scripts/dev.sh rebuild backend

# Frontend - rebuild after dependency changes
./scripts/dev.sh rebuild frontend
```

### "Permission denied" errors

```bash
# Make sure dev script is executable
chmod +x scripts/dev.sh

# Check Docker has permission to access files
# On Mac/Windows: Check Docker Desktop file sharing settings
```

### Clean slate (when all else fails)

```bash
# Nuclear option - removes everything and starts fresh
./scripts/dev.sh clean
./scripts/dev.sh start
./scripts/dev.sh migrate
```

## IDE Integration

### VS Code

Install recommended extensions:
- Docker
- Python
- ESLint
- Prettier

**Debugging Backend**:
1. Add to `backend/app/main.py`:
   ```python
   import debugpy
   debugpy.listen(("0.0.0.0", 5678))
   ```
2. Add port to docker-compose.dev.yml backend service:
   ```yaml
   ports:
     - "8000:8000"
     - "5678:5678"
   ```
3. Use VS Code "Attach to Backend" launch configuration

**Debugging Frontend**:
- Next.js dev server automatically exposes debugger
- Attach Chrome DevTools to http://localhost:3000

### PyCharm / IntelliJ

Configure Docker Compose as remote interpreter:
1. Settings → Project → Python Interpreter
2. Add → Docker Compose
3. Select docker-compose.dev.yml
4. Service: backend

## Differences from Production

| Aspect | Development | Production |
|--------|-------------|------------|
| **Hot-reload** | ✅ Enabled | ❌ Disabled |
| **Source mounting** | ✅ Volumes | ❌ Copied |
| **Debug mode** | ✅ Enabled | ❌ Disabled |
| **Logging** | DEBUG level | WARNING level |
| **Secrets** | Weak defaults | Strong from vault |
| **Image size** | Larger (dev tools) | Optimized |

**IMPORTANT**: Development credentials are intentionally weak. Never use them in UAT or production!

## Comparison: Old vs New Workflow

### Before (Old Workflow)

```bash
# Terminal 1
cd backend
poetry install
poetry shell
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload

# Terminal 2
cd frontend
npm install
npm run dev

# Terminal 3 (maybe)
cd backend
poetry run python -m workers.main

# Issues:
- 3+ terminals to manage
- No PostgreSQL/Redis isolation
- Different from UAT/production
- Complex setup for new developers
```

### After (New Workflow)

```bash
# Single command
./scripts/dev.sh start

# Everything just works:
✅ PostgreSQL
✅ Redis
✅ Backend with hot-reload
✅ Frontend with hot-reload
✅ Workers
✅ Same as UAT/production
```

## Next Steps

1. **Try it out**: `./scripts/dev.sh start`
2. **Make a change**: Edit a file and see hot-reload
3. **Read the code**: Backend in `backend/app/`, Frontend in `frontend/src/`
4. **Run tests**: `./scripts/dev.sh test`
5. **Explore API**: http://localhost:8000/docs

## Getting Help

- **Script help**: `./scripts/dev.sh help`
- **Docker Compose help**: `docker-compose -f docker-compose.dev.yml --help`
- **Check status**: `./scripts/dev.sh status`
- **View logs**: `./scripts/dev.sh logs <service>`

## Advanced

### Custom Environment Variables

Create `backend/.env.local` (gitignored):
```bash
# Override specific variables
OPENAI_API_KEY=your-key-here
```

### Running without helper script

```bash
# Start
docker-compose -f docker-compose.dev.yml up -d

# Stop
docker-compose -f docker-compose.dev.yml down

# Logs
docker-compose -f docker-compose.dev.yml logs -f backend

# Shell
docker-compose -f docker-compose.dev.yml exec backend /bin/sh
```

### Performance on Windows/Mac

Docker on Windows/Mac can be slow with file mounts. Optimizations:

1. **Allocate more resources**: Docker Desktop → Settings → Resources
2. **Use named volumes for node_modules** (already configured)
3. **Enable VirtioFS** (Mac): Docker Desktop → Settings → General
4. **Use WSL2** (Windows): Much faster than Hyper-V

### Connecting from host

Services are accessible from your host machine:

```bash
# PostgreSQL
psql -h localhost -p 5432 -U familycart -d familycart

# Redis
redis-cli -h localhost -p 6379
```

---

**Questions?** Open an issue or ask in team chat!
