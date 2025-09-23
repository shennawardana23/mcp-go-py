# Database Migration Guide: Native SQL Migration Management

## What is our Migration System?

Our custom migration system provides database schema version control using native SQL scripts. It allows you to:

- **Version Control Your Database Schema**: Keep track of database schema changes over time
- **Generate and Run Migrations**: Create and apply native SQL migration scripts
- **Collaborative Development**: Share database schema changes with team members
- **Production Deployments**: Safely apply schema changes to production databases
- **Connection Pooling**: Efficient database connections using psycopg pooling

## Why Use Our Migration System?

### 1. Database Schema Versioning

```sql
-- Example: migrations/002_add_user_created_at.sql
-- Add created_at column to users table
ALTER TABLE users ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
```

Our system automatically tracks which migrations have been applied using the `schema_migrations` table.

### 2. Safe Database Evolution

- **Reversible Migrations**: Each migration can be rolled back
- **Transaction Safety**: Migrations run in transactions using psycopg
- **Environment-Specific**: Different environments can have different migration states
- **Branching Support**: Handle database schema changes in feature branches
- **Connection Pooling**: Efficient database connections for migrations

### 3. Team Collaboration

```bash
# Initialize migrations directory (one-time setup)
mkdir migrations

# Create a new migration script
cat > migrations/002_add_user_created_at.sql << 'EOF'
-- Add created_at column to users table
ALTER TABLE users ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
EOF

# Apply migrations to database
python -c "from mcp_pba_tunnel.data.project_manager import DatabaseManager; db = DatabaseManager(); db.run_migrations()"

# Check current migration status
python -c "from mcp_pba_tunnel.data.project_manager import DatabaseManager; db = DatabaseManager(); print('Migrations status checked')"

# Roll back last migration (manual process)
# Edit migration script to include rollback statements
```

## Migration System in This Project

### Configuration Structure

```
migrations/
├── 001_initial_schema.sql
├── 002_add_user_timestamps.sql
└── 003_add_indexes.sql

config/
└── mcp_config.json
```

### Integration with psycopg

```python
# In your application
from mcp_pba_tunnel.data.project_manager import DatabaseManager

def run_migrations():
    """Run database migrations"""
    db = DatabaseManager()
    db.run_migrations()

# Database initialization
def init_database():
    # Create all tables using native SQL
    db = DatabaseManager()
    db.run_migrations()

    # Run migrations
    run_migrations()
```

### Migration Workflow

1. **Development**: Design database schema changes
2. **Create**: Write SQL migration script in migrations/ directory
3. **Review**: Check and test migration script
4. **Test**: Apply migration to development database
5. **Deploy**: Include migration in deployment process

## Best Practices

### 1. Migration Strategy

- **One Change Per Migration**: Keep migrations focused and reversible
- **Data Migrations Separate**: Handle data transformations in separate migrations
- **Test Migrations**: Always test migrations on a copy of production data
- **Backup Before Deployment**: Always backup before running migrations in production

### 2. Migration File Structure

```sql
-- migrations/002_add_user_timestamps.sql
-- Add user timestamps

-- Up migration
ALTER TABLE users ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE users ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

-- Down migration (for rollback)
-- ALTER TABLE users DROP COLUMN updated_at;
-- ALTER TABLE users DROP COLUMN created_at;
```

### 3. Environment Configuration

```json
// config/mcp_config.json
{
  "database": {
    "url": "postgresql://user:password@localhost/mcp_prompts",
    "pool_min_size": 5,
    "pool_max_size": 20,
    "timeout": 30
  }
}
```

## Common Commands

```bash
# Initialize migrations directory
mkdir migrations

# Create initial migration
cat > migrations/001_initial_schema.sql << 'EOF'
-- Initial schema migration
CREATE TABLE schema_migrations (
    version VARCHAR(50) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);
EOF

# Create new migration
cat > migrations/002_add_user_table.sql << 'EOF'
-- Add user table
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
EOF

# Apply all pending migrations
python -c "from mcp_pba_tunnel.data.project_manager import DatabaseManager; db = DatabaseManager(); db.run_migrations()"

# Check migration status
python -c "from mcp_pba_tunnel.data.project_manager import DatabaseManager; db = DatabaseManager(); print('Migrations status checked')"
# Roll back migrations (manual process)
# Edit migration script to include rollback statements
# Re-run migrations to apply rollback

# Show pending migrations
# Check migrations/ directory for new .sql files
```

## Integration with FastAPI

### Automatic Migration on Startup

```python
from fastapi import FastAPI
from mcp_pba_tunnel.data.project_manager import DatabaseManager

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """Run database migrations on startup"""
    db = DatabaseManager()
    db.run_migrations()
```

### Health Check with Migration Status

```python
@app.get("/health/database")
async def database_health():
    """Check database health and migration status"""
    try:
        from mcp_pba_tunnel.data.project_manager import DatabaseManager
        db = DatabaseManager()

        # Check database connection
        # (Connection is managed through psycopg pool)

        return {
            "status": "healthy",
            "database": "psycopg native queries",
            "connection_pool": "active"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
```

## Advanced Features

### Branching Migrations

When working with feature branches:

```bash
# Create branch-specific migration
cat > migrations/003_feature_branch_changes.sql << 'EOF'
-- Feature branch changes
ALTER TABLE prompt_templates ADD COLUMN branch_name VARCHAR(100);
EOF

# Apply migrations for specific branch
python -c "from mcp_pba_tunnel.data.project_manager import DatabaseManager; db = DatabaseManager(); db.run_migrations()"
```

### Custom Migration Operations

```sql
-- migrations/003_add_user_status.sql
-- Add user status column
ALTER TABLE users ADD COLUMN status VARCHAR(20) DEFAULT 'active';

-- Create index for performance
CREATE INDEX ix_users_email ON users(email);

-- Update existing users
UPDATE users SET status = 'active' WHERE status IS NULL;
```

## Conclusion

Our native SQL migration system is essential for:

- **Database Schema Evolution**: Managing changes to your database schema over time
- **Team Collaboration**: Ensuring all team members have consistent database states
- **Production Safety**: Providing safe, reversible database schema changes
- **Development Workflow**: Integrating database changes into your development process
- **Connection Pooling**: Efficient database connections using psycopg pooling

In this MCP-PBA-TUNNEL project, our migration system manages database schema changes for prompt templates, usage tracking, memory entries, and AI configuration storage using native PostgreSQL queries.
