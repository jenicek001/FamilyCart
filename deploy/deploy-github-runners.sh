#!/bin/bash
set -e

# FamilyCart GitHub Runners Deployment Script
# This script sets up and deploys self-hosted GitHub runners for FamilyCart

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

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
UAT_REPO_DIR="/opt/familycart-uat-repo"
RUNNERS_DIR="$UAT_REPO_DIR/github-runners"
DOCKER_COMPOSE_FILE="$UAT_REPO_DIR/docker-compose.runners.yml"

# Default configuration
DEFAULT_GITHUB_OWNER="honzik"
DEFAULT_GITHUB_REPO="FamilyCart"
DEFAULT_RUNNER_COUNT=3

show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Deploy FamilyCart GitHub self-hosted runners"
    echo ""
    echo "Options:"
    echo "  -t, --token TOKEN        GitHub personal access token (required)"
    echo "  -o, --owner OWNER        GitHub repository owner (default: $DEFAULT_GITHUB_OWNER)"
    echo "  -r, --repo REPO          GitHub repository name (default: $DEFAULT_GITHUB_REPO)"
    echo "  -c, --count COUNT        Number of runners to deploy (default: $DEFAULT_RUNNER_COUNT)"
    echo "  -s, --stop               Stop and remove all runners"
    echo "  -u, --update             Update runner images and restart"
    echo "  --status                 Show current runner status"
    echo "  --logs [RUNNER_NAME]     Show logs for specific runner or all"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --token ghp_xxxxxxxxxxxx"
    echo "  $0 --token ghp_xxxxxxxxxxxx --count 5"
    echo "  $0 --stop"
    echo "  $0 --status"
    echo "  $0 --logs familycart-runner-1"
}

# Parse command line arguments
parse_args() {
    GITHUB_TOKEN=""
    GITHUB_OWNER="$DEFAULT_GITHUB_OWNER"
    GITHUB_REPO="$DEFAULT_GITHUB_REPO"
    RUNNER_COUNT="$DEFAULT_RUNNER_COUNT"
    ACTION="deploy"
    RUNNER_NAME=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--token)
                GITHUB_TOKEN="$2"
                shift 2
                ;;
            -o|--owner)
                GITHUB_OWNER="$2"
                shift 2
                ;;
            -r|--repo)
                GITHUB_REPO="$2"
                shift 2
                ;;
            -c|--count)
                RUNNER_COUNT="$2"
                shift 2
                ;;
            -s|--stop)
                ACTION="stop"
                shift
                ;;
            -u|--update)
                ACTION="update"
                shift
                ;;
            --status)
                ACTION="status"
                shift
                ;;
            --logs)
                ACTION="logs"
                if [[ -n "$2" ]] && [[ ! "$2" =~ ^- ]]; then
                    RUNNER_NAME="$2"
                    shift 2
                else
                    shift
                fi
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                ;;
        esac
    done
}

# Validate GitHub token
validate_token() {
    if [[ -z "$GITHUB_TOKEN" ]] && [[ "$ACTION" == "deploy" || "$ACTION" == "update" ]]; then
        error "GitHub token is required for deployment. Use --token option."
    fi
    
    if [[ -n "$GITHUB_TOKEN" ]]; then
        log "Validating GitHub token..."
        
        # Test token by checking user info
        if ! curl -s -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/user >/dev/null 2>&1; then
            error "Invalid GitHub token or no internet connection"
        fi
        
        # Test repository access
        if ! curl -s -H "Authorization: Bearer $GITHUB_TOKEN" "https://api.github.com/repos/$GITHUB_OWNER/$GITHUB_REPO" >/dev/null 2>&1; then
            error "Cannot access repository $GITHUB_OWNER/$GITHUB_REPO with provided token"
        fi
        
        log "GitHub token validation successful"
    fi
}

# Setup directories and files
setup_directories() {
    log "Setting up directories and files..."
    
    # Create UAT repository directory if it doesn't exist
    if [[ ! -d "$UAT_REPO_DIR" ]]; then
        log "Creating UAT repository directory: $UAT_REPO_DIR"
        sudo mkdir -p "$UAT_REPO_DIR"
        sudo chown -R "$USER:$USER" "$UAT_REPO_DIR"
    fi
    
    # Copy GitHub runners configuration
    if [[ ! -d "$RUNNERS_DIR" ]]; then
        log "Copying GitHub runners configuration..."
        cp -r "$PROJECT_ROOT/deploy/github-runners" "$UAT_REPO_DIR/"
        chmod +x "$RUNNERS_DIR"/*.sh
    fi
    
    # Copy docker-compose.runners.yml if it doesn't exist
    if [[ ! -f "$DOCKER_COMPOSE_FILE" ]]; then
        log "Copying docker-compose.runners.yml..."
        cp "$PROJECT_ROOT/docker-compose.runners.yml" "$UAT_REPO_DIR/"
    fi
    
    log "Directory setup complete"
}

# Build runner Docker image
build_runner_image() {
    log "Building GitHub runner Docker image..."
    
    cd "$RUNNERS_DIR"
    
    # Check if image exists and get build date
    local image_exists=$(docker images -q familycart/github-runner:latest 2>/dev/null)
    if [[ -n "$image_exists" ]]; then
        local image_created=$(docker inspect --format='{{.Created}}' familycart/github-runner:latest 2>/dev/null | cut -d'T' -f1)
        info "Existing image found (created: $image_created)"
        
        # Check if we need to rebuild (if Dockerfile is newer than image)
        if [[ "Dockerfile" -nt <(docker inspect --format='{{.Created}}' familycart/github-runner:latest) ]]; then
            warn "Dockerfile is newer than image, rebuilding..."
        else
            log "Using existing image"
            return 0
        fi
    fi
    
    # Build the image
    log "Building Docker image (this may take several minutes)..."
    docker build -t familycart/github-runner:latest . || error "Failed to build Docker image"
    
    log "Docker image build successful"
}

# Generate environment file for runners
generate_env_file() {
    local env_file="$UAT_REPO_DIR/.env.runners"
    
    log "Generating environment file: $env_file"
    
    cat > "$env_file" << EOF
# FamilyCart GitHub Runners Configuration
GITHUB_OWNER=$GITHUB_OWNER
GITHUB_REPO=$GITHUB_REPO
GITHUB_TOKEN=$GITHUB_TOKEN

# Runner Configuration
RUNNER_LABELS=self-hosted,familycart,ubuntu,docker,uat
RUNNER_GROUP=default
RUNNER_WORK_DIRECTORY=/home/runner/work

# Docker Configuration
COMPOSE_PROJECT_NAME=familycart-runners
COMPOSE_FILE=$DOCKER_COMPOSE_FILE
EOF
    
    # Secure the environment file
    chmod 600 "$env_file"
    
    log "Environment file generated"
}

# Deploy runners
deploy_runners() {
    log "Deploying $RUNNER_COUNT GitHub runners..."
    
    cd "$UAT_REPO_DIR"
    
    # Load environment variables
    if [[ -f ".env.runners" ]]; then
        source ".env.runners"
    fi
    
    # Scale the runners
    docker compose -f docker-compose.runners.yml up -d --scale runner=$RUNNER_COUNT
    
    # Wait for runners to start
    log "Waiting for runners to initialize..."
    sleep 30
    
    # Check runner status
    check_runner_status
}

# Stop runners
stop_runners() {
    log "Stopping GitHub runners..."
    
    cd "$UAT_REPO_DIR"
    
    if [[ -f "docker-compose.runners.yml" ]]; then
        docker compose -f docker-compose.runners.yml down --remove-orphans
        log "All runners stopped and removed"
    else
        warn "docker-compose.runners.yml not found"
    fi
}

# Update runners
update_runners() {
    log "Updating GitHub runners..."
    
    # Rebuild image
    build_runner_image
    
    # Stop existing runners
    stop_runners
    
    # Deploy new runners
    deploy_runners
}

# Check runner status
check_runner_status() {
    info "=== GitHub Runners Status ==="
    
    cd "$UAT_REPO_DIR"
    
    if [[ ! -f "docker-compose.runners.yml" ]]; then
        warn "No runners configuration found"
        return
    fi
    
    # Check Docker containers
    local containers=$(docker compose -f docker-compose.runners.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "")
    
    if [[ -n "$containers" ]]; then
        echo "$containers"
    else
        warn "No runner containers found"
    fi
    
    # Check GitHub API for registered runners
    if [[ -n "$GITHUB_TOKEN" ]]; then
        info ""
        info "=== Registered Runners in GitHub ==="
        
        local api_response=$(curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
            "https://api.github.com/repos/$GITHUB_OWNER/$GITHUB_REPO/actions/runners" 2>/dev/null)
        
        if [[ -n "$api_response" ]]; then
            echo "$api_response" | jq -r '.runners[] | select(.labels[].name == "familycart") | "Name: \(.name), Status: \(.status), OS: \(.os), Labels: \(.labels | map(.name) | join(", "))"' 2>/dev/null || warn "Failed to parse GitHub API response"
        else
            warn "Failed to fetch runner information from GitHub API"
        fi
    fi
    
    info "================================="
}

# Show runner logs
show_logs() {
    cd "$UAT_REPO_DIR"
    
    if [[ -n "$RUNNER_NAME" ]]; then
        log "Showing logs for runner: $RUNNER_NAME"
        docker compose -f docker-compose.runners.yml logs -f "$RUNNER_NAME"
    else
        log "Showing logs for all runners"
        docker compose -f docker-compose.runners.yml logs -f
    fi
}

# Check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    # Check Docker
    if ! command -v docker >/dev/null 2>&1; then
        error "Docker is not installed"
    fi
    
    # Check Docker Compose
    if ! docker compose version >/dev/null 2>&1; then
        error "Docker Compose is not available"
    fi
    
    # Check disk space (need at least 5GB free)
    local free_space=$(df / | awk 'NR==2 {print $4}')
    if [[ $free_space -lt 5242880 ]]; then  # 5GB in KB
        warn "Low disk space detected (less than 5GB free)"
    fi
    
    # Check memory (recommend at least 4GB)
    local total_memory=$(free -m | awk 'NR==2{print $2}')
    if [[ $total_memory -lt 4000 ]]; then
        warn "Low memory detected (less than 4GB available)"
    fi
    
    log "System requirements check complete"
}

# Show system information
show_system_info() {
    info "=== System Information ==="
    info "Hostname: $(hostname)"
    info "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
    info "CPU cores: $(nproc)"
    info "Memory: $(free -h | awk 'NR==2{printf "%.1f GB", $2/1024/1024/1024}')"
    info "Disk space: $(df -h / | awk 'NR==2 {print $4}') free"
    info "Docker version: $(docker --version)"
    info "Docker Compose version: $(docker compose version)"
    info "Node.js version: $(node --version 2>/dev/null || echo 'Not installed')"
    info "Python version: $(python3 --version 2>/dev/null || echo 'Not installed')"
    info "Poetry version: $(poetry --version 2>/dev/null || echo 'Not installed')"
    info "================================="
}

# Main execution
main() {
    info "🚀 FamilyCart GitHub Runners Deployment"
    
    parse_args "$@"
    
    case "$ACTION" in
        "deploy")
            show_system_info
            check_requirements
            validate_token
            setup_directories
            build_runner_image
            generate_env_file
            deploy_runners
            log "✅ GitHub runners deployment complete!"
            ;;
        "stop")
            stop_runners
            log "✅ GitHub runners stopped"
            ;;
        "update")
            validate_token
            setup_directories
            update_runners
            log "✅ GitHub runners updated"
            ;;
        "status")
            check_runner_status
            ;;
        "logs")
            show_logs
            ;;
        *)
            error "Unknown action: $ACTION"
            ;;
    esac
}

# Run main function with all arguments
main "$@"
