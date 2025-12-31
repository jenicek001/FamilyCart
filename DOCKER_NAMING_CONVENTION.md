# Docker Naming Convention

**Established:** December 31, 2025  
**Purpose:** Clear, consistent naming across all environments

---

## Naming Structure

**Format:** `familycart-{environment}-{service}`

- **Prefix:** Always `familycart`
- **Environment:** `dev`, `uat`, `prod`, `github-ci`, or omit for app services
- **Service:** Explicit service name (never generic like "db")

**Special Case - GitHub Services:**
- **GitHub Runners:** `familycart-github-runner-{1,2,3}`
- **GitHub CI:** `familycart-github-ci-{service}` (for GitHub Actions on self-hosted runners)

---

## Service Names

| Service Type | Name | Notes |
|--------------|------|-------|
| PostgreSQL | `postgres` | Never "db" |
| Redis | `redis` | Never "cache" |
| Backend API | `backend` | FastAPI application |
| Frontend | `frontend` | Next.js application |
| GitHub Runner | `runner-{1,2,3}` | Environment-independent |

---

## Container Names by Environment

### Development (`docker-compose.dev.yml`)
- `familycart-dev-postgres` - PostgreSQL database (port 5436)
- `familycart-dev-redis` - Redis cache (port 6382)
- `familycart-dev-backend` - FastAPI backend (port 8003)
- `familycart-dev-frontend` - Next.js frontend (port 3003)

### UAT (`docker-compose.uat.yml`)
- `familycart-uat-postgres` - PostgreSQL database (port 5435)
- `familycart-uat-redis` - Redis cache (port 6380)
- `familycart-uat-backend` - FastAPI backend (port 8001)
- `familycart-uat-frontend` - Next.js frontend (port 3001)

### Production (`docker-compose.prod.yml` - to be created)
- `familycart-prod-postgres` - PostgreSQL database
- `familycart-prod-redis` - Redis cache
- `familycart-prod-backend` - FastAPI backend
- `familycart-prod-frontend` - Next.js frontend

### CI Infrastructure (`docker-compose.ci-infrastructure.yml`)
**For GitHub Actions on self-hosted runners:**
- `familycart-github-ci-postgres` - PostgreSQL for CI tests (port 5432)
- `familycart-github-ci-redis` - Redis for CI tests (port 6379)
- `familycart-github-ci-adminer` - Database admin tool (port 8080, profile: admin-tools)
- `familycart-github-ci-redis-commander` - Redis admin tool (port 8081, profile: admin-tools)

### GitHub Runners (`docker-compose.runners.yml`)
**Environment-independent - shared across dev/uat/prod:**
- `familycart-github-runner-1` - Primary runner
- `familycart-github-runner-2` - Secondary runner
- `familycart-github-runner-3` - Tertiary runner
- `familycart-github-registry-cache` - Docker registry cache
- `familycart-github-runner-monitor` - Prometheus node exporter
- `familycart-github-runner-logs` - Log aggregator (profile: monitoring)

---

## Network Names

| Network | Purpose | Used By |
|---------|---------|---------|
| `familycart-dev-network` | Development | dev services |
| `familycart-uat-network` | UAT | uat services |
| `familycart-prod-network` | Production | prod services |
| `familycart-ci-infrastructure` | GitHub CI tests | github-ci services + runners |
| `familycart-runners` | GitHub Runners only | github runner services |

---

## Volume Names

### Development
- `familycart-dev-postgres-data` → postgres_dev_data
- `familycart-dev-redis-data` → redis_dev_data
- `familycart-dev-frontend-node-modules` → frontend_node_modules

### UAT
- `familycart-uat-postgres-data` → uat-postgres-data
- `familycart-uat-redis-data` → uat-redis-data

### CI
- `familycart-github-ci-postgres-data` → postgres-ci-data
- `familycart-github-ci-redis-data` → redis-ci-data

### Runners
- `familycart-github-runner-1-work` → runner1-work
- `familycart-github-runner-2-work` → runner2-work
- `familycart-github-runner-3-work` → runner3-work
- `familycart-github-build-cache` → build-cache
- `familycart-github-registry-cache` → registry-cache

---

## Port Allocation

| Environment | Postgres | Redis | Backend | Frontend |
|-------------|----------|-------|---------|----------|
| **GitHub CI** | 5432 | 6379 | N/A | N/A |
| **UAT** | 5435 | 6380 | 8001 | 3001 |
| **Dev** | 5436 | 6382 | 8003 | 3003 |
| **Prod** | Internal | Internal | 80/443 | 80/443 |

**Note:** Production services are behind nginx reverse proxy, no direct port exposure.

---

## Why This Convention?

### ✅ Benefits
1. **Clear ownership:** `familycart-` prefix identifies project
2. **Environment isolation:** Explicit env in every name
3. **Service clarity:** No generic "db" - always explicit "postgres"
4. **GitHub clarity:** `github-runner` and `github-ci` make purpose unambiguous
5. **Easy filtering:** `docker ps | grep familycart-dev-` or `grep familycart-github-`
6. **No conflicts:** Different ports prevent accidental overlap
7. **Logical grouping:** All related services share prefix pattern

### ❌ Anti-Patterns (NEVER USE)
- ❌ `db` - Too generic (use `postgres`)
- ❌ `cache` - Too generic (use `redis`)
- ❌ `runner-1` - Missing "github" context
- ❌ `ci-postgres` - Missing "github" context
- ❌ `runner-1-dev` - Runners are not environment-specific
- ❌ `dev-db` - Wrong order (env should be in middle)
- ❌ `postgres-ci-familycart` - Wrong order (project first)

---

## Migration Guide

### From Old Naming to New

```bash
# Old (inconsistent)
familycart-dev-db              → familycart-dev-postgres ✅
familycart-dev-redis           → familycart-dev-redis ✅ (already correct)
postgres-ci-familycart         → familycart-github-ci-postgres ✅ FIXED
redis-ci-familycart            → familycart-github-ci-redis ✅ FIXED
familycart-runner-1            → familycart-github-runner-1 ✅ FIXED
familycart-registry-cache      → familycart-github-registry-cache ✅ FIXED
```

### Updating Existing Deployments

1. **Stop old containers:**
   ```bash
   docker stop postgres-ci-familycart redis-ci-familycart
   docker stop familycart-runner-1 familycart-runner-2 familycart-runner-3
   docker rm postgres-ci-familycart redis-ci-familycart
   docker rm familycart-runner-1 familycart-runner-2 familycart-runner-3
   ```

2. **Update compose files** (already done in this commit)

3. **Recreate with new names:**
   ```bash
   docker compose -f docker-compose.ci-infrastructure.yml up -d
   docker compose -f docker-compose.runners.yml up -d
   ```

4. **Verify naming:**
   ```bash
   docker ps --format "table {{.Names}}\t{{.Image}}" | grep familycart
   ```

---

## Enforcement

### Pre-commit Checks
Add to `.github/workflows/lint.yml`:
```yaml
- name: Check Docker naming convention
  run: |
    # Ensure all container names start with "familycart-"
    grep -r "container_name:" docker-compose*.yml | \
      grep -v "familycart-" && exit 1 || exit 0
```

### Documentation
All new Docker Compose files **MUST** follow this convention.

---

**Last Updated:** December 31, 2025  
**Maintained By:** DevOps Team
