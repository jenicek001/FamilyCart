# CI/CD Pipeline Analysis - UAT Deployment Issue

**Date:** November 7, 2025  
**Issue:** UAT is not automatically deployed after successful branch protection pass

---

## 🔍 Current CI/CD Architecture

### Workflow Files

1. **`.github/workflows/branch-protection.yml`**
   - **Triggers:** 
     - Pull requests to `main` and `develop`
     - Direct pushes to `develop`, `feature/*`, `hotfix/*`, `bugfix/*`, `chore/*`, `docs/*`, `release/*`
   - **Purpose:** Enforce code quality standards before merge
   - **Jobs:**
     - validate-branch-name
     - code-quality (linting, formatting, type checking)
     - security-scan (Trivy)
     - architecture-compliance
     - pr-size-check
     - status-check

2. **`.github/workflows/ci.yml`**
   - **Triggers:**
     - Pushes to `main` and `develop`
     - Pull requests to `main`
   - **Purpose:** Build, test, and deploy application
   - **Jobs:**
     - test
     - security-scan
     - build
     - **deploy-uat** (conditional)
     - deploy-production (conditional)
     - performance-test
     - cleanup

---

## 🎯 The Problem: UAT Deployment Flow

### Expected Flow (Ideal)
```
1. Create feature branch (feature/xyz)
   ↓
2. Push to feature branch
   ↓
3. branch-protection.yml runs (validates code quality)
   ↓
4. Create PR to develop
   ↓
5. branch-protection.yml runs on PR
   ↓
6. PR passes all checks ✅
   ↓
7. Merge PR to develop
   ↓
8. Push event to develop triggers ci.yml
   ↓
9. ci.yml runs: test → security-scan → build → deploy-uat ✅
```

### Current Flow (What's Happening)
```
1. Create feature branch
   ↓
2. Push to feature branch
   ↓
3. branch-protection.yml runs ✅
   ↓
4. Create PR to develop
   ↓
5. branch-protection.yml runs ✅
   ↓
6. PR merges to develop ✅
   ↓
7. ci.yml triggers on push to develop ✅
   ↓
8. deploy-uat job condition check:
   `if: github.ref == 'refs/heads/develop'` ✅
   ↓
9. UAT deployment should run...
   ❓ BUT DOES IT? ❓
```

---

## 🔎 Root Cause Analysis

### Why UAT Might Not Deploy Automatically

#### Issue #1: GitHub Environment Not Configured
**Impact:** HIGH  
**Probability:** HIGH

The `deploy-uat` job has:
```yaml
environment: uat
```

This requires a GitHub Environment named `uat` to exist. If not configured:
- Job will fail or skip silently
- Secrets won't be available
- Deployment won't proceed

**Check:**
- Go to GitHub repo → Settings → Environments
- Verify `uat` environment exists
- Check if secrets are configured (UAT_HOST, UAT_USER, UAT_SSH_KEY)

#### Issue #2: Missing Required Secrets
**Impact:** HIGH  
**Probability:** MEDIUM

The workflow expects these secrets:
```yaml
UAT_HOST: ${{ secrets.UAT_HOST }}
UAT_USER: ${{ secrets.UAT_USER }}
UAT_SSH_KEY: ${{ secrets.UAT_SSH_KEY }}
```

**Current Behavior:**
- If secrets are missing, deployment defaults to **local deployment** on self-hosted runner
- This might work but won't deploy to a remote UAT server

**Check:**
- GitHub repo → Settings → Environments → uat → Secrets
- Verify if secrets are set

#### Issue #3: Job Dependencies
**Impact:** MEDIUM  
**Probability:** LOW

The `deploy-uat` job depends on:
```yaml
needs: build
```

If the `build` job fails or skips, `deploy-uat` won't run.

**Check Recent Workflow Runs:**
```bash
# Check if build job completes successfully
# GitHub Actions UI → Actions → CI/CD workflow runs
```

#### Issue #4: Self-Hosted Runner Issues
**Impact:** MEDIUM  
**Probability:** MEDIUM

UAT deployment runs on `self-hosted` runners. Issues:
- Runner might be offline
- Runner might lack permissions to access `/opt/familycart-uat/`
- Docker daemon issues on runner
- Network connectivity to UAT server

**Check:**
```bash
# On runner machine
docker ps --filter "name=familycart-runner"

# Check UAT directory
ls -la /opt/familycart-uat/

# Check runner logs
docker logs familycart-runner-1
```

---

## 🛠️ Solution Roadmap

### Phase 1: Immediate Diagnosis (5 minutes)

#### Step 1: Check GitHub Environment
```bash
# Go to GitHub UI
https://github.com/jenicek001/FamilyCart/settings/environments
```
**Action:** Verify `uat` environment exists

#### Step 2: Check Workflow Runs
```bash
# Go to GitHub Actions
https://github.com/jenicek001/FamilyCart/actions
```
**Action:** Find recent workflow runs for `develop` branch
- Click on a recent run
- Check if `deploy-uat` job appears
- Check job status: Success/Skipped/Failed
- Read error logs

#### Step 3: Check Secrets
```bash
# Go to Environment Secrets
https://github.com/jenicek001/FamilyCart/settings/environments/uat/secrets
```
**Action:** Verify secrets are configured (or note they're missing)

### Phase 2: Quick Fixes

#### Fix A: Create UAT Environment (If Missing)
1. Go to: Settings → Environments → New environment
2. Name: `uat`
3. Click "Configure environment"
4. Leave protection rules empty (for now)
5. Save

#### Fix B: Configure Secrets for Local UAT Deployment
Since the workflow supports local deployment, you can skip remote secrets:
```yaml
# These can be empty/missing for local deployment
# Deployment will run on self-hosted runner
```

The workflow checks:
```bash
if [ -z "$UAT_HOST" ]; then
  # Local UAT deployment (self-hosted runner)
  cd /opt/familycart-uat
  docker compose -f docker-compose.uat.yml up -d
fi
```

**Action:** Ensure `/opt/familycart-uat/` exists on runner machine:
```bash
# On self-hosted runner
sudo mkdir -p /opt/familycart-uat
sudo chown $(whoami):$(whoami) /opt/familycart-uat
cd /opt/familycart-uat
# Copy docker-compose.uat.yml here
```

#### Fix C: Add Health Check Defaults
The workflow uses default URLs for local deployment:
```yaml
UAT_BASE_URL: ${{ secrets.UAT_BASE_URL || 'http://localhost:3001' }}
UAT_API_URL: ${{ secrets.UAT_API_URL || 'http://localhost:8001' }}
```

This should work automatically.

### Phase 3: Verify Deployment

#### Test the Pipeline
1. Create a dummy change to trigger deployment:
```bash
cd /home/honzik/GitHub/FamilyCart/FamilyCart
git checkout develop
git pull origin develop

# Make a trivial change
echo "# UAT deployment test - $(date)" >> README.md
git add README.md
git commit -m "test: Trigger UAT deployment verification"
git push origin develop
```

2. Watch GitHub Actions:
```bash
# Go to: https://github.com/jenicek001/FamilyCart/actions
# Click on the running workflow
# Monitor deploy-uat job
```

3. Check UAT deployment status:
```bash
# On runner machine (if local deployment)
cd /opt/familycart-uat
docker compose ps

# Check logs
docker compose logs backend frontend
```

---

## 📊 Diagnostic Checklist

Use this checklist to systematically identify the issue:

### GitHub Configuration
- [ ] UAT environment exists in GitHub Settings
- [ ] UAT environment has no blocking protection rules
- [ ] Secrets are configured (or intentionally empty for local deployment)
- [ ] Self-hosted runners are active and healthy

### Workflow Configuration
- [ ] ci.yml triggers on push to develop: `branches: [main, develop]` ✅
- [ ] deploy-uat condition: `github.ref == 'refs/heads/develop'` ✅
- [ ] deploy-uat depends on `build` job ✅
- [ ] build job completes successfully

### Infrastructure
- [ ] Self-hosted runners are running
- [ ] Runners have Docker access
- [ ] `/opt/familycart-uat/` directory exists
- [ ] `docker-compose.uat.yml` exists in UAT directory
- [ ] Runner has network access (if remote deployment)

### Recent Workflow Runs
- [ ] ci.yml workflow triggered on recent develop push
- [ ] test job passed
- [ ] security-scan job passed
- [ ] build job passed
- [ ] deploy-uat job appears in workflow
- [ ] deploy-uat job status (Check logs)

---

## 🔧 Recommended Actions (Prioritized)

### Priority 1: Create UAT Environment (5 minutes)
**If environment doesn't exist:**
```
1. GitHub → Settings → Environments → New environment
2. Name: "uat"
3. Save (no protection rules needed)
```

### Priority 2: Verify Self-Hosted Runner Setup (10 minutes)
**On runner machine:**
```bash
# Check runners are active
docker ps --filter "name=familycart-runner"

# Check runner logs for errors
docker logs familycart-runner-1 | grep -i error

# Verify UAT directory
sudo mkdir -p /opt/familycart-uat
sudo chown $(whoami):$(whoami) /opt/familycart-uat

# Copy UAT docker-compose file
cp /home/honzik/GitHub/FamilyCart/FamilyCart/docker-compose.uat.yml /opt/familycart-uat/
```

### Priority 3: Test Deployment Manually (15 minutes)
**Trigger a deployment:**
```bash
cd /home/honzik/GitHub/FamilyCart/FamilyCart
git checkout develop
echo "# Test $(date)" >> README.md
git add README.md
git commit -m "test: UAT deployment trigger"
git push origin develop
```

**Monitor:**
- GitHub Actions UI
- Runner logs: `docker logs -f familycart-runner-1`
- UAT services: `cd /opt/familycart-uat && docker compose ps`

### Priority 4: Review Workflow Logs (Immediate)
**If deployment already ran:**
```
1. Go to GitHub Actions
2. Find recent "CI/CD" workflow run for develop branch
3. Click on workflow run
4. Expand "deploy-uat" job
5. Read error messages
6. Check which step failed
```

---

## 🎯 Expected Outcome

After fixes are applied:

1. **Push to develop branch** → Triggers ci.yml workflow
2. **ci.yml workflow runs:**
   - ✅ test job passes
   - ✅ security-scan job passes
   - ✅ build job passes (builds Docker images, pushes to ghcr.io)
   - ✅ **deploy-uat job runs** (pulls images, deploys to /opt/familycart-uat/)
   - ✅ Health checks pass
   - ✅ UAT accessible at http://localhost:3001 (or configured URL)

3. **Verification:**
   ```bash
   # Check UAT is running
   curl http://localhost:8001/health
   curl http://localhost:3001/
   ```

---

## 🔍 Common Issues and Solutions

### Issue: "deploy-uat" job doesn't appear in workflow
**Cause:** Condition `github.ref == 'refs/heads/develop'` not met  
**Solution:** Verify the push is to `develop` branch (not a feature branch)

### Issue: "deploy-uat" job skipped
**Cause:** Previous job (`build`) failed or was skipped  
**Solution:** Fix failing jobs (test, security-scan, build)

### Issue: "Context access might be invalid: uat"
**Cause:** UAT environment doesn't exist in GitHub  
**Solution:** Create environment in Settings → Environments

### Issue: SSH connection failures
**Cause:** Remote UAT deployment configured but secrets missing  
**Solution:** Either configure secrets OR remove them for local deployment

### Issue: Permission denied on /opt/familycart-uat
**Cause:** Runner user lacks write permissions  
**Solution:** 
```bash
sudo chown -R $(whoami):$(whoami) /opt/familycart-uat
```

---

## 📝 Next Steps

1. **Immediate:** Check GitHub environment configuration (5 min)
2. **Quick:** Review recent workflow run logs (10 min)
3. **Setup:** Ensure runner infrastructure ready (15 min)
4. **Test:** Trigger deployment and monitor (20 min)
5. **Document:** Update this analysis with findings (10 min)

---

## 📚 Related Documentation

- **Workflow Files:**
  - `.github/workflows/ci.yml` - Main CI/CD pipeline
  - `.github/workflows/branch-protection.yml` - PR quality gates
  
- **Environment Setup:**
  - `docs/github/GITHUB_ENVIRONMENTS_SETUP.md` - Environment configuration guide
  
- **CI Infrastructure:**
  - `docker-compose.ci-infrastructure.yml` - CI databases
  - `docker-compose.runners.yml` - GitHub runners
  - `docker-compose.uat.yml` - UAT deployment config
  
- **Scripts:**
  - `scripts/ci-management.sh` - CI infrastructure management

---

**Status:** Analysis complete - awaiting diagnostic results

**Next Action:** Execute Priority 1-3 actions and report findings
