"""
Integration tests for Table API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from main import app
from app.api.v1.dependencies import get_table_repository
from app.crud.table import TableRepository
from app.schemas.table import TableCreate


@pytest.fixture
def client(session):
    """Create a test client with dependency override."""
    def override_get_table_repository():
        return TableRepository(session)
    
    app.dependency_overrides[get_table_repository] = override_get_table_repository
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


class TestTableEndpoints:
    """Test suite for table management endpoints."""
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check endpoint."""
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
    
    @pytest.mark.asyncio
    async def test_create_table_success(self, client, session):
        """Test successful table creation."""
        repo = TableRepository(session)
        
        response = client.post(
            "/api/v1/tables/",
            json={"table_number": "T1", "capacity": 4}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["table_number"] == "T1"
        assert data["capacity"] == 4
    
    @pytest.mark.asyncio
    async def test_create_table_invalid_capacity(self, client):
        """Test table creation with invalid capacity."""
        response = client.post(
            "/api/v1/tables/",
            json={"table_number": "T2", "capacity": 25}  # Out of range
        )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_get_table_success(self, client, session):
        """Test getting a table by ID."""
        repo = TableRepository(session)
        table = await repo.create(TableCreate(table_number="T3", capacity=2))
        
        response = client.get(f"/api/v1/tables/{table.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["table_number"] == "T3"
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_table(self, client):
        """Test getting a non-existent table."""
        response = client.get("/api/v1/tables/999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_list_tables(self, client, session):
        """Test listing all tables."""
        repo = TableRepository(session)
        for i in range(3):
            await repo.create(TableCreate(table_number=f"T{i}", capacity=i + 2))
        
        response = client.get("/api/v1/tables/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3
    
    @pytest.mark.asyncio
    async def test_update_table_success(self, client, session):
        """Test updating a table."""
        repo = TableRepository(session)
        table = await repo.create(TableCreate(table_number="T4", capacity=4))
        
        response = client.patch(
            f"/api/v1/tables/{table.id}",
            json={"capacity": 6}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["capacity"] == 6
    
    @pytest.mark.asyncio
    async def test_delete_table_success(self, client, session):
        """Test deleting a table."""
        repo = TableRepository(session)
        table = await repo.create(TableCreate(table_number="T5", capacity=4))
        
        response = client.delete(f"/api/v1/tables/{table.id}")
        
        assert response.status_code == 204
