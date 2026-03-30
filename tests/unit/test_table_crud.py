"""
Unit tests for Table CRUD operations.
"""

import pytest
from app.crud.table import TableRepository
from app.models.table import Table
from app.schemas.table import TableCreate, TableUpdate


@pytest.mark.asyncio
async def test_create_table(session):
    """Test creating a new table."""
    repo = TableRepository(session)
    
    table_data = TableCreate(
        table_number="T1",
        capacity=4,
    )
    
    table = await repo.create(table_data)
    
    assert table.id is not None
    assert table.table_number == "T1"
    assert table.capacity == 4
    assert table.status.value == "available"


@pytest.mark.asyncio
async def test_create_duplicate_table_number(session):
    """Test that duplicate table numbers are rejected."""
    repo = TableRepository(session)
    
    table_data = TableCreate(table_number="T1", capacity=4)
    await repo.create(table_data)
    
    with pytest.raises(ValueError, match="already exists"):
        await repo.create(table_data)


@pytest.mark.asyncio
async def test_get_table_by_id(session):
    """Test retrieving a table by ID."""
    repo = TableRepository(session)
    
    created = await repo.create(TableCreate(table_number="T2", capacity=2))
    retrieved = await repo.get_by_id(created.id)
    
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.table_number == "T2"


@pytest.mark.asyncio
async def test_get_nonexistent_table(session):
    """Test retrieving a non-existent table returns None."""
    repo = TableRepository(session)
    
    result = await repo.get_by_id(999)
    assert result is None


@pytest.mark.asyncio
async def test_get_table_by_number(session):
    """Test retrieving a table by table_number."""
    repo = TableRepository(session)
    
    await repo.create(TableCreate(table_number="T3", capacity=6))
    retrieved = await repo.get_by_number("T3")
    
    assert retrieved is not None
    assert retrieved.table_number == "T3"


@pytest.mark.asyncio
async def test_get_all_tables(session):
    """Test retrieving all tables with pagination."""
    repo = TableRepository(session)
    
    for i in range(5):
        await repo.create(TableCreate(table_number=f"T{i}", capacity=i + 2))
    
    tables = await repo.get_all(skip=0, limit=10)
    assert len(tables) == 5


@pytest.mark.asyncio
async def test_get_all_tables_pagination(session):
    """Test pagination in get_all."""
    repo = TableRepository(session)
    
    for i in range(10):
        await repo.create(TableCreate(table_number=f"T{i}", capacity=2))
    
    page1 = await repo.get_all(skip=0, limit=5)
    page2 = await repo.get_all(skip=5, limit=5)
    
    assert len(page1) == 5
    assert len(page2) == 5


@pytest.mark.asyncio
async def test_update_table(session):
    """Test updating a table."""
    repo = TableRepository(session)
    
    created = await repo.create(TableCreate(table_number="T4", capacity=4))
    updated = await repo.update(created.id, TableUpdate(capacity=6))
    
    assert updated is not None
    assert updated.capacity == 6
    assert updated.table_number == "T4"


@pytest.mark.asyncio
async def test_update_nonexistent_table(session):
    """Test updating a non-existent table returns None."""
    repo = TableRepository(session)
    
    result = await repo.update(999, TableUpdate(capacity=8))
    assert result is None


@pytest.mark.asyncio
async def test_delete_table(session):
    """Test deleting a table."""
    repo = TableRepository(session)
    
    created = await repo.create(TableCreate(table_number="T5", capacity=4))
    success = await repo.delete(created.id)
    
    assert success is True
    retrieved = await repo.get_by_id(created.id)
    assert retrieved is None


@pytest.mark.asyncio
async def test_delete_nonexistent_table(session):
    """Test deleting a non-existent table returns False."""
    repo = TableRepository(session)
    
    success = await repo.delete(999)
    assert success is False
