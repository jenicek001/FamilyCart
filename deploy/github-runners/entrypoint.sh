#!/bin/bash
set -e

# FamilyCart GitHub Runner Entrypoint Script

# Default values
RUNNER_NAME=${RUNNER_NAME:-"self-hosted-$(hostname)"}
RUNNER_WORK_DIRECTORY=${RUNNER_WORK_DIRECTORY:-"/home/runner/work"}
RUNNER_LABELS=${RUNNER_LABELS:-"self-hosted,familycart,ubuntu,docker"}
RUNNER_GROUP=${RUNNER_GROUP:-"default"}

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

# Validate required environment variables
validate_env() {
    log "Validating environment variables..."
    
    if [[ -z "$GITHUB_OWNER" ]]; then
        error "GITHUB_OWNER environment variable is required"
    fi
    
    if [[ -z "$GITHUB_REPO" ]]; then
        error "GITHUB_REPO environment variable is required"
    fi
    
    if [[ -z "$GITHUB_TOKEN" ]]; then
        error "GITHUB_TOKEN environment variable is required"
    fi
    
    log "Environment validation successful"
}

# Configure the runner
configure_runner() {
    log "Configuring GitHub runner: $RUNNER_NAME"
    
    # Create work directory
    mkdir -p "$RUNNER_WORK_DIRECTORY"
    
    # Check if runner is already configured
    if [[ -f ".runner" ]]; then
        warn "Runner appears to already be configured, removing old configuration..."
        ./config.sh remove --unattended || warn "Failed to remove existing configuration"
    fi
    
    # Get fresh registration token
    log "Fetching registration token from GitHub..."
    local response=$(curl -s -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/runners/registration-token")
    
    local reg_token=$(echo "$response" | sed -n 's/.*"token"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
    
    if [[ -z "$reg_token" ]]; then
        error "Failed to get registration token. Response: $response"
    fi
    
    log "Registration token obtained successfully"
    
    # Configure the runner
    log "Configuring runner for https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}"
    
    ./config.sh \
        --url "https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}" \
        --token "$reg_token" \
        --name "$RUNNER_NAME" \
        --work "$RUNNER_WORK_DIRECTORY" \
        --labels "$RUNNER_LABELS" \
        --runnergroup "$RUNNER_GROUP" \
        --unattended \
        --replace
    
    if [[ $? -eq 0 ]]; then
        log "Runner configuration successful"
    else
        error "Runner configuration failed"
    fi
}

# Start the runner
start_runner() {
    log "Starting GitHub runner: $RUNNER_NAME"
    
    # Set up signal handlers for graceful shutdown
    trap 'shutdown_runner' SIGTERM SIGINT
    
    # Start the runner
    ./run.sh &
    local runner_pid=$!
    
    log "Runner started with PID: $runner_pid"
    
    # Wait for runner process
    wait $runner_pid
    local exit_code=$?
    
    log "Runner process exited with code: $exit_code"
    exit $exit_code
}

# Graceful shutdown
shutdown_runner() {
    log "Received shutdown signal, cleaning up..."
    
    # Remove runner configuration
    if [[ -f ".runner" ]]; then
        log "Removing runner configuration..."
        ./config.sh remove --unattended || warn "Failed to remove runner configuration"
    fi
    
    log "Shutdown complete"
    exit 0
}

# Health check function
health_check() {
    if pgrep -f "Runner.Listener" > /dev/null; then
        log "Health check: Runner is healthy"
        return 0
    else
        error "Health check: Runner is not running"
        return 1
    fi
}

# Display system information
show_system_info() {
    info "=== System Information ==="
    info "Hostname: $(hostname)"
    info "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
    info "Architecture: $(uname -m)"
    info "CPU cores: $(nproc)"
    info "Memory: $(free -h | awk 'NR==2{printf "%.1f GB", $2/1024/1024/1024}')"
    info "Docker version: $(docker --version 2>/dev/null || echo 'Not available')"
    info "Node.js version: $(node --version 2>/dev/null || echo 'Not available')"
    info "Python version: $(python3 --version 2>/dev/null || echo 'Not available')"
    info "Poetry version: $(poetry --version 2>/dev/null || echo 'Not available')"
    info "================================="
}

# Display runner configuration
show_runner_info() {
    info "=== Runner Configuration ==="
    info "Runner Name: $RUNNER_NAME"
    info "Repository: https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}"
    info "Work Directory: $RUNNER_WORK_DIRECTORY"
    info "Labels: $RUNNER_LABELS"
    info "Runner Group: $RUNNER_GROUP"
    info "================================="
}

# Main execution
main() {
    log "🚀 Starting FamilyCart GitHub Runner"
    
    show_system_info
    show_runner_info
    
    # Handle special commands
    case "${1:-}" in
        "health")
            health_check
            exit $?
            ;;
        "version")
            info "Runner version: $(cat .runner 2>/dev/null | jq -r '.agentVersion' || echo 'Not configured')"
            exit 0
            ;;
        "configure-only")
            validate_env
            configure_runner
            log "Runner configured successfully, exiting"
            exit 0
            ;;
    esac
    
    # Normal startup process
    validate_env
    configure_runner
    start_runner
}

# Run main function with all arguments
main "$@"