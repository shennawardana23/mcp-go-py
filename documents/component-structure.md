# 🏗️ Component Structure: FastAPI MCP Server Architecture

## 📋 Overview

This document provides a comprehensive view of the FastAPI-based MCP server's component architecture, highlighting key interactions and dependencies between different parts of the system.

## 🎯 System Component Overview with Repository/Service Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        A[AI Assistants<br/>Claude, Cursor, GPT] --> B[MCP Clients<br/>JSON-RPC Protocol]
        B --> C[REST API Clients<br/>HTTP/JSON API]
        C --> D[Web Interfaces<br/>Admin Dashboard]
    end

    subgraph "Presentation Layer"
        A --> E[FastAPI Server<br/>Request Routing & Processing]
        D --> E
        E --> F[CORS Middleware<br/>Cross-origin handling]
        E --> G[Authentication<br/>JWT/API Key validation]
        E --> H[Rate Limiting<br/>Request throttling]
    end

    subgraph "Application Layer"
        E --> I[MCP Protocol Handler<br/>/mcp/* endpoints]
        E --> J[REST API Handler<br/>/api/* endpoints]
        E --> K[Background Tasks<br/>Celery workers]
        I --> L[PromptDataManager<br/>Facade Pattern]
        J --> L
    end

    subgraph "Business Logic Layer"
        L --> M[PromptService<br/>Template Business Logic]
        L --> N[AIService<br/>AI Integration Logic]
        L --> O[ValidationService<br/>Data Validation Rules]
        M --> P[Template Processor<br/>Variable substitution]
        N --> Q[Usage Tracker<br/>Analytics & metrics]
    end

    subgraph "Data Access Layer"
        M --> R[PromptRepository<br/>Template Database Operations]
        N --> S[AIConfigurationRepository<br/>AI Settings Storage]
        O --> T[ValidationRepository<br/>Validation Rules Storage]
        P --> U[TemplateProcessor<br/>Content Processing]
        Q --> V[AnalyticsRepository<br/>Usage Data Storage]
    end

    subgraph "Infrastructure Layer"
        R --> W[DatabaseConfig<br/>Connection Pool]
        S --> W
        T --> W
        W --> X[(PostgreSQL<br/>Native psycopg Queries)]
        K --> Y[Redis Cache<br/>Session & temporary data]
        Y --> X
        K --> Z[Message Queue<br/>Background task queue]
        Z --> AA[Task Workers<br/>Async processing]
    end

    subgraph "External Services"
        N --> BB[AI Services<br/>OpenAI, Anthropic APIs]
        AA --> BB
        W --> CC[External APIs<br/>Optional integrations]
    end

    subgraph "Enhanced Memory System"
        PS --> DD[Context Relationship Manager<br/>Relationship Mapping]
        PR --> EE[Enhanced Memory Repository<br/>Advanced Context Storage]
        DD --> FF[Importance Scoring Engine<br/>Relevance Calculation]
        EE --> GG[Tag-Based Organization<br/>Flexible Categorization]
        FF --> HH[Context Retrieval Engine<br/>Memory Querying]
        GG --> HH
    end

    subgraph "Advanced Tool Ecosystem"
        PM --> II[Web Scraping Engine<br/>BeautifulSoup4 + Requests]
        PM --> JJ[Code Analysis Tools<br/>Complexity + Quality Metrics]
        PM --> KK[Terminal Executor<br/>Safe Command Execution]
        PM --> LL[Database Analyzer<br/>Schema + Query Analysis]
        PM --> MM[Testing Framework<br/>Automated Test Execution]
        II --> NN[External Data Sources<br/>APIs + Web Content]
        JJ --> OO[Code Repository<br/>Source Code Files]
        KK --> PP[System Terminal<br/>Command Line Interface]
        LL --> QQ[Database Systems<br/>PostgreSQL + Analytics]
        MM --> RR[Test Suites<br/>Unit + Integration Tests]
    end
```

## 🔧 Detailed Component Architecture

### 1. FastAPI Application Server (Presentation Layer)

**Primary Responsibilities:**

- HTTP request handling and routing
- Middleware management and processing
- Response generation and formatting
- Background task scheduling
- Integration with application layer

```mermaid
graph TD
    A[FastAPI Application] --> B[Request/Response<br/>HTTP handling]
    A --> C[Routing<br/>URL path matching]
    A --> D[Middleware Stack<br/>CORS, auth, logging]
    A --> E[Exception Handling<br/>Error processing]
    A --> F[Background Tasks<br/>Celery integration]

    B --> G[Request Parser<br/>JSON/Form parsing]
    C --> H[Handler Execution<br/>Function dispatch]
    D --> I[Request Processing<br/>Pre/post processing]
    E --> J[Error Formatting<br/>User-friendly errors]
    F --> K[Task Queue<br/>Background processing]

    G --> L[Validation<br/>Pydantic models]
    H --> M[Application Layer<br/>PromptDataManager]
    I --> N[Security<br/>Input sanitization]
    J --> O[Logging<br/>Error tracking]
    K --> P[Workers<br/>Async execution]

    L --> Q[Business Logic Layer<br/>Service Layer]
    M --> Q
    N --> Q
    P --> R[External APIs<br/>AI services]
    Q --> S[Data Access Layer<br/>Repository Layer]
```

### 2. Application Layer (PromptDataManager Facade)

**Primary Responsibilities:**

- Main entry point for all data operations
- Orchestrates service and repository layers
- Manages global state and configuration
- Implements facade pattern for simplified interface

```python
class PromptDataManager:
    """Facade pattern implementation for data management"""

    def __init__(self):
        self.prompt_service = BusinessLogicPromptService()
        self.ai_service = AIService()
        self.db_manager = DatabaseManager()

    def render_template(self, template_name: str, variables: Dict[str, Any]) -> str:
        """Main template rendering method using layered architecture"""
        # Service layer handles business logic
        template = self.prompt_service.get_template(template_name)
        # Repository layer handles data access
        db_template = self.prompt_service.repository.get_by_name(template_name)
        # Process and return
        return template.render(variables)
```

### 3. Business Logic Layer (Service Layer)

**Primary Responsibilities:**

- Implement business logic and use cases
- Handle validation and business rules
- Orchestrate repository operations
- Provide transaction boundaries

**Key Components:**

- **PromptService**: Template business logic and validation
- **AIService**: AI configuration and integration logic
- **ValidationService**: Data validation utilities
- **Business Rules**: Domain-specific logic and constraints

### 4. Data Access Layer (Repository Layer)

**Primary Responsibilities:**

- Abstract database operations from business logic
- Provide consistent data access interface
- Handle database-specific optimizations
- Implement data mapping and transformation

**Key Components:**

- **PromptTemplateRepository**: Template database operations
- **AIConfigurationRepository**: AI model configuration storage
- **BaseRepository**: Generic CRUD operations for all entities
- **DatabaseConfig**: Connection pooling and transaction management

### 5. MCP Protocol Handler

**Primary Responsibilities:**

- JSON-RPC 2.0 protocol implementation
- MCP method routing and execution
- Response formatting according to MCP spec
- Error handling for protocol violations

```mermaid
graph TD
    A[MCP Protocol Handler] --> B[Protocol Validator<br/>JSON-RPC 2.0 compliance]
    A --> C[Method Router<br/>prompts/*, tools/* routing]
    A --> D[Parameter Extractor<br/>Request parameter parsing]
    A --> E[Response Builder<br/>MCP response formatting]
    A --> F[Error Handler<br/>Protocol error handling]

    B --> G[Version Check<br/>Protocol version validation]
    B --> H[Method Validation<br/>Supported methods check]
    C --> I[Prompts Handler<br/>Template operations]
    C --> J[Tools Handler<br/>Tool execution]
    D --> K[Argument Parser<br/>Parameter validation]
    E --> L[Success Response<br/>Result formatting]
    E --> M[Error Response<br/>JSON-RPC error format]
    F --> N[Protocol Errors<br/>Invalid request handling]

    I --> O[Database Layer<br/>Template queries]
    J --> P[Business Logic<br/>Tool execution]
    K --> Q[Validation Layer<br/>Input validation]
    L --> R[HTTP Response<br/>Final output]
    M --> R
    N --> R
```

### 3. Data Management Layer

**Primary Responsibilities:**

- Database connection management
- ORM operations and query building
- Transaction handling and rollbacks
- Connection pooling and optimization

```mermaid
graph TD
    A[Database Manager] --> B[Connection Pool<br/>SQLAlchemy engine]
    A --> C[Session Manager<br/>Transaction handling]
    A --> D[Query Builder<br/>SQL generation]
    A --> E[Migration Manager<br/>Schema management]
    A --> F[Backup Manager<br/>Data backup/restore]

    B --> G[Connection Factory<br/>Database connections]
    C --> H[Transaction Control<br/>Begin/commit/rollback]
    D --> I[SQL Generator<br/>Query construction]
    E --> J[Schema Manager<br/>Table/column management]
    F --> K[Export/Import<br/>Data serialization]

    G --> L[Pool Manager<br/>Connection pooling]
    H --> M[Error Recovery<br/>Rollback handling]
    I --> N[Optimization<br/>Query optimization]
    J --> O[Version Control<br/>Schema versioning]
    K --> P[Data Integrity<br/>Consistency checks]

    L --> Q[(Database<br/>PostgreSQL)]
    M --> Q
    N --> Q
    O --> Q
    P --> Q
```

### 4. Prompt Template Manager

**Primary Responsibilities:**

- Template CRUD operations
- Variable substitution and rendering
- Template validation and processing
- Usage tracking and analytics

```mermaid
graph TD
    A[Prompt Manager] --> B[Template CRUD<br/>Create/read/update/delete]
    A --> C[Variable Processor<br/>{{variable}} substitution]
    A --> D[Validator<br/>Template content validation]
    A --> E[Cache Manager<br/>Template caching]
    A --> F[Usage Tracker<br/>Analytics collection]

    B --> G[Database Layer<br/>SQLAlchemy operations]
    C --> H[Substitution Engine<br/>String replacement]
    D --> I[Syntax Checker<br/>Template validation]
    E --> J[Cache Layer<br/>Redis/in-memory cache]
    F --> K[Metrics Collector<br/>Usage statistics]

    G --> L[Transaction Manager<br/>Atomic operations]
    H --> M[Output Formatter<br/>Clean content]
    I --> N[Error Reporter<br/>Validation errors]
    J --> O[Cache Invalidation<br/>Update management]
    K --> P[Analytics Database<br/>Usage data storage]

    L --> Q[(Database<br/>Template storage)]
    M --> R[Response Builder<br/>Formatted output]
    N --> S[Error Handler<br/>Validation failures]
    O --> T[Cache Refresh<br/>Background updates]
    P --> U[Reporting System<br/>Usage reports]
```

### 5. AI Integration Layer

**Primary Responsibilities:**

- External AI service communication
- Request/response handling
- Rate limiting and quota management
- Fallback and error handling

```mermaid
graph TD
    A[AI Integration Layer] --> B[Service Clients<br/>OpenAI, Anthropic APIs]
    A --> C[Request Manager<br/>API call coordination]
    A --> D[Rate Limiter<br/>Quota management]
    A --> E[Response Processor<br/>Output formatting]
    A --> F[Fallback Manager<br/>Error recovery]

    B --> G[HTTP Client<br/>Async API calls]
    C --> H[Queue Manager<br/>Request queuing]
    D --> I[Quota Tracker<br/>Usage monitoring]
    E --> J[Content Parser<br/>Response parsing]
    F --> K[Retry Logic<br/>Error handling]

    G --> L[Connection Pool<br/>HTTP connections]
    H --> M[Priority Queue<br/>Request prioritization]
    I --> N[Usage Database<br/>Quota tracking]
    J --> O[Format Converter<br/>Response formatting]
    K --> P[Error Recovery<br/>Automatic retry]

    L --> Q[External APIs<br/>AI services]
    M --> Q
    N --> R[Metrics Database<br/>Usage tracking]
    O --> S[Cache Layer<br/>Response caching]
    P --> T[Alert System<br/>Error notifications]
```

## 🔄 Component Interaction Patterns

### Request-Response Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant F as FastAPI
    participant M as MCP Handler
    participant P as Prompt Manager
    participant D as Database
    participant A as AI Service

    C->>F: HTTP POST /mcp/prompts/list
    F->>M: Route to MCP handler
    M->>P: Get prompt templates
    P->>D: Query database
    D->>P: Return template data
    P->>M: Format response
    M->>F: Build HTTP response
    F->>C: Return response

    Note over C: Optional AI enhancement
    M->>A: Enhance with AI (optional)
    A->>M: Return enhanced content
```

### Error Handling Flow

```mermaid
flowchart TD
    A[Request Processing<br/>Any component] --> B{Error Type}
    B -->|Validation Error| C[Input Validation Error<br/>400 Bad Request]
    B -->|Database Error| D[Database Connection Error<br/>503 Service Unavailable]
    B -->|AI Service Error| E[External Service Error<br/>502 Bad Gateway]
    B -->|Template Error| F[Template Processing Error<br/>404 Not Found]

    C --> G[Error Response<br/>Client-friendly message]
    D --> H[Error Response<br/>Database error details]
    E --> I[Error Response<br/>Service unavailable]
    F --> J[Error Response<br/>Template not found]

    G --> K[Client Notification<br/>HTTP response with error]
    H --> K
    I --> K
    J --> K
```

### Data Flow Between Components

```mermaid
flowchart LR
    subgraph "Input Processing Layer"
        A[HTTP Request<br/>JSON payload] --> B[FastAPI Middleware<br/>CORS, logging, auth]
        B --> C[Request Parser<br/>JSON validation]
    end

    subgraph "Business Logic Layer"
        C --> D[MCP/REST Handler<br/>Route to appropriate handler]
        D --> E[Prompt Manager<br/>Template operations]
        E --> F[Template Processor<br/>Variable substitution]
        E --> G[Usage Tracker<br/>Analytics collection]
    end

    subgraph "Data Access Layer"
        F --> H[Database Layer<br/>psycopg Native Queries]
        G --> H
        H --> I[(Database<br/>PostgreSQL)]
        F --> J[AI Integration<br/>External API calls]
        J --> K[External Services<br/>OpenAI, Anthropic]
    end

    subgraph "Output Layer"
        H --> L[Response Builder<br/>JSON formatting]
        K --> L
        L --> M[HTTP Response<br/>FastAPI response]
    end
```

## 📊 Component Dependencies

### Internal Dependencies

```mermaid
graph TD
    A[FastAPI Server] --> B[Database Manager<br/>Connection handling]
    A --> C[Prompt Manager<br/>Template operations]
    A --> D[Configuration Manager<br/>Settings management]

    B --> E[psycopg Pool<br/>Database connections]
    C --> F[Template Processor<br/>Variable substitution]
    C --> G[Usage Tracker<br/>Analytics]
    C --> H[Cache Manager<br/>Performance optimization]

    D --> I[Environment Manager<br/>Config loading]
    E --> J[Connection Pool<br/>Database pooling]
    F --> K[Validation Engine<br/>Input validation]
    G --> L[Metrics Collector<br/>Usage statistics]
    H --> M[Redis Client<br/>Caching]
```

### External Dependencies

```mermaid
graph TD
    A[Application] --> B[FastAPI<br/>Web framework]
    A --> C[psycopg<br/>Database Native Queries]
    A --> D[Uvicorn<br/>ASGI server]
    A --> E[Pydantic<br/>Data validation]

    B --> F[Starlette<br/>ASGI framework]
    C --> G[Database Drivers<br/>psycopg2]
    D --> H[ASGI Specification<br/>Server interface]
    E --> I[Type System<br/>Runtime validation]

    F --> J[HTTP Handling<br/>Request/response]
    G --> K[SQL Generation<br/>Query building]
    H --> L[Server Protocol<br/>ASGI compliance]
    I --> M[Data Validation<br/>Schema validation]
```

## 🔧 Configuration Management

### Configuration Component Architecture

```mermaid
graph TD
    A[Configuration Files<br/>JSON/YAML/ENV] --> B[Config Loader<br/>File and env var loading]
    A --> C[Environment Manager<br/>Runtime configuration]
    A --> D[Validation Engine<br/>Config validation]

    B --> E[JSON Parser<br/>Configuration parsing]
    C --> F[Variable Substitution<br/>Environment variable replacement]
    D --> G[Schema Validator<br/>Configuration schema validation]

    E --> H[Application Config<br/>FastAPI settings]
    F --> I[Database Config<br/>Connection settings]
    G --> J[Security Config<br/>Authentication settings]

    H --> K[Server Configuration<br/>Host, port, workers]
    I --> L[Database Settings<br/>Pool, timeout, URL]
    J --> M[Security Settings<br/>JWT, CORS, rate limiting]
```

### Settings Hierarchy

```mermaid
graph TD
    A[Configuration Sources<br/>Priority order] --> B[Environment Variables<br/>Highest priority]
    A --> C[Configuration Files<br/>JSON/YAML files]
    A --> D[Default Values<br/>Built-in defaults]

    B --> E[Runtime Override<br/>Command line, environment]
    C --> F[File-based Config<br/>Static configuration]
    D --> G[Built-in Defaults<br/>Hardcoded fallbacks]

    E --> H[Application Settings<br/>FastAPI configuration]
    F --> H
    G --> H
```

## 📈 Performance Components

### Caching System Architecture

```mermaid
graph TD
    A[Cache Manager] --> B[In-Memory Cache<br/>Frequently used data]
    A --> C[Redis Cache<br/>Session and temporary data]
    A --> D[Database Cache<br/>Query result caching]

    B --> E[Template Cache<br/>Compiled templates]
    C --> F[Session Cache<br/>User sessions]
    D --> G[Query Cache<br/>Database query results]

    E --> H[Fast Retrieval<br/>~1ms access time]
    F --> I[Session Management<br/>User state]
    G --> J[Query Optimization<br/>Reduced DB load]

    H --> K[Performance Metrics<br/>Cache hit rates]
    I --> L[Session Analytics<br/>Usage patterns]
    J --> M[Query Analytics<br/>Performance monitoring]
```

### Async Processing Architecture

```mermaid
graph TD
    A[Async Components] --> B[FastAPI Async<br/>Non-blocking request handling]
    A --> C[Database Async<br/>Async database operations]
    A --> D[AI Service Async<br/>Non-blocking AI calls]
    A --> E[Background Tasks<br/>Celery workers]

    B --> F[Request Pool<br/>Concurrent request handling]
    C --> G[Connection Pool<br/>Database connections]
    D --> H[Service Pool<br/>External API connections]
    E --> I[Worker Pool<br/>Background processing]

    F --> J[Load Balancing<br/>Request distribution]
    G --> K[Connection Reuse<br/>Database efficiency]
    H --> L[Rate Limiting<br/>API quota management]
    I --> M[Task Distribution<br/>Workload balancing]

    J --> N[Scalability<br/>Handle high load]
    K --> O[Efficiency<br/>Resource optimization]
    L --> P[Reliability<br/>Service availability]
    M --> Q[Performance<br/>Task processing speed]
```

## 🧪 Testing Component Architecture

### Test Coverage Areas

```mermaid
graph TD
    A[Unit Tests<br/>Individual components] --> B[FastAPI Tests<br/>HTTP endpoints]
    A --> C[Database Tests<br/>psycopg queries]
    A --> D[Business Logic Tests<br/>Template processing]
    A --> E[Integration Tests<br/>Component interaction]

    B --> F[Endpoint Tests<br/>Request/response testing]
    C --> G[Model Tests<br/>Database operations]
    D --> H[Processor Tests<br/>Template rendering]
    E --> I[Workflow Tests<br/>End-to-end flows]

    F --> J[Mock Testing<br/>External service mocking]
    G --> K[Fixture Testing<br/>Test data management]
    H --> L[Performance Testing<br/>Load and stress testing]
    I --> M[Protocol Testing<br/>MCP compliance]
```

### Testing Infrastructure

```mermaid
graph TD
    A[Test Framework<br/>Pytest with async support] --> B[Test Client<br/>FastAPI test client]
    A --> C[Mock Library<br/>unittest.mock, responses]
    A --> D[Fixture System<br/>Database fixtures]
    A --> E[Coverage Tools<br/>pytest-cov]

    B --> F[HTTP Testing<br/>Request/response testing]
    C --> G[External Service Mocking<br/>AI service simulation]
    D --> H[Database Fixtures<br/>Test data setup]
    E --> I[Coverage Reports<br/>Code coverage metrics]

    F --> J[Integration Testing<br/>Full workflow testing]
    G --> K[Contract Testing<br/>API contract validation]
    H --> L[Data Validation<br/>Test data integrity]
    I --> M[Quality Gates<br/>Coverage requirements]
```

## 📚 Documentation Components

### Documentation Structure

```mermaid
graph TD
    A[Documentation System] --> B[API Documentation<br/>OpenAPI/Swagger]
    A --> C[Code Documentation<br/>Docstrings and comments]
    A --> D[User Documentation<br/>README and guides]
    A --> E[Developer Documentation<br/>Architecture docs]

    B --> F[Endpoint Documentation<br/>HTTP API reference]
    C --> G[Function Documentation<br/>Code reference]
    D --> H[Usage Examples<br/>Code samples]
    E --> I[Architecture Documentation<br/>System design]

    F --> J[Interactive API Explorer<br/>Swagger UI]
    G --> K[Code Examples<br/>Usage patterns]
    H --> L[Tutorials<br/>Step-by-step guides]
    I --> M[Diagrams<br/>System architecture]
```

This comprehensive component architecture ensures the FastAPI MCP server is well-structured, maintainable, and provides clear separation of concerns for different aspects of the prompt engineering functionality.
