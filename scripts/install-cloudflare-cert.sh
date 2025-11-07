#!/bin/bash
#
# Install Cloudflare Origin Certificate on VM2
# This script must be run on VM2 (158.180.30.112)
#

set -e

echo "==================================="
echo "Cloudflare Origin Certificate Setup"
echo "==================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ This script must be run as root (use sudo)"
    exit 1
fi

echo "Step 1: Create SSL directory for Cloudflare certificates"
mkdir -p /etc/nginx/ssl/cloudflare
chmod 700 /etc/nginx/ssl/cloudflare

echo ""
echo "Step 2: Install Cloudflare Origin Certificate"
echo "---"
echo "You need to paste the certificate and private key from Cloudflare dashboard:"
echo "  1. Go to: SSL/TLS > Origin Server"
echo "  2. Click 'Create Certificate'"
echo "  3. Configure:"
echo "     - Private key type: RSA (2048)"
echo "     - Hostnames: familycart.app, *.familycart.app"
echo "     - Certificate Validity: 15 years"
echo "  4. Copy the 'Origin Certificate' and 'Private Key'"
echo ""
echo "---"
echo ""

# Create certificate file
echo "Paste the Origin Certificate (including -----BEGIN CERTIFICATE----- and -----END CERTIFICATE-----)"
echo "When done, press Ctrl+D on a new line:"
cat > /etc/nginx/ssl/cloudflare/origin-cert.pem

echo ""
echo "✅ Certificate saved to /etc/nginx/ssl/cloudflare/origin-cert.pem"
echo ""

# Create private key file
echo "Paste the Private Key (including -----BEGIN PRIVATE KEY----- and -----END PRIVATE KEY-----)"
echo "When done, press Ctrl+D on a new line:"
cat > /etc/nginx/ssl/cloudflare/origin-key.pem

echo ""
echo "✅ Private key saved to /etc/nginx/ssl/cloudflare/origin-key.pem"
echo ""

# Set proper permissions
chmod 644 /etc/nginx/ssl/cloudflare/origin-cert.pem
chmod 600 /etc/nginx/ssl/cloudflare/origin-key.pem

echo "Step 3: Verify certificate files"
if openssl x509 -in /etc/nginx/ssl/cloudflare/origin-cert.pem -noout -text > /dev/null 2>&1; then
    echo "✅ Certificate is valid"
    echo "   Subject: $(openssl x509 -in /etc/nginx/ssl/cloudflare/origin-cert.pem -noout -subject | sed 's/subject=//')"
    echo "   Issuer: $(openssl x509 -in /etc/nginx/ssl/cloudflare/origin-cert.pem -noout -issuer | sed 's/issuer=//')"
    echo "   Valid until: $(openssl x509 -in /etc/nginx/ssl/cloudflare/origin-cert.pem -noout -enddate | sed 's/notAfter=//')"
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
echo "Step 4: Copy production Nginx configuration"
echo "   Source: /opt/familycart-app/nginx/sites-available/familycart-production"
echo "   Destination: /etc/nginx/sites-available/familycart-production"

if [ -f /opt/familycart-app/nginx/sites-available/familycart-production ]; then
    cp /opt/familycart-app/nginx/sites-available/familycart-production /etc/nginx/sites-available/
    echo "✅ Configuration copied"
else
    echo "⚠️  Configuration file not found at /opt/familycart-app/nginx/sites-available/familycart-production"
    echo "   Please ensure you've cloned the repo to /opt/familycart-app or update this path"
    exit 1
fi

echo ""
echo "Step 5: Enable the production site"
if [ -L /etc/nginx/sites-enabled/familycart-production ]; then
    echo "   Site already enabled"
else
    ln -s /etc/nginx/sites-available/familycart-production /etc/nginx/sites-enabled/
    echo "✅ Site enabled"
fi

echo ""
echo "Step 6: Test Nginx configuration"
if nginx -t; then
    echo "✅ Nginx configuration is valid"
else
    echo "❌ Nginx configuration test failed"
    echo "   Please fix the errors before reloading Nginx"
    exit 1
fi

echo ""
echo "Step 7: Reload Nginx"
systemctl reload nginx
echo "✅ Nginx reloaded"

echo ""
echo "==================================="
echo "✅ Installation Complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "  1. Update DNS in Cloudflare to point to this server (158.180.30.112)"
echo "  2. Wait for DNS propagation (usually 1-5 minutes)"
echo "  3. Test: curl -I https://familycart.app"
echo "  4. Visit: https://familycart.app in your browser"
echo ""
