# FamilyCart Production Deployment Guide
## Oracle Cloud Free Tier + Cloudflare + CI/CD

**Last Updated:** November 3, 2025  
**Target:** Production environment on OCI with automated CI/CD from main branch

---

## 📐 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Cloudflare (Global CDN)                      │
│  familycart.com, www.familycart.com → VM2 Public IP            │
│  Protection: WAF, DDoS, Rate Limiting, Bot Management           │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTPS (443)
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Oracle Cloud Infrastructure                    │
│                         Free Tier (2 VMs)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  VM1 (Database)                    VM2 (Application)            │
│  ┌──────────────┐                  ┌──────────────┐            │
│  │ PostgreSQL   │◄─────────────────┤ Backend API  │            │
│  │ Port: 5432   │  Private Network │ Port: 8000   │            │
│  ├──────────────┤                  ├──────────────┤            │
│  │ Redis        │◄─────────────────┤ Frontend     │            │
│  │ Port: 6379   │                  │ Port: 3000   │            │
│  └──────────────┘                  └──────────────┘            │
│   Private IP only                   Public IP (Cloudflare only) │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

GitHub Actions CI/CD Pipeline:
main branch → Build → Push Images → Deploy to VM2 (manual approval)
```

**VM Specifications (OCI Free Tier):**
- **VM1 (Database):** VM.Standard.E2.1.Micro (1 OCPU, 1GB RAM, 47GB Boot)
- **VM2 (Application):** VM.Standard.E2.1.Micro (1 OCPU, 1GB RAM, 47GB Boot)
- **OS:** Ubuntu 24.04 LTS (x86_64/AMD64)
- **Region:** Choose closest to users (e.g., eu-frankfurt-1)
- **Note:** ARM64 instances are rarely available in Free Tier; use AMD64 for compatibility

---

## 🚀 Deployment Steps

### Phase 1: OCI Infrastructure Setup

#### 1.1 Create OCI Account and Compartment

1. **Sign up for Oracle Cloud Free Tier:**
   - Visit: https://www.oracle.com/cloud/free/
   - Complete registration
   - Verify email and set up account

2. **Create Compartment for FamilyCart:**
   ```bash
   # Via OCI CLI (install first: https://docs.oracle.com/iaas/Content/API/SDKDocs/cliinstall.htm)
   oci iam compartment create \
     --compartment-id <your-tenancy-ocid> \
     --name "familycart-production" \
     --description "FamilyCart production environment"
   ```

   Or via Console:
   - Navigate to: Identity & Security → Compartments
   - Click "Create Compartment"
   - Name: `familycart-production`
   - Description: `FamilyCart production environment`

#### 1.2 Create Virtual Cloud Network (VCN)

```bash
# Create VCN
oci network vcn create \
  --compartment-id <compartment-ocid> \
  --display-name "familycart-vcn" \
  --cidr-block "10.0.0.0/16" \
  --dns-label "familycart"

# Note the VCN OCID from output
VCN_OCID="<vcn-ocid>"
```

Or via Console:
- Navigate to: Networking → Virtual Cloud Networks
- Click "Create VCN"
- Name: `familycart-vcn`
- IPv4 CIDR Block: `10.0.0.0/16`
- Check "Use DNS hostnames in this VCN"

#### 1.3 Create Internet Gateway

```bash
# Create Internet Gateway
oci network internet-gateway create \
  --compartment-id <compartment-ocid> \
  --vcn-id $VCN_OCID \
  --display-name "familycart-igw" \
  --is-enabled true

# Note the Internet Gateway OCID
IGW_OCID="<igw-ocid>"
```

#### 1.4 Create Route Table

```bash
# Create Route Table with internet gateway route
oci network route-table create \
  --compartment-id <compartment-ocid> \
  --vcn-id $VCN_OCID \
  --display-name "familycart-public-rt" \
  --route-rules '[
    {
      "destination": "0.0.0.0/0",
      "networkEntityId": "'$IGW_OCID'"
    }
  ]'

RT_OCID="<route-table-ocid>"
```

#### 1.5 Create Security Lists

**Public Security List (VM2 - Application):**
```bash
oci network security-list create \
  --compartment-id <compartment-ocid> \
  --vcn-id $VCN_OCID \
  --display-name "familycart-public-sl" \
  --egress-security-rules '[
    {
      "destination": "0.0.0.0/0",
      "protocol": "all",
      "isStateless": false
    }
  ]' \
  --ingress-security-rules '[
    {
      "source": "0.0.0.0/0",
      "protocol": "6",
      "isStateless": false,
      "tcpOptions": {
        "destinationPortRange": {
          "min": 22,
          "max": 22
        }
      },
      "description": "SSH access"
    },
    {
      "source": "0.0.0.0/0",
      "protocol": "6",
      "isStateless": false,
      "tcpOptions": {
        "destinationPortRange": {
          "min": 80,
          "max": 80
        }
      },
      "description": "HTTP (Cloudflare only - enforce in nftables)"
    },
    {
      "source": "0.0.0.0/0",
      "protocol": "6",
      "isStateless": false,
      "tcpOptions": {
        "destinationPortRange": {
          "min": 443,
          "max": 443
        }
      },
      "description": "HTTPS (Cloudflare only - enforce in nftables)"
    }
  ]'

PUBLIC_SL_OCID="<public-sl-ocid>"
```

**Private Security List (VM1 - Database):**
```bash
oci network security-list create \
  --compartment-id <compartment-ocid> \
  --vcn-id $VCN_OCID \
  --display-name "familycart-private-sl" \
  --egress-security-rules '[
    {
      "destination": "0.0.0.0/0",
      "protocol": "all",
      "isStateless": false
    }
  ]' \
  --ingress-security-rules '[
    {
      "source": "0.0.0.0/0",
      "protocol": "6",
      "isStateless": false,
      "tcpOptions": {
        "destinationPortRange": {
          "min": 22,
          "max": 22
        }
      },
      "description": "SSH access"
    },
    {
      "source": "10.0.0.0/16",
      "protocol": "6",
      "isStateless": false,
      "tcpOptions": {
        "destinationPortRange": {
          "min": 5432,
          "max": 5432
        }
      },
      "description": "PostgreSQL from VCN"
    },
    {
      "source": "10.0.0.0/16",
      "protocol": "6",
      "isStateless": false,
      "tcpOptions": {
        "destinationPortRange": {
          "min": 6379,
          "max": 6379
        }
      },
      "description": "Redis from VCN"
    }
  ]'

PRIVATE_SL_OCID="<private-sl-ocid>"
```

#### 1.6 Create Subnets

**Public Subnet (for VM2):**
```bash
oci network subnet create \
  --compartment-id <compartment-ocid> \
  --vcn-id $VCN_OCID \
  --display-name "familycart-public-subnet" \
  --cidr-block "10.0.1.0/24" \
  --route-table-id $RT_OCID \
  --security-list-ids '["'$PUBLIC_SL_OCID'"]' \
  --prohibit-public-ip-on-vnic false \
  --dns-label "public"

PUBLIC_SUBNET_OCID="<public-subnet-ocid>"
```

**Private Subnet (for VM1):**
```bash
oci network subnet create \
  --compartment-id <compartment-ocid> \
  --vcn-id $VCN_OCID \
  --display-name "familycart-private-subnet" \
  --cidr-block "10.0.2.0/24" \
  --route-table-id $RT_OCID \
  --security-list-ids '["'$PRIVATE_SL_OCID'"]' \
  --prohibit-public-ip-on-vnic false \
  --dns-label "private"

PRIVATE_SUBNET_OCID="<private-subnet-ocid>"
```

---

### Phase 2: Create Compute Instances

#### 2.1 Create VM1 (Database Server)

```bash
# List available Ubuntu 24.04 images for x86_64 (AMD64)
oci compute image list \
  --compartment-id <compartment-ocid> \
  --operating-system "Canonical Ubuntu" \
  --operating-system-version "24.04" \
  --shape "VM.Standard.E2.1.Micro" \
  --all

# Note the image OCID (look for x86_64/AMD64 architecture, NOT ARM)
IMAGE_OCID="<ubuntu-24.04-amd64-ocid>"

# Create VM1
oci compute instance launch \
  --compartment-id <compartment-ocid> \
  --availability-domain <AD-name> \
  --display-name "familycart-db-vm1" \
  --image-id $IMAGE_OCID \
  --shape "VM.Standard.E2.1.Micro" \
  --subnet-id $PRIVATE_SUBNET_OCID \
  --assign-public-ip true \
  --ssh-authorized-keys-file ~/.ssh/id_rsa.pub \
  --boot-volume-size-in-gbs 47

VM1_OCID="<vm1-ocid>"
```

**Get VM1 IP addresses:**
```bash
# Get public IP
oci compute instance list-vnics \
  --instance-id $VM1_OCID \
  --query 'data[0]."public-ip"' \
  --raw-output

# Get private IP
oci compute instance list-vnics \
  --instance-id $VM1_OCID \
  --query 'data[0]."private-ip"' \
  --raw-output

# Save these for later
VM1_PUBLIC_IP="<vm1-public-ip>"
VM1_PRIVATE_IP="<vm1-private-ip>"
```

#### 2.2 Create VM2 (Application Server)

```bash
# Create VM2
oci compute instance launch \
  --compartment-id <compartment-ocid> \
  --availability-domain <AD-name> \
  --display-name "familycart-app-vm2" \
  --image-id $IMAGE_OCID \
  --shape "VM.Standard.E2.1.Micro" \
  --subnet-id $PUBLIC_SUBNET_OCID \
  --assign-public-ip true \
  --ssh-authorized-keys-file ~/.ssh/id_rsa.pub \
  --boot-volume-size-in-gbs 47

VM2_OCID="<vm2-ocid>"
```

**Get VM2 IP addresses:**
```bash
VM2_PUBLIC_IP=$(oci compute instance list-vnics \
  --instance-id $VM2_OCID \
  --query 'data[0]."public-ip"' \
  --raw-output)

VM2_PRIVATE_IP=$(oci compute instance list-vnics \
  --instance-id $VM2_OCID \
  --query 'data[0]."private-ip"' \
  --raw-output)

echo "VM2 Public IP: $VM2_PUBLIC_IP"
echo "VM2 Private IP: $VM2_PRIVATE_IP"
```

---

### Phase 3: Configure VM1 (Database Server)

#### 3.1 Initial Setup

```bash
# SSH into VM1
ssh ubuntu@$VM1_PUBLIC_IP

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo apt install docker-compose -y

# Install jq for JSON parsing
sudo apt install jq -y

# Logout and login again for docker group to take effect
exit
ssh ubuntu@$VM1_PUBLIC_IP
```

#### 3.2 Configure Firewall (nftables)

```bash
# Create nftables config
sudo tee /etc/nftables.conf << 'EOF'
#!/usr/sbin/nft -f

flush ruleset

table inet filter {
  chain input {
    type filter hook input priority 0; policy drop;
    
    # Allow loopback
    iif lo accept
    
    # Allow established/related
    ct state { established, related } accept
    
    # Allow SSH from anywhere (temporarily, restrict later)
    tcp dport 22 accept
    
    # Allow PostgreSQL from VCN
    ip saddr 10.0.0.0/16 tcp dport 5432 accept
    
    # Allow Redis from VCN
    ip saddr 10.0.0.0/16 tcp dport 6379 accept
    
    # Allow ping
    icmp type echo-request accept
    
    # Log and drop everything else
    log prefix "nftables-drop: " drop
  }
  
  chain forward {
    type filter hook forward priority 0; policy drop;
  }
  
  chain output {
    type filter hook output priority 0; policy accept;
  }
}
EOF

# Enable and start nftables
sudo systemctl enable nftables
sudo systemctl start nftables
```

#### 3.3 Create Database Environment

```bash
# Create deployment directory
sudo mkdir -p /opt/familycart-db
sudo chown ubuntu:ubuntu /opt/familycart-db
cd /opt/familycart-db

# Create .env file with secure passwords
cat > .env << EOF
# PostgreSQL Configuration
POSTGRES_DB=familycart_prod
POSTGRES_USER=familycart
POSTGRES_PASSWORD=$(openssl rand -hex 32)
POSTGRES_PORT=5432

# Redis Configuration
REDIS_PASSWORD=$(openssl rand -hex 32)
REDIS_PORT=6379

# Backup Configuration
BACKUP_RETENTION_DAYS=7
EOF

# Secure the env file
chmod 600 .env

# Display generated passwords (save these securely!)
echo "=== IMPORTANT: Save these credentials securely ==="
cat .env
echo "=================================================="
```

#### 3.4 Create Docker Compose for Databases

```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: familycart-prod-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    networks:
      - db-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'

  redis:
    image: redis:8.0-alpine
    container_name: familycart-prod-redis
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD} --maxmemory 256mb --maxmemory-policy allkeys-lru --save 60 1000
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - db-network
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          memory: 384M
          cpus: '0.3'

volumes:
  postgres_data:
    name: familycart-prod-postgres-data
  redis_data:
    name: familycart-prod-redis-data

networks:
  db-network:
    name: familycart-prod-db-network
EOF
```

#### 3.5 Start Database Services

```bash
# Start services
docker-compose up -d

# Verify services are running
docker-compose ps

# Check logs
docker-compose logs -f
```

#### 3.6 Setup Automated Backups

```bash
# Create backup script
cat > /opt/familycart-db/backup.sh << 'EOF'
#!/bin/bash
set -euo pipefail

# Load environment variables
source /opt/familycart-db/.env

# Configuration
BACKUP_DIR="/opt/familycart-db/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/familycart_backup_$DATE.sql.gz"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Perform backup
echo "Starting PostgreSQL backup..."
docker exec familycart-prod-postgres pg_dump \
  -U "$POSTGRES_USER" \
  -d "$POSTGRES_DB" \
  | gzip > "$BACKUP_FILE"

echo "Backup completed: $BACKUP_FILE"

# Delete backups older than retention period
find "$BACKUP_DIR" -name "familycart_backup_*.sql.gz" -mtime +${BACKUP_RETENTION_DAYS:-7} -delete

echo "Old backups cleaned up (retention: ${BACKUP_RETENTION_DAYS:-7} days)"

# Backup Redis (optional)
docker exec familycart-prod-redis redis-cli -a "$REDIS_PASSWORD" SAVE
cp /var/lib/docker/volumes/familycart-prod-redis-data/_data/dump.rdb "$BACKUP_DIR/redis_backup_$DATE.rdb"

echo "Redis backup completed"
EOF

# Make backup script executable
chmod +x /opt/familycart-db/backup.sh

# Setup daily cron job (3 AM daily)
(crontab -l 2>/dev/null; echo "0 3 * * * /opt/familycart-db/backup.sh >> /opt/familycart-db/backup.log 2>&1") | crontab -

# Test backup immediately
/opt/familycart-db/backup.sh
```

---

### Phase 4: Configure VM2 (Application Server)

#### 4.1 Initial Setup

```bash
# SSH into VM2
ssh ubuntu@$VM2_PUBLIC_IP

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo apt install docker-compose -y

# Install nginx for reverse proxy
sudo apt install nginx -y

# Install jq for JSON parsing
sudo apt install jq -y

# Logout and login again
exit
ssh ubuntu@$VM2_PUBLIC_IP
```

#### 4.2 Configure Cloudflare IP Allowlist

```bash
# Create Cloudflare IP update script
sudo tee /usr/local/bin/update-cloudflare-ips.sh << 'EOF'
#!/bin/bash
set -euo pipefail

# Fetch Cloudflare IPs
TMP=$(mktemp)
curl -s https://api.cloudflare.com/client/v4/ips > "$TMP"

# Extract IPv4 and IPv6 ranges
IPV4=$(jq -r '.result.ipv4_cidrs[]' "$TMP" | paste -sd "," -)
IPV6=$(jq -r '.result.ipv6_cidrs[]' "$TMP" | paste -sd "," -)

# Create nftables include file
cat > /etc/nftables.d/cloudflare.nft <<NFTEOF
define cf_ipv4 = { $IPV4 }
define cf_ipv6 = { $IPV6 }
NFTEOF

# Reload nftables
nft -f /etc/nftables.conf

rm "$TMP"
echo "Cloudflare IPs updated successfully"
EOF

sudo chmod +x /usr/local/bin/update-cloudflare-ips.sh

# Create nftables directory
sudo mkdir -p /etc/nftables.d

# Create main nftables config
sudo tee /etc/nftables.conf << 'EOF'
#!/usr/sbin/nft -f

flush ruleset

include "/etc/nftables.d/cloudflare.nft"

table inet filter {
  chain input {
    type filter hook input priority 0; policy drop;
    
    # Allow loopback
    iif lo accept
    
    # Allow established/related
    ct state { established, related } accept
    
    # Allow SSH (restrict to your IP after initial setup)
    tcp dport 22 accept
    
    # Allow HTTP/HTTPS from Cloudflare only
    tcp dport { 80, 443 } ip saddr @cf_ipv4 accept
    tcp dport { 80, 443 } ip6 saddr @cf_ipv6 accept
    
    # Allow ping
    icmp type echo-request accept
    icmpv6 type { echo-request, nd-neighbor-solicit, nd-neighbor-advert } accept
    
    # Log and drop
    log prefix "nftables-drop: " drop
  }
  
  chain forward {
    type filter hook forward priority 0; policy drop;
  }
  
  chain output {
    type filter hook output priority 0; policy accept;
  }
}
EOF

# Initialize Cloudflare IPs
sudo /usr/local/bin/update-cloudflare-ips.sh

# Enable nftables
sudo systemctl enable nftables
sudo systemctl start nftables

# Setup daily update cron (2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/update-cloudflare-ips.sh >> /var/log/cloudflare-ip-update.log 2>&1") | crontab -
```

#### 4.3 Configure GitHub Container Registry Access

```bash
# Login to GitHub Container Registry (replace YOUR_GITHUB_PAT with your actual token)
echo "YOUR_GITHUB_PAT" | docker login ghcr.io -u jenicek001 --password-stdin

# Test pulling images
docker pull ghcr.io/jenicek001/familycart-backend:latest
docker pull ghcr.io/jenicek001/familycart-frontend:latest
```

#### 4.4 Create Application Environment

```bash
# Create deployment directory
sudo mkdir -p /opt/familycart-app
sudo chown ubuntu:ubuntu /opt/familycart-app
cd /opt/familycart-app

# Create .env file (use passwords from VM1)
cat > .env << 'EOF'
# Database Configuration (VM1 Private IP)
POSTGRES_SERVER=<VM1_PRIVATE_IP>
POSTGRES_PORT=5432
POSTGRES_DB=familycart_prod
POSTGRES_USER=familycart
POSTGRES_PASSWORD=<password-from-vm1>

# Redis Configuration (VM1 Private IP)
REDIS_HOST=<VM1_PRIVATE_IP>
REDIS_PORT=6379
REDIS_PASSWORD=<password-from-vm1>

# Backend Configuration
SECRET_KEY=<generate-with-openssl-rand-hex-32>
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ENVIRONMENT=production
DEBUG=false
ALLOWED_HOSTS=familycart.com,www.familycart.com

# Frontend Configuration
NEXT_PUBLIC_API_URL=https://familycart.com/api
NEXT_PUBLIC_WEBSOCKET_URL=wss://familycart.com/ws
NEXT_PUBLIC_ENVIRONMENT=production
EOF

# Generate SECRET_KEY
SECRET_KEY=$(openssl rand -hex 32)
sed -i "s|<generate-with-openssl-rand-hex-32>|$SECRET_KEY|" .env

# IMPORTANT: Edit this file and replace <VM1_PRIVATE_IP> and passwords from VM1
echo "IMPORTANT: Edit /opt/familycart-app/.env and replace placeholders with actual values from VM1"
nano .env

chmod 600 .env
```

#### 4.5 Create Docker Compose for Application

```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  backend:
    image: ghcr.io/jenicek001/familycart-backend:latest
    container_name: familycart-prod-backend
    restart: unless-stopped
    env_file: .env
    ports:
      - "8000:8000"
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.6'

  frontend:
    image: ghcr.io/jenicek001/familycart-frontend:latest
    container_name: familycart-prod-frontend
    restart: unless-stopped
    env_file: .env
    ports:
      - "3000:3000"
    depends_on:
      - backend
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.4'

networks:
  app-network:
    name: familycart-prod-app-network
EOF
```

#### 4.6 Configure Nginx Reverse Proxy

```bash
sudo tee /etc/nginx/sites-available/familycart << 'EOF'
upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:3000;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name familycart.com www.familycart.com;
    
    location / {
        return 301 https://$host$request_uri;
    }
}

# Main application
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name familycart.com www.familycart.com;
    
    # Cloudflare Origin Certificate (will be set up later)
    ssl_certificate /etc/ssl/cloudflare/familycart.pem;
    ssl_certificate_key /etc/ssl/cloudflare/familycart-key.pem;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # Logging
    access_log /var/log/nginx/familycart-access.log;
    error_log /var/log/nginx/familycart-error.log;
    
    # API endpoints
    location /api/ {
        proxy_pass http://backend/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # WebSocket
    location /ws {
        proxy_pass http://backend/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Health check
    location /health {
        proxy_pass http://backend/health;
    }
    
    # Frontend (everything else)
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
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/familycart /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Test config (will fail until SSL certs are in place)
sudo nginx -t
```

---

### Phase 5: Cloudflare Configuration

#### 5.1 Add Domain to Cloudflare

1. **Login to Cloudflare Dashboard:** https://dash.cloudflare.com/
2. **Add Site:**
   - Click "Add a Site"
   - Enter: `familycart.com`
   - Select Free plan
   - Click "Add site"

3. **Update Nameservers at your domain registrar:**
   - Copy the Cloudflare nameservers provided
   - Update at your domain registrar
   - Wait for DNS propagation (can take up to 24 hours)

#### 5.2 Configure DNS Records

Add the following DNS records in Cloudflare:

```
Type    Name    Content              Proxy Status    TTL
A       @       <VM2_PUBLIC_IP>      Proxied         Auto
A       www     <VM2_PUBLIC_IP>      Proxied         Auto
```

#### 5.3 Configure SSL/TLS

1. **Navigate to:** SSL/TLS → Overview
2. **Set encryption mode:** Full (strict)
3. **Generate Origin Certificate:**
   - Go to: SSL/TLS → Origin Server
   - Click "Create Certificate"
   - Leave default options (RSA 2048, 15 years)
   - Click "Create"
   - **IMPORTANT:** Save both the certificate and private key

4. **Install Origin Certificate on VM2:**
```bash
# On VM2
sudo mkdir -p /etc/ssl/cloudflare

# Paste certificate
sudo nano /etc/ssl/cloudflare/familycart.pem
# (paste certificate, save and exit)

# Paste private key
sudo nano /etc/ssl/cloudflare/familycart-key.pem
# (paste private key, save and exit)

sudo chmod 600 /etc/ssl/cloudflare/familycart-key.pem

# Test nginx config
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

#### 5.4 Configure Cloudflare Security

**SSL/TLS Settings:**
- SSL/TLS → Edge Certificates
  - ✅ Always Use HTTPS: ON
  - ✅ HTTP Strict Transport Security (HSTS): Enable (max-age=31536000)
  - ✅ Minimum TLS Version: TLS 1.2
  - ✅ Automatic HTTPS Rewrites: ON

**Security Settings:**
- Security → Settings
  - Security Level: Medium
  - Challenge Passage: 30 minutes
  - Browser Integrity Check: ON
  - Privacy Pass Support: ON

**Firewall Rules (optional but recommended):**
```
# Block common attack patterns
(http.request.uri.path contains "wp-admin" or http.request.uri.path contains "phpmyadmin") - Block

# Rate limit API endpoints
(http.request.uri.path contains "/api/" and not http.request.uri.path contains "/api/v1/health") - Rate Limit: 100 requests per minute
```

**Page Rules:**
- Create rule for `familycart.com/api/*`
  - Cache Level: Bypass
  - Security Level: High

---

### Phase 6: Deploy Application

#### 6.1 Start Application on VM2

```bash
# SSH into VM2
ssh ubuntu@$VM2_PUBLIC_IP

cd /opt/familycart-app

# Pull latest images
docker-compose pull

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

#### 6.2 Initialize Database

```bash
# Run database migrations on VM2
docker exec familycart-prod-backend alembic upgrade head

# Create initial admin user (optional)
docker exec -it familycart-prod-backend python -c "
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

db = SessionLocal()
admin = User(
    email='admin@familycart.com',
    hashed_password=get_password_hash('changeme123'),
    full_name='Admin User',
    is_active=True,
    is_superuser=True
)
db.add(admin)
db.commit()
print('Admin user created')
"
```

#### 6.3 Test Application

```bash
# Test locally on VM2
curl http://localhost:8000/health
curl http://localhost:3000

# Test through nginx
curl http://localhost/health

# Test through Cloudflare (from any computer)
curl https://familycart.com/health
```

---

### Phase 7: Configure CI/CD (GitHub Actions)

#### 7.1 Add Production Secrets to GitHub

Navigate to your GitHub repository: Settings → Secrets and variables → Actions

Add the following secrets:

```
PRODUCTION_HOST=<VM2_PUBLIC_IP>
PRODUCTION_USER=ubuntu
PRODUCTION_SSH_KEY=<contents-of-your-private-key>
```

#### 7.2 Update CI/CD Workflow

Edit `.github/workflows/ci.yml` to add production deployment job (if not already present):

```yaml
deploy-production:
  runs-on: self-hosted
  needs: [build, deploy-uat]
  if: github.ref == 'refs/heads/main'
  environment: production  # ← This triggers manual approval in GitHub
  steps:
    - name: Deploy to Production
      env:
        PRODUCTION_SSH_KEY: ${{ secrets.PRODUCTION_SSH_KEY }}
        PRODUCTION_HOST: ${{ secrets.PRODUCTION_HOST }}
        PRODUCTION_USER: ${{ secrets.PRODUCTION_USER }}
      run: |
        # Setup SSH
        mkdir -p ~/.ssh
        echo "$PRODUCTION_SSH_KEY" > ~/.ssh/production_key
        chmod 600 ~/.ssh/production_key
        
        # Deploy
        ssh -i ~/.ssh/production_key -o StrictHostKeyChecking=no $PRODUCTION_USER@$PRODUCTION_HOST << 'ENDSSH'
          cd /opt/familycart-app
          docker-compose pull
          docker-compose up -d
          docker-compose logs --tail=20
        ENDSSH
```

#### 7.3 Configure GitHub Environment Protection

1. **Navigate to:** Repository → Settings → Environments
2. **Click:** "New environment"
3. **Name:** `production`
4. **Configure protection rules:**
   - ✅ Required reviewers: Add yourself
   - ✅ Wait timer: 0 minutes
   - ✅ Deployment branches: Only `main`
5. **Click:** "Save protection rules"

---

### Phase 8: Test Complete Deployment Flow

#### 8.1 Push to Main Branch

```bash
# On your local machine
cd /home/honzik/GitHub/FamilyCart/FamilyCart

# Checkout main
git checkout main
git pull origin main

# Make a small change
echo "Production deployment tested $(date)" >> README.md

# Commit and push
git add README.md
git commit -m "test: Verify production deployment pipeline"
git push origin main
```

#### 8.2 Monitor CI/CD Pipeline

1. **Go to:** GitHub → Actions → Select the workflow run
2. **Watch stages:**
   - ✅ Run all tests
   - ✅ Build Docker images
   - ✅ Push to ghcr.io
   - ✅ Deploy to UAT
   - ⏸️ **Wait for manual approval**
3. **Approve Production Deployment:**
   - Click "Review deployments"
   - Check "production"
   - Click "Approve and deploy"
4. **Monitor deployment:**
   - Watch logs in GitHub Actions
   - Check application: https://familycart.com

---

## 📊 Monitoring and Maintenance

### Daily Operations

**Monitor Application Health:**
```bash
# Check VM2 application status
ssh ubuntu@$VM2_PUBLIC_IP "cd /opt/familycart-app && docker-compose ps"

# Check logs
ssh ubuntu@$VM2_PUBLIC_IP "cd /opt/familycart-app && docker-compose logs --tail=50"

# Check Cloudflare analytics
# Visit: https://dash.cloudflare.com → Analytics
```

**Monitor Database (VM1):**
```bash
ssh ubuntu@$VM1_PUBLIC_IP "cd /opt/familycart-db && docker-compose ps"
```

### Weekly Maintenance

```bash
# Update system packages
ssh ubuntu@$VM2_PUBLIC_IP "sudo apt update && sudo apt upgrade -y"
ssh ubuntu@$VM1_PUBLIC_IP "sudo apt update && sudo apt upgrade -y"

# Check disk usage
ssh ubuntu@$VM2_PUBLIC_IP "df -h"
ssh ubuntu@$VM1_PUBLIC_IP "df -h"

# Clean old Docker images
ssh ubuntu@$VM2_PUBLIC_IP "docker system prune -af --volumes"
```

### Backup Verification

```bash
# List backups
ssh ubuntu@$VM1_PUBLIC_IP "ls -lh /opt/familycart-db/backups/"

# Download backup (optional)
scp ubuntu@$VM1_PUBLIC_IP:/opt/familycart-db/backups/familycart_backup_*.sql.gz ./
```

---

## 🔧 Troubleshooting

### Application not accessible

1. **Check Cloudflare:** Verify DNS records are proxied and pointing to correct IP
2. **Check nginx:** `sudo systemctl status nginx`
3. **Check containers:** `docker-compose ps`
4. **Check firewall:** `sudo nft list ruleset`
5. **Check logs:** `docker-compose logs`, `/var/log/nginx/familycart-error.log`

### Database connection issues

1. **Verify VM1 private IP** in VM2's `.env`
2. **Test connectivity:** `telnet $VM1_PRIVATE_IP 5432`
3. **Check PostgreSQL logs:** `docker logs familycart-prod-postgres`
4. **Verify security list rules** in OCI console

### Deployment failures

1. **Check GitHub Actions logs**
2. **Verify secrets** are configured correctly
3. **SSH manually** and check disk space: `df -h`
4. **Check Docker login:** `docker pull ghcr.io/jenicek001/familycart-backend:latest`

---

## 🎯 Next Steps

After successful deployment:

- [ ] Restrict SSH access to specific IPs in nftables
- [ ] Configure monitoring (Prometheus + Grafana)
- [ ] Set up log aggregation (Loki, ELK)
- [ ] Configure automated security updates
- [ ] Set up uptime monitoring (UptimeRobot, Better Uptime)
- [ ] Configure email notifications (SendGrid, AWS SES)
- [ ] Add database replication (if needed)
- [ ] Set up Cloudflare Access for admin panel
- [ ] Configure CDN caching rules
- [ ] Set up automated penetration testing

---

## 📚 References

- [OCI Free Tier Documentation](https://docs.oracle.com/iaas/Content/FreeTier/freetier.htm)
- [OCI CLI Command Reference](https://docs.oracle.com/iaas/tools/oci-cli/latest/oci_cli_docs/)
- [Cloudflare Docs](https://developers.cloudflare.com/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

**Document Version:** 1.0  
**Last Updated:** November 3, 2025  
**Maintained by:** FamilyCart DevOps Team