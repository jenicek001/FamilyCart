#!/bin/bash
# test-nginx-config.sh
# Standalone nginx configuration tester

set -e

NGINX_DIR="/home/honzik/GitHub/FamilyCart/FamilyCart/deploy/nginx"

echo "🧪 Testing Nginx Configuration"
echo "==============================="

# Create a temporary directory with resolved configuration
TEMP_DIR=$(mktemp -d)
echo "📁 Creating temporary test environment..."

# Copy main config
cp "$NGINX_DIR/nginx.conf" "$TEMP_DIR/"

# Copy conf.d directory
cp -r "$NGINX_DIR/conf.d" "$TEMP_DIR/"

# Copy sites-available
cp -r "$NGINX_DIR/sites-available" "$TEMP_DIR/"

# Create sites-enabled with resolved files (not symlinks)
mkdir -p "$TEMP_DIR/sites-enabled"
for enabled_site in "$NGINX_DIR/sites-enabled/"*; do
    if [ -L "$enabled_site" ]; then
        site_name=$(basename "$enabled_site")
        cp "$NGINX_DIR/sites-available/$site_name" "$TEMP_DIR/sites-enabled/"
        echo "  ✅ Resolved enabled site: $site_name"
    fi
done

# Create a mock hosts file for upstream resolution
cat > "$TEMP_DIR/hosts" << 'EOF'
127.0.0.1 uat-backend
127.0.0.1 uat-frontend  
127.0.0.1 uat-prometheus
127.0.0.1 localhost
EOF

# Create SSL directory structure (empty for testing)
mkdir -p "$TEMP_DIR/ssl/familycart"
mkdir -p "$TEMP_DIR/ssl/connectedhome.cz" 
mkdir -p "$TEMP_DIR/ssl/default"

# Create dummy certificates for syntax testing
openssl req -x509 -nodes -days 1 -newkey rsa:1024 \
    -keyout "$TEMP_DIR/ssl/familycart/uat.familycart.local.key" \
    -out "$TEMP_DIR/ssl/familycart/uat.familycart.local.crt" \
    -subj "/C=CZ/CN=test" 2>/dev/null

openssl req -x509 -nodes -days 1 -newkey rsa:1024 \
    -keyout "$TEMP_DIR/ssl/connectedhome.cz/connectedhome.cz.key" \
    -out "$TEMP_DIR/ssl/connectedhome.cz/connectedhome.cz.crt" \
    -subj "/C=CZ/CN=test" 2>/dev/null

openssl req -x509 -nodes -days 1 -newkey rsa:1024 \
    -keyout "$TEMP_DIR/ssl/default/default.key" \
    -out "$TEMP_DIR/ssl/default/default.crt" \
    -subj "/C=CZ/CN=test" 2>/dev/null

echo "🔐 Created temporary SSL certificates for testing"

# Test with Docker
echo "🧪 Testing configuration with Docker..."

if docker run --rm \
   -v "$TEMP_DIR/nginx.conf:/etc/nginx/nginx.conf:ro" \
   -v "$TEMP_DIR/conf.d:/etc/nginx/conf.d:ro" \
   -v "$TEMP_DIR/sites-available:/etc/nginx/sites-available:ro" \
   -v "$TEMP_DIR/sites-enabled:/etc/nginx/sites-enabled:ro" \
   -v "$TEMP_DIR/ssl:/etc/nginx/ssl:ro" \
   -v "$TEMP_DIR/hosts:/etc/hosts:ro" \
   nginx:alpine nginx -t 2>/dev/null; then
    echo "✅ Nginx configuration syntax is VALID"
    RESULT=0
else
    echo "❌ Nginx configuration has ERRORS"
    echo ""
    echo "📋 Detailed error output:"
    docker run --rm \
       -v "$TEMP_DIR/nginx.conf:/etc/nginx/nginx.conf:ro" \
       -v "$TEMP_DIR/conf.d:/etc/nginx/conf.d:ro" \
       -v "$TEMP_DIR/sites-available:/etc/nginx/sites-available:ro" \
       -v "$TEMP_DIR/sites-enabled:/etc/nginx/sites-enabled:ro" \
       -v "$TEMP_DIR/ssl:/etc/nginx/ssl:ro" \
       -v "$TEMP_DIR/hosts:/etc/hosts:ro" \
       nginx:alpine nginx -t
    RESULT=1
fi

# Cleanup
echo "🧹 Cleaning up temporary files..."
rm -rf "$TEMP_DIR"

# Show summary
echo ""
echo "📊 Test Summary:"
echo "==============="
if [ $RESULT -eq 0 ]; then
    echo "✅ Configuration test PASSED"
    echo "   All syntax is valid and includes work correctly"
    echo ""
    echo "📋 Enabled sites tested:"
    for enabled_site in "$NGINX_DIR/sites-enabled/"*; do
        if [ -L "$enabled_site" ]; then
            site_name=$(basename "$enabled_site")
            echo "   ✅ $site_name"
        fi
    done
else
    echo "❌ Configuration test FAILED"
    echo "   Please fix the errors shown above"
fi

exit $RESULT
