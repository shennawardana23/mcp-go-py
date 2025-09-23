"""
Business logic service for prompt template operations
"""

import logging
from typing import Dict, List, Any, Optional
from uuid import UUID

from ..models import (
    PromptTemplate, PromptTemplateCreate, PromptTemplateUpdate,
    PromptUsage, GeneratedContent, MemoryEntry
)
from ..repositories import (
    PromptTemplateRepository, PromptUsageRepository,
    GeneratedContentRepository, MemoryRepository
)
from ..validation import DataValidator

logger = logging.getLogger(__name__)


class PromptService:
    """Service for prompt template business logic"""

    def __init__(self):
        self.template_repository = PromptTemplateRepository()
        self.usage_repository = PromptUsageRepository()
        self.content_repository = GeneratedContentRepository()
        self.memory_repository = MemoryRepository()

    def create_template(self, template_data: Dict[str, Any]) -> PromptTemplate:
        """Create a new prompt template with validation"""
        # Validate input data
        errors = DataValidator.validate_prompt_template_data(template_data)
        if errors:
            raise ValueError(f"Validation errors: {', '.join(errors)}")

        # Create template object
        template = PromptTemplate(**template_data)

        # Save to database
        self.template_repository.create(template)

        logger.info(f"Created prompt template: {template.name}")
        return template

    def get_template(self, template_id: UUID) -> Optional[PromptTemplate]:
        """Get a prompt template by ID"""
        data = self.template_repository.get_by_id(template_id)
        if data:
            return PromptTemplate(**data)
        return None

    def get_template_by_name(self, name: str) -> Optional[PromptTemplate]:
        """Get a prompt template by name"""
        data = self.template_repository.get_by_name(name)
        if data:
            return PromptTemplate(**data)
        return None

    def list_templates(self, category: Optional[str] = None) -> List[PromptTemplate]:
        """List all active prompt templates"""
        templates_data = self.template_repository.list_all(category)
        return [PromptTemplate(**data) for data in templates_data]

    def update_template(self, template_id: UUID, updates: Dict[str, Any]) -> bool:
        """Update a prompt template"""
        # Validate updates if they contain template data
        if any(key in updates for key in ['name', 'description', 'category', 'template_content', 'variables']):
            errors = DataValidator.validate_prompt_template_data(updates)
            if errors:
                raise ValueError(f"Validation errors: {', '.join(errors)}")

        success = self.template_repository.update(template_id, updates)

        if success:
            logger.info(f"Updated prompt template: {template_id}")

        return success

    def delete_template(self, template_id: UUID) -> bool:
        """Soft delete a prompt template"""
        return self.template_repository.delete(template_id)

    def render_template(self, template_name: str, variables: Dict[str, Any]) -> str:
        """Render a prompt template with variables"""
        template = self.get_template_by_name(template_name)

        if not template:
            raise ValueError(f"Template not found: {template_name}")

        if not template.is_active:
            raise ValueError(f"Template is not active: {template_name}")

        content = template.template_content

        # Replace variables in the template
        for var_name, var_value in variables.items():
            if var_name in template.variables:
                placeholder = f"{{{{{var_name}}}}}"
                content = content.replace(placeholder, str(var_value))

        return content

    def record_usage(self, prompt_id: UUID, ai_model: str, response_time: int, success: bool = True):
        """Record prompt usage statistics"""
        self.usage_repository.record_usage(prompt_id, ai_model, response_time, success)

    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get comprehensive usage statistics"""
        return self.usage_repository.get_usage_statistics()

    def get_categories(self) -> List[str]:
        """Get all available prompt categories"""
        return self.template_repository.get_categories()

    def get_templates_by_category(self, category: str) -> List[PromptTemplate]:
        """Get all templates in a specific category"""
        return self.list_templates(category=category)

    def store_generated_content(
        self,
        prompt_id: UUID,
        ai_model: str,
        input_variables: Dict[str, Any],
        generated_content: str,
        tokens_used: int,
        response_time: int
    ) -> str:
        """Store generated content"""
        content = GeneratedContent(
            prompt_id=prompt_id,
            ai_model=ai_model,
            input_variables=input_variables,
            generated_content=generated_content,
            tokens_used=tokens_used,
            response_time=response_time
        )

        return self.content_repository.create(content)

    def get_generated_content(self, prompt_id: UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """Get generated content for a prompt"""
        return self.content_repository.get_by_prompt_id(prompt_id, limit)

    def store_memory_entry(
        self,
        conversation_id: str,
        session_id: str,
        role: str,
        content: str,
        entry_metadata: Optional[Dict[str, Any]] = None,
        ttl_seconds: int = 3600
    ) -> str:
        """Store a memory entry for conversation history"""
        entry = MemoryEntry(
            conversation_id=conversation_id,
            session_id=session_id,
            role=role,
            content=content,
            entry_metadata=entry_metadata,
            ttl_seconds=ttl_seconds
        )

        return self.memory_repository.create(entry)

    def retrieve_memory_entries(self, conversation_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve memory entries for a conversation"""
        return self.memory_repository.get_by_conversation(conversation_id, limit)

    def clear_memory_entries(self, conversation_id: str) -> int:
        """Clear all memory entries for a conversation"""
        return self.memory_repository.delete_by_conversation(conversation_id)