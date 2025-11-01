# NGINX Reverse Proxy Repository Separation - Proposal

**Date:** October 2, 2025  
**Author:** AI IDE Assistant  
**Status:** Proposal for Review

## 📋 Executive Summary

This document proposes separating the NGINX reverse proxy configuration into an independent GitHub repository to enable:
- **Independent deployment and updates** without affecting application repositories
- **Multi-service hosting** across different domains (FamilyCart, Home Assistant, Grafana, etc.)
- **Centralized SSL/TLS certificate management** for all services
- **Simplified maintenance** with clear separation of concerns
- **Always-on infrastructure** independent of application deployments

## 🎯 Current Situation

### Existing Setup at `/opt/familycart-uat-repo`
The current nginx configuration is embedded within the FamilyCart UAT repository and serves multiple services:

1. **FamilyCart UAT Application** (`uat.familycart.app`)
   - Frontend (Next.js) on port 3000
   - Backend (FastAPI) on port 8000
   - WebSocket support for real-time updates
   - Full SSL/TLS with CloudFlare Origin Certificates

2. **Home Assistant** (`homeassistant.connectedhome.cz`)
   - Proxy to local IP: `192.168.3.30:8123`
   - WebSocket support for real-time home automation
   - Separate domain with own SSL certificates

3. **Grafana Monitoring** (`grafana.connectedhome.cz`)
   - Independent monitoring service
   - Separate domain with own SSL certificates
   - Rate limiting configured

### Current Directory Structure
```
/opt/familycart-uat-repo/
├── nginx/
│   ├── nginx.conf                    # Main configuration
│   ├── conf.d/                       # Common snippets
│   │   ├── ssl-common.conf           # SSL/TLS settings
│   │   ├── upstreams.conf            # Backend definitions
│   │   ├── rate-limiting.conf        # Rate limits
│   │   └── cloudflare-realip.conf    # CF real IP detection
│   ├── sites-available/              # All site configs
│   │   ├── familycart-uat            # FamilyCart UAT
│   │   ├── homeassistant             # Home Assistant
│   │   ├── grafana                   # Grafana monitoring
│   │   └── default                   # Default/catch-all
│   ├── sites-enabled/                # Enabled sites (symlinks)
│   │   ├── familycart-uat -> ../sites-available/familycart-uat
│   │   └── homeassistant -> ../sites-available/homeassistant
│   └── ssl/                          # SSL certificates by domain
│       ├── familycart.app/
│       │   ├── uat.familycart.app.crt
│       │   └── uat.familycart.app.key
│       └── connectedhome.cz/
│           ├── connectedhome.cz.crt
│           └── connectedhome.cz.key
├── docker-compose.uat.yml            # Contains uat-proxy service
└── scripts/
    ├── setup-cloudflare-certificates.sh
    └── test-nginx-config.sh
```

### Issues with Current Approach
1. **Tight Coupling**: Nginx configuration is tied to FamilyCart application repository
2. **Deployment Dependencies**: Updating FamilyCart code can affect nginx proxy
3. **Multi-Service Complexity**: Home Assistant and Grafana configs mixed with FamilyCart
4. **Branch Management**: Nginx changes require coordination with app development branches
5. **Independent Updates**: Cannot update nginx without pulling entire application repo

## 🏗️ Proposed Solution

### Create Independent Repository: `familycart-nginx-proxy`

Create a new repository specifically for nginx reverse proxy with the following structure:

```
familycart-nginx-proxy/
├── README.md
├── .gitignore
├── .env.example
├── docker-compose.yml              # Standalone nginx deployment
├── nginx/
│   ├── nginx.conf                  # Main configuration
│   ├── mime.types
│   ├── fastcgi_params
│   ├── uwsgi_params
│   ├── conf.d/                     # Common configuration snippets
│   │   ├── ssl-common.conf         # SSL/TLS best practices
│   │   ├── upstreams.conf          # Backend server definitions
│   │   ├── rate-limiting.conf      # Rate limiting rules
│   │   └── cloudflare-realip.conf  # CloudFlare real IP detection
│   ├── sites-available/            # All site configurations
│   │   ├── familycart-uat
│   │   ├── familycart-production   # For future production
│   │   ├── homeassistant
│   │   ├── grafana
│   │   └── default
│   ├── sites-enabled/              # Active sites (symlinks)
│   └── ssl/                        # SSL certificates
│       ├── familycart.app/
│       ├── connectedhome.cz/
│       └── .gitkeep                # Track directory, ignore certs
├── scripts/
│   ├── setup-certificates.sh       # Certificate installation
│   ├── test-config.sh              # Nginx config testing
│   ├── reload-nginx.sh             # Safe reload
│   ├── enable-site.sh              # Enable site helper
│   └── disable-site.sh             # Disable site helper
├── logs/
│   └── .gitkeep                    # Track directory, ignore logs
├── docs/
│   ├── DEPLOYMENT.md               # Deployment procedures
│   ├── SSL_MANAGEMENT.md           # SSL certificate management
│   ├── ADDING_SERVICES.md          # How to add new services
│   └── TROUBLESHOOTING.md          # Common issues and fixes
└── monitoring/
    ├── prometheus-targets.yml      # For nginx exporter
    └── grafana-dashboard.json      # Nginx monitoring dashboard
```

## 📝 Implementation Plan

### Phase 1: Repository Setup (Day 1)

1. **Create New Repository**
   ```bash
   # On GitHub
   - Create new repository: jenicek001/familycart-nginx-proxy
   - Description: "Standalone NGINX reverse proxy for FamilyCart and ConnectedHome services"
   - Visibility: Private
   - Initialize with README
   ```

2. **Clone and Initialize**
   ```bash
   cd /opt
   sudo git clone https://github.com/jenicek001/familycart-nginx-proxy.git
   sudo chown -R honzik:honzik familycart-nginx-proxy
   cd familycart-nginx-proxy
   ```

3. **Copy Existing Configuration**
   ```bash
   # Copy nginx configuration
   cp -r /opt/familycart-uat-repo/nginx/* ./nginx/
   
   # Copy scripts
   cp /opt/familycart-uat-repo/setup-cloudflare-certificates.sh ./scripts/setup-certificates.sh
   cp /opt/familycart-uat-repo/test-nginx-config.sh ./scripts/test-config.sh
   
   # Copy SSL certificates (will be ignored by git)
   cp -r /opt/familycart-uat-repo/nginx/ssl/* ./nginx/ssl/
   ```

4. **Create Standalone docker-compose.yml**
   ```yaml
   version: '3.9'
   
   # Standalone NGINX Reverse Proxy
   # Serves multiple services across different domains
   
   services:
     nginx-proxy:
       image: nginx:alpine
       container_name: nginx-reverse-proxy
       volumes:
         - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
         - ./nginx/sites-available:/etc/nginx/sites-available:ro
         - ./nginx/sites-enabled:/etc/nginx/sites-enabled:ro
         - ./nginx/conf.d:/etc/nginx/conf.d:ro
         - ./nginx/ssl:/etc/nginx/ssl:ro
         - ./logs:/var/log/nginx
       ports:
         - "80:80"
         - "443:443"
       networks:
         - proxy-network
         - familycart-uat-network
         - monitoring-network
       healthcheck:
         test: ["CMD", "nginx", "-t"]
         interval: 30s
         timeout: 10s
         retries: 3
       restart: always
       deploy:
         resources:
           limits:
             memory: 512M
             cpus: '0.5'
   
   networks:
     proxy-network:
       name: nginx-proxy-network
       driver: bridge
     
     # Connect to FamilyCart UAT network
     familycart-uat-network:
       external: true
       name: familycart-uat-network
     
     # Connect to monitoring network
     monitoring-network:
       external: true
       name: familycart-monitoring-network
   ```

5. **Create .gitignore**
   ```
   # SSL Certificates (sensitive)
   nginx/ssl/**/*.crt
   nginx/ssl/**/*.key
   nginx/ssl/**/*.pem
   !nginx/ssl/.gitkeep
   
   # Logs
   logs/**/*
   !logs/.gitkeep
   
   # Environment files
   .env
   .env.local
   
   # Backup files
   *.bak
   *.backup
   *~
   
   # OS files
   .DS_Store
   Thumbs.db
   
   # Editor files
   .vscode/
   .idea/
   *.swp
   *.swo
   ```

6. **Create README.md**
   - Document purpose and architecture
   - List all services being proxied
   - Include quick start guide
   - Add maintenance procedures

### Phase 2: Update Upstreams Configuration (Day 1-2)

1. **Modify nginx/conf.d/upstreams.conf**
   Update to support dynamic upstream resolution:
   
   ```nginx
   # FamilyCart UAT Services
   upstream familycart_backend {
       server uat-backend:8000 max_fails=3 fail_timeout=30s;
       keepalive 32;
       keepalive_requests 100;
       keepalive_timeout 60s;
   }
   
   upstream familycart_frontend {
       server uat-frontend:3000 max_fails=3 fail_timeout=30s;
       keepalive 32;
       keepalive_requests 100;
       keepalive_timeout 60s;
   }
   
   # Home Assistant (static IP)
   upstream homeassistant_service {
       server 192.168.3.30:8123 max_fails=3 fail_timeout=30s;
       keepalive 16;
   }
   
   # Grafana Monitoring
   upstream grafana_service {
       server familycart-monitoring-grafana:3000 max_fails=3 fail_timeout=30s;
       keepalive 16;
   }
   
   # Optional: Prometheus for metrics
   upstream prometheus_service {
       server familycart-monitoring-prometheus:9090 max_fails=3 fail_timeout=30s;
       keepalive 16;
   }
   ```

2. **Add DNS Resolver for Dynamic Resolution**
   Update nginx.conf to support dynamic upstream resolution:
   
   ```nginx
   http {
       # Add resolver for dynamic DNS (Docker internal DNS)
       resolver 127.0.0.11 valid=30s ipv6=off;
       resolver_timeout 10s;
       
       # ... rest of configuration
   }
   ```

### Phase 3: Testing and Validation (Day 2)

1. **Test Configuration Syntax**
   ```bash
   cd /opt/familycart-nginx-proxy
   ./scripts/test-config.sh
   ```

2. **Start Nginx Independently**
   ```bash
   docker compose up -d
   ```

3. **Verify Service Connectivity**
   ```bash
   # Test FamilyCart UAT
   curl -k https://uat.familycart.app/health
   
   # Test Home Assistant
   curl -k https://homeassistant.connectedhome.cz/health
   
   # Test Grafana
   curl -k https://grafana.connectedhome.cz/health
   ```

4. **Monitor Logs**
   ```bash
   docker compose logs -f nginx-proxy
   tail -f logs/nginx/error.log
   ```

### Phase 4: Update FamilyCart Repository (Day 2-3)

1. **Remove Nginx from docker-compose.uat.yml**
   Remove the `uat-proxy` service definition

2. **Update Backend Environment Variables**
   Ensure backend knows about external proxy:
   ```yaml
   uat-backend:
     environment:
       - PROXY_HEADERS_MODE=enabled
       - BEHIND_PROXY=true
   ```

3. **Update Network Configuration**
   Ensure services can communicate with external nginx:
   ```yaml
   networks:
     uat-network:
       external: false
       name: familycart-uat-network
   ```

4. **Test Application Without Embedded Nginx**
   ```bash
   cd /opt/familycart-uat-repo
   docker compose -f docker-compose.uat.yml up -d
   ```

### Phase 5: Documentation and Automation (Day 3-4)

1. **Create Comprehensive Documentation**
   - DEPLOYMENT.md: Full deployment procedures
   - SSL_MANAGEMENT.md: Certificate installation and renewal
   - ADDING_SERVICES.md: How to add new services
   - TROUBLESHOOTING.md: Common issues and solutions

2. **Create Helper Scripts**
   ```bash
   # scripts/enable-site.sh
   #!/bin/bash
   SITE=$1
   ln -s ../sites-available/$SITE nginx/sites-enabled/
   docker compose exec nginx-proxy nginx -s reload
   
   # scripts/disable-site.sh
   #!/bin/bash
   SITE=$1
   rm nginx/sites-enabled/$SITE
   docker compose exec nginx-proxy nginx -s reload
   
   # scripts/reload-nginx.sh
   #!/bin/bash
   docker compose exec nginx-proxy nginx -t && \
   docker compose exec nginx-proxy nginx -s reload
   ```

3. **Set Up Monitoring**
   - Add nginx-prometheus-exporter
   - Create Grafana dashboard for nginx metrics
   - Set up alerts for nginx downtime

### Phase 6: Production Deployment (Day 4-5)

1. **Deploy to /opt**
   ```bash
   cd /opt/familycart-nginx-proxy
   git pull origin main
   docker compose up -d
   ```

2. **Update Systemd for Auto-Start**
   Create `/etc/systemd/system/nginx-proxy.service`:
   ```ini
   [Unit]
   Description=NGINX Reverse Proxy
   Requires=docker.service
   After=docker.service
   
   [Service]
   Type=oneshot
   RemainAfterExit=yes
   WorkingDirectory=/opt/familycart-nginx-proxy
   ExecStart=/usr/bin/docker compose up -d
   ExecStop=/usr/bin/docker compose down
   
   [Install]
   WantedBy=multi-user.target
   ```
   
   Enable service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable nginx-proxy.service
   sudo systemctl start nginx-proxy.service
   ```

3. **Verify All Services**
   - Test all domains (uat.familycart.app, homeassistant.connectedhome.cz, grafana.connectedhome.cz)
   - Verify SSL/TLS certificates
   - Check WebSocket connections
   - Monitor logs for errors

## ✅ Benefits

### 1. **Separation of Concerns**
- Nginx configuration independent of application code
- Clear responsibility boundaries
- Easier to understand and maintain

### 2. **Independent Deployment**
- Update nginx without touching application
- Update application without touching nginx
- Reduced deployment risk

### 3. **Multi-Service Support**
- Easy to add new services (e.g., production FamilyCart, other apps)
- Centralized SSL certificate management
- Consistent security policies across all services

### 4. **Always-On Infrastructure**
- Nginx runs independently
- Application can be redeployed without proxy downtime
- Better uptime and reliability

### 5. **Simplified Maintenance**
- Single place for all proxy configuration
- Easy to enable/disable services
- Clear documentation and procedures

### 6. **Better Security**
- Centralized SSL/TLS management
- Consistent security headers
- Rate limiting across all services
- CloudFlare integration in one place

### 7. **Scalability**
- Easy to add new domains
- Support for multiple environments (UAT, production, staging)
- Can add load balancing across multiple backend instances

## 🔒 Security Considerations

### SSL Certificate Management
1. **Do NOT commit certificates to git**
   - Use `.gitignore` to exclude all certificate files
   - Document certificate installation process
   - Consider using secret management (e.g., Docker secrets, Vault)

2. **Certificate Rotation**
   - Document renewal process
   - Set up expiry monitoring
   - Automate renewal where possible

3. **Access Control**
   - Restrict access to `/opt/familycart-nginx-proxy` directory
   - Use appropriate file permissions (600 for keys, 644 for certs)
   - Limit who can deploy changes

### Network Security
1. **Network Isolation**
   - Use Docker networks to isolate services
   - Only expose necessary ports (80, 443)
   - Internal services communicate via Docker networks

2. **Rate Limiting**
   - Maintain rate limiting configuration
   - Monitor for abuse
   - Adjust limits based on usage patterns

## 📊 Migration Checklist

- [ ] Create new repository `familycart-nginx-proxy`
- [ ] Copy existing nginx configuration
- [ ] Create standalone docker-compose.yml
- [ ] Set up .gitignore (exclude certificates)
- [ ] Create comprehensive README.md
- [ ] Test nginx independently
- [ ] Update upstreams.conf for all services
- [ ] Verify connectivity to all backend services
- [ ] Remove nginx from docker-compose.uat.yml
- [ ] Test FamilyCart without embedded nginx
- [ ] Deploy to production (/opt/familycart-nginx-proxy)
- [ ] Set up systemd service for auto-start
- [ ] Create helper scripts (enable/disable sites, reload)
- [ ] Document SSL certificate management
- [ ] Set up monitoring and alerts
- [ ] Update PLANNING.md in FamilyCart repo
- [ ] Create migration summary document

## 🚀 Next Steps

1. **Review this proposal** with stakeholders
2. **Create the new repository** on GitHub
3. **Follow Phase 1-2** to set up initial structure
4. **Test thoroughly** in isolation before migrating
5. **Update FamilyCart repository** to use external nginx
6. **Deploy to production** with proper monitoring
7. **Document the migration** for future reference

## 📚 References

- [NGINX Official Documentation](https://nginx.org/en/docs/)
- [Docker Networking](https://docs.docker.com/network/)
- [CloudFlare Origin Certificates](https://developers.cloudflare.com/ssl/origin-configuration/origin-ca/)
- Current implementation: `/opt/familycart-uat-repo/MODULAR_NGINX_DEPLOYMENT_GUIDE.md`

---

**End of Proposal**
