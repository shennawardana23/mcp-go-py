#!/usr/bin/env python3
"""
Design Patterns Implementation for MCP-PBA-TUNNEL
Based on https://refactoring.guru/design-patterns/python

This module demonstrates the implementation of common design patterns
in the context of the MCP Prompt Engineering system.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import threading
import time
from contextlib import contextmanager


# =================== CREATIONAL PATTERNS ===================

class TemplateFactory:
    """
    FACTORY PATTERN
    Provides a way to create different types of prompt templates
    without specifying the exact classes of objects that will be created.
    """

    @staticmethod
    def create_template(template_type: str, **kwargs) -> 'PromptTemplate':
        """Factory method to create different template types"""
        templates = {
            'business_logic': BusinessLogicTemplate,
            'api_design': APIDesignTemplate,
            'database_schema': BusinessLogicTemplate,  # Using BusinessLogicTemplate as base
            'testing_strategy': BusinessLogicTemplate,  # Using BusinessLogicTemplate as base
            'documentation': BusinessLogicTemplate  # Using BusinessLogicTemplate as base
        }

        if template_type not in templates:
            raise ValueError(f"Unknown template type: {template_type}")

        return templates[template_type](**kwargs)


class PromptTemplate(ABC):
    """Abstract base class for all prompt templates"""

    def __init__(self, name: str, description: str, category: str):
        self.name = name
        self.description = description
        self.category = category
        self.created_at = datetime.now()

    @abstractmethod
    def render(self, variables: Dict[str, Any]) -> str:
        """Render the template with given variables"""
        pass

    def validate(self) -> bool:
        """Validate template structure"""
        return len(self.name) > 0 and len(self.description) > 0


class BusinessLogicTemplate(PromptTemplate):
    """Concrete implementation for business logic templates"""

    def __init__(self, **kwargs):
        super().__init__(
            name=kwargs.get('name', 'business_logic_template'),
            description=kwargs.get('description', 'Business logic implementation template'),
            category='development'
        )
        self.business_domain = kwargs.get('business_domain', '')
        self.requirements = kwargs.get('requirements', '')
        self.constraints = kwargs.get('constraints', '')

    def render(self, variables: Dict[str, Any]) -> str:
        return f"""
You are an expert {self.business_domain} developer.

Requirements:
{self.requirements}

Constraints:
{self.constraints}

Implement the business logic following best practices for:
- Code organization and structure
- Error handling and validation
- Performance optimization
- Security considerations

Variables to use:
{variables}
"""


class APIDesignTemplate(PromptTemplate):
    """Concrete implementation for API design templates"""

    def __init__(self, **kwargs):
        super().__init__(
            name=kwargs.get('name', 'api_design_template'),
            description=kwargs.get('description', 'API design template'),
            category='architecture'
        )
        self.resource_name = kwargs.get('resource_name', '')
        self.operations = kwargs.get('operations', [])

    def render(self, variables: Dict[str, Any]) -> str:
        return f"""
Design a REST API for the {self.resource_name} resource.

Operations to implement:
{', '.join(self.operations)}

Requirements:
- Follow REST principles
- Use proper HTTP status codes
- Include request/response examples
- Consider authentication and authorization

Variables: {variables}
"""


# =================== STRUCTURAL PATTERNS ===================

class PromptRenderer:
    """
    DECORATOR PATTERN
    Adds additional functionality to prompt templates without modifying their structure
    """

    def __init__(self, template: PromptTemplate):
        self._template = template

    def render(self, variables: Dict[str, Any]) -> str:
        """Basic rendering"""
        return self._template.render(variables)

    def render_with_ai_enhancement(self, variables: Dict[str, Any]) -> str:
        """Enhanced rendering with AI suggestions"""
        base_prompt = self.render(variables)
        return f"{base_prompt}\n\n--- AI Enhancement ---\nConsider these additional aspects..."

    def render_with_validation(self, variables: Dict[str, Any]) -> str:
        """Rendering with input validation"""
        if not self._template.validate():
            raise ValueError("Template validation failed")

        return self.render(variables)


class MemoryAdapter:
    """
    ADAPTER PATTERN
    Converts the interface of a class into another interface that clients expect
    """

    def __init__(self, memory_manager):
        self.memory_manager = memory_manager

    def get_conversation_history(self, conversation_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Adapt memory entries to conversation format"""
        entries = self.memory_manager.retrieve_memory_entries(conversation_id, limit)

        # Adapt the format
        return [
            {
                'role': entry['role'],
                'content': entry['content'],
                'timestamp': entry['timestamp']
            }
            for entry in entries
        ]


# =================== BEHAVIORAL PATTERNS ===================

class PromptChain:
    """
    CHAIN OF RESPONSIBILITY PATTERN
    Allows passing requests along a chain of handlers
    """

    def __init__(self):
        self.handlers: List['ChainHandler'] = []
        self.current_handler = 0

    def add_handler(self, handler: 'ChainHandler'):
        self.handlers.append(handler)

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process request through the chain"""
        if self.current_handler < len(self.handlers):
            handler = self.handlers[self.current_handler]
            self.current_handler += 1
            return handler.handle(request)
        return request


class ChainHandler(ABC):
    """Abstract handler for the chain"""

    @abstractmethod
    def handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        pass


class TemplateValidationHandler(ChainHandler):
    """Validates template and variables"""

    def handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        template_name = request.get('template_name')
        variables = request.get('variables', {})

        if not template_name or not variables:
            raise ValueError("Template name and variables are required")

        return request


class TemplateRenderingHandler(ChainHandler):
    """Renders the template with variables"""

    def __init__(self, template_manager):
        self.template_manager = template_manager

    def handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        template_name = request['template_name']
        variables = request['variables']

        rendered_prompt = self.template_manager.render_prompt_template(template_name, variables)
        request['rendered_prompt'] = rendered_prompt

        return request


class AIEnhancementHandler(ChainHandler):
    """Enhances the prompt with AI suggestions"""

    def __init__(self, ai_service):
        self.ai_service = ai_service

    def handle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        rendered_prompt = request['rendered_prompt']

        # Enhance with AI
        enhanced_prompt = self.ai_service.enhance_prompt(rendered_prompt)
        request['enhanced_prompt'] = enhanced_prompt

        return request


class PromptCommand:
    """
    COMMAND PATTERN
    Encapsulates a request as an object, allowing for parameterization
    of clients with queues, requests, and operations.
    """

    def __init__(self, action: str, parameters: Dict[str, Any]):
        self.action = action
        self.parameters = parameters
        self.timestamp = datetime.now()

    def execute(self) -> Dict[str, Any]:
        """Execute the command"""
        if self.action == 'render_template':
            return self._render_template()
        elif self.action == 'list_categories':
            return self._list_categories()
        elif self.action == 'get_statistics':
            return self._get_statistics()
        else:
            raise ValueError(f"Unknown action: {self.action}")

    def _render_template(self) -> Dict[str, Any]:
        # Implementation would call template manager
        return {"status": "rendered", "template": self.parameters.get('name')}

    def _list_categories(self) -> Dict[str, Any]:
        # Implementation would call template manager
        return {"status": "categories_listed", "categories": []}

    def _get_statistics(self) -> Dict[str, Any]:
        # Implementation would call statistics service
        return {"status": "statistics_retrieved", "stats": {}}

    def undo(self) -> Dict[str, Any]:
        """Undo the command if possible"""
        return {"status": "undone", "action": self.action}


class PromptObserver:
    """
    OBSERVER PATTERN
    Defines a one-to-many dependency between objects so that when one object
    changes state, all its dependents are notified and updated automatically.
    """

    def __init__(self):
        self._observers: List['Observer'] = []

    def attach(self, observer: 'Observer'):
        """Attach an observer"""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: 'Observer'):
        """Detach an observer"""
        self._observers.remove(observer)

    def notify(self, event: str, data: Dict[str, Any]):
        """Notify all observers of an event"""
        for observer in self._observers:
            observer.update(event, data)


class Observer(ABC):
    """Abstract observer interface"""

    @abstractmethod
    def update(self, event: str, data: Dict[str, Any]):
        pass


class UsageTracker(Observer):
    """Tracks prompt usage statistics"""

    def update(self, event: str, data: Dict[str, Any]):
        if event == 'template_rendered':
            self._track_usage(data)

    def _track_usage(self, data: Dict[str, Any]):
        template_name = data.get('template_name')
        ai_model = data.get('ai_model')
        response_time = data.get('response_time', 0)

        # Track usage statistics
        print(f"Template {template_name} used with {ai_model}, response time: {response_time}ms")


class CacheInvalidator(Observer):
    """Invalidates cache when templates are updated"""

    def update(self, event: str, data: Dict[str, Any]):
        if event == 'template_updated':
            self._invalidate_cache(data.get('template_id'))

    def _invalidate_cache(self, template_id: str):
        # Invalidate cached templates
        print(f"Cache invalidated for template: {template_id}")


# =================== CONCURRENCY PATTERNS ===================

class PromptCache:
    """
    SINGLETON PATTERN
    Ensures that only one instance of the cache exists
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_cache'):
            self._cache: Dict[str, Any] = {}
            self._ttl: Dict[str, float] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired"""
        if key in self._cache:
            if time.time() < self._ttl.get(key, 0):
                return self._cache[key]
            else:
                # Expired, remove from cache
                del self._cache[key]
                del self._ttl[key]
        return None

    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Set cache value with TTL"""
        self._cache[key] = value
        self._ttl[key] = time.time() + ttl_seconds

    def clear(self):
        """Clear all cache"""
        self._cache.clear()
        self._ttl.clear()


# =================== ENTERPRISE PATTERNS ===================

class PromptService:
    """
    FACADE PATTERN
    Provides a simplified interface to a complex subsystem
    """

    def __init__(self, template_manager, ai_service, memory_manager):
        self.template_manager = template_manager
        self.ai_service = ai_service
        self.memory_manager = memory_manager
        self.cache = PromptCache()
        self.observer = PromptObserver()

    def render_enhanced_prompt(
        self,
        template_name: str,
        variables: Dict[str, Any],
        conversation_id: str = None
    ) -> Dict[str, Any]:
        """
        Simplified interface for rendering enhanced prompts
        """
        # Check cache first
        cache_key = f"{template_name}:{hash(str(variables))}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # Render template
        rendered = self.template_manager.render_prompt_template(template_name, variables)

        # Enhance with AI
        enhanced = self.ai_service.enhance_prompt(rendered)

        # Store in memory if conversation_id provided
        if conversation_id:
            self.memory_manager.store_memory_entry(
                conversation_id=conversation_id,
                session_id="default",
                role="system",
                content=enhanced
            )

        result = {
            "original_prompt": rendered,
            "enhanced_prompt": enhanced,
            "template_name": template_name,
            "variables": variables
        }

        # Cache result
        self.cache.set(cache_key, result)

        # Notify observers
        self.observer.notify('template_rendered', {
            'template_name': template_name,
            'variables': variables
        })

        return result

    def get_prompt_categories(self) -> List[str]:
        """Get available prompt categories"""
        return self.template_manager.get_available_categories()

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return self.template_manager.get_usage_statistics()


# =================== UTILITY PATTERNS ===================

@contextmanager
def database_transaction(session_factory):
    """
    Context manager for database transactions
    """
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


class PromptBuilder:
    """
    BUILDER PATTERN
    Separates the construction of a complex object from its representation
    """

    def __init__(self):
        self._parts: List[str] = []

    def add_section(self, title: str, content: str):
        """Add a section to the prompt"""
        self._parts.append(f"## {title}\n{content}")
        return self

    def add_variable(self, name: str, value: Any):
        """Add a variable definition"""
        self._parts.append(f"**{name}**: {value}")
        return self

    def add_instruction(self, instruction: str):
        """Add an instruction"""
        self._parts.append(f"**Instruction**: {instruction}")
        return self

    def build(self) -> str:
        """Build the final prompt"""
        return "\n\n".join(self._parts)


# =================== EXAMPLE USAGE ===================

def demonstrate_patterns():
    """Demonstrate the implemented design patterns"""

    print("=== DESIGN PATTERNS DEMONSTRATION ===\n")

    # Factory Pattern
    print("1. FACTORY PATTERN:")
    template = TemplateFactory.create_template(
        'business_logic',
        name='user_auth_template',
        description='User authentication business logic',
        business_domain='e-commerce'
    )
    print(f"Created template: {template.name}")

    # Decorator Pattern
    print("\n2. DECORATOR PATTERN:")
    renderer = PromptRenderer(template)
    enhanced_prompt = renderer.render_with_ai_enhancement({})
    print(f"Enhanced prompt length: {len(enhanced_prompt)}")

    # Singleton Pattern
    print("\n3. SINGLETON PATTERN:")
    cache1 = PromptCache()
    cache2 = PromptCache()
    print(f"Same instance: {cache1 is cache2}")

    # Builder Pattern
    print("\n4. BUILDER PATTERN:")
    builder = PromptBuilder()
    prompt = (builder
              .add_section("Context", "You are building an API")
              .add_variable("framework", "FastAPI")
              .add_instruction("Follow REST principles")
              .build())
    print(f"Built prompt: {prompt[:100]}...")

    # Command Pattern
    print("\n5. COMMAND PATTERN:")
    command = PromptCommand('render_template', {'name': 'test'})
    result = command.execute()
    print(f"Command result: {result}")

    # Observer Pattern
    print("\n6. OBSERVER PATTERN:")
    observer = PromptObserver()
    tracker = UsageTracker()
    observer.attach(tracker)
    observer.notify('template_rendered', {'template_name': 'test'})
    print("Observer notified successfully")

    print("\n=== ALL PATTERNS DEMONSTRATED ===")


if __name__ == "__main__":
    demonstrate_patterns()
