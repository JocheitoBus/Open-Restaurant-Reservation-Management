# 🍽️ Restaurant Reservation Management System

Production-ready API for managing restaurant table reservations with FastAPI, SQLModel, and async SQLAlchemy.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### Local Development

**1. Install dependencies:**
```bash
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

**2. Create `.env` file (optional):**
```bash
copy .env.example .env
```

**3. Run the server:**
```bash
.\venv\Scripts\python.exe main.py
```

**4. Access the API:**
- 📊 **Swagger UI**: http://127.0.0.1:8000/docs
- 📝 **ReDoc**: http://127.0.0.1:8000/redoc  
- 💚 **Health Check**: GET http://127.0.0.1:8000

---

## 🐳 Docker

### Run with Docker Compose

```bash
docker-compose up -d
```

The API will be available at `http://localhost:8000`

### Build Docker Image

```bash
docker build -t reservation-api:latest .
docker run -p 8000:8000 reservation-api:latest
```

---

## 📋 API Endpoints

### Tables
- `POST /api/v1/tables/` - Create a new table
- `GET /api/v1/tables/` - List all tables (paginated)
- `GET /api/v1/tables/{id}` - Get table by ID
- `PATCH /api/v1/tables/{id}` - Update table
- `DELETE /api/v1/tables/{id}` - Delete table

**Example:**
```bash
# Create table
curl -X POST "http://localhost:8000/api/v1/tables/" \
  -H "Content-Type: application/json" \
  -d '{"table_number": "T1", "capacity": 4}'

# List tables
curl "http://localhost:8000/api/v1/tables/"
```

### Reservations
- `POST /api/v1/reservations/` - Create reservation (prevents overbooking)
- `GET /api/v1/reservations/` - List all reservations (paginated)
- `GET /api/v1/reservations/{id}` - Get reservation by ID
- `PATCH /api/v1/reservations/{id}` - Update reservation
- `DELETE /api/v1/reservations/{id}` - Delete reservation (hard delete)
- `POST /api/v1/reservations/{id}/cancel` - Cancel reservation (soft delete)

**Example:**
```bash
# Create reservation
curl -X POST "http://localhost:8000/api/v1/reservations/" \
  -H "Content-Type: application/json" \
  -d '{
    "table_id": 1,
    "customer_name": "John Doe",
    "party_size": 4,
    "start_time": "2026-04-15T19:00:00",
    "end_time": "2026-04-15T21:00:00"
  }'

# Cancel reservation
curl -X POST "http://localhost:8000/api/v1/reservations/1/cancel"
```

---

## 🧪 Testing

### Run All Tests

```bash
.\venv\Scripts\python.exe -m pytest
```

### Run Specific Tests

```bash
# Unit tests only
.\venv\Scripts\python.exe -m pytest tests/unit/

# Integration tests only
.\venv\Scripts\python.exe -m pytest tests/integration/

# Single test file
.\venv\Scripts\python.exe -m pytest tests/unit/test_table_crud.py::test_create_table -v
```

### With Coverage

```bash
pip install pytest-cov
pytest --cov=app --cov-report=html
```

---

## 📁 Project Structure

```
├── app/
│   ├── api/v1/
│   │   ├── endpoints/          # Route handlers (tables, reservations)
│   │   └── dependencies.py     # Dependency injection
│   │
│   ├── core/
│   │   ├── config.py          # Settings from environment
│   │   ├── constants.py       # Enums (status, environment)
│   │   └── security.py        # API Key authentication
│   │
│   ├── crud/                  # Repository pattern (CRUD)
│   │   ├── table.py
│   │   └── reservation.py
│   │
│   ├── db/
│   │   ├── session.py         # Database engine & session
│   │   └── base.py            # SQLModel Base
│   │
│   ├── models/                # SQLModel DB models
│   │   ├── table.py
│   │   └── reservation.py
│   │
│   ├── schemas/               # Pydantic validation schemas
│   │   ├── table.py
│   │   └── reservation.py
│   │
│   └── __init__.py
│
├── tests/
│   ├── conftest.py           # Pytest fixtures
│   ├── unit/                 # Unit tests (CRUD)
│   ├── integration/          # Integration tests (endpoints)
│   └── e2e/                  # End-to-end tests
│
├── main.py                   # FastAPI app entry point
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
├── Dockerfile               # Container image
├── docker-compose.yml       # Multi-container setup
├── MIGRATION_STRATEGY.md    # Database migrations guide
└── README.md               # This file
```

---

## 🔒 Security

### Current Implementation
- ✅ Input validation via Pydantic
- ✅ SQL injection prevention (ORM)
- ✅ Comprehensive error handling
- ✅ Async-first design

### Configuration for Production
- [ ] Configure proper API Key in `.env`
- [ ] Enable HTTPS/TLS
- [ ] Use PostgreSQL (not SQLite)
- [ ] Implement rate limiting
- [ ] Add request logging
- [ ] Set up secrets manager

---

## 💾 Database

**Current**: SQLite with async driver (`aiosqlite`)

**Supported**:
- PostgreSQL (recommended for production)
- MySQL (with async driver)
- Other SQLAlchemy-compliant databases

**Schema**:

```sql
-- Tables
CREATE TABLE tables (
  id INTEGER PRIMARY KEY,
  table_number VARCHAR(50) UNIQUE NOT NULL INDEXED,
  capacity INTEGER CHECK(1-20),
  status VARCHAR INDEXED,
  created_at DATETIME DEFAULT NOW(),
  updated_at DATETIME DEFAULT NOW()
);

-- Reservations with overbooking prevention
CREATE TABLE reservations (
  id INTEGER PRIMARY KEY,
  table_id INTEGER FOREIGN KEY,
  customer_name VARCHAR(255),
  party_size INTEGER CHECK(1-20),
  start_time DATETIME INDEXED,
  end_time DATETIME INDEXED,
  status VARCHAR INDEXED,
  special_requests VARCHAR(1000),
  created_at DATETIME,
  updated_at DATETIME,
  
  -- Composite index for overbooking detection
  INDEX idx_table_status_times (table_id, status, start_time, end_time)
);
```

---

## ⚙️ Configuration

Environment variables (`.env`):

```bash
# Application
APP_NAME=Restaurant Reservation System
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=development
API_KEY=dev-api-key-change-in-production

# Database
DATABASE_URL=sqlite+aiosqlite:///reservation_system.db
SQL_ECHO=false

# API
API_V1_PREFIX=/api/v1

# Restaurant
RESTAURANT_HOURS_START=10
RESTAURANT_HOURS_END=22
```

---

## 📈 Key Features

### Overbooking Prevention
- ✅ Real-time overlap detection
- ✅ Database index optimization
- ✅ Prevents double-booking via business logic

### API Design
- ✅ RESTful endpoints
- ✅ Pagination support
- ✅ Proper HTTP status codes
- ✅ OpenAPI/Swagger documentation

### Data Validation
- ✅ Pydantic schemas (request/response)
- ✅ Type hints throughout
- ✅ Range constraints (capacity, party size: 1-20)
- ✅ Time validation (end_time > start_time)

### Error Handling
- ✅ 400 Bad Request (validation errors)
- ✅ 404 Not Found (missing resources)
- ✅ 409 Conflict (overbooking)
- ✅ 500 Internal Server Error (with logging)

---

## 📚 Documentation

- [Migration Strategy](MIGRATION_STRATEGY.md) - Database schema versioning
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLModel Guide](https://sqlmodel.tiangolo.com/)
- [Pydantic v2](https://docs.pyd antic.dev/)

---

## 🐛 Troubleshooting

**"ModuleNotFoundError: No module named 'aiosqlite'"**
```bash
.\venv\Scripts\python.exe -m pip install aiosqlite
```

**"Address already in use"**
```bash
# Change port
.\venv\Scripts\python.exe main.py --port 8001
```

**Tests failing due to database issues**
```bash
# Tests use in-memory SQLite, so this shouldn't happen
# If it does, try reinstalling dependencies
pip install -r requirements.txt --force-reinstall
```

---

## ✨ Status

✅ **Production Ready**
- Tested async architecture
- Comprehensive error handling
- Full API documentation
- Automated tests included

---

**Last Updated**: March 2026  
**Python**: 3.14.3  
**FastAPI**: 0.135.2  
**SQLModel**: 0.0.37
