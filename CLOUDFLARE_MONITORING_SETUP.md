# CloudFlare UAT Monitoring Setup

## 🎯 Goal
Expose UAT monitoring services (Grafana, Prometheus, Alertmanager) via CloudFlare with proper security and best practices.

## 📋 Proposed Setup

### Domain Strategy
- **Primary**: `monitoring.uat.familycart.app` (Main Grafana dashboard)
- **Unified naming**: Following pattern `service.environment.domain.app` for reusability
- **Production ready**: Easy transition to `monitoring.prod.familycart.app`

### Services to Expose
1. **Grafana** (Port 3000) - Main dashboards → `monitoring.uat.familycart.app`
2. **Prometheus** (Port 9091) - Metrics API → `prometheus.monitoring.uat.familycart.app` (restricted)
3. **Alertmanager** (Port 9093) - Alert management → `alerts.monitoring.uat.familycart.app` (restricted)

### Security Measures
1. **CloudFlare Access Control**
   - Email-based authentication for team access
   - IP restrictions for additional security
   - Rate limiting and DDoS protection

2. **Basic Authentication** (Double layer)
   - Nginx basic auth in front of services
   - Grafana built-in authentication

3. **SSL/TLS**
   - CloudFlare Full (Strict) SSL
   - Auto HTTPS redirect

## 🔧 Implementation Plan

### Phase 1: Nginx Reverse Proxy Configuration
Create reverse proxy with SSL termination and authentication

### Phase 2: CloudFlare Configuration
- DNS records for subdomains
- Access policies setup
- SSL/TLS configuration

### Phase 3: Security Hardening
- Rate limiting
- IP allowlist (optional)
- Monitoring alerts for unauthorized access

### Phase 4: Documentation & Monitoring
- Access procedures documentation
- Alert setup for service availability
- Performance monitoring

## 📊 Expected Benefits
- ✅ Remote access to UAT metrics and dashboards
- ✅ Team collaboration on performance analysis
- ✅ Proactive monitoring of UAT environment
- ✅ Professional monitoring setup for stakeholders

## 🔒 Security Considerations
- Multi-layer authentication (CloudFlare + Basic Auth + Grafana)
- Restricted access to sensitive Prometheus/Alertmanager endpoints
- Audit logging for access attempts
- Regular security reviews

## 📝 Next Steps
1. Choose final subdomain names
2. Create nginx configuration for monitoring proxy
3. Set up CloudFlare DNS and Access policies
4. Configure monitoring services for external access
5. Test access and security measures
6. Document access procedures for team
