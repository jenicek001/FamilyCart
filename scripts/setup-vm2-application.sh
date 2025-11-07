#!/bin/bash
set -e

echo "========================================"
echo "FamilyCart VM2 Application Server Setup"
echo "========================================"
echo ""

# Variables
VM2_PRIVATE_IP="10.0.1.145"
VM1_PRIVATE_IP="10.0.1.191"
VCN_CIDR="10.0.0.0/16"

echo "📦 Step 1: Update system packages..."
sudo apt-get update
sudo apt-get upgrade -y

echo ""
echo "🐳 Step 2: Install Docker and Docker Compose..."
# Install prerequisites
sudo apt-get install -y ca-certificates curl gnupg lsb-release jq

# Add Docker GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add ubuntu user to docker group
sudo usermod -aG docker ubuntu

echo "✅ Docker installed: $(docker --version)"
echo "✅ Docker Compose installed: $(docker compose version)"

echo ""
echo "🌐 Step 3: Install and configure Nginx..."
sudo apt-get install -y nginx
sudo systemctl enable nginx
echo "✅ Nginx installed: $(nginx -v 2>&1)"

echo ""
echo "🔥 Step 4: Configure nftables firewall with Cloudflare IP allowlist..."
# Install nftables
sudo apt-get install -y nftables

# Create Cloudflare IP update script
sudo tee /usr/local/bin/update-cloudflare-ips.sh > /dev/null << 'CFEOF'
#!/bin/bash
set -e

# Fetch Cloudflare IP ranges
CF_IPS_V4=$(curl -s https://www.cloudflare.com/ips-v4)
CF_IPS_V6=$(curl -s https://www.cloudflare.com/ips-v6)

# Create nftables configuration with Cloudflare IPs
cat > /etc/nftables.conf << 'EOF'
#!/usr/sbin/nft -f

flush ruleset

# Define Cloudflare IPv4 ranges
define cloudflare_ips_v4 = {
EOF

# Add Cloudflare IPv4 ranges
echo "$CF_IPS_V4" | while read ip; do
    echo "    $ip," >> /etc/nftables.conf
done

cat >> /etc/nftables.conf << 'EOF'
}

# Define Cloudflare IPv6 ranges
define cloudflare_ips_v6 = {
EOF

# Add Cloudflare IPv6 ranges
echo "$CF_IPS_V6" | while read ip; do
    echo "    $ip," >> /etc/nftables.conf
done

cat >> /etc/nftables.conf << 'EOF'
}

table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;

        # Allow established/related connections
        ct state established,related accept

        # Allow loopback
        iif lo accept

        # Allow SSH from anywhere (for management)
        tcp dport 22 accept

        # Allow HTTP/HTTPS ONLY from Cloudflare IPs
        ip saddr $cloudflare_ips_v4 tcp dport { 80, 443 } accept
        ip6 saddr $cloudflare_ips_v6 tcp dport { 80, 443 } accept

        # Allow ICMP (ping)
        icmp type echo-request accept
        icmpv6 type echo-request accept

        # Log dropped packets (optional, for debugging)
        # counter log prefix "nft-drop: " drop
    }

    chain forward {
        type filter hook forward priority 0; policy drop;
    }

    chain output {
        type filter hook output priority 0; policy accept;
    }
}
EOF

# Reload nftables
systemctl restart nftables

echo "Cloudflare IPs updated at $(date)"
CFEOF

sudo chmod +x /usr/local/bin/update-cloudflare-ips.sh

# Run initial Cloudflare IP update
echo "Updating Cloudflare IP ranges..."
sudo /usr/local/bin/update-cloudflare-ips.sh

# Enable and start nftables
sudo systemctl enable nftables
sudo systemctl restart nftables

echo "✅ Firewall configured - HTTP/HTTPS restricted to Cloudflare only"
sudo nft list ruleset | head -20

echo ""
echo "📅 Step 5: Setup Cloudflare IP auto-update (daily at 2 AM)..."
# Install cron if not already installed
sudo apt-get install -y cron
sudo systemctl enable cron
sudo systemctl start cron

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null | grep -v update-cloudflare-ips.sh; echo "0 2 * * * /usr/local/bin/update-cloudflare-ips.sh >> /var/log/cloudflare-ip-update.log 2>&1") | crontab -

echo "✅ Daily Cloudflare IP update configured (2 AM)"

echo ""
echo "📁 Step 6: Create deployment directory..."
sudo mkdir -p /opt/familycart-app
sudo chown ubuntu:ubuntu /opt/familycart-app
cd /opt/familycart-app

echo ""
echo "🔐 Step 7: Generate application secrets..."
SECRET_KEY=$(openssl rand -base64 32)
GITHUB_TOKEN_PLACEHOLDER="YOUR_GITHUB_PAT"

echo "Generated application secret key"
echo ""

echo "💾 Step 8: Create environment configuration..."
cat > /opt/familycart-app/.env.app << EOF
# Application Configuration
SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database Configuration (VM1 Private IP)
POSTGRES_SERVER=$VM1_PRIVATE_IP
POSTGRES_PORT=5432
POSTGRES_USER=familycart
POSTGRES_PASSWORD=REPLACE_WITH_VM1_POSTGRES_PASSWORD
POSTGRES_DB=familycart_production

# Redis Configuration (VM1 Private IP)
REDIS_URI=redis://:REPLACE_WITH_VM1_REDIS_PASSWORD@$VM1_PRIVATE_IP:6379

# CORS Configuration
CORS_ORIGINS=["https://familycart.com","https://www.familycart.com"]

# Frontend Configuration
NEXT_PUBLIC_API_URL=https://familycart.com/api

# GitHub Container Registry
GITHUB_USERNAME=jenicek001
GITHUB_TOKEN=$GITHUB_TOKEN_PLACEHOLDER
EOF

chmod 600 /opt/familycart-app/.env.app

echo "⚠️  IMPORTANT: You need to update .env.app with:"
echo "  1. VM1 PostgreSQL password"
echo "  2. VM1 Redis password"
echo "  3. GitHub Personal Access Token"

echo ""
echo "🐳 Step 9: Create Docker Compose configuration..."
cat > /opt/familycart-app/docker-compose.yml << 'EOF'
services:
  backend:
    image: ghcr.io/jenicek001/familycart-backend:latest
    container_name: familycart-prod-backend
    restart: unless-stopped
    env_file:
      - .env.app
    environment:
      POSTGRES_SERVER: ${POSTGRES_SERVER}
      POSTGRES_PORT: ${POSTGRES_PORT}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
      REDIS_URI: ${REDIS_URI}
      SECRET_KEY: ${SECRET_KEY}
      ALGORITHM: ${ALGORITHM}
      ACCESS_TOKEN_EXPIRE_MINUTES: ${ACCESS_TOKEN_EXPIRE_MINUTES}
      CORS_ORIGINS: ${CORS_ORIGINS}
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    depends_on:
      - wait-for-db

  frontend:
    image: ghcr.io/jenicek001/familycart-frontend:latest
    container_name: familycart-prod-frontend
    restart: unless-stopped
    environment:
      NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL}
    ports:
      - "3000:3000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    depends_on:
      backend:
        condition: service_healthy

  wait-for-db:
    image: postgres:15-alpine
    container_name: familycart-wait-for-db
    restart: "no"
    env_file:
      - .env.app
    command: >
      sh -c "
        until pg_isready -h ${POSTGRES_SERVER} -p ${POSTGRES_PORT} -U ${POSTGRES_USER}; do
          echo 'Waiting for PostgreSQL on VM1...';
          sleep 2;
        done;
        echo 'PostgreSQL is ready!';
      "
EOF

echo ""
echo "🌐 Step 10: Configure Nginx reverse proxy..."
sudo tee /etc/nginx/sites-available/familycart << 'NGINXEOF'
# Upstream backends
upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:3000;
}

# HTTP - Redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name familycart.com www.familycart.com;

    # Allow Cloudflare IPs only (enforced by nftables)
    
    # Redirect all HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS - Main application
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name familycart.com www.familycart.com;

    # SSL certificates (will be configured with Cloudflare Origin Certificate)
    ssl_certificate /etc/nginx/ssl/familycart.com.pem;
    ssl_certificate_key /etc/nginx/ssl/familycart.com.key;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Cloudflare real IP
    set_real_ip_from 0.0.0.0/0;
    real_ip_header CF-Connecting-IP;

    # API requests to backend
    location /api {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://backend/health;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        access_log off;
    }

    # Frontend - Next.js
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files caching
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        proxy_pass http://frontend;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
NGINXEOF

# Create SSL directory
sudo mkdir -p /etc/nginx/ssl

# Create placeholder self-signed certificate (will be replaced with Cloudflare cert)
echo "Creating temporary self-signed certificate..."
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/familycart.com.key \
    -out /etc/nginx/ssl/familycart.com.pem \
    -subj "/C=US/ST=State/L=City/O=FamilyCart/CN=familycart.com" 2>/dev/null

# Enable site
sudo ln -sf /etc/nginx/sites-available/familycart /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Don't start nginx yet - will start after getting SSL cert
echo "✅ Nginx configured (will start after SSL setup)"

echo ""
echo "========================================"
echo "✅ VM2 Application Server Setup Complete!"
echo "========================================"
echo ""
echo "📊 Summary:"
echo "  - Docker & Docker Compose: Installed"
echo "  - Nginx: Configured (not started yet)"
echo "  - Firewall: Configured (HTTP/HTTPS from Cloudflare only)"
echo "  - Cloudflare IP Auto-update: Daily at 2 AM"
echo "  - Deployment directory: /opt/familycart-app"
echo ""
echo "⚠️  MANUAL STEPS REQUIRED:"
echo ""
echo "1. Update /opt/familycart-app/.env.app with database credentials:"
echo "   - Replace REPLACE_WITH_VM1_POSTGRES_PASSWORD"
echo "   - Replace REPLACE_WITH_VM1_REDIS_PASSWORD"
echo "   - Replace YOUR_GITHUB_PAT with your GitHub token"
echo ""
echo "2. Login to GitHub Container Registry:"
echo "   echo \"YOUR_GITHUB_PAT\" | docker login ghcr.io -u jenicek001 --password-stdin"
echo ""
echo "3. Pull Docker images:"
echo "   cd /opt/familycart-app"
echo "   docker compose pull"
echo ""
echo "4. Setup Cloudflare Origin Certificate:"
echo "   - Create certificate in Cloudflare dashboard"
echo "   - Save certificate to /etc/nginx/ssl/familycart.com.pem"
echo "   - Save private key to /etc/nginx/ssl/familycart.com.key"
echo ""
echo "5. Start services:"
echo "   cd /opt/familycart-app"
echo "   docker compose up -d"
echo "   sudo systemctl restart nginx"
echo ""
echo "🔍 Useful commands:"
echo "  - Check services: cd /opt/familycart-app && docker compose ps"
echo "  - View logs: docker compose logs -f"
echo "  - Test backend: curl http://localhost:8000/health"
echo "  - Test frontend: curl http://localhost:3000/"
echo "  - Check nginx: sudo nginx -t"
echo "  - Restart nginx: sudo systemctl restart nginx"
echo ""
