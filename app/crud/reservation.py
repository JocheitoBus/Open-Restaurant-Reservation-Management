"""
CRUD operations for reservation management.

Repository pattern implementation for reservation-related database operations.
Includes constraint validation to prevent table overbooking.
"""

from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import and_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import ReservationStatus
from app.models.reservation import Reservation
from app.schemas.reservation import (
    ReservationCreate,
    ReservationUpdate,
)


class ReservationRepository:
    """Repository for reservation CRUD operations."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize repository with database session.
        
        Args:
            session: AsyncSession for database operations
        """
        self.session = session

    async def create(self, reservation_create: ReservationCreate) -> Reservation:
        """
        Create a new reservation.
        
        Args:
            reservation_create: Reservation creation schema
            
        Returns:
            Created Reservation instance
            
        Raises:
            ValueError: If reservation overlaps with existing reservations or constraint violation
        """
        try:
            # Check for overlapping reservations
            await self._check_overbooking(
                table_id=reservation_create.table_id,
                start_time=reservation_create.start_time,
                end_time=reservation_create.end_time,
            )

            db_reservation = Reservation(**reservation_create.model_dump())
            self.session.add(db_reservation)
            await self.session.commit()
            await self.session.refresh(db_reservation)
            return db_reservation
        except ValueError:
            await self.session.rollback()
            raise
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(f"Database constraint violation: {str(e)}")
        except Exception as e:
            await self.session.rollback()
            raise

    async def get_by_id(self, reservation_id: int) -> Optional[Reservation]:
        """
        Retrieve a reservation by ID.
        
        Args:
            reservation_id: Reservation identifier
            
        Returns:
            Reservation instance or None if not found
        """
        statement = select(Reservation).where(Reservation.id == reservation_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_all(
        self, skip: int = 0, limit: int = 100
    ) -> Sequence[Reservation]:
        """
        Retrieve all reservations with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Sequence of Reservation instances
        """
        statement = select(Reservation).offset(skip).limit(limit)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_by_table_and_date(
        self, table_id: int, date: datetime
    ) -> Sequence[Reservation]:
        """
        Retrieve all reservations for a table on a specific date.
        
        Args:
            table_id: Table identifier
            date: Date to filter by (uses date component only)
            
        Returns:
            Sequence of Reservation instances for that date
        """
        start_of_day = datetime(date.year, date.month, date.day, 0, 0, 0)
        end_of_day = datetime(date.year, date.month, date.day, 23, 59, 59)

        statement = select(Reservation).where(
            and_(
                Reservation.table_id == table_id,
                Reservation.start_time >= start_of_day,
                Reservation.end_time <= end_of_day,
                Reservation.status != ReservationStatus.CANCELLED,
            )
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def update(
        self, reservation_id: int, reservation_update: ReservationUpdate
    ) -> Optional[Reservation]:
        """
        Update an existing reservation.
        
        Args:
            reservation_id: Reservation identifier
            reservation_update: Update schema with modified fields
            
        Returns:
            Updated Reservation instance or None if not found
            
        Raises:
            ValueError: If updated times would cause overbooking or constraint violation
        """
        try:
            db_reservation = await self.get_by_id(reservation_id)
            if not db_reservation:
                return None

            update_data = reservation_update.model_dump(exclude_unset=True)

            # Check for overbooking if time fields are being updated
            if "start_time" in update_data or "end_time" in update_data:
                new_start = update_data.get("start_time", db_reservation.start_time)
                new_end = update_data.get("end_time", db_reservation.end_time)
                await self._check_overbooking(
                    table_id=db_reservation.table_id,
                    start_time=new_start,
                    end_time=new_end,
                    exclude_reservation_id=reservation_id,
                )

            for key, value in update_data.items():
                setattr(db_reservation, key, value)

            self.session.add(db_reservation)
            await self.session.commit()
            await self.session.refresh(db_reservation)
            return db_reservation
        except ValueError:
            await self.session.rollback()
            raise
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(f"Database constraint violation: {str(e)}")
        except Exception as e:
            await self.session.rollback()
            raise

    async def delete(self, reservation_id: int) -> bool:
        """
        Delete a reservation by ID.
        
        Args:
            reservation_id: Reservation identifier
            
        Returns:
            True if deleted, False if not found
        """
        try:
            db_reservation = await self.get_by_id(reservation_id)
            if not db_reservation:
                return False

            self.session.delete(db_reservation)
            await self.session.commit()
            return True
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(f"Cannot delete reservation: {str(e)}")
        except Exception as e:
            await self.session.rollback()
            raise

    async def cancel(self, reservation_id: int) -> Optional[Reservation]:
        """
        Cancel a reservation (soft delete by changing status).
        
        Args:
            reservation_id: Reservation identifier
            
        Returns:
            Cancelled Reservation instance or None if not found
        """
        db_reservation = await self.get_by_id(reservation_id)
        if not db_reservation:
            return None

        db_reservation.status = ReservationStatus.CANCELLED
        self.session.add(db_reservation)
        await self.session.commit()
        await self.session.refresh(db_reservation)
        return db_reservation

    async def _check_overbooking(
        self,
        table_id: int,
        start_time: datetime,
        end_time: datetime,
        exclude_reservation_id: Optional[int] = None,
    ) -> None:
        """
        Check for overlapping reservations on the same table.
        
        Prevents overbooking by ensuring no time conflicts with active reservations.
        
        Args:
            table_id: Table identifier
            start_time: Reservation start time
            end_time: Reservation end time
            exclude_reservation_id: ID to exclude from check (for updates)
            
        Raises:
            ValueError: If an overlapping reservation exists
        """
        query = select(Reservation).where(
            and_(
                Reservation.table_id == table_id,
                Reservation.status != ReservationStatus.CANCELLED,
                Reservation.start_time < end_time,
                Reservation.end_time > start_time,
            )
        )

        if exclude_reservation_id is not None:
            query = query.where(Reservation.id != exclude_reservation_id)

        result = await self.session.execute(query)
        existing = result.scalar_one_or_none()

        if existing is not None:
            raise ValueError(
                f"Table {table_id} has an overlapping reservation "
                f"from {existing.start_time} to {existing.end_time}"
            )
