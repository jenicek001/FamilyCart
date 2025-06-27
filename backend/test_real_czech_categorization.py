#!/usr/bin/env python3
"""
Test adding a new Czech item via the API to verify categorization works.
"""
import asyncio
import sys
from pathlib import Path

# Add the backend directory to sys.path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.ai_service import ai_service
from app.crud.crud_category import category as crud_category
from app.api.deps import get_session

async def test_new_czech_item_categorization():
    """Test categorization with standardized categories."""
    
    # Mock the crud_category to return standardized categories
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
                MockCategory('Beverages'),
                MockCategory('Snacks'),
                MockCategory('Personal Care'),
                MockCategory('Household'),
                MockCategory('Other'),
            ]

    # Patch the crud_category
    import sys
    sys.modules['app.crud.crud_category'] = type('MockModule', (), {
        'category': MockCRUDCategory()
    })()
    
    # Test Czech items
    test_items = [
        "máslo",      # butter -> Dairy
        "jablka",     # apples -> Produce  
        "mrkev",      # carrots -> Produce
        "kuřecí maso", # chicken meat -> Meat
    ]
    
    print("=== Testing Czech Item Categorization with Standardized Categories ===\n")
    
    mock_db = object()
    
    for item_name in test_items:
        try:
            print(f"🔍 Testing: '{item_name}'")
            suggested_category = await ai_service.suggest_category(item_name, mock_db)
            print(f"   ✅ Suggested category: '{suggested_category}'")
            
            # Also test translation
            translation_result = await ai_service.standardize_and_translate_item_name(item_name)
            standardized = translation_result.get('standardized_name', item_name)
            print(f"   📝 Standardized name: '{standardized}'")
            print()
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            print()

if __name__ == "__main__":
    asyncio.run(test_new_czech_item_categorization())
