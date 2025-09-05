#!/bin/bash

# Export environment variables for Docker Compose with correct container names
export POSTGRES_USER=familycart_uat
export POSTGRES_DB=familycart_uat  
export UAT_DB_PASSWORD="msLnRRrfxr46M89eAWOaH+Kf6IZrS4D/AXQzMTA2/cc="
export UAT_REDIS_PASSWORD="OKjYXPltPpH1WGkI0KhkFiGwrJLhdC0kLLUXGUo3qHA="
export GRAFANA_ADMIN_PASSWORD="changeme123"
export GRAFANA_DOMAIN="localhost"

echo "🚀 Starting monitoring stack with proper credentials and container names..."
docker compose -f docker-compose.monitoring.yml "$@"
