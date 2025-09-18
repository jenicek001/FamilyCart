#!/usr/bin/env python3
"""
Playwright WebSocket Testing Script for FamilyCart
Tests the sophisticated session-based exclusion system
"""

import asyncio
import json
import time
import sys
import os
from playwright.async_api import async_playwright, Page, BrowserContext

# Add the backend directory to the Python path to import settings
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from app.core.config import settings

# Configuration
FRONTEND_URL = "http://localhost:9002"
BACKEND_URL = f"http://localhost:{settings.PORT}"
TEST_USER_EMAIL = "devtester@example.com"
TEST_USER_PASSWORD = "DevTest123!"

class WebSocketTester:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.contexts = []
        self.pages = []
        self.websocket_messages = []

    async def setup(self):
        """Initialize Playwright and browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)
        print("✅ Browser launched")

    async def cleanup(self):
        """Clean up resources"""
        for context in self.contexts:
            await context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("✅ Cleanup completed")

    async def create_page_context(self, device_name: str) -> tuple[BrowserContext, Page]:
        """Create a new browser context (simulates a different device)"""
        context = await self.browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent=f"PlaywrightTester-{device_name}"
        )
        self.contexts.append(context)
        
        page = await context.new_page()
        self.pages.append(page)
        
        # Listen for WebSocket messages
        page.on("websocket", self.on_websocket_frame)
        
        print(f"✅ Created context for {device_name}")
        return context, page

    def on_websocket_frame(self, ws):
        """Handle WebSocket frame events"""
        def on_frame_sent(payload):
            print(f"📤 WS Sent: {payload}")
            
        def on_frame_received(payload):
            print(f"📥 WS Received: {payload}")
            try:
                data = json.loads(payload)
                self.websocket_messages.append({
                    "timestamp": time.time(),
                    "type": "received",
                    "data": data
                })
            except json.JSONDecodeError:
                pass
        
        ws.on("framesent", on_frame_sent)
        ws.on("framereceived", on_frame_received)

    async def login_user(self, page: Page, device_name: str):
        """Login user on a specific page"""
        print(f"🔐 Logging in user on {device_name}")
        
        await page.goto(f"{FRONTEND_URL}/auth/login")
        await page.wait_for_selector('input[type="email"]', timeout=10000)
        
        # Fill login form
        await page.fill('input[type="email"]', TEST_USER_EMAIL)
        await page.fill('input[type="password"]', TEST_USER_PASSWORD)
        
        # Submit form
        await page.click('button[type="submit"]')
        
        # Wait for redirect to dashboard
        await page.wait_for_url(f"{FRONTEND_URL}/dashboard", timeout=15000)
        print(f"✅ {device_name} logged in successfully")

    async def navigate_to_websocket_test(self, page: Page, device_name: str):
        """Navigate to WebSocket test page"""
        print(f"🌐 Navigating {device_name} to WebSocket test page")
        
        await page.goto(f"{FRONTEND_URL}/websocket-test")
        await page.wait_for_selector('[data-testid="websocket-status"]', timeout=10000)
        
        # Wait for WebSocket connection
        await page.wait_for_function(
            "document.querySelector('[data-testid=\"websocket-status\"]').textContent.includes('Connected')",
            timeout=15000
        )
        
        print(f"✅ {device_name} connected to WebSocket")

    async def add_item(self, page: Page, device_name: str, item_name: str):
        """Add an item to the shopping list"""
        print(f"➕ {device_name} adding item: {item_name}")
        
        # Fill item name
        await page.fill('input[placeholder*="item"]', item_name)
        
        # Click add button
        await page.click('button:has-text("Add Item")')
        
        # Wait a bit for the action to complete
        await page.wait_for_timeout(1000)
        
        print(f"✅ {device_name} added item: {item_name}")

    async def verify_item_appears(self, page: Page, device_name: str, item_name: str, should_appear: bool = True):
        """Verify if an item appears in the list"""
        try:
            if should_appear:
                await page.wait_for_selector(f'text="{item_name}"', timeout=5000)
                print(f"✅ {device_name} sees item: {item_name}")
                return True
            else:
                # Check if item doesn't appear within timeout
                try:
                    await page.wait_for_selector(f'text="{item_name}"', timeout=2000)
                    print(f"❌ {device_name} unexpectedly sees item: {item_name}")
                    return False
                except:
                    print(f"✅ {device_name} correctly doesn't see item: {item_name}")
                    return True
        except:
            if should_appear:
                print(f"❌ {device_name} doesn't see expected item: {item_name}")
                return False
            else:
                print(f"✅ {device_name} correctly doesn't see item: {item_name}")
                return True

    async def test_multi_device_sync(self):
        """Test sophisticated session-based exclusion system"""
        print("\n🚀 Starting Multi-Device WebSocket Sync Test")
        print("=" * 60)
        
        # Create two browser contexts (simulating phone + desktop)
        context1, page1 = await self.create_page_context("Desktop")
        context2, page2 = await self.create_page_context("Mobile")
        
        # Login on both devices
        await self.login_user(page1, "Desktop")
        await self.login_user(page2, "Mobile")
        
        # Navigate to WebSocket test page
        await self.navigate_to_websocket_test(page1, "Desktop")
        await self.navigate_to_websocket_test(page2, "Mobile")
        
        print("\n📱💻 Both devices connected to same list with same user")
        print("Testing session-based exclusion...")
        
        # Test 1: Desktop adds item - Mobile should see it
        print("\n🧪 Test 1: Cross-device synchronization")
        await self.add_item(page1, "Desktop", "Desktop Item")
        await asyncio.sleep(2)  # Wait for WebSocket propagation
        
        result1 = await self.verify_item_appears(page2, "Mobile", "Desktop Item", True)
        
        # Test 2: Mobile adds item - Desktop should see it
        print("\n🧪 Test 2: Reverse synchronization")
        await self.add_item(page2, "Mobile", "Mobile Item")
        await asyncio.sleep(2)  # Wait for WebSocket propagation
        
        result2 = await self.verify_item_appears(page1, "Desktop", "Mobile Item", True)
        
        # Test 3: Same device adds item - should NOT trigger duplicate update
        print("\n🧪 Test 3: Session-based exclusion (preventing self-updates)")
        
        # Clear previous messages
        self.websocket_messages.clear()
        
        await self.add_item(page1, "Desktop", "Self-Update Test")
        await asyncio.sleep(2)
        
        # Check if desktop got its own update (it shouldn't)
        self_updates = [msg for msg in self.websocket_messages 
                      if 'Self-Update Test' in str(msg.get('data', {}))]
        
        print(f"WebSocket messages received: {len(self.websocket_messages)}")
        print(f"Self-update messages: {len(self_updates)}")
        
        # Test 4: Create third context to test multiple sessions
        print("\n🧪 Test 4: Three-way synchronization")
        context3, page3 = await self.create_page_context("Tablet")
        await self.login_user(page3, "Tablet")
        await self.navigate_to_websocket_test(page3, "Tablet")
        
        await self.add_item(page3, "Tablet", "Tablet Item")
        await asyncio.sleep(2)
        
        result3 = await self.verify_item_appears(page1, "Desktop", "Tablet Item", True)
        result4 = await self.verify_item_appears(page2, "Mobile", "Tablet Item", True)
        
        # Summary
        print("\n" + "=" * 60)
        print("🧪 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"✅ Cross-device sync (Desktop→Mobile): {'PASS' if result1 else 'FAIL'}")
        print(f"✅ Reverse sync (Mobile→Desktop): {'PASS' if result2 else 'FAIL'}")
        print(f"✅ Session exclusion (no self-updates): {'PASS' if len(self_updates) == 0 else 'FAIL'}")
        print(f"✅ Three-way sync (Tablet→Others): {'PASS' if result3 and result4 else 'FAIL'}")
        
        all_passed = result1 and result2 and (len(self_updates) == 0) and result3 and result4
        print(f"\n🎯 OVERALL RESULT: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
        
        return all_passed

    async def run_tests(self):
        """Run all tests"""
        try:
            await self.setup()
            success = await self.test_multi_device_sync()
            
            if success:
                print("\n🎉 Session-based WebSocket exclusion system is working perfectly!")
                print("✅ Same user can have multiple devices synchronized in real-time")
                print("✅ No duplicate updates when user modifies from same session")
            else:
                print("\n⚠️  Some tests failed - check the logs above")
                
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.cleanup()

async def main():
    """Main test runner"""
    print("🧪 FamilyCart WebSocket Session-Based Exclusion Test")
    print("Testing sophisticated multi-device same-user synchronization")
    print("=" * 80)
    
    tester = WebSocketTester()
    await tester.run_tests()

if __name__ == "__main__":
    asyncio.run(main())
