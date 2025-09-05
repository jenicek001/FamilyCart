#!/bin/bash
set -e

# FamilyCart GitHub Runner Configuration Script

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

# Configuration function
configure_runner() {
    local github_url="${1:-}"
    local github_token="${2:-}"
    local runner_name="${3:-"self-hosted-$(hostname)"}"
    local runner_labels="${4:-"self-hosted,familycart,ubuntu,docker"}"
    local runner_group="${5:-"default"}"
    local work_dir="${6:-"/home/runner/work"}"
    
    if [[ -z "$github_url" ]] || [[ -z "$github_token" ]]; then
        error "Usage: configure-runner.sh <github_url> <github_token> [runner_name] [labels] [group] [work_dir]"
    fi
    
    log "Configuring runner: $runner_name"
    log "Repository: $github_url"
    log "Labels: $runner_labels"
    
    # Create work directory
    mkdir -p "$work_dir"
    
    # Remove existing configuration if present
    if [[ -f ".runner" ]]; then
        warn "Removing existing runner configuration..."
        ./config.sh remove --token "$github_token" --unattended || true
    fi
    
    # Configure the runner
    ./config.sh \
        --url "$github_url" \
        --token "$github_token" \
        --name "$runner_name" \
        --work "$work_dir" \
        --labels "$runner_labels" \
        --runnergroup "$runner_group" \
        --unattended \
        --replace
    
    if [[ $? -eq 0 ]]; then
        log "Runner configuration successful"
        
        # Display runner information
        if [[ -f ".runner" ]]; then
            info "Runner configured with ID: $(cat .runner | jq -r '.agentId' 2>/dev/null || echo 'Unknown')"
            info "Runner version: $(cat .runner | jq -r '.agentVersion' 2>/dev/null || echo 'Unknown')"
        fi
    else
        error "Runner configuration failed"
    fi
}

# Main execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    configure_runner "$@"
fi
