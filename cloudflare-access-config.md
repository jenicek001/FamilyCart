# CloudFlare Access Configuration for UAT Monitoring

## 🛡️ CloudFlare Zero Trust Access Setup

### Application Configuration

#### 1. Main Grafana Dashboard Application
- **Name**: `UAT Monitoring Dashboard`
- **Subdomain**: `monitoring.uat`
- **Domain**: `familycart.app`
- **Type**: `Self-hosted`
- **Application URL**: `https://monitoring.uat.familycart.app`

**Session Duration**: `24 hours`
**Accept all available identity providers**: `Yes`

#### 2. Prometheus API Application (Restricted)
- **Name**: `UAT Prometheus API`
- **Subdomain**: `prometheus.monitoring.uat`
- **Domain**: `familycart.app`
- **Type**: `Self-hosted`
- **Application URL**: `https://prometheus.monitoring.uat.familycart.app`

**Session Duration**: `8 hours`
**Accept all available identity providers**: `No` (Admin only)

#### 3. Alertmanager Application (Restricted)  
- **Name**: `UAT Alertmanager`
- **Subdomain**: `alerts.monitoring.uat`
- **Domain**: `familycart.app`
- **Type**: `Self-hosted`
- **Application URL**: `https://alerts.monitoring.uat.familycart.app`

**Session Duration**: `8 hours`
**Accept all available identity providers**: `No` (Admin only)

### Access Policies

#### Policy 1: Team Access (Grafana)
```yaml
Name: UAT Monitoring Team Access
Action: Allow
Session Duration: 24 hours

Include Rules:
  - Email addresses in: 
    - your-email@domain.com
    - team-member@domain.com
    - stakeholder@domain.com

Require Rules: []

Exclude Rules: []
```

#### Policy 2: Admin Access (Prometheus/Alertmanager)
```yaml
Name: UAT Monitoring Admin Access
Action: Allow
Session Duration: 8 hours

Include Rules:
  - Email addresses in:
    - admin@domain.com
    - devops@domain.com

Require Rules:
  - Country: [Your Country Code]  # Optional geographic restriction

Exclude Rules: []
```

#### Policy 3: Emergency Access
```yaml
Name: UAT Monitoring Emergency Access
Action: Allow
Session Duration: 2 hours

Include Rules:
  - Everyone

Require Rules:
  - Any Access Group: Emergency Response Team
  - One-time PIN via Email

Exclude Rules: []
```

### Identity Providers Configuration

#### Email-based Authentication
```yaml
Provider Type: One-time PIN
Name: Email OTP for UAT Monitoring
```

#### Optional: Google Workspace/Microsoft 365
```yaml
Provider Type: SAML/OIDC
Name: Corporate SSO
Domain Restriction: your-company.com
```

### Additional Security Settings

#### Rate Limiting
- **Requests per minute**: `60`
- **Requests per 10 minutes**: `300`
- **Action on limit exceeded**: `Block`

#### Geographic Restrictions (Optional)
- **Allowed Countries**: `[Your country codes]`
- **Block Tor**: `Yes`
- **Block known anonymizers**: `Yes`

#### Device Security (Optional)
- **Require hard key**: `No` (unless you use hardware keys)
- **Require managed device**: `No` (unless you have MDM)
- **Browser isolation**: `No` (for monitoring tools compatibility)

### Audit and Logging

#### Access Logs
- **Log successful authentications**: `Yes`
- **Log failed authentications**: `Yes`
- **Log session details**: `Yes`
- **Export logs to SIEM**: `Optional`

#### Alerting
- **Failed authentication threshold**: `5 attempts in 5 minutes`
- **Unusual access pattern detection**: `Yes`
- **Geographic anomaly detection**: `Yes`

### DNS Configuration

#### Required DNS Records
```dns
Type: A
Name: monitoring.uat
Value: [YOUR_SERVER_IP]
TTL: Auto

Type: CNAME  
Name: prometheus.monitoring.uat
Value: monitoring.uat.familycart.app
TTL: Auto

Type: CNAME
Name: alerts.monitoring.uat  
Value: monitoring.uat.familycart.app
TTL: Auto
```

### SSL/TLS Configuration

#### SSL/TLS Settings
- **SSL/TLS encryption mode**: `Full (Strict)`
- **Always Use HTTPS**: `On`
- **Automatic HTTPS Rewrites**: `On`
- **Opportunistic Encryption**: `On`

#### HSTS (HTTP Strict Transport Security)
- **Enable HSTS**: `On`
- **Max Age**: `31536000` (1 year)
- **Include Subdomains**: `On`
- **Preload**: `Off` (optional, requires careful consideration)

#### TLS Settings
- **Minimum TLS Version**: `1.2`
- **TLS 1.3**: `On`
- **0-RTT Connection Resumption**: `Off` (security over speed)

### Firewall Rules (Optional)

#### Allow Monitoring Access
```yaml
Expression: (http.host eq "monitoring.uat.familycart.app" or 
            http.host eq "prometheus.monitoring.uat.familycart.app" or 
            http.host eq "alerts.monitoring.uat.familycart.app") and 
            cf.threat_score le 10

Action: Allow
```

#### Block Suspicious Activity
```yaml
Expression: (http.host contains "monitoring.uat") and 
            (cf.threat_score gt 30 or 
             http.user_agent contains "bot" or 
             http.request.uri.path contains ".." or
             http.request.method eq "DELETE")

Action: Block
```

### Testing Checklist

#### Pre-Launch Testing
- [ ] DNS resolution working for all subdomains
- [ ] SSL certificates properly configured
- [ ] Nginx proxy responding correctly
- [ ] Basic authentication working (if enabled)
- [ ] Grafana accessible and functioning
- [ ] Prometheus API responding
- [ ] Alertmanager interface accessible

#### CloudFlare Access Testing
- [ ] Authentication flow working
- [ ] Session duration respected
- [ ] Access policies enforcing correctly
- [ ] Logging and audit trails visible
- [ ] Rate limiting functioning
- [ ] Geographic restrictions working (if enabled)

### Maintenance

#### Regular Tasks
- **SSL Certificate Renewal**: CloudFlare handles automatically
- **Access Policy Review**: Monthly review of user access
- **Log Analysis**: Weekly review of access logs
- **Security Updates**: Monitor for nginx and service updates
- **Performance Monitoring**: Track access times and availability

#### Emergency Procedures
- **Immediate Access Blocking**: Disable application in CloudFlare Access
- **Emergency Access**: Use emergency access policy with additional verification
- **Incident Response**: Document and log all emergency access usage
