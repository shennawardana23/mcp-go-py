"""
Repository for prompt template operations
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
import json

from .base import BaseRepository
from ..models import (
    PromptTemplate, PromptUsage, GeneratedContent, MemoryEntry,
    ContextRelationship, ContextRelationshipCreate,
    EnhancedMemoryEntry, EnhancedMemoryEntryCreate
)


class PromptTemplateRepository(BaseRepository[PromptTemplate]):
    """Repository for prompt template database operations"""

    def __init__(self):
        super().__init__("prompt_templates")

    def create(self, template: PromptTemplate) -> str:
        """Create a new prompt template"""
        query = """
        INSERT INTO prompt_templates (
            id, name, description, category, template_content, variables, created_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        params = (
            str(template.id),
            template.name,
            template.description,
            template.category,
            template.template_content,
            self._serialize_json(template.variables),
            template.created_by
        )

        return self.execute_insert(query, params)

    def get_by_id(self, template_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a prompt template by ID"""
        query = """
        SELECT id, name, description, category, template_content, variables,
               version, is_active, created_at, updated_at, created_by
        FROM prompt_templates
        WHERE id = %s AND is_active = true
        """

        result = self.execute_query(query, (str(template_id),), fetch="one")
        if result:
            return {
                "id": UUID(result[0]),
                "name": result[1],
                "description": result[2],
                "category": result[3],
                "template_content": result[4],
                "variables": self._deserialize_json(result[5]) or [],
                "version": result[6],
                "is_active": result[7],
                "created_at": result[8],
                "updated_at": result[9],
                "created_by": result[10]
            }
        return None

    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a prompt template by name"""
        query = """
        SELECT id, name, description, category, template_content, variables,
               version, is_active, created_at, updated_at, created_by
        FROM prompt_templates
        WHERE name = %s AND is_active = true
        """

        result = self.execute_query(query, (name,), fetch="one")
        if result:
            return {
                "id": UUID(result[0]),
                "name": result[1],
                "description": result[2],
                "category": result[3],
                "template_content": result[4],
                "variables": self._deserialize_json(result[5]) or [],
                "version": result[6],
                "is_active": result[7],
                "created_at": result[8],
                "updated_at": result[9],
                "created_by": result[10]
            }
        return None

    def list_all(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all active prompt templates"""
        if category:
            query = """
            SELECT id, name, description, category, template_content, variables
            FROM prompt_templates
            WHERE is_active = true AND category = %s
            ORDER BY name
            """
            params = (category,)
        else:
            query = """
            SELECT id, name, description, category, template_content, variables
            FROM prompt_templates
            WHERE is_active = true
            ORDER BY category, name
            """
            params = None

        results = self.execute_query(query, params, fetch="all")
        return [
            {
                "id": UUID(row[0]),
                "name": row[1],
                "description": row[2],
                "category": row[3],
                "template_content": row[4],
                "variables": self._deserialize_json(row[5]) or []
            }
            for row in results
        ]

    def update(self, template_id: UUID, updates: Dict[str, Any]) -> bool:
        """Update a prompt template"""
        # Build dynamic update query
        update_fields = []
        params = []

        for key, value in updates.items():
            if key == "variables" and value is not None:
                update_fields.append(f"{key} = %s")
                params.append(self._serialize_json(value))
            elif value is not None:
                update_fields.append(f"{key} = %s")
                params.append(value)

        if not update_fields:
            return False

        query = f"""
        UPDATE prompt_templates
        SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """

        params.append(str(template_id))
        affected_rows = self.execute_update(query, tuple(params))

        return affected_rows > 0

    def delete(self, template_id: UUID) -> bool:
        """Soft delete a prompt template"""
        return self.update(template_id, {"is_active": False})

    def get_categories(self) -> List[str]:
        """Get all available prompt categories"""
        query = """
        SELECT DISTINCT category
        FROM prompt_templates
        WHERE is_active = true AND category IS NOT NULL
        ORDER BY category
        """

        results = self.execute_query(query, fetch="all")
        return [row[0] for row in results if row[0]]


class PromptUsageRepository(BaseRepository[PromptUsage]):
    """Repository for prompt usage tracking"""

    def __init__(self):
        super().__init__("prompt_usage")

    def record_usage(self, prompt_id: UUID, ai_model: str, response_time: int, success: bool = True):
        """Record prompt usage statistics"""
        # Check if usage record exists
        query = """
        SELECT id, usage_count, success_count, avg_response_time
        FROM prompt_usage
        WHERE prompt_id = %s AND ai_model = %s
        """

        result = self.execute_query(query, (str(prompt_id), ai_model), fetch="one")

        if result:
            # Update existing record
            usage_id, usage_count, success_count, avg_response_time = result
            new_usage_count = usage_count + 1
            new_success_count = success_count + (1 if success else 0)
            new_avg_response_time = ((avg_response_time * usage_count) + response_time) // new_usage_count

            update_query = """
            UPDATE prompt_usage
            SET usage_count = %s, success_count = %s, avg_response_time = %s, last_used_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """

            self.execute_update(update_query, (new_usage_count, new_success_count, new_avg_response_time, usage_id))
        else:
            # Create new usage record
            usage_id = str(UUID(uuid4().hex))
            insert_query = """
            INSERT INTO prompt_usage (id, prompt_id, ai_model, usage_count, success_count, avg_response_time)
            VALUES (%s, %s, %s, %s, %s, %s)
            """

            self.execute_insert(insert_query, (usage_id, str(prompt_id), ai_model, 1, 1 if success else 0, response_time))

    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get comprehensive usage statistics"""
        # Get all active templates
        templates_query = """
        SELECT id, name
        FROM prompt_templates
        WHERE is_active = true
        """

        templates = self.execute_query(templates_query, fetch="all")

        stats = {}
        for template_id, template_name in templates:
            # Get usage statistics for this template
            usage_query = """
            SELECT ai_model, SUM(usage_count), SUM(success_count)
            FROM prompt_usage
            WHERE prompt_id = %s
            GROUP BY ai_model
            """

            usage_results = self.execute_query(usage_query, (template_id,), fetch="all")

            total_usage = 0
            total_success = 0
            ai_models = []

            for ai_model, usage_count, success_count in usage_results:
                total_usage += usage_count
                total_success += success_count
                ai_models.append(ai_model)

            success_rate = (total_success / total_usage * 100) if total_usage > 0 else 0

            stats[template_name] = {
                "total_usage": total_usage,
                "success_rate": success_rate,
                "ai_models": ai_models
            }

        return stats


class GeneratedContentRepository(BaseRepository[GeneratedContent]):
    """Repository for generated content storage"""

    def __init__(self):
        super().__init__("generated_content")

    def create(self, content: GeneratedContent) -> str:
        """Store generated content"""
        query = """
        INSERT INTO generated_content (
            id, prompt_id, ai_model, input_variables, generated_content, tokens_used, response_time
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        params = (
            str(content.id),
            str(content.prompt_id),
            content.ai_model,
            self._serialize_json(content.input_variables),
            content.generated_content,
            content.tokens_used,
            content.response_time
        )

        return self.execute_insert(query, params)

    def get_by_prompt_id(self, prompt_id: UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """Get generated content for a prompt"""
        query = """
        SELECT id, ai_model, input_variables, generated_content, tokens_used, response_time, created_at
        FROM generated_content
        WHERE prompt_id = %s
        ORDER BY created_at DESC
        LIMIT %s
        """

        results = self.execute_query(query, (str(prompt_id), limit), fetch="all")
        return [
            {
                "id": UUID(row[0]),
                "ai_model": row[1],
                "input_variables": self._deserialize_json(row[2]) or {},
                "generated_content": row[3],
                "tokens_used": row[4],
                "response_time": row[5],
                "created_at": row[6].isoformat() if row[6] else None
            }
            for row in results
        ]


class MemoryRepository(BaseRepository[MemoryEntry]):
    """Repository for memory/conversation storage"""

    def __init__(self):
        super().__init__("memory_entries")

    def create(self, entry: MemoryEntry) -> str:
        """Store a memory entry"""
        query = """
        INSERT INTO memory_entries (
            id, conversation_id, session_id, role, content, entry_metadata, ttl_seconds
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        params = (
            str(entry.id),
            entry.conversation_id,
            entry.session_id,
            entry.role,
            entry.content,
            self._serialize_json(entry.entry_metadata),
            entry.ttl_seconds
        )

        return self.execute_insert(query, params)

    def get_by_conversation(self, conversation_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve memory entries for a conversation"""
        query = """
        SELECT id, role, content, entry_metadata, timestamp
        FROM memory_entries
        WHERE conversation_id = %s
        ORDER BY timestamp DESC
        LIMIT %s
        """

        results = self.execute_query(query, (conversation_id, limit), fetch="all")
        return [
            {
                "id": UUID(row[0]),
                "role": row[1],
                "content": row[2],
                "metadata": self._deserialize_json(row[3]) or {},
                "timestamp": row[4].isoformat() if row[4] else None
            }
            for row in results
        ]

    def delete_by_conversation(self, conversation_id: str) -> int:
        """Clear all memory entries for a conversation"""
        query = "DELETE FROM memory_entries WHERE conversation_id = %s"
        return self.execute_delete(query, (conversation_id,))


class EnhancedMemoryRepository(BaseRepository[EnhancedMemoryEntry]):
    """Enhanced repository for sophisticated memory management"""

    def __init__(self):
        super().__init__("enhanced_memory_entries")

    def create(self, entry: EnhancedMemoryEntry) -> str:
        """Store an enhanced memory entry"""
        query = """
        INSERT INTO enhanced_memory_entries (
            id, conversation_id, session_id, role, content, context_type,
            importance_score, tags, relationships, metadata, ttl_seconds
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        params = (
            str(entry.id),
            entry.conversation_id,
            entry.session_id,
            entry.role,
            entry.content,
            entry.context_type,
            entry.importance_score,
            self._serialize_json(entry.tags),
            self._serialize_json(entry.relationships),
            self._serialize_json(entry.metadata),
            entry.ttl_seconds
        )

        return self.execute_insert(query, params)

    def get_by_conversation(self, conversation_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve enhanced memory entries for a conversation"""
        query = """
        SELECT id, role, content, context_type, importance_score, tags,
               relationships, metadata, timestamp
        FROM enhanced_memory_entries
        WHERE conversation_id = %s
        ORDER BY importance_score DESC, timestamp DESC
        LIMIT %s
        """

        results = self.execute_query(query, (conversation_id, limit), fetch="all")
        return [
            {
                "id": UUID(row[0]),
                "role": row[1],
                "content": row[2],
                "context_type": row[3],
                "importance_score": row[4],
                "tags": self._deserialize_json(row[5]) or [],
                "relationships": self._deserialize_json(row[6]) or [],
                "metadata": self._deserialize_json(row[7]) or {},
                "timestamp": row[8].isoformat() if row[8] else None
            }
            for row in results
        ]

    def get_by_context_type(self, context_type: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get memory entries by context type"""
        query = """
        SELECT id, conversation_id, role, content, importance_score, tags, timestamp
        FROM enhanced_memory_entries
        WHERE context_type = %s
        ORDER BY importance_score DESC, timestamp DESC
        LIMIT %s
        """

        results = self.execute_query(query, (context_type, limit), fetch="all")
        return [
            {
                "id": UUID(row[0]),
                "conversation_id": row[1],
                "role": row[2],
                "content": row[3],
                "importance_score": row[4],
                "tags": self._deserialize_json(row[5]) or [],
                "timestamp": row[6].isoformat() if row[6] else None
            }
            for row in results
        ]

    def get_related_memories(self, memory_id: UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """Get memories related to a specific memory entry"""
        query = """
        SELECT em.id, em.role, em.content, em.context_type, em.importance_score, em.timestamp
        FROM enhanced_memory_entries em
        JOIN context_relationships cr ON em.id = cr.target_memory_id
        WHERE cr.source_memory_id = %s
        ORDER BY cr.strength DESC, em.importance_score DESC
        LIMIT %s
        """

        results = self.execute_query(query, (str(memory_id), limit), fetch="all")
        return [
            {
                "id": UUID(row[0]),
                "role": row[1],
                "content": row[2],
                "context_type": row[3],
                "importance_score": row[4],
                "timestamp": row[5].isoformat() if row[5] else None
            }
            for row in results
        ]

    def search_by_tags(self, tags: List[str], limit: int = 50) -> List[Dict[str, Any]]:
        """Search memory entries by tags"""
        placeholders = ', '.join(['%s'] * len(tags))
        query = f"""
        SELECT id, conversation_id, role, content, context_type, importance_score, timestamp
        FROM enhanced_memory_entries
        WHERE tags::text[] && ARRAY[{placeholders}]
        ORDER BY importance_score DESC, timestamp DESC
        LIMIT %s
        """

        params = tags + [limit]
        results = self.execute_query(query, params, fetch="all")
        return [
            {
                "id": UUID(row[0]),
                "conversation_id": row[1],
                "role": row[2],
                "content": row[3],
                "context_type": row[4],
                "importance_score": row[5],
                "timestamp": row[6].isoformat() if row[6] else None
            }
            for row in results
        ]

    def delete_by_conversation(self, conversation_id: str) -> int:
        """Clear all enhanced memory entries for a conversation"""
        query = "DELETE FROM enhanced_memory_entries WHERE conversation_id = %s"
        return self.execute_delete(query, (conversation_id,))


class ContextRelationshipRepository(BaseRepository[ContextRelationship]):
    """Repository for context relationship management"""

    def __init__(self):
        super().__init__("context_relationships")

    def create(self, relationship: ContextRelationship) -> str:
        """Create a context relationship"""
        query = """
        INSERT INTO context_relationships (
            id, source_memory_id, target_memory_id, relationship_type, strength, metadata
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """

        params = (
            str(relationship.id),
            str(relationship.source_memory_id),
            str(relationship.target_memory_id),
            relationship.relationship_type,
            relationship.strength,
            self._serialize_json(relationship.metadata)
        )

        return self.execute_insert(query, params)

    def get_relationships(self, memory_id: UUID) -> List[Dict[str, Any]]:
        """Get all relationships for a memory entry"""
        query = """
        SELECT id, source_memory_id, target_memory_id, relationship_type, strength, metadata, created_at
        FROM context_relationships
        WHERE source_memory_id = %s OR target_memory_id = %s
        ORDER BY strength DESC
        """

        results = self.execute_query(query, (str(memory_id), str(memory_id)), fetch="all")
        return [
            {
                "id": UUID(row[0]),
                "source_memory_id": UUID(row[1]),
                "target_memory_id": UUID(row[2]),
                "relationship_type": row[3],
                "strength": row[4],
                "metadata": self._deserialize_json(row[5]) or {},
                "created_at": row[6].isoformat() if row[6] else None
            }
            for row in results
        ]

    def get_relationships_by_type(self, relationship_type: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get relationships by type"""
        query = """
        SELECT id, source_memory_id, target_memory_id, strength, metadata, created_at
        FROM context_relationships
        WHERE relationship_type = %s
        ORDER BY strength DESC
        LIMIT %s
        """

        results = self.execute_query(query, (relationship_type, limit), fetch="all")
        return [
            {
                "id": UUID(row[0]),
                "source_memory_id": UUID(row[1]),
                "target_memory_id": UUID(row[2]),
                "strength": row[3],
                "metadata": self._deserialize_json(row[4]) or {},
                "created_at": row[5].isoformat() if row[5] else None
            }
            for row in results
        ]