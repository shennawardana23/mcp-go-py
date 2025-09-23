"""
Business logic service for prompt template operations
"""

import logging
from typing import Dict, List, Any, Optional
from uuid import UUID

from ..models import (
    PromptTemplate, PromptTemplateCreate, PromptTemplateUpdate,
    PromptUsage, GeneratedContent, MemoryEntry,
    ContextRelationship, ContextRelationshipCreate,
    EnhancedMemoryEntry, EnhancedMemoryEntryCreate
)
from ..repositories import (
    PromptTemplateRepository, PromptUsageRepository,
    GeneratedContentRepository, MemoryRepository,
    EnhancedMemoryRepository, ContextRelationshipRepository
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
        self.enhanced_memory_repository = EnhancedMemoryRepository()
        self.context_relationship_repository = ContextRelationshipRepository()

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

    def store_enhanced_memory_entry(
        self,
        conversation_id: str,
        session_id: str,
        role: str,
        content: str,
        context_type: str,
        importance_score: float = 0.5,
        tags: List[str] = None,
        relationships: List[str] = None,
        metadata: Dict[str, Any] = None,
        ttl_seconds: int = 3600
    ) -> str:
        """Store an enhanced memory entry with sophisticated context management"""
        entry = EnhancedMemoryEntry(
            conversation_id=conversation_id,
            session_id=session_id,
            role=role,
            content=content,
            context_type=context_type,
            importance_score=importance_score,
            tags=tags or [],
            relationships=relationships or [],
            metadata=metadata or {},
            ttl_seconds=ttl_seconds
        )

        return self.enhanced_memory_repository.create(entry)

    def retrieve_enhanced_memory_entries(
        self,
        conversation_id: str,
        context_type: str = None,
        tags: List[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retrieve enhanced memory entries with advanced filtering"""
        if context_type:
            return self.enhanced_memory_repository.get_by_context_type(context_type, limit)
        elif tags:
            return self.enhanced_memory_repository.search_by_tags(tags, limit)
        else:
            return self.enhanced_memory_repository.get_by_conversation(conversation_id, limit)

    def get_related_memories(self, memory_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get memories related to a specific memory entry"""
        try:
            memory_uuid = UUID(memory_id)
            return self.enhanced_memory_repository.get_related_memories(memory_uuid, limit)
        except ValueError:
            logger.error(f"Invalid memory ID format: {memory_id}")
            return []

    def create_context_relationship(
        self,
        source_memory_id: str,
        target_memory_id: str,
        relationship_type: str,
        strength: float = 1.0,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Create a context relationship between memory entries"""
        try:
            source_uuid = UUID(source_memory_id)
            target_uuid = UUID(target_memory_id)

            relationship = ContextRelationship(
                source_memory_id=source_uuid,
                target_memory_id=target_uuid,
                relationship_type=relationship_type,
                strength=strength,
                metadata=metadata or {}
            )

            return self.context_relationship_repository.create(relationship)
        except ValueError as e:
            logger.error(f"Invalid UUID format: {e}")
            raise

    def get_context_relationships(self, memory_id: str) -> List[Dict[str, Any]]:
        """Get all context relationships for a memory entry"""
        try:
            memory_uuid = UUID(memory_id)
            return self.context_relationship_repository.get_relationships(memory_uuid)
        except ValueError:
            logger.error(f"Invalid memory ID format: {memory_id}")
            return []

    def clear_enhanced_memory_entries(self, conversation_id: str) -> int:
        """Clear all enhanced memory entries for a conversation"""
        return self.enhanced_memory_repository.delete_by_conversation(conversation_id)

    def build_memory_context(
        self,
        conversation_id: str,
        context_types: List[str] = None,
        max_entries: int = 20,
        min_importance: float = 0.0
    ) -> str:
        """Build a comprehensive memory context for AI processing"""
        context_parts = []

        # Get relevant memory entries
        if context_types:
            for context_type in context_types:
                entries = self.retrieve_enhanced_memory_entries(
                    conversation_id,
                    context_type=context_type,
                    limit=max_entries
                )
                if entries:
                    context_parts.append(f"\n## {context_type.upper()} CONTEXT:")
                    for entry in entries:
                        if entry['importance_score'] >= min_importance:
                            context_parts.append(f"[{entry['role'].upper()}] {entry['content']}")
        else:
            # Get all conversation memory
            entries = self.retrieve_enhanced_memory_entries(conversation_id, limit=max_entries)
            if entries:
                context_parts.append("\n## CONVERSATION CONTEXT:")
                for entry in entries:
                    if entry['importance_score'] >= min_importance:
                        context_parts.append(f"[{entry['role'].upper()}] {entry['content']}")

        # Get related memories from relationships
        entries = self.retrieve_enhanced_memory_entries(conversation_id, limit=max_entries)
        related_memory_ids = []
        for entry in entries:
            related_memory_ids.extend(entry.get('relationships', []))

        if related_memory_ids:
            context_parts.append("\n## RELATED CONTEXT:")
            for memory_id in related_memory_ids[:5]:  # Limit to top 5 related memories
                try:
                    related_memories = self.get_related_memories(memory_id, limit=3)
                    for memory in related_memories:
                        context_parts.append(f"[RELATED] {memory['content']}")
                except Exception as e:
                    logger.warning(f"Could not retrieve related memory {memory_id}: {e}")

        return "\n".join(context_parts) if context_parts else "No relevant context found."