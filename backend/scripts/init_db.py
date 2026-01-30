"""
Initialize database with all required tables
"""
import asyncio
import sys
import traceback
sys.path.insert(0, "/code")

from app.db.session import engine
from app.db.base import Base  # This imports all models
from app.models.user import User
from app.models.shopping_list import ShoppingList
from app.models.item import Item
from app.models.category import Category

async def init_db():
    """Create all tables"""
    try:
        print("Starting database initialization...")
        print(f"Engine: {engine}")
        print(f"Base metadata tables: {[t.name for t in Base.metadata.sorted_tables]}")
        
        async with engine.begin() as conn:
            print("Connected to database")
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            print("Tables created")
        
        print("✅ Database tables created successfully!")
        print("Tables:", ", ".join([table.name for table in Base.metadata.sorted_tables]))
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        traceback.print_exc()
        raise

if __name__ == "__main__":
    asyncio.run(init_db())
