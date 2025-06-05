from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy.orm import Mapped, relationship, mapped_column # For SQLAlchemy 2.0+
from sqlalchemy import String, Boolean, ForeignKey # If needed for custom fields
from ..db.base import Base # Your SQLAlchemy Base

class User(SQLAlchemyBaseUserTableUUID, Base):
    # Add any additional fields here, e.g.:
    # first_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # last_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # shopping_lists: Mapped[list["ShoppingList"]] = relationship(back_populates="owner")
    pass

# If you need a separate OAuthAccount table (fastapi-users usually handles this internally or via association table)
# class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
#     pass
