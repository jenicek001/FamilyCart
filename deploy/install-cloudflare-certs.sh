#!/bin/bash
# install-cloudflare-certs.sh
# Script to install CloudFlare Origin Certificates for multi-service nginx

set -e

SSL_DIR="/etc/nginx/ssl"

echo "🔐 CloudFlare Origin Certificate Installation"
echo "============================================"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo "❌ This script must be run as root (use sudo)"
    echo "   Example: sudo ./install-cloudflare-certs.sh"
    exit 1
fi

# Create SSL directory
echo "📁 Creating SSL directory..."
mkdir -p "$SSL_DIR"
chmod 700 "$SSL_DIR"

# Function to install certificate
install_certificate() {
    local cert_name=$1
    local cert_file="$SSL_DIR/$cert_name.crt"
    local key_file="$SSL_DIR/$cert_name.key"
    
    echo ""
    echo "📝 Installing $cert_name certificate..."
    echo "   Certificate file: $cert_file"
    echo "   Private key file: $key_file"
    echo ""
    
    # Get certificate content
    echo "Paste the CloudFlare Origin Certificate (including -----BEGIN/END CERTIFICATE----- lines):"
    echo "Press Ctrl+D when finished:"
    cat > "$cert_file"
    
    echo ""
    echo "Paste the Private Key (including -----BEGIN/END PRIVATE KEY----- lines):"
    echo "Press Ctrl+D when finished:"
    cat > "$key_file"
    
    # Set correct permissions
    chmod 600 "$cert_file" "$key_file"
    chown root:root "$cert_file" "$key_file"
    
    # Validate certificate
    if openssl x509 -in "$cert_file" -noout -dates > /dev/null 2>&1; then
        echo "✅ Certificate installed and validated successfully"
        EXPIRY=$(openssl x509 -in "$cert_file" -noout -enddate | cut -d= -f2)
        echo "   Certificate expires: $EXPIRY"
    else
        echo "❌ Certificate validation failed - please check the format"
        rm -f "$cert_file" "$key_file"
        return 1
    fi
    
    # Validate private key
    if openssl rsa -in "$key_file" -check -noout > /dev/null 2>&1; then
        echo "✅ Private key validated successfully"
    else
        echo "❌ Private key validation failed - please check the format"
        rm -f "$cert_file" "$key_file"
        return 1
    fi
}

# Generate default self-signed certificate
generate_default_cert() {
    echo ""
    echo "🔑 Generating default self-signed certificate..."
    
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$SSL_DIR/default.key" \
        -out "$SSL_DIR/default.crt" \
        -subj "/C=CZ/ST=Prague/L=Prague/O=FamilyCart/CN=default" \
        > /dev/null 2>&1
    
    chmod 600 "$SSL_DIR/default.key" "$SSL_DIR/default.crt"
    chown root:root "$SSL_DIR/default.key" "$SSL_DIR/default.crt"
    
    echo "✅ Default certificate generated"
}

# Main installation process
echo ""
echo "This script will install CloudFlare Origin Certificates for:"
echo "  - connectedhome.cz (for grafana.connectedhome.cz and homeassistant.connectedhome.cz)"
echo "  - Generate a default self-signed certificate"
echo ""

read -p "Continue with certificate installation? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Installation cancelled"
    exit 0
fi

echo ""
echo "📋 Steps to get CloudFlare Origin Certificate:"
echo "1. Go to CloudFlare Dashboard → SSL/TLS → Origin Server"
echo "2. Click 'Create Certificate'"
echo "3. Use hostnames: *.connectedhome.cz, connectedhome.cz"
echo "4. Select RSA (2048) key type"
echo "5. Set validity to 15 years"
echo "6. Copy both Certificate and Private Key"
echo ""

# Install connectedhome.cz certificate
if install_certificate "connectedhome.cz"; then
    echo "✅ connectedhome.cz certificate installed successfully"
else
    echo "❌ Failed to install connectedhome.cz certificate"
    exit 1
fi

# Generate default certificate
generate_default_cert

# Display summary
echo ""
echo "🎉 Certificate Installation Complete!"
echo "===================================="
echo ""
echo "Installed certificates:"
echo "  ✅ $SSL_DIR/connectedhome.cz.crt"
echo "  ✅ $SSL_DIR/connectedhome.cz.key"
echo "  ✅ $SSL_DIR/default.crt"
echo "  ✅ $SSL_DIR/default.key"
echo ""
echo "📋 Next steps:"
echo "1. Configure DNS records in CloudFlare:"
echo "   - grafana.connectedhome.cz → [YOUR_PUBLIC_IP]"
echo "   - homeassistant.connectedhome.cz → [YOUR_PUBLIC_IP]"
echo ""
echo "2. Deploy multi-service nginx:"
echo "   ./deploy-multi-service-nginx.sh"
echo ""
echo "3. Test your services:"
echo "   - https://grafana.connectedhome.cz"
echo "   - https://homeassistant.connectedhome.cz"
echo ""
echo "🔒 Certificate expires on: $(openssl x509 -in "$SSL_DIR/connectedhome.cz.crt" -noout -enddate | cut -d= -f2)"
echo ""
echo "📚 For troubleshooting: deploy/CLOUDFLARE_MULTI_SERVICE_GUIDE.md"
