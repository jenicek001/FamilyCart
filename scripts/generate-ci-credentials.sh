#!/bin/bash

# Generate CI Infrastructure Secure Credentials
# This script generates secure passwords for CI infrastructure and provides setup instructions

set -e

echo "🔐 Generating secure credentials for CI infrastructure..."
echo "==========================================================="

# Generate secure passwords
CI_POSTGRES_PASSWORD=$(openssl rand -base64 32)
CI_REDIS_PASSWORD=$(openssl rand -base64 32)

echo ""
echo "📋 Generated Secure Credentials:"
echo "================================"
echo ""
echo "CI_POSTGRES_USER=ci_user_familycart"
echo "CI_POSTGRES_DB=ci_familycart_db"
echo "CI_POSTGRES_PASSWORD=$CI_POSTGRES_PASSWORD"
echo ""
echo "CI_REDIS_PASSWORD=$CI_REDIS_PASSWORD"
echo ""

# Create .env.ci file with generated credentials
cat > .env.ci << EOF
# CI Infrastructure Security Configuration
# Generated on: $(date)

# PostgreSQL Credentials
CI_POSTGRES_USER=ci_user_familycart
CI_POSTGRES_PASSWORD=$CI_POSTGRES_PASSWORD
CI_POSTGRES_DB=ci_familycart_db

# Redis Credentials  
CI_REDIS_PASSWORD=$CI_REDIS_PASSWORD

# GitHub Actions Secrets Configuration
# Add these secrets in: GitHub Repository → Settings → Secrets and variables → Actions
#
# Required secrets:
# - CI_POSTGRES_USER: ci_user_familycart
# - CI_POSTGRES_PASSWORD: $CI_POSTGRES_PASSWORD  
# - CI_POSTGRES_DB: ci_familycart_db
# - CI_REDIS_PASSWORD: $CI_REDIS_PASSWORD
# - GITHUB_TOKEN (automatically provided by GitHub)

# Security Notes:
# 1. Never commit this file to version control
# 2. Use different credentials for each environment (CI, UAT, Production)
# 3. Rotate passwords regularly (quarterly recommended)
# 4. Store production credentials in secure password managers
EOF

echo "📁 Created .env.ci file with generated credentials"
echo ""

echo "🔧 GitHub Secrets Setup Instructions:"
echo "====================================="
echo ""
echo "1. Go to your GitHub repository"
echo "2. Navigate to: Settings → Secrets and variables → Actions"
echo "3. Add the following repository secrets:"
echo ""
echo "   Name: CI_POSTGRES_USER"
echo "   Value: ci_user_familycart"
echo ""
echo "   Name: CI_POSTGRES_DB" 
echo "   Value: ci_familycart_db"
echo ""
echo "   Name: CI_POSTGRES_PASSWORD"
echo "   Value: $CI_POSTGRES_PASSWORD"
echo ""
echo "   Name: CI_REDIS_PASSWORD"
echo "   Value: $CI_REDIS_PASSWORD"
echo ""

echo "🚀 CI Infrastructure Update Commands:"
echo "===================================="
echo ""
echo "1. Restart CI infrastructure with new credentials:"
echo "   ./scripts/ci-management.sh restart-infrastructure"
echo ""
echo "2. Verify services are running:"
echo "   ./scripts/ci-management.sh status"
echo ""
echo "3. View infrastructure logs if needed:"
echo "   ./scripts/ci-management.sh logs-infrastructure"
echo ""

echo "⚠️  Important Security Notes:"
echo "============================"
echo ""
echo "• The .env.ci file contains sensitive credentials"
echo "• Add .env.ci to .gitignore if not already present"
echo "• Use secure credential storage for production environments"
echo "• Consider using GitHub Environment Protection Rules for sensitive deployments"
echo ""

echo "✅ Credential generation complete!"
echo ""
echo "Next steps:"
echo "1. Review the generated .env.ci file"
echo "2. Add the GitHub secrets as shown above"
echo "3. Restart CI infrastructure with new credentials"
echo "4. Test CI pipeline to ensure everything works"