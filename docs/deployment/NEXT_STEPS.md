# Production Deployment - Next Steps

## ✅ Completed Tasks

1. **Infrastructure Setup**
   - ✅ OCI VCN created (familycart-vcn, 10.0.0.0/16)
   - ✅ Public subnet (10.0.1.0/24)
   - ✅ Internet Gateway and Route Tables
   - ✅ Security Lists (SSH, HTTP, HTTPS, PostgreSQL, Redis, ICMP)

2. **VM1: Database Server** (141.147.22.49 / 10.0.1.191)
   - ✅ Ubuntu 24.04 Minimal provisioned
   - ✅ Docker 28.5.2 installed
   - ✅ PostgreSQL 15.14 running (HEALTHY)
   - ✅ Redis 8.2.3 running (HEALTHY)
   - ✅ Automated backups configured (daily 2 AM, 7-day retention)
   - ✅ Firewall configured (nftables + iptables)
   - ✅ **Database connectivity fixed** (Docker NAT issue resolved)

3. **VM2: Application Server** (158.180.30.112 / 10.0.1.145)
   - ✅ Ubuntu 24.04 Minimal provisioned
   - ✅ Docker 28.5.2 installed
   - ✅ Nginx 1.24.0 installed and configured
   - ✅ Cloudflare IP allowlist firewall configured
   - ✅ Environment variables configured (.env.app)
   - ✅ **Can connect to VM1 databases** (PostgreSQL & Redis)

4. **Security & Access**
   - ✅ SSH key pair generated (familycart_oci, 4096-bit RSA)
   - ✅ Strong database passwords generated
   - ✅ Firewalls configured on both VMs

## 🔨 Ready to Deploy

### Task 1: Update VM2 Environment Variables

Need to add GitHub Personal Access Token:

```bash
# On your local machine
ssh -i ~/.ssh/familycart_oci ubuntu@158.180.30.112

# Edit environment file
sudo nano /opt/familycart-app/.env.app

# Add this line (replace with your actual PAT):
GITHUB_TOKEN=ghp_your_personal_access_token_here

# Save (Ctrl+X, Y, Enter)
```

**How to create GitHub PAT**:
1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Name: `FamilyCart Production Deployment`
4. Expiration: 90 days (or custom)
5. Scopes: `read:packages` (to pull Docker images from ghcr.io)
6. Click "Generate token"
7. Copy the token (ghp_...)

### Task 2: Deploy Application on VM2

Once you have the GitHub PAT:

```bash
# On VM2
cd /opt/familycart-app

# Login to GitHub Container Registry
echo "YOUR_GITHUB_PAT" | docker login ghcr.io -u jenicek001 --password-stdin

# Pull latest images
docker compose pull

# Start services
docker compose up -d

# Verify containers are running
docker compose ps

# Check logs
docker compose logs -f --tail=100

# Test backend health endpoint
curl http://localhost:8000/health
# Expected: {"status":"healthy","database":"connected","redis":"connected"}

# Test frontend
curl http://localhost:3000
# Expected: HTML content
```

### Task 3: Configure Cloudflare DNS

1. **Add domain to Cloudflare**:
   - Go to Cloudflare dashboard → Add site
   - Enter your domain (e.g., `familycart.com`)
   - Select Free plan
   - Update nameservers at your domain registrar

2. **Create DNS records**:
   - Type: `A`, Name: `@`, IPv4: `158.180.30.112`, Proxy: ✅ Proxied (orange cloud)
   - Type: `A`, Name: `www`, IPv4: `158.180.30.112`, Proxy: ✅ Proxied (orange cloud)

3. **Verify DNS propagation**:
   ```bash
   nslookup familycart.com
   dig familycart.com
   ```

### Task 4: Generate Cloudflare Origin Certificate

1. **In Cloudflare Dashboard**:
   - SSL/TLS → Origin Server → Create Certificate
   - Private key type: RSA (2048)
   - Hostnames: `familycart.com, *.familycart.com`
   - Validity: 15 years
   - Click "Create"

2. **Install certificate on VM2**:
   ```bash
   # On VM2
   sudo mkdir -p /etc/nginx/ssl
   
   # Create certificate file
   sudo nano /etc/nginx/ssl/familycart.com.pem
   # Paste the Origin Certificate (everything including BEGIN/END lines)
   
   # Create private key file
   sudo nano /etc/nginx/ssl/familycart.com.key
   # Paste the Private Key (everything including BEGIN/END lines)
   
   # Set secure permissions
   sudo chmod 600 /etc/nginx/ssl/familycart.com.key
   sudo chmod 644 /etc/nginx/ssl/familycart.com.pem
   sudo chown root:root /etc/nginx/ssl/*
   ```

3. **Configure Cloudflare SSL mode**:
   - Go to SSL/TLS → Overview
   - Set mode: **Full (strict)** (not "Flexible"!)
   - Enable "Always Use HTTPS"
   - Enable "Automatic HTTPS Rewrites"

### Task 5: Start Nginx

```bash
# On VM2
sudo systemctl restart nginx
sudo systemctl status nginx

# Test Nginx configuration
sudo nginx -t

# Check if Nginx is listening
sudo netstat -tlnp | grep nginx
# Expected:
# tcp 0 0 0.0.0.0:80 0.0.0.0:* LISTEN 12345/nginx
# tcp 0 0 0.0.0.0:443 0.0.0.0:* LISTEN 12345/nginx

# Test endpoints
curl https://familycart.com/health
curl https://familycart.com
```

### Task 6: Configure GitHub Actions Secrets

Add these secrets to your GitHub repository:

1. Go to GitHub: https://github.com/jenicek001/FamilyCart
2. Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

```
PRODUCTION_SSH_KEY
===================
(Paste contents of ~/.ssh/familycart_oci - the PRIVATE key)

PRODUCTION_HOST
===============
158.180.30.112

PRODUCTION_USER
===============
ubuntu

PRODUCTION_URL
==============
https://familycart.com

SENTRY_AUTH_TOKEN
=================
(If using Sentry for error tracking - optional for now)
```

### Task 7: Test Production Deployment Workflow

```bash
# On your local machine
cd ~/GitHub/FamilyCart

# Make a small change to trigger deployment
git checkout main
git pull
echo "# Production deployment test" >> CHANGELOG.md
git add CHANGELOG.md
git commit -m "test: Trigger production deployment"
git push origin main
```

**Monitor GitHub Actions**:
1. Go to https://github.com/jenicek001/FamilyCart/actions
2. Watch the workflow:
   - ✅ Test (71 tests)
   - ✅ Build images
   - ✅ Push to ghcr.io
   - ✅ Deploy to UAT (automatic)
   - ⏸️ Wait for approval
   - Click "Review deployments" → Check "production" → "Approve and deploy"
   - ✅ Deploy to Production

### Task 8: Smoke Test Production

```bash
# Health check
curl https://familycart.com/health

# API test
curl https://familycart.com/api/v1/health

# Frontend test
curl https://familycart.com

# Check SSL certificate
openssl s_client -connect familycart.com:443 -servername familycart.com | grep "Verify return code"
# Expected: Verify return code: 0 (ok)

# Performance test
curl -o /dev/null -s -w "Time: %{time_total}s\nSize: %{size_download} bytes\n" https://familycart.com
```

## 📊 Current Infrastructure Summary

### VM1: Database Server
- **Public IP**: 141.147.22.49
- **Private IP**: 10.0.1.191
- **Services**: PostgreSQL 15.14, Redis 8.2.3
- **Status**: ✅ OPERATIONAL
- **Backups**: Daily at 2 AM UTC, 7-day retention, stored in `/var/backups/familycart`
- **Monitoring**: Docker health checks, systemd services

### VM2: Application Server
- **Public IP**: 158.180.30.112
- **Private IP**: 10.0.1.145
- **Services**: Backend (FastAPI), Frontend (React), Nginx
- **Status**: ⏳ Ready to deploy (waiting for GitHub PAT)
- **Firewall**: Cloudflare IPs only for HTTP/HTTPS
- **Reverse Proxy**: Nginx with SSL termination

### Network Security
- **Firewall**: nftables on both VMs (policy DROP)
- **SSH**: Key-based authentication only (password auth disabled)
- **Database**: Accessible only from VCN (10.0.0.0/16)
- **HTTP/HTTPS**: Accessible only from Cloudflare IPs
- **SSL**: Cloudflare Origin Certificate (Full Strict mode)

### Credentials & Secrets
- **SSH Key**: `~/.ssh/familycart_oci` (4096-bit RSA)
- **PostgreSQL Password**: Stored in `/opt/familycart-db/.env.db` (VM1)
- **Redis Password**: Stored in `/opt/familycart-db/.env.db` (VM1)
- **Application Secrets**: Stored in `/opt/familycart-app/.env.app` (VM2)

## 🎯 Priority Order

1. **HIGH**: Add GitHub PAT to VM2 `.env.app` (blocks everything else)
2. **HIGH**: Deploy application containers on VM2
3. **MEDIUM**: Configure Cloudflare DNS
4. **MEDIUM**: Generate and install Cloudflare Origin Certificate
5. **MEDIUM**: Start Nginx
6. **LOW**: Configure GitHub Actions secrets
7. **LOW**: Test production deployment workflow
8. **LOW**: Smoke test and monitoring setup

## ⚠️ Important Notes

- **Database connectivity is working**: PostgreSQL and Redis are accessible from VM2
- **Docker images are ready**: Already built and pushed to ghcr.io
- **Infrastructure is secure**: Firewalls configured, SSH key-based auth only
- **Manual approval required**: Production deployments require manual approval in GitHub Actions
- **No public database access**: PostgreSQL/Redis only accessible from VCN (not Internet)
- **Cloudflare protection**: All HTTP/HTTPS traffic goes through Cloudflare (DDoS protection, SSL)

## 📚 Documentation

- [Production Deployment Guide](./PRODUCTION_DEPLOYMENT_GUIDE.md)
- [VM Database Connectivity Fix](./VM_DATABASE_CONNECTIVITY_FIX.md)
- [Connection Fix Documentation](./CONNECTION_FIX_NEEDED.md) (historical)

## 🎉 Success Criteria

You'll know everything is working when:

1. ✅ `curl https://familycart.com/health` returns 200 OK with healthy status
2. ✅ Frontend loads in browser at https://familycart.com
3. ✅ SSL certificate is valid (green lock icon)
4. ✅ GitHub Actions deployment succeeds
5. ✅ Docker containers running on VM2: `docker compose ps` shows "healthy"
6. ✅ Logs show no errors: `docker compose logs --tail=100`

---

**Ready to proceed?** Start with Task 1 (add GitHub PAT) when you're ready! 🚀
