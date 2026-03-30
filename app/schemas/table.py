"""
Pydantic schemas for table request/response validation.

Separates API contracts from database models using Pydantic v2.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.core.constants import TableStatus


class TableBase(BaseModel):
    """Base schema with common table fields."""
    
    table_number: str = Field(min_length=1, max_length=50)
    capacity: int = Field(ge=1, le=20)
    status: TableStatus = Field(default=TableStatus.AVAILABLE)


class TableCreate(TableBase):
    """Schema for creating a new table."""
    pass


class TableUpdate(BaseModel):
    """Schema for updating an existing table."""
    
    table_number: Optional[str] = Field(default=None, min_length=1, max_length=50)
    capacity: Optional[int] = Field(default=None, ge=1, le=20)
    status: Optional[TableStatus] = Field(default=None)


class TableResponse(TableBase):
    """Schema for table API responses."""
    
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
