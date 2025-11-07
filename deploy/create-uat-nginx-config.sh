#!/bin/bash
# create-uat-nginx-config.sh
# Script to generate UAT-compatible nginx configuration from modular structure

set -e

PROJECT_ROOT="/home/honzik/GitHub/FamilyCart/FamilyCart"
MODULAR_NGINX_DIR="$PROJECT_ROOT/deploy/nginx"
UAT_NGINX_DIR="$PROJECT_ROOT/nginx"

echo "🔧 Creating UAT Nginx Configuration"
echo "==================================="

# Function to create unified UAT config (Approach A)
create_unified_uat_config() {
    echo "📦 Generating unified uat.conf from modular structure..."
    
    cat > "$UAT_NGINX_DIR/uat.conf" << 'EOF'
# UAT Nginx Configuration - Generated from Modular Structure
# DO NOT EDIT DIRECTLY - Regenerate using create-uat-nginx-config.sh

events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Logging configuration
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;

    # Performance settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 10M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=web:10m rate=30r/s;

    # Upstream definitions for FamilyCart UAT
    upstream uat_backend {
        server uat-backend:8000 max_fails=3 fail_timeout=30s;
    }

    upstream uat_frontend {
        server uat-frontend:3000 max_fails=3 fail_timeout=30s;
    }

    # WebSocket connection upgrade map
    map $http_upgrade $connection_upgrade {
        default upgrade;
        ''      close;
    }

    # CloudFlare Real IP configuration
    set_real_ip_from 103.21.244.0/22;
    set_real_ip_from 103.22.200.0/22;
    set_real_ip_from 103.31.4.0/22;
    set_real_ip_from 104.16.0.0/13;
    set_real_ip_from 104.24.0.0/14;
    set_real_ip_from 108.162.192.0/18;
    set_real_ip_from 131.0.72.0/22;
    set_real_ip_from 141.101.64.0/18;
    set_real_ip_from 162.158.0.0/15;
    set_real_ip_from 172.64.0.0/13;
    set_real_ip_from 173.245.48.0/20;
    set_real_ip_from 188.114.96.0/20;
    set_real_ip_from 190.93.240.0/20;
    set_real_ip_from 197.234.240.0/22;
    set_real_ip_from 198.41.128.0/17;
    set_real_ip_from 2400:cb00::/32;
    set_real_ip_from 2606:4700::/32;
    set_real_ip_from 2803:f800::/32;
    set_real_ip_from 2405:b500::/32;
    set_real_ip_from 2405:8100::/32;
    real_ip_header CF-Connecting-IP;

    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name uat.familycart.local localhost;
        
        # Health check endpoint (no redirect)
        location /health {
            access_log off;
            return 200 "FamilyCart UAT HTTP Healthy\n";
            add_header Content-Type text/plain;
        }
        
        # Redirect all other traffic to HTTPS
        location / {
            return 301 https://$server_name$request_uri;
        }
    }

    # HTTPS server for FamilyCart UAT
    server {
        listen 443 ssl http2;
        server_name uat.familycart.local localhost;

        # SSL Certificate
        ssl_certificate /etc/nginx/ssl/uat.familycart.local.crt;
        ssl_certificate_key /etc/nginx/ssl/uat.familycart.local.key;
        
        # Modern SSL configuration
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        
        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options DENY always;
        add_header X-Content-Type-Options nosniff always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' wss: https:; font-src 'self' data:;" always;

        # Dedicated access and error logs
        access_log /var/log/nginx/familycart-uat.access.log main;
        error_log /var/log/nginx/familycart-uat.error.log;

        # API endpoints
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://uat_backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # API-specific timeouts
            proxy_connect_timeout 10s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
            
            # CORS headers for UAT testing
            add_header Access-Control-Allow-Origin "https://uat.familycart.local" always;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
            add_header Access-Control-Allow-Headers "Accept, Authorization, Cache-Control, Content-Type, DNT, If-Modified-Since, Keep-Alive, Origin, User-Agent, X-Requested-With" always;
            add_header Access-Control-Allow-Credentials true always;
            
            # Handle preflight requests
            if ($request_method = 'OPTIONS') {
                return 204;
            }
        }

        # WebSocket endpoints
        location /ws {
            proxy_pass http://uat_backend/ws;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection $connection_upgrade;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket specific settings
            proxy_read_timeout 86400;
            proxy_send_timeout 86400;
            proxy_connect_timeout 10s;
        }

        # Frontend application
        location / {
            limit_req zone=web burst=50 nodelay;
            
            proxy_pass http://uat_frontend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Frontend-specific timeouts
            proxy_connect_timeout 5s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
            
            # Cache static assets
            location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
                expires 1y;
                add_header Cache-Control "public, immutable";
                access_log off;
            }
        }

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "FamilyCart UAT HTTPS Healthy\n";
            add_header Content-Type text/plain;
        }

        # Monitoring endpoints (if enabled)
        location /metrics {
            allow 127.0.0.1;
            allow 172.20.0.0/16;  # UAT network
            deny all;
            
            proxy_pass http://uat_backend/metrics;
            proxy_set_header Host $host;
        }

        # Block access to sensitive files
        location ~ /\. {
            deny all;
            access_log off;
            log_not_found off;
        }
        
        location ~ \.(env|log|sql|bak)$ {
            deny all;
            access_log off;
            log_not_found off;
        }
    }
}
EOF

    echo "✅ Unified uat.conf created"
}

# Function to create modular structure for UAT (Approach B)
create_modular_uat_structure() {
    echo "📁 Creating modular nginx structure for UAT..."
    
    # Copy modular structure to nginx directory
    cp -r "$MODULAR_NGINX_DIR"/* "$UAT_NGINX_DIR/"
    
    # Update the main nginx.conf to remove dev-specific paths
    sed -i 's|/home/honzik/GitHub/FamilyCart/FamilyCart/deploy/nginx|/etc/nginx|g' "$UAT_NGINX_DIR/nginx.conf"
    
    echo "✅ Modular structure copied to nginx/"
}

# Function to create SSL directory structure
create_ssl_structure() {
    echo "🔐 Creating SSL directory structure..."
    
    mkdir -p "$UAT_NGINX_DIR/ssl"
    
    cat > "$UAT_NGINX_DIR/ssl/README.md" << 'EOF'
# SSL Certificates for UAT Environment

## Directory Structure
```
ssl/
├── uat.familycart.local.crt  # Primary UAT certificate
├── uat.familycart.local.key  # Primary UAT private key
└── README.md                 # This file
```

## Certificate Installation

### For Self-Signed (Development/Testing):
```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/uat.familycart.local.key \
    -out ssl/uat.familycart.local.crt \
    -subj "/C=CZ/ST=Prague/L=Prague/O=FamilyCart/CN=uat.familycart.local"

# Set correct permissions
chmod 600 ssl/uat.familycart.local.*
```

### For Production Certificates:
1. Obtain certificates from your CA
2. Copy certificate to `ssl/uat.familycart.local.crt`
3. Copy private key to `ssl/uat.familycart.local.key`  
4. Set permissions: `chmod 600 ssl/uat.familycart.local.*`
EOF

    echo "✅ SSL directory structure created"
}

# Main execution
main() {
    echo "This script will prepare nginx configuration for UAT deployment."
    echo ""
    echo "Choose deployment approach:"
    echo "1. Unified config (backward compatible with existing UAT setup)"
    echo "2. Modular structure (requires updating UAT docker-compose.yml)"
    echo ""
    read -p "Enter choice (1 or 2): " -n 1 -r
    echo
    
    case $REPLY in
        1)
            echo "📦 Creating unified UAT configuration..."
            create_unified_uat_config
            create_ssl_structure
            
            echo ""
            echo "✅ Unified UAT configuration created!"
            echo "📁 Location: $UAT_NGINX_DIR/uat.conf"
            echo ""
            echo "📋 Next steps:"
            echo "1. Install SSL certificates in $UAT_NGINX_DIR/ssl/"
            echo "2. Commit changes: git add nginx/ && git commit -m 'feat: add UAT nginx config'"
            echo "3. Deploy to UAT: git push && cd /opt/familycart-uat-repo && git pull"
            ;;
        2)
            echo "📁 Creating modular UAT structure..."
            create_modular_uat_structure
            create_ssl_structure
            
            echo ""
            echo "✅ Modular UAT structure created!"
            echo "📁 Location: $UAT_NGINX_DIR/"
            echo ""
            echo "⚠️  IMPORTANT: Update UAT docker-compose.yml volume mounts:"
            echo "   Change from:"
            echo "     - ./nginx/uat.conf:/etc/nginx/nginx.conf:ro"
            echo "   To:"
            echo "     - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro"
            echo "     - ./nginx/sites-available:/etc/nginx/sites-available:ro"
            echo "     - ./nginx/sites-enabled:/etc/nginx/sites-enabled:ro"
            echo "     - ./nginx/conf.d:/etc/nginx/conf.d:ro"
            echo "     - ./nginx/ssl:/etc/nginx/ssl:ro"
            echo ""
            echo "📋 Next steps:"
            echo "1. Update docker-compose.uat.yml volume mounts"
            echo "2. Install SSL certificates in $UAT_NGINX_DIR/ssl/"
            echo "3. Commit changes: git add nginx/ docker-compose.uat.yml"
            echo "4. Deploy to UAT"
            ;;
        *)
            echo "❌ Invalid choice"
            exit 1
            ;;
    esac
    
    echo ""
    echo "🎯 UAT nginx configuration ready for deployment!"
}

# Run main function
main "$@"
