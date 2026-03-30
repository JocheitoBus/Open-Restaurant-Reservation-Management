"""
Database models for reservation management.

Defines the Reservation SQLModel entity with overbooking prevention logic.
Includes composite indexes for efficient overbooking detection queries.
"""

from datetime import datetime
from typing import Optional

from sqlmodel import Column, DateTime, Field, ForeignKey, SQLModel, func, Index
from pydantic import ConfigDict

from app.core.constants import ReservationStatus


class Reservation(SQLModel, table=True):
    """
    Reservation entity representing a customer's table booking.
    
    Implements constraints to prevent table overbooking by ensuring
    no overlapping reservations on the same table.
    
    Attributes:
        id: Unique reservation identifier
        table_id: Foreign key reference to the reserved table
        customer_name: Name of the customer making the reservation
        party_size: Number of people in the party
        start_time: Reservation start time
        end_time: Reservation end time
        status: Current reservation status
        special_requests: Optional notes or special requests
        created_at: Timestamp when the reservation was created
        updated_at: Timestamp when the reservation was last updated
    """
    
    __tablename__ = "reservations"
    
    id: Optional[int] = Field(primary_key=True, index=True)
    table_id: int = Field(foreign_key="tables.id", index=True)
    customer_name: str = Field(min_length=1, max_length=255)
    party_size: int = Field(ge=1, le=20)
    start_time: datetime = Field(index=True)
    end_time: datetime = Field(index=True)
    status: ReservationStatus = Field(default=ReservationStatus.PENDING, index=True)
    special_requests: Optional[str] = Field(default=None, max_length=1000)
    created_at: datetime = Field(
        default_factory=func.now,
        sa_column=Column(DateTime(timezone=True), server_default=func.now()),
    )
    updated_at: datetime = Field(
        default_factory=func.now,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )

    # Composite index for efficient overbooking detection queries
    __table_args__ = (
        Index("idx_table_status_times", "table_id", "status", "start_time", "end_time"),
    )

    model_config = ConfigDict(from_attributes=True)

    def overlaps_with(self, other: "Reservation") -> bool:
        """
        Check if this reservation overlaps with another reservation.
        
        Two reservations overlap if they share any time on the same table:
        - This reservation starts before the other ends, AND
        - This reservation ends after the other starts
        
        Args:
            other: Another Reservation instance to compare with
            
        Returns:
            True if reservations overlap, False otherwise
            
        Example:
            >>> res1 = Reservation(..., start_time=10:00, end_time=12:00)
            >>> res2 = Reservation(..., start_time=11:00, end_time=13:00)
            >>> res1.overlaps_with(res2)
            True
        """
        return self.start_time < other.end_time and self.end_time > other.start_time
