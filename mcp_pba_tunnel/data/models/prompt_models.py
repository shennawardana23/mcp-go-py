"""
Prompt-related data models and DTOs
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4
from enum import Enum


class PromptTemplateBase(BaseModel):
    """Base prompt template model"""
    name: str = Field(..., description="Unique name for the prompt template")
    description: str = Field(..., description="Description of what this template does")
    category: str = Field(..., description="Category: development, architecture, data, quality, communication")
    template_content: str = Field(..., description="The actual prompt template with variables")
    variables: List[str] = Field(..., description="List of variable names used in the template")
    created_by: str = Field(default="system", description="Who created this template")

    @validator('category')
    def validate_category(cls, v):
        valid_categories = ["development", "architecture", "data", "quality", "communication", "techniques"]
        if v not in valid_categories:
            raise ValueError(f"Category must be one of: {valid_categories}")
        return v


class PromptTemplateCreate(PromptTemplateBase):
    """Model for creating a new prompt template"""
    pass


class PromptTemplateUpdate(BaseModel):
    """Model for updating a prompt template"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    template_content: Optional[str] = None
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None

    @validator('category')
    def validate_category(cls, v):
        if v is not None:
            valid_categories = ["development", "architecture", "data", "quality", "communication", "techniques"]
            if v not in valid_categories:
                raise ValueError(f"Category must be one of: {valid_categories}")
        return v


class PromptTemplate(PromptTemplateBase):
    """Complete prompt template model"""
    id: UUID = Field(default_factory=uuid4, description="Unique identifier")
    version: str = Field(default="1.0.0", description="Template version")
    is_active: bool = Field(default=True, description="Whether the template is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class PromptUsageBase(BaseModel):
    """Base prompt usage model"""
    prompt_id: UUID = Field(..., description="ID of the prompt template")
    ai_model: str = Field(..., description="AI model used")
    usage_count: int = Field(default=0, description="Number of times used")
    success_count: int = Field(default=0, description="Number of successful uses")
    avg_response_time: int = Field(default=0, description="Average response time in ms")
    last_used_at: Optional[datetime] = None


class PromptUsageCreate(PromptUsageBase):
    """Model for creating prompt usage record"""
    pass


class PromptUsage(PromptUsageBase):
    """Complete prompt usage model"""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class GeneratedContentBase(BaseModel):
    """Base generated content model"""
    prompt_id: UUID = Field(..., description="ID of the prompt template")
    ai_model: str = Field(..., description="AI model used")
    input_variables: Dict[str, Any] = Field(..., description="Variables used in the prompt")
    generated_content: str = Field(..., description="The generated content")
    tokens_used: int = Field(..., description="Number of tokens used")
    response_time: int = Field(..., description="Response time in milliseconds")


class GeneratedContentCreate(GeneratedContentBase):
    """Model for creating generated content record"""
    pass


class GeneratedContent(GeneratedContentBase):
    """Complete generated content model"""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class MemoryEntryBase(BaseModel):
    """Base memory entry model"""
    conversation_id: str = Field(..., description="Conversation identifier")
    session_id: str = Field(default="default", description="Session identifier")
    role: str = Field(..., description="Role (user, assistant, system)")
    content: str = Field(..., description="Memory content")
    entry_metadata: Optional[Dict[str, Any]] = None
    ttl_seconds: int = Field(default=3600, description="Time to live in seconds")


class MemoryEntryCreate(MemoryEntryBase):
    """Model for creating memory entry"""
    pass


class MemoryEntry(MemoryEntryBase):
    """Complete memory entry model"""
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class ContextRelationshipBase(BaseModel):
    """Base context relationship model"""
    source_memory_id: UUID = Field(..., description="Source memory entry ID")
    target_memory_id: UUID = Field(..., description="Target memory entry ID")
    relationship_type: str = Field(..., description="Type of relationship (references, follows, contradicts, etc.)")
    strength: float = Field(default=1.0, ge=0.0, le=1.0, description="Relationship strength (0-1)")
    metadata: Optional[Dict[str, Any]] = None


class ContextRelationshipCreate(ContextRelationshipBase):
    """Model for creating context relationship"""
    pass


class ContextRelationship(ContextRelationshipBase):
    """Complete context relationship model"""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class ContextType(str, Enum):
    """Context type enumeration"""
    CONVERSATION = "conversation"
    CODE_ANALYSIS = "code_analysis"
    PROJECT_TASK = "project_task"
    WEB_CONTENT = "web_content"
    DATABASE_QUERY = "database_query"
    TEST_RESULT = "test_result"
    REASONING_STEP = "reasoning_step"
    KNOWLEDGE_BASE = "knowledge_base"


class EnhancedMemoryEntryBase(BaseModel):
    """Enhanced base memory entry model with sophisticated context management"""
    conversation_id: str = Field(..., description="Conversation identifier")
    session_id: str = Field(default="default", description="Session identifier")
    role: str = Field(..., description="Role (user, assistant, system)")
    content: str = Field(..., description="Memory content")
    context_type: ContextType = Field(default=ContextType.CONVERSATION, description="Type of context")
    importance_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Importance score (0-1)")
    tags: List[str] = Field(default_factory=list, description="Context tags for categorization")
    relationships: List[str] = Field(default_factory=list, description="Related memory IDs")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extended metadata")
    ttl_seconds: int = Field(default=3600, description="Time to live in seconds")


class EnhancedMemoryEntryCreate(EnhancedMemoryEntryBase):
    """Model for creating enhanced memory entry"""
    pass


class EnhancedMemoryEntry(EnhancedMemoryEntryBase):
    """Complete enhanced memory entry model"""
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    vector_embedding: Optional[List[float]] = None  # For semantic search

    class Config:
        from_attributes = True