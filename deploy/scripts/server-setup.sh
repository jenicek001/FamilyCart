#!/bin/bash
set -euo pipefail

# FamilyCart Self-Hosted Ubuntu Server Setup Script
# This script prepares an Ubuntu server for hosting GitHub runners and UAT environment

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root (use sudo)"
    fi
}

# System update and basic packages
update_system() {
    log "Updating system packages..."
    
    apt-get update
    apt-get upgrade -y
    
    # Install essential packages
    apt-get install -y \
        curl \
        wget \
        git \
        jq \
        unzip \
        tar \
        htop \
        tree \
        nano \
        vim \
        net-tools \
        ufw \
        fail2ban \
        unattended-upgrades \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        software-properties-common
    
    log "System update completed"
}

# Install Docker and Docker Compose
install_docker() {
    log "Installing Docker and Docker Compose..."
    
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Enable and start Docker
    systemctl enable docker
    systemctl start docker
    
    # Add current user to docker group
    if [[ -n "${SUDO_USER:-}" ]]; then
        usermod -aG docker "$SUDO_USER"
        log "Added $SUDO_USER to docker group"
    fi
    
    log "Docker installation completed"
}

# Configure firewall
setup_firewall() {
    log "Configuring firewall..."
    
    # Reset UFW to defaults
    ufw --force reset
    
    # Set default policies
    ufw default deny incoming
    ufw default allow outgoing
    
    # Allow SSH (custom port recommended)
    read -p "Enter SSH port (default 22): " ssh_port
    ssh_port=${ssh_port:-22}
    ufw allow "$ssh_port"/tcp comment 'SSH'
    
    # Allow HTTP and HTTPS for UAT
    ufw allow 80/tcp comment 'HTTP UAT'
    ufw allow 443/tcp comment 'HTTPS UAT'
    
    # Allow specific ports for services
    ufw allow 9090/tcp comment 'Prometheus'
    ufw allow 3000/tcp comment 'Grafana'
    
    # Enable firewall
    ufw --force enable
    
    log "Firewall configuration completed"
    
    if [[ "$ssh_port" != "22" ]]; then
        warn "Don't forget to update SSH configuration to use port $ssh_port"
        warn "Edit /etc/ssh/sshd_config and set Port $ssh_port"
        warn "Then restart SSH: systemctl restart ssh"
    fi
}

# Setup fail2ban for intrusion prevention
setup_fail2ban() {
    log "Configuring fail2ban..."
    
    # Create jail.local configuration
    cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 3

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10

[nginx-botsearch]
enabled = true
filter = nginx-botsearch
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 2
EOF
    
    # Restart fail2ban
    systemctl restart fail2ban
    systemctl enable fail2ban
    
    log "Fail2ban configuration completed"
}

# Create directory structure
create_directories() {
    log "Creating directory structure..."
    
    # Main directories
    mkdir -p /opt/familycart-uat
    mkdir -p /opt/github-runners
    mkdir -p /opt/monitoring
    mkdir -p /opt/backups
    mkdir -p /opt/logs
    mkdir -p /opt/scripts
    
    # SSL certificates directory
    mkdir -p /opt/ssl
    
    # Set permissions
    chown -R root:root /opt/
    chmod 755 /opt/familycart-uat
    chmod 755 /opt/github-runners
    chmod 755 /opt/monitoring
    chmod 700 /opt/backups
    chmod 755 /opt/logs
    chmod 755 /opt/scripts
    chmod 700 /opt/ssl
    
    log "Directory structure created"
}

# Install additional development tools
install_dev_tools() {
    log "Installing development tools..."
    
    # Node.js 20
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs
    
    # Python 3.11
    add-apt-repository -y ppa:deadsnakes/ppa
    apt-get update
    apt-get install -y python3.11 python3.11-dev python3.11-distutils python3-pip
    
    # Poetry
    curl -sSL https://install.python-poetry.org | python3 -
    ln -sf /root/.local/bin/poetry /usr/local/bin/poetry
    
    # k6 for load testing
    wget https://github.com/grafana/k6/releases/download/v0.47.0/k6-v0.47.0-linux-amd64.tar.gz
    tar -xzf k6-v0.47.0-linux-amd64.tar.gz
    mv k6-v0.47.0-linux-amd64/k6 /usr/local/bin/
    rm -rf k6-v0.47.0-linux-amd64*
    
    log "Development tools installed"
}

# Configure automatic updates
setup_auto_updates() {
    log "Configuring automatic updates..."
    
    # Configure unattended upgrades
    cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'EOF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}";
    "${distro_id}:${distro_codename}-security";
    "${distro_id}:${distro_codename}-updates";
    "${distro_id}ESMApps:${distro_codename}-apps-security";
    "${distro_id}ESM:${distro_codename}-infra-security";
};

Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Remove-New-Unused-Dependencies "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
EOF
    
    # Enable automatic updates
    cat > /etc/apt/apt.conf.d/20auto-upgrades << 'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
EOF
    
    log "Automatic updates configured"
}

# Create system monitoring script
create_monitoring() {
    log "Setting up system monitoring..."
    
    cat > /opt/scripts/system-monitor.sh << 'EOF'
#!/bin/bash
# System monitoring script for FamilyCart server

LOG_FILE="/opt/logs/system-monitor.log"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check disk space
check_disk_space() {
    local usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [[ $usage -gt 85 ]]; then
        log "WARNING: Disk usage is ${usage}%"
        return 1
    fi
    return 0
}

# Check memory usage
check_memory() {
    local usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    if (( $(echo "$usage > 90" | bc -l) )); then
        log "WARNING: Memory usage is ${usage}%"
        return 1
    fi
    return 0
}

# Check CPU load
check_cpu_load() {
    local load=$(uptime | awk -F'load average:' '{ print $2 }' | awk '{ print $1 }' | sed 's/,//')
    local cpu_count=$(nproc)
    if (( $(echo "$load > $cpu_count * 2" | bc -l) )); then
        log "WARNING: High CPU load: $load (CPUs: $cpu_count)"
        return 1
    fi
    return 0
}

# Check Docker containers
check_docker() {
    local unhealthy=$(docker ps --filter health=unhealthy --format "table {{.Names}}" | tail -n +2 | wc -l)
    if [[ $unhealthy -gt 0 ]]; then
        log "WARNING: $unhealthy unhealthy Docker containers"
        docker ps --filter health=unhealthy --format "table {{.Names}}\t{{.Status}}" | tail -n +2 | while read line; do
            log "  Unhealthy container: $line"
        done
        return 1
    fi
    return 0
}

# Main monitoring function
main() {
    log "Starting system monitoring check"
    
    local issues=0
    
    check_disk_space || ((issues++))
    check_memory || ((issues++))
    check_cpu_load || ((issues++))
    check_docker || ((issues++))
    
    if [[ $issues -eq 0 ]]; then
        log "System monitoring: All checks passed"
    else
        log "System monitoring: $issues issues detected"
    fi
    
    return $issues
}

main "$@"
EOF
    
    chmod +x /opt/scripts/system-monitor.sh
    
    # Create cron job
    cat > /etc/cron.d/system-monitor << 'EOF'
# System monitoring every 10 minutes
*/10 * * * * root /opt/scripts/system-monitor.sh
EOF
    
    log "System monitoring configured"
}

# Display final information
show_final_info() {
    log "🎉 FamilyCart server setup completed!"
    echo ""
    info "=== Next Steps ==="
    info "1. Reboot the server to apply all changes"
    info "2. Configure SSH key-based authentication"
    info "3. Set up GitHub runners using: /opt/scripts/setup-github-runners.sh"
    info "4. Deploy UAT environment using docker-compose files"
    info "5. Configure SSL certificates for HTTPS"
    echo ""
    info "=== Important Files ==="
    info "• System logs: /var/log/"
    info "• FamilyCart logs: /opt/logs/"
    info "• UAT deployment: /opt/familycart-uat/"
    info "• GitHub runners: /opt/github-runners/"
    info "• Scripts: /opt/scripts/"
    info "• SSL certificates: /opt/ssl/"
    echo ""
    info "=== Monitoring ==="
    info "• System monitor: /opt/scripts/system-monitor.sh"
    info "• Firewall status: ufw status verbose"
    info "• Docker status: docker ps"
    info "• Fail2ban status: fail2ban-client status"
    echo ""
    warn "Remember to:"
    warn "• Change default SSH port and disable password authentication"
    warn "• Set up proper SSL certificates for production use"
    warn "• Configure backup procedures for important data"
    warn "• Review and adjust firewall rules as needed"
    warn "• Set up monitoring alerts for critical issues"
}

# Main execution
main() {
    log "🚀 Starting FamilyCart Self-Hosted Server Setup"
    
    check_root
    update_system
    install_docker
    install_dev_tools
    create_directories
    setup_firewall
    setup_fail2ban
    setup_auto_updates
    create_monitoring
    show_final_info
    
    log "✅ Setup completed successfully!"
}

# Run main function
main "$@"