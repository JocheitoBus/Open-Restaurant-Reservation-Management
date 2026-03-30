"""
FastAPI dependency injection utilities.

Provides reusable dependencies for repository instances and database sessions.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.reservation import ReservationRepository
from app.crud.table import TableRepository
from app.db.session import get_session


async def get_table_repository(
    session: AsyncSession = Depends(get_session),
) -> TableRepository:
    """
    Dependency to provide TableRepository instance.
    
    Args:
        session: Database session (injected by FastAPI)
        
    Returns:
        TableRepository instance
        
    Example:
        @router.get("/tables")
        async def get_tables(repo: TableRepository = Depends(get_table_repository)):
            tables = await repo.get_all()
            return tables
    """
    return TableRepository(session)


async def get_reservation_repository(
    session: AsyncSession = Depends(get_session),
) -> ReservationRepository:
    """
    Dependency to provide ReservationRepository instance.
    
    Args:
        session: Database session (injected by FastAPI)
        
    Returns:
        ReservationRepository instance
        
    Example:
        @router.post("/reservations")
        async def create_reservation(
            data: ReservationCreate,
            repo: ReservationRepository = Depends(get_reservation_repository)
        ):
            return await repo.create(data)
    """
    return ReservationRepository(session)
