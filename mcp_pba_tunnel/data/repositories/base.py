"""
Base repository classes and interfaces
"""

import json
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, TypeVar, Generic, Protocol
from datetime import datetime
from uuid import UUID

from .database import DatabaseOperations

T = TypeVar('T')


class BaseRepository(Generic[T], DatabaseOperations):
    """Base repository class providing common CRUD operations"""

    def __init__(self, table_name: str):
        self.table_name = table_name

    def _serialize_json(self, data: Any) -> str:
        """Serialize data to JSON"""
        return json.dumps(data) if data is not None else None

    def _deserialize_json(self, data) -> Any:
        """Deserialize JSON data or return if already deserialized"""
        if data is None:
            return None
        elif isinstance(data, str):
            return json.loads(data)
        else:
            # Already deserialized (e.g., psycopg2 converted JSON to Python objects)
            return data

    def _format_timestamp(self, dt: datetime) -> str:
        """Format datetime for database"""
        return dt.isoformat() if dt else None