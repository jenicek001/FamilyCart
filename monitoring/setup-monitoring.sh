#!/bin/bash

set -e

echo "🔧 Setting up FamilyCart UAT Monitoring Stack..."

# Check if running as root/sudo
if [[ $EUID -eq 0 ]]; then
   echo "⚠️  This script should not be run as root. Please run as regular user with docker permissions."
   exit 1
fi

# Check Docker and Docker Compose are available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose V2 is not available"
    exit 1
fi

# Check Poetry 2.x is available
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed or not in PATH"
    exit 1
fi

POETRY_VERSION=$(poetry --version | grep -o '[0-9]\+\.[0-9]\+' | head -1)
if [[ $(echo "$POETRY_VERSION < 2.0" | bc) -eq 1 ]]; then
    echo "⚠️  Poetry version $POETRY_VERSION detected. Recommend upgrading to Poetry 2.x"
    echo "   Run: curl -sSL https://install.python-poetry.org | python3 -"
fi

# Ensure UAT network exists (should be created by main UAT deployment)
if ! docker network inspect familycart-uat &> /dev/null; then
    echo "⚠️  Creating familycart-uat network (should exist from main UAT deployment)"
    docker network create familycart-uat
fi

# Create basic auth file for admin endpoints
echo "🔐 Setting up basic authentication for admin endpoints..."
sudo apt update && sudo apt install -y apache2-utils
echo -n "Enter username for monitoring admin access: "
read -r ADMIN_USER
echo -n "Enter password for monitoring admin access: "
read -s ADMIN_PASS
echo
sudo mkdir -p /etc/nginx
echo "$ADMIN_PASS" | sudo htpasswd -ci /etc/nginx/.htpasswd "$ADMIN_USER"

# Set proper permissions for configurations
echo "📁 Setting up directory permissions..."
sudo chown -R $(whoami):$(whoami) .

# Install Prometheus metrics dependencies in backend (using Poetry 2.x)
if [ -f "../backend/pyproject.toml" ]; then
    echo "📦 Installing Prometheus metrics dependencies with Poetry 2.x..."
    cd ../backend
    poetry install --no-dev
    cd ../monitoring
else
    echo "⚠️  Backend pyproject.toml not found, skipping metrics dependencies installation"
fi

# Start monitoring stack
echo "🚀 Starting monitoring services..."
docker compose -f docker-compose.monitoring.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "📊 Checking service status..."
docker compose -f docker-compose.monitoring.yml ps

echo ""
echo "✅ FamilyCart UAT Monitoring Setup Complete!"
echo ""
echo "🌐 Access Points:"
echo "   📊 Grafana Dashboard: http://localhost:3000"
echo "   🔍 Prometheus: http://localhost:9090"
echo "   🚨 Alertmanager: http://localhost:9093"
echo ""
echo "🔑 Default Credentials:"
echo "   Grafana: admin / ${GRAFANA_ADMIN_PASSWORD:-changeme123}"
echo "   Prometheus/Alertmanager: $ADMIN_USER / [password you entered]"
echo ""
echo "🚨 Next Steps:"
echo "1. Add Cloudflare DNS record: monitoring.uat.familycart.app → your-server-ip"
echo "2. Copy monitoring nginx config to main nginx: cp monitoring/nginx/monitoring.conf ../nginx/"
echo "3. Restart nginx to enable monitoring.uat.familycart.app"
echo "4. Access via https://monitoring.uat.familycart.app"
echo ""
echo "🔧 Backend Metrics Integration:"
echo "1. Add metrics to FastAPI app (see monitoring/backend-metrics-integration.py)"
echo "2. Rebuild backend container: cd ../backend && docker build -t familycart-backend-uat ."
echo "3. Restart UAT stack: cd .. && docker compose -f docker-compose.uat.yml restart backend"
echo ""
echo "📈 Monitoring Stack Ready!"
