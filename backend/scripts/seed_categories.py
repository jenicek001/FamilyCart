#!/usr/bin/env python3
"""
Seed the database with standard shopping categories.
This script populates the category table with common supermarket categories.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.category import Category

# Create async engine and session maker
engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI_ASYNC, echo=False)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Standard shopping categories with icons
STANDARD_CATEGORIES = [
    {"name": "Produce", "icon_name": "nutrition", "translations": None},
    {"name": "Dairy", "icon_name": "egg_alt", "translations": None},
    {"name": "Meat", "icon_name": "kebab_dining", "translations": None},
    {"name": "Seafood", "icon_name": "phishing", "translations": None},
    {"name": "Bakery", "icon_name": "bakery_dining", "translations": None},
    {"name": "Frozen", "icon_name": "ac_unit", "translations": None},
    {"name": "Pantry", "icon_name": "inventory_2", "translations": None},
    {"name": "Beverages", "icon_name": "local_cafe", "translations": None},
    {"name": "Snacks", "icon_name": "cookie", "translations": None},
    {"name": "Personal Care", "icon_name": "face", "translations": None},
    {"name": "Household", "icon_name": "home", "translations": None},
    {"name": "Pet Supplies", "icon_name": "pets", "translations": None},
    {"name": "Baby", "icon_name": "child_care", "translations": None},
    {"name": "Health", "icon_name": "medical_services", "translations": None},
    {"name": "Alcohol", "icon_name": "liquor", "translations": None},
    {"name": "Deli", "icon_name": "restaurant", "translations": None},
    {"name": "Uncategorized", "icon_name": "category", "translations": None},
]


async def seed_categories():
    """Seed the database with standard categories."""
    async with async_session_maker() as session:
        try:
            # Check existing categories
            result = await session.execute(select(Category))
            existing = result.scalars().all()
            existing_names = {cat.name for cat in existing}

            print(f"Found {len(existing)} existing categories: {existing_names}")

            # Add only missing categories
            added_count = 0
            for cat_data in STANDARD_CATEGORIES:
                if cat_data["name"] not in existing_names:
                    category = Category(**cat_data)
                    session.add(category)
                    added_count += 1
                    print(f"  ✅ Added: {cat_data['name']}")
                else:
                    print(f"  ⏭️  Skipped (exists): {cat_data['name']}")

            await session.commit()
            print(f"\n✅ Seeding complete! Added {added_count} new categories.")
            print(f"Total categories in database: {len(existing) + added_count}")

        except Exception as e:
            print(f"❌ Error seeding categories: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_categories())
