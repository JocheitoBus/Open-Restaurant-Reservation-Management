"""
Business logic constants for the Reservation System.

Defines reservation statuses, table capacities, and other immutable business rules.
"""

from enum import Enum


class ReservationStatus(str, Enum):
    """Enumeration of valid reservation statuses."""
    
    PENDING: str = "pending"
    CONFIRMED: str = "confirmed"
    COMPLETED: str = "completed"
    CANCELLED: str = "cancelled"


class TableStatus(str, Enum):
    """Enumeration of valid table statuses."""
    
    AVAILABLE: str = "available"
    OCCUPIED: str = "occupied"
    RESERVED: str = "reserved"
    UNAVAILABLE: str = "unavailable"


# Capacity constraints
MIN_TABLE_CAPACITY: int = 1
MAX_TABLE_CAPACITY: int = 12

# Reservation duration constraints (in minutes)
MIN_RESERVATION_DURATION: int = 30
MAX_RESERVATION_DURATION: int = 240  # 4 hours

# Party size validation
MIN_PARTY_SIZE: int = 1
MAX_PARTY_SIZE: int = 20

# Default values
DEFAULT_RESERVATION_DURATION_MINUTES: int = 120  # 2 hours
