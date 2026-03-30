"""
Integration tests for Reservation API endpoints.
"""

from datetime import datetime, timedelta
import pytest
from fastapi.testclient import TestClient

from main import app
from app.api.v1.dependencies import get_reservation_repository, get_table_repository
from app.crud.reservation import ReservationRepository
from app.crud.table import TableRepository
from app.schemas.table import TableCreate
from app.core.constants import ReservationStatus


@pytest.fixture
def client_with_table(session):
    """Create test client with setup table."""
    def override_get_reservation_repository():
        return ReservationRepository(session)
    
    def override_get_table_repository():
        return TableRepository(session)
    
    app.dependency_overrides[get_reservation_repository] = override_get_reservation_repository
    app.dependency_overrides[get_table_repository] = override_get_table_repository
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


class TestReservationEndpoints:
    """Test suite for reservation management endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_reservation_success(self, client_with_table, session):
        """Test successful reservation creation."""
        # Create a table first
        table_repo = TableRepository(session)
        table = await table_repo.create(TableCreate(table_number="T-RES1", capacity=4))
        
        now = datetime.now()
        response = client_with_table.post(
            "/api/v1/reservations/",
            json={
                "table_id": table.id,
                "customer_name": "John Doe",
                "party_size": 2,
                "start_time": now.isoformat(),
                "end_time": (now + timedelta(hours=2)).isoformat(),
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["customer_name"] == "John Doe"
        assert data["status"] == "pending"
    
    @pytest.mark.asyncio
    async def test_create_overlapping_reservation(self, client_with_table, session):
        """Test that overlapping reservations are rejected."""
        table_repo = TableRepository(session)
        table = await table_repo.create(TableCreate(table_number="T-RES2", capacity=4))
        
        now = datetime.now()
        
        # Create first reservation
        client_with_table.post(
            "/api/v1/reservations/",
            json={
                "table_id": table.id,
                "customer_name": "Alice",
                "party_size": 2,
                "start_time": now.isoformat(),
                "end_time": (now + timedelta(hours=2)).isoformat(),
            }
        )
        
        # Try to create overlapping
        response = client_with_table.post(
            "/api/v1/reservations/",
            json={
                "table_id": table.id,
                "customer_name": "Bob",
                "party_size": 2,
                "start_time": (now + timedelta(hours=1)).isoformat(),
                "end_time": (now + timedelta(hours=3)).isoformat(),
            }
        )
        
        assert response.status_code == 409
        assert "overlap" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_get_reservation_success(self, client_with_table, session):
        """Test getting a reservation by ID."""
        table_repo = TableRepository(session)
        res_repo = ReservationRepository(session)
        
        table = await table_repo.create(TableCreate(table_number="T-RES3", capacity=4))
        now = datetime.now()
        
        from app.schemas.reservation import ReservationCreate
        res = await res_repo.create(ReservationCreate(
            table_id=table.id,
            customer_name="Charlie",
            party_size=3,
            start_time=now,
            end_time=now + timedelta(hours=1),
        ))
        
        response = client_with_table.get(f"/api/v1/reservations/{res.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["customer_name"] == "Charlie"
    
    @pytest.mark.asyncio
    async def test_cancel_reservation(self, client_with_table, session):
        """Test cancelling a reservation."""
        table_repo = TableRepository(session)
        res_repo = ReservationRepository(session)
        
        table = await table_repo.create(TableCreate(table_number="T-RES4", capacity=4))
        now = datetime.now()
        
        from app.schemas.reservation import ReservationCreate
        res = await res_repo.create(ReservationCreate(
            table_id=table.id,
            customer_name="Diana",
            party_size=2,
            start_time=now,
            end_time=now + timedelta(hours=2),
        ))
        
        response = client_with_table.post(f"/api/v1/reservations/{res.id}/cancel")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"
    
    @pytest.mark.asyncio
    async def test_list_reservations(self, client_with_table, session):
        """Test listing all reservations."""
        response = client_with_table.get("/api/v1/reservations/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
