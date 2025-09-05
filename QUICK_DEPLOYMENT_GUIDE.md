# FamilyCart Infrastructure Quick Deployment Guide

This guide provides step-by-step instructions for deploying the complete GitHub Runners + UAT Infrastructure.

## 📋 Prerequisites

- Ubuntu 22.04 LTS server with minimum 32GB RAM, 8+ CPU cores
- Docker and Docker Compose installed
- GitHub repository access with admin permissions
- Domain or subdomain for UAT environment (optional)

## 🚀 Deployment Steps

### Step 1: Validate Infrastructure (RECOMMENDED)

Run the comprehensive validation script to ensure all components are ready:

```bash
cd /opt/familycart
./scripts/validate-infrastructure.sh
```

Expected result: **100% validation success rate** (31/31 checks passed)

### Step 2: Deploy GitHub Self-Hosted Runners

1. **Generate GitHub Personal Access Token**
   - Follow guide: `GITHUB_AUTHORIZATION_SETUP.md`
   - Required permissions: `repo:all`, `workflow:write`, `admin:org`

2. **Configure Environment**
   ```bash
   # Create environment file for runners
   cp .env.runners.example .env.runners
   nano .env.runners
   ```

3. **Set GitHub Token**
   ```bash
   export GITHUB_TOKEN="your_github_token_here"
   ```

4. **Deploy Runners**
   ```bash
   # Option A: Using Docker Compose (Recommended)
   docker-compose -f docker-compose.runners.yml up -d

   # Option B: Using Setup Script
   sudo ./deploy/scripts/setup-github-runners.sh
   ```

5. **Verify Deployment**
   ```bash
   # Check runner health
   docker ps | grep familycart-runner
   docker logs familycart-runner-1

   # Check GitHub UI: Repository > Settings > Actions > Runners
   ```

### Step 3: Deploy UAT Environment

1. **Configure UAT Environment**
   ```bash
   cp .env.uat.example .env.uat
   nano .env.uat
   ```

   **Required variables:**
   ```env
   UAT_DB_PASSWORD=your_secure_db_password
   UAT_REDIS_PASSWORD=your_secure_redis_password
   UAT_SECRET_KEY=your_32_character_secret_key
   GEMINI_API_KEY=your_gemini_api_key
   ```

2. **Setup SSL Certificates (Optional)**
   ```bash
   cd nginx/ssl
   # Follow README.md for certificate generation
   
   # Quick self-signed certificate for testing:
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout uat.familycart.local.key \
     -out uat.familycart.local.crt \
     -subj "/CN=uat.familycart.local"
   ```

3. **Deploy UAT Stack**
   ```bash
   # Create necessary directories
   mkdir -p logs/{backend,frontend,nginx}

   # Deploy UAT environment
   docker-compose -f docker-compose.uat.yml up -d

   # Deploy monitoring (optional)
   docker-compose -f docker-compose.uat.yml --profile monitoring-enabled up -d
   ```

4. **Verify UAT Deployment**
   ```bash
   # Check service health
   curl -f http://localhost:8001/health
   curl -f http://localhost:3001/
   
   # Check all containers
   docker-compose -f docker-compose.uat.yml ps
   ```

### Step 4: Deploy Monitoring Stack

1. **Configure Monitoring**
   ```bash
   cd monitoring
   cp .env.monitoring.example .env.monitoring
   nano .env.monitoring
   ```

2. **Deploy Monitoring**
   ```bash
   docker-compose -f monitoring/docker-compose.monitoring.yml up -d
   ```

3. **Access Dashboards**
   - **Grafana**: http://localhost:3000 (admin/admin)
   - **Prometheus**: http://localhost:9090
   - **Alertmanager**: http://localhost:9093

### Step 5: Run Load Testing (Validation)

1. **Install k6** (if not available)
   ```bash
   # Ubuntu/Debian
   sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
   echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
   sudo apt-get update
   sudo apt-get install k6
   ```

2. **Run Performance Tests**
   ```bash
   cd deploy/scripts
   k6 run --env UAT_BASE_URL=http://localhost:3001 load-test.js
   ```

3. **Expected Results**
   - Support for 25+ concurrent users
   - 95% of requests under 500ms
   - Error rate under 2%

### Step 6: Configure CI/CD Pipeline

1. **Set GitHub Secrets**
   Go to GitHub Repository > Settings > Secrets and add:
   ```
   OCI_SSH_KEY=your_production_ssh_key
   OCI_HOST=your_production_server_ip
   OCI_USER=your_production_username
   PRODUCTION_URL=https://your-production-domain.com
   ```

2. **Test CI/CD Pipeline**
   ```bash
   # Push to develop branch to trigger UAT deployment
   git push origin develop

   # Push to main branch to trigger production deployment
   git push origin main
   ```

## 🔧 Maintenance & Monitoring

### Daily Checks
- Monitor GitHub runners status in repository settings
- Check UAT environment health: http://localhost:8001/health
- Review Grafana dashboards for system metrics

### Weekly Tasks
- Update runner images: `docker-compose -f docker-compose.runners.yml pull && docker-compose -f docker-compose.runners.yml up -d`
- Review system logs: `journalctl -u docker.service -f`
- Check resource usage in monitoring dashboards

### Monthly Tasks
- Rotate GitHub tokens and update environment
- Review and update SSL certificates
- Performance optimization based on monitoring data

## 🆘 Troubleshooting

### GitHub Runners Not Appearing
```bash
# Check runner logs
docker logs familycart-runner-1

# Verify GitHub token permissions
# Check network connectivity to GitHub
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
```

### UAT Environment Issues
```bash
# Check service health
docker-compose -f docker-compose.uat.yml ps
docker-compose -f docker-compose.uat.yml logs uat-backend

# Database connection issues
docker exec -it familycart-uat-db pg_isready -U familycart_uat -d familycart_uat
```

### SSL Certificate Problems
```bash
# Verify certificate validity
openssl x509 -in nginx/ssl/uat.familycart.local.crt -text -noout

# Test SSL connection
openssl s_client -connect uat.familycart.local:443
```

### Performance Issues
```bash
# Check system resources
htop
docker stats

# Check monitoring metrics
curl http://localhost:9090/api/v1/query?query=up
curl http://localhost:8001/system/info
```

## 📞 Support Resources

- **Infrastructure Validation**: `./scripts/validate-infrastructure.sh`
- **Detailed Setup Guide**: `DEPLOY_SELF_HOSTED_UAT.md`
- **GitHub Setup**: `GITHUB_AUTHORIZATION_SETUP.md`
- **Version Updates**: `GITHUB_RUNNERS_VERSIONS_UPDATE.md`
- **SSL Setup**: `nginx/ssl/README.md`

## 🎯 Success Metrics

- ✅ GitHub runners: 3 active runners visible in repository settings
- ✅ UAT environment: All health checks returning 200 OK
- ✅ Monitoring: All services showing as "UP" in Prometheus
- ✅ Load testing: Successfully handling 25+ concurrent users
- ✅ CI/CD: Successful deployment to UAT and production environments

---

**Need help?** Check the validation report in `test-results/` or run `./scripts/validate-infrastructure.sh` for detailed diagnostics.