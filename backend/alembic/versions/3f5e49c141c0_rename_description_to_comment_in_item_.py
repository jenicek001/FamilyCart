"""rename_description_to_comment_in_item_table

Revision ID: 3f5e49c141c0
Revises: 1aa3bd94a6b5
Create Date: 2025-07-18 10:44:47.433830

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3f5e49c141c0"
down_revision: Union[str, Sequence[str], None] = "1aa3bd94a6b5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Rename description column to comment in item table
    op.alter_column("item", "description", new_column_name="comment")


def downgrade() -> None:
    """Downgrade schema."""
    # Rename comment column back to description in item table
    op.alter_column("item", "comment", new_column_name="description")
