#!/bin/bash

set -e

echo "🏥 FamilyCart UAT Monitoring Health Check"
echo "========================================"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check service
check_service() {
    local service_name=$1
    local port=$2
    local path=${3:-"/"}
    
    echo -n "🔍 Checking $service_name ($port$path): "
    
    if curl -s -f "http://localhost:$port$path" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Healthy${NC}"
        return 0
    else
        echo -e "${RED}❌ Unhealthy${NC}"
        return 1
    fi
}

# Function to check Docker container
check_container() {
    local container_name=$1
    echo -n "🐳 Checking container $container_name: "
    
    if docker ps | grep -q "$container_name.*Up"; then
        echo -e "${GREEN}✅ Running${NC}"
        return 0
    else
        echo -e "${RED}❌ Not running${NC}"
        return 1
    fi
}

# Function to check metrics endpoint
check_metrics() {
    local endpoint=$1
    local service_name=$2
    
    echo -n "📊 Checking $service_name metrics: "
    
    if curl -s "$endpoint" | grep -q "# HELP"; then
        echo -e "${GREEN}✅ Available${NC}"
        return 0
    else
        echo -e "${RED}❌ No metrics${NC}"
        return 1
    fi
}

echo ""
echo "🐳 Docker Container Status:"
echo "==========================="

# Check monitoring containers
CONTAINERS=(
    "familycart-prometheus"
    "familycart-grafana"
    "familycart-node-exporter"
    "familycart-cadvisor"
    "familycart-redis-exporter"
    "familycart-postgres-exporter"
    "familycart-alertmanager"
)

container_issues=0
for container in "${CONTAINERS[@]}"; do
    if ! check_container "$container"; then
        ((container_issues++))
    fi
done

echo ""
echo "🌐 Service Health Checks:"
echo "========================"

service_issues=0

# Core monitoring services
check_service "Prometheus" "9090" "/" || ((service_issues++))
check_service "Grafana" "3000" "/api/health" || ((service_issues++))
check_service "Alertmanager" "9093" "/-/healthy" || ((service_issues++))

# Exporters
check_service "Node Exporter" "9100" "/metrics" || ((service_issues++))
check_service "cAdvisor" "8080" "/metrics" || ((service_issues++))
check_service "Redis Exporter" "9121" "/metrics" || ((service_issues++))
check_service "Postgres Exporter" "9187" "/metrics" || ((service_issues++))

echo ""
echo "📊 Metrics Validation:"
echo "====================="

metrics_issues=0

# Check key metrics are available
check_metrics "http://localhost:9090/api/v1/query?query=up" "Prometheus Targets" || ((metrics_issues++))
check_metrics "http://localhost:9100/metrics" "Node Metrics" || ((metrics_issues++))
check_metrics "http://localhost:8080/metrics" "Container Metrics" || ((metrics_issues++))

echo ""
echo "🔍 UAT Application Integration:"
echo "==============================="

integration_issues=0

# Check if main UAT services are being monitored
echo -n "🎯 UAT Backend monitoring: "
if docker ps | grep -q "familycart-backend-uat.*Up"; then
    echo -e "${GREEN}✅ Backend container running${NC}"
    # Try to check if backend has metrics endpoint
    if curl -s -f "http://localhost:8001/metrics" > /dev/null 2>&1; then
        echo "   📊 Backend metrics: ${GREEN}✅ Available${NC}"
    else
        echo "   📊 Backend metrics: ${YELLOW}⚠️  Not available (may need prometheus-fastapi-instrumentator)${NC}"
        ((integration_issues++))
    fi
else
    echo -e "${RED}❌ Backend container not running${NC}"
    ((integration_issues++))
fi

echo -n "🗄️  UAT Database monitoring: "
if docker ps | grep -q "familycart-db-uat.*Up"; then
    echo -e "${GREEN}✅ Database container running${NC}"
else
    echo -e "${RED}❌ Database container not running${NC}"
    ((integration_issues++))
fi

echo -n "🚀 UAT Redis monitoring: "
if docker ps | grep -q "familycart-redis-uat.*Up"; then
    echo -e "${GREEN}✅ Redis container running${NC}"
else
    echo -e "${RED}❌ Redis container not running${NC}"
    ((integration_issues++))
fi

echo ""
echo "📈 Summary:"
echo "=========="

total_issues=$((container_issues + service_issues + metrics_issues + integration_issues))

if [ $total_issues -eq 0 ]; then
    echo -e "${GREEN}🎉 All monitoring systems healthy!${NC}"
    echo ""
    echo "🌐 Access Points:"
    echo "   📊 Grafana: http://localhost:3000 (admin/changeme123)"
    echo "   🔍 Prometheus: http://localhost:9090"
    echo "   🚨 Alertmanager: http://localhost:9093"
    echo ""
    echo "🌍 External Access (if configured):"
    echo "   📊 Grafana: https://monitoring.uat.familycart.app"
    echo "   🔍 Prometheus: https://monitoring.uat.familycart.app/prometheus/"
    echo "   🚨 Alertmanager: https://monitoring.uat.familycart.app/alertmanager/"
    exit 0
else
    echo -e "${RED}❌ Found $total_issues issues:${NC}"
    echo "   🐳 Container issues: $container_issues"
    echo "   🌐 Service issues: $service_issues"
    echo "   📊 Metrics issues: $metrics_issues"
    echo "   🔗 Integration issues: $integration_issues"
    echo ""
    echo -e "${YELLOW}�� Troubleshooting:${NC}"
    echo "   1. Check container logs: docker compose -f docker-compose.monitoring.yml logs [service]"
    echo "   2. Restart monitoring stack: docker compose -f docker-compose.monitoring.yml down && docker compose -f docker-compose.monitoring.yml up -d"
    echo "   3. Check UAT services: docker compose -f docker-compose.uat.yml ps"
    echo "   4. Check network connectivity: docker network ls | grep familycart"
    exit 1
fi
