# Production Infrastructure Summary

## VM1 - Database Server (familycart-db-vm1)

### Connection Information
- **Public IP:** 141.147.22.49
- **Private IP:** 10.0.1.191
- **SSH Command:** `ssh -i ~/.ssh/familycart_oci ubuntu@141.147.22.49`

### Status
✅ **FULLY CONFIGURED AND OPERATIONAL**

### Services Running
- **PostgreSQL 15.14** - Port 5432
  - Database: `familycart_production`
  - User: `familycart`
  - Status: Healthy
  
- **Redis 8.2.3** - Port 6379
  - Max Memory: 512MB (LRU eviction)
  - Persistence: AOF + RDB snapshots
  - Status: Healthy

### Security Configuration
- **Firewall (nftables):** Active
  - SSH (22): Open from anywhere
  - PostgreSQL (5432): Restricted to VCN (10.0.0.0/16) only
  - Redis (6379): Restricted to VCN (10.0.0.0/16) only
  - ICMP (ping): Allowed

### Backup Configuration
- **Automated Backups:** Daily at 2:00 AM UTC
- **Retention Period:** 7 days
- **Backup Location:** `/opt/familycart-db/backups/`
- **Backup Script:** `/usr/local/bin/backup-familycart-db.sh`
- **Test Backup:** ✅ Successfully created (20251106_101337)

### Database Credentials
**⚠️ SAVE THESE SECURELY - REQUIRED FOR VM2 CONFIGURATION:**

```bash
# PostgreSQL
POSTGRES_SERVER=10.0.1.191
POSTGRES_PORT=5432
POSTGRES_USER=familycart
POSTGRES_PASSWORD=wzdtvkea6iSW4scp0q012Gk5dhiZE7/w4NLpn8ZF1Lw=
POSTGRES_DB=familycart_production

# Redis
REDIS_URI=redis://:9bfKCrde+c7J6HpOq9jRDOYrCfOqpLBfWSHzAeYNVoE=@10.0.1.191:6379
```

### Useful Commands
```bash
# SSH into VM1
ssh -i ~/.ssh/familycart_oci ubuntu@141.147.22.49

# Check service status
cd /opt/familycart-db && sudo docker compose --env-file .env.db ps

# View logs
cd /opt/familycart-db && sudo docker compose logs -f

# View credentials
cat /opt/familycart-db/.env.db

# Manual backup
sudo /usr/local/bin/backup-familycart-db.sh

# List backups
ls -lh /opt/familycart-db/backups/

# Restore from backup
gunzip < /opt/familycart-db/backups/familycart_backup_YYYYMMDD_HHMMSS.sql.gz | \
  sudo docker exec -i familycart-prod-db psql -U familycart -d familycart_production

# Test PostgreSQL connection
sudo docker exec familycart-prod-db psql -U familycart -d familycart_production -c "SELECT version();"

# Test Redis connection
sudo docker exec familycart-prod-redis redis-cli -a "9bfKCrde+c7J6HpOq9jRDOYrCfOqpLBfWSHzAeYNVoE=" ping

# Restart services
cd /opt/familycart-db && sudo docker compose --env-file .env.db restart

# Stop services
cd /opt/familycart-db && sudo docker compose down

# Start services
cd /opt/familycart-db && sudo docker compose --env-file .env.db up -d
```

---

## VM2 - Application Server (familycart-app-vm2)

### Connection Information
- **Public IP:** 158.180.30.112
- **Private IP:** 10.0.1.145
- **SSH Command:** `ssh -i ~/.ssh/familycart_oci ubuntu@158.180.30.112`

### Status
⏳ **READY FOR CONFIGURATION**

### Next Steps for VM2
1. SSH into VM2
2. Install Docker and docker-compose
3. Configure Cloudflare IP allowlist firewall (nftables)
4. Login to GitHub Container Registry
5. Create deployment directory `/opt/familycart-app`
6. Create docker-compose.yml for backend + frontend
7. Create .env file with database connections (using VM1 private IP)
8. Configure Nginx reverse proxy
9. Start application services

---

## Network Architecture

```
Internet
    |
    ↓
[Cloudflare CDN/WAF]
    |
    ↓
VM2 (158.180.30.112) - Application Server
  ├─ Nginx (80, 443)
  ├─ Backend FastAPI (8000)
  └─ Frontend Next.js (3000)
    |
    ↓ (Private Network: 10.0.0.0/16)
    |
VM1 (10.0.1.191) - Database Server
  ├─ PostgreSQL (5432) - Only accessible from VCN
  └─ Redis (6379) - Only accessible from VCN
```

---

## Security Summary

### VM1 (Database)
- ✅ Firewall configured (PostgreSQL/Redis restricted to VCN)
- ✅ Secure random passwords generated
- ✅ OCI Security Lists: PostgreSQL/Redis only from private subnet
- ✅ Automated backups with 7-day retention

### VM2 (Application) - To be configured
- ⏳ Cloudflare IP allowlist firewall
- ⏳ OCI Security Lists: HTTP/HTTPS open, SSH restricted
- ⏳ GitHub Container Registry authentication
- ⏳ Environment variables for database connection
- ⏳ Nginx reverse proxy with Cloudflare SSL

---

## Deployment Timeline

- **Nov 3, 2025 08:44 UTC** - VMs provisioned
- **Nov 6, 2025 10:00 UTC** - VM1 configuration started
- **Nov 6, 2025 10:13 UTC** - VM1 fully configured and tested ✅
- **Next:** Configure VM2 and Cloudflare

---

## Important Notes

1. **Database Credentials:** Stored securely on VM1 at `/opt/familycart-db/.env.db`
2. **SSH Keys:** Located at `~/.ssh/familycart_oci` (private) and `~/.ssh/familycart_oci.pub` (public)
3. **Database Access:** Only from VCN (10.0.0.0/16) - VM2 will connect using VM1's **private IP: 10.0.1.191**
4. **Backups:** Automated daily at 2 AM UTC, 7-day retention
5. **Firewall:** Both VMs protected by nftables + OCI Security Lists
6. **Docker:** Services managed via docker-compose for easy updates

---

## Ready for Next Phase

✅ **VM1 Database Server is production-ready**

Next steps:
1. Configure VM2 (Application Server)
2. Setup Cloudflare DNS and SSL
3. Deploy application containers
4. Configure GitHub Actions secrets
5. Test end-to-end deployment

---

*Configuration completed: November 6, 2025 10:13 UTC*
