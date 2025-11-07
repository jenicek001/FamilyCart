# 🗑️ File Deletion Confirmation Required

**Date:** October 16, 2025  
**Purpose:** Review and approve files for deletion before cleanup

---

## ✅ CONFIRMED SAFE TO DELETE

### 1. `requirements.txt` - **RECOMMENDATION: DELETE** ✅

**Reason:** Backend uses Poetry 2.x exclusively

**Evidence:**
- Backend has `pyproject.toml` and `poetry.lock` with all dependencies
- Last modified: June 27, 2025 (old, outdated versions)
- Contains outdated package versions (e.g., `fastapi==0.104.1` vs Poetry has `^0.115.14`)
- No references found in any Dockerfile or docker-compose files
- No GitHub workflow references
- Poetry is explicitly mentioned in development guidelines

**Current Content:** (31 lines with outdated packages)
```
fastapi==0.104.1        # Poetry has: ^0.115.14
uvicorn==0.24.0         # Poetry has: ^0.29.0
sqlalchemy==2.0.23      # Poetry has: ^2.0.30
pydantic==2.4.2         # Poetry has: ^2.7.1
# ... etc
```

**Risk Level:** 🟢 ZERO RISK - Not used anywhere

**Your Decision:** 
- [ ] ✅ APPROVED - Delete immediately
- [ ] ⚠️  ARCHIVE - Move to `docs/archives/`
- [ ] ❌ KEEP - Keep in root (please explain why)

---

### 2. `nginx-uat-extended.conf` - **RECOMMENDATION: DELETE** ✅

**Reason:** Duplicate/obsolete nginx configuration

**Evidence:**
- Proper nginx configs exist in:
  - `nginx/uat.conf` (6,483 bytes)
  - `nginx/multi-service.conf` (15,728 bytes)
  - `deploy/nginx/uat.conf` (separate deployment config)
- This file appears to be a test/extended version
- Not referenced in any docker-compose files
- Not referenced in deployment scripts

**Current Content:** Standard nginx config with gzip, upstream definitions

**Alternative:** `nginx/uat.conf` is the active configuration

**Risk Level:** 🟡 LOW RISK - May be a backup/alternative config

**Your Decision:**
- [ ] ✅ APPROVED - Delete immediately
- [ ] ⚠️  ARCHIVE - Move to `docs/archives/nginx/`
- [ ] ❌ KEEP - Keep in root (please explain why)

---

## ⚠️ REQUIRES YOUR REVIEW

### 3. `TASKS_OLD.md` - **RECOMMENDATION: DELETE** ⚠️

**Size:** 1,706 lines (largest task file)

**Current Active File:** `TASKS.md` (897 lines) - Well organized with sprint overview

**Content Preview:**
```
# TASKS.md
## Purpose: Tracks current tasks, backlog, and sub-tasks
## Sprint 1: Backend Foundation & Authentication
* [x] Initialize FastAPI project with Poetry
* [x] User registration and login
... (massive list of completed tasks)
```

**Question:** Is this historical data you want to preserve?

**Options:**
- **DELETE:** If all relevant info is in current `TASKS.md`
- **ARCHIVE:** Move to `docs/archives/tasks/TASKS_OLD.md` for historical reference
- **KEEP:** If you still reference this file

**Your Decision:**
- [ ] ✅ APPROVED - Delete (content is in TASKS.md)
- [ ] ⚠️  ARCHIVE - Move to `docs/archives/tasks/`
- [ ] ❌ KEEP - Still needed (please explain why)

---

### 4. `TASKS_NEW.md` - **RECOMMENDATION: DELETE** ⚠️

**Size:** 235 lines

**Content Preview:**
```
# TASKS.md
## Purpose: Tracks current tasks, backlog, and sub-tasks
# Sprint Overview & Status
## Completed Sprints ✅
### Sprint 1: Backend Foundation & Authentication ✅ COMPLETED
### Sprint 2: Core Shopping List API ✅ COMPLETED
...
```

**Observation:** This looks like an intermediate version between `TASKS_OLD.md` and `TASKS.md`

**Question:** Was this merged into the current `TASKS.md`?

**Your Decision:**
- [ ] ✅ APPROVED - Delete (merged into TASKS.md)
- [ ] ⚠️  ARCHIVE - Move to `docs/archives/tasks/`
- [ ] ❌ KEEP - Still needed (please explain why)

---

## 📋 Summary of Deletions

| File | Size | Risk | Recommendation |
|------|------|------|----------------|
| `requirements.txt` | 31 lines | 🟢 ZERO | DELETE - Not used, Poetry only |
| `nginx-uat-extended.conf` | ~250 lines | 🟡 LOW | DELETE - Duplicate config |
| `TASKS_OLD.md` | 1,706 lines | 🟡 LOW | DELETE or ARCHIVE |
| `TASKS_NEW.md` | 235 lines | 🟡 LOW | DELETE or ARCHIVE |
| `docker-compose.yml` | ~40 lines | 🟡 LOW | ARCHIVE - Superseded by dev.yml/uat.yml |
| `docker-compose.ci.yml` | ~80 lines | 🟡 LOW | ARCHIVE - Duplicate of ci-infrastructure.yml |

**Total Files to Clean:** 6 files (~2,300 lines of obsolete configuration/documentation)

---

## 🎯 Recommended Actions

### Phase 1: Immediate Deletions (Zero Risk)
```bash
# These are confirmed unused
git rm requirements.txt
git commit -m "chore: remove unused requirements.txt (Poetry 2.x is used)"
```

### Phase 2: After Your Confirmation - Simple Deletions
```bash
# If approved for deletion
git rm nginx-uat-extended.conf
git rm TASKS_OLD.md
git rm TASKS_NEW.md
git commit -m "chore: remove obsolete configuration and task files"
```

### Phase 3: Archive Docker Compose Files (Recommended)
```bash
# Archive obsolete/duplicate docker-compose files
mkdir -p docs/archives/docker-compose
git mv docker-compose.yml docs/archives/docker-compose/docker-compose.yml.legacy
git mv docker-compose.ci.yml docs/archives/docker-compose/docker-compose.ci.yml.legacy
git commit -m "chore: archive legacy docker-compose files"

# Add README to explain what files were archived and why
cat > docs/archives/docker-compose/README.md << 'EOF'
# Archived Docker Compose Files

## Files in this directory:

### docker-compose.yml.legacy
- **Date Archived:** October 16, 2025
- **Reason:** Basic PostgreSQL setup, superseded by docker-compose.dev.yml and docker-compose.uat.yml
- **Last Modified:** July 3, 2025
- **Note:** Port 5432 conflicts with ci-infrastructure setup

### docker-compose.ci.yml.legacy
- **Date Archived:** October 16, 2025
- **Reason:** Duplicate functionality of docker-compose.ci-infrastructure.yml (which is actively running)
- **Note:** Not referenced in GitHub workflows

## Active Docker Compose Files (in root):
- `docker-compose.uat.yml` - UAT environment (used by CI/CD)
- `docker-compose.uat-monitoring.yml` - UAT monitoring stack
- `docker-compose.runners.yml` - GitHub self-hosted runners (3 active runners)
- `docker-compose.ci-infrastructure.yml` - CI database services (PostgreSQL + Redis)
- `docker-compose.dev.yml` - Local development environment
EOF

git add docs/archives/docker-compose/README.md
git commit -m "docs: add explanation for archived docker-compose files"
```

### Alternative - Complete Deletion (If you don't need history)
```bash
# If you want to permanently delete instead of archiving
git rm requirements.txt nginx-uat-extended.conf TASKS_OLD.md TASKS_NEW.md
git rm docker-compose.yml docker-compose.ci.yml
git commit -m "chore: remove obsolete configuration files

- requirements.txt: Poetry 2.x is used instead
- nginx-uat-extended.conf: Duplicate configuration
- TASKS_OLD.md, TASKS_NEW.md: Superseded by TASKS.md
- docker-compose.yml: Superseded by dev.yml/uat.yml
- docker-compose.ci.yml: Duplicate of ci-infrastructure.yml"
```

### Phase 4: Archive Task Files (If Keeping History)
```bash
# If you want to preserve task history
mkdir -p docs/archives/tasks
git mv TASKS_OLD.md docs/archives/tasks/
git mv TASKS_NEW.md docs/archives/tasks/
git commit -m "chore: archive historical task files"
```

### Phase 5: Archive Nginx Config (If Keeping History)
```bash
# If you want to preserve nginx config
mkdir -p docs/archives/nginx
git mv nginx-uat-extended.conf docs/archives/nginx/
git commit -m "chore: archive extended nginx configuration"
```

---

## 📊 Additional Files Analysis (Not for Deletion)

### Docker Compose Files - Status Confirmed ✅

After reviewing GitHub workflows, running containers, and file contents:

| File | Status | Usage | Keep? |
|------|--------|-------|-------|
| `docker-compose.uat.yml` | ✅ ACTIVE | UAT deployment via CI/CD workflow | ✅ KEEP |
| `docker-compose.uat-monitoring.yml` | ✅ ACTIVE | UAT monitoring stack | ✅ KEEP |
| `docker-compose.runners.yml` | ✅ ACTIVE | GitHub runners (3 running for 8 days) | ✅ KEEP |
| `docker-compose.ci-infrastructure.yml` | ✅ ACTIVE | CI PostgreSQL + Redis (running for 8 days) | ✅ KEEP |
| `docker-compose.ci.yml` | 🟡 SIMILAR | Almost identical to ci-infrastructure.yml | ⚠️ EVALUATE |
| `docker-compose.dev.yml` | 🟢 DEV | Local development (ports 5434, 6381) | ✅ KEEP |
| `docker-compose.yml` | 🟡 BASIC | Basic PostgreSQL setup (port 5432) | ⚠️ EVALUATE |

**Analysis:**

1. **`docker-compose.ci.yml`** - Provides PostgreSQL (5432) + Redis for CI/CD
   - NOT referenced in GitHub workflows ❌
   - Almost identical to `docker-compose.ci-infrastructure.yml` which IS running
   - **Recommendation:** Archive or delete (duplicate functionality)

2. **`docker-compose.dev.yml`** - Local development environment
   - PostgreSQL on port 5434 (avoids conflict with CI on 5432)
   - Redis on port 6381 (avoids conflict)
   - Uses `.env.dev` file
   - **Recommendation:** KEEP - useful for local development

3. **`docker-compose.yml`** - Simple PostgreSQL setup
   - Last modified: July 3, 2025 (old)
   - Basic setup, no Redis
   - Port 5432 (conflicts with CI infrastructure)
   - **Recommendation:** Archive or delete (superseded by dev.yml and uat.yml)

**Running Containers Confirmed:**
```
postgres-ci-familycart     Up 8 days (healthy)   0.0.0.0:5432->5432/tcp
redis-ci-familycart        Up 8 days (healthy)   0.0.0.0:6379->6379/tcp
familycart-runner-1        Up 8 days (healthy)
familycart-runner-2        Up 8 days (healthy)
familycart-runner-3        Up 8 days (healthy)
```

**Recommendation:** 
- ✅ KEEP: `uat.yml`, `uat-monitoring.yml`, `runners.yml`, `ci-infrastructure.yml`, `dev.yml`
- ⚠️ ARCHIVE: `ci.yml` and `docker-compose.yml` (move to `docs/archives/docker-compose/`)

---

## 🔄 Next Steps After Approval

1. **You review this document** and mark your decisions above
2. **I execute approved deletions** with proper git commits
3. **We proceed to Phase 2:** Documentation reorganization (moving files to docs/ subdirectories)
4. **Phase 3:** Script reorganization
5. **Phase 4:** Create proper README updates and index files

---

## ❓ Questions for You

1. **TASKS files:** Do you want to preserve historical TASKS_OLD.md and TASKS_NEW.md in archives, or completely delete them?

2. **nginx-uat-extended.conf:** Is this a backup you might need, or safe to delete?

3. **Docker Compose files:** Should I investigate `docker-compose.yml`, `docker-compose.ci.yml`, and `docker-compose.dev.yml` usage before deciding on them?

4. **Execution timing:** Do you want me to:
   - Execute deletions immediately after your approval?
   - Create a script for you to review and run manually?
   - Do one file at a time with confirmation?

---

**Please review and respond with your decisions. I'll wait for your approval before deleting anything!** 🛡️
