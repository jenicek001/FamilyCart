from typing import Any, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings

# Create the SQLAlchemy engine
engine = create_engine(settings.DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for our models
class Base(DeclarativeBase):
    """Base class for all database models."""
    pass

def get_db() -> Generator:
    """
    Dependency function that yields database sessions.
    
    Yields:
        Session: A database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import all models here for Alembic to discover them
from ..models.user import User  # noqa
from ..models.shopping_list import ShoppingList  # noqa
from ..models.item import Item  # noqa
