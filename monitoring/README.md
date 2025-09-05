# FamilyCart UAT Monitoring Stack

## 📊 Overview

Comprehensive monitoring solution for FamilyCart UAT environment using:
- **Prometheus** - Metrics collection and alerting
- **Grafana** - Visualization and dashboards  
- **Node Exporter** - System metrics
- **cAdvisor** - Container metrics
- **Redis Exporter** - Redis cache metrics
- **PostgreSQL Exporter** - Database metrics
- **Alertmanager** - Alert routing and notifications

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose V2
- **Poetry 2.x** (for backend dependencies)
- Nginx (for SSL termination)
- Running FamilyCart UAT environment

### 1. Automatic Setup

```bash
# Run the automated setup script
cd /opt/familycart-uat-repo/monitoring
./setup-monitoring.sh
```

This script will:
- Check Poetry 2.x availability
- Install Prometheus FastAPI dependencies via Poetry
- Set up basic authentication
- Deploy monitoring stack
- Provide access URLs and credentials

### 2. Manual Setup (Poetry 2.x)

```bash
# Install backend monitoring dependencies
cd /opt/familycart-uat-repo/backend
poetry add prometheus-client prometheus-fastapi-instrumentator

# Start monitoring stack
cd /opt/familycart-uat-repo/monitoring
docker compose -f docker-compose.monitoring.yml up -d
```

## 🔧 Backend Integration (Poetry 2.x)

### Add Metrics to FastAPI App

1. **Install Dependencies** (Poetry 2.x):
```bash
cd backend
poetry add prometheus-client prometheus-fastapi-instrumentator
```

2. **Integrate Metrics** (see `backend-metrics-integration.py`):
```python
# In app/main.py
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="FamilyCart API", version="1.0.0")

# Enable metrics if configured
if os.getenv("ENABLE_METRICS", "false").lower() == "true":
    instrumentator = Instrumentator()
    instrumentator.instrument(app).expose(app, endpoint="/metrics")
```

3. **Rebuild Backend**:
```bash
cd backend
docker build -t familycart-backend-uat .
```

4. **Restart UAT Services**:
```bash
cd /opt/familycart-uat-repo
docker compose -f docker-compose.uat.yml restart backend
```

## 🌐 Access Points

### Local Access
- **Grafana**: http://localhost:3000 (admin/changeme123)
- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093

### HTTPS Access (with Nginx)
- **Grafana**: https://monitoring.uat.familycart.app
- **Prometheus**: https://monitoring.uat.familycart.app/prometheus/
- **Alertmanager**: https://monitoring.uat.familycart.app/alertmanager/

## 📈 Key Metrics

### Application Metrics
- HTTP request rates and response times
- WebSocket connection counts
- AI provider performance (Gemini, Ollama)
- Database query performance
- Redis cache hit rates

### System Metrics
- CPU, Memory, Disk usage
- Container resource consumption
- Network I/O statistics
- PostgreSQL connection pools

### Custom FamilyCart Metrics
- Shopping list counts
- Item creation/completion rates
- User activity patterns
- Real-time collaboration events

## 🚨 Alerting Rules

Configured alerts for:
- **Critical**: Service downtime, high error rates
- **Warning**: High resource usage, slow queries
- **Info**: Performance degradation, capacity planning

Alert destinations:
- Email notifications
- Webhook integrations
- Optional Slack/Discord channels

## 🛠️ Management Commands

### Health Check
```bash
cd /opt/familycart-uat-repo/monitoring
./health-check.sh
```

### View Logs
```bash
# All services
docker compose -f docker-compose.monitoring.yml logs

# Specific service
docker compose -f docker-compose.monitoring.yml logs grafana
docker compose -f docker-compose.monitoring.yml logs prometheus
```

### Restart Services
```bash
docker compose -f docker-compose.monitoring.yml restart
```

### Update Configuration
```bash
# Reload Prometheus config
docker compose -f docker-compose.monitoring.yml kill -s HUP prometheus

# Restart Grafana with new dashboards
docker compose -f docker-compose.monitoring.yml restart grafana
```

## 📊 Dashboard Overview

### FamilyCart Overview Dashboard
- Service status indicators
- System resource utilization
- Request rates and error counts
- Response time distributions

### System Performance Dashboard  
- CPU, Memory, Disk metrics
- Container resource usage
- Network throughput
- Database performance

### Application Insights Dashboard
- User activity patterns
- AI provider performance
- WebSocket connection health
- Feature usage statistics

## 🔐 Security Configuration

### Basic Authentication
Admin endpoints (Prometheus, Alertmanager) protected with:
- Username/password authentication
- Nginx reverse proxy security headers
- SSL/TLS encryption via Cloudflare

### Network Security
- Isolated Docker networks
- Firewall rules (UFW configuration)
- Internal service communication only
- External access via Nginx proxy

## 📚 Troubleshooting

### Common Issues

1. **Poetry Version Check**:
```bash
poetry --version  # Should be 2.x
# Upgrade if needed: curl -sSL https://install.python-poetry.org | python3 -
```

2. **Container Network Issues**:
```bash
docker network ls | grep familycart
docker network inspect familycart-uat
```

3. **Backend Metrics Not Available**:
```bash
# Check if metrics dependencies installed
cd backend && poetry show | grep prometheus

# Verify environment variable
docker compose -f docker-compose.uat.yml exec backend env | grep ENABLE_METRICS

# Test metrics endpoint
curl http://localhost:8001/metrics
```

4. **Grafana Connection Issues**:
```bash
# Check Prometheus connectivity from Grafana
docker compose -f docker-compose.monitoring.yml exec grafana \
    curl -f http://familycart-prometheus:9090/api/v1/status/config
```

### Log Analysis
```bash
# Backend logs for metrics errors
docker compose -f docker-compose.uat.yml logs backend | grep -i prometheus

# Prometheus target status
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.health != "up")'
```

## 🔄 Maintenance

### Regular Tasks
- Monitor disk usage (metrics retention: 15 days)
- Review alert configurations
- Update dashboard configurations
- Check SSL certificate expiration

### Backup Important Data
```bash
# Export Grafana dashboards
curl -u admin:changeme123 http://localhost:3000/api/search | \
    jq -r '.[] | select(.type == "dash-db") | .uid' | \
    xargs -I {} curl -u admin:changeme123 http://localhost:3000/api/dashboards/uid/{} > backup-{}.json

# Backup Prometheus data
docker compose -f docker-compose.monitoring.yml exec prometheus \
    tar czf /prometheus/backup-$(date +%Y%m%d).tar.gz /prometheus/
```

## 📖 Documentation Links

- [Prometheus Configuration](prometheus/prometheus.yml)
- [Grafana Dashboards](grafana/dashboards/)
- [Alert Rules](prometheus/rules/familycart.yml)
- [Backend Integration](backend-metrics-integration.py)

---

**Note**: This monitoring stack is designed for UAT environments. For production deployment, consider additional security hardening, data retention policies, and high-availability configurations.
