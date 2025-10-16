# Archived Docker Compose Files

**Date Archived:** October 16, 2025  
**Reason:** Cleanup of obsolete/duplicate configurations

---

## Files in this directory

### `docker-compose.yml.legacy`
- **Original Location:** Root directory
- **Date Archived:** October 16, 2025
- **Last Modified:** July 3, 2025
- **Reason:** Basic PostgreSQL-only setup, superseded by more comprehensive configurations
- **Superseded By:** 
  - `docker-compose.dev.yml` - Local development (port 5434)
  - `docker-compose.uat.yml` - UAT environment
- **Issue:** Port 5432 conflicts with CI infrastructure

**Original Purpose:** Simple development database setup

---

### `docker-compose.ci.yml.legacy`
- **Original Location:** Root directory
- **Date Archived:** October 16, 2025
- **Reason:** Duplicate functionality of `docker-compose.ci-infrastructure.yml` (which is actively running)
- **Status:** Not referenced in GitHub workflows
- **Note:** Almost identical to the active CI infrastructure configuration

**Original Purpose:** CI/CD testing services (PostgreSQL + Redis)

---

## ✅ Active Docker Compose Files (in root)

These files are currently in use and should NOT be archived:

| File | Purpose | Status |
|------|---------|--------|
| `docker-compose.uat.yml` | UAT environment deployment | ✅ Used by CI/CD workflow |
| `docker-compose.uat-monitoring.yml` | UAT monitoring stack (Prometheus, Grafana) | ✅ Active monitoring |
| `docker-compose.runners.yml` | GitHub self-hosted runners | ✅ 3 runners running |
| `docker-compose.ci-infrastructure.yml` | CI database services | ✅ PostgreSQL + Redis running 8+ days |
| `docker-compose.dev.yml` | Local development environment | ✅ Used by developers |

---

## 🔄 Migration Notes

If you need to restore or reference these files:

```bash
# View file content
cat docs/archives/docker-compose/docker-compose.yml.legacy

# Restore to root (if needed)
git mv docs/archives/docker-compose/docker-compose.yml.legacy docker-compose.yml

# Or access via git history
git log --all --full-history -- "**/docker-compose.yml"
```

---

## 📊 Running Infrastructure Status

**Confirmed Running Containers (October 16, 2025):**
```
postgres-ci-familycart     Up 8 days (healthy)   0.0.0.0:5432->5432/tcp
redis-ci-familycart        Up 8 days (healthy)   0.0.0.0:6379->6379/tcp
familycart-runner-1        Up 8 days (healthy)
familycart-runner-2        Up 8 days (healthy)
familycart-runner-3        Up 8 days (healthy)
```

These are managed by `docker-compose.ci-infrastructure.yml` and `docker-compose.runners.yml`.
