"""
AI configuration and model-related data models
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4


class AIConfigurationBase(BaseModel):
    """Base AI configuration model"""
    model_name: str = Field(..., description="Name of the AI model")
    provider: str = Field(..., description="AI provider (openai, anthropic, etc.)")
    api_base_url: Optional[str] = Field(None, description="Base URL for API calls")
    max_tokens: int = Field(default=4000, description="Maximum tokens per request")
    temperature: float = Field(default=0.7, description="Temperature for randomness")

    @validator('max_tokens')
    def validate_max_tokens(cls, v):
        if v < 1:
            raise ValueError("max_tokens must be greater than 0")
        return v

    @validator('temperature')
    def validate_temperature(cls, v):
        if not (0 <= v <= 2):
            raise ValueError("temperature must be between 0 and 2")
        return v


class AIConfigurationCreate(AIConfigurationBase):
    """Model for creating AI configuration"""
    pass


class AIConfigurationUpdate(BaseModel):
    """Model for updating AI configuration"""
    model_name: Optional[str] = None
    provider: Optional[str] = None
    api_base_url: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    is_active: Optional[bool] = None


class AIConfiguration(AIConfigurationBase):
    """Complete AI configuration model"""
    id: UUID = Field(default_factory=uuid4)
    is_active: bool = Field(default=True, description="Whether the configuration is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True