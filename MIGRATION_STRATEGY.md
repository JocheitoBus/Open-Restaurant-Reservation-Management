# Database Migration Strategy

## Development Environment

**Current Approach**: `create_all()` via `init_db()` during app startup

**Advantages:**
- Fast iteration
- Simple schema management
- No migration files to maintain

**Disadvantages:**
- ❌ No version control for schema changes
- ❌ No rollback capability
- ❌ Not suitable for production

---

## Production Environment (Recommended)

### Use Alembic for Schema Versioning

**Installation:**
```bash
pip install alembic
```

**Initialization (one-time setup):**
```bash
alembic init migrations
```

**Configuration (migrations/env.py):**
```python
# Update env.py for async SQLAlchemy 2.0+ with SQLite/PostgreSQL

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

async def run_migrations_online():
    """Run migrations in 'online' mode."""
    config.set_main_option("sqlalchemy.url", settings.database_url)
    
    connectable = create_async_engine(
        settings.database_url,
        future=True,
        echo=settings.sql_echo,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(run_migrations)
```

### Workflow

1. **After model changes:**
   ```bash
   alembic revision --autogenerate -m "Add new_field to reservations table"
   ```

2. **Review generated migration** (`migrations/versions/xxxx_*.py`)

3. **Apply migration:**
   ```bash
   alembic upgrade head
   ```

4. **Rollback (if needed):**
   ```bash
   alembic downgrade -1
   ```

---

## Current Database Schema

### Tables (SQLite + aiosqlite)

**tables**
```sql
id INTEGER PRIMARY KEY
table_number VARCHAR(50) UNIQUE NOT NULL
capacity INTEGER (CHECK: 1-20)
status VARCHAR DEFAULT 'available' INDEXED
created_at DATETIME DEFAULT CURRENT_TIMESTAMP
updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
```

**reservations**
```sql
id INTEGER PRIMARY KEY
table_id INTEGER FOREIGN KEY REFERENCES tables(id)
customer_name VARCHAR(255) NOT NULL
party_size INTEGER (CHECK: 1-20)
start_time DATETIME INDEXED
end_time DATETIME INDEXED
status VARCHAR DEFAULT 'pending' INDEXED
special_requests VARCHAR(1000) nullable
created_at DATETIME DEFAULT CURRENT_TIMESTAMP
updated_at DATETIME DEFAULT CURRENT_TIMESTAMP

COMPOSITE INDEX: (table_id, status, start_time, end_time)
```

---

## Security Considerations

### Development
✅ SQLite in-memory or local file is acceptable

### Production
- ❌ **DO NOT** store SQLite files in version control
- ❌ **DO NOT** use SQLite for multi-server deployments
- ✅ **Recommended**: PostgreSQL with proper credentials via environment variables
- ✅ **Recommended**: Enable `ssl_mode=require` for database connections
- ✅ **Recommended**: Regular database backups (automated dumps)

### Connection String Format

**SQLite (Development):**
```
sqlite+aiosqlite:///reservation_system.db
```

**PostgreSQL (Production):**
```
postgresql+asyncpg://username:password@localhost:5432/reservation_system
```

**Never commit credentials to git!** Use `.env` files with `python-dotenv`.

---

## Checklist for Production Deployment

- [ ] Use PostgreSQL (or managed database service)
- [ ] Set up Alembic migration versioning
- [ ] Configure automated database backups
- [ ] Set up monitoring/alerts for database connections
- [ ] Document manual migration procedures
- [ ] Test rollback procedures
- [ ] Enable SSL for database connections
- [ ] Configure connection pooling for high concurrency
