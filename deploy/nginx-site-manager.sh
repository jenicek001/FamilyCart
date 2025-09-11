#!/bin/bash
# nginx-site-manager.sh
# Script to manage nginx sites (enable/disable/list/test)

set -e

NGINX_SITES_AVAILABLE="/home/honzik/GitHub/FamilyCart/FamilyCart/deploy/nginx/sites-available"
NGINX_SITES_ENABLED="/home/honzik/GitHub/FamilyCart/FamilyCart/deploy/nginx/sites-enabled"
NGINX_CONFIG="/home/honzik/GitHub/FamilyCart/FamilyCart/deploy/nginx/nginx.conf"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_usage() {
    echo "Usage: $0 {enable|disable|list|test|reload} [site-name]"
    echo ""
    echo "Commands:"
    echo "  enable <site>    Enable a site (create symlink in sites-enabled)"
    echo "  disable <site>   Disable a site (remove symlink from sites-enabled)"
    echo "  list             List all available and enabled sites"
    echo "  test             Test nginx configuration"
    echo "  reload           Reload nginx configuration (if running in container)"
    echo ""
    echo "Examples:"
    echo "  $0 enable familycart-uat"
    echo "  $0 disable grafana"
    echo "  $0 list"
    echo "  $0 test"
}

enable_site() {
    local site=$1
    
    if [ -z "$site" ]; then
        echo -e "${RED}Error: Site name required${NC}"
        print_usage
        exit 1
    fi
    
    if [ ! -f "$NGINX_SITES_AVAILABLE/$site" ]; then
        echo -e "${RED}Error: Site '$site' not found in sites-available${NC}"
        echo "Available sites:"
        ls -1 "$NGINX_SITES_AVAILABLE/" | sed 's/^/  /'
        exit 1
    fi
    
    if [ -L "$NGINX_SITES_ENABLED/$site" ]; then
        echo -e "${YELLOW}Site '$site' is already enabled${NC}"
        exit 0
    fi
    
    echo -e "${BLUE}Enabling site: $site${NC}"
    ln -s "$NGINX_SITES_AVAILABLE/$site" "$NGINX_SITES_ENABLED/$site"
    echo -e "${GREEN}✅ Site '$site' enabled successfully${NC}"
    
    # Test configuration
    test_config
}

disable_site() {
    local site=$1
    
    if [ -z "$site" ]; then
        echo -e "${RED}Error: Site name required${NC}"
        print_usage
        exit 1
    fi
    
    if [ ! -L "$NGINX_SITES_ENABLED/$site" ]; then
        echo -e "${YELLOW}Site '$site' is not enabled${NC}"
        exit 0
    fi
    
    echo -e "${BLUE}Disabling site: $site${NC}"
    rm "$NGINX_SITES_ENABLED/$site"
    echo -e "${GREEN}✅ Site '$site' disabled successfully${NC}"
}

list_sites() {
    echo -e "${BLUE}📁 Available Sites:${NC}"
    if [ -d "$NGINX_SITES_AVAILABLE" ] && [ "$(ls -A $NGINX_SITES_AVAILABLE 2>/dev/null)" ]; then
        for site in "$NGINX_SITES_AVAILABLE"/*; do
            site_name=$(basename "$site")
            if [ -L "$NGINX_SITES_ENABLED/$site_name" ]; then
                echo -e "  ${GREEN}✅ $site_name${NC} (enabled)"
            else
                echo -e "  ${YELLOW}⭕ $site_name${NC} (available)"
            fi
        done
    else
        echo -e "  ${YELLOW}No sites available${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}🔗 Enabled Sites:${NC}"
    if [ -d "$NGINX_SITES_ENABLED" ] && [ "$(ls -A $NGINX_SITES_ENABLED 2>/dev/null)" ]; then
        for site in "$NGINX_SITES_ENABLED"/*; do
            if [ -L "$site" ]; then
                site_name=$(basename "$site")
                target=$(readlink "$site")
                echo -e "  ${GREEN}✅ $site_name${NC} → $target"
            fi
        done
    else
        echo -e "  ${YELLOW}No sites enabled${NC}"
    fi
}

test_config() {
    echo -e "${BLUE}🧪 Testing nginx configuration...${NC}"
    
    # Test using docker if available
    if command -v docker >/dev/null 2>&1; then
        # Create a temporary hosts file for testing that resolves upstreams to localhost
        TEMP_HOSTS_FILE=$(mktemp)
        cat > "$TEMP_HOSTS_FILE" << 'EOF'
127.0.0.1 uat-backend
127.0.0.1 uat-frontend  
127.0.0.1 uat-prometheus
127.0.0.1 homeassistant_service
EOF

        if docker run --rm \
           -v "$NGINX_CONFIG:/etc/nginx/nginx.conf:ro" \
           -v "$NGINX_SITES_AVAILABLE:/etc/nginx/sites-available:ro" \
           -v "$NGINX_SITES_ENABLED:/etc/nginx/sites-enabled:ro" \
           -v "$(dirname $NGINX_CONFIG)/conf.d:/etc/nginx/conf.d:ro" \
           -v "$TEMP_HOSTS_FILE:/etc/hosts:ro" \
           nginx:alpine nginx -t 2>/dev/null; then
            echo -e "${GREEN}✅ Nginx configuration syntax is valid${NC}"
            rm -f "$TEMP_HOSTS_FILE"
            return 0
        else
            echo -e "${RED}❌ Nginx configuration has syntax errors${NC}"
            echo -e "${YELLOW}Detailed error output:${NC}"
            # Show detailed errors
            docker run --rm \
               -v "$NGINX_CONFIG:/etc/nginx/nginx.conf:ro" \
               -v "$NGINX_SITES_AVAILABLE:/etc/nginx/sites-available:ro" \
               -v "$NGINX_SITES_ENABLED:/etc/nginx/sites-enabled:ro" \
               -v "$(dirname $NGINX_CONFIG)/conf.d:/etc/nginx/conf.d:ro" \
               -v "$TEMP_HOSTS_FILE:/etc/hosts:ro" \
               nginx:alpine nginx -t
            rm -f "$TEMP_HOSTS_FILE"
            return 1
        fi
    else
        echo -e "${YELLOW}Docker not available, cannot test configuration${NC}"
        echo -e "${BLUE}💡 Install Docker to enable configuration testing${NC}"
        return 0
    fi
}

reload_nginx() {
    echo -e "${BLUE}🔄 Reloading nginx configuration...${NC}"
    
    # Try to reload nginx if running in a container
    if docker ps --format "table {{.Names}}" | grep -q "familycart-uat-proxy"; then
        if docker exec familycart-uat-proxy nginx -s reload; then
            echo -e "${GREEN}✅ Nginx configuration reloaded successfully${NC}"
        else
            echo -e "${RED}❌ Failed to reload nginx configuration${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}Nginx container not running${NC}"
        return 1
    fi
}

# Main command handling
case "$1" in
    enable)
        enable_site "$2"
        ;;
    disable)
        disable_site "$2"
        ;;
    list)
        list_sites
        ;;
    test)
        test_config
        ;;
    reload)
        reload_nginx
        ;;
    *)
        print_usage
        exit 1
        ;;
esac
