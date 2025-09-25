#!/bin/bash

# CI Infrastructure Management Script
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DEPLOY_DIR="$PROJECT_DIR"

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
    docker compose -f "$DEPLOY_DIR/docker-compose.ci-infrastructure.yml" up -d
    
    log_info "Waiting for databases to be ready..."
    sleep 5
    
    # Health check
    if docker compose -f "$DEPLOY_DIR/docker-compose.ci-infrastructure.yml" ps --format json | jq -r '.[].Health' | grep -q "healthy"; then
        log_info "Infrastructure is healthy"
    else
        log_warn "Infrastructure may still be starting up"
    fi
}

stop_infrastructure() {
    log_info "Stopping CI infrastructure..."
    docker compose -f "$DEPLOY_DIR/docker-compose.ci-infrastructure.yml" down
}

# Runners management  
start_runners() {
    log_info "Starting GitHub runners..."
    
    # Ensure infrastructure is running first
    if ! docker network ls | grep -qE "(ci-network|familycart-ci-infrastructure)"; then
        log_warn "CI network not found, starting infrastructure first..."
        start_infrastructure
    fi
    
    docker compose -f "$DEPLOY_DIR/docker-compose.runners.yml" up -d
}

stop_runners() {
    log_info "Stopping GitHub runners..."
    docker compose -f "$DEPLOY_DIR/docker-compose.runners.yml" down
}

restart_runners() {
    log_info "Restarting GitHub runners..."
    docker compose -f "$DEPLOY_DIR/docker-compose.runners.yml" restart
}

scale_runners() {
    local count=${1:-1}
    log_info "Scaling runners to $count instances..."
    docker compose -f "$DEPLOY_DIR/docker-compose.runners.yml" up -d --scale runner="$count"
}

# Full stack management
start_all() {
    start_infrastructure
    sleep 10  # Give infrastructure time to fully initialize
    start_runners
}

stop_all() {
    stop_runners
    stop_infrastructure
}

status() {
    log_info "=== CI Infrastructure Status ==="
    docker compose -f "$DEPLOY_DIR/docker-compose.ci-infrastructure.yml" ps
    
    log_info "=== GitHub Runners Status ==="
    docker compose -f "$DEPLOY_DIR/docker-compose.runners.yml" ps
    
    log_info "=== Network Status ==="
    docker network ls | grep -E "(ci-network|familycart-ci-infrastructure)" || log_warn "CI network not found"
}

logs_infrastructure() {
    docker compose -f "$DEPLOY_DIR/docker-compose.ci-infrastructure.yml" logs -f "${1:-}"
}

logs_runners() {
    docker compose -f "$DEPLOY_DIR/docker-compose.runners.yml" logs -f "${1:-}"
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
    $0 start           # Start everything
    $0 scale-runners 3 # Run 3 runner instances
    $0 logs-infra postgres # View PostgreSQL logs
    $0 restart-runners # Restart runners without affecting databases

EOF
}

# Main command processing
case "${1:-}" in
    start-infra|infrastructure)
        start_infrastructure
        ;;
    stop-infra)
        stop_infrastructure
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
    logs-infra)
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