"""
Unit tests for Reservation CRUD operations.
"""

from datetime import datetime, timedelta
import pytest
from app.crud.reservation import ReservationRepository
from app.crud.table import TableRepository
from app.models.reservation import Reservation
from app.schemas.reservation import ReservationCreate, ReservationUpdate
from app.schemas.table import TableCreate
from app.core.constants import ReservationStatus


@pytest.fixture
async def table_setup(session):
    """Create a test table."""
    repo = TableRepository(session)
    table = await repo.create(TableCreate(table_number="T-TEST", capacity=4))
    return table


@pytest.mark.asyncio
async def test_create_reservation(session, table_setup):
    """Test creating a new reservation."""
    repo = ReservationRepository(session)
    
    now = datetime.now()
    res_data = ReservationCreate(
        table_id=table_setup.id,
        customer_name="John Doe",
        party_size=2,
        start_time=now,
        end_time=now + timedelta(hours=2),
    )
    
    reservation = await repo.create(res_data)
    
    assert reservation.id is not None
    assert reservation.customer_name == "John Doe"
    assert reservation.party_size == 2
    assert reservation.status == ReservationStatus.PENDING


@pytest.mark.asyncio
async def test_overbooking_prevention(session, table_setup):
    """Test that overlapping reservations are prevented."""
    repo = ReservationRepository(session)
    
    now = datetime.now()
    
    # Create first reservation
    res1 = ReservationCreate(
        table_id=table_setup.id,
        customer_name="Alice",
        party_size=2,
        start_time=now,
        end_time=now + timedelta(hours=2),
    )
    await repo.create(res1)
    
    # Try to create overlapping reservation
    res2 = ReservationCreate(
        table_id=table_setup.id,
        customer_name="Bob",
        party_size=2,
        start_time=now + timedelta(hours=1),
        end_time=now + timedelta(hours=3),
    )
    
    with pytest.raises(ValueError, match="overlapping"):
        await repo.create(res2)


@pytest.mark.asyncio
async def test_non_overlapping_reservations(session, table_setup):
    """Test that non-overlapping reservations on same table are allowed."""
    repo = ReservationRepository(session)
    
    now = datetime.now()
    
    # First reservation
    res1 = ReservationCreate(
        table_id=table_setup.id,
        customer_name="Alice",
        party_size=2,
        start_time=now,
        end_time=now + timedelta(hours=2),
    )
    await repo.create(res1)
    
    # Second reservation after first ends (OK)
    res2 = ReservationCreate(
        table_id=table_setup.id,
        customer_name="Bob",
        party_size=2,
        start_time=now + timedelta(hours=2),
        end_time=now + timedelta(hours=4),
    )
    
    reservation = await repo.create(res2)
    assert reservation.customer_name == "Bob"


@pytest.mark.asyncio
async def test_get_reservation_by_id(session, table_setup):
    """Test retrieving a reservation by ID."""
    repo = ReservationRepository(session)
    
    now = datetime.now()
    res_data = ReservationCreate(
        table_id=table_setup.id,
        customer_name="Charlie",
        party_size=3,
        start_time=now,
        end_time=now + timedelta(hours=1),
    )
    
    created = await repo.create(res_data)
    retrieved = await repo.get_by_id(created.id)
    
    assert retrieved is not None
    assert retrieved.customer_name == "Charlie"


@pytest.mark.asyncio
async def test_update_reservation(session, table_setup):
    """Test updating a reservation."""
    repo = ReservationRepository(session)
    
    now = datetime.now()
    res_data = ReservationCreate(
        table_id=table_setup.id,
        customer_name="Diana",
        party_size=2,
        start_time=now,
        end_time=now + timedelta(hours=2),
    )
    
    created = await repo.create(res_data)
    updated = await repo.update(
        created.id,
        ReservationUpdate(special_requests="No onions please")
    )
    
    assert updated.special_requests == "No onions please"


@pytest.mark.asyncio
async def test_cancel_reservation(session, table_setup):
    """Test cancelling a reservation (soft delete)."""
    repo = ReservationRepository(session)
    
    now = datetime.now()
    res_data = ReservationCreate(
        table_id=table_setup.id,
        customer_name="Eve",
        party_size=1,
        start_time=now,
        end_time=now + timedelta(hours=1),
    )
    
    created = await repo.create(res_data)
    cancelled = await repo.cancel(created.id)
    
    assert cancelled.status == ReservationStatus.CANCELLED


@pytest.mark.asyncio
async def test_delete_reservation(session, table_setup):
    """Test deleting a reservation (hard delete)."""
    repo = ReservationRepository(session)
    
    now = datetime.now()
    res_data = ReservationCreate(
        table_id=table_setup.id,
        customer_name="Frank",
        party_size=2,
        start_time=now,
        end_time=now + timedelta(hours=1),
    )
    
    created = await repo.create(res_data)
    success = await repo.delete(created.id)
    
    assert success is True
    retrieved = await repo.get_by_id(created.id)
    assert retrieved is None
