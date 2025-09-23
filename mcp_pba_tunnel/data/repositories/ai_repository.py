"""
Repository for AI configuration operations
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from .base import BaseRepository
from ..models import AIConfiguration


class AIConfigurationRepository(BaseRepository[AIConfiguration]):
    """Repository for AI configuration database operations"""

    def __init__(self):
        super().__init__("ai_configurations")

    def create(self, config: AIConfiguration) -> str:
        """Create a new AI configuration"""
        query = """
        INSERT INTO ai_configurations (
            id, model_name, provider, api_base_url, max_tokens, temperature
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """

        params = (
            str(config.id),
            config.model_name,
            config.provider,
            config.api_base_url,
            config.max_tokens,
            config.temperature
        )

        return self.execute_insert(query, params)

    def get_by_id(self, config_id: UUID) -> Optional[Dict[str, Any]]:
        """Get an AI configuration by ID"""
        query = """
        SELECT id, model_name, provider, api_base_url, max_tokens, temperature, is_active, created_at, updated_at
        FROM ai_configurations
        WHERE id = %s AND is_active = true
        """

        result = self.execute_query(query, (str(config_id),), fetch="one")
        if result:
            return {
                "id": UUID(result[0]),
                "model_name": result[1],
                "provider": result[2],
                "api_base_url": result[3],
                "max_tokens": result[4],
                "temperature": result[5],
                "is_active": result[6],
                "created_at": result[7],
                "updated_at": result[8]
            }
        return None

    def get_by_model_name(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get an AI configuration by model name"""
        query = """
        SELECT id, model_name, provider, api_base_url, max_tokens, temperature, is_active, created_at, updated_at
        FROM ai_configurations
        WHERE model_name = %s AND is_active = true
        """

        result = self.execute_query(query, (model_name,), fetch="one")
        if result:
            return {
                "id": UUID(result[0]),
                "model_name": result[1],
                "provider": result[2],
                "api_base_url": result[3],
                "max_tokens": result[4],
                "temperature": result[5],
                "is_active": result[6],
                "created_at": result[7],
                "updated_at": result[8]
            }
        return None

    def list_all(self) -> List[Dict[str, Any]]:
        """List all active AI configurations"""
        query = """
        SELECT id, model_name, provider, api_base_url, max_tokens, temperature, is_active
        FROM ai_configurations
        WHERE is_active = true
        ORDER BY provider, model_name
        """

        results = self.execute_query(query, fetch="all")
        return [
            {
                "id": UUID(row[0]),
                "model_name": row[1],
                "provider": row[2],
                "api_base_url": row[3],
                "max_tokens": row[4],
                "temperature": row[5],
                "is_active": row[6]
            }
            for row in results
        ]

    def update(self, config_id: UUID, updates: Dict[str, Any]) -> bool:
        """Update an AI configuration"""
        # Build dynamic update query
        update_fields = []
        params = []

        for key, value in updates.items():
            if value is not None:
                update_fields.append(f"{key} = %s")
                params.append(value)

        if not update_fields:
            return False

        query = f"""
        UPDATE ai_configurations
        SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """

        params.append(str(config_id))
        affected_rows = self.execute_update(query, tuple(params))

        return affected_rows > 0

    def delete(self, config_id: UUID) -> bool:
        """Soft delete an AI configuration"""
        return self.update(config_id, {"is_active": False})