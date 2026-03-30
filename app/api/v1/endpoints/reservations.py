"""
Reservation management endpoints.

API routes for CRUD operations on table reservations with overbooking prevention.
"""

from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException, status

from app.crud.reservation import ReservationRepository
from app.schemas.reservation import (
    ReservationCreate,
    ReservationResponse,
    ReservationUpdate,
)
from app.api.v1.dependencies import get_reservation_repository

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.post(
    "/",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new reservation",
)
async def create_reservation(
    reservation_create: ReservationCreate,
    repository: ReservationRepository = Depends(get_reservation_repository),
) -> ReservationResponse:
    """
    Create a new table reservation.
    
    Validates that the requested time slot is available and does not overlap
    with existing reservations on the same table.
    
    Args:
        reservation_create: Reservation creation data
        repository: Reservation repository dependency
        
    Returns:
        Created reservation with ID and timestamps
        
    Raises:
        HTTPException: 409 if table has overlapping reservations
    """
    try:
        reservation = await repository.create(reservation_create)
        return reservation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get(
    "/{reservation_id}",
    response_model=ReservationResponse,
    summary="Get reservation by ID",
)
async def get_reservation(
    reservation_id: int,
    repository: ReservationRepository = Depends(get_reservation_repository),
) -> ReservationResponse:
    """
    Retrieve a reservation by ID.
    
    Args:
        reservation_id: Reservation identifier
        repository: Reservation repository dependency
        
    Returns:
        Reservation data
        
    Raises:
        HTTPException: 404 if reservation not found
    """
    reservation = await repository.get_by_id(reservation_id)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservation {reservation_id} not found",
        )
    return reservation


@router.get(
    "/",
    response_model=Sequence[ReservationResponse],
    summary="List all reservations",
)
async def list_reservations(
    skip: int = 0,
    limit: int = 100,
    repository: ReservationRepository = Depends(get_reservation_repository),
) -> Sequence[ReservationResponse]:
    """
    List all reservations with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        repository: Reservation repository dependency
        
    Returns:
        List of reservations
    """
    reservations = await repository.get_all(skip=skip, limit=limit)
    return reservations


@router.patch(
    "/{reservation_id}",
    response_model=ReservationResponse,
    summary="Update a reservation",
)
async def update_reservation(
    reservation_id: int,
    reservation_update: ReservationUpdate,
    repository: ReservationRepository = Depends(get_reservation_repository),
) -> ReservationResponse:
    """
    Update an existing reservation.
    
    If updating time fields, validates that the new time slot does not conflict
    with other reservations on the same table.
    
    Args:
        reservation_id: Reservation identifier
        reservation_update: Fields to update
        repository: Reservation repository dependency
        
    Returns:
        Updated reservation data
        
    Raises:
        HTTPException: 404 if reservation not found
        HTTPException: 409 if updated time conflicts with existing reservations
    """
    try:
        reservation = await repository.update(reservation_id, reservation_update)
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reservation {reservation_id} not found",
            )
        return reservation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.delete(
    "/{reservation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a reservation",
)
async def delete_reservation(
    reservation_id: int,
    repository: ReservationRepository = Depends(get_reservation_repository),
) -> None:
    """
    Delete a reservation by ID (hard delete).
    
    Args:
        reservation_id: Reservation identifier
        repository: Reservation repository dependency
        
    Raises:
        HTTPException: 404 if reservation not found
    """
    try:
        success = await repository.delete(reservation_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reservation {reservation_id} not found",
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/{reservation_id}/cancel",
    response_model=ReservationResponse,
    summary="Cancel a reservation",
)
async def cancel_reservation(
    reservation_id: int,
    repository: ReservationRepository = Depends(get_reservation_repository),
) -> ReservationResponse:
    """
    Cancel a reservation (soft delete by setting status to CANCELLED).
    
    Cancelled reservations remain in the database for audit purposes.
    
    Args:
        reservation_id: Reservation identifier
        repository: Reservation repository dependency
        
    Returns:
        Cancelled reservation data
        
    Raises:
        HTTPException: 404 if reservation not found
    """
    try:
        reservation = await repository.cancel(reservation_id)
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Reservation {reservation_id} not found",
            )
        return reservation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
