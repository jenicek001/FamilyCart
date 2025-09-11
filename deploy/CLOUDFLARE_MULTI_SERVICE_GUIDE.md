# CloudFlare Configuration Guide for Multi-Service Nginx Proxy

This guide covers the CloudFlare setup required for your multi-service nginx proxy configuration.

## 🌐 Required Domain Configuration

### DNS Records in CloudFlare

You need to configure the following DNS records in CloudFlare:

1. **grafana.connectedhome.cz**
   - Type: A
   - Name: grafana
   - Content: [YOUR_PUBLIC_IP_ADDRESS]
   - Proxy status: ✅ Proxied (orange cloud)
   - TTL: Auto

2. **homeassistant.connectedhome.cz**  
   - Type: A
   - Name: homeassistant
   - Content: [YOUR_PUBLIC_IP_ADDRESS]
   - Proxy status: ✅ Proxied (orange cloud)
   - TTL: Auto

3. **uat.familycart.local** (if using CloudFlare)
   - Type: A
   - Name: uat
   - Content: [YOUR_PUBLIC_IP_ADDRESS]
   - Proxy status: ✅ Proxied (orange cloud)
   - TTL: Auto

## 🔐 SSL/TLS Certificates - CloudFlare Origin Certificates

### 1. Generate Origin Certificates

In CloudFlare Dashboard:
1. Go to **SSL/TLS** → **Origin Server**
2. Click **Create Certificate**
3. Select **Let CloudFlare generate a private key and a CSR**
4. Configure hostnames:
   ```
   *.connectedhome.cz
   connectedhome.cz
   ```
5. Key type: **RSA (2048)**
6. Certificate validity: **15 years**
7. Click **Create**

### 2. Save Certificate Files

Save the generated certificates as:

**For connectedhome.cz domains:**
- Certificate: `/etc/nginx/ssl/connectedhome.cz.crt`
- Private Key: `/etc/nginx/ssl/connectedhome.cz.key`

**For FamilyCart UAT (if using CloudFlare):**
- Certificate: `/etc/nginx/ssl/uat.familycart.local.crt`  
- Private Key: `/etc/nginx/ssl/uat.familycart.local.key`

**Default certificate for unknown domains:**
- Generate a self-signed certificate:
```bash
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/default.key \
    -out /etc/nginx/ssl/default.crt \
    -subj "/C=CZ/ST=Prague/L=Prague/O=Default/CN=default"
```

## ⚙️ CloudFlare Settings

### SSL/TLS Configuration

1. **SSL/TLS** → **Overview**
   - Encryption mode: **Full (strict)** 
   - This ensures end-to-end encryption between CloudFlare and your origin server

2. **SSL/TLS** → **Edge Certificates**
   - Always Use HTTPS: ✅ **On**
   - HTTP Strict Transport Security (HSTS): ✅ **Enable**
     - Max Age Header: 6 months
     - Include Subdomains: ✅ On
     - Preload: ✅ On
   - Minimum TLS Version: **TLS 1.2**
   - Opportunistic Encryption: ✅ **On**
   - TLS 1.3: ✅ **On**

### Security Settings

1. **Security** → **Settings**
   - Security Level: **Medium**
   - Challenge Passage: **30 minutes**
   - Browser Integrity Check: ✅ **On**

2. **Security** → **Bot Fight Mode**
   - Bot Fight Mode: ✅ **On** (optional, for basic bot protection)

### Firewall Rules (Optional but Recommended)

Create firewall rules to enhance security:

1. **Block non-CZ traffic for Home Assistant** (optional):
   ```
   Field: Country
   Operator: does not equal
   Value: Czech Republic
   Action: Block
   ```

2. **Rate limiting for API endpoints**:
   ```
   Field: URI Path
   Operator: starts with
   Value: /api/
   Action: Rate limit (10 requests per minute)
   ```

### Page Rules

1. **For Home Assistant** (homeassistant.connectedhome.cz/*):
   - Browser Cache TTL: **Respect Existing Headers**
   - Cache Level: **Bypass**
   - Disable Apps: ✅ **On**
   - Disable Performance: ✅ **On**

2. **For Grafana** (grafana.connectedhome.cz/*):
   - Browser Cache TTL: **30 minutes**
   - Cache Level: **Standard**
   - Security Level: **Medium**

## 🔧 Network Configuration

### Port Forwarding on Your Router

Make sure your router forwards these ports to your server:
- **Port 80** (HTTP) → Your server IP
- **Port 443** (HTTPS) → Your server IP

### Firewall Configuration on Server

If using UFW (Ubuntu Firewall):
```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow specific services (if needed locally)
sudo ufw allow from 192.168.0.0/16 to any port 8123  # Home Assistant
sudo ufw allow from 192.168.0.0/16 to any port 9090  # Grafana/Prometheus

# Reload firewall
sudo ufw reload
```

## 📋 SSL Certificate Installation Script

Create this script to install your CloudFlare certificates:

```bash
#!/bin/bash
# install-cloudflare-certs.sh

# Create SSL directory
sudo mkdir -p /etc/nginx/ssl

# Set secure permissions
sudo chmod 700 /etc/nginx/ssl

# Copy certificates (replace with your actual certificate content)
sudo tee /etc/nginx/ssl/connectedhome.cz.crt << 'EOF'
-----BEGIN CERTIFICATE-----
[PASTE YOUR CLOUDFLARE ORIGIN CERTIFICATE HERE]
-----END CERTIFICATE-----
EOF

sudo tee /etc/nginx/ssl/connectedhome.cz.key << 'EOF'
-----BEGIN PRIVATE KEY-----
[PASTE YOUR PRIVATE KEY HERE]  
-----END PRIVATE KEY-----
EOF

# Set correct permissions
sudo chmod 600 /etc/nginx/ssl/*
sudo chown root:root /etc/nginx/ssl/*

# Generate default certificate for unknown domains
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/default.key \
    -out /etc/nginx/ssl/default.crt \
    -subj "/C=CZ/ST=Prague/L=Prague/O=Default/CN=default"

echo "CloudFlare certificates installed successfully!"
```

## 🚀 Deployment Steps

### 1. Update Docker Compose

Update your `docker-compose.uat.yml` to use the new nginx configuration:

```yaml
  uat-proxy:
    image: nginx:alpine
    container_name: familycart-uat-proxy
    volumes:
      - ./nginx/multi-service.conf:/etc/nginx/nginx.conf:ro  # Updated config
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - uat-frontend
      - uat-backend
    networks:
      - uat-network
    healthcheck:
      test: ["CMD", "nginx", "-t"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
```

### 2. Testing Checklist

After deployment, test each service:

1. **FamilyCart UAT**: https://uat.familycart.local
2. **Grafana**: https://grafana.connectedhome.cz  
3. **Home Assistant**: https://homeassistant.connectedhome.cz
4. **Health checks**:
   - https://uat.familycart.local/health
   - https://grafana.connectedhome.cz/health
   - https://homeassistant.connectedhome.cz/health

### 3. Log Monitoring

Monitor the dedicated log files:
```bash
# FamilyCart UAT logs
tail -f /var/log/nginx/familycart-uat.access.log
tail -f /var/log/nginx/familycart-uat.error.log

# Grafana logs  
tail -f /var/log/nginx/grafana.access.log
tail -f /var/log/nginx/grafana.error.log

# Home Assistant logs
tail -f /var/log/nginx/homeassistant.access.log
tail -f /var/log/nginx/homeassistant.error.log
```

## 🔍 Troubleshooting

### Common Issues

1. **SSL Certificate Errors**:
   - Verify certificate files exist and have correct permissions
   - Check CloudFlare SSL/TLS mode is set to "Full (strict)"

2. **Home Assistant Connection Issues**:
   - Verify 192.168.3.30:8123 is accessible from nginx container
   - Check Home Assistant configuration allows proxy connections

3. **Rate Limiting Issues**:
   - Adjust rate limiting zones in nginx config if needed
   - Monitor nginx error logs for rate limit messages

### Useful Commands

```bash
# Test nginx configuration
docker exec familycart-uat-proxy nginx -t

# Reload nginx without downtime  
docker exec familycart-uat-proxy nginx -s reload

# Check certificate expiration
openssl x509 -in /etc/nginx/ssl/connectedhome.cz.crt -noout -dates
```

## 🔒 Security Considerations

1. **IP Allowlisting**: Consider restricting access to Grafana and Home Assistant to specific IP ranges
2. **Authentication**: Ensure both services have proper authentication configured
3. **Regular Updates**: Keep nginx, certificates, and services updated
4. **Log Monitoring**: Set up alerts for unusual access patterns
5. **Backup**: Regularly backup your SSL certificates and configurations

## 📞 Next Steps

1. Configure DNS records in CloudFlare
2. Generate and install Origin certificates  
3. Update nginx configuration
4. Test all services
5. Set up monitoring and alerting
6. Configure service-specific authentication if needed

This setup provides a robust, scalable foundation for hosting multiple services behind a single nginx proxy with CloudFlare integration.
