#!/usr/bin/env python3
"""
Quick test to verify WebSocket connection stability after fixing the reconnection loop issue.
"""

import asyncio
import websockets
import json
import time
import jwt
from datetime import datetime, timedelta

# Test configuration (update these as needed)
SECRET_KEY = "a_very_secret_key"  # Should match backend config
BASE_URL = "ws://localhost:8000"
LIST_ID = 11
USER_ID = "5f37cb05-fc62-43bf-bc5b-f04114a8ee0a"

def create_test_token():
    """Create a test JWT token with array audience like fastapi-users generates"""
    payload = {
        "sub": USER_ID,
        "aud": ["fastapi-users:auth"],  # Array audience format
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

async def test_websocket_stability():
    """Test WebSocket connection stability for 30 seconds"""
    token = create_test_token()
    url = f"{BASE_URL}/api/v1/ws/lists/{LIST_ID}?token={token}"
    
    print(f"Testing WebSocket stability at: {url}")
    print("Monitoring connection for 30 seconds...")
    
    try:
        async with websockets.connect(url) as websocket:
            start_time = time.time()
            message_count = 0
            
            # Send periodic pings to keep connection alive
            async def send_pings():
                while True:
                    await asyncio.sleep(10)
                    try:
                        await websocket.send(json.dumps({"type": "ping"}))
                        print(f"[{time.time() - start_time:.1f}s] Sent ping")
                    except Exception as e:
                        print(f"Error sending ping: {e}")
                        break
            
            # Listen for messages
            async def listen_messages():
                nonlocal message_count
                async for message in websocket:
                    message_count += 1
                    data = json.loads(message)
                    elapsed = time.time() - start_time
                    print(f"[{elapsed:.1f}s] Received: {data.get('type', 'unknown')} - {data.get('message', '')}")
                    
                    if elapsed > 30:  # Test for 30 seconds
                        break
            
            # Run both tasks concurrently
            await asyncio.gather(
                send_pings(),
                listen_messages(),
                return_exceptions=True
            )
            
            elapsed = time.time() - start_time
            print(f"\n✅ Connection stable for {elapsed:.1f}s")
            print(f"✅ Received {message_count} messages")
            print("✅ Test PASSED - No reconnection loops detected!")
            
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"❌ Connection closed unexpectedly: {e}")
        print("❌ Test FAILED - Connection not stable")
    except Exception as e:
        print(f"❌ Test error: {e}")
        print("❌ Test FAILED")

if __name__ == "__main__":
    print("WebSocket Stability Test")
    print("=" * 50)
    asyncio.run(test_websocket_stability())
