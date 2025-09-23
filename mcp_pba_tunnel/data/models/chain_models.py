"""
Prompt chain and execution-related data models
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class PromptChainStep(BaseModel):
    """Model for a single step in a prompt chain"""
    prompt_id: Optional[UUID] = Field(None, description="ID of the prompt template")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Input variables for this step")
    outputs: Optional[Dict[str, Any]] = Field(None, description="Output variables from this step")
    description: Optional[str] = Field(None, description="Description of this step")


class PromptChainBase(BaseModel):
    """Base prompt chain model"""
    name: str = Field(..., description="Name of the prompt chain")
    description: Optional[str] = Field(None, description="Description of the chain")
    steps: List[PromptChainStep] = Field(..., description="List of steps in the chain")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Global input variables")
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Global output variables")


class PromptChainCreate(PromptChainBase):
    """Model for creating a prompt chain"""
    pass


class PromptChain(PromptChainBase):
    """Complete prompt chain model"""
    id: UUID = Field(default_factory=uuid4)
    status: str = Field(default="active", description="Status of the chain")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class PromptChainExecutionStep(BaseModel):
    """Model for a step execution in a chain"""
    step_number: int = Field(..., description="Step number in the chain")
    prompt_id: Optional[UUID] = Field(None, description="ID of the prompt template")
    input_data: Dict[str, Any] = Field(..., description="Input data for this step")
    output_data: Optional[Dict[str, Any]] = Field(None, description="Output data from this step")
    execution_time: Optional[int] = Field(None, description="Execution time in milliseconds")
    status: str = Field(default="pending", description="Status of this step")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class PromptChainExecutionBase(BaseModel):
    """Base prompt chain execution model"""
    chain_id: UUID = Field(..., description="ID of the prompt chain")
    execution_id: str = Field(..., description="Unique execution identifier")
    steps: List[PromptChainExecutionStep] = Field(default_factory=list, description="List of executed steps")


class PromptChainExecutionCreate(PromptChainExecutionBase):
    """Model for creating a chain execution"""
    pass


class PromptChainExecution(PromptChainExecutionBase):
    """Complete prompt chain execution model"""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True