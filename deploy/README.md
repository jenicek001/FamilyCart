# FamilyCart Deployment Configuration

This directory contains all the configuration files and scripts needed to deploy FamilyCart on a self-hosted Ubuntu server with GitHub runners and UAT environment.

## Quick Start

1. **Server Setup** (run once):
   ```bash
   sudo ./scripts/server-setup.sh
   ```

2. **GitHub Runners Setup**:
   ```bash
   sudo ./scripts/setup-github-runners.sh
   # Then configure with your GitHub token
   ```

3. **UAT Environment Deploy**:
   ```bash
   cd /opt/familycart-uat
   cp docker-compose.uat.yml .
   cp .env.uat.example .env
   # Edit .env with your configuration
   docker-compose -f docker-compose.uat.yml up -d
   ```

## Directory Structure

```
deploy/
├── nginx/                  # Nginx reverse proxy configuration
│   └── uat.conf           # UAT environment nginx config
├── monitoring/            # Monitoring and metrics configuration
│   └── prometheus-uat.yml # Prometheus config for UAT
├── scripts/               # Setup and maintenance scripts
│   ├── server-setup.sh    # Complete Ubuntu server setup
│   ├── setup-github-runners.sh # GitHub runners installation
│   └── load-test.js       # k6 load testing script
└── github-runners/        # GitHub runners Docker configuration
    ├── Dockerfile         # Custom runner image
    └── entrypoint.sh      # Runner startup script
```

## Main Configuration Files

### UAT Environment
- `docker-compose.uat.yml` - UAT services configuration
- `.env.uat.example` - Environment variables template

### GitHub Runners  
- `docker-compose.runners.yml` - Self-hosted runners setup

### Monitoring
- Prometheus configuration for metrics collection
- System monitoring scripts for health checks

## Documentation

- **Main Guide**: `DEPLOY_SELF_HOSTED_UAT.md` - Complete deployment strategy
- **OCI Production**: `DEPLOY_OCI_FREE_TIER.md` - Production environment setup
- **CI/CD Pipeline**: `.github/workflows/ci.yml` - Automated build and deployment

## Prerequisites

- Ubuntu 24.04 LTS server
- 32+ GB RAM, 8+ CPU cores
- 500+ GB SSD storage
- 100 Mbps internet connection
- Domain name for SSL certificates

## Support

For detailed instructions, troubleshooting, and architecture details, see:
- `DEPLOY_SELF_HOSTED_UAT.md` 
- `TASKS.md` (Sprint 12 section)
- Individual script comments and help text