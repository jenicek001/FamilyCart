#!/bin/bash
# setup-ssl-certificates.sh
# Script to set up SSL certificates in organized directory structure

set -e

SSL_BASE_DIR="/home/honzik/GitHub/FamilyCart/FamilyCart/deploy/nginx/ssl"

echo "🔐 SSL Certificate Setup"
echo "========================"

# Create certificate directories
setup_directories() {
    echo "📁 Setting up certificate directories..."
    
    # Create main certificate directories
    sudo mkdir -p "$SSL_BASE_DIR/familycart"
    sudo mkdir -p "$SSL_BASE_DIR/connectedhome.cz"
    sudo mkdir -p "$SSL_BASE_DIR/default"
    
    # Set secure permissions
    sudo chmod 700 "$SSL_BASE_DIR"
    sudo chmod 700 "$SSL_BASE_DIR"/*/
    
    echo "✅ Certificate directories created"
}

# Generate default self-signed certificate
generate_default_cert() {
    echo "🔑 Generating default self-signed certificate..."
    
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$SSL_BASE_DIR/default/default.key" \
        -out "$SSL_BASE_DIR/default/default.crt" \
        -subj "/C=CZ/ST=Prague/L=Prague/O=FamilyCart/CN=default" \
        > /dev/null 2>&1
    
    sudo chmod 600 "$SSL_BASE_DIR/default/default.key" "$SSL_BASE_DIR/default/default.crt"
    sudo chown root:root "$SSL_BASE_DIR/default/default.key" "$SSL_BASE_DIR/default/default.crt"
    
    echo "✅ Default certificate generated"
}

# Install CloudFlare certificate for connectedhome.cz
install_connectedhome_cert() {
    echo ""
    echo "📝 Installing CloudFlare certificate for connectedhome.cz..."
    echo "   This certificate will be used for:"
    echo "   - grafana.connectedhome.cz"
    echo "   - homeassistant.connectedhome.cz"
    echo ""
    
    echo "Paste the CloudFlare Origin Certificate (including -----BEGIN/END CERTIFICATE----- lines):"
    echo "Press Ctrl+D when finished:"
    sudo tee "$SSL_BASE_DIR/connectedhome.cz/connectedhome.cz.crt" > /dev/null
    
    echo ""
    echo "Paste the Private Key (including -----BEGIN/END PRIVATE KEY----- lines):"
    echo "Press Ctrl+D when finished:"
    sudo tee "$SSL_BASE_DIR/connectedhome.cz/connectedhome.cz.key" > /dev/null
    
    # Set correct permissions
    sudo chmod 600 "$SSL_BASE_DIR/connectedhome.cz/connectedhome.cz.key" "$SSL_BASE_DIR/connectedhome.cz/connectedhome.cz.crt"
    sudo chown root:root "$SSL_BASE_DIR/connectedhome.cz/connectedhome.cz.key" "$SSL_BASE_DIR/connectedhome.cz/connectedhome.cz.crt"
    
    # Validate certificate
    if sudo openssl x509 -in "$SSL_BASE_DIR/connectedhome.cz/connectedhome.cz.crt" -noout -dates > /dev/null 2>&1; then
        echo "✅ connectedhome.cz certificate installed and validated"
        EXPIRY=$(sudo openssl x509 -in "$SSL_BASE_DIR/connectedhome.cz/connectedhome.cz.crt" -noout -enddate | cut -d= -f2)
        echo "   Certificate expires: $EXPIRY"
    else
        echo "❌ Certificate validation failed"
        sudo rm -f "$SSL_BASE_DIR/connectedhome.cz/connectedhome.cz.key" "$SSL_BASE_DIR/connectedhome.cz/connectedhome.cz.crt"
        return 1
    fi
}

# Install certificate for FamilyCart UAT
install_familycart_cert() {
    echo ""
    echo "🤔 FamilyCart UAT Certificate Options:"
    echo "1. Use existing self-signed certificate (for local testing)"
    echo "2. Install CloudFlare certificate for uat.familycart.local"
    echo "3. Skip (manually install later)"
    echo ""
    
    read -p "Choose option (1-3): " -n 1 -r
    echo
    
    case $REPLY in
        1)
            echo "🔑 Generating self-signed certificate for uat.familycart.local..."
            sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
                -keyout "$SSL_BASE_DIR/familycart/uat.familycart.local.key" \
                -out "$SSL_BASE_DIR/familycart/uat.familycart.local.crt" \
                -subj "/C=CZ/ST=Prague/L=Prague/O=FamilyCart/CN=uat.familycart.local" \
                > /dev/null 2>&1
            
            sudo chmod 600 "$SSL_BASE_DIR/familycart/uat.familycart.local.key" "$SSL_BASE_DIR/familycart/uat.familycart.local.crt"
            sudo chown root:root "$SSL_BASE_DIR/familycart/uat.familycart.local.key" "$SSL_BASE_DIR/familycart/uat.familycart.local.crt"
            echo "✅ Self-signed certificate generated for FamilyCart UAT"
            ;;
        2)
            echo "📝 Installing CloudFlare certificate for uat.familycart.local..."
            echo "Paste the CloudFlare Origin Certificate:"
            echo "Press Ctrl+D when finished:"
            sudo tee "$SSL_BASE_DIR/familycart/uat.familycart.local.crt" > /dev/null
            
            echo "Paste the Private Key:"
            echo "Press Ctrl+D when finished:"
            sudo tee "$SSL_BASE_DIR/familycart/uat.familycart.local.key" > /dev/null
            
            sudo chmod 600 "$SSL_BASE_DIR/familycart/uat.familycart.local.key" "$SSL_BASE_DIR/familycart/uat.familycart.local.crt"
            sudo chown root:root "$SSL_BASE_DIR/familycart/uat.familycart.local.key" "$SSL_BASE_DIR/familycart/uat.familycart.local.crt"
            echo "✅ CloudFlare certificate installed for FamilyCart UAT"
            ;;
        3)
            echo "⏭️  Skipping FamilyCart certificate installation"
            echo "   You can install it manually later in: $SSL_BASE_DIR/familycart/"
            ;;
        *)
            echo "❌ Invalid option"
            return 1
            ;;
    esac
}

# Display certificate summary
show_certificate_summary() {
    echo ""
    echo "🎉 SSL Certificate Setup Complete!"
    echo "=================================="
    echo ""
    echo "📁 Certificate Directory Structure:"
    echo "$SSL_BASE_DIR/"
    echo "├── connectedhome.cz/"
    echo "│   ├── connectedhome.cz.crt"
    echo "│   └── connectedhome.cz.key"
    echo "├── familycart/"
    echo "│   ├── uat.familycart.local.crt"
    echo "│   └── uat.familycart.local.key"
    echo "└── default/"
    echo "    ├── default.crt"
    echo "    └── default.key"
    echo ""
    echo "📋 Certificate Usage:"
    echo "  - connectedhome.cz.*     → grafana.connectedhome.cz, homeassistant.connectedhome.cz"
    echo "  - uat.familycart.local.* → uat.familycart.local"
    echo "  - default.*              → Unknown domains (fallback)"
    echo ""
    echo "🔧 Next Steps:"
    echo "1. Enable desired sites: ./nginx-site-manager.sh enable <site-name>"
    echo "2. Test configuration:   ./nginx-site-manager.sh test"
    echo "3. Deploy with:          ./deploy-modular-nginx.sh"
}

# Main execution
main() {
    if [[ $EUID -ne 0 ]] && ! sudo -n true 2>/dev/null; then
        echo "❌ This script requires sudo privileges for SSL file management"
        echo "   Please run: sudo ./setup-ssl-certificates.sh"
        exit 1
    fi
    
    echo "This script will set up SSL certificates for your nginx configuration."
    echo ""
    read -p "Continue with certificate setup? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled"
        exit 0
    fi
    
    setup_directories
    generate_default_cert
    install_connectedhome_cert
    install_familycart_cert
    show_certificate_summary
}

# Run main function
main "$@"
