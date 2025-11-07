#!/bin/bash
set -e

echo "========================================"
echo "FamilyCart VM1 Database Server Setup"
echo "========================================"
echo ""

# Variables
VM1_PRIVATE_IP="10.0.1.191"
VCN_CIDR="10.0.0.0/16"

echo "📦 Step 1: Update system packages..."
sudo apt-get update
sudo apt-get upgrade -y

echo ""
echo "🐳 Step 2: Install Docker and Docker Compose..."
# Install prerequisites
sudo apt-get install -y ca-certificates curl gnupg lsb-release

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
echo "🔥 Step 3: Configure nftables firewall..."
# Install nftables (should be pre-installed on Ubuntu 24.04)
sudo apt-get install -y nftables

# Create nftables configuration
sudo tee /etc/nftables.conf > /dev/null << 'EOF'
#!/usr/sbin/nft -f

flush ruleset

table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;

        # Allow established/related connections
        ct state established,related accept

        # Allow loopback
        iif lo accept

        # Allow SSH from anywhere (for management)
        tcp dport 22 accept

        # Allow PostgreSQL ONLY from VCN (10.0.0.0/16)
        ip saddr 10.0.0.0/16 tcp dport 5432 accept

        # Allow Redis ONLY from VCN (10.0.0.0/16)
        ip saddr 10.0.0.0/16 tcp dport 6379 accept

        # Allow ICMP (ping)
        icmp type echo-request accept

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

# Enable and start nftables
sudo systemctl enable nftables
sudo systemctl restart nftables

echo "✅ Firewall configured - PostgreSQL/Redis restricted to VCN only"
sudo nft list ruleset

echo ""
echo "📁 Step 4: Create deployment directory..."
sudo mkdir -p /opt/familycart-db
sudo chown ubuntu:ubuntu /opt/familycart-db
cd /opt/familycart-db

echo ""
echo "🔐 Step 5: Generate secure passwords..."
POSTGRES_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)

echo "Generated secure passwords (save these securely!):"
echo "POSTGRES_PASSWORD: $POSTGRES_PASSWORD"
echo "REDIS_PASSWORD: $REDIS_PASSWORD"
echo ""
echo "💾 Saving to /opt/familycart-db/.env.db..."

# Create .env file
cat > /opt/familycart-db/.env.db << EOF
# Database Configuration
POSTGRES_USER=familycart
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=familycart_production

# Redis Configuration
REDIS_PASSWORD=$REDIS_PASSWORD

# Backup Configuration
BACKUP_RETENTION_DAYS=7
EOF

chmod 600 /opt/familycart-db/.env.db

echo ""
echo "🐳 Step 6: Create Docker Compose configuration..."
cat > /opt/familycart-db/docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: familycart-prod-db
    restart: unless-stopped
    env_file:
      - .env.db
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
    command: >
      postgres
      -c max_connections=100
      -c shared_buffers=128MB
      -c effective_cache_size=384MB
      -c maintenance_work_mem=64MB
      -c checkpoint_completion_target=0.9
      -c wal_buffers=4MB
      -c default_statistics_target=100
      -c random_page_cost=1.1
      -c effective_io_concurrency=200
      -c work_mem=1MB
      -c min_wal_size=1GB
      -c max_wal_size=4GB
      -c logging_collector=on
      -c log_directory=/var/lib/postgresql/data/log
      -c log_filename=postgresql-%Y-%m-%d.log
      -c log_rotation_age=1d
      -c log_rotation_size=100MB

  redis:
    image: redis:8-alpine
    container_name: familycart-prod-redis
    restart: unless-stopped
    command: >
      redis-server
      --requirepass ${REDIS_PASSWORD}
      --maxmemory 512mb
      --maxmemory-policy allkeys-lru
      --save 900 1
      --save 300 10
      --save 60 10000
      --appendonly yes
      --appendfsync everysec
    env_file:
      - .env.db
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
EOF

echo ""
echo "🚀 Step 7: Start database services..."
docker compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

docker compose ps

echo ""
echo "🧪 Step 8: Test database connectivity..."
# Source the environment variables
source /opt/familycart-db/.env.db

# Test PostgreSQL
echo "Testing PostgreSQL connection..."
docker exec familycart-prod-db psql -U familycart -d familycart_production -c "SELECT version();" || echo "❌ PostgreSQL test failed"

# Test Redis
echo "Testing Redis connection..."
docker exec familycart-prod-redis redis-cli -a "$REDIS_PASSWORD" ping || echo "❌ Redis test failed"

echo ""
echo "📦 Step 9: Setup automated backups..."
sudo mkdir -p /opt/familycart-db/backups

# Create backup script
sudo tee /usr/local/bin/backup-familycart-db.sh > /dev/null << 'BACKUPEOF'
#!/bin/bash
set -e

# Load environment variables
source /opt/familycart-db/.env.db

BACKUP_DIR="/opt/familycart-db/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/familycart_backup_$TIMESTAMP.sql.gz"

echo "Starting backup at $(date)"

# Create PostgreSQL backup
docker exec familycart-prod-db pg_dump -U familycart -d familycart_production | gzip > "$BACKUP_FILE"

echo "Backup completed: $BACKUP_FILE"

# Delete backups older than retention period
find "$BACKUP_DIR" -name "familycart_backup_*.sql.gz" -mtime +${BACKUP_RETENTION_DAYS:-7} -delete

echo "Old backups cleaned up"
BACKUPEOF

sudo chmod +x /usr/local/bin/backup-familycart-db.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null | grep -v backup-familycart-db.sh; echo "0 2 * * * /usr/local/bin/backup-familycart-db.sh >> /var/log/familycart-backup.log 2>&1") | crontab -

echo "✅ Daily backups configured (2 AM)"

echo ""
echo "========================================"
echo "✅ VM1 Database Server Setup Complete!"
echo "========================================"
echo ""
echo "📊 Summary:"
echo "  - PostgreSQL 15: Running on port 5432"
echo "  - Redis 8: Running on port 6379"
echo "  - Firewall: Configured (PostgreSQL/Redis restricted to VCN)"
echo "  - Backups: Daily at 2 AM, 7 days retention"
echo ""
echo "🔐 IMPORTANT: Save these credentials securely!"
echo "  Database credentials saved in: /opt/familycart-db/.env.db"
echo ""
echo "📝 Next steps:"
echo "  1. Copy the credentials from /opt/familycart-db/.env.db"
echo "  2. Configure VM2 (Application Server)"
echo "  3. Use VM1 private IP (10.0.1.191) for database connections from VM2"
echo ""
echo "🔍 Useful commands:"
echo "  - Check services: cd /opt/familycart-db && docker compose ps"
echo "  - View logs: docker compose logs -f"
echo "  - View credentials: cat /opt/familycart-db/.env.db"
echo "  - Manual backup: /usr/local/bin/backup-familycart-db.sh"
echo ""
