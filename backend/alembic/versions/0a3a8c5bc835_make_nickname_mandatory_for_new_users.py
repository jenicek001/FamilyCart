"""make_nickname_mandatory_for_new_users

Revision ID: 0a3a8c5bc835
Revises: 7f96d9c28e64
Create Date: 2025-06-26 10:47:26.423270

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0a3a8c5bc835"
down_revision: Union[str, Sequence[str], None] = "7f96d9c28e64"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # First, set default nicknames for existing users who don't have one
    op.execute(
        """
        UPDATE "user" 
        SET nickname = CASE 
            WHEN first_name IS NOT NULL THEN first_name
            ELSE SPLIT_PART(email, '@', 1)
        END 
        WHERE nickname IS NULL
    """
    )

    # Add a check constraint to ensure new users must have a nickname
    # Note: We're not making the column NOT NULL because existing users might still have NULL temporarily
    op.create_check_constraint(
        "user_nickname_not_empty", "user", "nickname IS NOT NULL AND nickname != ''"
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remove the check constraint
    op.drop_constraint("user_nickname_not_empty", "user", type_="check")
