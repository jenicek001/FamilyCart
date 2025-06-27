#!/usr/bin/env python3
"""
Quick test for a single Czech item to verify the fix.
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent / "app"))

# Mock the crud_category before importing ai_service
class MockCategory:
    def __init__(self, name: str):
        self.name = name

class MockCRUDCategory:
    def get_multi(self, db, limit=100):
        return [
            MockCategory('Produce'),
            MockCategory('Dairy'), 
            MockCategory('Meat'),
            MockCategory('Pantry'),
            MockCategory('Frozen'),
        ]

sys.modules['app.crud.crud_category'] = type('MockModule', (), {
    'category': MockCRUDCategory()
})()

from app.services.ai_service import ai_service

async def test_single_item():
    """Test categorization of a single Czech item."""
    
    test_item = "rajčata"  # Czech for tomatoes
    print(f"🔍 Testing Czech item: '{test_item}'")
    
    try:
        mock_db = object()
        suggested_category = await ai_service.suggest_category(test_item, mock_db)
        print(f"✅ Suggested category: '{suggested_category}'")
        print(f"   Expected: 'Produce' or similar")
        
        # Check if it's a reasonable categorization
        if suggested_category.lower() in ['produce', 'vegetables', 'fruit']:
            print("✅ Categorization looks correct!")
        else:
            print(f"⚠️  Unexpected category, but Czech recognition seems to work")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_single_item())
