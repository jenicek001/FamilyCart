# UAT Deployment Strategy for Modular Nginx

## 🏗️ Repository Structure Understanding

### Development Repository: `/home/honzik/GitHub/FamilyCart/FamilyCart`
- This is where we develop and test configurations
- Changes are committed to git branches
- Full development environment with all tools

### UAT Deployment: `/opt/familycart-uat-repo`  
- This is the actual UAT environment deployment
- Pulls configurations from git repository
- Limited to production-ready configurations
- UAT docker-compose.yml expects: `./nginx/uat.conf`

## 🚀 Deployment Workflow

### Phase 1: Development (Current Location)
```bash
# Working in: /home/honzik/GitHub/FamilyCart/FamilyCart

# 1. Develop modular nginx configuration
cd deploy/nginx/
# Create sites-available/, sites-enabled/, conf.d/ structure

# 2. Test configuration  
./nginx-site-manager.sh test

# 3. Create UAT-ready nginx structure
# The UAT deployment expects nginx configuration at ./nginx/uat.conf
# We need to either:
# a) Create a unified config from our modular structure, OR
# b) Modify UAT docker-compose to use modular structure
```

### Phase 2: UAT Preparation
```bash
# Option A: Create unified config for UAT compatibility
./create-uat-nginx-config.sh

# Option B: Update UAT docker-compose.yml to use modular structure
# Modify the volume mount from:
#   - ./nginx/uat.conf:/etc/nginx/nginx.conf:ro
# To:
#   - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
#   - ./nginx/sites-available:/etc/nginx/sites-available:ro
#   - ./nginx/sites-enabled:/etc/nginx/sites-enabled:ro
#   - ./nginx/conf.d:/etc/nginx/conf.d:ro
```

### Phase 3: Git Workflow
```bash
# Commit changes to feature branch
git add .
git commit -m "feat: implement modular nginx configuration for multi-service UAT"
git push origin feature/workflow-test-demo

# Create PR to main branch for review
```

### Phase 4: UAT Deployment
```bash
# Run on UAT server (as user with access to /opt/familycart-uat-repo)
cd /opt/familycart-uat-repo
git pull origin main  # After PR is merged

# Ensure nginx directory structure exists
# Either unified config or modular structure depending on chosen approach

# Deploy UAT environment
docker-compose -f docker-compose.uat.yml down
docker-compose -f docker-compose.uat.yml up -d
```

## 🔧 Two Approaches for UAT Integration

### Approach A: Unified Config (Backward Compatible)
- **Pros:** No changes to existing UAT docker-compose.yml
- **Cons:** Loses modular benefits in UAT
- **Implementation:** Generate single `nginx/uat.conf` from modular structure

### Approach B: Full Modular (Modern)  
- **Pros:** Full modular benefits in UAT, easier maintenance
- **Cons:** Requires updating UAT docker-compose.yml
- **Implementation:** Copy entire modular structure to UAT

## 🎯 Recommended Approach

**Use Approach B (Full Modular)** because:
1. **Transparency:** You can see exactly what each service does
2. **Maintainability:** Easy to enable/disable services in UAT
3. **Consistency:** Same structure in dev and UAT
4. **Future-proof:** Easy to add new services

## 📋 Next Steps

1. **Finish development** of modular structure in dev environment
2. **Test thoroughly** with development tools
3. **Choose integration approach** (A or B)
4. **Update UAT docker-compose.yml** if using Approach B
5. **Create deployment scripts** for UAT environment
6. **Commit and create PR**
7. **Deploy to UAT** after PR approval
