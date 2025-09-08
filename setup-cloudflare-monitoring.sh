#!/bin/bash

# CloudFlare UAT Monitoring Setup Script
# Sets up external access to UAT monitoring services via CloudFlare
# Deploys to /opt/familycart-uat-repo (UAT environment)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="monitoring.uat.familycart.app"
PROMETHEUS_SUBDOMAIN="prometheus.monitoring.uat.familycart.app"
ALERTS_SUBDOMAIN="alerts.monitoring.uat.familycart.app"
UAT_REPO_PATH="/opt/familycart-uat-repo"
DEV_REPO_PATH="/home/honzik/GitHub/FamilyCart/FamilyCart"

echo -e "${BLUE}🔧 CloudFlare UAT Monitoring Setup${NC}"
echo "=================================="
echo -e "${YELLOW}📍 UAT Deployment Path: ${UAT_REPO_PATH}${NC}"
echo -e "${YELLOW}🌐 Primary Domain: ${DOMAIN}${NC}"

# Check if running as root for htpasswd generation
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}❌ Please don't run this script as root${NC}"
    exit 1
fi

# Check UAT repo exists
if [ ! -d "${UAT_REPO_PATH}" ]; then
    echo -e "${RED}❌ UAT repository not found at ${UAT_REPO_PATH}${NC}"
    echo -e "${YELLOW}Please ensure UAT environment is properly deployed${NC}"
    exit 1
fi

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

# Check if apache2-utils is installed (for htpasswd)
if ! command -v htpasswd &> /dev/null; then
    echo -e "${YELLOW}⚠️  Installing apache2-utils for htpasswd...${NC}"
    sudo apt update && sudo apt install -y apache2-utils
fi

# Check if openssl is installed
if ! command -v openssl &> /dev/null; then
    echo -e "${RED}❌ OpenSSL not found. Please install OpenSSL${NC}"
    exit 1
fi

# Check if docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker is not running. Please start Docker${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites met${NC}"

# Copy docker-compose file to UAT repo
echo -e "${YELLOW}� Setting up UAT monitoring configuration...${NC}"
if [ ! -f "${DEV_REPO_PATH}/docker-compose.uat-monitoring.yml" ]; then
    echo -e "${RED}❌ docker-compose.uat-monitoring.yml not found in dev repo${NC}"
    exit 1
fi

cp "${DEV_REPO_PATH}/docker-compose.uat-monitoring.yml" "${UAT_REPO_PATH}/"
echo -e "${GREEN}✅ Copied monitoring compose file to UAT${NC}"

# Create directory structure in UAT repo
echo -e "${YELLOW}� Setting up UAT directory structure...${NC}"
cd "${UAT_REPO_PATH}"
mkdir -p nginx/auth logs/nginx-monitoring monitoring/grafana/{provisioning,dashboards}

# Check existing SSL certificates
echo -e "${YELLOW}🔒 Checking existing SSL certificates...${NC}"
if [ -f "nginx/ssl/uat.familycart.app.crt" ] && [ -f "nginx/ssl/uat.familycart.app.key" ]; then
    echo -e "${GREEN}✅ Found existing CloudFlare Origin certificates${NC}"
    echo -e "${BLUE}📝 We'll reuse these certificates for monitoring domain${NC}"
    
    # Copy/rename for monitoring domain usage
    cp nginx/ssl/uat.familycart.app.crt nginx/ssl/monitoring.uat.familycart.app.crt
    cp nginx/ssl/uat.familycart.app.key nginx/ssl/monitoring.uat.familycart.app.key
    echo -e "${GREEN}✅ SSL certificates prepared for monitoring domain${NC}"
else
    echo -e "${RED}❌ Expected UAT SSL certificates not found${NC}"
    echo -e "${YELLOW}Expected: nginx/ssl/uat.familycart.app.crt and nginx/ssl/uat.familycart.app.key${NC}"
    exit 1
fi

# Generate basic auth credentials
echo -e "${YELLOW}🔐 Setting up authentication...${NC}"

# Check if auth files already exist
if [ ! -f "nginx/auth/.htpasswd" ]; then
    echo -e "${BLUE}Creating basic auth for Grafana access (optional layer)${NC}"
    read -p "Create basic auth for Grafana? (y/N): " create_grafana_auth
    if [[ $create_grafana_auth =~ ^[Yy]$ ]]; then
        read -p "Enter username for Grafana basic auth: " grafana_user
        htpasswd -c nginx/auth/.htpasswd "$grafana_user"
    else
        # Create empty file to prevent nginx errors
        touch nginx/auth/.htpasswd
    fi
fi

if [ ! -f "nginx/auth/.htpasswd-admin" ]; then
    echo -e "${BLUE}Creating admin auth for Prometheus/Alertmanager access${NC}"
    read -p "Enter admin username for Prometheus/Alertmanager: " admin_user
    htpasswd -c nginx/auth/.htpasswd-admin "$admin_user"
fi

echo -e "${GREEN}✅ Authentication configured${NC}"

# Copy nginx configuration
echo -e "${YELLOW}📄 Extending existing UAT nginx configuration...${NC}"
if [ ! -f "${DEV_REPO_PATH}/nginx-uat-extended.conf" ]; then
    echo -e "${RED}❌ nginx-uat-extended.conf not found in dev repo${NC}"
    exit 1
fi

# Backup existing nginx config
if [ -f "nginx/uat.conf" ]; then
    cp nginx/uat.conf nginx/uat.conf.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}✅ Existing nginx config backed up${NC}"
fi

# Copy extended nginx configuration
cp "${DEV_REPO_PATH}/nginx-uat-extended.conf" nginx/uat.conf
echo -e "${GREEN}✅ Extended nginx configuration installed${NC}"
echo -e "${BLUE}📝 This config handles both UAT app AND monitoring domains${NC}"

# Environment file setup
echo -e "${YELLOW}⚙️  Setting up environment configuration...${NC}"

if [ ! -f ".env.monitoring" ]; then
    echo "# UAT Monitoring Environment Configuration" > .env.monitoring
    echo "GRAFANA_ADMIN_USER=admin" >> .env.monitoring
    
    # Generate secure password
    GRAFANA_PASSWORD=$(openssl rand -base64 32)
    echo "GRAFANA_ADMIN_PASSWORD=$GRAFANA_PASSWORD" >> .env.monitoring
    
    echo "# Database connection for monitoring" >> .env.monitoring
    echo "POSTGRES_USER=familycart_uat" >> .env.monitoring
    echo "POSTGRES_DB=familycart_uat" >> .env.monitoring
    
    # Copy UAT database password if exists
    if [ -f ".env" ]; then
        UAT_DB_PASS=$(grep "UAT_DB_PASSWORD" .env | cut -d '=' -f2)
        if [ ! -z "$UAT_DB_PASS" ]; then
            echo "UAT_DB_PASSWORD=$UAT_DB_PASS" >> .env.monitoring
        fi
    fi
    
    echo -e "${GREEN}✅ Environment file created${NC}"
    echo -e "${BLUE}🔑 Grafana admin password: $GRAFANA_PASSWORD${NC}"
    echo -e "${YELLOW}⚠️  Save this password! It's also in .env.monitoring${NC}"
else
    echo -e "${GREEN}✅ Environment file already exists${NC}"
fi

# Display next steps
echo ""
echo -e "${GREEN}🎉 UAT Monitoring Setup Complete!${NC}"
echo "=================================="
echo -e "${BLUE}📍 Deployment Location: ${UAT_REPO_PATH}${NC}"
echo ""
echo -e "${BLUE}🏗️  Architecture:${NC}"
echo "✅ Single nginx instance (uat-proxy) handles ALL traffic:"
echo "   - uat.familycart.app → UAT Application"  
echo "   - monitoring.uat.familycart.app → Grafana Dashboard"
echo "   - prometheus.monitoring.uat.familycart.app → Prometheus API (restricted)"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "1. 🌐 Configure CloudFlare DNS:"
echo "   - A/AAAA record: monitoring.uat.familycart.app → YOUR_SERVER_IP"
echo "   - CNAME record: prometheus.monitoring.uat.familycart.app → monitoring.uat.familycart.app"
echo ""
echo "2. � Restart UAT services with new nginx config:"
echo "   cd ${UAT_REPO_PATH}"
echo "   docker-compose -f docker-compose.uat.yml down"
echo "   docker-compose -f docker-compose.uat.yml up -d"
echo ""
echo "3. 🚀 Start monitoring services:"
echo "   docker-compose -f docker-compose.uat-monitoring.yml up -d"
echo ""
echo "4. 🛡️  Configure CloudFlare Access (Recommended):"
echo "   - See cloudflare-access-config.md for detailed setup"
echo ""
echo "5. 🌍 Test access:"
echo "   - UAT App: https://uat.familycart.app"
echo "   - Monitoring: https://monitoring.uat.familycart.app" 
echo "   - Prometheus: https://prometheus.monitoring.uat.familycart.app"
echo ""
echo -e "${YELLOW}⚠️  Important: The existing uat-proxy nginx will handle all domains${NC}"
echo -e "${YELLOW}    No port conflicts - single nginx on 80/443${NC}"
