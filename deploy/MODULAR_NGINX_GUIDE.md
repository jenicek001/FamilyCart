# Modular Nginx Configuration Guide

This guide explains the modular nginx configuration system that replaces the monolithic approach.

## 🏗️ Architecture Overview

Instead of one giant configuration file, we now have a **clean, modular structure**:

```
deploy/nginx/
├── nginx.conf                 # Main config with includes
├── conf.d/                    # Shared configurations
│   ├── upstreams.conf         # Backend service definitions  
│   ├── rate-limiting.conf     # Rate limiting zones
│   ├── ssl-common.conf        # Shared SSL settings
│   └── cloudflare-realip.conf # CloudFlare IP ranges (single source)
├── sites-available/           # Individual site configs
│   ├── familycart-uat         # FamilyCart UAT site
│   ├── grafana                # Grafana monitoring  
│   ├── homeassistant          # Home Assistant
│   └── default                # Catch-all for unknown domains
├── sites-enabled/             # Enabled sites (symlinks)
│   ├── familycart-uat -> ../sites-available/familycart-uat
│   └── default -> ../sites-available/default
└── ssl/                       # Organized certificate storage
    ├── familycart/            # FamilyCart certificates
    ├── connectedhome.cz/      # connectedhome.cz certificates  
    └── default/               # Default/fallback certificates
```

## ✅ Key Advantages

### **vs. Previous Monolithic Approach:**

| Aspect | ❌ Monolithic | ✅ Modular |
|--------|-------------|-----------|
| **Configuration Size** | 400+ lines in one file | ~50-80 lines per service |
| **SSL Management** | Duplicated 3x | Single SSL config + per-domain certs |
| **CloudFlare IPs** | Repeated 3x | Single source of truth |
| **Service Management** | Edit giant file | Enable/disable with symlinks |
| **Maintainability** | Risk breaking all services | Isolate changes per service |
| **Testing** | All-or-nothing | Test individual services |
| **Transparency** | Opaque giant blob | Crystal clear what each file does |

### **Certificate Organization:**
```
ssl/
├── familycart/uat.familycart.local.{crt,key}       # FamilyCart only
├── connectedhome.cz/connectedhome.cz.{crt,key}     # Grafana + HomeAssistant  
└── default/default.{crt,key}                       # Fallback for unknowns
```

## 🚀 Management Commands

### **List Available Sites:**
```bash
./nginx-site-manager.sh list
```

### **Enable/Disable Services:**
```bash
# Enable Grafana
./nginx-site-manager.sh enable grafana

# Enable Home Assistant  
./nginx-site-manager.sh enable homeassistant

# Disable a service
./nginx-site-manager.sh disable grafana
```

### **Test Configuration:**
```bash
./nginx-site-manager.sh test
```

### **Reload Nginx:**
```bash
./nginx-site-manager.sh reload
```

## 📦 Deployment Workflow

### **1. Initial Setup:**
```bash
# Deploy the modular structure
./deploy-modular-nginx.sh

# Set up SSL certificates
./setup-ssl-certificates.sh
```

### **2. Enable Services as Needed:**
```bash
# FamilyCart UAT is enabled by default
./nginx-site-manager.sh enable grafana
./nginx-site-manager.sh enable homeassistant

# Test everything works
./nginx-site-manager.sh test
./nginx-site-manager.sh reload
```

## 🔧 Adding New Services

### **1. Create Site Configuration:**
Create `/deploy/nginx/sites-available/newservice`:
```nginx
server {
    listen 443 ssl http2;
    server_name newservice.yourdomain.com;

    # SSL Certificate
    ssl_certificate /etc/nginx/ssl/yourdomain.com/yourdomain.com.crt;
    ssl_certificate_key /etc/nginx/ssl/yourdomain.com/yourdomain.com.key;
    
    # Include shared configs
    include /etc/nginx/conf.d/ssl-common.conf;
    include /etc/nginx/conf.d/cloudflare-realip.conf;

    # Service-specific configuration
    location / {
        proxy_pass http://your_upstream/;
        # ... proxy settings
    }
}
```

### **2. Add Upstream (if needed):**
Edit `/deploy/nginx/conf.d/upstreams.conf`:
```nginx
upstream your_upstream {
    server your-service:port max_fails=3 fail_timeout=30s;
}
```

### **3. Enable the Service:**
```bash
./nginx-site-manager.sh enable newservice
./nginx-site-manager.sh test
./nginx-site-manager.sh reload
```

## 🔐 SSL Certificate Management

### **Certificate Structure:**
```
ssl/
├── familycart/
│   └── uat.familycart.local.{crt,key}
├── connectedhome.cz/  
│   └── connectedhome.cz.{crt,key}        # Wildcard cert for *.connectedhome.cz
└── default/
    └── default.{crt,key}                 # Self-signed fallback
```

### **Adding New Domain Certificates:**
1. Create directory: `ssl/newdomain.com/`
2. Add certificates: `newdomain.com.{crt,key}`
3. Reference in site config: `ssl_certificate /etc/nginx/ssl/newdomain.com/newdomain.com.crt;`

## 🧪 Testing Individual Services

### **Test Single Service:**
```bash
# Test only FamilyCart
docker run --rm -v $(pwd)/deploy/nginx/sites-available/familycart-uat:/etc/nginx/conf.d/test.conf:ro nginx:alpine nginx -t

# Test only Grafana  
docker run --rm -v $(pwd)/deploy/nginx/sites-available/grafana:/etc/nginx/conf.d/test.conf:ro nginx:alpine nginx -t
```

### **Test Full Configuration:**
```bash
./nginx-site-manager.sh test
```

## 📊 Monitoring & Logs

### **Separate Log Files:**
- `/var/log/nginx/familycart-uat.{access,error}.log`
- `/var/log/nginx/grafana.{access,error}.log` 
- `/var/log/nginx/homeassistant.{access,error}.log`
- `/var/log/nginx/unknown-domains.{access,error}.log`

### **Monitor Logs:**
```bash
# Monitor specific service
tail -f logs/nginx/grafana.access.log

# Monitor all services
tail -f logs/nginx/*.log
```

## 🔄 Migration from Monolithic

### **What Changed:**
1. **Single `multi-service.conf`** → **Multiple focused files**
2. **Repeated SSL config** → **Shared SSL config with includes**
3. **Mixed certificates** → **Organized by domain**
4. **All-or-nothing** → **Enable/disable individual services**

### **Migration Steps:**
1. Deploy new structure: `./deploy-modular-nginx.sh`
2. Set up certificates: `./setup-ssl-certificates.sh`
3. Enable needed services: `./nginx-site-manager.sh enable <service>`
4. Test: `./nginx-site-manager.sh test`
5. Deploy: `./nginx-site-manager.sh reload`

## 🆚 Comparison Example

### **❌ Old Monolithic Way:**
```nginx
# 400+ lines with everything mixed together
server {
    listen 443 ssl http2;
    server_name uat.familycart.local grafana.connectedhome.cz homeassistant.connectedhome.cz;
    
    # SSL config repeated 3 times
    ssl_certificate /etc/nginx/ssl/cert1.crt;
    # ... 20 lines of SSL config
    
    # CloudFlare IPs repeated 3 times  
    set_real_ip_from 103.21.244.0/22;
    # ... 15 lines of IP ranges
    
    # Everything mixed together...
}
```

### **✅ New Modular Way:**
```nginx
# familycart-uat (50 lines, focused)
server {
    listen 443 ssl http2;
    server_name uat.familycart.local;
    
    ssl_certificate /etc/nginx/ssl/familycart/uat.familycart.local.crt;
    ssl_certificate_key /etc/nginx/ssl/familycart/uat.familycart.local.key;
    
    include /etc/nginx/conf.d/ssl-common.conf;      # Shared SSL config
    include /etc/nginx/conf.d/cloudflare-realip.conf; # Shared CloudFlare IPs
    
    # FamilyCart-specific config only...
}
```

## 🎯 Best Practices

1. **One service per file** in `sites-available/`
2. **Shared config in `conf.d/`** (SSL, upstreams, rate limiting)
3. **Organized certificates** by domain in `ssl/domain/`
4. **Test before enabling** any new service
5. **Use meaningful names** for sites and upstreams
6. **Document service-specific** requirements in comments
7. **Keep security headers** service-appropriate (e.g., Grafana needs `SAMEORIGIN`)

This modular approach provides **transparency, maintainability, and safety** - exactly what you requested!
