"""
SQLModel base declaration registry.

All models inherit from Base to ensure they are tracked by SQLAlchemy.
"""

from sqlmodel import SQLModel


class Base(SQLModel):
    """
    Base class for all SQLModel entities.
    
    This class serves as the declarative base for all database models.
    SQLAlchemy uses this to track table metadata.
    """
    pass
