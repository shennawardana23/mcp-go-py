"""
Data validation utilities for the MCP Prompt Engineering System
"""

from typing import Dict, Any, List


class DataValidator:
    """Data validation utilities"""

    @staticmethod
    def validate_prompt_template_data(data: Dict[str, Any]) -> List[str]:
        """Validate prompt template data"""
        errors = []

        required_fields = ["name", "description", "category", "template_content", "variables"]
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")

        if "name" in data and not isinstance(data["name"], str):
            errors.append("Name must be a string")

        if "variables" in data and not isinstance(data["variables"], list):
            errors.append("Variables must be a list")

        if "category" in data:
            valid_categories = ["development", "architecture", "data", "quality", "communication", "techniques"]
            if data["category"] not in valid_categories:
                errors.append(f"Invalid category. Must be one of: {valid_categories}")

        return errors

    @staticmethod
    def validate_ai_configuration(config: Dict[str, Any]) -> List[str]:
        """Validate AI configuration"""
        errors = []

        required_fields = ["model_name", "provider"]
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")

        if "max_tokens" in config and config["max_tokens"] < 1:
            errors.append("max_tokens must be greater than 0")

        if "temperature" in config and not (0 <= config["temperature"] <= 2):
            errors.append("temperature must be between 0 and 2")

        return errors