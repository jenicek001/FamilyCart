"""convert_datetime_columns_to_timezone_aware

Revision ID: 6000f99ab353
Revises: d7b15d135da2
Create Date: 2025-06-26 12:13:04.119397

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6000f99ab353"
down_revision: Union[str, Sequence[str], None] = "d7b15d135da2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Convert datetime columns to timestamp with time zone
    # First, convert existing naive timestamps to UTC (assume they are already UTC)
    
    # For item table
    op.execute("""
        ALTER TABLE item 
        ALTER COLUMN created_at TYPE timestamp with time zone 
        USING created_at AT TIME ZONE 'UTC'
    """)
    
    op.execute("""
        ALTER TABLE item 
        ALTER COLUMN updated_at TYPE timestamp with time zone 
        USING updated_at AT TIME ZONE 'UTC'
    """)
    
    # For shopping_list table
    op.execute("""
        ALTER TABLE shopping_list 
        ALTER COLUMN created_at TYPE timestamp with time zone 
        USING created_at AT TIME ZONE 'UTC'
    """)
    
    op.execute("""
        ALTER TABLE shopping_list 
        ALTER COLUMN updated_at TYPE timestamp with time zone 
        USING updated_at AT TIME ZONE 'UTC'
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Convert back to timestamp without time zone
    # This will lose timezone information
    
    # For item table
    op.execute("""
        ALTER TABLE item 
        ALTER COLUMN created_at TYPE timestamp without time zone 
        USING created_at AT TIME ZONE 'UTC'
    """)
    
    op.execute("""
        ALTER TABLE item 
        ALTER COLUMN updated_at TYPE timestamp without time zone 
        USING updated_at AT TIME ZONE 'UTC'
    """)
    
    # For shopping_list table
    op.execute("""
        ALTER TABLE shopping_list 
        ALTER COLUMN created_at TYPE timestamp without time zone 
        USING created_at AT TIME ZONE 'UTC'
    """)
    
    op.execute("""
        ALTER TABLE shopping_list 
        ALTER COLUMN updated_at TYPE timestamp without time zone 
        USING updated_at AT TIME ZONE 'UTC'
    """);
