#!/bin/bash

# CI Infrastructure Management Script
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DEPLOY_DIR="$PROJECT_DIR"

# Environment file for secure credentials
ENV_CI_FILE="$PROJECT_DIR/.env.ci"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Infrastructure management
start_infrastructure() {
    log_info "Starting CI infrastructure (PostgreSQL, Redis)..."
    
    # Check for .env.ci file for secure credentials
    if [ -f "$ENV_CI_FILE" ]; then
        log_info "Using secure credentials from .env.ci"
        docker compose -p familycart-ci-infrastructure -f "$DEPLOY_DIR/docker-compose.ci-infrastructure.yml" --env-file "$ENV_CI_FILE" up -d
    else
        log_warn "No .env.ci file found, using default credentials (insecure for production)"
        log_warn "Run 'scripts/generate-ci-credentials.sh' to generate secure credentials"
        docker compose -p familycart-ci-infrastructure -f "$DEPLOY_DIR/docker-compose.ci-infrastructure.yml" up -d
    fi
    
    log_info "Waiting for databases to be ready..."
    sleep 5
    
    # Health check - count healthy containers
    HEALTHY_COUNT=$(docker compose -p familycart-ci-infrastructure -f "$DEPLOY_DIR/docker-compose.ci-infrastructure.yml" ps --format json | jq -r 'select(.Health == "healthy") | .Health' | wc -l)
    TOTAL_COUNT=$(docker compose -p familycart-ci-infrastructure -f "$DEPLOY_DIR/docker-compose.ci-infrastructure.yml" ps --format json | jq -r '.Health' | wc -l)
    
    if [ "$HEALTHY_COUNT" -eq "$TOTAL_COUNT" ] && [ "$TOTAL_COUNT" -gt 0 ]; then
        log_info "Infrastructure is healthy ($HEALTHY_COUNT/$TOTAL_COUNT containers)"
    else
        log_warn "Infrastructure may still be starting up ($HEALTHY_COUNT/$TOTAL_COUNT containers healthy)"
    fi
}

stop_infrastructure() {
    log_info "Stopping CI infrastructure..."
    docker compose -p familycart-ci-infrastructure -f "$DEPLOY_DIR/docker-compose.ci-infrastructure.yml" down
}

# Runners management  
start_runners() {
    local count=${1:-3}  # Default to 3 runners if no count specified
    log_info "Starting $count GitHub runners..."
    
    # Ensure infrastructure is running first
    if ! docker network ls | grep -qE "(ci-network|familycart-ci-infrastructure)"; then
        log_warn "CI network not found, starting infrastructure first..."
        start_infrastructure
    fi
    
    # Start the specified number of runners
    case $count in
        1) docker compose -p familycart-runners -f "$DEPLOY_DIR/docker-compose.runners.yml" up -d --remove-orphans runner-1 ;;
        2) docker compose -p familycart-runners -f "$DEPLOY_DIR/docker-compose.runners.yml" up -d --remove-orphans runner-1 runner-2 ;;
        3) docker compose -p familycart-runners -f "$DEPLOY_DIR/docker-compose.runners.yml" up -d --remove-orphans runner-1 runner-2 runner-3 ;;
        *) docker compose -p familycart-runners -f "$DEPLOY_DIR/docker-compose.runners.yml" up -d --remove-orphans ;;
    esac
}

stop_runners() {
    log_info "Stopping GitHub runners..."
    docker compose -p familycart-runners -f "$DEPLOY_DIR/docker-compose.runners.yml" stop
}

restart_runners() {
    log_info "Restarting GitHub runners..."
    docker compose -p familycart-runners -f "$DEPLOY_DIR/docker-compose.runners.yml" restart
}

scale_runners() {
    local count=${1:-3}
    log_info "Scaling runners to $count instances..."
    
    # Stop and remove only runner containers, not infrastructure
    docker compose -p familycart-runners -f "$DEPLOY_DIR/docker-compose.runners.yml" down --remove-orphans
    sleep 2
    
    # Start the requested number
    start_runners "$count"
}

# Full stack management
start_all() {
    start_infrastructure
    sleep 10  # Give infrastructure time to fully initialize
    start_runners 3  # Start 3 runners by default
}

stop_all() {
    stop_runners
    stop_infrastructure
}

status() {
    log_info "=== CI Infrastructure Status ==="
    # Show only infrastructure services: postgres-ci and redis-ci
    docker compose -p familycart-ci-infrastructure -f "$DEPLOY_DIR/docker-compose.ci-infrastructure.yml" ps --filter status=running 2>/dev/null | grep -E "(postgres-ci|redis-ci)" || echo "No CI infrastructure services running"
    
    log_info "=== GitHub Runners Status ==="  
    # Show only runner services
    RUNNER_CONTAINERS=$(docker compose -p familycart-runners -f "$DEPLOY_DIR/docker-compose.runners.yml" ps --filter status=running 2>/dev/null | grep -E "(runner-[0-9])" || true)
    
    if [ -n "$RUNNER_CONTAINERS" ]; then
        echo "$RUNNER_CONTAINERS"
    else
        echo "No GitHub runners are currently running"
    fi
    
    log_info "=== Network Status ==="
    docker network ls | grep -E "(runners|familycart-ci-infrastructure)" || log_warn "CI networks not found"
}

logs_infrastructure() {
    docker compose -p familycart-ci-infrastructure -f "$DEPLOY_DIR/docker-compose.ci-infrastructure.yml" logs -f "${1:-}"
}

logs_runners() {
    docker compose -p familycart-runners -f "$DEPLOY_DIR/docker-compose.runners.yml" logs -f "${1:-}"
}



# Help function
show_help() {
    cat << EOF
CI Infrastructure Management Script

Usage: $0 <command> [options]

Commands:
  Infrastructure:
    start-infra         Start PostgreSQL and Redis
    stop-infra          Stop infrastructure services
    restart-infra       Restart infrastructure with fresh credentials
    logs-infra [service] View infrastructure logs
    
  Runners:
    start-runners       Start GitHub runners
    stop-runners        Stop GitHub runners  
    restart-runners     Restart GitHub runners
    scale-runners <n>   Scale runners to n instances
    logs-runners [service] View runner logs
    
  Full Stack:
    start              Start infrastructure + runners
    stop               Stop all services
    status             Show status of all services
    
Examples:
    $0 start            # Start full CI environment
    $0 start-runners 3  # Start 3 runners
    $0 scale-runners 5  # Scale to 5 runners
    $0 restart-infrastructure # Restart databases with new credentials
    $0 stop             # Stop everything
    $0 status           # View service status
    $0 logs-infrastructure # View all infrastructure logs
    $0 restart-runners # Restart runners without affecting databases

Aliases:
    start-infra / start-infrastructure
    stop-infra / stop-infrastructure  
    restart-infra / restart-infrastructure
    logs-infra / logs-infrastructure
EOF
}

# Main command processing
case "${1:-}" in
    start-infra|infrastructure)
        start_infrastructure
        ;;
    stop-infra|stop-infrastructure)
        stop_infrastructure
        ;;
    restart-infra|restart-infrastructure)
        log_info "Restarting CI infrastructure with fresh credentials..."
        stop_infrastructure
        start_infrastructure
        ;;
    start-runners|runners)
        start_runners
        ;;
    stop-runners)
        stop_runners
        ;;
    restart-runners)
        restart_runners
        ;;
    scale-runners)
        scale_runners "$2"
        ;;
    start|up)
        start_all
        ;;
    stop|down)
        stop_all
        ;;
    status|ps)
        status
        ;;
    logs-infra|logs-infrastructure)
        logs_infrastructure "$2"
        ;;
    logs-runners)
        logs_runners "$2"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: ${1:-}"
        echo
        show_help
        exit 1
        ;;
esac