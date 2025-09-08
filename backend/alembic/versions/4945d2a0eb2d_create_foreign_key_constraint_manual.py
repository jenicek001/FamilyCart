"""create_foreign_key_constraint_manual

Revision ID: 4945d2a0eb2d
Revises: 795e7e423f03
Create Date: 2025-07-18 15:27:34.362310

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4945d2a0eb2d"
down_revision: Union[str, Sequence[str], None] = "795e7e423f03"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Check if foreign key constraint exists before creating it
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    # Get foreign keys for item table
    foreign_keys = inspector.get_foreign_keys("item")
    fk_exists = any(fk["name"] == "fk_item_quantity_unit_id" for fk in foreign_keys)

    if not fk_exists:
        op.create_foreign_key(
            "fk_item_quantity_unit_id",
            "item",
            "unit",
            ["quantity_unit_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove foreign key constraint from quantity_unit_id (if it exists)
    connection = op.get_bind()
    inspector = sa.inspect(connection)

    # Get foreign keys for item table
    foreign_keys = inspector.get_foreign_keys("item")
    fk_exists = any(fk["name"] == "fk_item_quantity_unit_id" for fk in foreign_keys)

    if fk_exists:
        op.drop_constraint("fk_item_quantity_unit_id", "item", type_="foreignkey")
