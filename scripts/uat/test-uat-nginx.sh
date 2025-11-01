#!/bin/bash
# test-uat-nginx.sh
# Test script for UAT nginx configuration

set -e

PROJECT_ROOT="/home/honzik/GitHub/FamilyCart/FamilyCart"
NGINX_DIR="$PROJECT_ROOT/nginx"

echo "🧪 Testing UAT Nginx Configuration"
echo "=================================="

# Create temporary SSL certificates for testing
create_test_certificates() {
    echo "🔐 Creating temporary SSL certificates for testing..."
    
    # Create SSL directory structure matching the configuration
    mkdir -p "$NGINX_DIR/ssl/familycart"
    mkdir -p "$NGINX_DIR/ssl/default"
    
    # Create certificate for familycart (matches sites-available/familycart-uat path)
    openssl req -x509 -nodes -days 1 -newkey rsa:1024 \
        -keyout "$NGINX_DIR/ssl/familycart/uat.familycart.local.key" \
        -out "$NGINX_DIR/ssl/familycart/uat.familycart.local.crt" \
        -subj "/C=CZ/CN=uat.familycart.local" 2>/dev/null
    
    # Create default certificate
    openssl req -x509 -nodes -days 1 -newkey rsa:1024 \
        -keyout "$NGINX_DIR/ssl/default/default.key" \
        -out "$NGINX_DIR/ssl/default/default.crt" \
        -subj "/C=CZ/CN=default" 2>/dev/null
    
    echo "✅ Test certificates created"
}

# Test configuration with Docker
test_with_docker() {
    echo "🧪 Testing configuration with Docker..."
    
    # Create temporary hosts file for upstream resolution
    TEMP_HOSTS=$(mktemp)
    cat > "$TEMP_HOSTS" << 'EOF'
127.0.0.1 uat-backend
127.0.0.1 uat-frontend
127.0.0.1 uat-prometheus
EOF

    # Test the configuration
    if docker run --rm \
       -v "$NGINX_DIR/nginx.conf:/etc/nginx/nginx.conf:ro" \
       -v "$NGINX_DIR/sites-available:/etc/nginx/sites-available:ro" \
       -v "$NGINX_DIR/sites-enabled:/etc/nginx/sites-enabled:ro" \
       -v "$NGINX_DIR/conf.d:/etc/nginx/conf.d:ro" \
       -v "$NGINX_DIR/ssl:/etc/nginx/ssl:ro" \
       -v "$TEMP_HOSTS:/etc/hosts:ro" \
       nginx:alpine nginx -t 2>/dev/null; then
        echo "✅ UAT nginx configuration is VALID"
        RESULT=0
    else
        echo "❌ UAT nginx configuration has ERRORS"
        echo ""
        echo "📋 Detailed error output:"
        docker run --rm \
           -v "$NGINX_DIR/nginx.conf:/etc/nginx/nginx.conf:ro" \
           -v "$NGINX_DIR/sites-available:/etc/nginx/sites-available:ro" \
           -v "$NGINX_DIR/sites-enabled:/etc/nginx/sites-enabled:ro" \
           -v "$NGINX_DIR/conf.d:/etc/nginx/conf.d:ro" \
           -v "$NGINX_DIR/ssl:/etc/nginx/ssl:ro" \
           -v "$TEMP_HOSTS:/etc/hosts:ro" \
           nginx:alpine nginx -t
        RESULT=1
    fi
    
    rm -f "$TEMP_HOSTS"
    return $RESULT
}

# Show configuration summary
show_summary() {
    echo ""
    echo "📊 UAT Configuration Summary"
    echo "============================"
    echo ""
    echo "📁 Nginx Directory Structure:"
    tree "$NGINX_DIR" 2>/dev/null || find "$NGINX_DIR" -type f | sort
    
    echo ""
    echo "🔗 Enabled Sites:"
    for site in "$NGINX_DIR/sites-enabled"/*; do
        if [ -L "$site" ]; then
            site_name=$(basename "$site")
            target=$(readlink "$site")
            echo "  ✅ $site_name → $target"
        fi
    done
    
    echo ""
    echo "📋 Services Configuration:"
    echo "  🌐 FamilyCart UAT: uat.familycart.local"
    echo "  🔒 Default catch-all: unknown domains → 444"
    echo "  📊 Additional services: grafana, homeassistant (available but disabled)"
    
    echo ""
    echo "🔧 Docker Compose Volume Mounts:"
    echo "  - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro"
    echo "  - ./nginx/sites-available:/etc/nginx/sites-available:ro"
    echo "  - ./nginx/sites-enabled:/etc/nginx/sites-enabled:ro"
    echo "  - ./nginx/conf.d:/etc/nginx/conf.d:ro"
    echo "  - ./nginx/ssl:/etc/nginx/ssl:ro"
}

# Cleanup test certificates
cleanup() {
    echo ""
    echo "🧹 Cleaning up test certificates..."
    rm -rf "$NGINX_DIR/ssl/familycart" "$NGINX_DIR/ssl/default"
    echo "✅ Test certificates removed"
}

# Main execution
main() {
    create_test_certificates
    
    if test_with_docker; then
        show_summary
        echo ""
        echo "🎉 UAT nginx configuration test PASSED!"
        echo ""
        echo "📋 Ready for deployment:"
        echo "1. Install production SSL certificates in nginx/ssl/"
        echo "2. Commit changes: git add nginx/ docker-compose.uat.yml"
        echo "3. Push to repository: git commit && git push"
        echo "4. Deploy to UAT: cd /opt/familycart-uat-repo && git pull"
        echo "5. Start UAT: docker-compose -f docker-compose.uat.yml up -d"
        
        cleanup
        exit 0
    else
        echo ""
        echo "❌ UAT nginx configuration test FAILED"
        echo "Please fix the errors shown above before deployment"
        
        cleanup
        exit 1
    fi
}

# Run main function
main "$@"
