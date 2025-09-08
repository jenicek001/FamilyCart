"""
Load test for WebSocket real-time functionality.
Tests multiple concurrent connections and message broadcasting.
"""

import asyncio
import websockets
import json
import time
import statistics
from datetime import datetime
from typing import List

# Configuration
WS_BASE_URL = "ws://localhost:8000/api/v1/ws/lists"
NUM_CONNECTIONS = 10
TEST_DURATION = 30  # seconds
MESSAGE_INTERVAL = 2  # seconds between broadcasts


class WebSocketLoadTest:
    """Load test for WebSocket functionality"""

    def __init__(self, num_connections: int, test_duration: int):
        self.num_connections = num_connections
        self.test_duration = test_duration
        self.connections: List[websockets.WebSocketServerProtocol] = []
        self.message_times: List[float] = []
        self.errors: List[str] = []

    async def simulate_connection(self, connection_id: int, list_id: int, token: str):
        """Simulate a single WebSocket connection"""

        uri = f"{WS_BASE_URL}/{list_id}?token={token}"

        try:
            async with websockets.connect(uri) as websocket:
                print(f"✅ Connection {connection_id} established")

                # Listen for messages
                while True:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        receive_time = time.time()

                        data = json.loads(message)
                        if data.get("type") in ["item_change", "list_change"]:
                            self.message_times.append(receive_time)
                            print(
                                f"📨 Connection {connection_id} received: {data.get('type')}"
                            )

                    except asyncio.TimeoutError:
                        # Send periodic ping to keep connection alive
                        await websocket.send(json.dumps({"type": "ping"}))

                    except websockets.exceptions.ConnectionClosed:
                        print(f"❌ Connection {connection_id} closed")
                        break

        except Exception as e:
            error_msg = f"Connection {connection_id} error: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")

    async def run_load_test(self, list_id: int, token: str):
        """Run the complete load test"""

        print(f"🚀 Starting WebSocket Load Test")
        print(f"   Connections: {self.num_connections}")
        print(f"   Duration: {self.test_duration}s")
        print(f"   List ID: {list_id}")
        print("=" * 50)

        # Start all connections
        connection_tasks = []
        for i in range(self.num_connections):
            task = asyncio.create_task(self.simulate_connection(i, list_id, token))
            connection_tasks.append(task)

        # Wait for connections to establish
        await asyncio.sleep(2)

        # Run test for specified duration
        start_time = time.time()
        end_time = start_time + self.test_duration

        print(f"🔥 Test running... (will stop in {self.test_duration}s)")

        # Let the test run
        await asyncio.sleep(self.test_duration)

        # Cancel all connection tasks
        for task in connection_tasks:
            task.cancel()

        # Wait for tasks to finish
        await asyncio.gather(*connection_tasks, return_exceptions=True)

        # Print results
        self.print_results()

    def print_results(self):
        """Print load test results"""

        print("\n" + "=" * 50)
        print("📊 LOAD TEST RESULTS")
        print("=" * 50)

        print(f"Connections attempted: {self.num_connections}")
        print(f"Errors: {len(self.errors)}")
        print(f"Messages received: {len(self.message_times)}")

        if self.errors:
            print("\n❌ Errors:")
            for error in self.errors[:5]:  # Show first 5 errors
                print(f"   - {error}")
            if len(self.errors) > 5:
                print(f"   ... and {len(self.errors) - 5} more")

        if self.message_times:
            avg_messages_per_second = len(self.message_times) / self.test_duration
            print(f"\n📈 Performance:")
            print(f"   Messages per second: {avg_messages_per_second:.2f}")
            print(f"   Total messages: {len(self.message_times)}")

        # Performance assessment
        success_rate = (
            (self.num_connections - len(self.errors)) / self.num_connections * 100
        )
        print(f"\n✅ Success Rate: {success_rate:.1f}%")

        if success_rate >= 95:
            print("🎉 EXCELLENT: WebSocket performance is great!")
        elif success_rate >= 85:
            print("👍 GOOD: WebSocket performance is acceptable")
        elif success_rate >= 70:
            print("⚠️  FAIR: WebSocket performance needs improvement")
        else:
            print("❌ POOR: WebSocket performance issues detected")


async def run_basic_load_test():
    """Run a basic load test without authentication (for testing connection limits)"""

    print("🧪 Running Basic WebSocket Load Test")
    print("This tests connection handling without authentication")
    print("=" * 50)

    # Test parameters
    num_connections = 5
    test_duration = 10

    async def test_connection(connection_id: int):
        """Test a single connection"""
        try:
            # Try to connect without auth (should fail gracefully)
            uri = f"ws://localhost:8000/api/v1/ws/lists/1?token=invalid"

            start_time = time.time()
            try:
                async with websockets.connect(uri) as websocket:
                    # This shouldn't succeed, but test the connection
                    await asyncio.sleep(1)

            except websockets.exceptions.InvalidStatusCode as e:
                end_time = time.time()
                response_time = end_time - start_time
                print(
                    f"✅ Connection {connection_id}: Auth rejected in {response_time:.3f}s (expected)"
                )
                return True

        except Exception as e:
            print(f"❌ Connection {connection_id}: Unexpected error: {e}")
            return False

    # Run concurrent connections
    tasks = []
    for i in range(num_connections):
        task = asyncio.create_task(test_connection(i))
        tasks.append(task)

    results = await asyncio.gather(*tasks)

    # Print results
    successful = sum(results)
    print(f"\n📊 Results:")
    print(f"   Connections tested: {num_connections}")
    print(f"   Proper auth rejection: {successful}")
    print(f"   Success rate: {successful/num_connections*100:.1f}%")

    if successful >= num_connections * 0.9:
        print("✅ WebSocket authentication and connection handling works correctly!")
    else:
        print("❌ WebSocket connection handling needs attention")


# Simple performance test that doesn't require authentication
async def test_websocket_endpoint_availability():
    """Test that WebSocket endpoint is available and responds correctly"""

    print("🔌 Testing WebSocket Endpoint Availability")
    print("=" * 40)

    try:
        # Test basic connectivity
        uri = "ws://localhost:8000/api/v1/ws/lists/1?token=test"

        start_time = time.time()

        try:
            async with websockets.connect(uri) as websocket:
                # This should fail auth but reach the endpoint
                await asyncio.sleep(0.1)

        except websockets.exceptions.InvalidStatusCode as e:
            end_time = time.time()
            response_time = end_time - start_time

            if e.status_code in [1008, 1003]:  # Auth failure codes
                print(
                    f"✅ Endpoint reachable, auth working (response in {response_time:.3f}s)"
                )
                return True
            else:
                print(f"❌ Unexpected status code: {e.status_code}")
                return False

        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

    except Exception as e:
        print(f"❌ Endpoint test failed: {e}")
        return False


if __name__ == "__main__":
    print("WebSocket Load Test Suite")
    print("Make sure the backend is running on localhost:8000\n")

    try:
        # Run basic tests
        print("1️⃣ Testing endpoint availability...")
        asyncio.run(test_websocket_endpoint_availability())

        print("\n2️⃣ Testing connection handling...")
        asyncio.run(run_basic_load_test())

        print("\n🎯 Basic WebSocket load testing completed!")
        print("\nFor full load testing with authentication:")
        print("1. Create test users and get valid JWT tokens")
        print("2. Use WebSocketLoadTest class with real credentials")
        print("3. Monitor server resources during testing")

    except KeyboardInterrupt:
        print("\n👋 Test interrupted by user")
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
