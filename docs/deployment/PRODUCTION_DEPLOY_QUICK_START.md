# Quick Start: Deploy FamilyCart Production

This is a condensed step-by-step guide to get FamilyCart running in production.

## Prerequisites
- ✅ Cloudflare Origin Certificates exist on local machine (from UAT setup)
- ✅ Backend and Frontend containers running on VM2
- ✅ DNS domains registered: familycart.app, familycart.cz, familycart.eu, nakoupit.app, nakoupit.com

---

## Step 1: Copy Certificates to VM2 (from local machine)

```bash
# On your LOCAL machine (where UAT runs)
scp -i ~/.ssh/familycart_oci /etc/nginx/ssl/cloudflare/origin-cert.pem \
    ubuntu@158.180.30.112:/tmp/

scp -i ~/.ssh/familycart_oci /etc/nginx/ssl/cloudflare/origin-key.pem \
    ubuntu@158.180.30.112:/tmp/
```

---

## Step 2: Install Nginx Configuration on VM2

```bash
# SSH to VM2
ssh -i ~/.ssh/familycart_oci ubuntu@158.180.30.112

# Pull latest code (includes new Nginx config)
cd /opt/familycart-app
sudo git pull

# OR if repo doesn't exist:
# sudo git clone https://github.com/jenicek001/FamilyCart.git /opt/familycart-app

# Run setup script
sudo bash /opt/familycart-app/scripts/setup-production-nginx.sh
```

---

## Step 3: Update Backend Environment

```bash
# Still on VM2
cd /opt/familycart-app

# Update .env.app
sudo nano .env.app
```

Change these lines:
```bash
# FROM:
CORS_ORIGINS=["https://familycart.com","https://www.familycart.com"]
NEXT_PUBLIC_API_URL=https://familycart.com/api

# TO:
CORS_ORIGINS=["https://familycart.app","https://www.familycart.app"]
NEXT_PUBLIC_API_URL=https://familycart.app/api
```

Save and restart containers:
```bash
docker compose restart backend frontend
```

---

## Step 4: Configure Cloudflare DNS

### A. familycart.app (primary domain)

1. **Cloudflare Dashboard** → Select `familycart.app`
2. **DNS > Records** → Add/Update:
   - Type: `A`, Name: `@`, Content: `158.180.30.112`, **Proxied ✅**
   - Type: `A`, Name: `www`, Content: `158.180.30.112`, **Proxied ✅**

### B. Redirect domains (familycart.cz, .eu, nakoupit.app, .com)

For **each redirect domain**:

1. **Add domain to Cloudflare** (if not already added)
2. **Update nameservers** at domain registrar
3. **Wait for activation**
4. **Configure DNS**:
   - Type: `A`, Name: `@`, Content: `158.180.30.112`, **Proxied ✅**
   - Type: `A`, Name: `www`, Content: `158.180.30.112`, **Proxied ✅**
5. **Create Redirect Rule**:
   - Go to: **Rules > Redirect Rules**
   - Click: **Create rule**
   - Name: `Redirect to familycart.app`
   - When: `All incoming requests`
   - Then: **Dynamic redirect**
     - Expression: `concat("https://familycart.app", http.request.uri.path)`
     - Status: `301`

---

## Step 5: SSL/TLS Settings (for all domains)

For **each domain**:

1. **SSL/TLS > Overview** → Set to: `Full (strict)`
2. **SSL/TLS > Edge Certificates** → Enable:
   - ✅ Always Use HTTPS
   - ✅ Automatic HTTPS Rewrites
   - ✅ HSTS (Max Age: 12 months, include subdomains, preload)

---

## Step 6: Verify Everything Works

```bash
# Test from local machine

# Check DNS
dig familycart.app +short

# Test HTTPS
curl -I https://familycart.app/health
# Expected: 200 OK

curl -I https://www.familycart.app/
# Expected: 200 OK

# Test redirects
curl -I https://familycart.cz/
# Expected: 301 redirect to https://familycart.app/

curl -I https://nakoupit.app/
# Expected: 301 redirect to https://familycart.app/
```

---

## Troubleshooting

### Backend shows wrong CORS origins in logs
```bash
# On VM2, check current .env.app
cat /opt/familycart-app/.env.app | grep CORS

# Restart containers to pick up changes
cd /opt/familycart-app
docker compose restart backend frontend

# Wait 30 seconds for health checks
sleep 30
docker compose ps
```

### Nginx errors
```bash
# Check Nginx status
sudo systemctl status nginx

# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/familycart-production.error.log
```

### SSL certificate errors
```bash
# Verify certificate on VM2
sudo openssl x509 -in /etc/nginx/ssl/cloudflare/origin-cert.pem -noout -text | grep DNS
# Should show: familycart.app, *.familycart.app

# Verify private key
sudo openssl rsa -in /etc/nginx/ssl/cloudflare/origin-key.pem -check
```

### Containers unhealthy
```bash
cd /opt/familycart-app
docker compose ps
docker compose logs backend --tail=50
docker compose logs frontend --tail=50
```

---

## Complete! 🎉

Your application should now be accessible at:
- **https://familycart.app** (primary)
- **https://www.familycart.app** (www redirect)
- All other domains redirect to familycart.app

