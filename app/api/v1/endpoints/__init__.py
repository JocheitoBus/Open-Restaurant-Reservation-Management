"""
Endpoints package.

Exports all route modules.
"""

from app.api.v1.endpoints import reservations, tables

__all__ = ["tables", "reservations"]
