# Deployment Documentation

**Purpose:** Guides and configurations for deploying FamilyCart to various environments

---

## 📁 Files in this Directory

### UAT Deployment
- **`DEPLOY_SELF_HOSTED_UAT.md`** ⭐ (747 lines) - Comprehensive UAT deployment guide
  - Self-hosted Ubuntu server setup
  - GitHub runners configuration
  - Docker compose infrastructure
  - Cloudflare proxy integration
  
- **`ENVIRONMENT_CONFIG.md`** - Environment variable configuration
  - Development vs production settings
  - Database connection strings
  - API keys and secrets management

### Production Planning
- **`DEPLOY_OCI_FREE_TIER.md`** (326 lines) - Oracle Cloud Infrastructure deployment
  - Free tier architecture
  - 2 micro VM setup
  - Cost optimization strategies
  - Cloudflare integration

### Infrastructure Setup
- **`docker_installation_ubuntu.md`** (188 lines) - Docker setup guide
  - Ubuntu x64/AMD64 installation
  - Prerequisites and system checks
  - Post-installation configuration
  
- **`DOCKER_COMPOSE_V2_REFERENCE.md`** (144 lines) - Docker Compose V2 commands
  - Migration from V1 to V2
  - Core commands for UAT deployment
  - Troubleshooting tips

### Cloudflare & Monitoring
- **`CLOUDFLARE_MONITORING_SETUP.md`** (193 lines) - Cloudflare monitoring setup
  - Domain strategy
  - Services to expose
  - Security measures
  - Zero Trust Access
  
- **`cloudflare-access-config.md`** (227 lines) - Cloudflare Access configuration
  - Application configuration
  - Grafana dashboard setup
  - Prometheus API access
  - Authentication policies

### Nginx Architecture
- **`NGINX_SEPARATION_PROPOSAL.md`** (544 lines) - Nginx separation strategy
  - Separate repository architecture
  - Reverse proxy configuration
  - Multi-service setup
  - SSL/TLS management

---

## 🎯 Quick Start

### Deploying UAT Environment
```bash
# 1. Read the comprehensive guide
cat DEPLOY_SELF_HOSTED_UAT.md

# 2. Install Docker
sudo bash < docker_installation_ubuntu.md

# 3. Set up environment variables
cp ../../.env.uat.example ../../.env
# Edit .env with your configuration

# 4. Deploy UAT
cd /opt/familycart-uat
docker compose -f docker-compose.uat.yml up -d

# 5. Set up monitoring
bash ../../scripts/uat/setup-cloudflare-monitoring.sh
```

### Planning Production Deployment
```bash
# Review OCI free tier strategy
cat DEPLOY_OCI_FREE_TIER.md
```

---

## 📊 Environment Overview

| Environment | Status | Documentation |
|-------------|--------|---------------|
| **Development** | ✅ Active | `docker-compose.dev.yml` in root |
| **UAT** | ✅ Active | `DEPLOY_SELF_HOSTED_UAT.md` (this machine) |
| **CI/CD** | ✅ Active | GitHub runners + infrastructure |
| **Production** | 📋 Planned | `DEPLOY_OCI_FREE_TIER.md` |

---

## 🔧 Related Directories

- **`/deploy/`** - Deployment scripts and templates
  - `deploy/nginx/` - Nginx configuration templates
  - `deploy/monitoring/` - Monitoring configurations
  - `deploy/github-runners/` - Runner Docker setup
  - `deploy/scripts/` - Server setup scripts

- **`/scripts/uat/`** - UAT operational scripts
  - `setup-cloudflare-monitoring.sh`
  - `test-uat-nginx.sh`

- **`/monitoring/`** - Active UAT monitoring stack
  - Prometheus, Grafana, Alertmanager configs
  - Health check scripts

---

## 🛡️ Security Considerations

All deployment guides include:
- ✅ SSL/TLS certificate management
- ✅ Cloudflare Zero Trust Access
- ✅ Environment variable security
- ✅ Docker security best practices
- ✅ Firewall configuration
- ✅ SSH key management

---

## 💡 Deployment Philosophy

1. **Infrastructure as Code** - All configurations versioned
2. **Security First** - Zero Trust, SSL everywhere
3. **Monitoring Built-in** - Prometheus + Grafana from day 1
4. **Cost Conscious** - Free tier optimization
5. **Reproducible** - Documented, scripted, automated

---

**For CI/CD setup, see:** `../github/` directory  
**For development workflow, see:** `../development/` directory
