#!/usr/bin/env python3
"""
MCP-PBA-TUNNEL: MCP Prompt-Based Architecture Tunnel

A FastAPI-based MCP server for standardized prompt engineering templates and AI agent integration.
"""

__version__ = "1.0.0"
__author__ = "MCP-PBA-TUNNEL Team"
__description__ = "Standardized AI-Powered Development Workflows"

from .core.config import get_config
from .server.fastapi_mcp_server import create_app

__all__ = [
    "__version__",
    "__author__",
    "__description__",
    "get_config",
    "create_app"
]
