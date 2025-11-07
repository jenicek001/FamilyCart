#!/bin/bash

# GitHub Token Update Script for FamilyCart
echo "🔐 GitHub Token Update Script"
echo "============================="

# Check if token provided
if [ -z "$1" ]; then
    echo "❌ Error: Please provide your GitHub token"
    echo "Usage: ./update-github-token.sh 'ghp_your_token_here'"
    exit 1
fi

NEW_TOKEN="$1"
echo "✅ Token received (${NEW_TOKEN:0:10}...)"

# Validate token format
if [[ ! "$NEW_TOKEN" =~ ^ghp_ ]]; then
    echo "❌ Error: Token should start with 'ghp_'"
    exit 1
fi

echo
echo "🔧 Updating environment variables..."

# Export for current session
export GITHUB_TOKEN="$NEW_TOKEN"
export CR_PAT="$NEW_TOKEN"

echo "✅ Current session updated"

# Add to bashrc for persistence
echo
echo "📝 Making changes permanent..."

# Backup existing bashrc
cp ~/.bashrc ~/.bashrc.backup.$(date +%Y%m%d_%H%M%S)

# Remove old GITHUB_TOKEN entries
sed -i '/^export GITHUB_TOKEN=/d' ~/.bashrc
sed -i '/^export CR_PAT=/d' ~/.bashrc

# Add new token
echo "export GITHUB_TOKEN=\"$NEW_TOKEN\"" >> ~/.bashrc
echo "export CR_PAT=\"\$GITHUB_TOKEN\"" >> ~/.bashrc

echo "✅ Token added to ~/.bashrc"

echo
echo "🧪 Testing token validity..."

# Test GitHub API access
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: token $GITHUB_TOKEN" \
    https://api.github.com/user)

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ GitHub API access: SUCCESS"
    
    # Get user info
    USER_INFO=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user)
    USERNAME=$(echo "$USER_INFO" | grep -o '"login":"[^"]*' | cut -d'"' -f4)
    echo "✅ Authenticated as: $USERNAME"
else
    echo "❌ GitHub API access: FAILED (HTTP $HTTP_STATUS)"
    echo "Please check token permissions"
    exit 1
fi

echo
echo "🐳 Testing GHCR access..."

# Test GHCR login
if echo "$CR_PAT" | docker login ghcr.io -u jenicek001 --password-stdin >/dev/null 2>&1; then
    echo "✅ GHCR login: SUCCESS"
else
    echo "❌ GHCR login: FAILED"
    echo "Please ensure token has 'write:packages' scope"
    exit 1
fi

echo
echo "🎉 TOKEN SETUP COMPLETE!"
echo "=============================="
echo "✅ GitHub API access working"
echo "✅ GHCR access working"
echo "✅ Environment variables updated"
echo "✅ Changes made permanent"
echo
echo "📋 Next steps:"
echo "1. Push Docker images: docker push ghcr.io/jenicek001/familycart-backend:latest"
echo "2. Push Docker images: docker push ghcr.io/jenicek001/familycart-frontend:latest"
echo "3. Deploy UAT: cd /opt/familycart-uat-repo && docker compose -f docker-compose.uat.yml up -d"
