# VM Database Connectivity Fix

## ✅ Problem Resolved

**Issue**: VM2 (Application Server) could not connect to VM1 (Database Server) databases despite correct OCI Security Lists and firewall rules.

## Root Cause

Docker's NAT PREROUTING rules were DNATing ALL incoming traffic on ports 5432/6379 to internal container IPs (172.18.0.x). Docker's raw table then **blocked** this traffic because it didn't arrive on the Docker bridge interface:

```bash
# NAT table - was DNATing external traffic
-A DOCKER ! -i br-9938e1b7f269 -p tcp -m tcp --dport 5432 -j DNAT --to-destination 172.18.0.2:5432
-A DOCKER ! -i br-9938e1b7f269 -p tcp -m tcp --dport 6379 -j DNAT --to-destination 172.18.0.3:6379

# Raw table - was dropping the DNATed packets
-A PREROUTING -d 172.18.0.2/32 ! -i br-9938e1b7f269 -j DROP
-A PREROUTING -d 172.18.0.3/32 ! -i br-9938e1b7f269 -j DROP
```

## Solution Applied on VM1

Added iptables NAT RETURN rule to bypass Docker DNAT for VCN traffic:

```bash
# Add RETURN rule BEFORE Docker DNAT rules
sudo iptables -t nat -I DOCKER 1 -i ens3 -s 10.0.0.0/16 -j RETURN

# Verify rule is first in chain
sudo iptables -t nat -L DOCKER -n -v

# Save rules permanently
sudo netfilter-persistent save
```

## Verification

Both databases now accessible from VM2:

```bash
# PostgreSQL - SUCCESS ✅
cd /opt/familycart-app
PGPASSWORD=$(grep "^POSTGRES_PASSWORD=" .env.app | cut -d= -f2-) \
  psql -h 10.0.1.191 -U familycart -d familycart_production -c "SELECT version();"

# Output:
# PostgreSQL 15.14 on x86_64-pc-linux-musl, compiled by gcc (Alpine 14.2.0) 14.2.0, 64-bit

# Redis - SUCCESS ✅
REDIS_PASSWORD=$(grep "^REDIS_PASSWORD=" .env.app | cut -d= -f2-) \
  redis-cli -h 10.0.1.191 -p 6379 -a "$REDIS_PASSWORD" ping

# Output: PONG
```

## Network Connectivity Status

- ✅ ICMP (ping) works between VMs
- ✅ SSH (port 22) accessible
- ✅ PostgreSQL (port 5432) accessible from VCN
- ✅ Redis (port 6379) accessible from VCN
- ✅ VM1 can connect to itself via private IP (10.0.1.191)
- ✅ Firewall rules made persistent (survives reboot)
- ✅ nftables policy: DROP by default (secure)
- ✅ iptables rules: Saved with netfilter-persistent

## Technical Details

### Why This Worked

1. **Incoming packet flow** (before fix):
   - Packet arrives at VM1 on `ens3` interface
   - NAT PREROUTING → DOCKER chain → DNAT to 172.18.0.2
   - Raw PREROUTING → DROP (not from Docker bridge)
   - **Packet dropped**

2. **Incoming packet flow** (after fix):
   - Packet arrives at VM1 on `ens3` interface from 10.0.0.0/16
   - NAT PREROUTING → DOCKER chain → RETURN (bypass DNAT)
   - Packet continues to INPUT chain with original destination (10.0.1.191:5432)
   - nftables/iptables ACCEPT rules match → **Packet accepted**
   - Docker container listening on 0.0.0.0:5432 receives connection

### NAT Table Final Configuration

```bash
Chain DOCKER (2 references)
 pkts bytes target     prot opt in     out     source               destination
    0     0 RETURN     0    --  ens3   *       10.0.0.0/16          0.0.0.0/0
    0     0 RETURN     0    --  docker0 *       0.0.0.0/0            0.0.0.0/0
    0     0 RETURN     0    --  br-9938e1b7f269 *       0.0.0.0/0            0.0.0.0/0
   42  2520 DNAT       6    --  !br-9938e1b7f269 *       0.0.0.0/0            0.0.0.0/0            tcp dpt:5432 to:172.18.0.2:5432
    0     0 DNAT       6    --  !br-9938e1b7f269 *       0.0.0.0/0            0.0.0.0/0            tcp dpt:6379 to:172.18.0.3:6379
```

### Security Implications

- **VCN traffic (10.0.0.0/16)**: Direct access to published Docker ports (5432, 6379)
- **External traffic (Internet)**: Still blocked by OCI Security Lists (only VM1 private subnet allowed)
- **Docker isolation**: Maintained for other networks
- **Firewall policies**: 
  - nftables: policy DROP (default deny)
  - iptables: Explicit ACCEPT for VCN → PostgreSQL/Redis

## Lessons Learned

1. **Docker NAT complexity**: Docker creates multiple iptables/nftables chains (nat, raw, filter, mangle) that interact in complex ways
2. **Debugging order**: Check packet flow from raw → mangle → nat → filter tables
3. **nftables vs iptables**: Both coexist on Ubuntu 24.04; nftables has priority "filter" but iptables NAT runs first
4. **Packet counters**: Essential for identifying which rules are matching
5. **Log rules**: Mangle PREROUTING LOG rules helped confirm packets were arriving
6. **Connection tracking**: Initial suspicion of ct state rules was incorrect - NAT was the culprit

## Date Fixed
2025-11-06 12:50 UTC

## Fixed By
GitHub Copilot (AI Agent) + User (honzik)
