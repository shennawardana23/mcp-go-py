"""
Database configuration and connection management
"""

import psycopg_pool
import psycopg
import threading
from contextlib import contextmanager
from typing import Generator, Optional

from ...core.config import get_database_url


class DatabaseConfig:
    """Database configuration and connection management"""

    _pool: Optional[psycopg_pool.ConnectionPool] = None
    _pool_lock = threading.Lock()

    @classmethod
    def get_connection_pool(cls) -> psycopg_pool.ConnectionPool:
        """Get or create database connection pool"""
        if cls._pool is None:
            with cls._pool_lock:
                if cls._pool is None:
                    database_url = get_database_url()
                    pool_kwargs = {
                        "conninfo": database_url,
                        "min_size": 5,
                        "max_size": 20,
                        "timeout": 30,
                        "num_workers": 3,
                    }

                    # PostgreSQL configuration

                    cls._pool = psycopg_pool.ConnectionPool(**pool_kwargs)

        return cls._pool

    @classmethod
    def close_connection_pool(cls):
        """Close the database connection pool"""
        if cls._pool is not None:
            cls._pool.close()
            cls._pool = None

    @classmethod
    @contextmanager
    def get_connection(cls) -> Generator[psycopg.Connection, None, None]:
        """Get database connection from pool"""
        pool = cls.get_connection_pool()
        conn = pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            pool.putconn(conn)


class DatabaseOperations:
    """Base class for database operations"""

    @staticmethod
    def execute_query(query: str, params: tuple = None, fetch: str = "all"):
        """Execute SQL query with proper connection management"""
        # Check if this is a DDL statement (CREATE, DROP, ALTER, etc.)
        ddl_keywords = ["CREATE", "DROP", "ALTER", "TRUNCATE"]
        query_upper = query.strip().upper()

        with DatabaseConfig.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())

                # DDL statements don't return data
                if any(keyword in query_upper for keyword in ddl_keywords):
                    return None

                if fetch == "one":
                    return cur.fetchone()
                elif fetch == "all":
                    return cur.fetchall()
                elif fetch == "count":
                    return cur.rowcount
                else:
                    return None

    @staticmethod
    def execute_insert(query: str, params: tuple = None) -> str:
        """Execute INSERT query and return inserted ID"""
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                return cur.fetchone()[0] if cur.description else None

    @staticmethod
    def execute_update(query: str, params: tuple = None) -> int:
        """Execute UPDATE query and return affected rows"""
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                return cur.rowcount

    @staticmethod
    def execute_delete(query: str, params: tuple = None) -> int:
        """Execute DELETE query and return affected rows"""
        with DatabaseConfig.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                return cur.rowcount