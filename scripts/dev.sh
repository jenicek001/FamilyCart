#!/bin/bash

# FamilyCart Development Helper Script
# Simplifies common Docker Compose commands for development

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.dev.yml"
COMPOSE_CMD="docker compose"

# Helper functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Commands
cmd_start() {
    print_header "Starting Development Environment"
    $COMPOSE_CMD -f "$COMPOSE_FILE" up -d
    print_success "Development environment started"
    echo ""
    print_info "Services:"
    echo "  🌐 Frontend:  http://localhost:3000"
    echo "  🔌 Backend:   http://localhost:8000"
    echo "  📊 API Docs:  http://localhost:8000/docs"
    echo "  🗄️  PostgreSQL: localhost:5432"
    echo "  💾 Redis:     localhost:6379"
    echo ""
    print_info "View logs with: $0 logs"
}

cmd_stop() {
    print_header "Stopping Development Environment"
    $COMPOSE_CMD -f "$COMPOSE_FILE" down
    print_success "Development environment stopped"
}

cmd_restart() {
    print_header "Restarting Development Environment"
    $COMPOSE_CMD -f "$COMPOSE_FILE" restart "$@"
    if [ -z "$1" ]; then
        print_success "All services restarted"
    else
        print_success "Service(s) $@ restarted"
    fi
}

cmd_rebuild() {
    print_header "Rebuilding Development Environment"
    $COMPOSE_CMD -f "$COMPOSE_FILE" down
    $COMPOSE_CMD -f "$COMPOSE_FILE" build --no-cache "$@"
    $COMPOSE_CMD -f "$COMPOSE_FILE" up -d
    print_success "Development environment rebuilt and started"
}

cmd_logs() {
    SERVICE="${1:-backend}"
    print_header "Viewing logs for: $SERVICE"
    $COMPOSE_CMD -f "$COMPOSE_FILE" logs -f "$SERVICE"
}

cmd_shell() {
    SERVICE="${1:-backend}"
    print_header "Opening shell in: $SERVICE"
    $COMPOSE_CMD -f "$COMPOSE_FILE" exec "$SERVICE" /bin/sh
}

cmd_migrate() {
    print_header "Running Database Migrations"
    $COMPOSE_CMD -f "$COMPOSE_FILE" exec backend alembic upgrade head
    print_success "Migrations completed"
}

cmd_migrate_create() {
    if [ -z "$1" ]; then
        print_error "Migration name required"
        echo "Usage: $0 migrate:create <migration_name>"
        exit 1
    fi
    print_header "Creating Migration: $1"
    $COMPOSE_CMD -f "$COMPOSE_FILE" exec backend alembic revision --autogenerate -m "$1"
    print_success "Migration created"
}

cmd_test() {
    print_header "Running Tests"
    $COMPOSE_CMD -f "$COMPOSE_FILE" exec backend pytest "$@"
}

cmd_clean() {
    print_header "Cleaning Development Environment"
    echo "This will remove all containers, volumes, and networks"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        $COMPOSE_CMD -f "$COMPOSE_FILE" down -v
        print_success "Development environment cleaned (volumes removed)"
    else
        print_info "Clean cancelled"
    fi
}

cmd_status() {
    print_header "Development Environment Status"
    $COMPOSE_CMD -f "$COMPOSE_FILE" ps
}

cmd_build() {
    print_header "Building Images"
    $COMPOSE_CMD -f "$COMPOSE_FILE" build "$@"
    print_success "Build completed"
}

cmd_help() {
    cat << EOF
FamilyCart Development Helper

Usage: $0 <command> [options]

Commands:
  start              Start the development environment
  stop               Stop the development environment
  restart [service]  Restart all services or specific service
  rebuild [service]  Rebuild and restart (no cache)
  logs [service]     View logs (default: backend)
  shell [service]    Open shell in container (default: backend)
  migrate            Run database migrations
  migrate:create <name>  Create new migration
  test [args]        Run tests (pass pytest args)
  clean              Remove all containers and volumes
  status             Show status of all services
  build [service]    Build images
  help               Show this help message

Examples:
  $0 start                    # Start all services
  $0 logs frontend            # View frontend logs
  $0 shell backend            # Open shell in backend
  $0 migrate                  # Run migrations
  $0 migrate:create add_user  # Create new migration
  $0 test                     # Run all tests
  $0 test tests/unit          # Run specific tests
  $0 rebuild frontend         # Rebuild frontend only
  $0 clean                    # Clean everything

Services:
  - postgres   PostgreSQL database
  - redis      Redis cache
  - backend    FastAPI backend
  - frontend   Next.js frontend
  - runner-1   Background worker

EOF
}

# Main command handler
case "$1" in
    start)
        cmd_start
        ;;
    stop)
        cmd_stop
        ;;
    restart)
        shift
        cmd_restart "$@"
        ;;
    rebuild)
        shift
        cmd_rebuild "$@"
        ;;
    logs)
        shift
        cmd_logs "$@"
        ;;
    shell)
        shift
        cmd_shell "$@"
        ;;
    migrate)
        cmd_migrate
        ;;
    migrate:create)
        shift
        cmd_migrate_create "$@"
        ;;
    test)
        shift
        cmd_test "$@"
        ;;
    clean)
        cmd_clean
        ;;
    status)
        cmd_status
        ;;
    build)
        shift
        cmd_build "$@"
        ;;
    help|--help|-h)
        cmd_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        cmd_help
        exit 1
        ;;
esac
