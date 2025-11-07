# GitHub CI/CD Documentation

**Purpose:** GitHub setup, runner configuration, and CI/CD pipeline documentation

---

## 📁 Files in this Directory

### Environment Setup
- **`GITHUB_ENVIRONMENTS_SETUP.md`** (139 lines) - GitHub Environments configuration
  - Environment creation (development, UAT, production)
  - Environment-specific secrets
  - Protection rules and approvals
  - Deployment workflows

### Token & Authentication
- **`GITHUB_TOKEN_STEPS.md`** - Token setup walkthrough
  - Step-by-step token creation
  - Required permissions/scopes
  - Security best practices
  
- **`create-github-token-guide.md`** - Personal Access Token guide
  - Core repository access
  - Token management
  - Rotation strategies

### MCP Server Integration
- **`setup-github-mcp-server.md`** (183 lines) - Model Context Protocol server
  - MCP server setup for GitHub
  - API integration
  - Usage examples

---

## 🎯 Quick Start

### Setting Up GitHub Runners

```bash
# 1. Create a GitHub Personal Access Token
# Follow: create-github-token-guide.md

# 2. Set up self-hosted runners
cd ../../deploy/github-runners/
# Edit configuration with your token
docker compose -f ../../docker-compose.runners.yml up -d

# 3. Verify runners are active
docker ps --filter "name=familycart-runner"
```

### Configuring GitHub Environments

```bash
# Read the comprehensive guide
cat GITHUB_ENVIRONMENTS_SETUP.md

# Set up environments in GitHub UI:
# 1. Settings → Environments
# 2. Create: development, uat, production
# 3. Add environment secrets
# 4. Configure protection rules
```

### Updating Runner Tokens

```bash
# Use the token update script
../../scripts/update-github-token.sh
```

---

## 🏃 Active GitHub Infrastructure

### Self-Hosted Runners (This Machine)
```
✅ familycart-runner-1    Up 8+ days (healthy)
✅ familycart-runner-2    Up 8+ days (healthy)
✅ familycart-runner-3    Up 8+ days (healthy)
```

**Managed by:** `docker-compose.runners.yml` in root directory

### CI Infrastructure (This Machine)
```
✅ postgres-ci-familycart    Up 8+ days (healthy)   Port 5432
✅ redis-ci-familycart       Up 8+ days (healthy)   Port 6379
```

**Managed by:** `docker-compose.ci-infrastructure.yml` in root directory

---

## 🔄 CI/CD Workflow

### Current Workflow (`.github/workflows/ci.yml`)

1. **Code Push** → Triggers CI pipeline
2. **Lint & Test** → Code quality checks
3. **Build Images** → Docker images for backend/frontend
4. **Push to Registry** → GitHub Container Registry (ghcr.io)
5. **Deploy to UAT** → Automatic deployment to `/opt/familycart-uat/`
6. **Health Checks** → Verify deployment success

### Workflow Files Location
```
.github/workflows/
├── ci.yml              # Main CI/CD pipeline
└── [other workflows]
```

---

## 📊 GitHub Environments

| Environment | Purpose | Protection | Deployment Target |
|-------------|---------|------------|-------------------|
| **development** | Feature testing | None | Developer machines |
| **uat** | User acceptance | Auto-deploy | This machine (`/opt/familycart-uat/`) |
| **production** | Live environment | Manual approval | Oracle Cloud (planned) |

---

## 🔑 Secrets Management

### Repository Secrets
Located in: GitHub Settings → Secrets and variables → Actions

**Required secrets:**
- `GHCR_TOKEN` - GitHub Container Registry access
- `UAT_HOST` - UAT server hostname
- `UAT_SSH_KEY` - SSH key for UAT deployment
- Database credentials
- Redis credentials
- API keys

### Environment-Specific Secrets
Each environment has its own secrets:
- Development: Local testing credentials
- UAT: UAT server credentials  
- Production: Production credentials (future)

---

## 🛠️ Maintenance Scripts

Located in `/scripts/` directory:

- **`update-github-token.sh`** - Update runner GitHub tokens
- **`push-docker-images.sh`** - Manual image push to registry
- **`ci-management.sh`** - CI infrastructure management
- **`generate-ci-credentials.sh`** - Generate CI credentials

---

## 📚 Related Documentation

- **CI/CD Archive:** `../archives/ci-cd/` - Completed CI/CD work
  - `CI_INFRASTRUCTURE_COMPLETE.md`
  - `CI_QUALITY_STANDARDS.md`
  - `WORKFLOW_TEST_RESULTS.md`

- **Test Reports:** `../archives/test-reports/` - CI/CD test history

- **Deployment:** `../deployment/` - Environment deployment guides

---

## 🎯 Best Practices

### Runner Management
- ✅ Keep tokens secure and rotated
- ✅ Monitor runner health and logs
- ✅ Resource limits to prevent crashes
- ✅ Separate runners for parallel builds

### Workflow Design
- ✅ Fail fast with linting first
- ✅ Cache dependencies for speed
- ✅ Comprehensive test coverage
- ✅ Automatic deployment to UAT
- ✅ Manual approval for production

### Security
- ✅ Secrets stored in GitHub Secrets
- ✅ Never commit credentials to repo
- ✅ Environment-specific protection rules
- ✅ SSH key-based authentication

---

## 🔍 Troubleshooting

### Runner Issues
```bash
# Check runner logs
docker logs familycart-runner-1

# Restart runners
docker compose -f docker-compose.runners.yml restart

# Rebuild runners
docker compose -f docker-compose.runners.yml up -d --build
```

### CI Infrastructure Issues
```bash
# Check database
docker logs postgres-ci-familycart

# Check Redis
docker logs redis-ci-familycart

# Restart infrastructure
docker compose -f docker-compose.ci-infrastructure.yml restart
```

---

**For deployment instructions, see:** `../deployment/` directory  
**For archived CI/CD docs, see:** `../archives/ci-cd/` directory
