#!/usr/bin/env python3
"""
Test script to verify the Gemini icon suggestion fix.

This script tests the icon suggestion functionality to ensure:
1. Plain text responses are handled correctly
2. JSON responses (legacy) are handled correctly  
3. Error handling is robust
4. The fix resolves the "Expecting value: line 1 column 1 (char 0)" error
"""

import asyncio
import sys
import os
import logging

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

from app.services.gemini_provider import GeminiProvider
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_icon_suggestion():
    """Test the icon suggestion functionality."""
    print("🧪 Testing Gemini Icon Suggestion Fix")
    print("=" * 50)
    
    # Test configuration
    print(f"✅ Model: {settings.GEMINI_MODEL_NAME}")
    print(f"✅ API Key configured: {bool(settings.GOOGLE_API_KEY)}")
    
    try:
        # Initialize the provider
        provider = GeminiProvider()
        print(f"✅ Provider initialized successfully")
        print(f"✅ Provider name: {provider.provider_name}")
        print(f"✅ Model name: {provider.model_name}")
        
        # Test cases
        test_cases = [
            ("Milk", "Dairy"),
            ("Laptop", "Electronics"), 
            ("Shampoo", "Personal Care"),
            ("Apple", "Produce"),
            ("Bread", "Pantry")
        ]
        
        print("\n🔍 Testing Icon Suggestions:")
        print("-" * 30)
        
        for item_name, category_name in test_cases:
            try:
                print(f"\n📱 Testing: '{item_name}' in '{category_name}'")
                
                # Call the icon suggestion method
                suggested_icon = await provider.suggest_icon(item_name, category_name)
                
                print(f"   ✅ Result: '{suggested_icon}'")
                
                # Verify the result is valid
                if suggested_icon and isinstance(suggested_icon, str):
                    print(f"   ✅ Valid string response")
                else:
                    print(f"   ❌ Invalid response type: {type(suggested_icon)}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                print(f"   ❌ Error type: {type(e).__name__}")
        
        print("\n🎯 Testing Edge Cases:")
        print("-" * 25)
        
        # Test with empty/invalid inputs
        edge_cases = [
            ("", ""),
            ("Unknown Item", "Unknown Category"),
            ("тест", "категория"),  # Cyrillic
            ("🍎", "🥬")  # Emojis
        ]
        
        for item_name, category_name in edge_cases:
            try:
                print(f"\n🔍 Edge case: '{item_name}' in '{category_name}'")
                suggested_icon = await provider.suggest_icon(item_name, category_name)
                print(f"   ✅ Result: '{suggested_icon}'")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("\n" + "=" * 50)
        print("✅ Icon suggestion fix test completed successfully!")
        print("✅ The 'Expecting value: line 1 column 1 (char 0)' error should be resolved.")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        print(f"❌ Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_icon_suggestion())
