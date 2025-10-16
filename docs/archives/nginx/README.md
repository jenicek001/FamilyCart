# Archived Nginx Configuration Files

**Date Archived:** October 16, 2025  
**Reason:** Duplicate/extended configurations superseded by modular setup

---

## Files in this directory

### `nginx-uat-extended.conf`
- **Date Archived:** October 16, 2025
- **Original Location:** Root directory
- **Reason:** Duplicate/extended nginx configuration file
- **Superseded By:**
  - `nginx/uat.conf` - Active UAT configuration
  - `nginx/multi-service.conf` - Multi-service setup
  - `deploy/nginx/` - Deployment configurations
- **Status:** Not referenced in any active deployment

**Original Purpose:** Extended nginx configuration for UAT environment testing

---

## ✅ Active Nginx Configurations

### Root `/nginx/` Directory
- `nginx/uat.conf` (6,483 bytes) - Main UAT configuration
- `nginx/multi-service.conf` (15,728 bytes) - Multi-service proxy setup
- `nginx/nginx.conf` - Base nginx configuration
- `nginx/conf.d/` - Modular configuration includes
- `nginx/sites-available/`, `nginx/sites-enabled/` - Site configurations
- `nginx/ssl/` - SSL certificates and configuration

### Deployment `/deploy/nginx/` Directory
- `deploy/nginx/uat.conf` - UAT deployment configuration
- `deploy/nginx/nginx.conf` - Deployment base config
- `deploy/nginx/conf.d/` - Deployment modules

---

## 📝 Important Notes

### Nginx Repository Separation

According to `NGINX_SEPARATION_PROPOSAL.md`, nginx is planned to be in a **separate repository** on this machine. The current structure supports:

1. **Development configs** - `/nginx/` in this repo
2. **Deployment configs** - `/deploy/nginx/` for deployment templates
3. **Active nginx** - Separate repo on this machine (via Cloudflare proxy)

### UAT Environment

- **UAT is hosted on this machine**
- **Nginx runs as reverse proxy** (separate from this repo)
- **Cloudflare proxy** sits in front of nginx
- **Monitoring** via `/monitoring/` directory in this repo

---

## 🔄 Migration Notes

If you need to reference this configuration:

```bash
# View archived config
cat docs/archives/nginx/nginx-uat-extended.conf

# Compare with active config
diff docs/archives/nginx/nginx-uat-extended.conf nginx/uat.conf

# Check deployment guides
cat docs/deployment/NGINX_SEPARATION_PROPOSAL.md
cat docs/deployment/DEPLOY_SELF_HOSTED_UAT.md
```

---

## 🔍 Related Documentation

- `NGINX_SEPARATION_PROPOSAL.md` - Nginx architecture and separation strategy
- `DEPLOY_SELF_HOSTED_UAT.md` - UAT deployment guide
- `CLOUDFLARE_MONITORING_SETUP.md` - Cloudflare proxy configuration
- `deploy/nginx/` - Deployment configuration templates
