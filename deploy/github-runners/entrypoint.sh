#!/bin/bash
set -e

# FamilyCart GitHub Runner Entrypoint Script
# Based on GitHub's official documentation and best practices
# 
# References:
# - GitHub Actions Runner: https://github.com/actions/runner
# - Self-hosted runner configuration: https://docs.github.com/en/actions/hosting-your-own-runners
# - Runner authentication flow: https://github.com/actions/runner/blob/main/docs/res/runner-auth-diags.txt
# - Automation scripts: https://github.com/actions/runner/blob/main/docs/automate.md

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

# Logging functions following GitHub Actions patterns
# Based on GitHub's runner logging and workflow command documentation
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

info() {
    log "INFO: $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
    # Use GitHub Actions workflow command format for warnings
    echo "::warning::$1" >&2
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    # Use GitHub Actions workflow command format for errors
    echo "::error::$1" >&2
    exit 1
}

# GitHub Actions group logging for better organization
start_group() {
    echo "::group::$1" >&2
}

end_group() {
    echo "::endgroup::" >&2
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
    
    # Create work directory with proper permissions
    mkdir -p "$RUNNER_WORK_DIRECTORY"
    chmod 755 "$RUNNER_WORK_DIRECTORY"
    
    # Ensure the runner user owns the work directory
    if [[ $(id -u) -eq 0 ]]; then
        chown -R runner:runner "$RUNNER_WORK_DIRECTORY"
    fi
    
    # Fix Docker config directory permissions
    if [[ -d "/home/runner/.docker" ]]; then
        if [[ $(id -u) -eq 0 ]]; then
            # Fix ownership if running as root
            chown -R runner:runner /home/runner/.docker
        fi
        chmod -R 755 /home/runner/.docker
        if [[ -f "/home/runner/.docker/config.json" ]]; then
            chmod 644 /home/runner/.docker/config.json
        fi
    fi
    
    # Check if runner is already configured
    if [[ -f ".runner" ]]; then
        warn "Runner appears to already be configured, removing old configuration..."
        local removal_token=$(get_removal_token)
        if [[ -n "$removal_token" ]] && ./config.sh remove --token "$removal_token"; then
            log "Existing configuration removed successfully"
        else
            warn "Failed to remove existing configuration from GitHub, cleaning up local files..."
            rm -f .runner .credentials .credentials_rsaparams
            rm -rf _diag
        fi
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
    
    # Configure the runner following GitHub's official recommendations
    # Source: https://github.com/actions/runner/blob/main/docs/automate.md
    log "Configuring runner for https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}"
    
    # Use GitHub's recommended configuration approach
    ./config.sh \
        --url "https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}" \
        --token "$reg_token" \
        --name "$RUNNER_NAME" \
        --work "$RUNNER_WORK_DIRECTORY" \
        --labels "$RUNNER_LABELS" \
        --runnergroup "$RUNNER_GROUP" \
        --unattended \
        --replace \
        --ephemeral
    
    if [[ $? -eq 0 ]]; then
        log "Runner configuration successful"
    else
        error "Runner configuration failed"
    fi
}

# Start the runner following GitHub's official patterns
start_runner() {
    log "Starting GitHub runner: $RUNNER_NAME"
    
    # Set up signal handlers for graceful shutdown
    # Based on GitHub's container hook timeout handling
    trap 'shutdown_runner' SIGTERM SIGINT
    
    # Set up runner hooks if requested (following GitHub's official documentation)
    # Source: https://github.com/actions/runner/blob/main/docs/adrs/1751-runner-job-hooks.md
    if [[ -n "${ACTIONS_RUNNER_HOOK_JOB_STARTED:-}" ]]; then
        log "Job started hook configured: $ACTIONS_RUNNER_HOOK_JOB_STARTED"
        export ACTIONS_RUNNER_HOOK_JOB_STARTED
    fi
    
    if [[ -n "${ACTIONS_RUNNER_HOOK_JOB_COMPLETED:-}" ]]; then
        log "Job completed hook configured: $ACTIONS_RUNNER_HOOK_JOB_COMPLETED"
        export ACTIONS_RUNNER_HOOK_JOB_COMPLETED
    fi
    
    # Set up container hooks if requested
    if [[ -n "${ACTIONS_RUNNER_CONTAINER_HOOKS:-}" ]]; then
        log "Container hooks configured: $ACTIONS_RUNNER_CONTAINER_HOOKS"
        export ACTIONS_RUNNER_CONTAINER_HOOKS
    fi
    
    # Set up proxy environment variables if configured
    # Based on GitHub's proxy support documentation
    if [[ -n "${https_proxy:-}" ]]; then
        log "HTTPS proxy configured: $https_proxy"
        export https_proxy
    fi
    
    if [[ -n "${http_proxy:-}" ]]; then
        log "HTTP proxy configured: $http_proxy" 
        export http_proxy
    fi
    
    if [[ -n "${no_proxy:-}" ]]; then
        log "No proxy hosts configured: $no_proxy"
        export no_proxy
    fi
    
    # Verify runner binary exists and is executable
    if [[ ! -f "./run.sh" ]]; then
        error "Runner binary ./run.sh not found"
    fi
    
    if [[ ! -x "./run.sh" ]]; then
        log "Making run.sh executable"
        chmod +x ./run.sh
    fi
    
    # Start the runner with retry logic for robustness
    local max_retries=3
    local retry_count=0
    
    while [[ $retry_count -lt $max_retries ]]; do
        log "Starting runner attempt $((retry_count + 1))/$max_retries"
        
        # Start the runner in background
        ./run.sh &
        local runner_pid=$!
        
        log "Runner started with PID: $runner_pid"
        
        # Wait for the runner process
        wait $runner_pid
        local exit_code=$?
        
        log "Runner exited with code: $exit_code"
        
        # If exit code is 0, it's a normal shutdown
        if [[ $exit_code -eq 0 ]]; then
            log "Runner shutdown normally"
            break
        fi
        
        # If exit code is 2, it typically means the runner was stopped for update
        if [[ $exit_code -eq 2 ]]; then
            log "Runner stopped for update, will restart automatically"
            sleep 5
            continue
        fi
        
        # For other exit codes, increment retry counter
        retry_count=$((retry_count + 1))
        
        if [[ $retry_count -lt $max_retries ]]; then
            warn "Runner failed with exit code $exit_code, retrying in 10 seconds..."
            sleep 10
        else
            error "Runner failed $max_retries times, giving up"
        fi
    done
    local exit_code=$?
    
    log "Runner process exited with code: $exit_code"
    exit $exit_code
}

# Get runner removal token
get_removal_token() {
    local response=$(curl -s -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/runners/remove-token")
    
    local removal_token=$(echo "$response" | sed -n 's/.*"token"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
    
    if [[ -n "$removal_token" ]]; then
        echo "$removal_token"
    else
        warn "Failed to get removal token. Response: $response"
        return 1
    fi
}

# Graceful shutdown following GitHub's signal handling best practices
# Based on GitHub's container hook timeout handling documentation
shutdown_runner() {
    log "Received shutdown signal, cleaning up..."
    
    # First, try to gracefully stop the runner process
    local runner_pid=$(pgrep -f "Runner.Listener" || echo "")
    if [[ -n "$runner_pid" ]]; then
        log "Stopping Runner.Listener process (PID: $runner_pid)"
        kill -TERM "$runner_pid" 2>/dev/null || true
        
        # Wait for graceful shutdown with timeout
        for i in {1..10}; do
            if ! pgrep -f "Runner.Listener" > /dev/null; then
                log "Runner.Listener stopped gracefully"
                break
            fi
            sleep 1
        done
        
        # Force kill if still running
        if pgrep -f "Runner.Listener" > /dev/null; then
            log "Force stopping Runner.Listener"
            kill -KILL "$runner_pid" 2>/dev/null || true
        fi
    fi
    
    # Remove runner configuration if it exists (for ephemeral runners)
    if [[ -f ".credentials" ]] && [[ -f ".runner" ]]; then
        log "Removing runner configuration..."
        
        # Get removal token
        local response=$(curl -s -X POST \
            -H "Authorization: token $GITHUB_TOKEN" \
            -H "Accept: application/vnd.github.v3+json" \
            "https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/runners/remove-token")
        
        local removal_token=$(echo "$response" | sed -n 's/.*"token"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
        
        if [[ -n "$removal_token" ]]; then
            timeout 30 ./config.sh remove --token "$removal_token" || {
                warn "Failed to remove runner configuration with removal token"
            }
        else
            warn "Failed to get removal token, attempting force removal"
            timeout 15 ./config.sh remove --unattended || {
                warn "Failed to remove runner configuration"
            }
        fi
    fi
    
    log "Shutdown complete"
    exit 0
}

# Health check function following GitHub's authentication flow documentation
# Source: https://github.com/actions/runner/blob/main/docs/res/runner-auth-diags.txt
health_check() {
    # Primary check: Runner.Listener process should be running for active runner
    if pgrep -f "Runner.Listener" > /dev/null; then
        log "Health check: Runner.Listener is healthy and active"
        return 0
    fi
    
    # Secondary check: For ephemeral runners, configuration files indicate ready state
    # Based on GitHub's self-hosted runner configuration process
    if [[ -f ".runner" ]] && [[ -f ".credentials" ]]; then
        # Verify configuration is valid by checking key fields
        if jq -e '.agentVersion and .gitHubUrl and .agentName' .runner >/dev/null 2>&1; then
            log "Health check: Runner configuration is valid (may be between jobs)"
            return 0
        fi
    fi
    
    # Tertiary check: Check if runner is in configuration phase
    if pgrep -f "config.sh" > /dev/null; then
        log "Health check: Runner is being configured"
        return 0
    fi
    
    # Check if entrypoint process is still active (startup phase)
    if pgrep -f "entrypoint.sh" > /dev/null; then
        log "Health check: Runner is starting up"
        return 0
    fi
    
    # Check for any GitHub Actions worker processes (job execution)
    if pgrep -f "Runner.Worker" > /dev/null; then
        log "Health check: Runner worker process is active"
        return 0
    fi
    
    # Runner is not running and not starting up
    warn "Health check: Runner is not running"
    return 1
}

# Display system information using GitHub's group logging format
show_system_info() {
    start_group "System Information"
    info "Hostname: $(hostname)"
    info "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
    info "Architecture: $(uname -m)"
    info "CPU cores: $(nproc)"
    
    # Improved memory detection for Docker containers
    local mem_bytes=$(cat /sys/fs/cgroup/memory/memory.limit_in_bytes 2>/dev/null || echo "0")
    local mem_usage=$(cat /sys/fs/cgroup/memory/memory.usage_in_bytes 2>/dev/null || echo "0")
    
    if command -v bc >/dev/null 2>&1 && [[ "$mem_bytes" != "0" ]] && [[ "$mem_bytes" != "9223372036854775807" ]]; then
        local mem_gb=$(echo "scale=1; $mem_bytes / 1024 / 1024 / 1024" | bc -l 2>/dev/null || echo "0.0")
        local usage_gb=$(echo "scale=1; $mem_usage / 1024 / 1024 / 1024" | bc -l 2>/dev/null || echo "0.0")
        info "Container Memory Limit: ${mem_gb} GB (Used: ${usage_gb} GB)"
    else
        # Fallback to system memory if cgroup info unavailable or bc missing
        local sys_mem=$(free -h | awk 'NR==2{print $2}' 2>/dev/null || echo "Unknown")
        info "System Memory: ${sys_mem} (Docker container - limited visibility)"
        
        # Also show available memory for diagnostics
        local avail_mem=$(free -h | awk 'NR==2{print $7}' 2>/dev/null || echo "Unknown")
        info "Available Memory: ${avail_mem}"
    fi
    info "Docker version: $(docker --version 2>/dev/null || echo 'Not available')"
    info "Node.js version: $(node --version 2>/dev/null || echo 'Not available')"
    info "Python version: $(python3 --version 2>/dev/null || echo 'Not available')"
    info "Poetry version: $(poetry --version 2>/dev/null || echo 'Not available')"
    end_group
}

# Display runner configuration using GitHub's group logging format
show_runner_info() {
    start_group "Runner Configuration"
    info "Runner Name: $RUNNER_NAME"
    info "Repository: https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}"
    info "Work Directory: $RUNNER_WORK_DIRECTORY"
    info "Labels: $RUNNER_LABELS"
    info "Runner Group: $RUNNER_GROUP"
    end_group
}

# Pre-startup connectivity checks based on GitHub's official diagnostics
# Source: https://github.com/actions/runner/blob/main/docs/checks/actions.md
check_github_connectivity() {
    log "Performing GitHub connectivity checks..."
    
    # Check basic internet connectivity to GitHub
    if ! curl -s --max-time 10 https://api.github.com/zen > /dev/null; then
        warn "Cannot reach GitHub API (api.github.com)"
        return 1
    fi
    
    # Check Actions-specific endpoints
    if ! curl -s --max-time 10 https://vstoken.actions.githubusercontent.com/_apis/health > /dev/null; then
        warn "Cannot reach GitHub Actions token service"
        return 1
    fi
    
    if ! curl -s --max-time 10 https://pipelines.actions.githubusercontent.com/_apis/health > /dev/null; then
        warn "Cannot reach GitHub Actions pipeline service"
        return 1
    fi
    
    log "✅ GitHub connectivity checks passed"
    return 0
}

# Main execution
main() {
    log "🚀 Starting FamilyCart GitHub Runner"
    
    show_system_info
    show_runner_info
    
    # Perform connectivity checks before proceeding
    if ! check_github_connectivity; then
        warn "GitHub connectivity issues detected, but continuing startup..."
        sleep 5
    fi    # Handle special commands
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