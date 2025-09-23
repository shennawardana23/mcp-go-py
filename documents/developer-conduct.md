# 👨‍💻 Developer Conduct & Best Practices Guide

## 🎯 Welcome to MCP-PBA-TUNNEL

Welcome to the MCP-PBA-TUNNEL project! This document outlines the standards, practices, and guidelines that ensure consistent, high-quality development across the entire codebase. As a contributor, you're joining a team dedicated to building robust, maintainable, and scalable software solutions.

## 📋 Table of Contents

- [🎯 Welcome to MCP-PBA-TUNNEL](#-welcome-to-mcp-pba-tunnel)
- [📋 Table of Contents](#-table-of-contents)
- [🏗️ Project Structure](#-project-structure)
- [💻 Development Workflow](#-development-workflow)
- [📝 Code Standards](#-code-standards)
- [🧪 Testing Guidelines](#-testing-guidelines)
- [📚 Documentation Standards](#-documentation-standards)
- [🔧 Design Patterns & Architecture](#-design-patterns--architecture)
- [🛠️ Object-Oriented Programming](#-object-oriented-programming)
- [🔒 Security Considerations](#-security-considerations)
- [⚡ Performance Best Practices](#-performance-best-practices)
- [🗃️ Database Management](#-database-management)
- [🔄 Migration Management](#-migration-management)
- [🧠 Enhanced Memory System Development](#-enhanced-memory-system-development)
- [🛠️ Advanced Tools Development](#-advanced-tools-development)
- [🤝 Collaboration Guidelines](#-collaboration-guidelines)
- [📊 Code Review Process](#-code-review-process)
- [🚀 Deployment Guidelines](#-deployment-guidelines)
- [🔍 Troubleshooting](#-troubleshooting)
- [📞 Getting Help](#-getting-help)
- [🎯 Contributing Checklist](#-contributing-checklist)
- [📋 Appendices](#-appendices)

## 🏗️ Project Structure

### Core Architecture Overview

```mermaid
graph TB
    subgraph "Application Layer"
        A[FastAPI Server<br/>HTTP/REST API] --> B[Request Processing<br/>Validation & Routing]
        B --> C[Business Logic<br/>Template Management]
        C --> D[Data Layer<br/>Database Operations]
    end

    subgraph "Data Management"
        C --> E[SQLAlchemy ORM<br/>Database Models]
        E --> F[(SQLite/PostgreSQL<br/>Persistent Storage)]
        C --> G[Redis Cache<br/>Session Management]
    end

    subgraph "External Services"
        C --> H[AI Services<br/>OpenAI, Anthropic APIs]
        H --> I[External APIs<br/>Optional Integrations]
    end

    subgraph "Development Tools"
        J[Alembic<br/>Database Migrations] --> E
        K[Pytest<br/>Unit & Integration Tests] --> A
        L[Git<br/>Version Control] --> M[GitHub<br/>Code Repository]
    end
```

### Directory Structure

```
mcp-pba-tunnel/
├── server/                    # 🖥️ FastAPI Application
│   └── fastapi_mcp_server.py # Main server application
├── data/                      # 🗃️ Data Management Layer
│   ├── project_manager.py    # Database models & business logic
│   ├── patterns.py           # Design pattern implementations
│   └── config.json           # Data layer configuration
├── config/                    # ⚙️ Application Configuration
│   └── mcp_config.json       # Server settings & AI configs
├── mcp/                       # 🔗 MCP Protocol Integration
│   └── mcp_config.json       # MCP client configurations
├── documents/                 # 📚 Documentation
│   ├── README.md             # Documentation index
│   ├── user-guide.md         # Getting started guide
│   ├── architecture.md       # System architecture
│   ├── flow-control.md       # Request processing analysis
│   ├── data-lineage.md       # Data transformation tracing
│   ├── component-structure.md# Component architecture
│   ├── design-patterns.md    # Design pattern implementations
│   ├── alembic-guide.md      # Database migration guide
│   └── developer-conduct.md  # This document
├── tests/                     # 🧪 Test Suite
│   └── test_mcp_server.py    # Unit & integration tests
├── alembic/                   # 🗃️ Database Migrations
│   ├── env.py               # Migration environment
│   ├── script.py.mako       # Migration template
│   └── versions/            # Migration files
├── pyproject.toml            # 📦 Python Project Configuration
├── requirements.txt          # 📋 Dependencies
├── setup.py                  # 🔧 Installation Script
├── Makefile                  # 🛠️ Build Automation
├── Dockerfile                # 🐳 Container Configuration
└── .gitignore               # 🚫 Git Ignore Rules
```

## 💻 Development Workflow

### 1. Environment Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/mcp-pba-tunnel.git
cd mcp-pba-tunnel

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
python3 -c "from data.project_manager import DatabaseManager; print('Database initialized')"

# 5. Start development server
python3 server/fastapi_mcp_server.py
```

### 2. Development Process

```mermaid
flowchart TD
    A[Feature Request<br/>or Bug Report] --> B[Issue Creation<br/>GitHub Issues]
    B --> C[Branch Creation<br/>git checkout -b feature/issue-name]
    C --> D[Implementation<br/>Code Development]
    D --> E[Testing<br/>Unit & Integration Tests]
    E --> F[Documentation<br/>Update README & Docs]
    F --> G[Pull Request<br/>GitHub PR]
    G --> H[Code Review<br/>Team Review]
    H --> I[Approval & Merge<br/>Main Branch]
    I --> J[Deployment<br/>Production Release]
```

### 3. Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name
git checkout -b hotfix/bug-fix-name
git checkout -b release/version-number

# Development workflow
git add .
git commit -m "feat: add new template category"
git commit -m "fix: resolve memory leak in cache"
git commit -m "docs: update API documentation"

# Push and create PR
git push origin feature/your-feature-name
# Create Pull Request on GitHub
```

### 4. Commit Message Standards

```bash
# Format: type(scope): description
# Types: feat, fix, docs, style, refactor, test, chore
git commit -m "feat: add new prompt template category"
git commit -m "fix: resolve database connection issue"
git commit -m "docs: update API documentation"
git commit -m "refactor: optimize database queries"
git commit -m "test: add unit tests for template rendering"
```

## 📝 Code Standards

### 1. Python Code Style

```python
# ✅ Good: Descriptive variable names
class PromptTemplateManager:
    def __init__(self, database_url: str) -> None:
        self.database_connection = create_engine(database_url)
        self.template_cache: Dict[str, Any] = {}
        self.usage_statistics = defaultdict(int)

# ❌ Bad: Short, unclear names
class PTM:
    def __init__(self, db: str) -> None:
        self.db = create_engine(db)
        self.tc = {}
        self.us = defaultdict(int)

# ✅ Good: Type hints and docstrings
def render_template(
    template_name: str,
    variables: Dict[str, Any],
    user_context: Optional[str] = None
) -> str:
    """
    Render a prompt template with given variables.

    Args:
        template_name: Name of the template to render
        variables: Dictionary of variables to substitute
        user_context: Optional user context for personalization

    Returns:
        Rendered template string

    Raises:
        TemplateNotFoundError: When template doesn't exist
        ValidationError: When variables are invalid
    """
    pass
```

### 2. Error Handling

```python
# ✅ Good: Comprehensive error handling
class TemplateManager:
    def get_template(self, template_name: str) -> PromptTemplate:
        """Retrieve template by name with proper error handling"""
        try:
            template = self._load_from_cache(template_name)
            if not template:
                template = self._load_from_database(template_name)

            if not template:
                raise TemplateNotFoundError(
                    f"Template '{template_name}' not found"
                )

            return template

        except DatabaseConnectionError as e:
            logger.error(f"Database error loading template: {e}")
            raise TemplateServiceError("Template service unavailable")
        except ValidationError as e:
            logger.error(f"Template validation failed: {e}")
            raise TemplateProcessingError("Invalid template data")
        except Exception as e:
            logger.critical(f"Unexpected error in template service: {e}")
            raise TemplateServiceError("Internal service error")

# ❌ Bad: No error handling
def get_template(name):
    return self.templates[name]
```

### 3. Import Organization

```python
# ✅ Good: Organized imports
# Standard library imports
import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# Third-party imports
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine
from pydantic import BaseModel

# Local imports
from data.project_manager import DatabaseManager
from config.settings import get_config
from utils.logging import setup_logger
```

## 🧪 Testing Guidelines

### 1. Test Structure

```mermaid
graph TD
    A[Unit Tests<br/>Individual Functions] --> B[Integration Tests<br/>Component Interaction]
    B --> C[System Tests<br/>End-to-End Flows]
    C --> D[Performance Tests<br/>Load & Stress Testing]
    D --> E[Acceptance Tests<br/>User Scenario Testing]

    A --> F[Test Coverage<br/>80%+ Requirement]
    F --> G[Quality Gates<br/>CI/CD Integration]
```

### 2. Test Examples

```python
# ✅ Good: Comprehensive unit test
def test_template_rendering():
    """Test template rendering with various scenarios"""
    template_manager = TemplateManager()

    # Test successful rendering
    result = template_manager.render_template(
        "business_logic",
        {"domain": "e-commerce", "type": "API"}
    )
    assert "e-commerce" in result
    assert "API" in result

    # Test error handling
    with pytest.raises(TemplateNotFoundError):
        template_manager.render_template("nonexistent", {})

    # Test edge cases
    edge_result = template_manager.render_template(
        "business_logic",
        {"domain": "", "type": None}
    )
    assert edge_result is not None

# ✅ Good: Integration test
def test_template_api_integration():
    """Test template API endpoints"""
    client = TestClient(app)

    # Test successful API call
    response = client.post(
        "/api/prompts/business_logic/render",
        json={"variables": {"domain": "e-commerce"}}
    )
    assert response.status_code == 200
    assert "e-commerce" in response.json()["content"]

    # Test error handling
    error_response = client.post(
        "/api/prompts/nonexistent/render",
        json={}
    )
    assert error_response.status_code == 404
```

### 3. Test Coverage Requirements

- **Core Business Logic**: 90%+ coverage
- **API Endpoints**: 85%+ coverage
- **Data Layer**: 95%+ coverage
- **Error Handling**: 100% coverage
- **Edge Cases**: Comprehensive testing

## 📚 Documentation Standards

### 1. Docstring Format

```python
def create_prompt_template(
    self,
    name: str,
    description: str,
    category: str,
    template_content: str,
    variables: List[str]
) -> str:
    """
    Create a new prompt template.

    This method creates and stores a new prompt template in the database,
    performing validation and ensuring uniqueness of template names.

    Args:
        name: Unique identifier for the template
        description: Human-readable description of the template's purpose
        category: Classification category (development, architecture, etc.)
        template_content: The actual template text with {{variable}} placeholders
        variables: List of variable names used in the template

    Returns:
        The ID of the created template

    Raises:
        ValidationError: If template data is invalid
        DuplicateTemplateError: If template name already exists
        DatabaseError: If database operation fails

    Example:
        >>> manager = TemplateManager()
        >>> template_id = manager.create_prompt_template(
        ...     name="api_design",
        ...     description="REST API design template",
        ...     category="architecture",
        ...     template_content="Design API for {{resource}} with {{operations}}",
        ...     variables=["resource", "operations"]
        ... )
        >>> print(template_id)
        'uuid-12345-abcde'
    """
    pass
```

### 2. Documentation Updates

- **API Changes**: Update OpenAPI/Swagger documentation
- **New Features**: Add examples and usage guides
- **Bug Fixes**: Document resolved issues
- **Architecture Changes**: Update architectural diagrams

## 🔧 Design Patterns & Architecture

### 1. Implemented Patterns

```mermaid
graph TD
    subgraph "Creational Patterns"
        A[Factory Pattern<br/>Template Creation] --> B[Singleton Pattern<br/>Cache Management]
        A --> C[Builder Pattern<br/>Complex Prompts]
    end

    subgraph "Structural Patterns"
        D[Decorator Pattern<br/>Template Enhancement] --> E[Adapter Pattern<br/>Interface Conversion]
        D --> F[Facade Pattern<br/>Simplified Interface]
    end

    subgraph "Behavioral Patterns"
        G[Observer Pattern<br/>Event Notifications] --> H[Command Pattern<br/>Operations]
        G --> I[Chain of Responsibility<br/>Request Processing]
    end

    subgraph "Enterprise Patterns"
        J[Context Manager<br/>Resource Management] --> K[Service Layer<br/>Business Logic]
    end
```

### 2. Architecture Principles

- **SOLID Principles**: Single responsibility, Open-closed, Liskov substitution
- **DRY (Don't Repeat Yourself)**: Eliminate code duplication
- **KISS (Keep It Simple, Stupid)**: Simple, maintainable solutions
- **YAGNI (You Aren't Gonna Need It)**: Only implement what's needed

### 3. Layered Architecture

```python
# Presentation Layer (FastAPI)
@app.post("/api/prompts/{name}/render")
async def render_prompt(name: str, variables: Dict[str, Any]):
    """HTTP endpoint for template rendering"""
    pass

# Business Logic Layer (Template Manager)
class TemplateManager:
    """Business logic for template operations"""
    def render_template(self, name: str, variables: Dict[str, Any]) -> str:
        pass

# Data Access Layer (Database Manager)
class DatabaseManager:
    """Data persistence and retrieval"""
    def get_template(self, name: str) -> PromptTemplate:
        pass
```

## 🛠️ Object-Oriented Programming

### 1. Class Design Principles

```python
# ✅ Good: Well-designed class
class PromptTemplateManager:
    """Manages prompt template operations with proper encapsulation"""

    def __init__(self, database_manager: DatabaseManager):
        self._database_manager = database_manager
        self._cache: Dict[str, PromptTemplate] = {}
        self._observers: List[Observer] = []

    def get_template(self, name: str) -> PromptTemplate:
        """Retrieve template with caching"""
        if name not in self._cache:
            template = self._database_manager.get_template(name)
            self._cache[name] = template
            self._notify_observers(f"template_loaded_{name}")
        return self._cache[name]

    def _notify_observers(self, event: str):
        """Notify all observers of events"""
        for observer in self._observers:
            observer.update(event)

# ❌ Bad: Poorly designed class
class BadTemplateManager:
    def __init__(self):
        pass

    def do_everything(self, data):
        # This method does too much - violates SRP
        pass
```

### 2. Inheritance vs Composition

```python
# ✅ Good: Composition over inheritance
class TemplateService:
    """Service layer using composition"""

    def __init__(
        self,
        template_manager: TemplateManager,
        cache_manager: CacheManager,
        ai_service: Optional[AIService] = None
    ):
        self.template_manager = template_manager
        self.cache_manager = cache_manager
        self.ai_service = ai_service

    def render_enhanced_template(
        self,
        template_name: str,
        variables: Dict[str, Any]
    ) -> str:
        """Render template with optional AI enhancement"""
        template = self.template_manager.get_template(template_name)
        rendered = template.render(variables)

        if self.ai_service:
            rendered = self.ai_service.enhance(rendered)

        return rendered

# ❌ Bad: Excessive inheritance
class TemplateManager(Validator, Cacher, DatabaseConnector, AIEnhancer):
    """Too many responsibilities"""
    pass
```

### 3. Interface Design

```python
# ✅ Good: Clean interface design
class TemplateRepository(ABC):
    """Abstract interface for template storage"""

    @abstractmethod
    def get_template(self, name: str) -> PromptTemplate:
        """Retrieve template by name"""
        pass

    @abstractmethod
    def save_template(self, template: PromptTemplate) -> str:
        """Save template and return ID"""
        pass

    @abstractmethod
    def list_templates(self, category: str) -> List[PromptTemplate]:
        """List templates by category"""
        pass

class DatabaseTemplateRepository(TemplateRepository):
    """Concrete implementation using database"""

    def get_template(self, name: str) -> PromptTemplate:
        # Implementation
        pass
```

## 🔒 Security Considerations

### 1. Input Validation

```python
# ✅ Good: Comprehensive input validation
def validate_template_variables(
    variables: Dict[str, Any],
    allowed_variables: List[str]
) -> Dict[str, Any]:
    """Validate template variables against allowed list"""

    # Check for required variables
    missing_vars = set(allowed_variables) - set(variables.keys())
    if missing_vars:
        raise ValidationError(f"Missing required variables: {missing_vars}")

    # Check for unexpected variables
    extra_vars = set(variables.keys()) - set(allowed_variables)
    if extra_vars:
        raise ValidationError(f"Unexpected variables: {extra_vars}")

    # Sanitize variable values
    sanitized = {}
    for key, value in variables.items():
        if isinstance(value, str):
            sanitized[key] = self._sanitize_string(value)
        else:
            sanitized[key] = value

    return sanitized

def _sanitize_string(self, value: str) -> str:
    """Sanitize string input to prevent injection attacks"""
    # Remove potentially dangerous characters
    # Limit length to prevent DoS
    # Normalize unicode characters
    pass
```

### 2. Database Security

```python
# ✅ Good: Parameterized queries
def get_template_by_name(self, name: str) -> PromptTemplate:
    """Retrieve template using parameterized query"""

    with self.get_session() as session:
        statement = select(PromptTemplate).where(
            PromptTemplate.name == name,
            PromptTemplate.is_active == True
        )
        template = session.execute(statement).scalar_one_or_none()

        if not template:
            raise TemplateNotFoundError(f"Template '{name}' not found")

        return template

# ❌ Bad: String concatenation (SQL injection risk)
def bad_get_template(self, name: str):
    query = f"SELECT * FROM templates WHERE name = '{name}'"
    # This is vulnerable to SQL injection!
```

### 3. API Security

```python
# ✅ Good: Secure API endpoints
@app.post("/api/prompts/{template_name}/render")
async def render_template_secure(
    template_name: str,
    variables: Dict[str, Any],
    request: Request
):
    """Secure template rendering endpoint"""

    # Rate limiting
    client_ip = request.client.host
    if self.rate_limiter.is_rate_limited(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Input validation
    if not self.validator.is_valid_template_name(template_name):
        raise HTTPException(status_code=400, detail="Invalid template name")

    # Content type validation
    if not isinstance(variables, dict):
        raise HTTPException(status_code=400, detail="Variables must be a dictionary")

    # Size limits
    if len(str(variables)) > 10_000:  # 10KB limit
        raise HTTPException(status_code=413, detail="Variables too large")

    # Process request
    result = await self.template_manager.render_template(template_name, variables)

    # Log access for monitoring
    logger.info(f"Template rendered: {template_name} from {client_ip}")

    return result
```

## ⚡ Performance Best Practices

### 1. Database Optimization

```python
# ✅ Good: Optimized database queries
def get_templates_by_category(self, category: str) -> List[PromptTemplate]:
    """Efficiently retrieve templates with proper indexing"""

    with self.get_session() as session:
        # Use specific columns to reduce data transfer
        statement = (
            select(PromptTemplate.id, PromptTemplate.name, PromptTemplate.description)
            .where(PromptTemplate.category == category)
            .where(PromptTemplate.is_active == True)
            .order_by(PromptTemplate.name)
        )

        result = session.execute(statement)
        templates = [TemplateInfo(**row._asdict()) for row in result]

        return templates

# ❌ Bad: Inefficient query
def bad_get_templates(self, category: str):
    all_templates = session.query(PromptTemplate).all()  # Loads everything
    return [t for t in all_templates if t.category == category]  # Filters in Python
```

### 2. Caching Strategy

```python
# ✅ Good: Intelligent caching
class TemplateCache:
    """Multi-level caching for templates"""

    def __init__(self):
        self.memory_cache: Dict[str, Any] = {}  # Fast access
        self.redis_cache = RedisCache()  # Distributed cache
        self.cache_timestamps: Dict[str, datetime] = {}

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get template with cascading cache lookup"""

        # 1. Check memory cache first (fastest)
        if name in self.memory_cache:
            template, timestamp = self.memory_cache[name]
            if self._is_cache_valid(timestamp):
                return template

        # 2. Check Redis cache (distributed)
        cached = self.redis_cache.get(f"template:{name}")
        if cached:
            template = self._deserialize_template(cached)
            self.memory_cache[name] = (template, datetime.now())
            return template

        # 3. Load from database (slowest)
        template = self._load_from_database(name)
        if template:
            self.memory_cache[name] = (template, datetime.now())
            self.redis_cache.set(f"template:{name}", self._serialize_template(template))

        return template
```

### 3. Async Processing

```python
# ✅ Good: Proper async handling
@app.post("/api/prompts/render-async")
async def render_template_async(
    template_name: str,
    variables: Dict[str, Any]
) -> Dict[str, Any]:
    """Asynchronous template rendering"""

    # Start background processing
    task_id = await self.background_processor.start_task(
        template_name, variables
    )

    return {
        "task_id": task_id,
        "status": "processing",
        "message": "Template rendering started"
    }

# Check task status
@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get async task status"""

    status = await self.background_processor.get_task_status(task_id)

    return {
        "task_id": task_id,
        "status": status,
        "progress": "75%" if status == "processing" else "100%"
    }
```

## 🗃️ Database Management

### 1. Connection Management

```python
# ✅ Good: Proper connection pooling
class DatabaseManager:
    """Database operations with connection pooling"""

    def __init__(self, database_url: str):
        self.engine = create_engine(
            database_url,
            # Connection pool settings
            pool_size=20,           # Base pool size
            max_overflow=30,        # Additional connections
            pool_timeout=30,        # Connection timeout
            pool_recycle=3600,      # Recycle connections
            # Performance settings
            echo=False,             # Disable SQL logging in production
            future=True,            # Use SQLAlchemy 2.0 style
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database transaction failed: {e}")
            raise
        finally:
            session.close()
```

### 2. Query Optimization

```python
# ✅ Good: Optimized queries with proper indexing
class TemplateRepository:
    """Optimized template database operations"""

    def get_templates_with_usage_stats(
        self,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get templates with usage statistics"""

        with self.get_session() as session:
            # Use JOIN to get related data in one query
            query = (
                session.query(
                    PromptTemplate,
                    func.count(PromptUsage.id).label('usage_count'),
                    func.avg(PromptUsage.avg_response_time).label('avg_time')
                )
                .outerjoin(PromptUsage)
                .group_by(PromptTemplate.id)
            )

            if category:
                query = query.filter(PromptTemplate.category == category)

            query = query.limit(limit)

            results = []
            for template, usage_count, avg_time in query:
                results.append({
                    'template': template,
                    'usage_count': usage_count or 0,
                    'avg_response_time': avg_time or 0
                })

            return results

    def bulk_update_usage_stats(
        self,
        template_updates: List[Dict[str, Any]]
    ) -> None:
        """Bulk update usage statistics for performance"""

        with self.get_session() as session:
            # Use bulk update instead of individual updates
            for update in template_updates:
                session.query(PromptUsage).filter(
                    PromptUsage.prompt_id == update['prompt_id']
                ).update({
                    'usage_count': PromptUsage.usage_count + update['increment'],
                    'last_used_at': datetime.utcnow()
                })

            session.commit()
```

## 🔄 Migration Management

### 1. Alembic Migration Structure

```mermaid
graph TD
    A[Alembic Configuration<br/>alembic.ini] --> B[Migration Environment<br/>env.py]
    B --> C[Migration Scripts<br/>versions/*.py]
    C --> D[Database Schema<br/>Current State]

    A --> E[Migration Commands<br/>alembic upgrade/downgrade]
    E --> F[Schema Changes<br/>Apply/Revert]
    F --> D
```

### 2. Migration Best Practices

```python
# ✅ Good: Well-structured migration
"""Add template metadata columns

Revision ID: 002_add_metadata
Revises: 001_initial_schema
Create Date: 2024-01-15 10:30:00.000000
"""

from alembic import op
import sqlalchemy as sa

def upgrade():
    """Add metadata columns to templates table"""
    op.add_column(
        'prompt_templates',
        sa.Column('created_by', sa.String(100), nullable=True)
    )
    op.add_column(
        'prompt_templates',
        sa.Column('last_modified_by', sa.String(100), nullable=True)
    )
    op.create_index(
        'ix_prompt_templates_created_by',
        'prompt_templates',
        ['created_by']
    )

def downgrade():
    """Remove metadata columns"""
    op.drop_index('ix_prompt_templates_created_by')
    op.drop_column('prompt_templates', 'last_modified_by')
    op.drop_column('prompt_templates', 'created_by')
```

### 3. Migration Commands

```bash
# Create new migration
alembic revision --autogenerate -m "Add user tracking"

# Apply migrations to database
alembic upgrade head

# Roll back last migration
alembic downgrade -1

# Check current migration status
alembic current

# Show migration history
alembic history

# Generate SQL without applying
alembic upgrade head --sql
```

## 🧠 Enhanced Memory System Development

### 1. Memory Context Architecture

The enhanced memory system provides sophisticated context management with relationships and importance scoring:

```mermaid
graph TB
    subgraph "Memory Context Management"
        A[Context Creation<br/>Conversation + Session] --> B[Importance Scoring<br/>Calculate Relevance]
        B --> C[Tag Processing<br/>Extract Categories]
        C --> D[Relationship Mapping<br/>Link Related Entries]
        D --> E[Context Storage<br/>Persistent Memory]
        E --> F[Context Retrieval<br/>Smart Querying]
    end

    subgraph "Memory Patterns"
        G[Conversation Memory<br/>Chat History] --> A
        H[Task Memory<br/>Project Context] --> A
        I[Reference Memory<br/>Knowledge Base] --> A
    end

    subgraph "Advanced Features"
        F --> J[Importance Filtering<br/>Relevance-Based Retrieval]
        F --> K[Relationship Queries<br/>Context Connections]
        F --> L[Tag-Based Search<br/>Categorized Access]
    end
```

### 2. Memory Development Guidelines

#### Context Relationship Management

```python
# ✅ Good: Proper context relationship handling
class EnhancedMemoryManager:
    """Manages enhanced memory with context relationships"""

    def __init__(self, repository: EnhancedMemoryRepository):
        self.repository = repository
        self.relationship_manager = ContextRelationshipManager()

    def store_context_entry(
        self,
        conversation_id: str,
        content: str,
        context_type: str = "conversation",
        importance_score: float = 0.5,
        tags: List[str] = None,
        relationships: List[str] = None
    ) -> str:
        """Store memory entry with context relationships"""

        # Validate inputs
        if not self._validate_content(content):
            raise ValidationError("Invalid memory content")

        # Calculate importance score if not provided
        if importance_score == 0.5:  # Default value
            importance_score = self._calculate_importance_score(content)

        # Extract tags from content
        if not tags:
            tags = self._extract_tags(content)

        # Create memory entry
        entry = EnhancedMemoryEntry(
            conversation_id=conversation_id,
            content=content,
            context_type=context_type,
            importance_score=importance_score,
            tags=tags or []
        )

        # Store entry
        entry_id = self.repository.create(entry)

        # Create relationships if provided
        if relationships:
            self._create_relationships(entry_id, relationships)

        return entry_id

    def _calculate_importance_score(self, content: str) -> float:
        """Calculate importance score based on content analysis"""
        # Implementation details...
        pass

    def _extract_tags(self, content: str) -> List[str]:
        """Extract relevant tags from content"""
        # Implementation details...
        pass

    def _create_relationships(self, entry_id: str, related_ids: List[str]):
        """Create relationships between memory entries"""
        for related_id in related_ids:
            relationship = ContextRelationship(
                from_entry_id=entry_id,
                to_entry_id=related_id,
                relationship_type="related_to"
            )
            self.relationship_manager.create_relationship(relationship)
```

#### Memory Query Patterns

```python
# ✅ Good: Context-aware memory retrieval
def retrieve_relevant_context(
    self,
    conversation_id: str,
    context_type: str = None,
    importance_threshold: float = 0.3,
    relationship_filter: str = None,
    limit: int = 10
) -> List[EnhancedMemoryEntry]:
    """Retrieve context-aware memory entries"""

    # Build query with filters
    query_filters = {
        "conversation_id": conversation_id,
        "importance_threshold": importance_threshold
    }

    if context_type:
        query_filters["context_type"] = context_type

    # Get base entries
    entries = self.repository.query_entries(**query_filters)

    # Apply relationship filtering
    if relationship_filter:
        entries = self._filter_by_relationships(entries, relationship_filter)

    # Sort by relevance and importance
    entries = self._sort_by_relevance(entries, conversation_id)

    return entries[:limit]

def _filter_by_relationships(
    self,
    entries: List[EnhancedMemoryEntry],
    relationship_filter: str
) -> List[EnhancedMemoryEntry]:
    """Filter entries based on relationship criteria"""
    # Implementation details...
    pass

def _sort_by_relevance(
    self,
    entries: List[EnhancedMemoryEntry],
    conversation_id: str
) -> List[EnhancedMemoryEntry]:
    """Sort entries by relevance to conversation context"""
    # Implementation details...
    pass
```

### 3. Memory Testing Guidelines

```python
# ✅ Good: Comprehensive memory system testing
def test_enhanced_memory_system():
    """Test enhanced memory system functionality"""

    # Test context creation
    memory_manager = EnhancedMemoryManager(repository)

    # Store context entry
    entry_id = memory_manager.store_context_entry(
        conversation_id="test_chat_123",
        content="How do I create a REST API?",
        context_type="conversation",
        importance_score=0.8,
        tags=["api", "development", "question"]
    )

    assert entry_id is not None
    assert len(entry_id) == 36  # UUID format

    # Test context retrieval
    entries = memory_manager.retrieve_relevant_context(
        conversation_id="test_chat_123",
        importance_threshold=0.5
    )

    assert len(entries) == 1
    assert entries[0].content == "How do I create a REST API?"
    assert entries[0].importance_score == 0.8

    # Test relationship filtering
    related_entries = memory_manager.retrieve_relevant_context(
        conversation_id="test_chat_123",
        relationship_filter="api_related"
    )

    # Verify filtering works correctly
    assert len(related_entries) >= 0

# ✅ Good: Context relationship testing
def test_memory_relationships():
    """Test memory relationship functionality"""

    # Create multiple related entries
    api_entry_id = memory_manager.store_context_entry(
        conversation_id="test_chat_123",
        content="REST API design principles",
        context_type="reference",
        tags=["api", "architecture"]
    )

    auth_entry_id = memory_manager.store_context_entry(
        conversation_id="test_chat_123",
        content="Authentication strategies",
        context_type="reference",
        tags=["auth", "security"],
        relationships=[api_entry_id]
    )

    # Retrieve related entries
    related_entries = memory_manager.retrieve_relevant_context(
        conversation_id="test_chat_123",
        relationship_filter="api_related"
    )

    # Verify relationships work
    assert len(related_entries) > 0
    assert auth_entry_id in [e.id for e in related_entries]
```

### 4. Memory Performance Optimization

```python
# ✅ Good: Memory query optimization
class OptimizedMemoryRepository(BaseRepository[EnhancedMemoryEntry]):
    """Optimized memory repository with indexing"""

    def __init__(self):
        super().__init__("enhanced_memory_entries")
        self._create_indexes()

    def _create_indexes(self):
        """Create performance indexes"""
        # Index for conversation-based queries
        self.execute_query("""
            CREATE INDEX IF NOT EXISTS ix_memory_conversation_importance
            ON enhanced_memory_entries (conversation_id, importance_score DESC)
        """)

        # Index for tag-based queries
        self.execute_query("""
            CREATE INDEX IF NOT EXISTS ix_memory_tags_gin
            ON enhanced_memory_entries USING GIN (tags)
        """)

        # Index for relationship queries
        self.execute_query("""
            CREATE INDEX IF NOT EXISTS ix_memory_relationships
            ON context_relationships (from_entry_id, to_entry_id)
        """)

    def query_by_importance_range(
        self,
        conversation_id: str,
        min_importance: float,
        max_importance: float
    ) -> List[EnhancedMemoryEntry]:
        """Query entries by importance range with optimized indexing"""
        query = """
        SELECT * FROM enhanced_memory_entries
        WHERE conversation_id = %s
        AND importance_score BETWEEN %s AND %s
        ORDER BY importance_score DESC
        """

        return self.execute_query(query, (conversation_id, min_importance, max_importance))

    def query_by_tags(self, tags: List[str]) -> List[EnhancedMemoryEntry]:
        """Query entries by tags using GIN index"""
        # Convert tags to PostgreSQL array syntax
        tag_array = "{" + ",".join(f'"{tag}"' for tag in tags) + "}"

        query = """
        SELECT * FROM enhanced_memory_entries
        WHERE tags @> %s::text[]
        ORDER BY importance_score DESC
        """

        return self.execute_query(query, (tag_array,))
```

## 🛠️ Advanced Tools Development

### 1. Tool Architecture Overview

The advanced tool ecosystem provides comprehensive development capabilities:

```mermaid
graph TB
    subgraph "Tool Categories"
        A[Web Scraping<br/>Data Collection] --> B[Code Analysis<br/>Quality Assessment]
        A --> C[Terminal Execution<br/>Command Processing]
        B --> D[Database Tools<br/>Schema Analysis]
        C --> E[Testing Tools<br/>Validation]
        D --> F[Project Management<br/>Task Tracking]
    end

    subgraph "Core Components"
        G[Tool Registry<br/>Tool Discovery] --> H[Execution Engine<br/>Safe Execution]
        H --> I[Security Manager<br/>Sandboxing]
        I --> J[Result Processor<br/>Output Handling]
        J --> K[Context Integration<br/>Memory Updates]
    end

    subgraph "Integration Points"
        G --> L[MCP Protocol<br/>Tool Interface]
        H --> M[AI Enhancement<br/>Optional Processing]
        J --> N[Memory System<br/>Context Storage]
    end
```

### 2. Tool Development Standards

#### Web Scraping Tools

```python
# ✅ Good: Secure and robust web scraping
class WebScrapingTool:
    """Secure web scraping with rate limiting and error handling"""

    def __init__(self, rate_limiter: RateLimiter, cache_manager: CacheManager):
        self.rate_limiter = rate_limiter
        self.cache_manager = cache_manager
        self.session = self._create_secure_session()

    def _create_secure_session(self) -> requests.Session:
        """Create secure HTTP session with proper headers"""
        session = requests.Session()

        # Security headers
        session.headers.update({
            'User-Agent': 'MCP-PBA-TUNNEL/1.0 (Research Bot)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

        # Timeout settings
        session.timeout = 30

        return session

    def scrape_webpage(
        self,
        url: str,
        extract_selectors: Dict[str, str] = None,
        output_format: str = "json"
    ) -> Dict[str, Any]:
        """Scrape webpage with security and caching"""

        # Rate limiting
        if not self.rate_limiter.check_limit(url):
            raise RateLimitError(f"Rate limit exceeded for {url}")

        # Check cache first
        cache_key = f"scrape_{hash(url)}"
        cached_result = self.cache_manager.get(cache_key)
        if cached_result:
            return cached_result

        try:
            # Validate URL
            if not self._validate_url(url):
                raise ValidationError(f"Invalid URL: {url}")

            # Make request
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Parse content
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract data
            extracted_data = {}
            if extract_selectors:
                for key, selector in extract_selectors.items():
                    elements = soup.select(selector)
                    extracted_data[key] = [elem.get_text().strip() for elem in elements]

            # Format output
            result = {
                "url": url,
                "status_code": response.status_code,
                "content_length": len(response.content),
                "extracted_data": extracted_data,
                "scraped_at": datetime.utcnow().isoformat()
            }

            # Cache result
            self.cache_manager.set(cache_key, result, ttl=3600)  # 1 hour

            return result

        except requests.RequestException as e:
            raise ScrapingError(f"Failed to scrape {url}: {str(e)}")
        except Exception as e:
            raise ScrapingError(f"Unexpected error scraping {url}: {str(e)}")

    def _validate_url(self, url: str) -> bool:
        """Validate URL for security"""
        try:
            parsed = urlparse(url)
            # Only allow HTTP/HTTPS
            if parsed.scheme not in ['http', 'https']:
                return False
            # Check for suspicious patterns
            if 'javascript:' in url.lower() or 'data:' in url.lower():
                return False
            return True
        except Exception:
            return False
```

#### Code Analysis Tools

```python
# ✅ Good: Comprehensive code analysis
class CodeAnalysisTool:
    """Comprehensive code analysis with multiple metrics"""

    def __init__(self, complexity_analyzer: ComplexityAnalyzer):
        self.complexity_analyzer = complexity_analyzer
        self.metrics_calculators = {
            'cyclomatic_complexity': self._calculate_cyclomatic_complexity,
            'maintainability_index': self._calculate_maintainability_index,
            'lines_of_code': self._count_lines_of_code,
            'code_duplication': self._detect_duplication,
            'security_issues': self._scan_security_issues
        }

    def analyze_codebase(
        self,
        file_path: str,
        analysis_types: List[str] = None,
        output_format: str = "detailed"
    ) -> Dict[str, Any]:
        """Analyze codebase with multiple metrics"""

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Code file not found: {file_path}")

        # Default to all analysis types
        if not analysis_types:
            analysis_types = list(self.metrics_calculators.keys())

        # Read and parse code
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
        except UnicodeDecodeError:
            # Try different encodings
            with open(file_path, 'r', encoding='latin-1') as f:
                code_content = f.read()

        # Analyze code
        analysis_results = {}
        for analysis_type in analysis_types:
            if analysis_type in self.metrics_calculators:
                try:
                    result = self.metrics_calculators[analysis_type](code_content, file_path)
                    analysis_results[analysis_type] = result
                except Exception as e:
                    analysis_results[analysis_type] = {
                        "error": str(e),
                        "status": "failed"
                    }

        # Generate summary
        summary = self._generate_analysis_summary(analysis_results)

        # Format output
        result = {
            "file_path": file_path,
            "file_size": os.path.getsize(file_path),
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "analysis_types": analysis_types,
            "results": analysis_results,
            "summary": summary
        }

        return result

    def _calculate_cyclomatic_complexity(self, code: str, file_path: str) -> Dict[str, Any]:
        """Calculate cyclomatic complexity"""
        # Implementation using radon or similar tool
        pass

    def _calculate_maintainability_index(self, code: str, file_path: str) -> Dict[str, Any]:
        """Calculate maintainability index"""
        # Implementation details...
        pass

    def _count_lines_of_code(self, code: str, file_path: str) -> Dict[str, Any]:
        """Count lines of code"""
        lines = code.split('\n')
        total_lines = len(lines)
        code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        blank_lines = len([line for line in lines if not line.strip()])

        return {
            "total_lines": total_lines,
            "code_lines": code_lines,
            "comment_lines": comment_lines,
            "blank_lines": blank_lines,
            "comment_ratio": comment_lines / total_lines if total_lines > 0 else 0
        }

    def _detect_duplication(self, code: str, file_path: str) -> Dict[str, Any]:
        """Detect code duplication"""
        # Implementation details...
        pass

    def _scan_security_issues(self, code: str, file_path: str) -> Dict[str, Any]:
        """Scan for security issues"""
        # Implementation details...
        pass

    def _generate_analysis_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analysis summary"""
        # Implementation details...
        pass
```

#### Terminal Execution Tools

```python
# ✅ Good: Secure terminal execution
class TerminalExecutionTool:
    """Secure terminal command execution with sandboxing"""

    def __init__(self, security_manager: SecurityManager):
        self.security_manager = security_manager
        self.execution_context = {}

    def execute_command(
        self,
        command: str,
        working_directory: str = None,
        environment: Dict[str, str] = None,
        timeout: int = 300,
        max_output_size: int = 10 * 1024 * 1024  # 10MB
    ) -> Dict[str, Any]:
        """Execute command securely"""

        # Validate command
        if not self._validate_command(command):
            raise SecurityError(f"Command not allowed: {command}")

        # Set up execution environment
        exec_env = os.environ.copy()
        if environment:
            exec_env.update(environment)

        # Set working directory
        work_dir = working_directory or os.getcwd()
        if not os.path.exists(work_dir):
            raise FileNotFoundError(f"Working directory not found: {work_dir}")

        # Execute command
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=work_dir,
                env=exec_env,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            # Validate output size
            if len(result.stdout) > max_output_size or len(result.stderr) > max_output_size:
                raise OutputSizeError("Command output too large")

            return {
                "command": command,
                "working_directory": work_dir,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": result.execution_time,
                "status": "success"
            }

        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Command timed out after {timeout} seconds")
        except Exception as e:
            raise ExecutionError(f"Command execution failed: {str(e)}")

    def _validate_command(self, command: str) -> bool:
        """Validate command for security"""
        # Block dangerous commands
        dangerous_patterns = [
            r'rm\s+-rf',
            r'sudo\s+',
            r'chmod\s+777',
            r'eval\s+',
            r'exec\s+',
            r'system\s*\(',
            r'subprocess\s*\('
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return False

        return True

    def _sanitize_environment(self, environment: Dict[str, str]) -> Dict[str, str]:
        """Sanitize environment variables"""
        # Remove sensitive environment variables
        sensitive_vars = [
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY',
            'DATABASE_PASSWORD',
            'API_KEY',
            'SECRET_KEY'
        ]

        sanitized = environment.copy()
        for var in sensitive_vars:
            if var in sanitized:
                sanitized[var] = '***REDACTED***'

        return sanitized
```

### 3. Tool Testing Guidelines

```python
# ✅ Good: Comprehensive tool testing
def test_web_scraping_tool():
    """Test web scraping functionality"""

    # Mock HTTP responses
    with patch('requests.Session.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = '<html><body><h1>Test</h1><p>Data</p></body></html>'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Test scraping
        tool = WebScrapingTool(rate_limiter=MockRateLimiter(), cache_manager=MockCache())

        result = tool.scrape_webpage(
            url="https://example.com",
            extract_selectors={"title": "h1", "content": "p"}
        )

        assert result["url"] == "https://example.com"
        assert result["status_code"] == 200
        assert "title" in result["extracted_data"]
        assert "content" in result["extracted_data"]

# ✅ Good: Code analysis testing
def test_code_analysis_tool():
    """Test code analysis functionality"""

    tool = CodeAnalysisTool(complexity_analyzer=MockComplexityAnalyzer())

    # Test with sample code
    sample_code = '''
def complex_function():
    if True:
        for i in range(10):
            if i > 5:
                return i
    return 0
'''

    with patch('builtins.open', mock_open(read_data=sample_code)):
        result = tool.analyze_codebase(
            file_path="/path/to/sample.py",
            analysis_types=["cyclomatic_complexity", "lines_of_code"]
        )

        assert result["file_path"] == "/path/to/sample.py"
        assert "results" in result
        assert "cyclomatic_complexity" in result["results"]
        assert "lines_of_code" in result["results"]

# ✅ Good: Terminal execution testing
def test_terminal_execution_tool():
    """Test terminal execution functionality"""

    tool = TerminalExecutionTool(security_manager=MockSecurityManager())

    # Test with safe command
    result = tool.execute_command(
        command="echo 'Hello World'",
        timeout=10
    )

    assert result["command"] == "echo 'Hello World'"
    assert result["return_code"] == 0
    assert result["stdout"].strip() == "Hello World"
    assert result["status"] == "success"

    # Test security validation
    with pytest.raises(SecurityError):
        tool.execute_command("rm -rf /")

    # Test timeout
    with pytest.raises(TimeoutError):
        tool.execute_command("sleep 5", timeout=1)
```

### 4. Tool Integration Patterns

```python
# ✅ Good: Tool integration with memory system
class ToolIntegrationManager:
    """Manages tool integration with enhanced memory"""

    def __init__(self, memory_manager: EnhancedMemoryManager):
        self.memory_manager = memory_manager
        self.tool_registry = ToolRegistry()

    def execute_tool_with_memory(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        conversation_id: str,
        store_results: bool = True
    ) -> Dict[str, Any]:
        """Execute tool with memory integration"""

        # Get tool from registry
        tool = self.tool_registry.get_tool(tool_name)

        # Store execution context in memory
        execution_context_id = self.memory_manager.store_context_entry(
            conversation_id=conversation_id,
            content=f"Executing tool: {tool_name} with parameters: {parameters}",
            context_type="tool_execution",
            importance_score=0.7,
            tags=["tool_execution", tool_name]
        )

        try:
            # Execute tool
            result = tool.execute(parameters)

            # Store results in memory if requested
            if store_results:
                result_id = self.memory_manager.store_context_entry(
                    conversation_id=conversation_id,
                    content=f"Tool {tool_name} results: {result}",
                    context_type="tool_result",
                    importance_score=0.6,
                    tags=["tool_result", tool_name],
                    relationships=[execution_context_id]
                )

                # Create relationship between execution and results
                self.memory_manager.relationship_manager.create_relationship(
                    from_entry_id=execution_context_id,
                    to_entry_id=result_id,
                    relationship_type="execution_result"
                )

            return result

        except Exception as e:
            # Store error in memory
            error_id = self.memory_manager.store_context_entry(
                conversation_id=conversation_id,
                content=f"Tool {tool_name} failed: {str(e)}",
                context_type="tool_error",
                importance_score=0.9,  # High importance for errors
                tags=["tool_error", tool_name, "error"],
                relationships=[execution_context_id]
            )

            raise e
```

## 🤝 Collaboration Guidelines

### 1. Communication Standards

```mermaid
graph TD
    A[Team Communication] --> B[GitHub Issues<br/>Feature Requests & Bugs]
    B --> C[Pull Requests<br/>Code Reviews]
    C --> D[Documentation<br/>Update README & Docs]
    D --> E[Team Meetings<br/>Sprint Planning]

    A --> F[Slack/Discord<br/>Quick Questions]
    F --> G[Code Comments<br/>Implementation Details]
    G --> H[Commit Messages<br/>Change Descriptions]
```

### 2. Code Ownership

```python
# ✅ Good: Clear code ownership with proper attribution
"""
Template Enhancement Module

Author: John Doe <john.doe@company.com>
Created: 2024-01-15
Modified: 2024-01-20 by Jane Smith <jane.smith@company.com>

This module handles AI-powered template enhancement using
various language models and caching strategies.
"""

class TemplateEnhancer:
    """AI-powered template enhancement service"""

    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
        self.enhancement_cache: Dict[str, str] = {}
```

### 3. Knowledge Sharing

```bash
# Weekly knowledge sharing schedule
Monday: Architecture review
Tuesday: Code review sessions
Wednesday: Technical deep-dive
Thursday: Best practices sharing
Friday: Documentation updates
```

## 📊 Code Review Process

### 1. Review Checklist

```mermaid
graph TD
    A[Code Review] --> B[Functionality Check<br/>Does it work as expected?]
    B --> C[Code Quality<br/>Follows standards?]
    C --> D[Security Review<br/>Any vulnerabilities?]
    D --> E[Performance Check<br/>Optimized?]
    E --> F[Testing Review<br/>Tests included?]
    F --> G[Documentation Check<br/>Docs updated?]

    A --> H[Style Review<br/>PEP 8 compliance?]
    H --> I[Error Handling<br/>Proper exceptions?]
    I --> J[Edge Cases<br/>Handled correctly?]
    J --> K[Integration Check<br/>Breaks existing code?]
```

### 2. Review Standards

```python
# ✅ Good: Review-ready code
def calculate_template_complexity(template: PromptTemplate) -> int:
    """
    Calculate the complexity score of a template.

    Complexity factors:
    - Number of variables (1 point each)
    - Length of template content (1 point per 100 chars)
    - Number of conditional blocks (2 points each)
    - Number of nested structures (3 points each)

    Args:
        template: The template to analyze

    Returns:
        Integer complexity score (0-100)
    """
    complexity = 0

    # Count variables
    variable_count = len(template.variables)
    complexity += min(variable_count, 20)  # Cap at 20 points

    # Content length
    content_length = len(template.template_content)
    complexity += min(content_length // 100, 30)  # Cap at 30 points

    # Conditional blocks (simplified)
    conditional_count = template.template_content.count('{{if')
    complexity += conditional_count * 2

    return min(complexity, 100)  # Cap at 100

# ❌ Bad: Not review-ready code
def calc_complexity(t):
    # No docstring, unclear variable names
    c = 0
    c += len(t.variables)
    c += len(t.template_content) // 100
    return c
```

### 3. Review Comments

```python
# ✅ Good: Constructive review comments
"""
This is a great implementation! The complexity calculation is well-thought-out.

Considerations:
1. The variable counting logic looks good, but we should also consider
   nested variables (e.g., {{user.name}} should count as 2 variables)

2. For the content length calculation, maybe we should strip whitespace
   before counting to get a more accurate measure.

3. Could you add some unit tests for edge cases like:
   - Empty templates
   - Templates with only whitespace
   - Templates with nested variables

Overall, this looks ready to merge with those minor improvements!
"""

# ❌ Bad: Unhelpful review comments
"""
This code is bad. Fix it."
"""
```

## 🚀 Deployment Guidelines

### 1. Environment Configuration

```yaml
# Production environment setup
production:
  database:
    url: "postgresql://user:pass@prod-db:5432/mcp_tunnel"
    pool_size: 50
    max_overflow: 100

  server:
    host: "0.0.0.0"
    port: 9001
    workers: 4

  cache:
    redis_url: "redis://prod-cache:6379"
    ttl: 3600

  logging:
    level: "INFO"
    file: "/var/log/mcp-tunnel/app.log"
```

### 2. Deployment Process

```mermaid
graph TD
    A[Development<br/>Local Testing] --> B[Staging<br/>Integration Testing]
    B --> C[Pre-Production<br/>Load Testing]
    C --> D[Production<br/>Live Deployment]

    A --> E[Code Review<br/>Quality Gates]
    E --> F[Automated Tests<br/>Unit & Integration]
    F --> G[Security Scan<br/>Vulnerability Check]
    G --> H[Performance Test<br/>Load & Stress]
    H --> I[Deployment Ready<br/>All Checks Pass]
```

### 3. Monitoring & Alerting

```python
# ✅ Good: Comprehensive monitoring
class HealthChecker:
    """System health monitoring"""

    def check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            start_time = time.time()
            with self.db_manager.get_session() as session:
                session.execute(text("SELECT 1"))
            response_time = time.time() - start_time

            return {
                "status": "healthy",
                "response_time": response_time,
                "connection_pool": self.db_manager.engine.pool.size()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    def check_external_services(self) -> Dict[str, Any]:
        """Check external API availability"""
        services = ["openai", "anthropic", "redis"]
        status = {}

        for service in services:
            try:
                health = self._check_service_health(service)
                status[service] = health
            except Exception as e:
                status[service] = {"status": "error", "error": str(e)}

        return status
```

## 🔍 Troubleshooting

### 1. Common Issues & Solutions

```mermaid
graph TD
    A[Problem Occurs] --> B[Check Logs<br/>Application Logs]
    B --> C[Database Issues<br/>Connection/Queries]
    C --> D[External Services<br/>API Failures]
    D --> E[Configuration Problems<br/>Settings/Config]

    A --> F[Performance Issues<br/>Slow Response]
    F --> G[Memory Problems<br/>Resource Usage]
    G --> H[Network Issues<br/>Connectivity]
    H --> I[Application Errors<br/>Code Problems]
```

### 2. Debugging Guide

```python
# ✅ Good: Comprehensive debugging
def debug_template_rendering(
    template_name: str,
    variables: Dict[str, Any]
) -> Dict[str, Any]:
    """Debug template rendering with detailed information"""

    debug_info = {
        "template_name": template_name,
        "variables": variables,
        "steps": [],
        "errors": []
    }

    try:
        # Step 1: Template loading
        debug_info["steps"].append("Loading template...")
        template = self.template_manager.get_template(template_name)
        debug_info["template_id"] = template.id
        debug_info["steps"].append(f"Template loaded: {template.name}")

        # Step 2: Variable processing
        debug_info["steps"].append("Processing variables...")
        processed_vars = self.variable_processor.process(variables)
        debug_info["processed_variables"] = processed_vars
        debug_info["steps"].append(f"Variables processed: {len(processed_vars)} variables")

        # Step 3: Template rendering
        debug_info["steps"].append("Rendering template...")
        rendered = template.render(processed_vars)
        debug_info["rendered_length"] = len(rendered)
        debug_info["steps"].append(f"Template rendered: {len(rendered)} characters")

        debug_info["success"] = True
        return debug_info

    except Exception as e:
        debug_info["errors"].append(str(e))
        debug_info["success"] = False
        return debug_info
```

## 📞 Getting Help

### 1. Support Channels

```mermaid
graph TD
    A[Need Help?] --> B[Documentation<br/>Check README & Docs]
    B --> C[GitHub Issues<br/>Bug Reports]
    C --> D[GitHub Discussions<br/>Q&A Forum]
    D --> E[Team Chat<br/>Slack/Discord]

    A --> F[Urgent Issue<br/>Critical Bug]
    F --> G[Emergency Contact<br/>Team Leads]
    G --> H[Status Page<br/>System Status]
```

### 2. Help Request Template

```markdown
## Problem Description
[Clear description of the issue]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment
- OS: [Operating System]
- Python Version: [Python version]
- MCP-PBA-TUNNEL Version: [Version]
- Database: [Database type/version]

## Logs/Errors
[Include relevant logs or error messages]

## Additional Context
[Any other relevant information]
```

## 🎯 Contributing Checklist

### Before Submitting Code

- [ ] **Code Quality**: Follows PEP 8, type hints, docstrings
- [ ] **Tests**: Unit tests included, 80%+ coverage
- [ ] **Documentation**: README updated, examples included
- [ ] **Security**: Input validation, no vulnerabilities
- [ ] **Performance**: Optimized queries, proper caching
- [ ] **Error Handling**: Comprehensive exception handling
- [ ] **Migration**: Database changes have migrations
- [ ] **Review**: Code reviewed by at least one team member

### Before Merging PR

- [ ] **Tests Pass**: All CI/CD tests successful
- [ ] **Code Review**: Approved by reviewers
- [ ] **Integration**: Works with existing codebase
- [ ] **Documentation**: All docs updated
- [ ] **Migration**: Database migrations applied
- [ ] **Deployment**: Ready for production deployment

## 📋 Appendices

### A. Glossary

- **MCP**: Model Context Protocol - Standard for AI assistant integration
- **PBA**: Prompt-Based Architecture - Our system architecture approach
- **TUNNEL**: Template UNified Neural Engineering Layer - System name
- **ORM**: Object-Relational Mapping - Database abstraction layer
- **ASGI**: Asynchronous Server Gateway Interface - Python async web standard

### B. Command Reference

```bash
# Development
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Database
python3 -m alembic upgrade head
python3 -m alembic revision --autogenerate -m "description"

# Testing
pytest
pytest --cov=data --cov-report=html

# Documentation
python3 -m http.server 8000  # Serve docs locally

# Production
gunicorn server.fastapi_mcp_server:app -w 4 -b 0.0.0.0:9001
```

### C. Configuration Files

```json
{
  "development": {
    "database": "sqlite:///dev.db",
    "debug": true,
    "log_level": "DEBUG"
  },
  "production": {
    "database": "postgresql://prod-db:5432/mcp_tunnel",
    "debug": false,
    "log_level": "INFO"
  }
}
```

---

**Thank you for contributing to MCP-PBA-TUNNEL! 🚀**

This comprehensive guide ensures that all contributors understand our standards, processes, and best practices. Remember: good code is not just about functionality, but also about maintainability, security, and collaboration.

*Last updated: January 2024*
*Version: 1.0.0*
