# FamilyCart Self-Hosted Ubuntu Build & UAT Environment

This document provides a comprehensive strategy for deploying a self-hosted Ubuntu server that serves as both a **build environment** (GitHub runners) and **User Acceptance Testing (UAT) environment** for the FamilyCart application. This setup is designed to complement the [OCI production deployment](./DEPLOY_OCI_FREE_TIER.md) and support up to 50 concurrent users.

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Server Requirements](#server-requirements) 
3. [Security & Network Configuration](#security--network-configuration)
4. [GitHub Self-Hosted Runners](#github-self-hosted-runners)
5. [UAT Environment Setup](#uat-environment-setup)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Deployment Procedures](#deployment-procedures)

---

## Architecture Overview

### Deployment Strategy
```
┌─────────────────────────────────────────────────────────────┐
│ Self-Hosted Ubuntu Server (Home DMZ)                        │
├─────────────────────────────────────────────────────────────┤
│ 1. GitHub Self-Hosted Runners                              │
│    - Container builds (backend, frontend)                  │ 
│    - Code quality checks (pytest, eslint, security scans)  │
│    - Automated testing and validation                      │
│                                                             │
│ 2. UAT Environment                                         │ 
│    - Complete FamilyCart stack deployment                  │
│    - User acceptance testing for <50 users                 │
│    - Pre-production validation                             │
│                                                             │
│ 3. Supporting Services                                     │
│    - Docker registry cache                                 │
│    - Monitoring and logging                                │
│    - Backup and recovery systems                           │
└─────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────┐
│ Production Environment (OCI Free Tier)                     │
│ - High availability deployment                              │
│ - Cloudflare integration                                    │ 
│ - Production-grade monitoring                               │
└─────────────────────────────────────────────────────────────┘
```

### Service Distribution
| Service | Self-Hosted | OCI Production | Purpose |
|---------|-------------|----------------|---------|
| GitHub Runners | ✅ | ❌ | Build automation & CI/CD |
| UAT Deployment | ✅ | ❌ | Pre-production testing |
| Production API | ❌ | ✅ | Live user traffic |
| Production DB | ❌ | ✅ | Production data |
| Monitoring | ✅ | ✅ | Both environments |

---

## Server Requirements

### Minimum Hardware Specifications
- **CPU**: 8+ cores (for parallel builds and UAT load)
- **RAM**: 32+ GB (GitHub runners + full stack + 50 concurrent users)
- **Storage**: 500+ GB SSD (Docker images, builds, logs, backups)
- **Network**: 100 Mbps up/down (confirmed available)

### Software Requirements  
- **OS**: Ubuntu 24.04 LTS
- **Docker**: Latest stable version
- **Docker Compose**: V2+
- **Git**: Latest version
- **Node.js**: 20+ (for runner actions)
- **Python**: 3.12+ (for backend builds)

### Resource Allocation Planning
```yaml
GitHub Runners: 16GB RAM, 4 CPU cores
UAT Environment: 12GB RAM, 4 CPU cores  
System + Monitoring: 4GB RAM, 2 CPU cores
Total: 32GB RAM, 8+ CPU cores
```

---

## Security & Network Configuration

### Network Architecture
```
Internet ──► Router/Firewall ──► DMZ Subnet ──► Ubuntu Server
                    │                              │
                    │              ┌───────────────┼─── Port 22 (SSH)
                    │              │               ├─── Port 80/443 (UAT Web)
                    └──────────────┼───────────────┼─── Port 9418 (Git, if needed)
                                   │               └─── Internal Docker Network
                                   │
                           GitHub Webhook Endpoints
```

### Security Hardening Checklist
- [ ] **SSH Configuration**
  - [ ] Key-based authentication only (disable password)
  - [ ] Change default SSH port (security through obscurity)
  - [ ] Configure fail2ban for intrusion prevention
  - [ ] Limit SSH access to specific IP ranges

- [ ] **Firewall Configuration (UFW)**
  ```bash
  # Basic firewall rules
  ufw default deny incoming
  ufw default allow outgoing
  ufw allow 2222/tcp    # Custom SSH port
  ufw allow 80/tcp      # HTTP for UAT
  ufw allow 443/tcp     # HTTPS for UAT
  ufw allow 9000/tcp    # GitHub webhook receiver
  ufw enable
  ```

- [ ] **System Hardening**
  - [ ] Regular system updates (unattended-upgrades)
  - [ ] Disable unnecessary services
  - [ ] Configure log rotation and monitoring
  - [ ] Set up intrusion detection (AIDE or similar)

### SSL/TLS Configuration
- Use Let's Encrypt for UAT environment SSL certificates
- Implement proper certificate renewal automation
- Configure HTTPS redirects for all web traffic

---

## GitHub Self-Hosted Runners

### Runner Architecture  
- **Multiple Runners**: 3-4 concurrent runners for parallel builds
- **Container Isolation**: Each runner in separate Docker container
- **Auto-scaling**: Dynamic runner creation based on queue depth
- **Security**: Ephemeral runners for security isolation

### Installation Script
Create `/opt/github-runners/setup-runners.sh`:
```bash
#!/bin/bash
set -euo pipefail

GITHUB_OWNER="jenicek001"
GITHUB_REPO="FamilyCart" 
RUNNER_COUNT=3
WORK_DIR="/opt/github-runners"

# Create runner directories
for i in $(seq 1 $RUNNER_COUNT); do
    mkdir -p "$WORK_DIR/runner-$i"
done

# Download and configure runners (requires GitHub token)
# See detailed implementation in scripts/setup-github-runners.sh
```

### Runner Capabilities
- **Container Builds**: Docker-in-Docker for building FamilyCart images
- **Multi-language**: Python (Poetry), Node.js (npm), Docker
- **Code Quality**: 
  - Backend: pytest, black, isort, bandit, pylint
  - Frontend: eslint, prettier, typescript, playwright
- **Security Scanning**: Container vulnerability scanning with Trivy
- **Performance Testing**: Load testing with automated benchmarks

### Runner Docker Compose
Create `docker-compose.github-runners.yml`:
```yaml
version: '3.9'
services:
  runner-1:
    build: ./github-runner
    environment:
      - GITHUB_OWNER=jenicek001
      - GITHUB_REPO=FamilyCart
      - RUNNER_NAME=self-hosted-1
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - runner1-work:/work
    restart: unless-stopped

  runner-2:
    build: ./github-runner  
    environment:
      - GITHUB_OWNER=jenicek001
      - GITHUB_REPO=FamilyCart
      - RUNNER_NAME=self-hosted-2
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - runner2-work:/work
    restart: unless-stopped

  runner-3:
    build: ./github-runner
    environment:
      - GITHUB_OWNER=jenicek001  
      - GITHUB_REPO=FamilyCart
      - RUNNER_NAME=self-hosted-3
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - runner3-work:/work
    restart: unless-stopped

volumes:
  runner1-work:
  runner2-work:  
  runner3-work:
```

---

## UAT Environment Setup

### UAT Service Configuration
Create `docker-compose.uat.yml` for UAT-specific deployment:
```yaml
version: '3.9'
services:
  uat-db:
    image: postgres:15-alpine
    container_name: familycart-uat-db
    environment:
      - POSTGRES_DB=familycart_uat
      - POSTGRES_USER=familycart_uat
      - POSTGRES_PASSWORD=${UAT_DB_PASSWORD}
    volumes:
      - uat_postgres_data:/var/lib/postgresql/data
    ports:
      - "5433:5432"  # Different port from dev
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U familycart_uat -d familycart_uat"]
      interval: 10s
      timeout: 5s
      retries: 5

  uat-redis:
    image: redis:8.0-alpine
    container_name: familycart-uat-redis
    command: ["redis-server", "--requirepass", "${UAT_REDIS_PASSWORD}"]
    ports:
      - "6380:6379"  # Different port from dev
    volumes:
      - uat_redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${UAT_REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  uat-backend:
    image: ghcr.io/jenicek001/familycart-backend:latest
    container_name: familycart-uat-backend
    environment:
      - POSTGRES_SERVER=uat-db
      - POSTGRES_DB=familycart_uat
      - POSTGRES_USER=familycart_uat
      - POSTGRES_PASSWORD=${UAT_DB_PASSWORD}
      - REDIS_HOST=uat-redis
      - REDIS_PASSWORD=${UAT_REDIS_PASSWORD}
      - SECRET_KEY=${UAT_SECRET_KEY}
      - ENVIRONMENT=uat
    ports:
      - "8001:8000"  # Different port from dev
    depends_on:
      uat-db:
        condition: service_healthy
      uat-redis:
        condition: service_healthy
    restart: unless-stopped

  uat-frontend:
    image: ghcr.io/jenicek001/familycart-frontend:latest
    container_name: familycart-uat-frontend
    environment:
      - NEXT_PUBLIC_API_URL=https://uat.familycart.local/api
      - NEXT_PUBLIC_ENVIRONMENT=uat
    ports:
      - "3001:3000"  # Different port from dev
    depends_on:
      - uat-backend
    restart: unless-stopped

  # Reverse proxy for UAT (nginx)
  uat-proxy:
    image: nginx:alpine
    container_name: familycart-uat-proxy
    volumes:
      - ./nginx/uat.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    ports:
      - "80:80"
      - "443:443" 
    depends_on:
      - uat-frontend
      - uat-backend
    restart: unless-stopped

volumes:
  uat_postgres_data:
  uat_redis_data:
```

### UAT Environment Features
- **Isolated Data**: Separate PostgreSQL database for UAT testing
- **Performance Monitoring**: Resource usage tracking for capacity planning
- **User Simulation**: Load testing tools for concurrent user simulation
- **Feature Flags**: Environment-specific feature toggles
- **Test Data Management**: Automated test data seeding and cleanup

### Domain Configuration
- **UAT Domain**: `uat.familycart.local` (internal DNS or hosts file)
- **SSL Certificates**: Self-signed or Let's Encrypt for testing
- **Load Balancer**: nginx for reverse proxy and SSL termination

---

## CI/CD Pipeline

### Enhanced GitHub Actions Workflow
Update `.github/workflows/ci.yml`:
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: jenicek001/familycart

jobs:
  test:
    runs-on: self-hosted
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Poetry
        uses: snok/install-poetry@v1

      - name: Install backend dependencies
        working-directory: ./backend
        run: poetry install

      - name: Run backend tests
        working-directory: ./backend
        run: |
          poetry run pytest --cov=app --cov-report=xml
          poetry run black --check .
          poetry run isort --check-only .
          poetry run bandit -r app/

      - name: Set up Node.js  
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install frontend dependencies
        working-directory: ./frontend
        run: npm ci

      - name: Run frontend tests
        working-directory: ./frontend
        run: |
          npm run lint
          npm run typecheck
          npm run build

  security-scan:
    runs-on: self-hosted
    needs: test
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  build:
    runs-on: self-hosted
    needs: [test, security-scan]
    outputs:
      backend-image: ${{ steps.meta-backend.outputs.tags }}
      frontend-image: ${{ steps.meta-frontend.outputs.tags }}
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract backend metadata
        id: meta-backend
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-backend
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=sha,prefix={{branch}}-

      - name: Build and push backend image
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: ${{ steps.meta-backend.outputs.tags }}
          labels: ${{ steps.meta-backend.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Extract frontend metadata
        id: meta-frontend
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}-frontend
          tags: |
            type=ref,event=branch
            type=ref,event=pr  
            type=sha,prefix={{branch}}-

      - name: Build and push frontend image
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: true
          tags: ${{ steps.meta-frontend.outputs.tags }}
          labels: ${{ steps.meta-frontend.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-uat:
    runs-on: self-hosted
    needs: build
    if: github.ref == 'refs/heads/develop'
    steps:
      - name: Deploy to UAT
        run: |
          cd /opt/familycart-uat
          docker-compose -f docker-compose.uat.yml pull
          docker-compose -f docker-compose.uat.yml up -d --remove-orphans
          
      - name: Health check UAT deployment
        run: |
          sleep 30
          curl -f http://localhost:3001/health || exit 1
          curl -f http://localhost:8001/health || exit 1

      - name: Run UAT integration tests
        working-directory: ./frontend
        run: npm run test:uat

  deploy-production:
    runs-on: self-hosted
    needs: build
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
      - name: Deploy to OCI Production
        env:
          OCI_SSH_KEY: ${{ secrets.OCI_SSH_KEY }}
          OCI_HOST: ${{ secrets.OCI_HOST }}
        run: |
          echo "$OCI_SSH_KEY" > /tmp/oci_key
          chmod 600 /tmp/oci_key
          ssh -i /tmp/oci_key -o StrictHostKeyChecking=no ubuntu@$OCI_HOST \
            'cd /opt/familycart && docker-compose -f docker-compose.app.yml pull && docker-compose -f docker-compose.app.yml up -d --remove-orphans'
          rm /tmp/oci_key

  performance-test:
    runs-on: self-hosted
    needs: deploy-uat
    if: github.ref == 'refs/heads/develop'
    steps:
      - name: Run load tests
        run: |
          docker run --rm --network host \
            grafana/k6 run - <scripts/load-test.js \
            -e UAT_BASE_URL=http://localhost:3001
```

### Deployment Automation Features
- **Automated Testing**: Comprehensive test suite before any deployment
- **Security Scanning**: Container and dependency vulnerability scanning  
- **Multi-Environment**: Separate UAT and production deployment pipelines
- **Health Checks**: Automated verification of deployment success
- **Rollback Capability**: Quick rollback to previous versions on failure
- **Performance Validation**: Load testing on UAT before production deployment

---

## Monitoring & Maintenance

### Monitoring Stack
Deploy lightweight monitoring using `docker-compose.monitoring.yml`:
```yaml
version: '3.9'
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: familycart-prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    container_name: familycart-grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    ports:
      - "3000:3000"

  node-exporter:
    image: prom/node-exporter:latest
    container_name: familycart-node-exporter
    command:
      - '--path.rootfs=/host'
    volumes:
      - '/:/host:ro,rslave'
    ports:
      - "9100:9100"

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: familycart-cadvisor
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    ports:
      - "8080:8080"

volumes:
  prometheus_data:
  grafana_data:
```

### Key Monitoring Metrics
- **System Resources**: CPU, Memory, Disk usage
- **Container Health**: Docker container status and resource consumption  
- **Application Performance**: Response times, error rates, throughput
- **GitHub Runner Status**: Queue depth, build times, success rates
- **UAT Usage**: Concurrent users, feature usage patterns

### Automated Maintenance Tasks
Create `/opt/maintenance/maintenance.sh`:
```bash
#!/bin/bash
# Daily maintenance tasks

# Clean up old Docker images and containers
docker system prune -af --volumes

# Backup UAT database
pg_dump -h localhost -p 5433 -U familycart_uat familycart_uat > \
  /opt/backups/uat-$(date +%Y%m%d).sql

# Rotate logs
journalctl --vacuum-time=7d

# Update system packages
apt update && apt upgrade -y

# Restart services if needed
systemctl status docker || systemctl restart docker
```

### Log Management
- **Centralized Logging**: All container logs forwarded to syslog
- **Log Rotation**: Automatic cleanup of old logs (7-day retention)
- **Log Analysis**: Basic monitoring for errors and performance issues
- **Alert Notifications**: Email notifications for critical issues

---

## Deployment Procedures

### Initial Server Setup
1. **Ubuntu Installation & Hardening**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install required packages
   sudo apt install -y docker.io docker-compose-plugin git curl jq
   
   # Configure Docker
   sudo usermod -aG docker $USER
   sudo systemctl enable docker
   sudo systemctl start docker
   ```

2. **Security Configuration**
   ```bash
   # Configure SSH
   sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
   sudo sed -i 's/#Port 22/Port 2222/' /etc/ssh/sshd_config
   sudo systemctl restart ssh
   
   # Configure firewall
   sudo ufw default deny incoming
   sudo ufw default allow outgoing
   sudo ufw allow 2222/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

3. **GitHub Runners Installation**
   ```bash
   # Create runners directory
   sudo mkdir -p /opt/github-runners
   cd /opt/github-runners
   
   # Download and configure runners (see detailed script)
   sudo bash scripts/setup-github-runners.sh
   ```

4. **UAT Environment Setup**
   ```bash
   # Create UAT directory
   sudo mkdir -p /opt/familycart-uat
   cd /opt/familycart-uat
   
   # Copy configuration files
   sudo cp docker-compose.uat.yml .
   sudo cp .env.uat .env
   
   # Start UAT environment
   sudo docker-compose -f docker-compose.uat.yml up -d
   ```

### Regular Maintenance Procedures

#### Weekly Tasks
- [ ] Review system resource usage and performance metrics
- [ ] Check GitHub runner health and queue status  
- [ ] Verify UAT environment functionality with basic tests
- [ ] Review security logs for any suspicious activity
- [ ] Update system packages and container images

#### Monthly Tasks
- [ ] Full system backup including configurations and data
- [ ] Performance optimization based on monitoring data
- [ ] Security audit of system configuration
- [ ] Review and update documentation
- [ ] Capacity planning assessment for future growth

#### Emergency Procedures
- [ ] **Runner Failure**: Restart individual runners or full runner service
- [ ] **UAT Downtime**: Quick rollback to previous stable deployment
- [ ] **Security Incident**: Isolate server, review logs, update configurations
- [ ] **Resource Exhaustion**: Scale resources or optimize configurations

### Backup and Recovery
- **Automated Backups**: Daily backup of UAT database and configurations
- **Backup Retention**: 7 days local, 30 days remote (optional cloud storage)
- **Recovery Testing**: Monthly recovery drills to ensure backup integrity
- **Disaster Recovery**: Complete server rebuild procedures documented

---

## Performance Optimization

### Resource Optimization Strategies
- **Container Resource Limits**: Prevent resource exhaustion with explicit limits
- **Docker Layer Caching**: Optimize build times with effective layer caching
- **Image Optimization**: Multi-stage builds and minimal base images
- **Network Optimization**: Local Docker registry cache for faster pulls

### Capacity Planning
- **User Load Testing**: Regular load testing to validate 50-user capacity
- **Resource Monitoring**: Track resource usage trends for proactive scaling
- **Performance Benchmarking**: Establish baselines for response times and throughput
- **Growth Planning**: Define scaling strategies for increased user load

---

## Cost Analysis

### Infrastructure Costs
| Component | Monthly Cost | Annual Cost |
|-----------|-------------|-------------|
| Server Hardware | $0 (owned) | $0 |
| Internet Bandwidth | $0 (existing) | $0 |
| Power Consumption | ~$50 | ~$600 |
| **Total Self-Hosted** | **~$50** | **~$600** |

### Cost Comparison vs Cloud
- **Self-Hosted**: ~$50/month (power only)
- **Equivalent Cloud**: ~$300-500/month (8-core, 32GB RAM)
- **Annual Savings**: ~$3,000-5,400 compared to cloud hosting

### ROI Analysis
- **Investment**: Server hardware (one-time cost)
- **Operational Savings**: $3,000+ annually vs cloud
- **Additional Benefits**: Full control, no vendor lock-in, learning opportunities

---

This deployment strategy provides a robust, secure, and cost-effective foundation for FamilyCart's development and testing infrastructure while maintaining the flexibility to scale to cloud-based production deployment.

---
*Document Version: 1.0*  
*Last Updated: January 2025*  
*Author: FamilyCart DevOps Automation*