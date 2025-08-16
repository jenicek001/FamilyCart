## FamilyCart Deployment on Oracle Cloud Free Tier (2 Micro VMs) with Cloudflare

This document summarizes the recommended approach to deploy the current FamilyCart stack (PostgreSQL, Redis, Backend / FastAPI, Frontend / Next.js) on Oracle Cloud Infrastructure (OCI) Always Free Tier using only two Ubuntu 24.04 micro VMs, fronted by Cloudflare (DNS + CDN + security). It emphasizes low memory footprint, security (Cloudflare IP allowlist), automation, and easy rollback while preserving your existing local development & testing workflow.

---
## 1. Goals & Constraints
| Goal | Detail |
|------|--------|
| Cost | 100% Free Tier (2× VM.Standard.E2.1.Micro: 1 vCPU / 1 GB RAM each) |
| Availability | Acceptable for small private beta; single region OK |
| Simplicity | Minimal moving parts; build in CI, run images on VMs |
| Security | Only Cloudflare can reach app ports; SSH locked to your IP |
| Automation | GitHub Actions builds + deploy via SSH (pull images & restart) |
| Data Safety | Daily PostgreSQL dumps w/ rotation |
| Local Dev | Existing docker-compose + local tests unchanged |

### Services
1. PostgreSQL 15 (stateful)
2. Redis 8 (cache / ephemeral or optional persistence)
3. Backend (FastAPI + Uvicorn)
4. Frontend (Next.js production build) – optionally convert to static export later.

---
## 2. Recommended Architecture (Option B)
Split stateful and stateless workloads:

| VM | Role | Services | Notes |
|----|------|----------|-------|
| VM1 | Stateful | PostgreSQL, Redis | Private data; no public HTTP exposure |
| VM2 | App Layer | Backend API, Frontend (and optional reverse proxy) | Only VM needing public HTTP/HTTPS |

Both VMs share a private subnet (low-latency internal traffic). Cloudflare proxies all external traffic to VM2. VM1 has only SSH (optionally restricted further) open publicly—or can have zero public ingress if you administer through a bastion / Cloudflare Tunnel later.

### Why This Split?
* Keeps memory pressure manageable (DB buffers separate from Python/Node processes)
* Simplifies backups (only VM1) and rolling deployments (only VM2 restarts often)
* Avoids single point of resource contention

---
## 3. Future Evolutions (Optional)
| Phase | Enhancement | Benefit |
|-------|------------|---------|
| Phase 2 | Cloudflare Tunnel (zero exposed origin ports) | Eliminates IP allowlist maintenance |
| Phase 2 | Static export of frontend (Next.js `next export`) served by nginx | Lower runtime RAM |
| Phase 3 | Add reverse proxy (Caddy / nginx) for gzip, Brotli, TLS origin cert | Performance & security |
| Phase 3 | Redis AOF or persistence only if needed for sessions | Durability |

---
## 4. Networking & DNS
Cloudflare (zone: `familycart.app`):
* `app.familycart.app` → Frontend (proxied) – or same host as API if SPA consumes `/api`.
* `api.familycart.app` → Backend (proxied) – can initially point to same IP as frontend and rely on path-based routing or separate ports reversed by nginx.

Internal service hostname usage (environment variables on VM2):
```
POSTGRES_SERVER=<VM1 private IP>
REDIS_HOST=<VM1 private IP>
```

---
## 5. Security & Firewall Strategy
1. Allow only Cloudflare IP ranges to reach ports 80/443 on VM2.
2. Deny all other inbound traffic (except SSH from your static IP/ trusted range).
3. VM1: Inbound only SSH (or none if you adopt a bastion). Postgres & Redis bind to private subnet IP.
4. Long term: Introduce Cloudflare Tunnel to remove need for maintaining IP list.

### Cloudflare IP Allowlist Automation (Concept)
Daily job:
1. Fetch `https://api.cloudflare.com/client/v4/ips`
2. Populate nftables sets (`cf_ipv4`, `cf_ipv6`)
3. Reload nftables atomically.

Pseudo-script outline:
```bash
#!/usr/bin/env bash
set -euo pipefail
TMP=$(mktemp)
curl -s https://api.cloudflare.com/client/v4/ips > "$TMP"
IPV4=$(jq -r '.result.ipv4_cidrs[]' "$TMP" | paste -sd "," -)
IPV6=$(jq -r '.result.ipv6_cidrs[]' "$TMP" | paste -sd "," -)
cat > /etc/nftables.d/cloudflare.nft <<EOF
define cf_ipv4 = { $IPV4 }
define cf_ipv6 = { $IPV6 }
EOF
nft -f /etc/nftables.conf
```

Nftables rule snippet:
```nft
table inet filter {
  set cf_ipv4 { type ipv4_addr; flags interval; }
  set cf_ipv6 { type ipv6_addr; flags interval; }
  chain input {
    type filter hook input priority 0;
    iif lo accept
    ct state { established, related } accept
    tcp dport { 80,443 } ip saddr @cf_ipv4 accept
    tcp dport { 80,443 } ip6 saddr @cf_ipv6 accept
    tcp dport 22 ip saddr { <YOUR_IP> } accept
    reject with icmpx type admin-prohibited
  }
}
```

---
## 6. Docker / Compose Layout

### VM1 (`docker-compose.stateful.yml`)
```yaml
version: "3.9"
services:
  postgres:
    image: postgres:15-alpine
    env_file: .env
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
  redis:
    image: redis:8.0-alpine
    command: ["redis-server","--requirepass","$$REDIS_PASSWORD","--appendonly","no"]
    env_file: .env
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD","redis-cli","-a","$$REDIS_PASSWORD","ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
volumes:
  postgres_data:
  redis_data:
```

### VM2 (`docker-compose.app.yml`)
```yaml
version: "3.9"
services:
  backend:
    image: ghcr.io/<yourorg>/familycart-backend:latest
    env_file: .env
    environment:
      POSTGRES_SERVER: 10.x.x.x
      REDIS_HOST: 10.x.x.x
    depends_on: []
    restart: unless-stopped
  frontend:
    image: ghcr.io/<yourorg>/familycart-frontend:latest
    env_file: .env
    depends_on:
      - backend
    restart: unless-stopped
```

Later you may add an nginx / Caddy service to reverse proxy and serve static assets.

---
## 7. Environment Variables (Deployment Subset)
| Variable | Purpose | Location |
|----------|---------|----------|
| POSTGRES_USER / PASSWORD / DB | DB auth | VM1 `.env` |
| POSTGRES_SERVER | Backend DB host | VM2 `.env` |
| POSTGRES_PORT | Usually 5432 | Both |
| REDIS_PASSWORD | Redis auth | Both (VM1 defines, VM2 consumes) |
| REDIS_HOST | Redis hostname | VM2 |
| SECRET_KEY | JWT signing | Backend only |
| ACCESS_TOKEN_EXPIRE_MINUTES | Auth TTL | Backend |

Store `.env` with permissions `600` (root-owned) and load via compose `env_file`.

---
## 8. CI/CD (GitHub Actions Outline)

Workflow stages:
1. Test: Run backend pytest + frontend build.
2. Build: Build backend & frontend images, tag with `git sha` + `latest`, push to GHCR.
3. Deploy: SSH to VM2 (and VM1 if stateful images changed) → `docker compose pull && docker compose up -d --remove-orphans`.

Minimal conceptual job (pseudocode):
```yaml
jobs:
  test:
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install poetry && poetry install --no-root
      - run: poetry run pytest -q
      - uses: actions/setup-node@v4
      - run: npm ci --prefix frontend && npm run build --prefix frontend
  build:
    needs: test
    steps:
      - uses: actions/checkout@v4
      - name: Login GHCR
        run: echo "${{ secrets.GHCR_PAT }}" | docker login ghcr.io -u USERNAME --password-stdin
      - run: docker build -t ghcr.io/ORG/familycart-backend:latest backend
      - run: docker build -t ghcr.io/ORG/familycart-frontend:latest frontend
      - run: docker push ghcr.io/ORG/familycart-backend:latest
      - run: docker push ghcr.io/ORG/familycart-frontend:latest
  deploy:
    needs: build
    steps:
      - name: Deploy VM2
        run: |
          ssh -o StrictHostKeyChecking=no $VM2_USER@$VM2_IP \
            'cd /opt/familycart && docker compose -f docker-compose.app.yml pull && docker compose -f docker-compose.app.yml up -d --remove-orphans'
```

Add SHA tagging for rollback: tag & push `ghcr.io/ORG/familycart-backend:<GIT_SHA>`.

### Rollback
SSH to VM2 and:
```bash
docker compose -f docker-compose.app.yml pull backend:sha123 frontend:sha123
docker compose -f docker-compose.app.yml up -d
```

---
## 9. Backups
Nightly cron on VM1:
```bash
pg_dump -Fc -U $POSTGRES_USER $POSTGRES_DB > /var/backups/familycart_$(date +%F).dump
find /var/backups -name 'familycart_*.dump' -mtime +14 -delete
```
Optional: rclone to encrypted remote storage.

Restore test:
```bash
pg_restore -l backup.dump | head
pg_restore -c -d $POSTGRES_DB -U $POSTGRES_USER backup.dump
```

---
## 10. Resource Tuning (Initial)
| Component | Setting | Rationale |
|-----------|---------|-----------|
| Postgres | shared_buffers=64MB | Low memory footprint |
| Postgres | max_connections=40 | Limit per micro VM |
| Redis | appendonly no | Skip persistence if cache only |
| Backend | 1 Uvicorn worker | Avoid duplication of memory |
| Frontend | Static build optional | Reduce Node runtime RAM |

Create a small swap file (1–2 GB) to mitigate OOM (understand performance tradeoffs):
```bash
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
sudo swapon -a
```

---
## 11. Monitoring & Observability (Minimal Start)
| Aspect | Approach |
|--------|----------|
| Uptime | Cloudflare health checks (optional) |
| Logs | `docker logs --since 1h` + manual review |
| Metrics | Defer heavy tooling; add later if needed |
| Alerts | Email via simple cron grep (e.g., error frequency) |

Later: Lightweight Prometheus + Grafana or hosted solution if constraints ease.

---
## 12. Local Development Continuity
Nothing changes: existing `docker-compose.yml` runs all services locally including Ollama. Deployment environment omits Ollama unless explicitly needed (resource savings). Keep tests & scripts identical; just ensure env overrides for production (.env differs).

---
## 13. Hardening Checklist
| Item | Status (Initial) |
|------|------------------|
| SSH key-only auth | Configure immediately |
| Disable root SSH | Yes (PermitRootLogin no) |
| Firewall default deny | Yes |
| Cloudflare IP allowlist | Implement script |
| Secrets not in git | Use `.env` only on servers |
| Regular PostgreSQL backups | Cron daily |
| Package updates | Unattended upgrades enabled |

---
## 14. Quick Deployment Bootstrap (Manual First Run)
On both VMs:
```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin jq nftables
sudo usermod -aG docker $USER
newgrp docker
```

VM1:
```bash
mkdir -p /opt/familycart && cd /opt/familycart
curl -O https://raw.githubusercontent.com/<yourrepo>/main/deploy/docker-compose.stateful.yml
cp /home/ubuntu/.env .env   # create with DB + Redis vars
docker compose -f docker-compose.stateful.yml up -d
```

VM2:
```bash
mkdir -p /opt/familycart && cd /opt/familycart
curl -O https://raw.githubusercontent.com/<yourrepo>/main/deploy/docker-compose.app.yml
cp /home/ubuntu/.env .env   # create with backend/front env + DB host
docker compose -f docker-compose.app.yml up -d
```

After CI builds images, switch to pulling from GHCR instead of local builds.

---
## 15. Future Improvements (Backlog)
* Cloudflare Tunnel (remove IP allowlist maintenance)
* Static frontend export + object storage or Cloudflare Pages
* sops-encrypted secrets repo integration
* Blue/green deployment for backend (optional)
* Add lightweight metrics (cAdvisor + Prometheus) if performance troubleshooting needed
* Automated load test (k6 / Locust) in CI nightly

---
## 16. Summary
Deploy with a stateful vs stateless split across two micro VMs; lock down ingress to Cloudflare; build & push images in GitHub Actions; pull and restart containers via automated SSH job; keep DB backups rotating; plan for Cloudflare Tunnel and static asset optimization later. This minimizes operational risk and memory pressure while staying inside Always Free limitations.

---
Document Version: 2025-08-14
Author: Deployment Automation (Generated Summary)
