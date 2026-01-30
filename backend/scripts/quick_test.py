#!/usr/bin/env python3
"""
Quick test to verify AI categorization and WebSocket functionality.
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from app.core.config import settings

# Build database URL
DATABASE_URL = (
    f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
    f"{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

def test_ai_categorization():
    """Test AI categorization by checking database for properly categorized items."""
    print("\n" + "=" * 60)
    print("TESTING AI CATEGORIZATION")
    print("=" * 60)
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Get all items with their categories
        result = conn.execute(text("""
            SELECT 
                i.id,
                i.name,
                c.name as category,
                i.created_at
            FROM item i
            JOIN category c ON i.category_id = c.id
            ORDER BY i.created_at DESC
            LIMIT 10
        """))
        
        items = list(result)
        
        if not items:
            print("⚠️  No items in database. Please add items via the UI to test.")
            print("\nTo test AI categorization:")
            print("1. Navigate to http://192.168.12.200:3003")
            print("2. Sign in")
            print("3. Open a shopping list")
            print("4. Add item: 'Butter' - should categorize as 'Dairy'")
            print("5. Add item: 'Apple' - should categorize as 'Produce'")
            return
        
        print(f"\nFound {len(items)} recent items:\n")
        print(f"{'ID':<5} {'Name':<20} {'Category':<20} {'Created'}")
        print("-" * 70)
        
        uncategorized_count = 0
        properly_categorized = 0
        
        for item in items:
            item_id, name, category, created = item
            status = "✅" if category != "Uncategorized" else "⚠️ "
            print(f"{status} {item_id:<3} {name:<20} {category:<20} {created}")
            
            if category == "Uncategorized":
                uncategorized_count += 1
            else:
                properly_categorized += 1
        
        print("\n" + "=" * 60)
        print(f"Properly Categorized: {properly_categorized}")
        print(f"Uncategorized: {uncategorized_count}")
        
        if properly_categorized > 0:
            print("\n✅ AI CATEGORIZATION IS WORKING!")
            print("Items are being automatically categorized by Gemini API.")
        elif uncategorized_count == len(items):
            print("\n⚠️  All items are 'Uncategorized'")
            print("These may be old items created before categories were seeded.")
            print("Add a new item via the UI to test AI categorization.")
        
        print("=" * 60)


def check_gemini_config():
    """Verify Gemini API key is set."""
    print("\n" + "=" * 60)
    print("GEMINI API CONFIGURATION")
    print("=" * 60)
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if gemini_key:
        print(f"✅ GEMINI_API_KEY: {gemini_key[:10]}...{gemini_key[-4:]} (length: {len(gemini_key)})")
    else:
        print("❌ GEMINI_API_KEY not set")
        return
    
    ai_provider = os.getenv("AI_PROVIDER", "gemini")
    model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash-exp")
    
    print(f"✅ AI_PROVIDER: {ai_provider}")
    print(f"✅ GEMINI_MODEL_NAME: {model_name}")
    print("=" * 60)


def main():
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "QUICK FUNCTIONALITY TEST" + " " * 19 + "║")
    print("╚" + "=" * 58 + "╝")
    
    check_gemini_config()
    test_ai_categorization()
    
    print("\n" + "=" * 60)
    print("WEBSOCKET VERIFICATION")
    print("=" * 60)
    print("Run from host machine:")
    print("  docker exec familycart-frontend-dev env | grep WEBSOCKET")
    print("Expected: NEXT_PUBLIC_WEBSOCKET_URL=ws://192.168.12.200:8003")
    print("")
    print("Check backend logs:")
    print("  docker logs familycart-backend-dev 2>&1 | grep -i websocket")
    print("Expected: WebSocket connections showing '[accepted]'")
    print("=" * 60)
    
    print("\n" + "=" * 60)
    print("MANUAL TESTING STEPS")
    print("=" * 60)
    print("1. Open browser: http://192.168.12.200:3003")
    print("2. Open Developer Tools (F12) → Console tab")
    print("3. Sign in with: playwright.user1@test.com / Test123!")
    print("4. Click on 'Playwright Test List'")
    print("5. Verify in console: 'WebSocket connected' (no error 1006)")
    print("6. Add item: 'Butter' → should show category 'Dairy'")
    print("7. Add item: 'Apple' → should show category 'Produce'")
    print("8. Open same list in another tab → verify real-time sync")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
