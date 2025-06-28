#!/usr/bin/env python3
"""
Test script to verify the item update functionality is working after the async session fix
"""
import asyncio
import sys
import os
sys.path.append('/home/honzik/GitHub/FamilyCart/FamilyCart/backend')

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.services.ai_service import AIService
from app.models.category import Category

async def test_ai_service_async():
    """Test that the AI service now works with async sessions"""
    print("🧪 Testing AI Service with Async Session")
    print("=" * 50)
    
    ai_service = AIService()
    
    # Create a test database session
    async with AsyncSessionLocal() as session:
        try:
            # Test the suggest_category method that was causing the error
            print("📝 Testing suggest_category method with async session...")
            
            # Test with a simple item name
            test_item = "apple"
            suggested_category = await ai_service.suggest_category(test_item, session)
            
            print(f"✅ SUCCESS: suggest_category('{test_item}') returned: '{suggested_category}'")
            
            # Verify we can also query categories directly
            result = await session.execute(select(Category).limit(5))
            categories = result.scalars().all()
            print(f"📋 Found {len(categories)} categories in database")
            for cat in categories:
                print(f"   - {cat.name}")
                
            return True
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False

async def main():
    print("🚀 Testing Item Update Fix")
    print("Testing async session compatibility in AI service")
    print()
    
    success = await test_ai_service_async()
    
    print()
    if success:
        print("🎉 All tests passed! The async session fix is working.")
        print("✅ Item updates should now work without 500 errors.")
    else:
        print("❌ Tests failed. There may still be an issue with the fix.")
        
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
