#!/usr/bin/env python3
"""
Test WebSocket connection from the perspective of a browser client
to debug the "Connection issue" error.
"""

import asyncio
import websockets
import json
import sys

async def test_websocket_connection():
    """Test WebSocket connection like the frontend would do"""
    
    # Use test user token (Berta)
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4ZGVjY2Y1MC0zMzExLTQ4NmYtYmIxNS1iMGVjOGMwZDJkZWQiLCJhdWQiOlsiZmFzdGFwaS11c2VyczphdXRoIl0sImV4cCI6MTc1NDI4Mzg4NH0.K6J6CzbDJ_GV3JgNBEpgIQlfn0qmXoqBHLQITpCGTlA"
    list_id = 11
    
    # Construct WebSocket URL like the frontend does
    ws_url = f"ws://localhost:8000/api/v1/ws/lists/{list_id}?token={token}"
    
    print(f"🔌 Testing WebSocket connection to: {ws_url}")
    
    try:
        async with websockets.connect(ws_url) as websocket:
            print("✅ WebSocket connection established successfully!")
            
            # Send a ping message
            ping_message = {"type": "ping"}
            await websocket.send(json.dumps(ping_message))
            print("📤 Sent ping message")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Received response: {response}")
                
                # Parse response
                response_data = json.loads(response)
                print(f"📋 Parsed response: {response_data}")
                
            except asyncio.TimeoutError:
                print("⏰ No response received within 5 seconds")
            
            # Keep connection open for a bit to test stability
            print("⏳ Keeping connection open for 10 seconds...")
            await asyncio.sleep(10)
            
            print("✅ Connection test completed successfully")
            
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ WebSocket connection closed: {e}")
        return False
    except websockets.exceptions.InvalidURI as e:
        print(f"❌ Invalid WebSocket URI: {e}")
        return False
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

async def main():
    """Main test function"""
    print("🧪 WebSocket Connection Test")
    print("=" * 40)
    
    success = await test_websocket_connection()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
