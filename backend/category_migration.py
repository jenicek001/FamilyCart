"""
Database migration to standardize categories to English.
"""

from sqlalchemy import text

# Category mappings from Czech to English
CATEGORY_MAPPINGS = {
    "Mléčné výrobky": "Dairy",
    "mléčné výrobky": "Dairy",
    "Ovoce a zelenina": "Produce",
    "ovoce a zelenina": "Produce",
    "Groceries": "Other",  # Generic category -> Other
    "other": "Other",
    "dairy": "Dairy",
    "pantry": "Pantry",
}

STANDARD_CATEGORIES = [
    "Produce",  # Fruits, vegetables
    "Dairy",  # Milk, cheese, yogurt
    "Meat",  # Meat, seafood, poultry
    "Pantry",  # Dry goods, canned items, bread
    "Frozen",  # Frozen foods, ice cream
    "Beverages",  # Drinks
    "Snacks",  # Chips, candy, etc.
    "Personal Care",  # Toiletries, health
    "Household",  # Cleaning, paper products
    "Other",  # Everything else
]


def get_migration_sql():
    """Generate SQL for category standardization migration."""

    sql = f"""
-- Category Standardization Migration
-- Standardizes all categories to English names

BEGIN;

-- Step 1: Create new standardized categories if they don't exist
INSERT INTO category (name) 
SELECT unnest(ARRAY{STANDARD_CATEGORIES}) AS name
WHERE NOT EXISTS (
    SELECT 1 FROM category WHERE category.name = unnest(ARRAY{STANDARD_CATEGORIES})
);

-- Step 2: Update items to use standardized categories
"""

    for old_name, new_name in CATEGORY_MAPPINGS.items():
        sql += f"""
-- Map '{old_name}' -> '{new_name}'
UPDATE item 
SET category_id = (SELECT id FROM category WHERE name = '{new_name}')
WHERE category_id = (SELECT id FROM category WHERE name = '{old_name}');
"""

    sql += (
        """
-- Step 3: Remove old Czech/mixed categories that are now empty
DELETE FROM category 
WHERE name NOT IN """
        + str(tuple(STANDARD_CATEGORIES)).replace("'", "''")
        + """;

COMMIT;

-- Verification query
SELECT 
    c.name,
    COUNT(i.id) as item_count
FROM 
    category c
    LEFT JOIN item i ON c.id = i.category_id
GROUP BY 
    c.id, c.name
ORDER BY 
    item_count DESC, c.name;
"""
    )

    return sql


if __name__ == "__main__":
    print("Category Standardization Migration SQL:")
    print("=" * 50)
    print(get_migration_sql())
