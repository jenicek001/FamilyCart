#!/bin/bash
set -e

# FamilyCart GitHub Runner Entrypoint Script
RUNNER_NAME=${RUNNER_NAME:-"familycart-self-hosted-$(hostname)"}
RUNNER_WORK_DIRECTORY=${RUNNER_WORK_DIRECTORY:-"/home/runner/work"}
RUNNER_LABELS=${RUNNER_LABELS:-"self-hosted,familycart,ubuntu,docker"}
RUNNER_GROUP=${RUNNER_GROUP:-"default"}

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

error() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1" >&2
    exit 1
}

# Validate environment
if [[ -z "$GITHUB_OWNER" ]]; then error "GITHUB_OWNER is required"; fi
if [[ -z "$GITHUB_REPO" ]]; then error "GITHUB_REPO is required"; fi  
if [[ -z "$GITHUB_TOKEN" ]]; then error "GITHUB_TOKEN is required"; fi

log "🚀 Starting GitHub Runner: $RUNNER_NAME"
log "Repository: https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}"

# Clean token and get registration token
CLEAN_TOKEN=$(printf "%s" "$GITHUB_TOKEN" | tr -d '\n\r\t ')
log "Getting registration token from GitHub API..."

REGISTRATION_TOKEN=$(curl -s -X POST \
    -H "Authorization: token ${CLEAN_TOKEN}" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/runners/registration-token" \
    | jq -r '.token' 2>/dev/null || echo "")

if [[ -z "$REGISTRATION_TOKEN" || "$REGISTRATION_TOKEN" == "null" ]]; then
    error "Failed to get registration token from GitHub API"
fi

log "Registration token obtained successfully"

# Create work directory
mkdir -p "$RUNNER_WORK_DIRECTORY"

# Remove existing runner if configured
if [[ -f ".runner" ]]; then
    log "Removing existing runner configuration..."
    ./config.sh remove --token "$REGISTRATION_TOKEN" --unattended || true
fi

# Configure runner
log "Configuring runner..."
./config.sh \
    --url "https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}" \
    --token "$REGISTRATION_TOKEN" \
    --name "$RUNNER_NAME" \
    --work "$RUNNER_WORK_DIRECTORY" \
    --labels "$RUNNER_LABELS" \
    --runnergroup "$RUNNER_GROUP" \
    --unattended \
    --replace

if [[ $? -ne 0 ]]; then
    error "Runner configuration failed"
fi

log "✅ Runner configured successfully"

# Set up cleanup on exit
cleanup() {
    log "Cleaning up runner..."
    if [[ -f ".runner" ]]; then
        # Get new registration token for cleanup
        NEW_TOKEN=$(curl -s -X POST \
            -H "Authorization: token ${CLEAN_TOKEN}" \
            -H "Accept: application/vnd.github.v3+json" \
            "https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/runners/registration-token" \
            | jq -r '.token' 2>/dev/null || echo "")
        
        if [[ -n "$NEW_TOKEN" && "$NEW_TOKEN" != "null" ]]; then
            ./config.sh remove --token "$NEW_TOKEN" --unattended || true
        fi
    fi
    log "Cleanup complete"
}

trap 'cleanup' SIGTERM SIGINT EXIT

# Start runner
log "🏃 Starting runner process..."
exec ./run.sh
