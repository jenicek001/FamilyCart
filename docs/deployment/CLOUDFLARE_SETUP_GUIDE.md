# Cloudflare Setup Guide - FamilyCart Production

## Domain Configuration Overview

**Primary Domain**: `familycart.app` (and `www.familycart.app`)

**Redirect Domains** (301 permanent redirect to familycart.app):
- `familycart.cz` + `www.familycart.cz`
- `familycart.eu` + `www.familycart.eu`
- `nakoupit.app` + `www.nakoupit.app`
- `nakoupit.com` + `www.nakoupit.com`

---

## Step 1: Configure DNS for familycart.app

Since familycart.app is already in Cloudflare (used for UAT), you just need to add/update DNS records:

1. **Go to Cloudflare Dashboard** → Select `familycart.app` domain
2. **Go to DNS > Records**
3. **Add/Update these A records**:

| Type | Name | Content | Proxy Status | TTL |
|------|------|---------|--------------|-----|
| **A** | `@` | `158.180.30.112` | ✅ Proxied | Auto |
| **A** | `www` | `158.180.30.112` | ✅ Proxied | Auto |
| **A** | `uat` | `your-local-ip` | ⚠️ DNS Only (grey) | Auto |

**Note**: Keep the existing `uat` record pointing to your local machine (grey cloud = DNS only).

---

## Step 2: Add Redirect Domains to Cloudflare

For each redirect domain, follow these steps:

### 2.1 Add familycart.cz

1. **Cloudflare Dashboard** → Click "Add a Site"
2. **Enter domain**: `familycart.cz`
3. **Select Free plan** → Continue
4. **Note the nameservers** (e.g., `ns1.cloudflare.com`, `ns2.cloudflare.com`)
5. **Update nameservers at your domain registrar** (where you bought familycart.cz)
6. **Wait for activation** (usually 5-30 minutes)

### 2.2 Configure DNS for familycart.cz

Once active:

| Type | Name | Content | Proxy Status | TTL |
|------|------|---------|--------------|-----|
| **A** | `@` | `158.180.30.112` | ✅ Proxied | Auto |
| **A** | `www` | `158.180.30.112` | ✅ Proxied | Auto |

### 2.3 Repeat for other redirect domains

Repeat steps 2.1 and 2.2 for:
- `familycart.eu`
- `nakoupit.app`
- `nakoupit.com`

---

## Step 3: SSL/TLS Configuration

### 3.1 Set Encryption Mode

For **each domain** (familycart.app, familycart.cz, familycart.eu, nakoupit.app, nakoupit.com):

1. **Go to SSL/TLS > Overview**
2. **Set encryption mode**: `Full (strict)`

### 3.2 Origin Certificates

You already have Cloudflare Origin Certificates for familycart.app from UAT setup.

**Certificate files location on local machine**:
- Look for files like: `/etc/nginx/ssl/cloudflare/origin-cert.pem`
- And: `/etc/nginx/ssl/cloudflare/origin-key.pem`

**These certificates should cover**:
- `familycart.app`
- `*.familycart.app` (wildcard for all subdomains including uat)

The same certificates will work for production since they cover the entire domain.

---

## Step 4: Configure Redirects

Since you have multiple redirect domains and Cloudflare Free plan only allows 3 Page Rules, use **Redirect Rules** (which are unlimited on Free plan).

### 4.1 For familycart.cz

1. **Go to Rules > Redirect Rules** (in familycart.cz domain)
2. **Click "Create rule"**
3. **Configure**:
   - Rule name: `Redirect to familycart.app`
   - When incoming requests match: `All incoming requests`
   - Then: **Dynamic redirect**
     - Expression: `concat("https://familycart.app", http.request.uri.path)`
     - Status code: `301`
4. **Save**

### 4.2 Repeat for other redirect domains

Create the same redirect rule for:
- `familycart.eu` → `https://familycart.app`
- `nakoupit.app` → `https://familycart.app`
- `nakoupit.com` → `https://familycart.app`

---

## Step 5: Additional Cloudflare Settings

Apply these settings to **familycart.app** (primary domain):

### A. Security (Security > Settings)
- ✅ Security Level: `Medium`
- ✅ Bot Fight Mode: `On`
- ✅ Challenge Passage: `30 minutes`

### B. SSL/TLS (SSL/TLS > Edge Certificates)
- ✅ Always Use HTTPS: `On`
- ✅ Automatic HTTPS Rewrites: `On`
- ✅ Enable HSTS:
  - Max Age: `12 months`
  - Include subdomains: ✅
  - Preload: ✅
  - No-Sniff header: ✅

### C. Speed (Speed > Optimization)
- ✅ Auto Minify: JavaScript, CSS, HTML
- ✅ Brotli: `On`
- ✅ Early Hints: `On`

### D. Caching (Caching > Configuration)
- Caching Level: `Standard`
- Browser Cache TTL: `4 hours`

---

## Step 6: Copy Certificates to VM2

You already have Cloudflare Origin Certificates for familycart.app on your local machine (used for UAT).

**Certificate location**: `/opt/familycart-nginx-proxy/nginx/ssl/familycart.app/`

**Verify certificate details**:
```bash
# Check certificate validity and domains covered
openssl x509 -in /opt/familycart-nginx-proxy/nginx/ssl/familycart.app/uat.familycart.app.crt \
    -noout -issuer -subject -dates

# Check Subject Alternative Names
openssl x509 -in /opt/familycart-nginx-proxy/nginx/ssl/familycart.app/uat.familycart.app.crt \
    -noout -text | grep -A1 "Subject Alternative Name"
```

Expected output:
- Issuer: CloudFlare Origin SSL Certificate Authority
- Covers: `familycart.app`, `*.familycart.app`
- Valid until: ~2040

**Copy to VM2**:

```bash
# From local machine
scp -i ~/.ssh/familycart_oci \
    /opt/familycart-nginx-proxy/nginx/ssl/familycart.app/uat.familycart.app.crt \
    ubuntu@158.180.30.112:/tmp/origin-cert.pem

scp -i ~/.ssh/familycart_oci \
    /opt/familycart-nginx-proxy/nginx/ssl/familycart.app/uat.familycart.app.key \
    ubuntu@158.180.30.112:/tmp/origin-key.pem
```

---

## Step 7: Install Certificates and Nginx Config on VM2

SSH into VM2 and run the deployment script:

```bash
# SSH to VM2
ssh -i ~/.ssh/familycart_oci ubuntu@158.180.30.112

# Run the setup script
sudo bash /opt/familycart-app/scripts/setup-production-nginx.sh
```

This script will:
1. Move certificates from /tmp to /etc/nginx/ssl/cloudflare/
2. Set proper permissions
3. Copy production Nginx configuration
4. Enable the site
5. Test and reload Nginx

---

## Step 8: Update Backend Configuration

Update the backend environment to use familycart.app:

```bash
ssh -i ~/.ssh/familycart_oci ubuntu@158.180.30.112
cd /opt/familycart-app
nano .env.app
```

Change CORS_ORIGINS and NEXT_PUBLIC_API_URL:
```bash
CORS_ORIGINS=["https://familycart.app","https://www.familycart.app"]
NEXT_PUBLIC_API_URL=https://familycart.app/api
```

Restart containers:
```bash
docker compose restart backend frontend
```

---

## Step 9: Verification

### A. Check DNS propagation
```bash
dig familycart.app +short
# Should return: Cloudflare IPs (not 158.180.30.112 directly due to proxy)

dig www.familycart.app +short
# Should also return: Cloudflare IPs
```

### B. Test HTTPS endpoints
```bash
curl -I https://familycart.app/health
# Should return: 200 OK

curl -I https://www.familycart.app/
# Should return: 200 OK

curl -I https://familycart.cz/
# Should return: 301 redirect to https://familycart.app/
```

### C. Test from browser
1. Visit: https://familycart.app
2. Check for valid SSL certificate (issued by Cloudflare)
3. Test login and basic functionality
4. Visit: https://familycart.cz → should redirect to https://familycart.app

---

## Troubleshooting

### Issue: "Too many redirects"
- Check that Cloudflare SSL mode is set to "Full (strict)", not "Flexible"
- Ensure Nginx is listening on port 443 with SSL

### Issue: "Connection refused"
- Check that Nginx is running: `sudo systemctl status nginx`
- Check firewall allows HTTPS: `sudo iptables -L INPUT -n | grep 443`

### Issue: "Certificate error"
- Verify Cloudflare Origin Certificate is properly installed on VM2
- Check certificate matches the domain: `openssl x509 -in /etc/nginx/ssl/cloudflare/origin-cert.pem -noout -text | grep DNS`

### Issue: Backend/Frontend not accessible
- Check containers are healthy: `docker compose ps`
- Check Nginx upstream definitions point to correct ports (8000, 3000)
- Check logs: `sudo tail -f /var/log/nginx/familycart-production.error.log`

---

## Summary Checklist

- [ ] familycart.app DNS updated (@ and www → 158.180.30.112, proxied)
- [ ] Redirect domains added to Cloudflare (familycart.cz, .eu, nakoupit.app, .com)
- [ ] Redirect domains DNS configured (@ and www → 158.180.30.112, proxied)
- [ ] SSL/TLS set to "Full (strict)" for all domains
- [ ] Redirect Rules created for all redirect domains
- [ ] Additional Cloudflare settings configured (Security, Speed, Caching)
- [ ] Cloudflare Origin Certificates copied to VM2
- [ ] Production Nginx configuration deployed
- [ ] Backend .env.app updated with familycart.app domains
- [ ] Containers restarted
- [ ] HTTPS access verified
- [ ] Redirects verified

