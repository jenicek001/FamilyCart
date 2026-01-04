#!/bin/bash

# Generate Development Environment File
# This script creates .env.dev with secure random passwords

set -e

ENV_FILE="backend/.env.dev"
EXAMPLE_FILE="backend/.env.dev.example"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== FamilyCart Dev Environment Generator ===${NC}"
echo ""

# Check if .env.dev already exists
if [ -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}⚠️  $ENV_FILE already exists!${NC}"
    read -p "Overwrite? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled. Existing file preserved."
        exit 0
    fi
fi

# Check if example file exists
if [ ! -f "$EXAMPLE_FILE" ]; then
    echo -e "${YELLOW}Error: $EXAMPLE_FILE not found!${NC}"
    exit 1
fi

echo -e "${GREEN}Generating secure passwords...${NC}"

# Generate secure random passwords (32 characters)
POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
SECRET_KEY=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-64)

# Copy example file and replace placeholders
cp "$EXAMPLE_FILE" "$ENV_FILE"

# Replace passwords in the file
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS sed syntax
    sed -i '' "s/POSTGRES_PASSWORD=CHANGE_ME_generate_secure_password/POSTGRES_PASSWORD=$POSTGRES_PASSWORD/" "$ENV_FILE"
    sed -i '' "s/REDIS_PASSWORD=CHANGE_ME_generate_secure_redis_password/REDIS_PASSWORD=$REDIS_PASSWORD/" "$ENV_FILE"
    sed -i '' "s/SECRET_KEY=CHANGE_ME_generate_secure_secret_key/SECRET_KEY=$SECRET_KEY/" "$ENV_FILE"
else
    # Linux sed syntax
    sed -i "s/POSTGRES_PASSWORD=CHANGE_ME_generate_secure_password/POSTGRES_PASSWORD=$POSTGRES_PASSWORD/" "$ENV_FILE"
    sed -i "s/REDIS_PASSWORD=CHANGE_ME_generate_secure_redis_password/REDIS_PASSWORD=$REDIS_PASSWORD/" "$ENV_FILE"
    sed -i "s/SECRET_KEY=CHANGE_ME_generate_secure_secret_key/SECRET_KEY=$SECRET_KEY/" "$ENV_FILE"
fi

echo -e "${GREEN}✅ Created $ENV_FILE with secure passwords${NC}"
echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. Review $ENV_FILE and update any optional values (email, AI keys)"
echo "2. NEVER commit $ENV_FILE to git (it's in .gitignore)"
echo "3. Start development: ./scripts/dev.sh start"
echo ""
echo -e "${GREEN}Generated passwords:${NC}"
echo "PostgreSQL: ********** (hidden for security)"
echo "Redis:      ********** (hidden for security)"
echo "Secret Key: ********** (hidden for security)"
echo ""
echo -e "${YELLOW}⚠️  These passwords are stored in $ENV_FILE${NC}"
echo -e "${YELLOW}⚠️  Keep this file secure and never commit it to version control${NC}"
