# Docker Compose V2 Command Reference

## Migration from V1 to V2

**IMPORTANT**: As of Docker Compose V2, the command syntax has changed from `docker-compose` to `docker compose` (note the space instead of hyphen). The old `docker-compose` (V1) is deprecated and should be replaced with the new `docker compose` (V2) commands.

## Core Commands for FamilyCart UAT Deployment

### Build Services
```bash
# Build all services defined in compose file
docker compose -f docker-compose.uat.yml build

# Build specific service
docker compose -f docker-compose.uat.yml build backend

# Force rebuild without cache
docker compose -f docker-compose.uat.yml build --no-cache
```

### Start/Stop Services
```bash
# Start all services in background
docker compose -f docker-compose.uat.yml up -d

# Start with build if needed
docker compose -f docker-compose.uat.yml up -d --build

# Pull latest images and start
docker compose -f docker-compose.uat.yml pull
docker compose -f docker-compose.uat.yml up -d --remove-orphans

# Stop all services
docker compose -f docker-compose.uat.yml down

# Stop and remove volumes
docker compose -f docker-compose.uat.yml down -v
```

### Service Management
```bash
# List running services
docker compose -f docker-compose.uat.yml ps

# View logs (all services)
docker compose -f docker-compose.uat.yml logs

# View logs (specific service, follow)
docker compose -f docker-compose.uat.yml logs -f backend

# View logs (last 100 lines)
docker compose -f docker-compose.uat.yml logs --tail=100

# Execute command in running container
docker compose -f docker-compose.uat.yml exec backend bash

# Scale a service
docker compose -f docker-compose.uat.yml up --scale backend=3 -d
```

### Maintenance Commands
```bash
# View service configuration
docker compose -f docker-compose.uat.yml config

# Pull latest images
docker compose -f docker-compose.uat.yml pull

# Remove stopped containers
docker compose -f docker-compose.uat.yml rm

# View resource usage stats
docker compose -f docker-compose.uat.yml stats

# Restart specific service
docker compose -f docker-compose.uat.yml restart backend
```

### GitHub Actions Runner Commands
```bash
# Start runners
docker compose -f docker-compose.github-runners.yml up -d

# View runner logs
docker compose -f docker-compose.github-runners.yml logs -f

# Stop runners
docker compose -f docker-compose.github-runners.yml down
```

## Key Differences from V1

1. **Command Structure**: `docker-compose` → `docker compose` (space instead of hyphen)
2. **Plugin Integration**: V2 is integrated as a Docker CLI plugin
3. **Performance**: V2 is written in Go and generally faster than Python-based V1
4. **Compose Specification**: V2 follows the Compose Specification and ignores the `version` field in compose files

## Installation Requirements

Ensure you have Docker Compose V2 installed:
```bash
# Check version
docker compose version

# If not installed, install the plugin
sudo apt update && sudo apt install -y docker-compose-plugin
```

## UAT Deployment Quick Commands

```bash
# Navigate to UAT directory
cd /opt/familycart-uat-repo

# Full deployment (pull, build, start)
docker compose -f docker-compose.uat.yml pull
docker compose -f docker-compose.uat.yml build
docker compose -f docker-compose.uat.yml up -d --remove-orphans

# Check deployment status
docker compose -f docker-compose.uat.yml ps
docker compose -f docker-compose.uat.yml logs --tail=50

# Health check
curl -s http://localhost:8080/health | jq
```

## Troubleshooting Commands

```bash
# View all containers (including stopped)
docker compose -f docker-compose.uat.yml ps -a

# Force recreate all containers
docker compose -f docker-compose.uat.yml up -d --force-recreate

# View resource usage
docker compose -f docker-compose.uat.yml top

# Export current configuration
docker compose -f docker-compose.uat.yml config > current-config.yml
```

This reference ensures all FamilyCart UAT deployment operations use the modern Docker Compose V2 syntax.
