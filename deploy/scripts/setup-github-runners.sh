#!/bin/bash
set -euo pipefail

# FamilyCart GitHub Self-Hosted Runners Setup Script
# This script sets up multiple GitHub self-hosted runners for the FamilyCart repository

# Configuration
GITHUB_OWNER="jenicek001"
GITHUB_REPO="FamilyCart"
RUNNER_COUNT=3
BASE_DIR="/opt/github-runners"
RUNNER_VERSION="2.317.0"  # Update to latest version as needed
WORK_DIR="/opt/github-runners-work"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root (use sudo)"
    fi
}

# Install dependencies
install_dependencies() {
    log "Installing dependencies..."
    
    apt-get update
    apt-get install -y \
        curl \
        tar \
        jq \
        docker.io \
        docker-compose-plugin \
        python3 \
        python3-pip \
        nodejs \
        npm \
        git \
        wget \
        unzip \
        build-essential \
        libssl-dev \
        libffi-dev
    
    # Install Poetry
    if ! command -v poetry &> /dev/null; then
        log "Installing Poetry..."
        curl -sSL https://install.python-poetry.org | python3 -
        ln -sf /root/.local/bin/poetry /usr/local/bin/poetry
    fi
    
    # Install k6 for load testing
    if ! command -v k6 &> /dev/null; then
        log "Installing k6..."
        wget https://github.com/grafana/k6/releases/download/v0.47.0/k6-v0.47.0-linux-amd64.tar.gz
        tar -xzf k6-v0.47.0-linux-amd64.tar.gz
        mv k6-v0.47.0-linux-amd64/k6 /usr/local/bin/
        rm -rf k6-v0.47.0-linux-amd64*
    fi
    
    log "Dependencies installed successfully"
}

# Create runner user and directories
setup_directories() {
    log "Setting up directories and user..."
    
    # Create github-runner user
    if ! id "github-runner" &>/dev/null; then
        useradd -m -s /bin/bash github-runner
        usermod -aG docker github-runner
    fi
    
    # Create directories
    mkdir -p "$BASE_DIR"
    mkdir -p "$WORK_DIR"
    mkdir -p "/var/log/github-runners"
    
    # Set permissions
    chown -R github-runner:github-runner "$BASE_DIR"
    chown -R github-runner:github-runner "$WORK_DIR"
    chown -R github-runner:github-runner "/var/log/github-runners"
    
    log "Directories setup complete"
}

# Download and extract GitHub runner
download_runner() {
    log "Downloading GitHub runner..."
    
    cd "$BASE_DIR"
    
    # Download runner if not already present
    if [[ ! -f "actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz" ]]; then
        wget "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"
    fi
    
    log "GitHub runner downloaded"
}

# Setup individual runner
setup_runner() {
    local runner_id=$1
    local runner_name="self-hosted-${runner_id}"
    local runner_dir="${BASE_DIR}/runner-${runner_id}"
    
    log "Setting up runner: $runner_name"
    
    # Create runner directory
    mkdir -p "$runner_dir"
    cd "$runner_dir"
    
    # Extract runner if not already done
    if [[ ! -f "run.sh" ]]; then
        tar xzf "${BASE_DIR}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz"
    fi
    
    # Configure runner (this requires a GitHub token)
    log "Note: Runner $runner_name ready for configuration"
    log "To configure, run as github-runner user:"
    log "  cd $runner_dir"
    log "  ./config.sh --url https://github.com/$GITHUB_OWNER/$GITHUB_REPO --token YOUR_GITHUB_TOKEN --name $runner_name --work ${WORK_DIR}/runner-${runner_id}"
    
    # Set permissions
    chown -R github-runner:github-runner "$runner_dir"
    
    # Create systemd service
    create_systemd_service "$runner_id" "$runner_name" "$runner_dir"
}

# Create systemd service for runner
create_systemd_service() {
    local runner_id=$1
    local runner_name=$2
    local runner_dir=$3
    
    log "Creating systemd service for $runner_name"
    
    cat > "/etc/systemd/system/github-runner-${runner_id}.service" << EOF
[Unit]
Description=GitHub Actions Runner ($runner_name)
After=network.target
Wants=network.target

[Service]
Type=simple
User=github-runner
Group=github-runner
WorkingDirectory=$runner_dir
ExecStart=$runner_dir/run.sh
Restart=always
RestartSec=5
KillMode=process
KillSignal=SIGTERM
TimeoutStopSec=5m

# Environment variables
Environment=DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1
Environment=RUNNER_MANUALLY_TRAP_SIG=1
Environment=ACTIONS_RUNNER_PRINT_LOG_TO_STDOUT=1

# Security settings
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$runner_dir
ReadWritePaths=$WORK_DIR/runner-${runner_id}
ReadWritePaths=/var/log/github-runners
ReadWritePaths=/tmp
ReadWritePaths=/var/run/docker.sock

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=github-runner-$runner_id

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable "github-runner-${runner_id}.service"
    
    log "Systemd service created for $runner_name"
}

# Create Docker configuration for runners
setup_docker_for_runners() {
    log "Configuring Docker for GitHub runners..."
    
    # Create Docker daemon configuration
    mkdir -p /etc/docker
    cat > /etc/docker/daemon.json << EOF
{
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "100m",
        "max-file": "3"
    },
    "storage-driver": "overlay2",
    "features": {
        "buildkit": true
    },
    "registry-mirrors": [],
    "insecure-registries": [],
    "default-ulimits": {
        "nofile": {
            "Hard": 64000,
            "Name": "nofile",
            "Soft": 64000
        }
    }
}
EOF
    
    # Restart Docker
    systemctl restart docker
    systemctl enable docker
    
    # Add github-runner to docker group (already done above)
    
    log "Docker configuration complete"
}

# Create monitoring script
create_monitoring_script() {
    log "Creating monitoring script..."
    
    cat > "/usr/local/bin/monitor-github-runners.sh" << 'EOF'
#!/bin/bash
# GitHub Runners Monitoring Script

RUNNER_COUNT=3
LOG_FILE="/var/log/github-runners/monitor.log"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_runner() {
    local runner_id=$1
    local service_name="github-runner-${runner_id}.service"
    
    if systemctl is-active --quiet "$service_name"; then
        log "✅ Runner $runner_id is running"
        return 0
    else
        log "❌ Runner $runner_id is not running"
        
        # Try to restart
        log "🔄 Attempting to restart runner $runner_id"
        systemctl restart "$service_name"
        sleep 5
        
        if systemctl is-active --quiet "$service_name"; then
            log "✅ Runner $runner_id restarted successfully"
            return 0
        else
            log "❌ Failed to restart runner $runner_id"
            return 1
        fi
    fi
}

# Check system resources
check_system() {
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
    local mem_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    
    log "💻 System Status - CPU: ${cpu_usage}%, Memory: ${mem_usage}%, Disk: ${disk_usage}%"
    
    # Alert on high resource usage
    if (( $(echo "$cpu_usage > 90" | bc -l) )); then
        log "⚠️  HIGH CPU USAGE: ${cpu_usage}%"
    fi
    
    if (( $(echo "$mem_usage > 85" | bc -l) )); then
        log "⚠️  HIGH MEMORY USAGE: ${mem_usage}%"
    fi
    
    if [[ $disk_usage -gt 85 ]]; then
        log "⚠️  HIGH DISK USAGE: ${disk_usage}%"
    fi
}

# Main monitoring loop
main() {
    log "🚀 Starting GitHub runners monitoring"
    
    check_system
    
    local failed_runners=0
    for i in $(seq 1 $RUNNER_COUNT); do
        if ! check_runner $i; then
            ((failed_runners++))
        fi
    done
    
    if [[ $failed_runners -eq 0 ]]; then
        log "✅ All runners are healthy"
    else
        log "❌ $failed_runners runners are unhealthy"
    fi
    
    log "📊 Monitoring check completed"
}

main "$@"
EOF
    
    chmod +x "/usr/local/bin/monitor-github-runners.sh"
    
    # Create cron job for monitoring
    cat > "/etc/cron.d/github-runners-monitor" << EOF
# Monitor GitHub runners every 5 minutes
*/5 * * * * root /usr/local/bin/monitor-github-runners.sh
EOF
    
    log "Monitoring script created"
}

# Create management scripts
create_management_scripts() {
    log "Creating management scripts..."
    
    # Start all runners script
    cat > "/usr/local/bin/start-github-runners.sh" << EOF
#!/bin/bash
for i in {1..$RUNNER_COUNT}; do
    echo "Starting runner \$i..."
    systemctl start github-runner-\$i.service
done
echo "All runners started"
EOF
    
    # Stop all runners script
    cat > "/usr/local/bin/stop-github-runners.sh" << EOF
#!/bin/bash
for i in {1..$RUNNER_COUNT}; do
    echo "Stopping runner \$i..."
    systemctl stop github-runner-\$i.service
done
echo "All runners stopped"
EOF
    
    # Status check script
    cat > "/usr/local/bin/status-github-runners.sh" << EOF
#!/bin/bash
echo "GitHub Runners Status:"
echo "====================="
for i in {1..$RUNNER_COUNT}; do
    status=\$(systemctl is-active github-runner-\$i.service)
    echo "Runner \$i: \$status"
done
echo ""
echo "System Resources:"
echo "================"
echo "CPU: \$(top -bn1 | grep "Cpu(s)" | awk '{print \$2}')"
echo "Memory: \$(free -h | grep Mem | awk '{print \$3 "/" \$2}')"
echo "Disk: \$(df -h / | tail -1 | awk '{print \$3 "/" \$2 " (" \$5 " used)"}')"
EOF
    
    chmod +x /usr/local/bin/{start,stop,status}-github-runners.sh
    
    log "Management scripts created"
}

# Main setup function
main() {
    log "Starting FamilyCart GitHub Runners setup..."
    
    check_root
    install_dependencies
    setup_directories
    setup_docker_for_runners
    download_runner
    
    # Setup individual runners
    for i in $(seq 1 $RUNNER_COUNT); do
        setup_runner $i
    done
    
    create_monitoring_script
    create_management_scripts
    
    log "✅ GitHub Runners setup completed!"
    echo ""
    log "📋 Next Steps:"
    log "1. Generate GitHub token with repo:all and workflow permissions"
    log "2. Configure each runner by running as github-runner user:"
    for i in $(seq 1 $RUNNER_COUNT); do
        log "   sudo -u github-runner bash -c 'cd ${BASE_DIR}/runner-${i} && ./config.sh --url https://github.com/$GITHUB_OWNER/$GITHUB_REPO --token YOUR_TOKEN --name self-hosted-${i} --work ${WORK_DIR}/runner-${i}'"
    done
    log "3. Start all runners: /usr/local/bin/start-github-runners.sh"
    log "4. Check status: /usr/local/bin/status-github-runners.sh"
    echo ""
    warn "Remember to:"
    warn "- Keep your GitHub token secure and rotate it regularly"
    warn "- Monitor runner performance and resource usage"
    warn "- Keep the runner software updated"
    warn "- Review runner logs regularly: journalctl -u github-runner-1.service -f"
}

# Run main function
main "$@"