"""
Table management endpoints.

API routes for CRUD operations on restaurant tables.
"""

from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException, status

from app.crud.table import TableRepository
from app.schemas.table import TableCreate, TableResponse, TableUpdate
from app.api.v1.dependencies import get_table_repository

router = APIRouter(prefix="/tables", tags=["tables"])


@router.post(
    "/",
    response_model=TableResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new table",
)
async def create_table(
    table_create: TableCreate,
    repository: TableRepository = Depends(get_table_repository),
) -> TableResponse:
    """
    Create a new table in the restaurant.
    
    Args:
        table_create: Table creation data
        repository: Table repository dependency
        
    Returns:
        Created table with ID and timestamps
        
    Raises:
        HTTPException: 400 if table_number already exists
    """
    try:
        table = await repository.create(table_create)
        return table
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{table_id}",
    response_model=TableResponse,
    summary="Get table by ID",
)
async def get_table(
    table_id: int,
    repository: TableRepository = Depends(get_table_repository),
) -> TableResponse:
    """
    Retrieve a table by ID.
    
    Args:
        table_id: Table identifier
        repository: Table repository dependency
        
    Returns:
        Table data
        
    Raises:
        HTTPException: 404 if table not found
    """
    table = await repository.get_by_id(table_id)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table {table_id} not found",
        )
    return table


@router.get(
    "/",
    response_model=Sequence[TableResponse],
    summary="List all tables",
)
async def list_tables(
    skip: int = 0,
    limit: int = 100,
    repository: TableRepository = Depends(get_table_repository),
) -> Sequence[TableResponse]:
    """
    List all tables with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        repository: Table repository dependency
        
    Returns:
        List of tables
    """
    tables = await repository.get_all(skip=skip, limit=limit)
    return tables


@router.patch(
    "/{table_id}",
    response_model=TableResponse,
    summary="Update a table",
)
async def update_table(
    table_id: int,
    table_update: TableUpdate,
    repository: TableRepository = Depends(get_table_repository),
) -> TableResponse:
    """
    Update an existing table.
    
    Args:
        table_id: Table identifier
        table_update: Fields to update
        repository: Table repository dependency
        
    Returns:
        Updated table data
        
    Raises:
        HTTPException: 404 if table not found, 400 if constraint violation
    """
    try:
        table = await repository.update(table_id, table_update)
        if not table:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Table {table_id} not found",
            )
        return table
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/{table_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a table",
)
async def delete_table(
    table_id: int,
    repository: TableRepository = Depends(get_table_repository),
) -> None:
    """
    Delete a table by ID.
    
    Args:
        table_id: Table identifier
        repository: Table repository dependency
        
    Raises:
        HTTPException: 404 if table not found, 409 if has active reservations
    """
    try:
        success = await repository.delete(table_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Table {table_id} not found",
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
