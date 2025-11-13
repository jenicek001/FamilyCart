#!/bin/bash
# Update UAT .env with email configuration
# Automatically detects UAT deployment location from Docker

set -e  # Exit on any error

echo "=================================================="
echo "UAT Email Configuration Update Script"
echo "=================================================="
echo ""

# Detect UAT directory from running Docker container
echo "🔍 Detecting UAT deployment location..."
UAT_DIR=$(docker inspect familycart-uat-backend --format '{{range $key, $value := .Config.Labels}}{{if eq $key "com.docker.compose.project.working_dir"}}{{$value}}{{end}}{{end}}' 2>/dev/null)

if [ -z "$UAT_DIR" ]; then
    echo "❌ ERROR: Could not find UAT backend container"
    echo "   Make sure 'familycart-uat-backend' container is running"
    exit 1
fi

echo "✅ Found UAT at: $UAT_DIR"

ENV_FILE="$UAT_DIR/.env"
COMPOSE_FILE="$UAT_DIR/docker-compose.uat.yml"

echo "=================================================="
echo "UAT Email Configuration Update Script"
echo "=================================================="
echo ""

# Check if UAT directory exists
if [ ! -d "$UAT_DIR" ]; then
    echo "❌ ERROR: UAT directory not found at $UAT_DIR"
    exit 1
fi

# Backup existing .env
if [ -f "$ENV_FILE" ]; then
    BACKUP_FILE="$ENV_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo "📦 Creating backup: $BACKUP_FILE"
    cp "$ENV_FILE" "$BACKUP_FILE"
else
    echo "⚠️  No existing .env file found. Creating new one."
fi

echo ""
echo "Adding email configuration to .env file..."
echo ""

# Read credentials from local development .env
DEV_ENV="/home/honzik/GitHub/FamilyCart/FamilyCart/backend/.env"

if [ ! -f "$DEV_ENV" ]; then
    echo "❌ ERROR: Development .env not found at $DEV_ENV"
    echo "Please provide Brevo credentials manually."
    exit 1
fi

# Extract Brevo credentials from development .env
BREVO_USER=$(grep "^BREVO_SMTP_USER=" "$DEV_ENV" | cut -d '=' -f2-)
BREVO_PASSWORD=$(grep "^BREVO_SMTP_PASSWORD=" "$DEV_ENV" | cut -d '=' -f2-)

if [ -z "$BREVO_USER" ] || [ -z "$BREVO_PASSWORD" ]; then
    echo "❌ ERROR: Could not find Brevo credentials in $DEV_ENV"
    exit 1
fi

# Append email configuration to UAT .env
cat >> "$ENV_FILE" << EOF

# ============================================================================
# EMAIL SERVICE CONFIGURATION - Added $(date)
# ============================================================================

# Email Provider
EMAIL_PROVIDER=brevo

# Sender Configuration
FROM_EMAIL=noreply@familycart.app
FROM_NAME=FamilyCart

# Frontend URL (UAT)
FRONTEND_URL=https://uat.familycart.app

# Brevo SMTP Credentials
BREVO_SMTP_HOST=smtp-relay.brevo.com
BREVO_SMTP_PORT=587
BREVO_SMTP_USER=$BREVO_USER
BREVO_SMTP_PASSWORD=$BREVO_PASSWORD

# Token Expiration Times (seconds)
VERIFICATION_TOKEN_LIFETIME_SECONDS=172800  # 48 hours
RESET_PASSWORD_TOKEN_LIFETIME_SECONDS=3600  # 1 hour
INVITATION_TOKEN_LIFETIME_SECONDS=604800    # 7 days
EOF

echo "✅ Email configuration added to $ENV_FILE"
echo ""
echo "📋 Configuration summary:"
echo "   EMAIL_PROVIDER: brevo"
echo "   FROM_EMAIL: noreply@familycart.app"
echo "   FRONTEND_URL: https://uat.familycart.app"
echo "   BREVO_SMTP_USER: $BREVO_USER"
echo ""
echo "🔄 Restarting UAT backend service..."
cd "$UAT_DIR"

# Detect backend service name
BACKEND_SERVICE=$(docker compose -f "$COMPOSE_FILE" ps --services | grep -i backend | head -n1)
if [ -z "$BACKEND_SERVICE" ]; then
    echo "❌ ERROR: Could not find backend service in compose file"
    exit 1
fi

echo "   Service name: $BACKEND_SERVICE"
docker compose -f "$COMPOSE_FILE" restart "$BACKEND_SERVICE"

echo ""
echo "⏳ Waiting for backend to start..."
sleep 5

echo ""
echo "📊 Checking backend logs for email service initialization..."
docker compose -f "$COMPOSE_FILE" logs --tail=50 "$BACKEND_SERVICE" | grep -i "email\|smtp\|brevo" || true

echo ""
echo "=================================================="
echo "✅ UAT EMAIL CONFIGURATION COMPLETE"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Test user registration at https://uat.familycart.app"
echo "2. Check email inbox for verification email"
echo "3. Monitor logs: docker compose -f docker-compose.uat.yml logs -f backend"
echo ""
echo "To view full backend logs:"
echo "  cd $UAT_DIR && docker compose -f $COMPOSE_FILE logs -f $BACKEND_SERVICE"
echo ""
