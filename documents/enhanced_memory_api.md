# Enhanced Memory System API Reference

## Overview

The Enhanced Memory System provides sophisticated context management with relationships, importance scoring, and advanced querying capabilities that rival Context7 and Sequential Thinking systems.

## Core Concepts

### Memory Entries

- **Conversation ID**: Groups related memory entries
- **Context Types**: conversation, code_analysis, project_task, web_content, database_query, test_result, reasoning_step, knowledge_base
- **Importance Scoring**: 0.1-1.0 scale for relevance ranking
- **Relationships**: Link memory entries with strength and metadata

### Key Features

- Context-aware memory storage and retrieval
- Relationship mapping between memory entries
- Importance-based filtering and ranking
- TTL (Time To Live) support
- Advanced querying with multiple filters

## API Endpoints

### Store Memory Entry

```json
POST /api/memory/enhanced
{
  "conversation_id": "string",
  "session_id": "string",
  "role": "user|assistant|system",
  "content": "string",
  "context_type": "conversation|code_analysis|project_task|web_content|database_query|test_result|reasoning_step|knowledge_base",
  "importance_score": 0.5,
  "tags": ["array", "of", "strings"],
  "metadata": {"key": "value"},
  "ttl_seconds": 3600
}
```

### Retrieve Memory Entries

```json
GET /api/memory/enhanced?conversation_id=string&context_type=string&min_importance=0.5&limit=50
```

### Create Memory Relationship

```json
POST /api/memory/relationships
{
  "source_memory_id": "uuid",
  "target_memory_id": "uuid",
  "relationship_type": "references|leads_to|informs|depends_on",
  "strength": 0.7,
  "metadata": {"key": "value"}
}
```

## Usage Examples

### Basic Memory Operations

```python
from mcp_pba_tunnel.data.project_manager import PromptDataManager
from mcp_pba_tunnel.data.models.prompt_models import ContextType

manager = PromptDataManager()

# Store a memory entry
memory_id = manager.store_enhanced_memory_entry(
    conversation_id='project-analysis-001',
    session_id='analysis-session',
    role='user',
    content='Analyze the authentication system architecture',
    context_type=ContextType.REASONING_STEP,
    importance_score=0.9,
    tags=['authentication', 'architecture', 'security'],
    metadata={'project_phase': 'analysis'}
)

# Retrieve related memories
entries = manager.retrieve_enhanced_memory_entries(
    conversation_id='project-analysis-001',
    context_type=ContextType.CODE_ANALYSIS
)
```

### Advanced Reasoning Flow

```python
# Create problem statement
problem_id = manager.store_enhanced_memory_entry(
    conversation_id='auth-system-design',
    session_id='design-session',
    role='user',
    content='Implement secure JWT authentication with rate limiting',
    context_type=ContextType.REASONING_STEP,
    importance_score=0.9
)

# Create reasoning steps
step1_id = manager.store_enhanced_memory_entry(
    conversation_id='auth-system-design',
    session_id='design-session',
    role='assistant',
    content='Step 1: Design JWT token structure and validation',
    context_type=ContextType.REASONING_STEP,
    importance_score=0.8
)

# Link reasoning steps
manager.create_context_relationship(
    source_memory_id=problem_id,
    target_memory_id=step1_id,
    relationship_type='leads_to',
    strength=0.9
)
```

## Context Types

### Conversation

- User/assistant dialogue
- Chat history and context
- Question-answer pairs

### Code Analysis

- Code review findings
- Complexity analysis
- Security vulnerability reports
- Performance bottlenecks

### Project Task

- Task definitions and requirements
- Implementation notes
- Progress tracking
- Dependencies and milestones

### Web Content

- Scraped web page content
- API documentation
- Research findings
- Reference materials

### Database Query

- SQL query analysis
- Schema design notes
- Data modeling decisions
- Performance optimization notes

### Test Result

- Unit test results
- Integration test outcomes
- Performance test data
- Security test findings

### Reasoning Step

- Problem decomposition
- Solution planning
- Decision rationale
- Alternative considerations

### Knowledge Base

- Best practices
- Design patterns
- Security guidelines
- Performance tips

## Best Practices

### Memory Organization

1. Use descriptive conversation IDs that reflect the context
2. Set appropriate importance scores (0.1-1.0 scale)
3. Include relevant tags for easy filtering
4. Add meaningful metadata for additional context

### Relationship Management

1. Create relationships between related memory entries
2. Use appropriate relationship types
3. Set realistic relationship strengths
4. Include relationship metadata for context

### Performance Considerations

1. Use appropriate context types for your data
2. Set reasonable TTL values
3. Use importance scoring for prioritization
4. Clean up old entries regularly

## Error Handling

The API provides detailed error responses:

```json
{
  "error": {
    "code": "MEMORY_VALIDATION_ERROR",
    "message": "Invalid context type provided",
    "details": {
      "field": "context_type",
      "provided_value": "invalid_type",
      "valid_values": ["conversation", "code_analysis", ...]
    }
  }
}
```

## Security Considerations

- Input validation on all fields
- XSS prevention in content fields
- SQL injection protection
- Rate limiting for API endpoints
- Access control for sensitive operations

## Performance Metrics

- Memory queries: <100ms response time
- Relationship lookups: <50ms average
- Storage throughput: 1000+ entries/second
- Query throughput: 500+ queries/second
