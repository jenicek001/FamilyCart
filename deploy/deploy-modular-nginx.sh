#!/bin/bash
# deploy-modular-nginx.sh  
# Script to deploy the new modular nginx configuration

set -e

PROJECT_ROOT="/home/honzik/GitHub/FamilyCart/FamilyCart"
NGINX_DIR="$PROJECT_ROOT/deploy/nginx"
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.uat.yml"

echo "🚀 Deploying Modular Nginx Configuration"
echo "========================================="

# Function to backup current configuration
backup_current_config() {
    echo "💾 Backing up current configuration..."
    
    BACKUP_DIR="$PROJECT_ROOT/deploy/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup current nginx config if it exists
    if [ -f "$NGINX_DIR/uat.conf" ]; then
        cp "$NGINX_DIR/uat.conf" "$BACKUP_DIR/uat.conf.backup"
    fi
    
    if [ -f "$NGINX_DIR/multi-service.conf" ]; then
        cp "$NGINX_DIR/multi-service.conf" "$BACKUP_DIR/multi-service.conf.backup"
    fi
    
    if [ -f "$DOCKER_COMPOSE_FILE" ]; then
        cp "$DOCKER_COMPOSE_FILE" "$BACKUP_DIR/docker-compose.uat.yml.backup"
    fi
    
    echo "✅ Configuration backed up to $BACKUP_DIR"
}

# Function to enable default sites
enable_default_sites() {
    echo "🔗 Enabling default sites..."
    
    # Enable FamilyCart UAT (always enabled)
    ./nginx-site-manager.sh enable familycart-uat
    
    # Enable default catch-all
    ./nginx-site-manager.sh enable default
    
    echo "✅ Default sites enabled"
}

# Function to update docker-compose
update_docker_compose() {
    echo "🐳 Updating Docker Compose configuration..."
    
    # Update the nginx configuration path in docker-compose
    if grep -q "uat.conf\|multi-service.conf" "$DOCKER_COMPOSE_FILE"; then
        sed -i 's|./deploy/nginx/[^:]*\.conf:/etc/nginx/nginx\.conf:ro|./deploy/nginx/nginx.conf:/etc/nginx/nginx.conf:ro|g' "$DOCKER_COMPOSE_FILE"
        echo "✅ Updated nginx.conf path in docker-compose"
    fi
    
    # Check if volume mounts need to be added for modular structure
    if ! grep -q "sites-available" "$DOCKER_COMPOSE_FILE"; then
        echo "⚠️  Docker Compose needs manual updates for modular nginx structure"
        echo "   Please add these volume mounts to uat-proxy service:"
        echo "   - ./deploy/nginx/sites-available:/etc/nginx/sites-available:ro"
        echo "   - ./deploy/nginx/sites-enabled:/etc/nginx/sites-enabled:ro"
        echo "   - ./deploy/nginx/conf.d:/etc/nginx/conf.d:ro"
        echo "   - ./deploy/nginx/ssl:/etc/nginx/ssl:ro"
    fi
}

# Function to test configuration
test_configuration() {
    echo "🧪 Testing modular nginx configuration..."
    
    if ./nginx-site-manager.sh test; then
        echo "✅ Configuration test passed"
    else
        echo "❌ Configuration test failed"
        exit 1
    fi
}

# Function to deploy
deploy_configuration() {
    echo "🚀 Deploying configuration..."
    
    cd "$PROJECT_ROOT"
    
    # Stop current services
    echo "🛑 Stopping current services..."
    docker-compose -f docker-compose.uat.yml down
    
    # Start services with new configuration
    echo "▶️  Starting services with modular configuration..."
    docker-compose -f docker-compose.uat.yml up -d
    
    # Wait for nginx to start
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    # Check if nginx is running
    if docker ps | grep -q "familycart-uat-proxy"; then
        echo "✅ Nginx proxy container is running"
    else
        echo "❌ Nginx proxy container failed to start"
        echo "   Check logs: docker logs familycart-uat-proxy"
        exit 1
    fi
}

# Function to show management commands
show_management_info() {
    echo ""
    echo "🎉 Modular Nginx Deployment Complete!"
    echo "====================================="
    echo ""
    echo "📋 Site Management Commands:"
    echo "  ./nginx-site-manager.sh list                    # List all sites"
    echo "  ./nginx-site-manager.sh enable grafana          # Enable Grafana"
    echo "  ./nginx-site-manager.sh enable homeassistant    # Enable Home Assistant"
    echo "  ./nginx-site-manager.sh disable grafana         # Disable Grafana"
    echo "  ./nginx-site-manager.sh test                    # Test configuration"
    echo "  ./nginx-site-manager.sh reload                  # Reload nginx"
    echo ""
    echo "📁 Directory Structure:"
    echo "  deploy/nginx/"
    echo "  ├── nginx.conf              # Main configuration"
    echo "  ├── conf.d/                 # Shared configs (SSL, upstreams, etc.)"
    echo "  ├── sites-available/        # Available site configurations"
    echo "  ├── sites-enabled/          # Enabled sites (symlinks)"
    echo "  └── ssl/                    # SSL certificates by domain"
    echo ""
    echo "🔧 Next Steps:"
    echo "1. Install SSL certificates: ./setup-ssl-certificates.sh"
    echo "2. Enable additional services:"
    echo "   ./nginx-site-manager.sh enable grafana"
    echo "   ./nginx-site-manager.sh enable homeassistant"
    echo "3. Test and reload: ./nginx-site-manager.sh test && ./nginx-site-manager.sh reload"
}

# Main execution
main() {
    echo "This will deploy the new modular nginx configuration."
    echo ""
    read -p "Continue with deployment? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deployment cancelled"
        exit 0
    fi
    
    backup_current_config
    enable_default_sites
    test_configuration
    update_docker_compose
    deploy_configuration
    show_management_info
    
    echo ""
    echo "✅ Modular nginx deployment completed successfully!"
}

# Run main function
main "$@"
