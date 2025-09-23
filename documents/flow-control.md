# 🔄 Flow Control: Request Processing Analysis

## 📋 Overview

This document provides a comprehensive analysis of the FastAPI-based MCP server's request processing flow, from initial client request through prompt template resolution to final response generation.

## 🎯 Request Processing Architecture

### HTTP Request Lifecycle with Layered Architecture

```mermaid
sequenceDiagram
    participant C as MCP Client
    participant F as FastAPI Server
    participant R as Request Router
    participant PM as PromptDataManager
    participant PS as PromptService
    participant PR as PromptRepository
    participant DB as Database Layer
    participant A as AI Integration

    C->>F: HTTP POST /mcp/prompts/list
    Note over F: Input Validation & Routing
    F->>R: Route to MCP Handler
    R->>PM: Process Request (Facade Pattern)
    PM->>PS: Get Available Templates (Service Layer)
    PS->>PR: Query Templates (Repository Pattern)
    PR->>DB: Execute Native SQL Query
    DB->>PR: Return Raw Database Results
    PR->>PS: Transform to Domain Objects
    PS->>PM: Apply Business Rules & Validation
    PM->>R: Format Response
    R->>F: Generate JSON Response
    F->>C: Return HTTP Response

    Note over C: Client processes response
```

### Detailed Request Flow Components with Layered Architecture

```mermaid
flowchart TD
    A[Client Request<br/>HTTP POST /mcp/prompts/list] --> B[FastAPI Middleware<br/>CORS, Logging, Validation]
    B --> C[Request Parsing<br/>JSON Body Processing]
    C --> D{MCP Protocol<br/>Validation}
    D -->|Valid| E[Route Handler<br/>/mcp/prompts/list]
    D -->|Invalid| F[Error Response<br/>400 Bad Request]

    E --> G[PromptDataManager<br/>Facade Layer]
    G --> H[PromptService<br/>Business Logic Layer]
    H --> I[PromptRepository<br/>Data Access Layer]
    I --> J[DatabaseConfig<br/>Connection Pool]
    J --> K[(PostgreSQL<br/>Native psycopg Queries)]
    K --> J
    J --> I
    I --> H
    H --> G
    G --> L[Response Building<br/>JSON-RPC Format]
    L --> M[HTTP Response<br/>200 OK with JSON]

    F --> N[Error Handler<br/>Log and Format Error]
    N --> M

    H --> O[ValidationService<br/>Data Validation]
    O --> P[Cache Manager<br/>Template Caching]
    P --> Q[AI Integration<br/>Optional Enhancement]
```

## 🔍 Detailed Flow Analysis

### 1. Client Request Initiation

**Endpoint**: `POST /mcp/prompts/list`

```mermaid
flowchart TD
    A[AI Assistant<br/>Claude/Cursor] --> B[Generate JSON-RPC Request<br/>{"jsonrpc": "2.0", "id": "123", "method": "prompts/list"}]
    B --> C[HTTP Client<br/>Send POST Request]
    C --> D[Network Layer<br/>TCP/IP Transport]
    D --> E[FastAPI Server<br/>Receive Request]

    E --> F[Request Context<br/>URL, Headers, Body]
    F --> G[Middleware Stack<br/>CORS, Logging, Security]
    G --> H[Route Matching<br/>Match /mcp/prompts/list]
    H --> I[Handler Execution<br/>list_prompts() Function]
```

**Data Flow:**

- **Input**: JSON-RPC 2.0 formatted request
- **Validation**: Protocol version, method name, parameters
- **Routing**: FastAPI automatic route resolution
- **Processing**: Template retrieval and formatting

### 2. Server Request Processing with Layered Architecture

**Request Handler**: `list_prompts()` - Uses Repository/Service Pattern

```mermaid
flowchart TD
    A[Handler Start<br/>async def list_prompts(request: Dict) -> Dict] --> B[Input Validation<br/>Check JSON-RPC Format]
    B --> C[PromptDataManager.get_data_manager()<br/>Get Facade Instance]
    C --> D[PromptService.list_templates()<br/>Business Logic Call]
    D --> E[PromptRepository.find_active_templates()<br/>Repository Query]
    E --> F[DatabaseConfig.get_connection()<br/>Connection Pool Access]
    F --> G[psycopg Native Query<br/>SELECT * FROM prompt_templates WHERE is_active=True]
    G --> H[Result Processing<br/>Transform Raw Data to Objects]
    H --> I[Service Layer Validation<br/>Business Rules Applied]
    I --> J[Response Building<br/>JSON-RPC Success Response]
    J --> K[Session Cleanup<br/>Connection Pool Return]
    K --> L[Return Response<br/>FastAPI HTTP Response]

    B --> M[Error: Invalid Request<br/>400 Bad Request]
    M --> N[Error Response<br/>JSON-RPC Error Format]
    N --> L
```

**Repository Layer Query**:

```sql
-- Repository executes optimized native queries
SELECT
    id, name, description, category, variables,
    created_at, updated_at
FROM prompt_templates
WHERE is_active = true
ORDER BY category, name
```

**Service Layer Processing**:

```python
# Service layer adds business logic
def list_templates(self) -> List[PromptTemplate]:
    # Get from repository
    templates = self.repository.find_active_templates()

    # Apply business rules
    for template in templates:
        template.validate_category()
        template.sanitize_content()

    # Return processed templates
    return templates
```

### 3. Template Processing Pipeline with Repository/Service Layers

**Template Resolution Flow**:

```mermaid
flowchart TD
    A[Template Request<br/>Template Name + Variables] --> B[Service Layer<br/>Input Validation & Business Rules]
    B --> C[Repository Layer<br/>Database Query & Object Mapping]
    C --> D{Template Found}
    D -->|Yes| E[Domain Model Creation<br/>Transform DB Row to Object]
    D -->|No| F[Repository Exception<br/>TemplateNotFoundError]

    E --> G[Service Layer Processing<br/>Business Logic & Validation]
    G --> H[Variable Processing<br/>Parse Template Variables]
    H --> I[Content Rendering<br/>Replace {{variables}} with Values]
    I --> J[AI Enhancement<br/>Optional GPT/Claude Integration]
    J --> K[Output Formatting<br/>Clean and Structure Response]
    K --> L[Success Response<br/>Rendered Template Content]

    F --> M[Service Exception Handling<br/>404 Not Found with Details]
    M --> L

    G --> N[Validation Service<br/>Data Validation & Sanitization]
    N --> O[Cache Manager<br/>Template Caching for Performance]
```

### 4. Database/Data Management Flow with Repository Pattern

**Repository Layer Query Flow**:

```mermaid
flowchart TD
    A[Service Request<br/>Business Operation] --> B[Repository Layer<br/>Data Access Interface]
    B --> C[Connection Pool<br/>DatabaseConfig.get_connection_pool()]
    C --> D[Native SQL Query<br/>Repository builds optimized queries]
    D --> E[Parameter Binding<br/>Safe SQL injection prevention]
    E --> F[Query Execution<br/>psycopg native query execution]
    F --> G[Result Processing<br/>Transform raw data to domain objects]
    G --> H[Connection Pool<br/>Return Connection to Pool]
    H --> I[Repository Response<br/>Domain objects returned to service]

    D --> J[Error Handling<br/>Database exceptions caught]
    J --> K[Repository Exception<br/>Transform to business exceptions]
    K --> L[Service Error Handling<br/>Business logic error handling]
    L --> M[Error Response<br/>User-friendly error messages]
```

**Repository Pattern Benefits**:

- **Separation of Concerns**: Database logic isolated from business logic
- **Testability**: Easy to mock repository for unit testing
- **Consistency**: Standardized data access patterns
- **Performance**: Optimized queries and connection pooling
- **Maintainability**: Changes to database schema isolated to repository layer

**Connection Pool Management**:

- **Pool Size**: Configurable based on load requirements (min_size: 5, max_size: 20)
- **Overflow Protection**: Additional connections beyond pool size
- **Timeout Handling**: Connection acquisition timeout (30 seconds)
- **Connection Recycling**: Automatic connection refresh to prevent stale connections
- **Thread Safety**: Thread-safe connection pool access

## 📊 Data Lineage Analysis

### Example: `template_name` Variable Flow

**Variable**: `template_name`
**Context**: Prompt template rendering request

```mermaid
flowchart LR
    subgraph "Input Stage"
        A[HTTP Request<br/>template_name="business_logic"] --> B[URL Parsing<br/>Extract from Query String]
        B --> C[Validation<br/>Check Template Exists]
    end

    subgraph "Processing Stage"
        C --> D[Database Query<br/>SELECT * FROM prompt_templates WHERE name=%s]
        D --> E[Template Loading<br/>Load Template Content]
        E --> F[Variable Substitution<br/>Replace {{variables}} in Content]
    end

    subgraph "Output Stage"
        F --> G[Response Building<br/>Format JSON Response]
        G --> H[HTTP Response<br/>Return Rendered Content]
    end
```

**Transformation Points:**

1. **Input Sanitization**: URL decode and validate template name
2. **Database Query**: Convert name to SQL WHERE clause
3. **Template Processing**: Replace `{{variable}}` placeholders with actual values
4. **Response Formatting**: Structure data for JSON response

### Example: `prompt_variables` Variable Flow

**Variable**: `prompt_variables`
**Context**: Template rendering with multiple variables

```mermaid
stateDiagram-v2
    [*] --> InputValidation
    InputValidation --> VariableParsing
    VariableParsing --> DatabaseStorage
    DatabaseStorage --> TemplateProcessing
    TemplateProcessing --> ResponseGeneration
    ResponseGeneration --> [*]

    InputValidation : variables = {"domain": "ecommerce", "type": "api"}
    VariableParsing : Parse JSON input<br/>Validate variable types
    DatabaseStorage : Store input variables<br/>JSON field in database
    TemplateProcessing : template = "Design API for {{domain}} {{type}}"
    ResponseGeneration : output = "Design API for ecommerce api"
```

## 🔧 Control Flow Branching

### MCP Protocol vs REST API Routing

```mermaid
flowchart TD
    A[Incoming Request<br/>POST Request] --> B{Request Path}
    B -->|/mcp/*| C[MCP Protocol Handler<br/>JSON-RPC Processing]
    B -->|/api/*| D[REST API Handler<br/>Standard HTTP API]
    B -->|/health| E[Health Check<br/>System Status]

    C --> F{Method Type}
    C --> G[Protocol Validation<br/>JSON-RPC 2.0 Format]
    G --> H[Method Routing<br/>prompts/*, tools/*]
    H --> I[Handler Execution<br/>Template/Database Operations]

    D --> J[API Validation<br/>Pydantic Models]
    J --> K[Business Logic<br/>CRUD Operations]
    K --> L[Response Formatting<br/>JSON Response]

    E --> M[Health Checks<br/>Database, External Services]
    M --> N[Status Response<br/>200 OK or 503 Service Unavailable]
```

### Error Handling Flow

```mermaid
flowchart TD
    A[Request Processing] --> B{Error Type}
    B -->|Validation Error| C[Client Error<br/>400 Bad Request]
    B -->|Database Error| D[Server Error<br/>500 Internal Server Error]
    B -->|Template Error| E[Not Found<br/>404 Not Found]
    B -->|AI Service Error| F[External Service Error<br/>503 Service Unavailable]

    C --> G[Error Response<br/>Validation Details]
    D --> H[Error Response<br/>Database Error Info]
    E --> I[Error Response<br/>Template Not Found]
    F --> J[Error Response<br/>Service Unavailable]

    G --> K[Client Notification<br/>User-Friendly Error]
    H --> K
    I --> K
    J --> K
```

## 📈 Performance Control Flow

### Caching Strategy Flow

```mermaid
flowchart TD
    A[Template Request] --> B{Cache Hit}
    B -->|Yes| C[Return Cached Template<br/>Fast Response]
    B -->|No| D[Load from Database<br/>Cache Template<br/>Return Template]

    C --> E[Template Processing<br/>Variable Substitution]
    D --> E

    E --> F[Response Generation<br/>JSON Formatting]
    F --> G[Cache Update<br/>Update Access Time]
    G --> H[Return Response]
```

**Cache Invalidation**:

- **Time-based**: TTL expiration
- **Event-based**: Template updates trigger cache refresh
- **Manual**: Admin cache purge endpoints

### Async Processing Flow

```mermaid
sequenceDiagram
    participant C as Client
    participant S as FastAPI Server
    participant W as Worker Process
    participant AI as AI Service

    C->>S: Render Complex Template
    S->>W: Queue Background Task
    S->>C: Return Task ID
    C->>S: Poll for Status
    S->>W: Check Task Status
    W->>AI: Process Template (Background)
    AI->>W: Return Generated Content
    W->>S: Update Task Status
    S->>C: Return Completed Content
```

## 🎯 Critical Path Analysis

### Fastest Path: Simple Template Listing

```mermaid
flowchart LR
    A[Request] --> B[Validation] --> C[Cache Check] --> D[Database Query] --> E[Response]
    G[Total Time: ~50ms]

    B --> F[Error Path<br/>~20ms]
    F --> E
```

**Optimization Points:**

- **Cache Hit Rate**: 90%+ for frequently accessed templates
- **Database Indexing**: Optimized queries on template name/category
- **Connection Pooling**: Pre-warmed database connections

### Slowest Path: Complex Template with AI Processing

```mermaid
flowchart LR
    A[Request] --> B[Validation] --> C[Template Load] --> D[AI Processing] --> E[Response]
    G[Total Time: ~5-30s]

    B --> F[Error Path<br/>~100ms]
    F --> E
```

**Optimization Strategies:**

- **Background Processing**: Move AI calls to async workers
- **Response Streaming**: Stream partial results as available
- **Caching**: Cache common AI responses
- **Rate Limiting**: Prevent AI service overload

## 📊 Monitoring Points

### Metrics Collection Flow

```mermaid
flowchart TD
    A[Request Start] --> B[Timing Metrics<br/>Request Duration]
    B --> C[Counter Metrics<br/>Request Count by Endpoint]
    C --> D[Error Metrics<br/>Error Rate by Type]
    D --> E[Database Metrics<br/>Query Performance]
    E --> F[External Service Metrics<br/>AI API Response Times]
    F --> G[Cache Metrics<br/>Hit/Miss Rates]
    G --> H[Metrics Storage<br/>Prometheus/StatsD]
    H --> I[Monitoring Dashboard<br/>Grafana/Kibana]
```

### Health Check Flow

```mermaid
flowchart TD
    A[Health Check Request<br/>GET /health] --> B[Database Connectivity<br/>Test Connection Pool]
    B --> C[External Services<br/>AI API Endpoints]
    C --> D[Cache System<br/>Redis Connection]
    D --> E[Background Workers<br/>Celery Status]
    E --> F[Overall Status<br/>200 OK or 503 Error]
    F --> G[Status Response<br/>JSON with Details]
```

## 🔐 Security Control Flow

### Input Validation Pipeline

```mermaid
flowchart TD
    A[Raw Input<br/>JSON Payload] --> B[Format Validation<br/>JSON Schema Check]
    B --> C[Business Rules<br/>Template Name Validation]
    C --> D[Security Check<br/>SQL Injection Prevention]
    D --> E[Sanitization<br/>XSS Prevention]
    E --> F[Safe Processing<br/>Template Rendering]
    F --> G[Response Generation<br/>Safe Output]
```

### Authentication Flow

```mermaid
flowchart TD
    A[Request] --> B{Has Auth Header}
    B -->|No| C[Optional Auth<br/>Public Endpoint]
    B -->|Yes| D[JWT Validation<br/>Token Verification]
    D --> E{Role Check}
    E -->|Authorized| F[Process Request<br/>Template Access]
    E -->|Unauthorized| G[403 Forbidden<br/>Access Denied]
    G --> H[Error Response]

    C --> F
    F --> I[Success Response]
```

This comprehensive flow control analysis ensures developers understand exactly how requests are processed, where performance bottlenecks may occur, and how the system maintains security and reliability throughout the entire request lifecycle.
