#!/bin/bash

# FamilyCart Docker Images Push Script
echo "🐳 FamilyCart Docker Images Push to GHCR"
echo "========================================"

# Check if logged into GHCR
if ! docker info | grep -q "ghcr.io"; then
    echo "🔑 Logging into GHCR..."
    if ! echo "$CR_PAT" | docker login ghcr.io -u jenicek001 --password-stdin; then
        echo "❌ Failed to login to GHCR. Please check your token."
        exit 1
    fi
fi

echo "✅ GHCR login successful"

# Verify images exist locally
echo
echo "🔍 Checking local images..."

BACKEND_IMAGE="ghcr.io/jenicek001/familycart-backend:latest"
FRONTEND_IMAGE="ghcr.io/jenicek001/familycart-frontend:latest"

if ! docker image inspect "$BACKEND_IMAGE" >/dev/null 2>&1; then
    echo "❌ Backend image not found locally: $BACKEND_IMAGE"
    echo "Please build it first: cd backend && docker build -t $BACKEND_IMAGE ."
    exit 1
fi

if ! docker image inspect "$FRONTEND_IMAGE" >/dev/null 2>&1; then
    echo "❌ Frontend image not found locally: $FRONTEND_IMAGE"
    echo "Please build it first: cd frontend && docker build -t $FRONTEND_IMAGE ."
    exit 1
fi

echo "✅ Both images found locally"

# Show image details
echo
echo "📊 Image Details:"
echo "Backend:  $(docker image inspect $BACKEND_IMAGE --format '{{.Id}}' | cut -d':' -f2 | cut -c1-12)"
echo "Frontend: $(docker image inspect $FRONTEND_IMAGE --format '{{.Id}}' | cut -d':' -f2 | cut -c1-12)"
echo "Backend Size:  $(docker image inspect $BACKEND_IMAGE --format '{{.Size}}' | numfmt --to=iec-i --suffix=B)"
echo "Frontend Size: $(docker image inspect $FRONTEND_IMAGE --format '{{.Size}}' | numfmt --to=iec-i --suffix=B)"

echo
echo "🚀 Pushing backend image..."
if docker push "$BACKEND_IMAGE"; then
    echo "✅ Backend push: SUCCESS"
else
    echo "❌ Backend push: FAILED"
    exit 1
fi

echo
echo "🚀 Pushing frontend image..."
if docker push "$FRONTEND_IMAGE"; then
    echo "✅ Frontend push: SUCCESS"
else
    echo "❌ Frontend push: FAILED"
    exit 1
fi

echo
echo "🧪 Verifying images in registry..."

# Test pull to verify availability
if docker pull "$BACKEND_IMAGE" >/dev/null 2>&1; then
    echo "✅ Backend image verified in registry"
else
    echo "⚠️  Backend image pull test failed"
fi

if docker pull "$FRONTEND_IMAGE" >/dev/null 2>&1; then
    echo "✅ Frontend image verified in registry"
else
    echo "⚠️  Frontend image pull test failed"
fi

echo
echo "🎉 DOCKER IMAGES PUSH COMPLETE!"
echo "================================"
echo "✅ Backend: $BACKEND_IMAGE"
echo "✅ Frontend: $FRONTEND_IMAGE"
echo
echo "📋 Next step:"
echo "Deploy UAT: cd /opt/familycart-uat-repo && docker compose -f docker-compose.uat.yml up -d"
