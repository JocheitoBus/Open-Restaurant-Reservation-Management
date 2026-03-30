"""
Database session configuration and management.

Provides async SQLAlchemy session factory and database utilities.
Implements proper async session lifecycle and initialization.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)


# Create async engine with SQLite
engine: AsyncEngine = create_async_engine(
    url=settings.database_url,
    echo=settings.sql_echo,
    future=True,
    connect_args={"check_same_thread": False},  # Required for SQLite async
)

# Create async session factory
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI dependency injection.
    
    Yields an AsyncSession for database operations.
    Automatically handles session cleanup on completion or error.
    
    Yields:
        AsyncSession: Database session instance
        
    Example:
        @app.get("/tables")
        async def get_tables(session: AsyncSession = Depends(get_session)):
            # Use session for database operations
            pass
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for manual session management outside FastAPI endpoints.
    
    Useful for background tasks or one-off database operations.
    
    Yields:
        AsyncSession: Database session instance
        
    Example:
        async with get_db_session() as session:
            result = await session.execute(select(Table))
            tables = result.scalars().all()
    """
    session = async_session()
    try:
        yield session
    finally:
        await session.close()


async def init_db() -> None:
    """
    Initialize database tables at application startup.
    
    Creates all tables defined in SQLModel models via metadata.create_all().
    This is suitable for development and staging environments.
    
    **IMPORTANT - Production Migration Strategy:**
    For production environments, use Alembic migrations instead:
      1. Install: pip install alembic
      2. Init: alembic init migrations
      3. Configure: Update migrations/env.py for async support
      4. Create migration: alembic revision --autogenerate -m "description"
      5. Apply: alembic upgrade head
    
    This approach provides:
    - Version control for schema changes
    - Rollback capability on deployment failures
    - Audit trail of all schema modifications
    - Safe concurrent deployment support
    
    Raises:
        Exception: If table creation fails (connection, permissions, etc.)
        
    Logs:
        - INFO: Table creation completion
        - ERROR: Any exceptions during creation (includes stacktrace)
    """
    try:
        from app.models.base import Base
        
        logger.info(f"🔄 Initializing database tables from models...")
        logger.debug(f"📊 Database URL: {settings.database_url}")
        logger.debug(f"📋 Models to create: {list(Base.metadata.tables.keys())}")
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info(f"✅ Database initialization complete")
        logger.info(f"📊 Tables created: {', '.join(Base.metadata.tables.keys())}")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}", exc_info=True)
        raise


async def close_db() -> None:
    """
    Close the database connection.
    
    Should be called during application shutdown.
    Safely disposes of the connection pool.
    
    Logs:
        - INFO: Connection closed
        - ERROR: Any exceptions during cleanup
    """
    try:
        logger.info("🔌 Closing database connections...")
        await engine.dispose()
        logger.info("✅ Database connections closed successfully")
    except Exception as e:
        logger.error(f"❌ Error closing database connection: {e}", exc_info=True)
        raise
