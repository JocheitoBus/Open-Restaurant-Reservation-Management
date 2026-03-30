---
description: "Generate FastAPI production-ready boilerplate with Clean Architecture for a dining reservation system"
name: "FastAPI Reservation System Boilerplate"
argument-hint: "Project name and core features (tables, reservations, etc.)"
agent: "agent"
---

# FastAPI Production Boilerplate Generator

Generate a professional **production-ready FastAPI project structure** following **Clean Architecture** principles with full type-hinting.

## Requirements Template

When invoking this prompt, provide:

1. **Project Context**: Restaurant reservation system, booking platform, etc.
2. **Core Features**: 
   - Table Management (id, table_number, capacity)
   - Availability Logic (opening/closing hours, table status)
   - Reservation Engine (id, table_id, customer_name, start_time, end_time, party_size, status)
3. **Technical Stack**:
   - Backend: **FastAPI** (async)
   - Database: **SQLite** with **SQLModel** (SQLAlchemy + Pydantic v2)
   - Configuration: **Pydantic-settings** for environment variables
   - Testing: **Pytest** (unit/integration) + **Playwright** (E2E)

## Output Structure

Generate:

✅ **Folder Structure** (Clean Architecture):
- `/app/core/` - Configuration, constants, dependencies
- `/app/db/` - Database connection setup
- `/app/models/` - SQLModel ORM entities
- `/app/schemas/` - Pydantic request/response schemas
- `/app/crud/` - Database Repository layer (Create, Read, Update, Delete)
- `/app/api/` - API routes (versioned endpoints)
- `/tests/` - Unit, integration, and E2E tests

✅ **Core Files**:
- `main.py` - FastAPI entry point with lifespan events
- `requirements.txt` - All dependencies with versions
- `app/db/session.py` - Async database connection and session management
- `app/core/config.py` - Environment configuration using Pydantic-settings
- `app/core/constants.py` - Business logic constants
- `pytest.ini` - Pytest configuration
- `.env.example` - Environment variables template

## Implementation Principles

- **Full Type-Hinting**: Every function, parameter, and return type
- **Async/Await**: All database and I/O operations
- **Dependency Injection**: FastAPI Depends() for loosely-coupled layers
- **Resource Management**: Context managers for DB sessions (lifespan)
- **Error Handling**: Custom exception handlers and validation
- **Extensibility**: Versioned API for future scaling
- **No Overbooking**: Constraint logic documented in reservation CRUD

## Key Business Logic Constraints

- Prevent overlapping reservations on the same table
- Respect restaurant opening/closing hours
- Track reservation status (pending, confirmed, completed, cancelled)
- Support partial day availability (time-based slots)

---

**Use this prompt when setting up a new FastAPI dining/booking system with SQLite and SQLModel.**
