# MCP-PBA-TUNNEL 🚀

> **MCP Prompt-Based Architecture Tunnel - Standardized AI-Powered Development Workflows**

A powerful FastAPI-based Model Context Protocol (MCP) server that provides standardized prompt engineering templates and AI agent integration, enabling consistent, high-quality development workflows across your organization with advanced prompting techniques from industry best practices.

## ✨ What is MCP-PBA-TUNNEL?

MCP-PBA-TUNNEL (MCP Prompt-Based Architecture Tunnel) implements a comprehensive MCP server that leverages advanced prompt engineering techniques to provide standardized templates for common development tasks. The system integrates cutting-edge prompting strategies from promptingguide.ai and provides seamless AI agent integration for consistent, high-quality development workflows.

### 🎯 Key Features

- **🤖 Advanced AI Integration**: Seamless integration with GPT-4, Claude, and other AI models
- **📝 Standardized Templates**: Pre-built prompt templates for common development tasks
- **🏗️ Multi-Category Support**: Development, Architecture, Data, Quality, Communication
- **⚡ Template Management**: Create, update, and manage prompt templates via API
- **📊 Usage Analytics**: Track template usage and AI model performance
- **🧠 Enhanced Memory System**: Sophisticated context management with relationships and importance scoring
- **🛠️ Advanced Tool Set**: Web scraping, API integration, code analysis, file operations, terminal execution
- **🎯 Project Management**: Task tracking, database query tools, testing and validation capabilities
- **🔬 Advanced Reasoning**: Multi-step reasoning chains, context-aware planning tools
- **🔒 Production Ready**: FastAPI, psycopg, Redis, comprehensive monitoring
- **🎨 MCP Protocol**: Full MCP 2024-11-05 specification compliance

## 🏃‍♂️ Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL with psycopg native queries

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/mcp-pba-tunnel.git
cd mcp-pba-tunnel

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize PostgreSQL database
python -c "from mcp_pba_tunnel.data.project_manager import DatabaseManager; db = DatabaseManager('postgresql://postgres:password@localhost:5432/mcp_pba_tunnel'); db.run_migrations(); print('✅ PostgreSQL database initialized')"

# Start the FastAPI server
python -m mcp_pba_tunnel.server.fastapi_mcp_server
```

### Test the Server

```bash
# Health check
curl http://localhost:9001/health

# List prompt categories
curl http://localhost:9001/api/categories

# List MCP prompts
curl -X POST http://localhost:9001/mcp/prompts/list -H "Content-Type: application/json"
```

## 🛠️ Usage Examples

### Using with AI Assistants

MCP-PBA-TUNNEL integrates seamlessly with AI assistants like Claude and Cursor:

**Claude Desktop Configuration:**

```json
{
  "mcpServers": {
    "mcp-pba-tunnel": {
      "command": "python",
      "args": ["-m", "mcp_pba_tunnel.server.fastapi_mcp_server"],
      "cwd": "/path/to/mcp-pba-tunnel"
    }
  }
}
```

**Cursor Configuration:**

```json
{
  "mcpServers": {
    "mcp-pba-tunnel": {
      "command": "uv",
      "args": [
        "run",
        "--with", "mcp-pba-tunnel",
        "python",
        "-m", "mcp_pba_tunnel.server.fastapi_mcp_server"
      ],
      "cwd": "/path/to/mcp-pba-tunnel"
    }
  }
}
```

### Advanced Prompting Techniques

MCP-PBA-TUNNEL implements industry-standard prompting techniques from promptingguide.ai, including:

#### Available Techniques

- **Zero-Shot**: Direct prompting without examples
- **Few-Shot**: Prompting with a few examples
- **Chain-of-Thought**: Step-by-step reasoning
- **Tree of Thoughts**: Multi-path reasoning
- **ReAct**: Reasoning + Acting
- **Self-Consistency**: Multiple reasoning paths
- **Meta Prompting**: Prompts that generate other prompts
- **Prompt Chaining**: Sequential prompt execution

#### Memory Management Tools

**Backend Memory (`memory_be`)**:

```json
{
  "jsonrpc": "2.0",
  "id": "memory-store",
  "method": "tools/call",
  "params": {
    "name": "memory_be",
    "arguments": {
      "operation": "store",
      "conversation_id": "chat_123",
      "session_id": "user_456",
      "data": {
        "role": "user",
        "content": "How do I create a REST API?",
        "metadata": {"timestamp": "2024-01-15T10:30:00Z"}
      }
    }
  }
}
```

**Frontend Memory (`memory_fe`)**:

```json
{
  "jsonrpc": "2.0",
  "id": "memory-history",
  "method": "tools/call",
  "params": {
    "name": "memory_fe",
    "arguments": {
      "action": "get_history",
      "session_id": "user_456"
    }
  }
}
```

#### Prompt Chain Management

**Backend Chain Execution (`prompt_chain_be`)**:

```json
{
  "jsonrpc": "2.0",
  "id": "chain-execute",
  "method": "tools/call",
  "params": {
    "name": "prompt_chain_be",
    "arguments": {
      "chain_id": "api_design_chain",
      "steps": [
        {"prompt_id": "business_logic", "inputs": {"domain": "ecommerce"}},
        {"prompt_id": "api_design", "inputs": {"resource_name": "products"}},
        {"prompt_id": "database_schema", "inputs": {"entity_name": "product"}}
      ],
      "inputs": {"business_domain": "retail"}
    }
  }
}
```

**Frontend Chain Visualization (`prompt_chain_fe`)**:

```json
{
  "jsonrpc": "2.0",
  "id": "chain-visualize",
  "method": "tools/call",
  "params": {
    "name": "prompt_chain_fe",
    "arguments": {
      "chain_id": "api_design_chain",
      "visualize": true
    }
  }
}
```

#### Technique Rendering

```json
{
  "jsonrpc": "2.0",
  "id": "technique-render",
  "method": "tools/call",
  "params": {
    "name": "render_technique",
    "arguments": {
      "technique": "chain_of_thought",
      "variables": {
        "problem_statement": "Calculate the sum of numbers from 1 to 100",
        "reasoning_steps": "Use the formula for the sum of an arithmetic series: n(n+1)/2",
        "final_answer_format": "The sum is {result}"
      }
    }
  }
}
```

### Development Workflow

```bash
# 1. Start the development server
python -m mcp_pba_tunnel.server.fastapi_mcp_server

# 2. Test MCP protocol
curl -X POST http://localhost:9001/mcp/prompts/list \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": "test", "method": "prompts/list", "params": {}}'

# 3. Create custom templates
curl -X POST http://localhost:9001/api/prompts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_custom_template",
    "description": "My custom prompt template",
    "category": "development",
    "template_content": "Custom template for {{domain}}",
    "variables": ["domain"]
  }'

# 4. Run tests
pytest tests/

# 5. Check code quality
make pre-commit
```

### Template Categories

| Category | Description | Use Cases |
|----------|-------------|-----------|
| **Development** | Business logic implementation | Code generation, algorithm design |
| **Architecture** | System design and patterns | API design, database schema |
| **Data** | Data processing and analytics | ETL pipelines, data modeling |
| **Quality** | Testing and code quality | Test strategies, code review |
| **Communication** | Documentation and reporting | Technical docs, user guides |

### Advanced Enhanced Capabilities

MCP-PBA-TUNNEL now includes sophisticated AI-powered tools that rival Context7 and Sequential Thinking:

#### 🧠 Enhanced Memory System with Context Management

**Sophisticated Context Relationships:**

```python
from mcp_pba_tunnel.data.project_manager import PromptDataManager

manager = PromptDataManager()

# Store enhanced memory with relationships
memory_id = manager.store_enhanced_memory_entry(
    conversation_id="chat_123",
    session_id="user_456",
    role="user",
    content="How do I create a REST API?",
    context_type="conversation",
    importance_score=0.8,
    tags=["api", "development", "question"],
    relationships=["previous_context_id"],
    metadata={"source": "user_query", "timestamp": "2024-01-15T10:30:00Z"}
)
```

**Context-Aware Memory Retrieval:**

```json
{
  "jsonrpc": "2.0",
  "id": "enhanced-memory-query",
  "method": "tools/call",
  "params": {
    "name": "enhanced_memory",
    "arguments": {
      "operation": "query",
      "conversation_id": "chat_123",
      "context_type": "conversation",
      "importance_threshold": 0.6,
      "relationship_filter": "related_to_api_design"
    }
  }
}
```

#### 🛠️ Advanced Tool Set

**Web Scraping & API Integration:**

```json
{
  "jsonrpc": "2.0",
  "id": "web-scraping",
  "method": "tools/call",
  "params": {
    "name": "web_scraper",
    "arguments": {
      "operation": "scrape",
      "url": "https://api.github.com/repos/example/repo",
      "extract": ["name", "description", "stargazers_count"],
      "format": "json"
    }
  }
}
```

**Code Analysis Tools:**

```json
{
  "jsonrpc": "2.0",
  "id": "code-analysis",
  "method": "tools/call",
  "params": {
    "name": "code_analyzer",
    "arguments": {
      "operation": "analyze",
      "file_path": "/path/to/code.py",
      "analysis_type": "complexity",
      "metrics": ["cyclomatic_complexity", "maintainability_index", "lines_of_code"]
    }
  }
}
```

**Terminal Execution:**

```json
{
  "jsonrpc": "2.0",
  "id": "terminal-exec",
  "method": "tools/call",
  "params": {
    "name": "terminal_executor",
    "arguments": {
      "command": "python -m pytest tests/ -v --cov=src",
      "working_directory": "/path/to/project",
      "environment": {"PYTHONPATH": "/path/to/src"},
      "timeout": 300
    }
  }
}
```

#### 🎯 Project Management & Task Tracking

**Database Query & Analysis:**

```json
{
  "jsonrpc": "2.0",
  "id": "db-query",
  "method": "tools/call",
  "params": {
    "name": "database_analyzer",
    "arguments": {
      "operation": "query",
      "query": "SELECT table_name, column_name, data_type FROM information_schema.columns WHERE table_schema = 'public'",
      "analysis_type": "schema_analysis",
      "output_format": "json"
    }
  }
}
```

**Testing & Validation Tools:**

```json
{
  "jsonrpc": "2.0",
  "id": "test-runner",
  "method": "tools/call",
  "params": {
    "name": "test_validator",
    "arguments": {
      "operation": "run_tests",
      "test_directory": "/path/to/tests",
      "test_pattern": "*.py",
      "coverage_threshold": 85,
      "output_format": "detailed"
    }
  }
}
```

#### 🔬 Advanced Reasoning & Planning

**Multi-Step Reasoning Chains:**

```json
{
  "jsonrpc": "2.0",
  "id": "reasoning-chain",
  "method": "tools/call",
  "params": {
    "name": "advanced_reasoning",
    "arguments": {
      "operation": "reasoning_chain",
      "problem_statement": "Design a microservices architecture for an e-commerce platform",
      "reasoning_steps": [
        "Analyze business requirements",
        "Identify service boundaries",
        "Design communication patterns",
        "Plan data consistency strategies",
        "Define monitoring and observability"
      ],
      "context_data": "Previous architectural decisions and constraints",
      "output_format": "structured_design_document"
    }
  }
}
```

### AI Model Integration

MCP-PBA-TUNNEL supports multiple AI models with advanced prompting techniques:

```python
# Advanced prompting with different models
from mcp_pba_tunnel.data.project_manager import PromptDataManager

manager = PromptDataManager()

# Chain-of-Thought prompting
cot_prompt = manager.render_prompt_template(
    "business_logic_implementation",
    {
        "business_domain": "e-commerce",
        "requirements": "Implement user authentication system",
        "reasoning_steps": "5",
        "output_format": "Python Flask with detailed comments"
    }
)

# Few-shot prompting
few_shot_prompt = manager.render_prompt_template(
    "api_design",
    {
        "resource_name": "products",
        "examples": "3",
        "format": "REST API specification"
    }
)

# Advanced reasoning chain prompting
reasoning_prompt = manager.render_prompt_template(
    "advanced_reasoning_chain",
    {
        "problem_statement": "Optimize database performance for high-traffic API",
        "context_data": "Current schema and query patterns",
        "constraints": ["Minimize schema changes", "Maintain backward compatibility"],
        "reasoning_steps": ["Analyze current performance", "Identify bottlenecks", "Propose solutions", "Evaluate trade-offs"],
        "final_answer_format": "Detailed optimization plan with implementation steps"
    }
)
```

## 📊 Monitoring & Analytics

MCP-PBA-TUNNEL provides comprehensive monitoring and analytics:

```bash
# Get usage statistics
curl http://localhost:9001/api/stats

# Monitor health status
curl http://localhost:9001/health

# View template categories
curl http://localhost:9001/api/categories
```

## 🎯 Design Patterns

MCP-PBA-TUNNEL implements modern Python design patterns for maintainable and scalable architecture:

- **Factory Pattern**: Template creation and management
- **Decorator Pattern**: Prompt enhancement and validation
- **Observer Pattern**: Event-driven updates and notifications
- **Singleton Pattern**: Shared resources like caching
- **Facade Pattern**: Simplified interfaces for complex operations
- **Builder Pattern**: Complex prompt construction
- **Command Pattern**: Encapsulated operations and undo support

For detailed implementation, see [Design Patterns Documentation](documents/design-patterns.md).

## 🏗️ Architecture

### Core Components

```mermaid
graph TB
    subgraph "MCP-PBA-TUNNEL"
        A[FastAPI Server] --> B[Prompt Engine]
        A --> C[Database Layer]
        A --> D[AI Integration]
        A --> E[Background Tasks]

        B --> F[Template Manager]
        B --> G[Variable Processor]
        C --> H[psycopg Native Queries]
        D --> I[OpenAI/Anthropic]
        E --> J[Redis/Celery]
    end

    subgraph "Data Storage"
        H --> K[(PostgreSQL)]
        J --> L[(Redis)]
    end
```

## 🚀 Installation

### Option 1: From Source (Recommended)

```bash
# Clone repository
git clone https://github.com/your-org/mcp-pba-tunnel.git
cd mcp-pba-tunnel

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Initialize PostgreSQL database
python -c "from mcp_pba_tunnel.data.project_manager import DatabaseManager; db = DatabaseManager('postgresql://postgres:password@localhost:5432/mcp_pba_tunnel'); db.run_migrations(); print('✅ PostgreSQL database initialized')"

# Start server
python -m mcp_pba_tunnel.server.fastapi_mcp_server
```

### Option 2: Using uv (Modern Python Package Manager)

```bash
# Clone and setup
git clone https://github.com/your-org/mcp-pba-tunnel.git
cd mcp-pba-tunnel

# Install with uv
uv venv
uv pip install -e .

# Run with uv
uv run python -m mcp_pba_tunnel.server.fastapi_mcp_server
```

### Option 3: Docker

```bash
# Build and run with Docker
docker build -t mcp-pba-tunnel .
docker run -p 9001:9001 mcp-pba-tunnel
```

## 🧪 Testing

MCP-PBA-TUNNEL includes comprehensive testing:

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test categories
pytest tests/ -k "database"
pytest tests/ -k "mcp"

# Performance testing
pytest tests/ -k "performance" --tb=short
```

## 📈 Performance & Scaling

### Production Deployment

```bash
# Using gunicorn with uvicorn workers
gunicorn mcp_pba_tunnel.server.fastapi_mcp_server:create_app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:9001

# With Docker Compose
docker-compose up -d

# Load balancing with multiple instances
gunicorn mcp_pba_tunnel.server.fastapi_mcp_server:create_app -w 8 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:9001
```

### Monitoring

- **Health Checks**: `/health` endpoint for load balancers
- **Metrics**: Request timing, error rates, usage statistics
- **Logging**: Structured JSON logging with configurable levels
- **Tracing**: Request tracing for debugging and optimization

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md).

### Development Setup

```bash
# Fork and clone
git clone https://github.com/your-username/mcp-pba-tunnel.git
cd mcp-pba-tunnel

# Setup development environment
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"

# Run pre-commit checks
make pre-commit

# Create a feature branch
git checkout -b feature/your-feature-name
```

### Code Standards

- **Python 3.11+** with type hints
- **Ruff** for linting and formatting
- **MyPy** for type checking
- **Pytest** for testing
- **Pre-commit hooks** for quality gates

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** for the amazing web framework
- **psycopg** for native PostgreSQL queries and connection pooling
- **Pydantic** for data validation
- **OpenAI & Anthropic** for AI model APIs
- **MCP Community** for the protocol specification
- **Prompt Engineering Guide** for advanced prompting techniques

## 📞 Support

- **Documentation**: [GitHub Pages](https://your-org.github.io/mcp-pba-tunnel)
- **Issues**: [GitHub Issues](https://github.com/your-org/mcp-pba-tunnel/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/mcp-pba-tunnel/discussions)
- **Email**: <support@mcp-pba-tunnel.dev>

---

<div align="center">

**MCP-PBA-TUNNEL** - *Empowering AI with Standardized, High-Quality Prompt Engineering*

[🏃‍♂️ Quick Start](#🏃‍♂️-quick-start) • [📖 Documentation](documents/) • [🛠️ Usage Examples](#🛠️-usage-examples) • [🤝 Contribute](CONTRIBUTING.md)

</div>
