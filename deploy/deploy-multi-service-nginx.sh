#!/bin/bash
# deploy-multi-service-nginx.sh
# Script to deploy multi-service nginx configuration with CloudFlare support

set -e

PROJECT_ROOT="/home/honzik/GitHub/FamilyCart/FamilyCart"
NGINX_CONFIG_DIR="$PROJECT_ROOT/deploy/nginx"
SSL_DIR="/etc/nginx/ssl"
LOG_DIR="$PROJECT_ROOT/logs/nginx"

echo "🚀 Deploying Multi-Service Nginx Configuration"
echo "=============================================="

# Function to check if script is run with sudo for SSL operations
check_sudo() {
    if [[ $EUID -eq 0 ]]; then
        echo "✅ Running with root privileges"
    else
        echo "⚠️  Some operations require sudo privileges"
        echo "   You'll be prompted for password when needed"
    fi
}

# Function to create necessary directories
setup_directories() {
    echo "📁 Setting up directories..."
    
    # Create log directories
    sudo mkdir -p "$LOG_DIR"
    sudo chmod 755 "$LOG_DIR"
    
    # Create SSL directory if it doesn't exist
    sudo mkdir -p "$SSL_DIR"
    sudo chmod 700 "$SSL_DIR"
    
    echo "✅ Directories created successfully"
}

# Function to backup current configuration
backup_current_config() {
    echo "💾 Backing up current configuration..."
    
    BACKUP_DIR="$PROJECT_ROOT/deploy/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup current nginx config if it exists
    if [ -f "$NGINX_CONFIG_DIR/uat.conf" ]; then
        cp "$NGINX_CONFIG_DIR/uat.conf" "$BACKUP_DIR/uat.conf.backup"
        echo "✅ Current uat.conf backed up to $BACKUP_DIR"
    fi
    
    # Backup docker-compose if needed
    if [ -f "$PROJECT_ROOT/docker-compose.uat.yml" ]; then
        cp "$PROJECT_ROOT/docker-compose.uat.yml" "$BACKUP_DIR/docker-compose.uat.yml.backup"
        echo "✅ Docker Compose configuration backed up"
    fi
}

# Function to check SSL certificates
check_ssl_certificates() {
    echo "🔐 Checking SSL certificates..."
    
    REQUIRED_CERTS=(
        "$SSL_DIR/connectedhome.cz.crt"
        "$SSL_DIR/connectedhome.cz.key"
        "$SSL_DIR/default.crt" 
        "$SSL_DIR/default.key"
    )
    
    MISSING_CERTS=()
    
    for cert in "${REQUIRED_CERTS[@]}"; do
        if [ ! -f "$cert" ]; then
            MISSING_CERTS+=("$cert")
        fi
    done
    
    if [ ${#MISSING_CERTS[@]} -gt 0 ]; then
        echo "⚠️  Missing SSL certificates:"
        for cert in "${MISSING_CERTS[@]}"; do
            echo "   - $cert"
        done
        echo ""
        echo "📋 Please install SSL certificates first:"
        echo "   1. Generate CloudFlare Origin Certificates"
        echo "   2. Run: sudo ./install-cloudflare-certs.sh"
        echo "   3. Or see: deploy/CLOUDFLARE_MULTI_SERVICE_GUIDE.md"
        echo ""
        read -p "Continue without SSL certificates? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "❌ Deployment aborted. Please install SSL certificates first."
            exit 1
        fi
    else
        echo "✅ All SSL certificates found"
        
        # Verify certificate validity
        if openssl x509 -in "$SSL_DIR/connectedhome.cz.crt" -noout -dates > /dev/null 2>&1; then
            echo "✅ SSL certificates appear to be valid"
            EXPIRY=$(openssl x509 -in "$SSL_DIR/connectedhome.cz.crt" -noout -enddate | cut -d= -f2)
            echo "   Certificate expires: $EXPIRY"
        else
            echo "⚠️  SSL certificate validation failed - check certificate format"
        fi
    fi
}

# Function to test nginx configuration
test_nginx_config() {
    echo "🧪 Testing nginx configuration..."
    
    # Test the multi-service config syntax
    if docker run --rm -v "$NGINX_CONFIG_DIR/multi-service.conf:/etc/nginx/nginx.conf:ro" nginx:alpine nginx -t; then
        echo "✅ Nginx configuration syntax is valid"
    else
        echo "❌ Nginx configuration has syntax errors"
        echo "   Please check deploy/nginx/multi-service.conf"
        exit 1
    fi
}

# Function to check if services are accessible
check_upstream_services() {
    echo "🌐 Checking upstream services..."
    
    # Check if Home Assistant is accessible
    if timeout 5 curl -s http://192.168.3.30:8123/health > /dev/null 2>&1; then
        echo "✅ Home Assistant (192.168.3.30:8123) is accessible"
    else
        echo "⚠️  Home Assistant (192.168.3.30:8123) is not accessible"
        echo "   - Check if Home Assistant is running"
        echo "   - Verify network connectivity"
        echo "   - This won't prevent deployment but will cause 502 errors for homeassistant.connectedhome.cz"
    fi
    
    # Check for Grafana/Prometheus container (will be created by docker-compose)
    echo "ℹ️  Grafana service will be available after docker-compose up"
}

# Function to update docker-compose configuration
update_docker_compose() {
    echo "🐳 Updating Docker Compose configuration..."
    
    DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.uat.yml"
    
    # Check if multi-service config is already referenced
    if grep -q "multi-service.conf" "$DOCKER_COMPOSE_FILE"; then
        echo "✅ Docker Compose already configured for multi-service"
    else
        echo "📝 Updating nginx volume mapping in docker-compose.uat.yml"
        
        # Create a temporary file with updated configuration
        sed 's|./deploy/nginx/uat.conf:/etc/nginx/nginx.conf:ro|./deploy/nginx/multi-service.conf:/etc/nginx/nginx.conf:ro|g' "$DOCKER_COMPOSE_FILE" > "$DOCKER_COMPOSE_FILE.tmp"
        
        # Replace original file
        mv "$DOCKER_COMPOSE_FILE.tmp" "$DOCKER_COMPOSE_FILE"
        
        echo "✅ Docker Compose configuration updated"
    fi
}

# Function to deploy the configuration
deploy_configuration() {
    echo "🚀 Deploying configuration..."
    
    # Stop current services
    echo "🛑 Stopping current services..."
    cd "$PROJECT_ROOT"
    docker-compose -f docker-compose.uat.yml down
    
    # Update docker-compose
    update_docker_compose
    
    # Start services with new configuration
    echo "▶️  Starting services with new configuration..."
    docker-compose -f docker-compose.uat.yml up -d
    
    # Wait for services to start
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    # Check if nginx container is running
    if docker ps | grep -q "familycart-uat-proxy"; then
        echo "✅ Nginx proxy container is running"
    else
        echo "❌ Nginx proxy container failed to start"
        echo "   Check logs: docker logs familycart-uat-proxy"
        exit 1
    fi
}

# Function to run post-deployment tests
run_tests() {
    echo "🧪 Running post-deployment tests..."
    
    # Test each endpoint
    ENDPOINTS=(
        "http://localhost/health:FamilyCart UAT"
        "http://localhost:80:Nginx Base"
    )
    
    for endpoint_info in "${ENDPOINTS[@]}"; do
        IFS=':' read -r endpoint service <<< "$endpoint_info"
        
        echo -n "   Testing $service ($endpoint)... "
        if timeout 10 curl -s "$endpoint" > /dev/null 2>&1; then
            echo "✅"
        else
            echo "❌"
        fi
    done
    
    echo ""
    echo "📋 Manual testing needed for:"
    echo "   - https://uat.familycart.local (if SSL configured)"
    echo "   - https://grafana.connectedhome.cz (requires DNS & SSL)"
    echo "   - https://homeassistant.connectedhome.cz (requires DNS & SSL)"
}

# Function to show next steps
show_next_steps() {
    echo ""
    echo "🎉 Deployment Complete!"
    echo "====================="
    echo ""
    echo "📋 Next Steps:"
    echo ""
    echo "1. 🌐 DNS Configuration:"
    echo "   - Configure CloudFlare DNS for grafana.connectedhome.cz"
    echo "   - Configure CloudFlare DNS for homeassistant.connectedhome.cz"
    echo ""
    echo "2. 🔐 SSL Certificates (if not done yet):"
    echo "   - Generate CloudFlare Origin Certificates"
    echo "   - Install certificates using provided script"
    echo "   - See: deploy/CLOUDFLARE_MULTI_SERVICE_GUIDE.md"
    echo ""
    echo "3. 🧪 Testing:"
    echo "   - Test FamilyCart UAT: https://uat.familycart.local"
    echo "   - Test Grafana: https://grafana.connectedhome.cz"
    echo "   - Test Home Assistant: https://homeassistant.connectedhome.cz"
    echo ""
    echo "4. 📊 Monitoring:"
    echo "   - Monitor logs: docker logs -f familycart-uat-proxy"
    echo "   - Check service logs in logs/nginx/"
    echo ""
    echo "5. 📚 Documentation:"
    echo "   - Full guide: deploy/CLOUDFLARE_MULTI_SERVICE_GUIDE.md"
    echo "   - Troubleshooting section included"
    echo ""
    echo "🔗 Quick Status Check:"
    echo "   docker-compose -f docker-compose.uat.yml ps"
    echo "   docker logs familycart-uat-proxy"
}

# Main execution
main() {
    echo "Multi-Service Nginx Deployment Script"
    echo "====================================="
    echo ""
    
    # Confirm deployment
    read -p "Deploy multi-service nginx configuration? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deployment cancelled"
        exit 0
    fi
    
    check_sudo
    setup_directories
    backup_current_config
    check_ssl_certificates
    test_nginx_config
    check_upstream_services
    deploy_configuration
    run_tests
    show_next_steps
    
    echo ""
    echo "✅ Multi-service nginx deployment completed successfully!"
}

# Run main function
main "$@"
