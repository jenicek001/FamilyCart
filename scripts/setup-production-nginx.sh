#!/bin/bash
#
# Setup Production Nginx Configuration on VM2
# This script installs Cloudflare certificates and configures Nginx for production
#

set -e

echo "=============================================="
echo "FamilyCart Production Nginx Setup"
echo "=============================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ This script must be run as root (use sudo)"
    exit 1
fi

# Step 1: Create SSL directory
echo "Step 1: Create SSL directory for Cloudflare certificates"
mkdir -p /etc/nginx/ssl/cloudflare
chmod 700 /etc/nginx/ssl/cloudflare
echo "✅ Directory created: /etc/nginx/ssl/cloudflare"
echo ""

# Step 2: Move certificates from /tmp
echo "Step 2: Install Cloudflare Origin Certificates"
if [ -f /tmp/origin-cert.pem ] && [ -f /tmp/origin-key.pem ]; then
    mv /tmp/origin-cert.pem /etc/nginx/ssl/cloudflare/origin-cert.pem
    mv /tmp/origin-key.pem /etc/nginx/ssl/cloudflare/origin-key.pem
    chmod 644 /etc/nginx/ssl/cloudflare/origin-cert.pem
    chmod 600 /etc/nginx/ssl/cloudflare/origin-key.pem
    echo "✅ Certificates installed from /tmp/"
elif [ -f /etc/nginx/ssl/cloudflare/origin-cert.pem ] && [ -f /etc/nginx/ssl/cloudflare/origin-key.pem ]; then
    echo "✅ Certificates already exist at /etc/nginx/ssl/cloudflare/"
else
    echo "❌ ERROR: Certificate files not found!"
    echo ""
    echo "Please copy certificates first:"
    echo "  From local machine:"
    echo "    scp -i ~/.ssh/familycart_oci /etc/nginx/ssl/cloudflare/origin-cert.pem ubuntu@158.180.30.112:/tmp/"
    echo "    scp -i ~/.ssh/familycart_oci /etc/nginx/ssl/cloudflare/origin-key.pem ubuntu@158.180.30.112:/tmp/"
    echo ""
    echo "  Then run this script again."
    exit 1
fi
echo ""

# Step 3: Verify certificates
echo "Step 3: Verify certificate files"
if openssl x509 -in /etc/nginx/ssl/cloudflare/origin-cert.pem -noout -text > /dev/null 2>&1; then
    echo "✅ Certificate is valid"
    echo "   Subject: $(openssl x509 -in /etc/nginx/ssl/cloudflare/origin-cert.pem -noout -subject | sed 's/subject=//')"
    echo "   Issuer: $(openssl x509 -in /etc/nginx/ssl/cloudflare/origin-cert.pem -noout -issuer | sed 's/issuer=//')"
    echo "   Valid until: $(openssl x509 -in /etc/nginx/ssl/cloudflare/origin-cert.pem -noout -enddate | sed 's/notAfter=//')"
    echo "   DNS Names:"
    openssl x509 -in /etc/nginx/ssl/cloudflare/origin-cert.pem -noout -text | grep -A1 "Subject Alternative Name" | tail -1 | sed 's/DNS://g' | tr ',' '\n' | sed 's/^/     - /'
else
    echo "❌ Certificate validation failed"
    exit 1
fi

if openssl rsa -in /etc/nginx/ssl/cloudflare/origin-key.pem -check > /dev/null 2>&1; then
    echo "✅ Private key is valid"
else
    echo "❌ Private key validation failed"
    exit 1
fi
echo ""

# Step 4: Copy production Nginx configuration
echo "Step 4: Install production Nginx configuration"
NGINX_CONF_SOURCE="/opt/familycart-app/nginx/sites-available/familycart-production"
NGINX_CONF_DEST="/etc/nginx/sites-available/familycart-production"

if [ -f "$NGINX_CONF_SOURCE" ]; then
    cp "$NGINX_CONF_SOURCE" "$NGINX_CONF_DEST"
    echo "✅ Configuration copied to $NGINX_CONF_DEST"
else
    echo "❌ Configuration file not found at $NGINX_CONF_SOURCE"
    echo "   Checking if repo is cloned..."
    if [ ! -d /opt/familycart-app ]; then
        echo "   Repo not found. Cloning from GitHub..."
        cd /opt
        git clone https://github.com/jenicek001/FamilyCart.git familycart-app
        if [ -f "$NGINX_CONF_SOURCE" ]; then
            cp "$NGINX_CONF_SOURCE" "$NGINX_CONF_DEST"
            echo "✅ Configuration copied after cloning repo"
        else
            echo "❌ Configuration still not found after cloning"
            exit 1
        fi
    else
        echo "   Pulling latest changes..."
        cd /opt/familycart-app
        git pull
        if [ -f "$NGINX_CONF_SOURCE" ]; then
            cp "$NGINX_CONF_SOURCE" "$NGINX_CONF_DEST"
            echo "✅ Configuration copied after git pull"
        else
            echo "❌ Configuration file still not found"
            exit 1
        fi
    fi
fi
echo ""

# Step 5: Enable the production site
echo "Step 5: Enable production site"
NGINX_ENABLED="/etc/nginx/sites-enabled/familycart-production"
if [ -L "$NGINX_ENABLED" ]; then
    echo "   Site already enabled"
else
    ln -s "$NGINX_CONF_DEST" "$NGINX_ENABLED"
    echo "✅ Site enabled: $NGINX_ENABLED"
fi
echo ""

# Step 6: Ensure required Nginx config files exist
echo "Step 6: Check required Nginx configuration files"

# ssl-common.conf
if [ ! -f /etc/nginx/conf.d/ssl-common.conf ]; then
    echo "   Creating /etc/nginx/conf.d/ssl-common.conf"
    cat > /etc/nginx/conf.d/ssl-common.conf << 'SSLCONF'
# SSL common configuration
# Modern SSL configuration for maximum security

# SSL protocols (TLS 1.2 and 1.3 only)
ssl_protocols TLSv1.2 TLSv1.3;

# SSL ciphers (strong ciphers only)
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';
ssl_prefer_server_ciphers off;

# SSL session cache and timeout
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
ssl_session_tickets off;

# OCSP stapling
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;

# Diffie-Hellman parameter for DHE ciphersuites
# ssl_dhparam /etc/nginx/ssl/dhparam.pem;
SSLCONF
    echo "✅ Created ssl-common.conf"
else
    echo "✅ ssl-common.conf exists"
fi

# cloudflare-realip.conf
if [ ! -f /etc/nginx/conf.d/cloudflare-realip.conf ]; then
    echo "   Creating /etc/nginx/conf.d/cloudflare-realip.conf"
    cat > /etc/nginx/conf.d/cloudflare-realip.conf << 'CFCONF'
# Cloudflare Real IP configuration
# Restore actual client IP from Cloudflare headers

# Set real IP from Cloudflare
set_real_ip_from 173.245.48.0/20;
set_real_ip_from 103.21.244.0/22;
set_real_ip_from 103.22.200.0/22;
set_real_ip_from 103.31.4.0/22;
set_real_ip_from 141.101.64.0/18;
set_real_ip_from 108.162.192.0/18;
set_real_ip_from 190.93.240.0/20;
set_real_ip_from 188.114.96.0/20;
set_real_ip_from 197.234.240.0/22;
set_real_ip_from 198.41.128.0/17;
set_real_ip_from 162.158.0.0/15;
set_real_ip_from 104.16.0.0/13;
set_real_ip_from 104.24.0.0/14;
set_real_ip_from 172.64.0.0/13;
set_real_ip_from 131.0.72.0/22;
set_real_ip_from 2400:cb00::/32;
set_real_ip_from 2606:4700::/32;
set_real_ip_from 2803:f800::/32;
set_real_ip_from 2405:b500::/32;
set_real_ip_from 2405:8100::/32;
set_real_ip_from 2a06:98c0::/29;
set_real_ip_from 2c0f:f248::/32;

# Use CF-Connecting-IP header
real_ip_header CF-Connecting-IP;
CFCONF
    echo "✅ Created cloudflare-realip.conf"
else
    echo "✅ cloudflare-realip.conf exists"
fi
echo ""

# Step 7: Create upstream configuration if not in main nginx.conf
echo "Step 7: Check upstream configuration"
if [ ! -f /etc/nginx/conf.d/upstreams.conf ]; then
    echo "   Creating /etc/nginx/conf.d/upstreams.conf"
    cat > /etc/nginx/conf.d/upstreams.conf << 'UPCONF'
# Backend and Frontend upstream definitions
upstream familycart_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

upstream familycart_frontend {
    server 127.0.0.1:3000;
    keepalive 32;
}
UPCONF
    echo "✅ Created upstreams.conf"
else
    echo "✅ upstreams.conf exists"
fi
echo ""

# Step 8: Create rate limiting zones
echo "Step 8: Check rate limiting configuration"
if ! grep -q "limit_req_zone" /etc/nginx/nginx.conf 2>/dev/null; then
    if [ ! -f /etc/nginx/conf.d/rate-limiting.conf ]; then
        echo "   Creating /etc/nginx/conf.d/rate-limiting.conf"
        cat > /etc/nginx/conf.d/rate-limiting.conf << 'RATECONF'
# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=web:10m rate=30r/s;
RATECONF
        echo "✅ Created rate-limiting.conf"
    else
        echo "✅ rate-limiting.conf exists"
    fi
else
    echo "✅ Rate limiting configured in nginx.conf"
fi
echo ""

# Step 9: Test Nginx configuration
echo "Step 9: Test Nginx configuration"
if nginx -t 2>&1; then
    echo "✅ Nginx configuration is valid"
else
    echo "❌ Nginx configuration test failed"
    echo ""
    echo "Please review the errors above and fix them before continuing."
    exit 1
fi
echo ""

# Step 10: Reload or start Nginx
echo "Step 10: Reload Nginx"
if systemctl is-active --quiet nginx; then
    systemctl reload nginx
    echo "✅ Nginx reloaded"
else
    systemctl start nginx
    systemctl enable nginx
    echo "✅ Nginx started and enabled"
fi
echo ""

# Step 11: Display status
echo "=============================================="
echo "✅ Installation Complete!"
echo "=============================================="
echo ""
echo "Current status:"
systemctl status nginx --no-pager -l | head -10
echo ""
echo "Enabled sites:"
ls -la /etc/nginx/sites-enabled/ | grep familycart
echo ""
echo "Next steps:"
echo "  1. Update backend .env.app with familycart.app domains"
echo "     cd /opt/familycart-app && nano .env.app"
echo "     Change CORS_ORIGINS and NEXT_PUBLIC_API_URL to use familycart.app"
echo ""
echo "  2. Restart containers:"
echo "     cd /opt/familycart-app && docker compose restart backend frontend"
echo ""
echo "  3. Configure Cloudflare DNS (see CLOUDFLARE_SETUP_GUIDE.md)"
echo ""
echo "  4. Test once DNS propagates:"
echo "     curl -I https://familycart.app/health"
echo ""
