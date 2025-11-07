#!/usr/bin/env python3
"""
Test WebSocket connection from the perspective of a browser client
to debug the "Connection issue" error.
"""

import asyncio
import json
import sys

import websockets

#!/usr/bin/env python3
"""
WebSocket debugging utility to test real-time notifications for shopping lists.
"""

import asyncio
import json
import os
import sys

import websockets

# Add the parent directory to the Python path to import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings


async def test_websocket(list_id: str, token: str):
    """Test WebSocket connection for a specific shopping list."""
    ws_url = f"ws://localhost:{settings.PORT}/api/v1/ws/lists/{list_id}?token={token}"


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
