"""add_last_modified_by_to_item

Revision ID: 687785059f62
Revises: 6000f99ab353
Create Date: 2025-06-26 13:25:05.314894

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "687785059f62"
down_revision: Union[str, Sequence[str], None] = "6000f99ab353"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add last_modified_by column to item table
    # Initially nullable, we'll populate it with the owner_id in a follow-up migration
    op.add_column("item", sa.Column("last_modified_by_id", sa.UUID(), nullable=True))
    op.create_foreign_key(
        "item_last_modified_by_id_fkey", "item", "user", ["last_modified_by_id"], ["id"]
    )

    # Set initial value: last_modified_by = owner for all existing items
    op.execute("UPDATE item SET last_modified_by_id = owner_id")

    # Make the column non-nullable after setting initial values
    op.alter_column("item", "last_modified_by_id", nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove foreign key constraint and column
    op.drop_constraint("item_last_modified_by_id_fkey", "item", type_="foreignkey")
    op.drop_column("item", "last_modified_by_id")
