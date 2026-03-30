"""
CRUD operations for table management.

Repository pattern implementation for table-related database operations.
"""

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.table import Table
from app.schemas.table import TableCreate, TableUpdate


class TableRepository:
    """Repository for table CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize repository with database session.
        
        Args:
            session: AsyncSession for database operations
        """
        self.session = session

    async def create(self, table_create: TableCreate) -> Table:
        """
        Create a new table.
        
        Args:
            table_create: Table creation schema
            
        Returns:
            Created Table instance
            
        Raises:
            ValueError: If table_number already exists (constraint violation)
        """
        try:
            db_table = Table(**table_create.model_dump())
            self.session.add(db_table)
            await self.session.commit()
            await self.session.refresh(db_table)
            return db_table
        except IntegrityError as e:
            await self.session.rollback()
            if "table_number" in str(e):
                raise ValueError(f"Table number '{table_create.table_number}' already exists")
            raise ValueError(f"Database constraint violation: {str(e)}")
        except Exception as e:
            await self.session.rollback()
            raise

    async def get_by_id(self, table_id: int) -> Optional[Table]:
        """
        Retrieve a table by ID.
        
        Args:
            table_id: Table identifier
            
        Returns:
            Table instance or None if not found
        """
        statement = select(Table).where(Table.id == table_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_number(self, table_number: str) -> Optional[Table]:
        """
        Retrieve a table by its display number.
        
        Args:
            table_number: Table display number (e.g., "T1")
            
        Returns:
            Table instance or None if not found
        """
        statement = select(Table).where(Table.table_number == table_number)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> Sequence[Table]:
        """
        Retrieve all tables with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Sequence of Table instances
        """
        statement = select(Table).offset(skip).limit(limit)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def update(self, table_id: int, table_update: TableUpdate) -> Optional[Table]:
        """
        Update an existing table.
        
        Args:
            table_id: Table identifier
            table_update: Update schema with modified fields
            
        Returns:
            Updated Table instance or None if not found
            
        Raises:
            ValueError: If constraint violation occurs
        """
        try:
            db_table = await self.get_by_id(table_id)
            if not db_table:
                return None

            update_data = table_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_table, key, value)

            self.session.add(db_table)
            await self.session.commit()
            await self.session.refresh(db_table)
            return db_table
        except IntegrityError as e:
            await self.session.rollback()
            if "table_number" in str(e):
                raise ValueError(f"Table number already exists")
            raise ValueError(f"Database constraint violation: {str(e)}")
        except Exception as e:
            await self.session.rollback()
            raise

    async def delete(self, table_id: int) -> bool:
        """
        Delete a table by ID.
        
        Args:
            table_id: Table identifier
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            ValueError: If foreign key constraint prevents deletion
        """
        try:
            db_table = await self.get_by_id(table_id)
            if not db_table:
                return False

            self.session.delete(db_table)
            await self.session.commit()
            return True
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(f"Cannot delete table with active reservations: {str(e)}")
        except Exception as e:
            await self.session.rollback()
            raise
