#!/usr/bin/env python3
"""
MCP Prompt Engineering Server
FastAPI-based MCP server for standardized prompt engineering templates and AI agent integration
"""

import os
import json
import asyncio
import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session

# Import our data management system
from ..data.project_manager import get_data_manager
from ..data.validation import DataValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global data manager
data_manager = get_data_manager()

# Pydantic models for API
class PromptTemplateRequest(BaseModel):
    """Request model for creating prompt templates"""
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

class PromptRenderRequest(BaseModel):
    """Request model for rendering prompt templates"""
    template_name: str = Field(..., description="Name of the template to render")
    variables: Dict[str, Any] = Field(..., description="Variables to substitute in the template")

# FastAPI app setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("Starting MCP Prompt Engineering Server")
    logger.info("Available categories: " + ", ".join(data_manager.get_available_categories()))

    yield

    # Shutdown
    logger.info("Shutting down MCP Prompt Engineering Server")

app = FastAPI(
    title="MCP Prompt Engineering Server",
    description="MCP server for standardized prompt engineering templates and AI agent integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "mcp-prompt-engineering-server",
        "version": "1.0.0"
    }

# MCP Protocol Endpoints

@app.post("/mcp/prompts/list")
async def list_prompts(request: Dict[str, Any] = None):
    """List available prompt templates (MCP protocol)"""
    try:
        templates = data_manager.list_templates()

        prompts = []
        for template in templates:
            prompts.append({
                "name": template.name,
                "description": template.description,
                "arguments": [
                    {
                        "name": var,
                        "description": f"Variable: {var}",
                        "required": True
                    }
                    for var in template.variables or []
                ]
            })

        return {
            "jsonrpc": "2.0",
            "id": request.get("id") if request else None,
            "result": {
                "prompts": prompts
            }
        }

    except Exception as e:
        logger.error(f"Error listing prompts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mcp/prompts/get")
async def get_prompt(request: Dict[str, Any]):
    """Get a specific prompt template (MCP protocol)"""
    try:
        params = request.get("params", {})
        template_name = params.get("name")

        if not template_name:
            raise HTTPException(status_code=400, detail="Template name is required")

        template = data_manager.get_template_by_name(template_name)

        if not template:
            raise HTTPException(status_code=404, detail=f"Template not found: {template_name}")

        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "prompt": {
                    "name": template.name,
                    "description": template.description,
                    "content": template.template_content,
                    "arguments": [
                        {
                            "name": var,
                            "description": f"Variable: {var}",
                            "required": True
                        }
                        for var in template.variables or []
                    ]
                }
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mcp/tools/list")
async def list_tools(request: Dict[str, Any] = None):
    """List available tools (MCP protocol)"""
    try:
        tools = [
            {
                "name": "render_prompt",
                "description": "Render a prompt template with variables",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "template_name": {"type": "string"},
                        "variables": {"type": "object"}
                    },
                    "required": ["template_name", "variables"]
                }
            },
            {
                "name": "create_prompt_template",
                "description": "Create a new prompt template",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "category": {"type": "string"},
                        "template_content": {"type": "string"},
                        "variables": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["name", "description", "category", "template_content", "variables"]
                }
            },
            {
                "name": "memory_be",
                "description": "Backend memory management for conversation history",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "operation": {"type": "string", "enum": ["store", "retrieve", "clear"]},
                        "conversation_id": {"type": "string"},
                        "session_id": {"type": "string"},
                        "data": {"type": "object"}
                    },
                    "required": ["operation", "conversation_id"]
                }
            },
            {
                "name": "memory_fe",
                "description": "Frontend memory interface for UI interactions",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["get_history", "save_context"]},
                        "session_id": {"type": "string"}
                    },
                    "required": ["action", "session_id"]
                }
            },
            {
                "name": "prompt_chain_be",
                "description": "Backend prompt chaining for complex workflows",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "chain_id": {"type": "string"},
                        "steps": {"type": "array"},
                        "inputs": {"type": "object"}
                    },
                    "required": ["chain_id", "steps"]
                }
            },
            {
                "name": "prompt_chain_fe",
                "description": "Frontend prompt chain visualization",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "chain_id": {"type": "string"},
                        "visualize": {"type": "boolean"}
                    },
                    "required": ["chain_id"]
                }
            },
            {
                "name": "render_technique",
                "description": "Render a specific prompt engineering technique template",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "technique": {"type": "string"},
                        "variables": {"type": "object"}
                    },
                    "required": ["technique", "variables"]
                }
            }
        ]

        return {
            "jsonrpc": "2.0",
            "id": request.get("id") if request else None,
            "result": {
                "tools": tools
            }
        }

    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mcp/tools/call")
async def call_tool(request: Dict[str, Any]):
    """Call a tool (MCP protocol)"""
    try:
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "render_prompt":
            template_name = arguments.get("template_name")
            variables = arguments.get("variables", {})

            if not template_name:
                raise HTTPException(status_code=400, detail="template_name is required")

            try:
                rendered_content = data_manager.render_prompt_template(template_name, variables)
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": rendered_content,
                        "template_name": template_name,
                        "variables_used": variables
                    }
                }
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))

        elif tool_name == "create_prompt_template":
            required_fields = ["name", "description", "category", "template_content", "variables"]

            if not all(field in arguments for field in required_fields):
                raise HTTPException(status_code=400, detail=f"Missing required fields: {required_fields}")

            # Validate the data
            errors = DataValidator.validate_prompt_template_data(arguments)
            if errors:
                raise HTTPException(status_code=400, detail=f"Validation errors: {errors}")

            template_id = data_manager.create_prompt_template(
                name=arguments["name"],
                description=arguments["description"],
                category=arguments["category"],
                template_content=arguments["template_content"],
                variables=arguments["variables"],
                created_by=arguments.get("created_by", "system")
            )

            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "template_id": template_id,
                    "message": f"Template '{arguments['name']}' created successfully"
                }
            }

        elif tool_name == "memory_be":
            operation = arguments.get("operation")
            conversation_id = arguments.get("conversation_id")
            session_id = arguments.get("session_id", "default")
            data = arguments.get("data", {})

            if operation == "store":
                memory_id = data_manager.store_memory_entry(
                    conversation_id=conversation_id,
                    session_id=session_id,
                    role=data.get("role", "user"),
                    content=data.get("content", ""),
                    metadata=data.get("metadata", {})
                )
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "memory_id": memory_id,
                        "message": "Memory entry stored successfully"
                    }
                }

            elif operation == "retrieve":
                entries = data_manager.retrieve_memory_entries(conversation_id)
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "entries": entries,
                        "count": len(entries)
                    }
                }

            elif operation == "clear":
                data_manager.clear_memory_entries(conversation_id)
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "message": "Memory entries cleared successfully"
                    }
                }

            else:
                raise HTTPException(status_code=400, detail=f"Unknown memory operation: {operation}")

        elif tool_name == "memory_fe":
            action = arguments.get("action")
            session_id = arguments.get("session_id")

            if action == "get_history":
                # For simplicity, use a default conversation ID
                entries = data_manager.retrieve_memory_entries(f"session_{session_id}")
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "history": entries,
                        "session_id": session_id
                    }
                }

            elif action == "save_context":
                # This would typically save context, but simplified here
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "message": "Context saved successfully",
                        "session_id": session_id
                    }
                }

            else:
                raise HTTPException(status_code=400, detail=f"Unknown memory action: {action}")

        elif tool_name == "prompt_chain_be":
            chain_id = arguments.get("chain_id")
            steps = arguments.get("steps", [])
            inputs = arguments.get("inputs", {})

            if not chain_id:
                raise HTTPException(status_code=400, detail="chain_id is required")

            execution_id = data_manager.execute_prompt_chain(chain_id, str(uuid.uuid4()))

            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "execution_id": execution_id,
                    "message": "Prompt chain execution started",
                    "steps_count": len(steps)
                }
            }

        elif tool_name == "prompt_chain_fe":
            chain_id = arguments.get("chain_id")
            visualize = arguments.get("visualize", False)

            # Get chain status
            status = data_manager.get_prompt_chain_status(chain_id)

            if visualize:
                # Return visualization-friendly data
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "chain_id": chain_id,
                        "status": status,
                        "visualization": {
                            "total_steps": status["total_steps"],
                            "completed_steps": status["completed_steps"],
                            "failed_steps": status["failed_steps"],
                            "steps": status["steps"]
                        }
                    }
                }

            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "chain_id": chain_id,
                    "status": status
                }
            }

        elif tool_name == "render_technique":
            technique = arguments.get("technique")
            variables = arguments.get("variables", {})

            if not technique:
                raise HTTPException(status_code=400, detail="technique is required")

            try:
                rendered_content = data_manager.render_technique_template(technique, variables)
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "technique": technique,
                        "content": rendered_content,
                        "variables_used": variables
                    }
                }
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))

        else:
            raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calling tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Additional REST API endpoints for management

@app.get("/api/prompts")
async def get_prompts(category: Optional[str] = None):
    """Get all prompt templates"""
    try:
        templates = data_manager.get_templates_by_category(category) if category else data_manager.list_templates()
        return {
            "templates": [
                {
                    "id": template.id,
                    "name": template.name,
                    "description": template.description,
                    "category": template.category,
                    "variables": template.variables,
                    "created_at": template.created_at.isoformat() if template.created_at else None,
                    "updated_at": template.updated_at.isoformat() if template.updated_at else None
                }
                for template in templates
            ]
        }
    except Exception as e:
        logger.error(f"Error getting prompts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/prompts")
async def create_prompt_template(request: PromptTemplateRequest):
    """Create a new prompt template"""
    try:
        # Validate the request
        errors = DataValidator.validate_prompt_template_data(request.dict())
        if errors:
            raise HTTPException(status_code=400, detail=f"Validation errors: {errors}")

        template_id = data_manager.create_prompt_template(
            name=request.name,
            description=request.description,
            category=request.category,
            template_content=request.template_content,
            variables=request.variables,
            created_by=request.created_by
        )

        return {
            "id": template_id,
            "message": f"Template '{request.name}' created successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating prompt template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/prompts/{template_name}/render")
async def render_prompt_template(template_name: str, variables: str):
    """Render a prompt template with variables"""
    try:
        # Parse variables from query string
        import urllib.parse
        variables_dict = dict(urllib.parse.parse_qsl(variables))

        rendered_content = data_manager.render_prompt_template(template_name, variables_dict)

        return {
            "template_name": template_name,
            "variables": variables_dict,
            "rendered_content": rendered_content
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error rendering prompt template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/categories")
async def get_categories():
    """Get all available prompt categories"""
    try:
        categories = data_manager.get_available_categories()
        return {"categories": categories}
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_usage_statistics():
    """Get usage statistics"""
    try:
        stats = data_manager.get_usage_statistics()
        return {"statistics": stats}
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception handler: {exc}", exc_info=True)
    return {
        "error": "Internal server error",
        "detail": str(exc)
    }


def create_app() -> FastAPI:
    """Factory function to create and configure the FastAPI application"""
    return app


# Main entry point
if __name__ == "__main__":
    import uvicorn

    logger.info("Starting MCP Prompt Engineering Server")
    logger.info("Available endpoints:")
    logger.info("  - MCP Protocol: /mcp/*")
    logger.info("  - REST API: /api/*")
    logger.info("  - Health Check: /health")

    uvicorn.run(
        "mcp_pba_tunnel.server.fastapi_mcp_server:app",
        host="0.0.0.0",
        port=9001,
        reload=True,
        log_level="info"
    )
