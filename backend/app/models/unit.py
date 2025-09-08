from sqlalchemy import String, Boolean, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from ..db.base import Base


class Unit(Base):
    """Unit model for quantity measurements."""

    __tablename__ = "unit"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    symbol: Mapped[str] = mapped_column(String(10), nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    base_unit: Mapped[str | None] = mapped_column(String(20))
    conversion_factor: Mapped[Optional[float]] = mapped_column(Numeric(15, 6))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    locale: Mapped[str | None] = mapped_column(String(10))

    def __str__(self) -> str:
        return f"{self.name} ({self.symbol})"
