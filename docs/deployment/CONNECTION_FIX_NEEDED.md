# ⚠️ CONNECTION ISSUE IDENTIFIED

## Problem
VM2 cannot connect to VM1's PostgreSQL/Redis databases over the private network.

## Root Cause Analysis

### 1. VM1 nftables firewall: ✅ CORRECT
```bash
ip saddr 10.0.0.0/16 tcp dport 5432 accept  # Allows VCN
ip saddr 10.0.0.0/16 tcp dport 6379 accept  # Allows VCN
```

### 2. Docker Port Binding: ✅ CORRECT
```
0.0.0.0:5432 -> PostgreSQL container
0.0.0.0:6379 -> Redis container
```

### 3. Likely Issue: OCI Security Lists ❌

The **OCI Security List for the Private Subnet** needs to allow ingress traffic from the public subnet.

## Solution: Update OCI Security Lists

### In OCI Web Console:

1. **Navigate to Security Lists:**
   - Go to: **Networking** → **Virtual Cloud Networks**
   - Click: **familycart-vcn**
   - Click: **Security Lists** (left sidebar)

2. **Update "Security List for Private Subnet":**
   
   **Current Rule (needs update):**
   - Source: `10.0.0.0/16` (VCN CIDR)
   - Destination Port: 5432, 6379
   
   **PROBLEM:** Both VMs are on the **Public Subnet** (10.0.1.0/24), NOT the private subnet!
   
3. **Check Current Subnet Configuration:**
   - VM1 (10.0.1.191) - Public Subnet ✅
   - VM2 (10.0.1.145) - Public Subnet ✅
   
4. **Update "Default Security List" (for Public Subnet):**
   
   **Add Ingress Rules:**
   
   a) PostgreSQL (VM1 from VM2):
   - **Source Type:** CIDR
   - **Source CIDR:** `10.0.1.0/24` (Public Subnet)
   - **IP Protocol:** TCP
   - **Source Port Range:** All
   - **Destination Port Range:** `5432`
   - **Description:** "PostgreSQL from VCN"
   
   b) Redis (VM1 from VM2):
   - **Source Type:** CIDR
   - **Source CIDR:** `10.0.1.0/24` (Public Subnet)
   - **IP Protocol:** TCP
   - **Source Port Range:** All
   - **Destination Port Range:** `6379`
   - **Description:** "Redis from VCN"

### Alternative: Simpler Approach

Since both VMs are on the public subnet and we're already using nftables for security:

**In "Default Security List" (Public Subnet), add:**

- **Source CIDR:** `10.0.0.0/16` (entire VCN)
- **IP Protocol:** TCP
- **Destination Port Range:** `5432,6379`
- **Description:** "Database access within VCN"

This allows any VM in the VCN to access PostgreSQL/Redis, but nftables on VM1 already restricts this.

---

## Steps to Fix (IN ORDER):

### 1. Update OCI Security List (IN OCI WEB CONSOLE):
   - Navigate to: Networking → VCNs → familycart-vcn → Security Lists
   - Click: **Default Security List for familycart-vcn**
   - Click: **Add Ingress Rules**
   - Add PostgreSQL rule (5432) from 10.0.0.0/16
   - Add Redis rule (6379) from 10.0.0.0/16
   - Click **Add Ingress Rules** button

### 2. Test Connection from VM2:
```bash
ssh -i ~/.ssh/familycart_oci ubuntu@158.180.30.112

# Test PostgreSQL
PGPASSWORD="wzdtvkea6iSW4scp0q012Gk5dhiZE7/w4NLpn8ZF1Lw=" \
  psql -h 10.0.1.191 -U familycart -d familycart_production -c "SELECT 1;"

# Test Redis
redis-cli -h 10.0.1.191 -p 6379 -a "9bfKCrde+c7J6HpOq9jRDOYrCfOqpLBfWSHzAeYNVoE=" ping
```

### 3. Deploy Application (after connectivity confirmed):
```bash
# On VM2
cd /opt/familycart-app

# Login to GitHub (using your PAT)
echo "YOUR_GITHUB_PAT" | docker login ghcr.io -u jenicek001 --password-stdin

# Pull images
docker compose pull

# Start services
docker compose up -d

# Check status
docker compose ps
```

---

## Next: Configure Cloudflare

After database connectivity is working and application is deployed, we'll:
1. Setup Cloudflare DNS (A records pointing to 158.180.30.112)
2. Generate Cloudflare Origin Certificate
3. Install certificate on VM2
4. Restart Nginx
5. Test end-to-end HTTPS access

---

**CURRENT STATUS:** Waiting for OCI Security List update to allow database traffic between VMs.
