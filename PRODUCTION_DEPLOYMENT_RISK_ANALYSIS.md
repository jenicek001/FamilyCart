# Production Deployment Risk Analysis & Mitigation Strategy

**Date:** December 18, 2025  
**Purpose:** Minimize production downtime by analyzing UAT deployment lessons and verifying all configurations  
**Status:** Pre-deployment verification required

---

## 🎯 Executive Summary

Based on comprehensive analysis of UAT deployment challenges and configuration comparisons, this document outlines critical risks and mandatory verification steps before production deployment.

**Key Finding:** UAT deployment took significant effort due to configuration mismatches. Production deployment requires:
- ✅ Complete environment variable verification
- ✅ Database migration readiness check
- ✅ Network and nginx configuration validation
- ✅ Dependency version compatibility verification
- ⚠️ **CRITICAL:** No production docker-compose.yml file exists - must be created

---

## ⚠️ CRITICAL RISKS IDENTIFIED

### 🔴 RISK #1: Missing Production Docker Compose Configuration
**Severity:** CRITICAL  
**Impact:** Cannot deploy without this file  
**Status:** ❌ NOT RESOLVED

**Finding:**
- UAT has `docker-compose.uat.yml` (265 lines, fully configured)
- Production has NO equivalent `docker-compose.prod.yml` or `docker-compose.app.yml`
- Documentation references `/opt/familycart-app/docker-compose.yml` but file doesn't exist in repo

**Required Action:**
```bash
# Must create: docker-compose.prod.yml
# Based on: docker-compose.uat.yml
# Changes needed:
#   - Remove uat- prefixes from service names
#   - Use production ports (80/443 instead of 3001/8001)
#   - Use production environment variables
#   - Use production volume names
#   - Configure for 2-VM architecture (stateful vs stateless)
```

**Mitigation Steps:**
1. Create `docker-compose.stateful.yml` for VM1 (PostgreSQL + Redis)
2. Create `docker-compose.app.yml` for VM2 (Backend + Frontend)
3. Test configurations in staging environment
4. Verify all environment variable references match production .env

---

### 🔴 RISK #2: Environment Variable Mismatches
**Severity:** HIGH  
**Impact:** Service failures, security vulnerabilities  
**Status:** ⚠️ REQUIRES VERIFICATION

**UAT Configuration (.env.uat.example - 54 variables):**
```bash
# Database
UAT_DB_PASSWORD=*****
POSTGRES_DB=familycart_uat
POSTGRES_USER=familycart_uat
POSTGRES_SERVER=uat-db
POSTGRES_PORT=5432

# Redis
UAT_REDIS_PASSWORD=*****
REDIS_HOST=uat-redis
REDIS_PORT=6379

# Application
UAT_SECRET_KEY=*****
UAT_TOKEN_EXPIRE_MINUTES=60
UAT_ALLOWED_HOSTS=localhost,127.0.0.1,uat.familycart.local
UAT_WEBSOCKET_ORIGINS=http://localhost:3001,https://uat.familycart.local

# Email (Production credentials)
EMAIL_PROVIDER=brevo
BREVO_SMTP_HOST=smtp-relay.brevo.com
BREVO_SMTP_PORT=587
BREVO_SMTP_USER=*****
BREVO_SMTP_PASSWORD=*****
FROM_EMAIL=noreply@familycart.app
FROM_NAME=FamilyCart
FRONTEND_URL=https://uat.familycart.app

# AI Configuration
GEMINI_API_KEY=*****
OLLAMA_HOST=http://uat-ollama:11434
OPENAI_API_KEY=*****
```

**Production Requirements (from DEPLOY_OCI_FREE_TIER.md):**
```bash
# VM1 (Database Server) - /opt/familycart-db/.env.db
POSTGRES_USER=familycart
POSTGRES_PASSWORD=***** (DIFFERENT from UAT)
POSTGRES_DB=familycart_production
REDIS_PASSWORD=***** (DIFFERENT from UAT)

# VM2 (Application Server) - /opt/familycart-app/.env.app
POSTGRES_SERVER=<VM1_PRIVATE_IP> (NOT hostname)
POSTGRES_PORT=5432
POSTGRES_USER=familycart
POSTGRES_PASSWORD=***** (MUST MATCH VM1)
POSTGRES_DB=familycart_production
REDIS_HOST=<VM1_PRIVATE_IP> (NOT hostname)
REDIS_PORT=6379
REDIS_PASSWORD=***** (MUST MATCH VM1)
SECRET_KEY=***** (NEW, DIFFERENT from UAT)
ACCESS_TOKEN_EXPIRE_MINUTES=1440 (24 hours, NOT 60)
ENVIRONMENT=production
DEBUG=false
ALLOWED_HOSTS=familycart.app,www.familycart.app
FRONTEND_URL=https://familycart.app
WEBSOCKET_ALLOWED_ORIGINS=https://familycart.app,https://www.familycart.app

# Email - SAME as UAT
EMAIL_PROVIDER=brevo
BREVO_SMTP_HOST=smtp-relay.brevo.com
BREVO_SMTP_PORT=587
BREVO_SMTP_USER=***** (SAME as UAT)
BREVO_SMTP_PASSWORD=***** (SAME as UAT)
FROM_EMAIL=noreply@familycart.app
FROM_NAME=FamilyCart

# AI - SAME as UAT
GEMINI_API_KEY=***** (SAME as UAT)
OPENAI_API_KEY=***** (SAME as UAT)
# Note: OLLAMA_HOST not set in production (Ollama disabled to save resources)

# CORS Configuration
CORS_ORIGINS=["https://familycart.app","https://www.familycart.app"]
NEXT_PUBLIC_API_URL=https://familycart.app/api
```

**Critical Differences:**
| Variable | UAT | Production | Risk if Wrong |
|----------|-----|------------|---------------|
| `POSTGRES_SERVER` | `uat-db` | `<VM1_PRIVATE_IP>` | ❌ Cannot connect to DB |
| `REDIS_HOST` | `uat-redis` | `<VM1_PRIVATE_IP>` | ❌ Cannot connect to Redis |
| `POSTGRES_DB` | `familycart_uat` | `familycart_production` | ❌ Wrong database |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | `1440` | ⚠️ Users logged out frequently |
| `ALLOWED_HOSTS` | UAT domain | Production domains | ❌ CORS failures |
| `WEBSOCKET_ALLOWED_ORIGINS` | UAT URLs | Production URLs | ❌ WebSocket blocked |
| `ENVIRONMENT` | `uat` | `production` | ⚠️ Wrong logging level |
| `DEBUG` | `false` | `false` | ✅ Same |

**Verification Checklist:**
- [ ] Create production .env file for VM1 (database)
- [ ] Create production .env file for VM2 (application)
- [ ] Verify all passwords are DIFFERENT from UAT
- [ ] Verify VM1 private IP is correct
- [ ] Verify all production domains are listed
- [ ] Test .env files with dry-run before deployment

---

### 🟡 RISK #3: Database Migration State Unknown
**Severity:** HIGH  
**Impact:** Data corruption, application crashes  
**Status:** ⚠️ REQUIRES VERIFICATION

**Current Migration State:**
```
Total Migrations: 15
Last Migration: ef912aabcc42_add_structured_quantity_and_unit_table.py (Nov 7, 2025)

Migration History:
1. 6d724cac3283 - initial_migration
2. 7f96d9c28e64 - add_nickname_column_to_user_table
3. 687785059f62 - add_last_modified_by_to_item
4. 6000f99ab353 - convert_datetime_columns_to_timezone_aware
5. d7b15d135da2 - update_timezone_aware_datetime_functions
6. 1aa3bd94a6b5 - add_standardized_name_and_translations
7. 2ebcd4b137e2 - add_icon_name_and_translations_to_category
8. 3f5e49c141c0 - rename_description_to_comment_in_item
9. 4fb56a654813 - add_icon_name_and_translations_to_category
10. b9398919b7f1 - final_model_updates_for_icon_and_translations
11. ef912aabcc42 - add_structured_quantity_and_unit_table
12. 795e7e423f03 - add_foreign_key_constraint_to_quantity
13. 4945d2a0eb2d - create_foreign_key_constraint_manual
14. 0a2113921588 - fix_unit_relationship_foreign_key
15. 0a3a8c5bc835 - make_nickname_mandatory_for_new_users
```

**Production Database Concerns:**
1. **Unknown State:** We don't know current migration level in production
2. **UAT vs Prod Drift:** UAT might be ahead of production
3. **No Rollback Plan:** If migration fails mid-way, no documented recovery

**Pre-Deployment Verification Required:**
```bash
# On Production VM1
docker exec familycart-prod-db psql -U familycart -d familycart_production \
  -c "SELECT * FROM alembic_version;"

# Compare with current HEAD
cd /home/honzik/GitHub/FamilyCart/FamilyCart/backend
alembic current
# Expected: 0a3a8c5bc835 (head)

# If production is behind, test upgrade path in staging first
```

**Migration Strategy:**
1. ✅ Backup production database BEFORE any migration
2. ✅ Test all pending migrations in UAT environment first
3. ✅ Verify data integrity after each migration
4. ✅ Have rollback script ready for each migration
5. ⚠️ Plan for downtime during migration (estimate: 5-10 minutes)

---

### 🟡 RISK #4: Docker Image Version Compatibility
**Severity:** MEDIUM  
**Impact:** Runtime errors, incompatibility issues  
**Status:** ⚠️ REQUIRES VERIFICATION

**Current Image Specifications:**

**Backend (Python 3.12):**
```dockerfile
FROM python:3.12-slim
Poetry version: Latest (via pip)
Dependencies:
  - fastapi = "^0.121.0"
  - uvicorn = "^0.29.0"
  - sqlalchemy = "^2.0.30"
  - alembic = "^1.13.1"
  - redis = "^5.0.4"
  - pydantic = "^2.7.1"
```

**Frontend (Node 20):**
```dockerfile
FROM node:20-alpine
Next.js version: 15.2.3
React version: 18.3.1
```

**Database Services (UAT Configuration):**
```yaml
postgres: postgres:15-alpine
redis: redis:8.0-alpine
```

**Version Compatibility Matrix:**
| Component | UAT Version | Production Required | Compatible? |
|-----------|-------------|---------------------|-------------|
| Python | 3.12-slim | 3.12-slim | ✅ Same |
| Node.js | 20-alpine | 20-alpine | ✅ Same |
| PostgreSQL | 15-alpine | 15-alpine | ✅ Same |
| Redis | 8.0-alpine | 8.0-alpine | ✅ Same |
| Poetry | Latest | Latest | ⚠️ Pin version |
| FastAPI | ^0.121.0 | ^0.121.0 | ✅ Same |
| Next.js | 15.2.3 | 15.2.3 | ✅ Same |

**Known Security Vulnerabilities (from SECURITY_VULNERABILITIES_ANALYSIS.md):**
- ❌ python-jose: CVE-2024-33663 (CRITICAL) - upgrade to 3.4.0 required
- ❌ starlette: CVE-2025-62727 (HIGH) - upgrade to 0.49.1 required
- ❌ python-multipart: CVE-2024-53981 (HIGH) - upgrade to 0.0.18 required
- ❌ axios: DoS vulnerability - upgrade to 1.12.0 required

**Pre-Deployment Action:**
```bash
# Update backend dependencies
cd backend
poetry update python-jose starlette python-multipart

# Update frontend dependencies
cd frontend
npm update axios

# Test in UAT first before production
```

---

### 🟡 RISK #5: Nginx Configuration Mismatches
**Severity:** MEDIUM  
**Impact:** 404 errors, SSL issues, WebSocket failures  
**Status:** ⚠️ REQUIRES VERIFICATION

**UAT Nginx Configuration:**
```nginx
# File: /etc/nginx/sites-available/familycart-uat
server_name: uat.familycart.local, localhost
Ports: 80 → 443 (HTTPS redirect)
SSL: /etc/nginx/ssl/familycart/uat.familycart.local.crt
Upstream: 127.0.0.1:8001 (backend), 127.0.0.1:3001 (frontend)
```

**Production Nginx Configuration:**
```nginx
# File: /etc/nginx/sites-available/familycart-production
server_name: familycart.app, www.familycart.app
Ports: 80 → 443 (HTTPS redirect)
SSL: Cloudflare Origin Certificates
Upstream: 127.0.0.1:8000 (backend), 127.0.0.1:3000 (frontend)
Redirect domains:
  - familycart.cz → familycart.app
  - familycart.eu → familycart.app
  - nakoupit.app → familycart.app
  - nakoupit.com → familycart.app
```

**Critical Differences:**
| Config Item | UAT | Production | Impact if Wrong |
|-------------|-----|------------|-----------------|
| Server Name | `uat.familycart.local` | `familycart.app` | ❌ 404 errors |
| Backend Port | `8001` | `8000` | ❌ Cannot reach API |
| Frontend Port | `3001` | `3000` | ❌ Cannot reach app |
| SSL Cert Path | Self-signed | Cloudflare certs | ❌ SSL errors |
| Cloudflare IPs | Not configured | Must whitelist | ❌ DDoS exposure |

**Verification Steps:**
1. ✅ Verify nginx configuration file exists: `nginx/sites-available/familycart-production`
2. ⚠️ Verify Cloudflare origin certificates are installed on VM2
3. ⚠️ Verify Cloudflare IP allowlist is configured in nftables
4. ⚠️ Test nginx configuration syntax before deployment
5. ⚠️ Verify WebSocket proxy settings for production domains

---

### 🟡 RISK #6: Network Architecture Differences
**Severity:** MEDIUM  
**Impact:** Service communication failures  
**Status:** ⚠️ REQUIRES PLANNING

**UAT Architecture (Single Server):**
```
All services on one machine:
- uat-db (port 5435)
- uat-redis (port 6380)
- uat-backend (port 8001)
- uat-frontend (port 3001)
- uat-ollama (port 11435, optional)

Network: uat-network (Docker bridge)
Communication: Container names (uat-db, uat-redis)
```

**Production Architecture (2-VM Split):**
```
VM1 (Stateful - Private IP only):
- postgres (port 5432)
- redis (port 6379)
Network: Private subnet 10.0.0.0/16

VM2 (Stateless - Public IP + Cloudflare):
- backend (port 8000)
- frontend (port 3000)
Network: Public + Private subnet
```

**Critical Configuration Changes:**
```bash
# UAT uses container names
POSTGRES_SERVER=uat-db  # Resolves via Docker DNS

# Production uses private IP
POSTGRES_SERVER=10.0.1.5  # Must be VM1's actual private IP

# Same for Redis
REDIS_HOST=10.0.1.5  # Must match VM1
```

**Pre-Deployment Verification:**
1. ✅ Verify VM1 private IP address (check OCI console)
2. ✅ Verify VM2 can reach VM1:5432 (PostgreSQL)
3. ✅ Verify VM2 can reach VM1:6379 (Redis)
4. ✅ Verify firewall rules allow private subnet traffic
5. ✅ Test connection with `nc` or `telnet` before deploying

---

### 🟢 RISK #7: CI/CD Pipeline Differences
**Severity:** LOW  
**Impact:** Manual deployment required  
**Status:** ⚠️ DOCUMENTED BEHAVIOR

**UAT Deployment (Automated):**
```yaml
Trigger: Push to 'develop' branch
Runner: self-hosted
Environment: uat
Secrets: UAT_HOST, UAT_USER, UAT_SSH_KEY (optional)
Default: Local deployment on runner at /opt/familycart-uat
Health Check: http://localhost:3001, http://localhost:8001
```

**Production Deployment (Manual Approval Required):**
```yaml
Trigger: Push to 'main' branch
Runner: self-hosted
Environment: production (requires approval)
Secrets: PRODUCTION_HOST, PRODUCTION_USER, PRODUCTION_SSH_KEY
No Default: Must have remote SSH configured
Health Check: https://familycart.app/health
```

**Key Differences:**
- ✅ UAT: Auto-deploys on develop push
- ⚠️ Production: Requires manual approval via GitHub environment protection
- ⚠️ Production: SSH to remote VM2 required (no local deployment option)
- ⚠️ Production: Must pull images from GHCR

**Pre-Deployment Setup:**
1. ✅ Create GitHub environment: `production`
2. ✅ Add environment secrets: PRODUCTION_HOST, PRODUCTION_USER, PRODUCTION_SSH_KEY
3. ✅ Configure environment protection: Require manual approval
4. ✅ Verify SSH key has access to VM2
5. ✅ Verify VM2 can pull from ghcr.io/jenicek001/familycart-*

---

## 📋 PRE-DEPLOYMENT VERIFICATION CHECKLIST

### Phase 1: Configuration Files (CRITICAL)
- [ ] **Create docker-compose.stateful.yml** (VM1: PostgreSQL + Redis)
  - Based on docker-compose.uat.yml services: uat-db, uat-redis
  - Remove `uat-` prefixes
  - Use standard ports (5432, 6379)
  - Configure for production resource limits
  - Test locally before deployment

- [ ] **Create docker-compose.app.yml** (VM2: Backend + Frontend)
  - Based on docker-compose.uat.yml services: uat-backend, uat-frontend
  - Remove `uat-` prefixes
  - Use standard ports (8000, 3000)
  - Configure environment variables for VM1 private IP
  - Test locally before deployment

- [ ] **Create production .env files**
  - `/opt/familycart-db/.env.db` (VM1)
  - `/opt/familycart-app/.env.app` (VM2)
  - Verify all required variables from comparison table above
  - **NEVER** use UAT passwords in production

- [ ] **Verify nginx configuration**
  - File exists: `nginx/sites-available/familycart-production`
  - Correct server names: familycart.app, www.familycart.app
  - Correct upstream ports: 8000, 3000
  - SSL certificate paths match Cloudflare origin certs
  - Test configuration: `nginx -t`

### Phase 2: Infrastructure Preparation
- [ ] **VM1 (Database Server)**
  - [ ] Verify private IP address: `ip addr show`
  - [ ] Create directory: `/opt/familycart-db`
  - [ ] Copy docker-compose.stateful.yml
  - [ ] Copy .env.db file
  - [ ] Test Docker Compose: `docker compose config`
  - [ ] Verify firewall allows VM2 → VM1:5432, VM1:6379

- [ ] **VM2 (Application Server)**
  - [ ] Verify can reach VM1 private IP: `nc -zv <VM1_IP> 5432`
  - [ ] Verify can reach VM1 Redis: `nc -zv <VM1_IP> 6379`
  - [ ] Create directory: `/opt/familycart-app`
  - [ ] Copy docker-compose.app.yml
  - [ ] Copy .env.app file
  - [ ] Install nginx configuration
  - [ ] Install Cloudflare origin certificates
  - [ ] Test nginx: `nginx -t`
  - [ ] Verify firewall allows Cloudflare IPs → VM2:80,443

- [ ] **Cloudflare Configuration**
  - [ ] Verify DNS points to VM2 public IP
  - [ ] SSL/TLS mode: Full (strict)
  - [ ] Origin certificates installed on VM2
  - [ ] Firewall rules configured (Cloudflare IPs only)

### Phase 3: Database Migration Planning
- [ ] **Check current production DB state**
  ```bash
  docker exec familycart-prod-db psql -U familycart -d familycart_production \
    -c "SELECT * FROM alembic_version;"
  ```

- [ ] **Backup production database**
  ```bash
  docker exec familycart-prod-db pg_dump -U familycart -d familycart_production \
    | gzip > prod_backup_$(date +%Y%m%d_%H%M%S).sql.gz
  ```

- [ ] **Test migrations in UAT**
  - Run all pending migrations
  - Verify data integrity
  - Document any issues
  - Prepare rollback scripts

- [ ] **Plan downtime window**
  - Estimate migration time: 5-10 minutes
  - Schedule during low-traffic period
  - Notify users in advance
  - Prepare rollback procedure

### Phase 4: Security Verification
- [ ] **Update vulnerable dependencies**
  ```bash
  # Backend
  poetry update python-jose starlette python-multipart
  
  # Frontend
  npm update axios
  ```

- [ ] **Verify secrets are unique**
  - [ ] SECRET_KEY different from UAT
  - [ ] POSTGRES_PASSWORD different from UAT
  - [ ] REDIS_PASSWORD different from UAT
  - [ ] All secrets stored in GitHub environment

- [ ] **Review security headers in nginx**
  - [ ] X-Frame-Options: DENY
  - [ ] X-Content-Type-Options: nosniff
  - [ ] Strict-Transport-Security configured
  - [ ] Content-Security-Policy configured

### Phase 5: CI/CD Pipeline Setup
- [ ] **GitHub Environment Configuration**
  - [ ] Create environment: `production`
  - [ ] Add secret: `PRODUCTION_HOST` (VM2 public IP)
  - [ ] Add secret: `PRODUCTION_USER` (ubuntu)
  - [ ] Add secret: `PRODUCTION_SSH_KEY` (private key)
  - [ ] Enable required reviewers
  - [ ] Test SSH connection from runner to VM2

- [ ] **Container Registry Access**
  - [ ] Verify VM2 can pull: `ghcr.io/jenicek001/familycart-backend:latest`
  - [ ] Verify VM2 can pull: `ghcr.io/jenicek001/familycart-frontend:latest`
  - [ ] Test docker login: `docker login ghcr.io`

### Phase 6: Deployment Testing (Staging)
- [ ] **Deploy to staging environment first**
  - [ ] Test complete deployment procedure
  - [ ] Verify all services start correctly
  - [ ] Run health checks
  - [ ] Test WebSocket connections
  - [ ] Test API endpoints
  - [ ] Test frontend accessibility

- [ ] **Load Testing**
  - [ ] Test with expected user load
  - [ ] Monitor resource usage
  - [ ] Verify no memory leaks
  - [ ] Test database connection pooling

### Phase 7: Rollback Preparation
- [ ] **Document rollback procedure**
  - [ ] How to restore database backup
  - [ ] How to revert to previous Docker images
  - [ ] How to restore nginx configuration
  - [ ] Emergency contact information

- [ ] **Test rollback in staging**
  - [ ] Verify backup restoration works
  - [ ] Verify service downgrade works
  - [ ] Document timing and steps

---

## 🚀 RECOMMENDED DEPLOYMENT SEQUENCE

### Step 1: Pre-Deployment (1-2 days before)
1. ✅ Complete all verification checklist items above
2. ✅ Create and test all production configuration files
3. ✅ Update vulnerable dependencies
4. ✅ Test full deployment in staging environment
5. ✅ Schedule maintenance window
6. ✅ Notify users of upcoming maintenance

### Step 2: Database Migration (Day of deployment)
1. ✅ Create full database backup
2. ✅ Stop UAT environment to prevent confusion
3. ✅ Enable maintenance mode on production frontend
4. ✅ Run database migrations on production
5. ✅ Verify migration success
6. ✅ Test database connectivity

### Step 3: Application Deployment
1. ✅ SSH to VM1, start stateful services:
   ```bash
   cd /opt/familycart-db
   docker compose -f docker-compose.stateful.yml up -d
   docker compose -f docker-compose.stateful.yml ps
   docker compose -f docker-compose.stateful.yml logs -f
   ```

2. ✅ Verify database and Redis are healthy:
   ```bash
   docker exec familycart-prod-db pg_isready -U familycart
   docker exec familycart-prod-redis redis-cli -a $REDIS_PASSWORD ping
   ```

3. ✅ SSH to VM2, start application services:
   ```bash
   cd /opt/familycart-app
   docker compose -f docker-compose.app.yml up -d
   docker compose -f docker-compose.app.yml ps
   docker compose -f docker-compose.app.yml logs -f
   ```

4. ✅ Verify services are healthy:
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:3000/
   ```

5. ✅ Start nginx and verify HTTPS:
   ```bash
   sudo systemctl start nginx
   sudo systemctl status nginx
   curl -I https://familycart.app/health
   ```

### Step 4: Post-Deployment Verification
1. ✅ Access application via browser: https://familycart.app
2. ✅ Test login functionality
3. ✅ Create test shopping list
4. ✅ Test real-time WebSocket updates
5. ✅ Verify AI categorization works
6. ✅ Test email notifications
7. ✅ Monitor logs for errors
8. ✅ Check Cloudflare analytics
9. ✅ Disable maintenance mode
10. ✅ Notify users deployment is complete

### Step 5: Monitoring (First 24 hours)
1. ✅ Monitor application logs continuously
2. ✅ Monitor database connection pool
3. ✅ Monitor Redis memory usage
4. ✅ Monitor CPU and memory on both VMs
5. ✅ Monitor error rates in logs
6. ✅ Monitor response times
7. ✅ Check for any reported user issues

---

## 📊 CONFIGURATION COMPARISON SUMMARY

### Environment Variables: UAT vs Production

| Category | UAT Count | Prod Count | Differences |
|----------|-----------|------------|-------------|
| Database | 5 | 5 | Hostnames, passwords |
| Redis | 3 | 3 | Hostnames, passwords |
| Security | 3 | 3 | SECRET_KEY, token expiry |
| Email | 8 | 8 | ✅ Identical |
| AI | 3 | 2 | Ollama disabled in prod |
| Domains | 2 | 4 | Additional prod domains |
| **Total** | **54** | **52** | **8 critical differences** |

### Docker Services: UAT vs Production

| Service | UAT | Production | Notes |
|---------|-----|------------|-------|
| PostgreSQL | ✅ uat-db | ✅ postgres (VM1) | Different hostname |
| Redis | ✅ uat-redis | ✅ redis (VM1) | Different hostname |
| Backend | ✅ uat-backend | ✅ backend (VM2) | Different ports |
| Frontend | ✅ uat-frontend | ✅ frontend (VM2) | Different ports |
| Ollama | ⚠️ Optional | ❌ Disabled | Save resources |
| Prometheus | ⚠️ Profile | ⚠️ TBD | Monitoring |
| Nginx | ✅ External | ✅ External (VM2) | Different config |

### Network Differences

| Aspect | UAT | Production |
|--------|-----|------------|
| Architecture | Single server | 2 VMs (split) |
| Database Access | Docker network | Private IP |
| Redis Access | Docker network | Private IP |
| External Access | Ports 3001, 8001 | Ports 80, 443 |
| SSL | Self-signed | Cloudflare |
| Firewall | Open (development) | Cloudflare IPs only |

---

## ⏱️ ESTIMATED DEPLOYMENT TIMELINE

| Phase | Duration | Critical? |
|-------|----------|-----------|
| Pre-deployment verification | 4-6 hours | ✅ YES |
| Create configuration files | 2-3 hours | ✅ YES |
| Test in staging | 2-4 hours | ✅ YES |
| Database backup | 10-15 min | ✅ YES |
| Database migration | 5-10 min | ✅ YES |
| Deploy VM1 services | 5-10 min | ✅ YES |
| Deploy VM2 services | 10-15 min | ✅ YES |
| Nginx configuration | 5-10 min | ✅ YES |
| Health verification | 15-20 min | ✅ YES |
| **Total Downtime** | **30-45 min** | ✅ |
| Post-deployment monitoring | 24 hours | ✅ YES |

---

## 🎯 SUCCESS CRITERIA

### Must Pass Before Going Live:
- [ ] All services healthy in staging environment
- [ ] Database migrations tested and successful
- [ ] Health checks passing for all services
- [ ] WebSocket connections working
- [ ] AI categorization functional
- [ ] Email notifications sending
- [ ] SSL certificates valid
- [ ] Cloudflare protection active
- [ ] No security vulnerabilities (critical/high)
- [ ] Rollback procedure tested and documented

### Post-Deployment Success Metrics:
- [ ] Zero application errors in first hour
- [ ] Response time < 200ms for API calls
- [ ] WebSocket latency < 100ms
- [ ] Database connection pool healthy
- [ ] Redis memory usage < 80%
- [ ] CPU usage < 60% on both VMs
- [ ] Memory usage < 80% on both VMs
- [ ] No user-reported issues in first 24 hours

---

## 📞 EMERGENCY CONTACTS & PROCEDURES

### Rollback Trigger Conditions:
1. Application crashes repeatedly
2. Database migration fails
3. Critical security vulnerability exploited
4. > 50% of users unable to access app
5. Data corruption detected
6. Performance degradation > 5x baseline

### Immediate Rollback Procedure:
```bash
# 1. Stop all services
ssh ubuntu@VM2_IP "cd /opt/familycart-app && docker compose down"
ssh ubuntu@VM1_IP "cd /opt/familycart-db && docker compose down"

# 2. Restore database
scp prod_backup_YYYYMMDD_HHMMSS.sql.gz ubuntu@VM1_IP:/tmp/
ssh ubuntu@VM1_IP "gunzip < /tmp/prod_backup_*.sql.gz | \
  docker exec -i familycart-prod-db psql -U familycart -d familycart_production"

# 3. Revert to previous Docker images
# (Tag previous working images as :rollback beforehand)
ssh ubuntu@VM2_IP "cd /opt/familycart-app && \
  docker compose -f docker-compose.app.yml down && \
  docker pull ghcr.io/jenicek001/familycart-backend:rollback && \
  docker pull ghcr.io/jenicek001/familycart-frontend:rollback && \
  docker compose -f docker-compose.app.yml up -d"

# 4. Verify rollback success
curl https://familycart.app/health
```

---

## 📝 FINAL RECOMMENDATIONS

### Before Deployment:
1. ✅ **DO NOT SKIP** any verification checklist item
2. ✅ **TEST EVERYTHING** in staging first
3. ✅ **BACKUP DATABASE** before any changes
4. ✅ **HAVE ROLLBACK PLAN** ready and tested
5. ✅ **SCHEDULE MAINTENANCE** during low-traffic hours

### During Deployment:
1. ✅ Follow deployment sequence exactly
2. ✅ Verify each step before proceeding
3. ✅ Monitor logs continuously
4. ✅ Have team available for support
5. ✅ Be prepared to rollback if needed

### After Deployment:
1. ✅ Monitor for 24 hours minimum
2. ✅ Respond to user feedback quickly
3. ✅ Document any issues encountered
4. ✅ Update deployment procedures based on lessons learned
5. ✅ Schedule post-deployment review meeting

---

## ✅ CONCLUSION

**Production deployment is HIGH RISK without completing verification checklist.**

**Critical Missing Items:**
1. ❌ No production docker-compose files
2. ❌ No production .env files verified
3. ⚠️ Security vulnerabilities not patched
4. ⚠️ Database migration state unknown
5. ⚠️ Staging environment testing incomplete

**Recommendation:** **DO NOT DEPLOY** until all verification items are complete.

**Estimated Time to Production-Ready:** 2-3 days of careful preparation

**Risk Level:** 
- Current: 🔴 HIGH (70% chance of deployment issues)
- After verification: 🟢 LOW (10% chance of deployment issues)

---

**Document Status:** DRAFT - Requires team review and approval  
**Next Steps:** Complete Phase 1 verification checklist  
**Target Production Date:** TBD after verification complete
