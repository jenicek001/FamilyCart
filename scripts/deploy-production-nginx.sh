#!/bin/bash
###############################################################################
# FamilyCart Production NGINX Deployment Script
# 
# Purpose: Deploy optimized NGINX configuration to production (VM2)
# Based on: UAT config analysis + 2025 best practices + Cloudflare integration
# 
# Usage: 
#   Local machine: ./scripts/deploy-production-nginx.sh
#   (Script will SSH to VM2 and deploy configuration)
#
# Prerequisites:
#   - SSH access to VM2 configured (~/.ssh/familycart_oci)
#   - Cloudflare Origin Certificates already installed on VM2
#   - Backend/frontend containers running on VM2
#   - Repository cloned on local machine
#
###############################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VM2_IP="158.180.30.112"
VM2_USER="ubuntu"
SSH_KEY="$HOME/.ssh/familycart_oci"
REPO_DIR="/opt/familycart-repo"
APP_DIR="/opt/familycart-app"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check SSH key
    if [ ! -f "$SSH_KEY" ]; then
        log_error "SSH key not found: $SSH_KEY"
        exit 1
    fi
    
    # Check repository directory
    if [ ! -d "nginx" ]; then
        log_error "Must run from FamilyCart repository root"
        log_info "Current directory: $(pwd)"
        exit 1
    fi
    
    # Check VM2 connectivity
    if ! ssh -i "$SSH_KEY" -o ConnectTimeout=5 -o BatchMode=yes "${VM2_USER}@${VM2_IP}" "echo 'Connected'" &>/dev/null; then
        log_error "Cannot connect to VM2 (${VM2_IP})"
        exit 1
    fi
    
    log_success "All prerequisites met"
}

backup_existing_config() {
    log_info "Creating backup of existing NGINX configuration on VM2..."
    
    ssh -i "$SSH_KEY" "${VM2_USER}@${VM2_IP}" "bash -s" <<'ENDSSH'
        if [ -d "/etc/nginx/sites-available" ]; then
            BACKUP_DIR="/etc/nginx/backup-$(date +%Y%m%d-%H%M%S)"
            sudo mkdir -p "$BACKUP_DIR"
            sudo cp -r /etc/nginx/sites-available "$BACKUP_DIR/" 2>/dev/null || true
            sudo cp -r /etc/nginx/sites-enabled "$BACKUP_DIR/" 2>/dev/null || true
            sudo cp -r /etc/nginx/conf.d "$BACKUP_DIR/" 2>/dev/null || true
            echo "$BACKUP_DIR"
        fi
ENDSSH
    
    log_success "Backup created"
}

deploy_config_files() {
    log_info "Deploying NGINX configuration files to VM2..."
    
    # Create temporary directory on VM2
    TEMP_DIR=$(ssh -i "$SSH_KEY" "${VM2_USER}@${VM2_IP}" "mktemp -d")
    log_info "Created temporary directory: $TEMP_DIR"
    
    # Copy configuration files to temporary directory
    log_info "Copying sites-available/familycart-production..."
    scp -i "$SSH_KEY" nginx/sites-available/familycart-production "${VM2_USER}@${VM2_IP}:${TEMP_DIR}/"
    
    log_info "Copying conf.d files..."
    scp -i "$SSH_KEY" nginx/conf.d/ssl-common.conf "${VM2_USER}@${VM2_IP}:${TEMP_DIR}/"
    scp -i "$SSH_KEY" nginx/conf.d/cloudflare-realip.conf "${VM2_USER}@${VM2_IP}:${TEMP_DIR}/"
    scp -i "$SSH_KEY" nginx/conf.d/rate-limiting.conf "${VM2_USER}@${VM2_IP}:${TEMP_DIR}/"
    scp -i "$SSH_KEY" nginx/conf.d/upstreams.conf "${VM2_USER}@${VM2_IP}:${TEMP_DIR}/"
    
    # Move files to proper locations on VM2
    log_info "Installing configuration files..."
    ssh -i "$SSH_KEY" "${VM2_USER}@${VM2_IP}" "bash -s" <<ENDSSH
        # Move site configuration
        sudo cp ${TEMP_DIR}/familycart-production /etc/nginx/sites-available/
        
        # Move conf.d files
        sudo cp ${TEMP_DIR}/ssl-common.conf /etc/nginx/conf.d/
        sudo cp ${TEMP_DIR}/cloudflare-realip.conf /etc/nginx/conf.d/
        sudo cp ${TEMP_DIR}/rate-limiting.conf /etc/nginx/conf.d/
        sudo cp ${TEMP_DIR}/upstreams.conf /etc/nginx/conf.d/
        
        # Set proper permissions
        sudo chmod 644 /etc/nginx/sites-available/familycart-production
        sudo chmod 644 /etc/nginx/conf.d/ssl-common.conf
        sudo chmod 644 /etc/nginx/conf.d/cloudflare-realip.conf
        sudo chmod 644 /etc/nginx/conf.d/rate-limiting.conf
        sudo chmod 644 /etc/nginx/conf.d/upstreams.conf
        
        # Clean up temporary directory
        rm -rf ${TEMP_DIR}
ENDSSH
    
    log_success "Configuration files deployed"
}

enable_production_site() {
    log_info "Enabling production site..."
    
    ssh -i "$SSH_KEY" "${VM2_USER}@${VM2_IP}" "bash -s" <<'ENDSSH'
        # Enable production site
        sudo ln -sf /etc/nginx/sites-available/familycart-production /etc/nginx/sites-enabled/
        
        # Remove default site if exists
        if [ -L /etc/nginx/sites-enabled/default ]; then
            sudo rm /etc/nginx/sites-enabled/default
            echo "Removed default site"
        fi
        
        # List enabled sites
        echo "Enabled sites:"
        ls -la /etc/nginx/sites-enabled/
ENDSSH
    
    log_success "Production site enabled"
}

test_nginx_config() {
    log_info "Testing NGINX configuration..."
    
    TEST_OUTPUT=$(ssh -i "$SSH_KEY" "${VM2_USER}@${VM2_IP}" "sudo nginx -t 2>&1" || true)
    
    if echo "$TEST_OUTPUT" | grep -q "syntax is ok"; then
        log_success "NGINX configuration test passed"
        echo "$TEST_OUTPUT"
        return 0
    else
        log_error "NGINX configuration test failed"
        echo "$TEST_OUTPUT"
        return 1
    fi
}

check_certificates() {
    log_info "Verifying SSL certificates..."
    
    ssh -i "$SSH_KEY" "${VM2_USER}@${VM2_IP}" "bash -s" <<'ENDSSH'
        if [ -f /etc/nginx/ssl/cloudflare/origin-cert.pem ]; then
            echo "Certificate found:"
            sudo openssl x509 -in /etc/nginx/ssl/cloudflare/origin-cert.pem -noout -subject -issuer -dates -ext subjectAltName
        else
            echo "ERROR: Certificate not found at /etc/nginx/ssl/cloudflare/origin-cert.pem"
            exit 1
        fi
        
        if [ -f /etc/nginx/ssl/cloudflare/origin-key.pem ]; then
            echo "Private key found and readable"
        else
            echo "ERROR: Private key not found at /etc/nginx/ssl/cloudflare/origin-key.pem"
            exit 1
        fi
ENDSSH
    
    log_success "SSL certificates verified"
}

update_backend_env() {
    log_info "Updating backend environment variables..."
    
    ssh -i "$SSH_KEY" "${VM2_USER}@${VM2_IP}" "bash -s" <<ENDSSH
        cd ${APP_DIR}
        
        # Create backup of .env.app
        sudo cp .env.app .env.app.backup-\$(date +%Y%m%d-%H%M%S)
        
        # Update CORS_ORIGINS
        sudo sed -i 's|CORS_ORIGINS=.*|CORS_ORIGINS=["https://familycart.app","https://www.familycart.app"]|g' .env.app
        
        # Update NEXT_PUBLIC_API_URL (if exists)
        if grep -q "NEXT_PUBLIC_API_URL" .env.app; then
            sudo sed -i 's|NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=https://familycart.app/api|g' .env.app
        else
            echo "NEXT_PUBLIC_API_URL=https://familycart.app/api" | sudo tee -a .env.app
        fi
        
        echo "Updated environment variables:"
        grep -E "(CORS_ORIGINS|NEXT_PUBLIC_API_URL)" .env.app
ENDSSH
    
    log_success "Backend environment updated"
}

restart_services() {
    log_info "Restarting backend and frontend containers..."
    
    ssh -i "$SSH_KEY" "${VM2_USER}@${VM2_IP}" "bash -s" <<ENDSSH
        cd ${APP_DIR}
        sudo docker compose restart backend frontend
        
        # Wait for services to be healthy
        echo "Waiting for services to be healthy..."
        sleep 5
        
        # Check service status
        sudo docker compose ps backend frontend
ENDSSH
    
    log_success "Services restarted"
}

start_nginx() {
    log_info "Starting NGINX..."
    
    ssh -i "$SSH_KEY" "${VM2_USER}@${VM2_IP}" "bash -s" <<'ENDSSH'
        # Check if nginx is already running
        if sudo systemctl is-active --quiet nginx; then
            echo "NGINX is running, reloading configuration..."
            sudo systemctl reload nginx
        else
            echo "Starting NGINX..."
            sudo systemctl start nginx
        fi
        
        # Enable on boot
        sudo systemctl enable nginx
        
        # Check status
        sudo systemctl status nginx --no-pager
ENDSSH
    
    log_success "NGINX started"
}

verify_deployment() {
    log_info "Verifying deployment..."
    
    # Test local health endpoints
    log_info "Testing backend health (localhost:8000)..."
    ssh -i "$SSH_KEY" "${VM2_USER}@${VM2_IP}" "curl -s -o /dev/null -w 'HTTP %{http_code} - %{time_total}s\n' http://localhost:8000/health"
    
    log_info "Testing frontend health (localhost:3000)..."
    ssh -i "$SSH_KEY" "${VM2_USER}@${VM2_IP}" "curl -s -o /dev/null -w 'HTTP %{http_code} - %{time_total}s\n' http://localhost:3000/"
    
    # Test NGINX listening
    log_info "Checking NGINX listening ports..."
    ssh -i "$SSH_KEY" "${VM2_USER}@${VM2_IP}" "sudo netstat -tlnp | grep nginx"
    
    log_success "Deployment verification complete"
}

print_next_steps() {
    echo ""
    log_info "======================================================================"
    log_success "Production NGINX deployment complete!"
    log_info "======================================================================"
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Configure Cloudflare DNS:"
    echo "   - Point familycart.app (A record) → ${VM2_IP} (Proxied: ON)"
    echo "   - Point www.familycart.app (A record) → ${VM2_IP} (Proxied: ON)"
    echo "   - Add redirect domains: familycart.cz, .eu, nakoupit.app, .com"
    echo ""
    echo "2. Configure Cloudflare SSL/TLS:"
    echo "   - SSL/TLS encryption mode: Full (strict)"
    echo "   - Enable: Always Use HTTPS, Automatic HTTPS Rewrites"
    echo "   - Enable: HSTS (with includeSubDomains)"
    echo ""
    echo "3. Configure Cloudflare Redirect Rules:"
    echo "   - familycart.cz → familycart.app"
    echo "   - familycart.eu → familycart.app"
    echo "   - nakoupit.app → familycart.app"
    echo "   - nakoupit.com → familycart.app"
    echo ""
    echo "4. Test production endpoints (after DNS propagation):"
    echo "   curl -I https://familycart.app/health"
    echo "   curl -I https://familycart.app/"
    echo "   curl -I https://familycart.app/api/v1/health"
    echo ""
    echo "5. Verify SSL configuration:"
    echo "   https://www.ssllabs.com/ssltest/analyze.html?d=familycart.app"
    echo ""
    echo "6. Verify security headers:"
    echo "   https://securityheaders.com/?q=familycart.app"
    echo ""
    echo "Logs:"
    echo "   Access: /var/log/nginx/familycart-production.access.log"
    echo "   Error:  /var/log/nginx/familycart-production.error.log"
    echo ""
}

# Main execution
main() {
    log_info "Starting FamilyCart Production NGINX Deployment"
    echo ""
    
    check_prerequisites
    backup_existing_config
    check_certificates
    deploy_config_files
    enable_production_site
    
    if test_nginx_config; then
        update_backend_env
        restart_services
        start_nginx
        verify_deployment
        print_next_steps
    else
        log_error "Deployment failed due to NGINX configuration errors"
        log_warning "Configuration files have been deployed but NGINX was not started"
        log_info "Fix the errors and run: ssh -i $SSH_KEY ${VM2_USER}@${VM2_IP} 'sudo nginx -t'"
        exit 1
    fi
}

# Run main function
main
