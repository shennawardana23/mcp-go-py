"""
Business logic service for AI configuration operations
"""

import logging
from typing import Dict, List, Any, Optional
from uuid import UUID

from ..models import AIConfiguration, AIConfigurationCreate, AIConfigurationUpdate
from ..repositories import AIConfigurationRepository
from ..validation import DataValidator

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI configuration business logic"""

    def __init__(self):
        self.repository = AIConfigurationRepository()

    def create_configuration(self, config_data: Dict[str, Any]) -> AIConfiguration:
        """Create a new AI configuration with validation"""
        # Validate input data
        errors = DataValidator.validate_ai_configuration(config_data)
        if errors:
            raise ValueError(f"Validation errors: {', '.join(errors)}")

        # Create configuration object
        config = AIConfiguration(**config_data)

        # Save to database
        self.repository.create(config)

        logger.info(f"Created AI configuration: {config.model_name} ({config.provider})")
        return config

    def get_configuration(self, config_id: UUID) -> Optional[AIConfiguration]:
        """Get an AI configuration by ID"""
        data = self.repository.get_by_id(config_id)
        if data:
            return AIConfiguration(**data)
        return None

    def get_configuration_by_model(self, model_name: str) -> Optional[AIConfiguration]:
        """Get an AI configuration by model name"""
        data = self.repository.get_by_model_name(model_name)
        if data:
            return AIConfiguration(**data)
        return None

    def list_configurations(self) -> List[AIConfiguration]:
        """List all active AI configurations"""
        configs_data = self.repository.list_all()
        return [AIConfiguration(**data) for data in configs_data]

    def update_configuration(self, config_id: UUID, updates: Dict[str, Any]) -> bool:
        """Update an AI configuration"""
        # Validate updates if they contain configuration data
        if any(key in updates for key in ['model_name', 'provider', 'max_tokens', 'temperature']):
            errors = DataValidator.validate_ai_configuration(updates)
            if errors:
                raise ValueError(f"Validation errors: {', '.join(errors)}")

        success = self.repository.update(config_id, updates)

        if success:
            logger.info(f"Updated AI configuration: {config_id}")

        return success

    def delete_configuration(self, config_id: UUID) -> bool:
        """Soft delete an AI configuration"""
        return self.repository.delete(config_id)

    def get_active_configurations(self) -> List[AIConfiguration]:
        """Get all active AI configurations"""
        return self.list_configurations()

    def get_configurations_by_provider(self, provider: str) -> List[AIConfiguration]:
        """Get AI configurations by provider"""
        all_configs = self.list_configurations()
        return [config for config in all_configs if config.provider == provider]