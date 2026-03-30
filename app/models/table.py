"""
Database models for table management.

Defines the Table SQLModel entity with all required fields and relationships.
"""

from datetime import datetime
from typing import Optional

from sqlmodel import Column, DateTime, Field, SQLModel, func, Index
from pydantic import ConfigDict

from app.core.constants import TableStatus


class Table(SQLModel, table=True):
    """
    Table entity representing a physical dining table in the restaurant.
    
    Each table has a unique display number (e.g., "T1", "T2"), a seating capacity,
    and a status indicating availability. Timestamps track creation and updates.
    
    Attributes:
        id: Unique table identifier (primary key)
        table_number: Unique display number for the table (e.g., "T1", "T2")
        capacity: Number of seats at this table (1-20 capacity range)
        status: Current table status (available, occupied, reserved, unavailable)
        created_at: Timestamp when the table was created (server-set)
        updated_at: Timestamp when the table was last updated (auto-updated)
    """
    
    __tablename__ = "tables"
    
    id: Optional[int] = Field(primary_key=True, index=True)
    table_number: str = Field(unique=True, index=True, min_length=1, max_length=50)
    capacity: int = Field(ge=1, le=20)
    status: TableStatus = Field(default=TableStatus.AVAILABLE, index=True)
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

    model_config = ConfigDict(from_attributes=True)
