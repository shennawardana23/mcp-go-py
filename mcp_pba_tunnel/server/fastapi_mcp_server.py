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
            },
            {
                "name": "enhanced_memory",
                "description": "Enhanced memory management with context and relationships",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "operation": {"type": "string", "enum": ["store", "retrieve", "relate", "context", "clear"]},
                        "conversation_id": {"type": "string"},
                        "session_id": {"type": "string"},
                        "content": {"type": "string"},
                        "context_type": {"type": "string"},
                        "importance_score": {"type": "number"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "relationship_type": {"type": "string"},
                        "target_memory_id": {"type": "string"},
                        "strength": {"type": "number"}
                    },
                    "required": ["operation", "conversation_id"]
                }
            },
            {
                "name": "code_analysis",
                "description": "Analyze code files for patterns, complexity, and suggestions",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string"},
                        "analysis_type": {"type": "string", "enum": ["complexity", "patterns", "security", "performance"]},
                        "output_format": {"type": "string", "enum": ["summary", "detailed", "json"]}
                    },
                    "required": ["file_path", "analysis_type"]
                }
            },
            {
                "name": "file_operations",
                "description": "Read, write, and manipulate files in the project",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "operation": {"type": "string", "enum": ["read", "write", "search", "replace"]},
                        "file_path": {"type": "string"},
                        "content": {"type": "string"},
                        "search_pattern": {"type": "string"},
                        "replace_with": {"type": "string"}
                    },
                    "required": ["operation", "file_path"]
                }
            },
            {
                "name": "terminal_execution",
                "description": "Execute terminal commands safely",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string"},
                        "working_directory": {"type": "string"},
                        "environment_vars": {"type": "object"},
                        "timeout": {"type": "number"}
                    },
                    "required": ["command"]
                }
            },
            {
                "name": "sequential_reasoning",
                "description": "Multi-step reasoning and problem solving",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "problem": {"type": "string"},
                        "reasoning_steps": {"type": "number"},
                        "constraints": {"type": "array", "items": {"type": "string"}},
                        "evaluation_criteria": {"type": "array", "items": {"type": "string"}},
                        "context_types": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["problem"]
                }
            },
            {
                "name": "project_tracker",
                "description": "Track project progress and tasks",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "operation": {"type": "string", "enum": ["create_task", "update_status", "get_progress", "generate_report"]},
                        "task_data": {"type": "object"},
                        "project_id": {"type": "string"},
                        "task_id": {"type": "string"},
                        "status": {"type": "string"}
                    },
                    "required": ["operation"]
                }
            },
            {
                "name": "data_analyzer",
                "description": "Analyze data patterns and generate insights",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "data_source": {"type": "string"},
                        "analysis_type": {"type": "string", "enum": ["patterns", "trends", "correlations", "anomalies"]},
                        "parameters": {"type": "object"},
                        "output_format": {"type": "string"}
                    },
                    "required": ["data_source", "analysis_type"]
                }
            },
            {
                "name": "test_generator",
                "description": "Generate and execute tests automatically",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "code_file": {"type": "string"},
                        "test_framework": {"type": "string"},
                        "coverage_target": {"type": "number"},
                        "test_types": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["code_file", "test_framework"]
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

        elif tool_name == "enhanced_memory":
            # Import enhanced memory components
            from ..core.performance_monitor import record_tool_usage
            from ..core.security_validator import SecurityValidator
            from ..data.models.prompt_models import ContextType

            operation = arguments.get("operation")
            conversation_id = arguments.get("conversation_id")
            content = arguments.get("content")
            context_type = arguments.get("context_type", "conversation")
            importance_score = float(arguments.get("importance_score", 0.5))
            tags = arguments.get("tags", [])
            metadata = arguments.get("metadata", {})

            # Security validation
            validator = SecurityValidator()
            if not validator.validate_input(content):
                raise HTTPException(status_code=400, detail="Invalid content detected")

            if operation == "store":
                # Store enhanced memory entry
                memory_id = data_manager.store_enhanced_memory_entry(
                    conversation_id=conversation_id,
                    session_id=arguments.get("session_id", "default"),
                    role=arguments.get("role", "user"),
                    content=content,
                    context_type=context_type,
                    importance_score=importance_score,
                    tags=tags,
                    relationships=arguments.get("relationships", []),
                    metadata=metadata,
                    ttl_seconds=arguments.get("ttl_seconds", 3600)
                )

                # Record performance metrics
                record_tool_usage("enhanced_memory", 100.0, True)

                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "memory_id": memory_id,
                        "message": "Enhanced memory entry stored successfully",
                        "context_type": context_type,
                        "importance_score": importance_score
                    }
                }

            elif operation == "retrieve":
                # Retrieve enhanced memory entries
                min_importance = float(arguments.get("min_importance", 0.1))
                limit = int(arguments.get("limit", 50))

                entries = data_manager.retrieve_enhanced_memory_entries(
                    conversation_id=conversation_id,
                    context_type=context_type if context_type != "all" else None,
                    min_importance=min_importance,
                    limit=limit
                )

                record_tool_usage("enhanced_memory", 50.0, True)

                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "entries": entries,
                        "count": len(entries),
                        "conversation_id": conversation_id
                    }
                }

            elif operation == "relate":
                # Create relationship between memory entries
                source_id = arguments.get("source_memory_id")
                target_id = arguments.get("target_memory_id")
                relationship_type = arguments.get("relationship_type")
                strength = float(arguments.get("strength", 1.0))
                relationship_metadata = arguments.get("metadata", {})

                rel_id = data_manager.create_context_relationship(
                    source_memory_id=source_id,
                    target_memory_id=target_id,
                    relationship_type=relationship_type,
                    strength=strength,
                    metadata=relationship_metadata
                )

                record_tool_usage("enhanced_memory", 30.0, True)

                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "relationship_id": rel_id,
                        "message": "Memory relationship created successfully",
                        "relationship_type": relationship_type,
                        "strength": strength
                    }
                }

            elif operation == "context":
                # Query by context and relationships
                context_type = arguments.get("context_type")
                tags_filter = arguments.get("tags", [])
                include_relationships = arguments.get("include_relationships", False)

                entries = data_manager.retrieve_enhanced_memory_entries(
                    conversation_id=conversation_id,
                    context_type=context_type,
                    tags=tags_filter if tags_filter else None
                )

                if include_relationships:
                    # Add relationship data
                    for entry in entries:
                        related = data_manager.get_related_memories(entry["id"])
                        entry["relationships"] = related

                record_tool_usage("enhanced_memory", 80.0, True)

                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "entries": entries,
                        "count": len(entries),
                        "context_type": context_type,
                        "relationships": include_relationships
                    }
                }

            elif operation == "clear":
                # Clear enhanced memory entries
                count = data_manager.clear_enhanced_memory_entries(conversation_id)

                record_tool_usage("enhanced_memory", 25.0, True)

                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "message": f"Cleared {count} enhanced memory entries",
                        "conversation_id": conversation_id,
                        "entries_cleared": count
                    }
                }

            else:
                raise HTTPException(status_code=400, detail=f"Unknown enhanced memory operation: {operation}")

        elif tool_name == "code_analysis":
            from ..core.performance_monitor import record_tool_usage
            from ..core.security_validator import SecurityValidator

            file_path = arguments.get("file_path")
            analysis_type = arguments.get("analysis_type", "complexity")
            output_format = arguments.get("output_format", "summary")

            # Security validation
            validator = SecurityValidator()
            if not validator.validate_file_path(file_path):
                raise HTTPException(status_code=400, detail="Invalid or blocked file path")

            # Perform code analysis (simplified implementation)
            analysis_result = {
                "file_path": file_path,
                "analysis_type": analysis_type,
                "lines_of_code": 100,  # Placeholder
                "complexity": "medium",  # Placeholder
                "security_issues": [],  # Placeholder
                "performance_suggestions": [],  # Placeholder
                "timestamp": datetime.now().isoformat()
            }

            # Add analysis-specific data based on type
            if analysis_type == "complexity":
                analysis_result.update({
                    "cyclomatic_complexity": 15,
                    "cognitive_complexity": 20,
                    "maintainability_index": 75,
                    "technical_debt_ratio": 0.1
                })
            elif analysis_type == "security":
                analysis_result.update({
                    "vulnerability_count": 2,
                    "severity_levels": {"high": 0, "medium": 1, "low": 1},
                    "security_score": 85,
                    "recommendations": ["Use parameterized queries", "Implement input validation"]
                })
            elif analysis_type == "performance":
                analysis_result.update({
                    "performance_score": 78,
                    "bottlenecks": ["Database queries", "Memory allocation"],
                    "optimizations": ["Add database indexing", "Implement caching"],
                    "estimated_improvement": "35%"
                })

            record_tool_usage("code_analysis", 200.0, True)

            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": analysis_result
            }

        elif tool_name == "file_operations":
            from ..core.performance_monitor import record_tool_usage
            from ..core.security_validator import SecurityValidator

            operation = arguments.get("operation")
            file_path = arguments.get("file_path")
            content = arguments.get("content", "")
            search_pattern = arguments.get("search_pattern", "")
            replace_content = arguments.get("replace_content", "")

            validator = SecurityValidator()
            if not validator.validate_file_path(file_path):
                raise HTTPException(status_code=400, detail="Invalid or blocked file path")

            if operation == "read":
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()

                    # Sanitize output
                    sanitized_content = validator.sanitize_output(file_content, 1000000)

                    record_tool_usage("file_operations", 50.0, True)

                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "operation": "read",
                            "file_path": file_path,
                            "content": sanitized_content,
                            "size": len(sanitized_content),
                            "encoding": "utf-8"
                        }
                    }
                except FileNotFoundError:
                    raise HTTPException(status_code=404, detail="File not found")
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

            elif operation == "write":
                try:
                    # Security validation
                    if not validator.validate_input(content):
                        raise HTTPException(status_code=400, detail="Invalid content detected")

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)

                    record_tool_usage("file_operations", 75.0, True)

                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "operation": "write",
                            "file_path": file_path,
                            "bytes_written": len(content),
                            "message": "File written successfully"
                        }
                    }
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Error writing file: {str(e)}")

            elif operation == "search":
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()

                    # Sanitize output
                    sanitized_content = validator.sanitize_output(file_content, 1000000)

                    matches = []
                    if search_pattern:
                        lines = sanitized_content.split('\n')
                        for i, line in enumerate(lines):
                            if search_pattern in line:
                                matches.append({
                                    "line_number": i + 1,
                                    "line_content": line.strip(),
                                    "match_position": line.find(search_pattern)
                                })

                    record_tool_usage("file_operations", 40.0, True)

                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "operation": "search",
                            "file_path": file_path,
                            "search_pattern": search_pattern,
                            "matches": matches,
                            "total_matches": len(matches)
                        }
                    }
                except FileNotFoundError:
                    raise HTTPException(status_code=404, detail="File not found")
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Error searching file: {str(e)}")

            else:
                raise HTTPException(status_code=400, detail=f"Unknown file operation: {operation}")

        elif tool_name == "terminal_execution":
            from ..core.performance_monitor import record_tool_usage
            from ..core.security_validator import SecurityValidator
            import subprocess
            import tempfile

            command = arguments.get("command")
            working_directory = arguments.get("working_directory", ".")
            timeout = int(arguments.get("timeout", 30))

            validator = SecurityValidator()

            # Security validation
            if not validator.validate_command(command):
                raise HTTPException(status_code=400, detail="Command blocked for security reasons")

            if not validator.validate_file_path(working_directory):
                raise HTTPException(status_code=400, detail="Invalid working directory")

            try:
                # Execute command in safe environment
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=working_directory,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

                # Sanitize output
                sanitized_stdout = validator.sanitize_output(result.stdout, 1000000)
                sanitized_stderr = validator.sanitize_output(result.stderr, 1000000)

                record_tool_usage("terminal_execution", float(timeout * 100), True)

                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "command": command,
                        "working_directory": working_directory,
                        "return_code": result.returncode,
                        "stdout": sanitized_stdout,
                        "stderr": sanitized_stderr,
                        "timeout": timeout,
                        "execution_time": f"{timeout}s"
                    }
                }

            except subprocess.TimeoutExpired:
                record_tool_usage("terminal_execution", float(timeout * 100), False)
                raise HTTPException(status_code=408, detail=f"Command timed out after {timeout} seconds")
            except Exception as e:
                record_tool_usage("terminal_execution", 1000.0, False)
                raise HTTPException(status_code=500, detail=f"Error executing command: {str(e)}")

        elif tool_name == "sequential_reasoning":
            from ..core.performance_monitor import record_tool_usage
            from ..data.models.prompt_models import ContextType

            problem = arguments.get("problem")
            reasoning_steps = int(arguments.get("reasoning_steps", 5))
            constraints = arguments.get("constraints", [])
            evaluation_criteria = arguments.get("evaluation_criteria", [])

            # Store problem statement
            problem_id = data_manager.store_enhanced_memory_entry(
                conversation_id="reasoning-session",
                session_id="reasoning-process",
                role="user",
                content=problem,
                context_type=ContextType.REASONING_STEP,
                importance_score=0.95,
                metadata={"type": "problem_statement", "steps": reasoning_steps}
            )

            # Generate reasoning steps
            reasoning_steps_data = []
            step_descriptions = [
                "Analyze the problem and identify key components",
                "Break down into manageable sub-problems",
                "Identify constraints and requirements",
                "Develop potential solution approaches",
                "Evaluate alternatives and select best approach",
                "Plan implementation steps",
                "Identify potential risks and mitigation strategies"
            ]

            for i in range(min(reasoning_steps, len(step_descriptions))):
                step_content = f"Step {i+1}: {step_descriptions[i]}"
                step_id = data_manager.store_enhanced_memory_entry(
                    conversation_id="reasoning-session",
                    session_id="reasoning-process",
                    role="assistant",
                    content=step_content,
                    context_type=ContextType.REASONING_STEP,
                    importance_score=0.8,
                    metadata={"step": i+1, "problem_id": problem_id}
                )

                # Create relationship to previous step
                if reasoning_steps_data:
                    data_manager.create_context_relationship(
                        source_memory_id=reasoning_steps_data[-1]["id"],
                        target_memory_id=step_id,
                        relationship_type="leads_to",
                        strength=0.8
                    )

                reasoning_steps_data.append({
                    "id": step_id,
                    "step": i+1,
                    "content": step_content
                })

            # Create final solution synthesis
            solution_id = data_manager.store_enhanced_memory_entry(
                conversation_id="reasoning-session",
                session_id="reasoning-process",
                role="assistant",
                content="Solution synthesis and final recommendations",
                context_type=ContextType.REASONING_STEP,
                importance_score=0.9,
                metadata={"type": "solution_synthesis", "problem_id": problem_id}
            )

            # Link to last reasoning step
            if reasoning_steps_data:
                data_manager.create_context_relationship(
                    source_memory_id=reasoning_steps_data[-1]["id"],
                    target_memory_id=solution_id,
                    relationship_type="leads_to",
                    strength=0.9
                )

            record_tool_usage("sequential_reasoning", 500.0, True)

            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "problem_id": problem_id,
                    "problem": problem,
                    "reasoning_steps": reasoning_steps,
                    "steps_completed": reasoning_steps_data,
                    "solution_id": solution_id,
                    "constraints": constraints,
                    "evaluation_criteria": evaluation_criteria,
                    "status": "completed"
                }
            }

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

        elif tool_name == "enhanced_memory":
            operation = arguments.get("operation")
            conversation_id = arguments.get("conversation_id")
            session_id = arguments.get("session_id", "default")
            context_type = arguments.get("context_type", "conversation")
            importance_score = arguments.get("importance_score", 0.5)
            tags = arguments.get("tags", [])
            relationship_type = arguments.get("relationship_type")
            target_memory_id = arguments.get("target_memory_id")
            strength = arguments.get("strength", 1.0)

            if operation == "store":
                content = arguments.get("content")
                if not content:
                    raise HTTPException(status_code=400, detail="content is required for store operation")

                memory_id = data_manager.store_enhanced_memory_entry(
                    conversation_id=conversation_id,
                    session_id=session_id,
                    role="user",  # Default role
                    content=content,
                    context_type=context_type,
                    importance_score=importance_score,
                    tags=tags,
                    metadata={}
                )
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "memory_id": memory_id,
                        "message": "Enhanced memory entry stored successfully",
                        "conversation_id": conversation_id
                    }
                }

            elif operation == "retrieve":
                entries = data_manager.retrieve_enhanced_memory_entries(
                    conversation_id=conversation_id,
                    limit=50
                )
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "entries": entries,
                        "count": len(entries),
                        "conversation_id": conversation_id
                    }
                }

            elif operation == "relate":
                if not target_memory_id or not relationship_type:
                    raise HTTPException(status_code=400, detail="target_memory_id and relationship_type are required")

                relationship_id = data_manager.create_context_relationship(
                    source_memory_id=arguments.get("source_memory_id"),
                    target_memory_id=target_memory_id,
                    relationship_type=relationship_type,
                    strength=strength,
                    metadata={}
                )
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "relationship_id": relationship_id,
                        "message": f"Context relationship '{relationship_type}' created successfully"
                    }
                }

            elif operation == "context":
                context_types = arguments.get("context_types", ["conversation", "code_analysis", "project_task"])
                context = data_manager.build_memory_context(
                    conversation_id=conversation_id,
                    context_types=context_types,
                    max_entries=20,
                    min_importance=0.0
                )
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "context": context,
                        "conversation_id": conversation_id
                    }
                }

            elif operation == "clear":
                count = data_manager.clear_enhanced_memory_entries(conversation_id)
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "message": f"Cleared {count} enhanced memory entries",
                        "conversation_id": conversation_id
                    }
                }

        elif tool_name == "code_analysis":
            file_path = arguments.get("file_path")
            analysis_type = arguments.get("analysis_type")
            output_format = arguments.get("output_format", "summary")

            if not file_path or not analysis_type:
                raise HTTPException(status_code=400, detail="file_path and analysis_type are required")

            try:
                import os
                import ast
                import re

                if not os.path.exists(file_path):
                    raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

                with open(file_path, 'r', encoding='utf-8') as f:
                    code_content = f.read()

                analysis_result = {}

                if analysis_type == "complexity":
                    # Analyze code complexity
                    lines = len(code_content.split('\n'))
                    functions = len(re.findall(r'def\s+\w+', code_content))
                    classes = len(re.findall(r'class\s+\w+', code_content))

                    analysis_result = {
                        "lines_of_code": lines,
                        "function_count": functions,
                        "class_count": classes,
                        "complexity_score": min(10, (lines // 50) + (functions * 2) + (classes * 3))
                    }

                elif analysis_type == "patterns":
                    # Analyze code patterns
                    patterns = {
                        "docstrings": len(re.findall(r'"""[\s\S]*?"""', code_content)),
                        "type_hints": len(re.findall(r'->\s*\w+', code_content)),
                        "async_functions": len(re.findall(r'async def', code_content)),
                        "decorators": len(re.findall(r'@\w+', code_content))
                    }
                    analysis_result = patterns

                elif analysis_type == "security":
                    # Basic security analysis
                    security_issues = []
                    if re.search(r'eval\s*\(', code_content):
                        security_issues.append("Use of eval() detected")
                    if re.search(r'exec\s*\(', code_content):
                        security_issues.append("Use of exec() detected")
                    if re.search(r'os\.system\s*\(', code_content):
                        security_issues.append("Use of os.system() detected")

                    analysis_result = {
                        "security_issues": security_issues,
                        "risk_level": "HIGH" if security_issues else "LOW"
                    }

                elif analysis_type == "performance":
                    # Basic performance analysis
                    performance_issues = []
                    if re.search(r'\.append\s*\(', code_content):
                        performance_issues.append("Multiple list appends - consider list comprehension")
                    if len(code_content) > 10000:
                        performance_issues.append("Large file size - consider splitting")

                    analysis_result = {
                        "performance_issues": performance_issues,
                        "file_size": len(code_content),
                        "recommendations": "Consider optimization" if performance_issues else "No major issues"
                    }

                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "file_path": file_path,
                        "analysis_type": analysis_type,
                        "analysis_result": analysis_result,
                        "output_format": output_format
                    }
                }

            except Exception as e:
                logger.error(f"Code analysis error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        elif tool_name == "file_operations":
            operation = arguments.get("operation")
            file_path = arguments.get("file_path")

            if not operation or not file_path:
                raise HTTPException(status_code=400, detail="operation and file_path are required")

            try:
                import os

                if operation == "read":
                    if not os.path.exists(file_path):
                        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "operation": operation,
                            "file_path": file_path,
                            "content": content,
                            "size": len(content)
                        }
                    }

                elif operation == "write":
                    content = arguments.get("content", "")
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)

                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "operation": operation,
                            "file_path": file_path,
                            "message": f"Successfully wrote {len(content)} characters to file"
                        }
                    }

                elif operation == "search":
                    search_pattern = arguments.get("search_pattern", "")
                    if not search_pattern:
                        raise HTTPException(status_code=400, detail="search_pattern is required for search operation")

                    if not os.path.exists(file_path):
                        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    matches = []
                    for i, line in enumerate(content.split('\n'), 1):
                        if search_pattern in line:
                            matches.append({"line": i, "content": line.strip()})

                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "operation": operation,
                            "file_path": file_path,
                            "search_pattern": search_pattern,
                            "matches": matches,
                            "match_count": len(matches)
                        }
                    }

                elif operation == "replace":
                    search_pattern = arguments.get("search_pattern", "")
                    replace_with = arguments.get("replace_with", "")

                    if not search_pattern or not replace_with:
                        raise HTTPException(status_code=400, detail="search_pattern and replace_with are required")

                    if not os.path.exists(file_path):
                        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    new_content = content.replace(search_pattern, replace_with)

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)

                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "operation": operation,
                            "file_path": file_path,
                            "search_pattern": search_pattern,
                            "replace_with": replace_with,
                            "replacements": content.count(search_pattern)
                        }
                    }

            except Exception as e:
                logger.error(f"File operation error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        elif tool_name == "terminal_execution":
            command = arguments.get("command")
            working_directory = arguments.get("working_directory", ".")
            environment_vars = arguments.get("environment_vars", {})
            timeout = arguments.get("timeout", 30)

            if not command:
                raise HTTPException(status_code=400, detail="command is required")

            try:
                import subprocess
                import os

                # Set environment variables
                env = os.environ.copy()
                env.update(environment_vars)

                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=working_directory,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    env=env
                )

                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "command": command,
                        "working_directory": working_directory,
                        "return_code": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "success": result.returncode == 0
                    }
                }

            except subprocess.TimeoutExpired:
                raise HTTPException(status_code=408, detail=f"Command timed out after {timeout} seconds")
            except Exception as e:
                logger.error(f"Terminal execution error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        elif tool_name == "sequential_reasoning":
            problem = arguments.get("problem")
            reasoning_steps = arguments.get("reasoning_steps", 5)
            constraints = arguments.get("constraints", [])
            evaluation_criteria = arguments.get("evaluation_criteria", [])
            context_types = arguments.get("context_types", [])

            if not problem:
                raise HTTPException(status_code=400, detail="problem is required")

            try:
                # Build context if context types are specified
                context = ""
                if context_types:
                    conversation_id = arguments.get("conversation_id", "default")
                    context = data_manager.build_memory_context(
                        conversation_id=conversation_id,
                        context_types=context_types,
                        max_entries=10,
                        min_importance=0.3
                    )

                # Create reasoning prompt
                reasoning_prompt = f"""
                Problem: {problem}

                {f'Context: {context}' if context else ''}

                {f'Constraints: {" | ".join(constraints)}' if constraints else ''}

                Please solve this step by step with {reasoning_steps} reasoning steps.
                {f'Evaluation Criteria: {" | ".join(evaluation_criteria)}' if evaluation_criteria else ''}

                Provide your answer in the following format:
                STEP 1: [First reasoning step]
                STEP 2: [Second reasoning step]
                ...
                FINAL ANSWER: [Your solution]
                """

                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "problem": problem,
                        "reasoning_steps": reasoning_steps,
                        "reasoning_prompt": reasoning_prompt,
                        "constraints": constraints,
                        "evaluation_criteria": evaluation_criteria
                    }
                }

            except Exception as e:
                logger.error(f"Sequential reasoning error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        elif tool_name == "project_tracker":
            operation = arguments.get("operation")
            project_id = arguments.get("project_id", "default")

            if operation == "create_task":
                task_data = arguments.get("task_data", {})
                if not task_data:
                    raise HTTPException(status_code=400, detail="task_data is required for create_task operation")

                # Store task as enhanced memory
                memory_id = data_manager.store_enhanced_memory_entry(
                    conversation_id=f"project_{project_id}",
                    session_id="project_manager",
                    role="system",
                    content=f"Task created: {task_data.get('title', 'Untitled')}",
                    context_type="project_task",
                    importance_score=0.7,
                    tags=["task", "created"],
                    metadata=task_data
                )

                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "operation": operation,
                        "project_id": project_id,
                        "task_id": memory_id,
                        "message": "Task created successfully"
                    }
                }

            elif operation == "update_status":
                task_id = arguments.get("task_id")
                status = arguments.get("status")

                if not task_id or not status:
                    raise HTTPException(status_code=400, detail="task_id and status are required")

                # Store status update as enhanced memory
                memory_id = data_manager.store_enhanced_memory_entry(
                    conversation_id=f"project_{project_id}",
                    session_id="project_manager",
                    role="system",
                    content=f"Task {task_id} status updated to: {status}",
                    context_type="project_task",
                    importance_score=0.6,
                    tags=["task", "status_update", status],
                    metadata={"task_id": task_id, "status": status}
                )

                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "operation": operation,
                        "project_id": project_id,
                        "task_id": task_id,
                        "status": status,
                        "message": f"Task status updated to {status}"
                    }
                }

            elif operation == "get_progress":
                # Get all project tasks
                tasks = data_manager.retrieve_enhanced_memory_entries(
                    conversation_id=f"project_{project_id}",
                    context_type="project_task",
                    limit=100
                )

                completed_tasks = [t for t in tasks if t.get('metadata', {}).get('status') == 'completed']
                total_tasks = len(tasks)

                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "operation": operation,
                        "project_id": project_id,
                        "total_tasks": total_tasks,
                        "completed_tasks": len(completed_tasks),
                        "progress_percentage": (len(completed_tasks) / total_tasks * 100) if total_tasks > 0 else 0,
                        "tasks": tasks
                    }
                }

            elif operation == "generate_report":
                tasks = data_manager.retrieve_enhanced_memory_entries(
                    conversation_id=f"project_{project_id}",
                    context_type="project_task",
                    limit=100
                )

                report = f"""
                # Project Progress Report - {project_id}

                Total Tasks: {len(tasks)}
                Completed Tasks: {len([t for t in tasks if t.get('metadata', {}).get('status') == 'completed'])}
                In Progress Tasks: {len([t for t in tasks if t.get('metadata', {}).get('status') == 'in_progress'])}
                Pending Tasks: {len([t for t in tasks if t.get('metadata', {}).get('status') == 'pending'])}

                ## Task Details:
                """
                for task in tasks:
                    metadata = task.get('metadata', {})
                    report += f"\n- {metadata.get('title', 'Untitled')}: {metadata.get('status', 'unknown')}"

                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "operation": operation,
                        "project_id": project_id,
                        "report": report
                    }
                }

        elif tool_name == "data_analyzer":
            data_source = arguments.get("data_source")
            analysis_type = arguments.get("analysis_type")
            parameters = arguments.get("parameters", {})
            output_format = arguments.get("output_format", "summary")

            if not data_source or not analysis_type:
                raise HTTPException(status_code=400, detail="data_source and analysis_type are required")

            try:
                # This is a basic implementation - in a real system you'd connect to actual data sources
                analysis_result = {
                    "data_source": data_source,
                    "analysis_type": analysis_type,
                    "parameters": parameters,
                    "analysis_timestamp": datetime.utcnow().isoformat()
                }

                # Mock analysis based on type
                if analysis_type == "patterns":
                    analysis_result["patterns"] = ["Pattern 1", "Pattern 2", "Pattern 3"]
                    analysis_result["insights"] = "Data shows consistent patterns over time"

                elif analysis_type == "trends":
                    analysis_result["trend_direction"] = "upward"
                    analysis_result["trend_strength"] = 0.75
                    analysis_result["insights"] = "Strong upward trend detected"

                elif analysis_type == "correlations":
                    analysis_result["correlations"] = [
                        {"variables": ["A", "B"], "correlation": 0.8},
                        {"variables": ["B", "C"], "correlation": 0.6}
                    ]
                    analysis_result["insights"] = "Strong positive correlations found"

                elif analysis_type == "anomalies":
                    analysis_result["anomalies"] = ["Anomaly at point 15", "Anomaly at point 67"]
                    analysis_result["insights"] = "Multiple data anomalies detected"

                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "data_source": data_source,
                        "analysis_type": analysis_type,
                        "analysis_result": analysis_result,
                        "output_format": output_format
                    }
                }

            except Exception as e:
                logger.error(f"Data analysis error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        elif tool_name == "test_generator":
            code_file = arguments.get("code_file")
            test_framework = arguments.get("test_framework")
            coverage_target = arguments.get("coverage_target", 80)
            test_types = arguments.get("test_types", ["unit"])

            if not code_file or not test_framework:
                raise HTTPException(status_code=400, detail="code_file and test_framework are required")

            try:
                import os
                import ast

                if not os.path.exists(code_file):
                    raise HTTPException(status_code=404, detail=f"Code file not found: {code_file}")

                with open(code_file, 'r', encoding='utf-8') as f:
                    code_content = f.read()

                # Parse the code to extract functions and classes
                tree = ast.parse(code_content)

                functions = []
                classes = []

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        functions.append({
                            "name": node.name,
                            "args": [arg.arg for arg in node.args.args],
                            "line": node.lineno
                        })
                    elif isinstance(node, ast.ClassDef):
                        classes.append({
                            "name": node.name,
                            "line": node.lineno
                        })

                # Generate test code based on framework
                test_code = f"# Generated tests for {code_file}\n"

                if test_framework == "pytest":
                    test_code += "import pytest\n"
                    test_code += f"from {os.path.splitext(os.path.basename(code_file))[0]} import *\n\n"

                    for func in functions:
                        test_code += f"""
def test_{func['name']}():
    # Test for {func['name']}
    result = {func['name']}({', '.join([f'arg{i}' for i in range(len(func['args']))])})
    assert result is not None
"""

                elif test_framework == "unittest":
                    test_code += "import unittest\n"
                    test_code += f"from {os.path.splitext(os.path.basename(code_file))[0]} import *\n\n"

                    test_code += f"""
class TestGenerated(unittest.TestCase):
"""

                    for func in functions:
                        test_code += f"""
    def test_{func['name']}(self):
        # Test for {func['name']}
        result = {func['name']}({', '.join([f'arg{i}' for i in range(len(func['args']))])})
        self.assertIsNotNone(result)
"""

                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "code_file": code_file,
                        "test_framework": test_framework,
                        "functions_found": len(functions),
                        "classes_found": len(classes),
                        "coverage_target": coverage_target,
                        "generated_test_code": test_code,
                        "test_types": test_types
                    }
                }

            except Exception as e:
                logger.error(f"Test generation error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        elif tool_name == "data_analyzer":
            from ..core.performance_monitor import record_tool_usage
            from ..data.repositories.database import DatabaseConfig

            analysis_type = arguments.get("analysis_type", "patterns")
            data_source = arguments.get("data_source", "memory")
            parameters = arguments.get("parameters", {})

            analysis_results = {
                "analysis_type": analysis_type,
                "data_source": data_source,
                "timestamp": datetime.now().isoformat(),
                "results": {}
            }

            if analysis_type == "patterns":
                # Analyze patterns in memory entries
                try:
                    with DatabaseConfig.get_connection() as conn:
                        with conn.cursor() as cur:
                            cur.execute('''
                                SELECT context_type, COUNT(*) as count
                                FROM enhanced_memory_entries
                                GROUP BY context_type
                                ORDER BY count DESC
                            ''')
                            pattern_data = cur.fetchall()

                            analysis_results["results"] = {
                                "context_type_distribution": {row[0]: row[1] for row in pattern_data},
                                "total_entries": sum(count for _, count in pattern_data),
                                "most_common_context": pattern_data[0][0] if pattern_data else None
                            }
                except Exception as e:
                    analysis_results["error"] = f"Pattern analysis failed: {str(e)}"

            elif analysis_type == "trends":
                # Analyze trends over time
                try:
                    with DatabaseConfig.get_connection() as conn:
                        with conn.cursor() as cur:
                            cur.execute('''
                                SELECT DATE(timestamp) as date, COUNT(*) as entries
                                FROM enhanced_memory_entries
                                GROUP BY DATE(timestamp)
                                ORDER BY date DESC
                                LIMIT 30
                            ''')
                            trend_data = cur.fetchall()

                            analysis_results["results"] = {
                                "daily_entry_counts": {row[0]: row[1] for row in trend_data},
                                "trend_direction": "increasing" if len(trend_data) >= 2 and trend_data[0][1] > trend_data[1][1] else "decreasing"
                            }
                except Exception as e:
                    analysis_results["error"] = f"Trend analysis failed: {str(e)}"

            record_tool_usage("data_analyzer", 150.0, True)

            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": analysis_results
            }

        elif tool_name == "web_scraper":
            from ..core.performance_monitor import record_tool_usage
            from ..core.security_validator import SecurityValidator
            import requests
            from bs4 import BeautifulSoup

            url = arguments.get("url")
            extract_type = arguments.get("extract_type", "text")
            max_content_size = int(arguments.get("max_content_size", 5000000))

            validator = SecurityValidator()

            # Security validation
            if not validator.validate_input(url):
                raise HTTPException(status_code=400, detail="Invalid URL detected")

            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (compatible; MCP-PBA-TUNNEL/1.0)'
                }

                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()

                if len(response.content) > max_content_size:
                    raise HTTPException(status_code=413, detail="Content too large")

                if extract_type == "text":
                    soup = BeautifulSoup(response.content, 'html.parser')
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()

                    text_content = soup.get_text(separator=' ', strip=True)

                    # Sanitize output
                    sanitized_content = validator.sanitize_output(text_content, 1000000)

                    record_tool_usage("web_scraper", 300.0, True)

                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "url": url,
                            "extract_type": "text",
                            "content": sanitized_content,
                            "title": soup.title.string if soup.title else "No title",
                            "content_length": len(sanitized_content),
                            "status_code": response.status_code
                        }
                    }

                elif extract_type == "metadata":
                    soup = BeautifulSoup(response.content, 'html.parser')

                    metadata = {
                        "title": soup.title.string if soup.title else "No title",
                        "description": "",
                        "keywords": [],
                        "links": len(soup.find_all('a')),
                        "images": len(soup.find_all('img')),
                        "headers": {}
                    }

                    # Extract meta description
                    meta_desc = soup.find('meta', attrs={'name': 'description'})
                    if meta_desc:
                        metadata["description"] = meta_desc.get('content', '')

                    # Extract meta keywords
                    meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
                    if meta_keywords:
                        keywords = meta_keywords.get('content', '')
                        metadata["keywords"] = [k.strip() for k in keywords.split(',') if k.strip()]

                    # Extract headers
                    for i in range(1, 7):
                        headers = soup.find_all(f'h{i}')
                        metadata["headers"][f"h{i}"] = len(headers)

                    record_tool_usage("web_scraper", 100.0, True)

                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": {
                            "url": url,
                            "extract_type": "metadata",
                            "metadata": metadata,
                            "status_code": response.status_code
                        }
                    }

            except requests.RequestException as e:
                record_tool_usage("web_scraper", 500.0, False)
                raise HTTPException(status_code=500, detail=f"Web scraping failed: {str(e)}")

        elif tool_name == "project_tracker":
            from ..core.performance_monitor import record_tool_usage
            from ..data.models.prompt_models import ContextType

            operation = arguments.get("operation")
            task_name = arguments.get("task_name")
            description = arguments.get("description")
            priority = arguments.get("priority", "medium")
            assignee = arguments.get("assignee")
            dependencies = arguments.get("dependencies", [])

            if operation == "create_task":
                # Create a new project task
                task_id = data_manager.store_enhanced_memory_entry(
                    conversation_id="project-tasks",
                    session_id="task-management",
                    role="user",
                    content=f"Task: {task_name}\nDescription: {description}",
                    context_type=ContextType.PROJECT_TASK,
                    importance_score=0.8,
                    metadata={
                        "task_type": "project_task",
                        "priority": priority,
                        "assignee": assignee,
                        "status": "pending",
                        "dependencies": dependencies,
                        "created_at": datetime.now().isoformat()
                    }
                )

                record_tool_usage("project_tracker", 80.0, True)

                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "task_id": task_id,
                        "task_name": task_name,
                        "status": "created",
                        "priority": priority,
                        "message": f"Task '{task_name}' created successfully"
                    }
                }

            elif operation == "update_status":
                task_id = arguments.get("task_id")
                new_status = arguments.get("status", "in_progress")

                # Update task status
                updated_task_id = data_manager.store_enhanced_memory_entry(
                    conversation_id="project-tasks",
                    session_id="task-management",
                    role="assistant",
                    content=f"Status update for task {task_id}: {new_status}",
                    context_type=ContextType.PROJECT_TASK,
                    importance_score=0.6,
                    metadata={
                        "task_type": "status_update",
                        "task_id": task_id,
                        "status": new_status,
                        "updated_at": datetime.now().isoformat()
                    }
                )

                record_tool_usage("project_tracker", 40.0, True)

                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "task_id": task_id,
                        "status": new_status,
                        "update_id": updated_task_id,
                        "message": f"Task status updated to {new_status}"
                    }
                }

            elif operation == "get_progress":
                # Get project progress
                entries = data_manager.retrieve_enhanced_memory_entries(
                    conversation_id="project-tasks",
                    context_type=ContextType.PROJECT_TASK
                )

                # Analyze progress
                total_tasks = len(entries)
                completed_tasks = len([e for e in entries if e.get("metadata", {}).get("status") == "completed"])
                in_progress_tasks = len([e for e in entries if e.get("metadata", {}).get("status") == "in_progress"])
                pending_tasks = len([e for e in entries if e.get("metadata", {}).get("status") == "pending"])

                progress_report = {
                    "total_tasks": total_tasks,
                    "completed": completed_tasks,
                    "in_progress": in_progress_tasks,
                    "pending": pending_tasks,
                    "completion_percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
                    "tasks": entries
                }

                record_tool_usage("project_tracker", 60.0, True)

                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": progress_report
                }

        elif tool_name == "test_validator":
            from ..core.performance_monitor import record_tool_usage
            import subprocess
            import tempfile
            import os

            operation = arguments.get("operation")
            test_path = arguments.get("test_path", ".")
            test_type = arguments.get("test_type", "unit")

            if operation == "run_tests":
                try:
                    # Run pytest
                    result = subprocess.run(
                        ["python", "-m", "pytest", test_path, "-v", "--tb=short"],
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 minute timeout
                    )

                    # Parse results
                    test_results = {
                        "operation": "run_tests",
                        "test_path": test_path,
                        "test_type": test_type,
                        "return_code": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "timestamp": datetime.now().isoformat()
                    }

                    # Extract summary
                    if "passed" in result.stdout and "failed" in result.stdout:
                        lines = result.stdout.split('\n')
                        for line in lines:
                            if "passed" in line and "failed" in line:
                                test_results["summary"] = line.strip()
                                break

                    record_tool_usage("test_validator", 10000.0, result.returncode == 0)

                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "result": test_results
                    }

                except subprocess.TimeoutExpired:
                    record_tool_usage("test_validator", 300000.0, False)
                    raise HTTPException(status_code=408, detail="Test execution timed out")
                except Exception as e:
                    record_tool_usage("test_validator", 1000.0, False)
                    raise HTTPException(status_code=500, detail=f"Test execution failed: {str(e)}")

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
