"""
Simple script to create test users in the database
"""
import asyncio
import sys
sys.path.insert(0, "/code")

from app.db.session import AsyncSessionLocal
from app.models.user import User  
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_test_users():
    """Create test users for development testing"""
    async with AsyncSessionLocal() as session:
        # Create test user
        test_user = User(
            email="test@familycart.com",
            hashed_password=pwd_context.hash("testpass123"),
            is_active=True,
            is_verified=True,
            full_name="Test User"
        )
        session.add(test_user)
        
        # Create another test user
        test_user2 = User(
            email="demo@familycart.com",
            hashed_password=pwd_context.hash("demo123"),
            is_active=True,
            is_verified=True,
            full_name="Demo User"
        )
        session.add(test_user2)
        
        await session.commit()
        print("✅ Test users created successfully!")
        print("   - test@familycart.com / testpass123")
        print("   - demo@familycart.com / demo123")

if __name__ == "__main__":
    asyncio.run(create_test_users())
