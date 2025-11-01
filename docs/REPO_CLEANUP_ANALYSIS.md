# FamilyCart Repository Cleanup Analysis
**Date:** October 16, 2025  
**Status:** Recommendations for root directory organization

## 🎯 Executive Summary

The repository root contains **60+ files** (42 MD docs, 7 docker-compose files, 9 scripts, and various config files) that need organization. This analysis categorizes them by purpose and recommends a cleanup strategy.

---

## 📊 Current State Analysis

### File Categories Identified

#### 1. **Documentation Files (42 MD files)**
- **Active Project Docs (Keep in Root):** 5 files
- **CI/CD Documentation:** 13 files
- **Deployment Guides:** 8 files
- **Sprint Summaries & Archives:** 10 files
- **Temporary/Test Files:** 6 files

#### 2. **Docker Compose Files (7 files)**
- **Active UAT Environment:** 2 files
- **CI/CD Infrastructure:** 3 files
- **Development/Legacy:** 2 files

#### 3. **Scripts (9 files)**
- **Active Operational Scripts:** 2 files
- **Test/Debug Scripts:** 5 files
- **Legacy Scripts:** 2 files

#### 4. **Configuration Files**
- `requirements.txt` - **UNUSED** (Poetry 2.x is used)
- `alembic.ini` - Active (database migrations)
- `nginx-uat-extended.conf` - Legacy config
- Various test files

---

## 📁 Detailed File Categorization

### A. Keep in Root (Essential Active Files)

#### Documentation (5 files)
1. ✅ `README.md` - Main project documentation
2. ✅ `TASKS.md` - Current active tasks
3. ✅ `USER_STORIES.md` - Feature requirements
4. ✅ `PLANNING.md` - Project planning
5. ✅ `global_rules.md` - Development guidelines

#### Docker Compose (3 files)
1. ✅ `docker-compose.uat.yml` - **ACTIVE UAT** (hosted on this machine via Cloudflare)
2. ✅ `docker-compose.uat-monitoring.yml` - **ACTIVE UAT monitoring** (should stay on this machine)
3. ✅ `docker-compose.runners.yml` - **ACTIVE GitHub runners** (on this machine)

#### Configuration (1 file)
1. ✅ `alembic.ini` - Database migration config (backend also has its own)

#### Scripts (0 - all should move)

---

### B. Move to `docs/` Directory

#### Active Deployment Documentation (8 files) → `docs/deployment/`
1. `DEPLOY_SELF_HOSTED_UAT.md` ⭐ (747 lines - comprehensive UAT guide)
2. `DEPLOY_OCI_FREE_TIER.md` (326 lines - production planning)
3. `CLOUDFLARE_MONITORING_SETUP.md`
4. `cloudflare-access-config.md`
5. `ENVIRONMENT_CONFIG.md`
6. `DOCKER_COMPOSE_V2_REFERENCE.md`
7. `docker_installation_ubuntu.md`
8. `NGINX_SEPARATION_PROPOSAL.md` (544 lines - architectural doc)

#### GitHub Setup Guides (3 files) → `docs/github/`
1. `GITHUB_ENVIRONMENTS_SETUP.md`
2. `GITHUB_TOKEN_STEPS.md`
3. `create-github-token-guide.md`
4. `setup-github-mcp-server.md`

#### Development Workflow (1 file) → `docs/development/`
1. `DEVELOPMENT_WORKFLOW_PROPOSAL.md` (372 lines - important architecture doc)

#### Feature Documentation (2 files) → `docs/features/`
1. `QUANTITY_UNITS_IMPLEMENTATION.md` (447 lines)
2. `HOME_ASSISTANT_CONFIG_UPDATE.md`

---

### C. Move to `docs/archives/` (Historical/Completed)

#### Completed Sprint Summaries (10 files)
1. `WEEK_1_WORKFLOW_SETUP_SUMMARY.md`
2. `SPRINT_7_LIST_RENAME_SUMMARY.md`
3. `CREATE_LIST_UI_SUMMARY.md`
4. `LIVE_UPDATES_UI_SUMMARY.md`
5. `RENAME_FIX_SUMMARY.md`
6. `PR_CHECK_FIX_SUMMARY.md`
7. `FRONTEND_ESLINT_FIX_SUMMARY.md`
8. `GITHUB_WORKFLOW_FIX_SUMMARY.md`
9. `AUTH_FIX.md`
10. `UAT_SYNC_COMPLETE.md`

#### Completed CI/CD Documentation (5 files)
1. `CI_INFRASTRUCTURE_COMPLETE.md`
2. `CI_QUALITY_STANDARDS.md`
3. `UAT_MONITORING_SUMMARY.md`
4. `WORKFLOW_TEST_RESULTS.md`

---

### D. Move to `docs/archives/test-reports/` (Temporary Test Files)

These are one-off test verification files that should be archived:

1. `CICD_TEST.md` (1 line - test timestamp)
2. `CI_DEBUG_TEST.md`
3. `CI_INFRASTRUCTURE_TEST.md`
4. `CI_RUNNER_FIX_TEST.md`
5. `CI_RUNNER_FIX_VERIFICATION.md`
6. `CI_RUNNER_TEST.md` (3 test timestamps)
7. `RUNNER_FIXES_TEST.md`

---

### E. Move to `scripts/` Directory

#### Active Operational Scripts (2 files)
1. `push-docker-images.sh` - Used for container registry operations
2. `update-github-token.sh` - GitHub runner maintenance

#### UAT Infrastructure Scripts (2 files) → `scripts/uat/`
1. `setup-cloudflare-monitoring.sh`
2. `test-uat-nginx.sh`

#### Test/Debug Scripts (5 files) → `scripts/testing/` or DELETE
1. `debug_redis_config.py` - One-off debug script
2. `test_ci_infrastructure.py` - CI testing
3. `test_runner_stability.py` - Runner testing
4. `test_websocket_playwright.py` - WebSocket testing
5. `simple-nginx-test.sh` - Nginx testing

**Recommendation:** Move to `scripts/testing/` or consider deleting if tests are now in proper test suites.

---

### F. Archive or Delete

#### Obsolete Task Files (2 files) → DELETE or `docs/archives/`
1. `TASKS_OLD.md` (1,706 lines - superseded by TASKS.md)
2. `TASKS_NEW.md` (235 lines - merged into TASKS.md?)

**Recommendation:** If content is already in `TASKS.md`, delete these files.

#### Docker Compose Files to Archive/Delete (4 files)

1. `docker-compose.yml` - **Legacy** (last modified Jul 3, basic dev setup)
   - **Action:** Move to `docs/archives/docker-compose/` or DELETE
   
2. `docker-compose.dev.yml` - **Development environment**
   - **Status:** If still used by developers, keep it
   - **Action:** Keep in root OR move to `docker/` subdirectory
   
3. `docker-compose.ci.yml` - **CI testing infrastructure**
   - **Status:** Used by GitHub runners?
   - **Action:** If unused, move to `docs/archives/docker-compose/`
   
4. `docker-compose.ci-infrastructure.yml` - **CI infrastructure setup**
   - **Status:** Check if still needed for runners
   - **Action:** If unused, move to `docs/archives/docker-compose/`

#### Obsolete Configuration (2 files) → DELETE
1. ❌ `requirements.txt` - **NOT USED** (Poetry 2.x in `backend/pyproject.toml`)
   - Backend uses Poetry with `backend/pyproject.toml` and `backend/poetry.lock`
   - This file is outdated (last modified Jun 27) with old versions
   - **Action:** DELETE immediately
   
2. ❌ `nginx-uat-extended.conf` - Duplicate/obsolete nginx config
   - Proper configs are in `nginx/` and `deploy/nginx/` directories
   - **Action:** DELETE or move to archives

#### Test Result Files (1 file)
1. `test_runner_improvements.txt` - **Action:** Move to `docs/archives/test-reports/`

---

## 🎨 Proposed Directory Structure

```
FamilyCart/
├── README.md                          # Keep - main docs
├── TASKS.md                           # Keep - active tasks
├── USER_STORIES.md                    # Keep - requirements
├── PLANNING.md                        # Keep - project planning
├── global_rules.md                    # Keep - dev guidelines
├── alembic.ini                        # Keep - DB migrations
│
├── docker-compose.uat.yml             # Keep - ACTIVE UAT
├── docker-compose.uat-monitoring.yml  # Keep - ACTIVE monitoring
├── docker-compose.runners.yml         # Keep - ACTIVE runners
├── docker-compose.dev.yml             # Keep - if used by devs
│
├── backend/                           # Existing - unchanged
├── frontend/                          # Existing - unchanged
├── deploy/                            # Existing - unchanged
├── monitoring/                        # Existing - unchanged
├── nginx/                             # Existing - unchanged
│
├── docs/                              # Enhanced structure
│   ├── deployment/                    # NEW - deployment guides
│   │   ├── DEPLOY_SELF_HOSTED_UAT.md
│   │   ├── DEPLOY_OCI_FREE_TIER.md
│   │   ├── CLOUDFLARE_MONITORING_SETUP.md
│   │   ├── cloudflare-access-config.md
│   │   ├── ENVIRONMENT_CONFIG.md
│   │   ├── DOCKER_COMPOSE_V2_REFERENCE.md
│   │   ├── docker_installation_ubuntu.md
│   │   └── NGINX_SEPARATION_PROPOSAL.md
│   │
│   ├── github/                        # NEW - GitHub setup
│   │   ├── GITHUB_ENVIRONMENTS_SETUP.md
│   │   ├── GITHUB_TOKEN_STEPS.md
│   │   ├── create-github-token-guide.md
│   │   └── setup-github-mcp-server.md
│   │
│   ├── development/                   # NEW - dev workflow
│   │   └── DEVELOPMENT_WORKFLOW_PROPOSAL.md
│   │
│   ├── features/                      # NEW - feature specs
│   │   ├── QUANTITY_UNITS_IMPLEMENTATION.md
│   │   └── HOME_ASSISTANT_CONFIG_UPDATE.md
│   │
│   ├── archives/                      # NEW - historical docs
│   │   ├── sprints/                   # Sprint summaries
│   │   │   ├── WEEK_1_WORKFLOW_SETUP_SUMMARY.md
│   │   │   ├── SPRINT_7_LIST_RENAME_SUMMARY.md
│   │   │   ├── CREATE_LIST_UI_SUMMARY.md
│   │   │   ├── LIVE_UPDATES_UI_SUMMARY.md
│   │   │   └── ...
│   │   │
│   │   ├── fixes/                     # Completed fixes
│   │   │   ├── AUTH_FIX.md
│   │   │   ├── RENAME_FIX_SUMMARY.md
│   │   │   ├── PR_CHECK_FIX_SUMMARY.md
│   │   │   ├── FRONTEND_ESLINT_FIX_SUMMARY.md
│   │   │   └── GITHUB_WORKFLOW_FIX_SUMMARY.md
│   │   │
│   │   ├── ci-cd/                     # CI/CD completion docs
│   │   │   ├── CI_INFRASTRUCTURE_COMPLETE.md
│   │   │   ├── CI_QUALITY_STANDARDS.md
│   │   │   ├── UAT_MONITORING_SUMMARY.md
│   │   │   ├── UAT_SYNC_COMPLETE.md
│   │   │   └── WORKFLOW_TEST_RESULTS.md
│   │   │
│   │   ├── test-reports/              # Test verification files
│   │   │   ├── CICD_TEST.md
│   │   │   ├── CI_DEBUG_TEST.md
│   │   │   ├── CI_INFRASTRUCTURE_TEST.md
│   │   │   ├── CI_RUNNER_TEST.md
│   │   │   ├── RUNNER_FIXES_TEST.md
│   │   │   └── test_runner_improvements.txt
│   │   │
│   │   └── docker-compose/            # Old compose files
│   │       ├── docker-compose.yml.old
│   │       ├── docker-compose.ci.yml.old
│   │       └── docker-compose.ci-infrastructure.yml.old
│   │
│   └── [existing docs files...]       # ai-caching-analysis.md, etc.
│
├── scripts/                           # Enhanced structure
│   ├── push-docker-images.sh         # From root
│   ├── update-github-token.sh         # From root
│   ├── uat/                           # NEW - UAT operations
│   │   ├── setup-cloudflare-monitoring.sh
│   │   └── test-uat-nginx.sh
│   ├── testing/                       # NEW - test scripts
│   │   ├── debug_redis_config.py
│   │   ├── test_ci_infrastructure.py
│   │   ├── test_runner_stability.py
│   │   ├── test_websocket_playwright.py
│   │   └── simple-nginx-test.sh
│   └── [existing scripts...]          # ci-management.sh, etc.
│
└── sprints/                           # Existing - unchanged
    └── [sprint reports...]
```

---

## 🚀 Reorganization Plan

### Phase 1: Create New Directory Structure
```bash
mkdir -p docs/deployment
mkdir -p docs/github
mkdir -p docs/development
mkdir -p docs/features
mkdir -p docs/archives/sprints
mkdir -p docs/archives/fixes
mkdir -p docs/archives/ci-cd
mkdir -p docs/archives/test-reports
mkdir -p docs/archives/docker-compose
mkdir -p scripts/uat
mkdir -p scripts/testing
```

### Phase 2: Move Documentation Files

#### Deployment Docs
```bash
git mv DEPLOY_SELF_HOSTED_UAT.md docs/deployment/
git mv DEPLOY_OCI_FREE_TIER.md docs/deployment/
git mv CLOUDFLARE_MONITORING_SETUP.md docs/deployment/
git mv cloudflare-access-config.md docs/deployment/
git mv ENVIRONMENT_CONFIG.md docs/deployment/
git mv DOCKER_COMPOSE_V2_REFERENCE.md docs/deployment/
git mv docker_installation_ubuntu.md docs/deployment/
git mv NGINX_SEPARATION_PROPOSAL.md docs/deployment/
```

#### GitHub Setup Docs
```bash
git mv GITHUB_ENVIRONMENTS_SETUP.md docs/github/
git mv GITHUB_TOKEN_STEPS.md docs/github/
git mv create-github-token-guide.md docs/github/
git mv setup-github-mcp-server.md docs/github/
```

#### Development Docs
```bash
git mv DEVELOPMENT_WORKFLOW_PROPOSAL.md docs/development/
```

#### Feature Docs
```bash
git mv QUANTITY_UNITS_IMPLEMENTATION.md docs/features/
git mv HOME_ASSISTANT_CONFIG_UPDATE.md docs/features/
```

#### Sprint Archives
```bash
git mv WEEK_1_WORKFLOW_SETUP_SUMMARY.md docs/archives/sprints/
git mv SPRINT_7_LIST_RENAME_SUMMARY.md docs/archives/sprints/
git mv CREATE_LIST_UI_SUMMARY.md docs/archives/sprints/
git mv LIVE_UPDATES_UI_SUMMARY.md docs/archives/sprints/
```

#### Fix Archives
```bash
git mv AUTH_FIX.md docs/archives/fixes/
git mv RENAME_FIX_SUMMARY.md docs/archives/fixes/
git mv PR_CHECK_FIX_SUMMARY.md docs/archives/fixes/
git mv FRONTEND_ESLINT_FIX_SUMMARY.md docs/archives/fixes/
git mv GITHUB_WORKFLOW_FIX_SUMMARY.md docs/archives/fixes/
```

#### CI/CD Archives
```bash
git mv CI_INFRASTRUCTURE_COMPLETE.md docs/archives/ci-cd/
git mv CI_QUALITY_STANDARDS.md docs/archives/ci-cd/
git mv UAT_MONITORING_SUMMARY.md docs/archives/ci-cd/
git mv UAT_SYNC_COMPLETE.md docs/archives/ci-cd/
git mv WORKFLOW_TEST_RESULTS.md docs/archives/ci-cd/
```

#### Test Report Archives
```bash
git mv CICD_TEST.md docs/archives/test-reports/
git mv CI_DEBUG_TEST.md docs/archives/test-reports/
git mv CI_INFRASTRUCTURE_TEST.md docs/archives/test-reports/
git mv CI_RUNNER_FIX_TEST.md docs/archives/test-reports/
git mv CI_RUNNER_FIX_VERIFICATION.md docs/archives/test-reports/
git mv CI_RUNNER_TEST.md docs/archives/test-reports/
git mv RUNNER_FIXES_TEST.md docs/archives/test-reports/
git mv test_runner_improvements.txt docs/archives/test-reports/
```

### Phase 3: Move Scripts
```bash
git mv push-docker-images.sh scripts/
git mv update-github-token.sh scripts/
git mv setup-cloudflare-monitoring.sh scripts/uat/
git mv test-uat-nginx.sh scripts/uat/
git mv debug_redis_config.py scripts/testing/
git mv test_ci_infrastructure.py scripts/testing/
git mv test_runner_stability.py scripts/testing/
git mv test_websocket_playwright.py scripts/testing/
git mv simple-nginx-test.sh scripts/testing/
```

### Phase 4: Handle Docker Compose Files

**Evaluate first, then decide:**
```bash
# Check if these are still referenced in CI/CD
grep -r "docker-compose.ci" .github/workflows/
grep -r "docker-compose.yml" .github/workflows/

# If not used:
git mv docker-compose.yml docs/archives/docker-compose/docker-compose.yml.old
git mv docker-compose.ci.yml docs/archives/docker-compose/docker-compose.ci.yml.old
git mv docker-compose.ci-infrastructure.yml docs/archives/docker-compose/docker-compose.ci-infrastructure.yml.old

# If docker-compose.dev.yml is used, keep it or move to docker/ subdirectory
```

### Phase 5: Delete Obsolete Files
```bash
# After confirming content is preserved elsewhere:
git rm requirements.txt
git rm nginx-uat-extended.conf
git rm TASKS_OLD.md
git rm TASKS_NEW.md
```

### Phase 6: Update References

Create a script to update documentation references:
```bash
# Find all markdown files with references to moved files
find . -name "*.md" -exec grep -l "DEPLOY_SELF_HOSTED_UAT.md" {} \;

# Update references systematically
# Example: DEPLOY_SELF_HOSTED_UAT.md -> docs/deployment/DEPLOY_SELF_HOSTED_UAT.md
```

---

## 🎯 Priority Actions

### Immediate (Do First)
1. ✅ **DELETE `requirements.txt`** - Confirmed unused, Poetry 2.x is the standard
2. ✅ **DELETE `nginx-uat-extended.conf`** - Duplicate config
3. ✅ Create archive directories
4. ✅ Move test report files (low risk)

### High Priority (This Week)
1. Move deployment documentation to `docs/deployment/`
2. Move sprint summaries to `docs/archives/sprints/`
3. Move scripts to `scripts/` subdirectories
4. Archive obsolete task files

### Medium Priority (Next Sprint)
1. Evaluate and archive unused docker-compose files
2. Update documentation cross-references
3. Create index files in new directories

### Low Priority (Future)
1. Consider consolidating `nginx/` and `deploy/nginx/` directories
2. Evaluate `monitoring/` vs root monitoring files
3. Review `sprints/` directory organization

---

## 📋 Verification Checklist

After reorganization, verify:

- [ ] UAT environment still deploys correctly (`docker-compose.uat.yml`)
- [ ] UAT monitoring works (`docker-compose.uat-monitoring.yml`)
- [ ] GitHub runners function properly (`docker-compose.runners.yml`)
- [ ] Scripts in `scripts/` are executable
- [ ] Documentation links are updated
- [ ] GitHub Actions workflows still reference correct files
- [ ] Developer onboarding docs point to new locations

---

## 🔍 Analysis of Existing Directories

### `/deploy/` - Well Organized ✅
- Contains deployment scripts, nginx configs, GitHub runner setup
- Has proper README.md
- Subdirectories: `nginx/`, `monitoring/`, `github-runners/`, `scripts/`
- **Recommendation:** Keep as-is

### `/nginx/` - Potential Duplicate ⚠️
- Contains similar nginx configs as `deploy/nginx/`
- **Question:** Is this used for local development or UAT?
- **Recommendation:** 
  - If identical to `deploy/nginx/`, consolidate
  - If for different purposes, document the difference
  - NGINX_SEPARATION_PROPOSAL.md mentions nginx is in a separate repo on this machine

### `/monitoring/` - Similar to `deploy/monitoring/` ⚠️
- Contains Prometheus, Grafana, Alertmanager configs
- Has its own docker-compose.monitoring.yml
- **Recommendation:**
  - Clarify if root `/monitoring/` is for UAT (on this machine)
  - `deploy/monitoring/` might be for production deployment templates
  - Keep root `/monitoring/` for active UAT monitoring

### `/scripts/` - Good Structure ✅
- Contains CI/CD management scripts
- Well organized with clear purpose
- **Recommendation:** Add root scripts here

### `/docs/` - Needs Reorganization ⚠️
- Currently focused on AI, design, and technical docs
- Missing deployment and CI/CD sections
- **Recommendation:** Add new subdirectories as proposed

### `/sprints/` - Good Archive ✅
- Contains historical sprint reports
- **Recommendation:** Keep as-is, move newer summaries here

---

## 💡 Key Findings

### ✅ Confirmed Unused
- **`requirements.txt`** - Backend uses Poetry 2.x (`backend/pyproject.toml`)
- Test timestamp files (CICD_TEST.md, etc.)

### ⚠️ Needs Clarification
- **`docker-compose.ci.yml`** - Still used by GitHub runners?
- **`docker-compose.ci-infrastructure.yml`** - Still needed?
- **`docker-compose.yml`** - Legacy development file?
- **Root `/nginx/` vs `/deploy/nginx/`** - Separate repo mentioned in proposal
- **Root `/monitoring/` vs `/deploy/monitoring/`** - UAT vs deployment templates?

### ✅ Active Infrastructure (On This Machine)
- **UAT Environment:** `docker-compose.uat.yml`
- **UAT Monitoring:** `docker-compose.uat-monitoring.yml`, `/monitoring/` directory
- **GitHub Runners:** `docker-compose.runners.yml`, `/deploy/github-runners/`
- **Nginx Proxy:** Separate repo (per NGINX_SEPARATION_PROPOSAL.md)

### 🎯 Production Status
- **Production does not exist yet** (per your note)
- `DEPLOY_OCI_FREE_TIER.md` contains production planning

---

## 📝 Recommended Next Steps

1. **Review this analysis** with your team/stakeholders
2. **Answer clarification questions** about docker-compose files
3. **Execute Phase 1** (immediate deletions and archive creation)
4. **Execute Phase 2** (documentation moves) - low risk
5. **Test after each phase** to ensure UAT/CI/CD still works
6. **Update README.md** to reflect new structure
7. **Create index files** in new `docs/` subdirectories

---

## 🎉 Expected Benefits

- **Cleaner root directory** - Only 8-10 essential files
- **Better organization** - Logical grouping by purpose
- **Easier onboarding** - Clear navigation for new developers
- **Reduced confusion** - Archive old/completed work
- **Improved maintenance** - Clear separation of active vs historical

---

**Next Action:** Would you like me to execute the reorganization plan, or would you prefer to review and approve specific phases first?
