#!/bin/bash
# Script to verify UAT deployment setup
# Following project rules: scripts should be well-documented and maintainable

set -e

echo "==================================="
echo "UAT Deployment Setup Verification"
echo "==================================="
echo ""

# Check 1: UAT directory exists
echo "✓ Checking UAT directory..."
if [ -d "/opt/familycart-uat" ]; then
    echo "  ✅ /opt/familycart-uat exists"
    ls -la /opt/familycart-uat/
else
    echo "  ❌ /opt/familycart-uat does not exist"
    echo "  Creating directory..."
    sudo mkdir -p /opt/familycart-uat
    sudo chown $(whoami):$(whoami) /opt/familycart-uat
    echo "  ✅ Directory created"
fi

echo ""

# Check 2: docker-compose.uat.yml exists
echo "✓ Checking UAT docker-compose file..."
if [ -f "/opt/familycart-uat/docker-compose.uat.yml" ]; then
    echo "  ✅ docker-compose.uat.yml exists"
else
    echo "  ❌ docker-compose.uat.yml missing"
    echo "  Copying from repository..."
    cp docker-compose.uat.yml /opt/familycart-uat/
    echo "  ✅ File copied"
fi

echo ""

# Check 3: Self-hosted runners are active
echo "✓ Checking GitHub self-hosted runners..."
RUNNER_COUNT=$(docker ps --filter "name=familycart-runner" --format "{{.Names}}" | wc -l)
if [ "$RUNNER_COUNT" -gt 0 ]; then
    echo "  ✅ Found $RUNNER_COUNT active runner(s):"
    docker ps --filter "name=familycart-runner" --format "  - {{.Names}} ({{.Status}})"
else
    echo "  ❌ No active runners found"
    echo "  Start runners with: docker compose -f docker-compose.runners.yml up -d"
fi

echo ""

# Check 4: CI infrastructure
echo "✓ Checking CI infrastructure..."
if docker ps --filter "name=postgres-ci-familycart" --format "{{.Names}}" | grep -q postgres; then
    echo "  ✅ PostgreSQL CI database running"
else
    echo "  ⚠️  PostgreSQL CI database not running"
fi

if docker ps --filter "name=redis-ci-familycart" --format "{{.Names}}" | grep -q redis; then
    echo "  ✅ Redis CI cache running"
else
    echo "  ⚠️  Redis CI cache not running"
fi

echo ""

# Check 5: GitHub Environment (requires gh CLI)
echo "✓ Checking GitHub Environment configuration..."
if command -v gh &> /dev/null; then
    # Note: gh CLI doesn't have direct command to list environments
    # User needs to check manually
    echo "  ℹ️  Please verify GitHub Environment manually:"
    echo "  https://github.com/jenicek001/FamilyCart/settings/environments"
    echo "  - Ensure 'uat' environment exists"
    echo "  - No secrets required for local UAT deployment"
else
    echo "  ⚠️  GitHub CLI not available"
fi

echo ""

# Check 6: Current branch and recent CI/CD status
echo "✓ Checking current branch and CI/CD status..."
CURRENT_BRANCH=$(git branch --show-current)
echo "  Current branch: $CURRENT_BRANCH"

if command -v gh &> /dev/null; then
    echo "  Recent CI/CD runs:"
    gh run list --workflow=ci.yml --limit=3 --json conclusion,status,displayTitle,createdAt | \
        jq -r '.[] | "  - [\(.conclusion)] \(.displayTitle) (\(.createdAt))"'
else
    echo "  ⚠️  Cannot check recent runs (gh CLI not available)"
fi

echo ""
echo "==================================="
echo "Verification Complete"
echo "==================================="
echo ""
echo "Next Steps:"
echo "1. Verify GitHub Environment 'uat' exists at:"
echo "   https://github.com/jenicek001/FamilyCart/settings/environments"
echo ""
echo "2. Commit the updated ci.yml workflow:"
echo "   git add .github/workflows/ci.yml"
echo "   git commit -m 'fix: Enable UAT deployment from both develop and main branches'"
echo "   git push origin main"
echo ""
echo "3. Watch the deployment:"
echo "   https://github.com/jenicek001/FamilyCart/actions"
echo ""
echo "4. After deployment, verify UAT is running:"
echo "   curl http://localhost:8001/health"
echo "   curl http://localhost:3001/"
