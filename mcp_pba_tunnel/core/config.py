#!/usr/bin/env python3
"""
Configuration management for MCP-PBA-TUNNEL
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Database
    database_url: str = Field(default="postgresql://postgres:password@localhost:5432/mcp_pba_tunnel")
    db_host: str = Field(default="localhost")
    db_port: str = Field(default="5432")
    db_name: str = Field(default="mcp_pba_tunnel")
    db_user: str = Field(default="postgres")
    db_password: str = Field(default="password")

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=9001)
    debug: bool = Field(default=False)

    # AWS
    aws_region: str = Field(default="us-east-1")
    lambda_memory: int = Field(default=512)
    lambda_timeout: int = Field(default=30)

    # AI Configuration
    openai_api_key: Optional[str] = Field(default=None)
    anthropic_api_key: Optional[str] = Field(default=None)
    default_model: str = Field(default="gpt-4")
    max_tokens: int = Field(default=4000)
    temperature: float = Field(default=0.7)

    # Redis/Cache
    redis_url: Optional[str] = Field(default=None)
    cache_ttl: int = Field(default=3600)

    # Security
    secret_key: str = Field(default="your-secret-key-change-in-production")
    cors_origins: list = Field(default=["*"])

    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
_settings = None


def get_settings() -> Settings:
    """Get application settings singleton"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def get_config() -> Dict[str, Any]:
    """Get configuration as dictionary"""
    settings = get_settings()

    # Try to load config from file
    config_file = Path("config/mcp_config.json")
    if config_file.exists():
        try:
            with open(config_file) as f:
                file_config = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            file_config = {}
    else:
        file_config = {}

    # Merge settings with file config
    config = {
        "database": {
            "url": settings.database_url,
            "pool_size": 20,
            "max_overflow": 30,
            "pool_timeout": 30,
            "pool_recycle": 3600
        },
        "server": {
            "host": settings.host,
            "port": settings.port,
            "debug": settings.debug
        },
        "aws": {
            "region": settings.aws_region,
            "lambda": {
                "memory_size": settings.lambda_memory,
                "timeout": settings.lambda_timeout
            }
        },
        "ai": {
            "default_model": settings.default_model,
            "max_tokens": settings.max_tokens,
            "temperature": settings.temperature,
            "supported_models": ["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet", "claude-3-haiku"]
        },
        "redis": {
            "url": settings.redis_url,
            "ttl": settings.cache_ttl
        } if settings.redis_url else None,
        "security": {
            "secret_key": settings.secret_key,
            "cors_origins": settings.cors_origins
        },
        "logging": {
            "level": settings.log_level,
            "format": settings.log_format
        }
    }

    # Update with file config if available
    for key, value in file_config.items():
        if key in config and isinstance(value, dict) and isinstance(config[key], dict):
            config[key].update(value)
        else:
            config[key] = value

    return config


def get_database_url() -> str:
    """Get PostgreSQL database URL from settings"""
    settings = get_settings()

    # AWS Lambda environment
    if os.environ.get('LAMBDA_TASK_ROOT'):
        return os.environ.get('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/mcp_pba_tunnel')

    # Always use PostgreSQL
    if all([settings.db_host, settings.db_name, settings.db_user, settings.db_password]):
        return f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

    return settings.database_url
