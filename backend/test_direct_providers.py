#!/usr/bin/env python3
"""
Test direct provider calls to see where the issue lies.
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, '/home/honzik/GitHub/FamilyCart/FamilyCart/backend')

async def test_direct_providers():
    try:
        from app.services.fallback_ai_service import fallback_ai_service
        
        print("Testing direct provider calls...")
        print("=" * 50)
        
        # Test Ollama directly first to ensure it works
        print("Testing Ollama provider directly...")
        try:
            ollama_result = await fallback_ai_service.fallback_provider.suggest_category_async("sůl do myčky", ["Cleaning", "Food"])
            print(f"✓ Ollama result: {ollama_result}")
        except Exception as e:
            print(f"✗ Ollama error: {e}")
        
        # Test Gemini directly to trigger quota error
        print("\nTesting Gemini provider directly (should hit quota limit)...")
        try:
            gemini_result = await fallback_ai_service.primary_provider.suggest_category_async("sůl do myčky", ["Cleaning", "Food"])
            print(f"✓ Gemini result: {gemini_result}")
        except Exception as e:
            print(f"✗ Gemini error (expected): {e}")
            
        # Test fallback service (should catch Gemini error and use Ollama)
        print("\nTesting fallback service (should catch Gemini error and use Ollama)...")
        try:
            fallback_result = await fallback_ai_service.suggest_category_async("sůl do myčky", ["Cleaning", "Food"])
            print(f"✓ Fallback service result: {fallback_result}")
        except Exception as e:
            print(f"✗ Fallback service error: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct_providers())
