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

# Get registration token from GitHub API
get_registration_token() {
    log "Getting registration token for https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}"
    
    # Clean the PAT token (remove any whitespace/newlines)
    local clean_pat=$(echo "${GITHUB_PAT}" | tr -d '\n\r\t ')
    
    local token_response=$(curl -L \
        -X POST \
        -H "Accept: application/vnd.github+json" \
        -H "Authorization: Bearer ${clean_pat}" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/runners/registration-token \
        2>/dev/null)
    
    if [[ $? -ne 0 ]]; then
        error "Failed to get registration token from GitHub API"
    fi
    
    local registration_token=$(echo "$token_response" | jq -r '.token' | tr -d '\n\r\t ')
    
    if [[ -z "$registration_token" || "$registration_token" == "null" ]]; then
        error "Invalid registration token received from GitHub API"
    fi
    
    echo "$registration_token"
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
    
    if [[ -z "$GITHUB_PAT" ]]; then
        error "GITHUB_PAT environment variable is required"
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
        warn "Runner appears to already be configured, checking configuration..."
        
        # Read existing configuration
        local configured_url=$(jq -r '.gitHubUrl' .runner 2>/dev/null || echo "")
        local expected_url="https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}"
        
        if [[ "$configured_url" == "$expected_url" ]]; then
            log "Runner is already configured for the correct repository"
            return 0
        else
            warn "Runner configured for different repository, reconfiguring..."
            # Get registration token for removal
            local removal_token=$(get_registration_token)
            ./config.sh remove --token "$removal_token" || warn "Failed to remove existing configuration"
        fi
    fi
    
    # Get fresh registration token
    local registration_token=$(get_registration_token)
    
    # Configure the runner
    log "Configuring runner for https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}"
    
    ./config.sh \
        --url "https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}" \
        --token "$registration_token" \
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
        local removal_token=$(get_registration_token)
        ./config.sh remove --token "$removal_token" --unattended || warn "Failed to remove runner configuration"
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