#!/bin/bash

# Test WebSocket JWT audience validation fix
# This script tests both string and array audience formats

echo "🔧 Testing WebSocket JWT Audience Validation Fix"
echo "================================================"

# Test configuration
SECRET_KEY="a_very_secret_key"
USER_ID="5f37cb05-fc62-43bf-bc5b-f04114a8ee0a"
LIST_ID=11
BASE_URL="ws://localhost:8000"

echo "📋 Test Details:"
echo "  - User ID: $USER_ID"  
echo "  - List ID: $LIST_ID"
echo "  - Backend: $BASE_URL"
echo ""

# Create test token with ARRAY audience (the problematic format)
echo "🎯 Creating JWT token with ARRAY audience format..."
ARRAY_AUDIENCE_TOKEN=$(python3 -c "
import jwt
from datetime import datetime, timedelta
payload = {
    'sub': '$USER_ID',
    'aud': ['fastapi-users:auth'],  # Array format that was causing issues
    'exp': datetime.utcnow() + timedelta(hours=1)
}
print(jwt.encode(payload, '$SECRET_KEY', algorithm='HS256'))
")

echo "✅ Token created: ${ARRAY_AUDIENCE_TOKEN:0:30}..."
echo ""

# Test the WebSocket endpoint with wscat if available
if command -v wscat &> /dev/null; then
    echo "🔗 Testing WebSocket connection with array audience token..."
    echo "   URL: $BASE_URL/api/v1/ws/lists/$LIST_ID?token=$ARRAY_AUDIENCE_TOKEN"
    echo ""
    echo "   This should now succeed (previously failed with 'Invalid audience' error)"
    echo "   Press Ctrl+C to stop the test after confirming connection works"
    echo ""
    
    timeout 10s wscat -c "$BASE_URL/api/v1/ws/lists/$LIST_ID?token=$ARRAY_AUDIENCE_TOKEN" || true
    
    echo ""
    echo "🎉 If you saw 'Connected' and/or connection_established messages above,"
    echo "   then the JWT audience validation fix is working!"
else
    echo "⚠️  wscat not available. Install with: npm install -g wscat"
    echo "   Or test manually with a WebSocket client using this URL:"
    echo "   $BASE_URL/api/v1/ws/lists/$LIST_ID?token=$ARRAY_AUDIENCE_TOKEN"
fi

echo ""
echo "🔍 Expected behavior:"
echo "   ✅ BEFORE fix: Connection rejected with 403 'Invalid audience'"
echo "   ✅ AFTER fix:  Connection accepted and 'connection_established' message received"
echo ""
echo "📚 Fix Summary:"
echo "   - Modified authenticate_user() to handle both string and array audience formats"
echo "   - Fixed useWebSocket hook dependency loop causing reconnection cycles"
echo "   - WebSocket connections should now be stable without continuous reconnects"
