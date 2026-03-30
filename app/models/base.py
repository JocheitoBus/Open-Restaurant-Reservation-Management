"""
Base model package for SQLModel metadata binding.

Provides a common Base object aliases SQLModel for use in metadata creation 
and declarative model mapping. All database models inherit from Base (SQLModel) 
to enable automatic table creation via metadata.create_all().

Usage:
    from app.models.base import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
"""

from sqlmodel import SQLModel

# `Base` acts as an alias for SQLModel declarative base
# Used for metadata binding and table creation during initialization
Base = SQLModel
