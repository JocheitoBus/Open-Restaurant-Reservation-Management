"""
API schemas package.

Exports all Pydantic schemas for request/response validation.
"""

from app.schemas.reservation import (
    ReservationCreate,
    ReservationResponse,
    ReservationUpdate,
)
from app.schemas.table import TableCreate, TableResponse, TableUpdate

__all__ = [
    "TableCreate",
    "TableUpdate",
    "TableResponse",
    "ReservationCreate",
    "ReservationUpdate",
    "ReservationResponse",
]
