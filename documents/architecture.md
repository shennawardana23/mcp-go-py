# 🏗️ MCP-PBA-TUNNEL - Architecture Overview

## 📋 Overview

MCP-PBA-TUNNEL (MCP Prompt-Based Architecture Tunnel) is a sophisticated FastAPI-based Model Context Protocol (MCP) server that provides standardized prompt engineering templates and AI agent integration, enabling consistent, high-quality development workflows across your organization.

## 🎯 Core System Architecture

```mermaid
graph TB
    subgraph "MCP-PBA-TUNNEL Ecosystem"
        A[MCP Client<br/>Claude/Cursor] --> B[MCP-PBA-TUNNEL<br/>FastAPI Server]
        B --> C[Prompt Engine<br/>Template Management]
        B --> D[AI Integration<br/>Multi-Model Support]
        B --> E[Database Layer<br/>psycopg Native Queries]
        B --> F[Background Tasks<br/>Celery Processing]
    end

    subgraph "Template Categories"
        G[Development<br/>Business Logic] --> H[Template Engine<br/>Variable Substitution]
        I[Architecture<br/>API Design] --> H
        J[Data<br/>Schema Design] --> H
        K[Quality<br/>Testing Strategy] --> H
        L[Communication<br/>Documentation] --> H
    end

    subgraph "AI Integration"
        M[OpenAI<br/>GPT-4/GPT-3.5] --> N[AI Gateway<br/>Request/Response]
        O[Anthropic<br/>Claude] --> N
        P[Custom Models<br/>Local/Enterprise] --> N
    end

    B --> G
    B --> I
    B --> J
    B --> K
    B --> L
    B --> M
    B --> O
    B --> P
```

## 🔧 Component Architecture

### 1. FastAPI MCP Server (`mcp_pba_tunnel/server/fastapi_mcp_server.py`)

The core FastAPI-based MCP server implementation that handles all prompt template requests and manages AI integration for prompt engineering, now enhanced with advanced tool capabilities.

**Key Components:**

- **Main Application**: FastAPI server handling MCP protocol and REST API requests
- **Request Handlers**: Route handlers for MCP and REST endpoints
- **Enhanced Tool Integration**: Advanced tools including web scraping, code analysis, terminal execution
- **Data Manager Integration**: Uses the refactored repository/service layer with enhanced memory
- **Background Tasks**: Celery integration for async processing
- **Advanced Reasoning**: Multi-step reasoning chains and context-aware planning tools

### 2. Data Models Layer (`mcp_pba_tunnel/data/models/`)

Pydantic-based data models providing type safety and validation throughout the system.

**Components:**

- **Base Models**: Core data structures with validation
- **DTOs**: Data Transfer Objects for API communication
- **Domain Models**: Business domain representations
- **Validation**: Automatic data validation and sanitization

### 3. Repository Layer (`mcp_pba_tunnel/data/repositories/`)

Database operations layer implementing the Repository pattern for clean data access.

**Components:**

- **DatabaseConfig**: Connection pooling and transaction management
- **BaseRepository**: Generic CRUD operations for all entities
- **PromptTemplateRepository**: Prompt template database operations
- **AIConfigurationRepository**: AI model configuration storage
- **Connection Management**: psycopg native queries with pooling

### 4. Service Layer (`mcp_pba_tunnel/data/services/`)

Business logic layer implementing use cases and application rules.

**Components:**

- **PromptService**: Prompt template business logic and validation
- **AIService**: AI configuration and integration logic
- **ValidationService**: Data validation utilities
- **Business Rules**: Domain-specific logic and constraints

### 5. Enhanced Memory System (`mcp_pba_tunnel/data/models/prompt_models.py`)

Sophisticated context management with relationships and importance scoring.

**Features:**

- **Context Relationships**: Link memory entries with importance-based relationships
- **Importance Scoring**: Weighted memory entries for context-aware retrieval
- **Tag-Based Organization**: Flexible categorization and filtering system
- **Metadata Enrichment**: Rich context data with timestamps and source tracking
- **Context Types**: Support for different memory categories (conversation, task, reference)

**Enhanced Memory Models:**

- **ContextRelationship**: Models relationships between memory entries
- **ContextType**: Enumeration for different memory categories
- **EnhancedMemoryEntry**: Advanced memory entry with importance scoring and tags

### 6. Advanced Tool Components

#### Web Scraping & API Integration

- **BeautifulSoup4**: HTML/XML parsing and data extraction
- **Requests/httpx**: HTTP client for API interactions
- **Data Processing**: JSON, XML, and structured data handling

#### Code Analysis Tools

- **Complexity Analysis**: Cyclomatic complexity, maintainability index
- **Code Quality Metrics**: Lines of code, duplication detection
- **Performance Analysis**: Execution time, memory usage tracking

#### Terminal Execution

- **Command Processing**: Safe command execution with timeouts
- **Environment Management**: Working directory and environment variable control
- **Output Capture**: Structured result handling and error management

#### Database Query & Analysis

- **Schema Analysis**: Table structure, relationships, and metadata extraction
- **Query Optimization**: Performance analysis and improvement suggestions
- **Data Profiling**: Statistics and pattern analysis

#### Testing & Validation Tools

- **Test Execution**: Automated test running with coverage reporting
- **Code Validation**: Linting, type checking, and security scanning
- **Performance Testing**: Load testing and benchmark analysis

### 7. Main Facade (`mcp_pba_tunnel/data/project_manager.py`)

Orchestrates the repository and service layers using the Facade pattern, now enhanced with advanced tool capabilities.

**Features:**

- **Template Management**: CRUD operations for prompt templates
- **Enhanced Memory Management**: Sophisticated context management with relationships
- **Usage Tracking**: Analytics and performance monitoring
- **Advanced Tool Integration**: Web scraping, code analysis, terminal execution
- **Project Management**: Task tracking, database tools, testing capabilities
- **AI Integration**: Connection to external AI services with advanced reasoning
- **Data Validation**: Input sanitization and validation
- **Migration Management**: Database schema evolution

**Supported Categories:**

- **Development**: Business logic and API design templates
- **Architecture**: System design and architecture templates
- **Data**: Database schema and data modeling templates
- **Quality**: Testing strategy and code quality templates
- **Communication**: Documentation and presentation templates
- **Techniques**: Advanced reasoning and planning templates

### 8. MCP Protocol Integration

Direct MCP protocol endpoints for AI assistants to interact with the prompt engineering system. No separate client needed - AI models can call the server endpoints directly.

## 🎯 Advanced Reasoning Architecture

### Context-Aware Planning System

The enhanced MCP-PBA-TUNNEL includes sophisticated reasoning capabilities:

```mermaid
graph TB
    subgraph "Advanced Reasoning Pipeline"
        A[Problem Input<br/>Complex Task] --> B[Context Gathering<br/>Memory + Relationships]
        B --> C[Multi-Step Analysis<br/>Sequential Reasoning]
        C --> D[Solution Planning<br/>Structured Approach]
        D --> E[Execution Strategy<br/>Step-by-Step Plan]
        E --> F[Validation & Refinement<br/>Quality Assurance]
    end

    subgraph "Memory Integration"
        G[Enhanced Memory<br/>Context Storage] --> B
        H[Relationship Mapping<br/>Context Linking] --> B
        I[Importance Scoring<br/>Relevance Ranking] --> C
    end

    subgraph "Tool Integration"
        J[Web Scraping<br/>External Data] --> C
        K[Code Analysis<br/>Technical Assessment] --> D
        L[Database Queries<br/>Data Validation] --> E
        M[Testing Tools<br/>Validation] --> F
    end
```

### Enhanced Tool Ecosystem

**Web Scraping & API Integration:**

- Real-time data fetching from external APIs
- HTML/XML parsing and structured data extraction
- API response processing and transformation
- Rate limiting and error handling

**Code Analysis & Quality:**

- Cyclomatic complexity analysis
- Maintainability index calculation
- Code duplication detection
- Performance profiling and optimization suggestions

**Database Tools:**

- Schema analysis and documentation
- Query performance optimization
- Data profiling and statistics
- Relationship mapping and dependency analysis

**Project Management:**

- Task breakdown and estimation
- Progress tracking and milestone management
- Resource allocation and scheduling
- Risk assessment and mitigation planning

## 🔒 Security Architecture

### Enhanced Security Model

```mermaid
graph TD
    A[Input Validation<br/>Comprehensive Sanitization] --> B[Authentication<br/>JWT Token Validation]
    B --> C[Authorization<br/>Role-Based Access Control]
    C --> D[Rate Limiting<br/>API Request Throttling]
    D --> E[Audit Logging<br/>Security Event Tracking]
    E --> F[Data Encryption<br/>Sensitive Information Protection]
    F --> G[Secure Headers<br/>HTTP Security Headers]
    G --> H[Monitoring<br/>Security Event Detection]
```

### Advanced Security Features

- **Enhanced Input Validation**: Multi-layer validation with sanitization
- **JWT Authentication**: Secure token-based authentication system
- **Role-Based Access Control**: Granular permission management
- **Rate Limiting**: Protection against abuse and DoS attacks
- **Audit Logging**: Comprehensive security event tracking
- **Data Encryption**: Encryption at rest and in transit
- **Security Headers**: HTTP security headers for web protection
- **Vulnerability Scanning**: Automated security vulnerability detection

## 🔄 Request Flow Architecture

### New Layered Architecture Flow

```mermaid
sequenceDiagram
    participant A as AI Assistant
    participant S as FastAPI Server
    participant PM as PromptDataManager
    participant PS as PromptService
    participant PR as PromptRepository
    participant DB as Database Layer
    participant AI as AI Integration

    A->>S: render_prompt(template_name, variables)
    S->>PM: render_template(template_name, variables)
    PM->>PS: validate_and_process_request()
    PS->>PR: get_template_by_name(template_name)
    PR->>DB: SELECT * FROM prompt_templates WHERE name=%s
    DB->>PR: return_template_data()
    PR->>PS: return_template_object()
    PS->>PM: validate_variables_and_render()
    PM->>AI: enhance_with_ai(optional)
    AI->>PM: return_enhanced_content()
    PM->>S: format_response()
    S->>A: return_rendered_prompt()
```

### Layer Interaction Overview

```mermaid
flowchart TD
    A[Presentation Layer<br/>FastAPI Server] --> B[Application Layer<br/>PromptDataManager Facade]
    B --> C[Business Logic Layer<br/>Service Layer]
    C --> D[Data Access Layer<br/>Repository Layer]
    D --> E[(Database Layer<br/>PostgreSQL)]

    A --> F[External APIs<br/>AI Services]
    B --> G[Cache Layer<br/>Redis/Memory]

    C --> H[Validation Layer<br/>Data Validation]
    D --> I[Connection Pool<br/>psycopg Pool]
```

## 📊 Data Flow Architecture

### Prompt Template Processing Data Flow

```mermaid
flowchart TD
    A[User Request<br/>Template Name<br/>Variables<br/>Category] --> B[Input Validation<br/>Sanitize Parameters<br/>Validate Template]
    B --> C[Template Loading<br/>Load Template Content<br/>Parse Variables]
    C --> D[Variable Processing<br/>Substitution<br/>Validation<br/>Formatting]
    D --> E[Content Generation<br/>Replace Placeholders<br/>Apply Formatting<br/>AI Enhancement]
    E --> F[Response Building<br/>Format JSON Response<br/>Add Metadata<br/>Track Usage]
    F --> G[Success Response<br/>Rendered Content<br/>Template Info<br/>Processing Stats]
```

### Data Lineage - Template Variable Flow

**Example: How `template_name` flows through the system**

```mermaid
flowchart LR
    A[Client Input<br/>template_name="business_logic"] --> B[MCP Server<br/>Request Parsing]
    B --> C[Prompt Manager<br/>Template Resolution]
    C --> D[Template Variables<br/>{{business_domain}} → "e-commerce"]
    D --> E[Content Rendering<br/>Replace Variables<br/>Format Output]
    E --> F[Response Structure<br/>JSON Response<br/>with rendered content]
```

## 🏛️ Component Structure

### Layered Architecture Components

```mermaid
graph TB
    subgraph "Presentation Layer"
        A[FastAPI Server] --> B[Request Handler]
        B --> C[Response Builder]
        A --> D[Middleware Layer<br/>CORS, Logging, Auth]
        A --> E[Route Handlers<br/>MCP & REST endpoints]
    end

    subgraph "Application Layer"
        B --> F[PromptDataManager<br/>Main Facade]
        F --> G[Service Orchestrator]
        F --> H[Data Validator]
    end

    subgraph "Business Logic Layer"
        G --> I[PromptService<br/>Template Operations]
        G --> J[AIService<br/>AI Integration]
        G --> K[ValidationService<br/>Business Rules]
    end

    subgraph "Data Access Layer"
        I --> L[PromptRepository<br/>Database Operations]
        J --> M[AIConfigurationRepository<br/>Model Settings]
        L --> N[DatabaseConfig<br/>Connection Pool]
        M --> N
    end

    subgraph "Infrastructure Layer"
        N --> O[(PostgreSQL<br/>Primary Storage)]
        F --> P[Cache Manager<br/>Redis/Memory Cache]
        P --> Q[External APIs<br/>AI Services]
    end
```

### Prompt Template Structure

```mermaid
graph TD
    A[Templates Directory] --> B[Development Templates]
    A --> C[Architecture Templates]
    A --> D[Data Templates]
    A --> E[Quality Templates]
    A --> F[Communication Templates]
    A --> G[Techniques Templates]

    B --> H[Business Logic Template]
    B --> I[API Design Template]
    C --> J[Database Schema Template]
    C --> K[System Design Template]
    D --> L[Testing Strategy Template]
    E --> M[Code Review Template]
    F --> N[Documentation Template]
    G --> O[Zero-Shot Template]
    G --> P[Chain-of-Thought Template]
```

## 🔐 Security Architecture

```mermaid
flowchart TD
    A[Input Validation] --> B[Path Sanitization]
    A --> C[Framework Validation]
    A --> D[Feature Validation]

    B --> E[Safe File Operations]
    E --> F[Directory Creation]
    E --> G[File Writing]

    C --> H[Template Loading]
    H --> I[Template Processing]
    I --> J[Variable Substitution]

    D --> K[Feature Processing]
    K --> L[Dependency Management]
    L --> M[Configuration Files]
```

## 📈 Performance Architecture

### Caching Strategy

```mermaid
graph TD
    A[Template Cache] --> B[Memory Cache<br/>Template Content]
    A --> C[File System Cache<br/>Generated Prompts]
    A --> D[Configuration Cache<br/>Template Settings]

    B --> E[Fast Template Loading]
    C --> F[Quick Prompt Access]
    D --> G[Rapid Configuration]
```

### Async Processing

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    participant P as Prompt Processor
    participant AI as AI Service

    C->>S: Render Template
    S->>P: Start Processing (Async)
    P->>AI: Enhance with AI (Background)
    S->>C: Return Template ID
    C->>S: Check Status
    S->>P: Get Progress
    P->>C: Progress Update
```

## 🚀 Deployment Architecture

### Development Setup

```mermaid
graph TD
    A[Local Development] --> B[Python Environment]
    B --> C[FastAPI Server]
    C --> D[Template Files]
    D --> E[Data Store]
    E --> F[Client Interface]

    C --> G[AI Integration<br/>(Optional)]
    G --> H[OpenAI/Anthropic<br/>API Integration]
```

### Production Deployment

```mermaid
graph TD
    A[Production Server] --> B[Docker Container]
    B --> C[FastAPI Application]
    C --> D[Volume Mounts<br/>Templates & Data]
    D --> E[Persistent Storage]
    E --> F[Prompt Processing]

    A --> G[Load Balancer<br/>(Optional)]
    G --> H[Multiple Instances]
    H --> I[High Availability]
```

## 📊 Monitoring & Observability

```mermaid
graph TD
    A[Application Metrics] --> B[Request Count]
    A --> C[Processing Time]
    A --> D[Error Rate]
    A --> E[Template Usage]

    B --> F[Prometheus<br/>Metrics Collection]
    C --> F
    D --> F
    E --> F

    F --> G[Grafana<br/>Dashboards]
    G --> H[Performance<br/>Monitoring]
    G --> I[Usage Analytics]
    G --> J[Error Tracking]
```

## 🔧 Configuration Management

```mermaid
graph TD
    A[Configuration Files] --> B[mcp_config.json<br/>Server Settings]
    A --> C[Template Config<br/>Prompt Settings]
    A --> D[Feature Config<br/>Available Features]

    B --> E[Environment Variables<br/>API Keys, Ports]
    C --> F[Template Variables<br/>Prompt Names, Paths]
    D --> G[Feature Flags<br/>Enable/Disable Features]
```

## 📚 Documentation Structure

```mermaid
graph TD
    A[Documentation] --> B[Architecture<br/>System Design]
    A --> C[API Reference<br/>MCP Protocol]
    A --> D[User Guide<br/>Usage Examples]
    A --> E[Developer Guide<br/>Contributing]
    A --> F[Deployment<br/>Production Setup]

    B --> G[Component Diagrams<br/>Mermaid Charts]
    C --> H[Request/Response<br/>Examples]
    D --> I[Code Samples<br/>Framework Usage]
    E --> J[Setup Instructions<br/>Development Environment]
    F --> K[Docker Compose<br/>Production Deployment]
```

## 🎯 Key Benefits

### For Developers

- **Rapid Prompt Creation**: Generate standardized prompt templates in seconds
- **Best Practices**: Built-in prompt engineering best practices and patterns
- **Template Categories**: Choose the right template category for your needs
- **Feature Rich**: Integrated AI enhancement and variable substitution

### For Organizations

- **Standardization**: Consistent prompt templates across teams
- **Accelerated Development**: Faster prompt creation for AI workflows
- **Quality Assurance**: Built-in validation, testing, and monitoring
- **Scalability**: Support for multiple AI models and integrations

### For AI Assistants

- **MCP Integration**: Seamless integration with Claude, Cursor, etc.
- **Context Awareness**: Full prompt context for intelligent assistance
- **Template Management**: Standardized prompt templates with AI enhancement
- **Workflow Optimization**: Track and manage prompt usage and effectiveness

## 🚀 Future Enhancements

```mermaid
graph LR
    A[Current Features] --> B[Template System<br/>6 Categories]
    A --> C[Feature Integration<br/>Database, Auth, etc.]
    A --> D[Data Management<br/>Template Tracking]

    B --> E[Custom Templates<br/>User-Defined Templates]
    C --> F[Advanced Features<br/>API Gateway, Caching]
    D --> G[Analytics Dashboard<br/>Usage Metrics]
    E --> H[Plugin System<br/>Community Extensions]
    F --> I[CI/CD Integration<br/>Automated Testing]
    G --> J[Multi-Cloud<br/>Deployment Options]
```

This architecture provides a solid foundation for AI-powered prompt template generation while maintaining flexibility for future enhancements and customizations.
