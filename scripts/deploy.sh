#!/bin/bash
set -e

# Universal deployment script for both UAT and PROD
# Usage: deploy.sh
#
# Required environment variables:
#   BACKEND_IMAGE - Full backend image tag (e.g., ghcr.io/jenicek001/familycart-backend:develop)
#   FRONTEND_IMAGE - Full frontend image tag (e.g., ghcr.io/jenicek001/familycart-frontend:develop)
#   DEPLOY_HOST - SSH host to deploy to
#   DEPLOY_USER - SSH user
#   DEPLOY_SSH_KEY - SSH private key content
#   DEPLOY_PATH - Path on remote server (e.g., /opt/familycart-uat)
#   COMPOSE_FILE - Docker compose file to use (e.g., docker-compose.uat.yml)
#   ENV_NAME - Environment name for logging (e.g., UAT, PRODUCTION)

echo "🚀 Deploying to ${ENV_NAME} environment..."
echo "Backend Image: ${BACKEND_IMAGE}"
echo "Frontend Image: ${FRONTEND_IMAGE}"
echo "Deploy Target: ${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_PATH}"

# Prepare SSH key
echo "$DEPLOY_SSH_KEY" > /tmp/deploy_key
chmod 600 /tmp/deploy_key

# Copy deployment files to server
echo "📦 Copying deployment files..."
scp -i /tmp/deploy_key -o StrictHostKeyChecking=no \
  ${COMPOSE_FILE} \
  ${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_PATH}/

# Copy environment file if it exists
if [ -f ".env.${ENV_NAME,,}" ]; then
  echo "📄 Copying .env.${ENV_NAME,,} as .env..."
  scp -i /tmp/deploy_key -o StrictHostKeyChecking=no \
    .env.${ENV_NAME,,} \
    ${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_PATH}/.env
elif [ -f ".env" ]; then
  echo "📄 Copying .env..."
  scp -i /tmp/deploy_key -o StrictHostKeyChecking=no \
    .env \
    ${DEPLOY_USER}@${DEPLOY_HOST}:${DEPLOY_PATH}/.env
else
  echo "⚠️  No .env file found, services may not start correctly"
fi

# Deploy on remote server
echo "🚀 Deploying services on ${DEPLOY_HOST}..."
ssh -i /tmp/deploy_key -o StrictHostKeyChecking=no ${DEPLOY_USER}@${DEPLOY_HOST} \
  BACKEND_IMAGE="${BACKEND_IMAGE}" \
  FRONTEND_IMAGE="${FRONTEND_IMAGE}" \
  DEPLOY_PATH="${DEPLOY_PATH}" \
  COMPOSE_FILE="${COMPOSE_FILE}" \
  ENV_NAME="${ENV_NAME}" \
  GITHUB_TOKEN="${GITHUB_TOKEN}" \
  bash << 'ENDSSH'
  set -e
  cd ${DEPLOY_PATH}
  
  # Export image tags for docker-compose
  export BACKEND_IMAGE="${BACKEND_IMAGE}"
  export FRONTEND_IMAGE="${FRONTEND_IMAGE}"
  
  # Login to GitHub Container Registry if token is available
  if [ -n "${GITHUB_TOKEN}" ]; then
    echo "🔐 Logging into GitHub Container Registry..."
    echo "${GITHUB_TOKEN}" | docker login ghcr.io -u $(echo ${BACKEND_IMAGE} | cut -d'/' -f2) --password-stdin
  fi
  
  # Pull new images
  echo "📥 Pulling images..."
  docker compose -f ${COMPOSE_FILE} pull
  
  # Deploy services
  echo "🔄 Starting services..."
  docker compose -f ${COMPOSE_FILE} up -d
  
  # Wait for services to stabilize
  echo "⏳ Waiting for services to start..."
  sleep 30
  
  # Verify services are running
  echo "📊 Service status:"
  docker compose -f ${COMPOSE_FILE} ps
  
  echo "✅ ${ENV_NAME} deployment completed!"
ENDSSH

# Cleanup SSH key
rm /tmp/deploy_key

echo "✅ Deployment script completed successfully!"
