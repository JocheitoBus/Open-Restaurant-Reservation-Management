"""
Pydantic schemas for reservation request/response validation.

Separates API contracts from database models using Pydantic v2.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.constants import ReservationStatus


class ReservationBase(BaseModel):
    """Base schema with common reservation fields."""
    
    table_id: int = Field(ge=1)
    customer_name: str = Field(min_length=1, max_length=255)
    party_size: int = Field(ge=1, le=20)
    start_time: datetime
    end_time: datetime
    special_requests: Optional[str] = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def validate_time_range(self) -> "ReservationBase":
        """Validate that end_time is after start_time."""
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class ReservationCreate(ReservationBase):
    """Schema for creating a new reservation."""
    
    status: ReservationStatus = Field(default=ReservationStatus.PENDING)


class ReservationUpdate(BaseModel):
    """Schema for updating an existing reservation."""
    
    customer_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    party_size: Optional[int] = Field(default=None, ge=1, le=20)
    start_time: Optional[datetime] = Field(default=None)
    end_time: Optional[datetime] = Field(default=None)
    status: Optional[ReservationStatus] = Field(default=None)
    special_requests: Optional[str] = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def validate_time_range(self) -> "ReservationUpdate":
        """Validate that end_time is after start_time if both are provided."""
        if (
            self.start_time is not None
            and self.end_time is not None
            and self.end_time <= self.start_time
        ):
            raise ValueError("end_time must be after start_time")
        return self


class ReservationResponse(ReservationBase):
    """Schema for reservation API responses."""
    
    id: int
    status: ReservationStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
