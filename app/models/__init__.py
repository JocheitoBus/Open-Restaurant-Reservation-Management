"""
Data models package.

Exports all SQLModel entities for easy importing.
"""

from app.models.reservation import Reservation
from app.models.table import Table

__all__ = ["Table", "Reservation"]
