import time
import asyncio
import logging
import functools
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import json

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    data: Any
    timestamp: datetime
    ttl_seconds: int
    access_count: int = 0

class PerformanceOptimizer:
    """Performance optimization utilities"""

    def __init__(self):
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.query_cache: Dict[str, CacheEntry] = {}
        self.cache_stats = {
            'memory_hits': 0,
            'memory_misses': 0,
            'query_hits': 0,
            'query_misses': 0
        }

    def get_cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = json.dumps({
            'args': [str(arg) for arg in args],
            'kwargs': {k: str(v) for k, v in kwargs.items()}
        }, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()

    def get_from_cache(self, cache: Dict[str, CacheEntry], key: str, ttl_seconds: int) -> Optional[Any]:
        """Get data from cache if valid"""
        if key not in cache:
            self.cache_stats[f'{cache.__name__}_misses'] += 1
            return None

        entry = cache[key]
        entry.access_count += 1

        # Check TTL
        if datetime.now() - entry.timestamp > timedelta(seconds=ttl_seconds):
            del cache[key]
            self.cache_stats[f'{cache.__name__}_misses'] += 1
            return None

        self.cache_stats[f'{cache.__name__}_hits'] += 1
        return entry.data

    def set_cache(self, cache: Dict[str, CacheEntry], key: str, data: Any, ttl_seconds: int = 300):
        """Set data in cache"""
        cache[key] = CacheEntry(
            data=data,
            timestamp=datetime.now(),
            ttl_seconds=ttl_seconds
        )

    def cache_memory_query(self, func: Callable):
        """Decorator for caching memory queries"""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = self.get_cache_key(func.__name__, *args, **kwargs)

            # Try to get from cache
            cached_result = self.get_from_cache(self.memory_cache, cache_key, 300)
            if cached_result is not None:
                return cached_result

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            self.set_cache(self.memory_cache, cache_key, result, 300)

            return result
        return wrapper

    def cache_query_result(self, func: Callable):
        """Decorator for caching query results"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = self.get_cache_key(func.__name__, *args, **kwargs)

            # Try to get from cache
            cached_result = self.get_from_cache(self.query_cache, cache_key, 60)
            if cached_result is not None:
                return cached_result

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            self.set_cache(self.query_cache, cache_key, result, 60)

            return result
        return wrapper

    def measure_performance(self, func: Callable):
        """Decorator to measure function performance"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                logger.info(f"{func.__name__} executed in {execution_time:.4f}s")

                return result

            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"{func.__name__} failed after {execution_time:.4f}s: {e}")
                raise

        return wrapper

    def batch_process(self, items: List[Any], batch_size: int = 100):
        """Process items in batches for better performance"""
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]

    def optimize_query(self, query: str, params: tuple = None) -> tuple:
        """Optimize SQL query for better performance"""
        optimized_query = query

        # Add query hints for better performance
        if 'SELECT' in query.upper() and 'ORDER BY' not in query.upper():
            # Add LIMIT if missing
            if 'LIMIT' not in query.upper():
                optimized_query = query.rstrip(';') + ' LIMIT 1000;'

        return optimized_query, params

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_memory_requests = self.cache_stats['memory_hits'] + self.cache_stats['memory_misses']
        total_query_requests = self.cache_stats['query_hits'] + self.cache_stats['query_misses']

        return {
            'memory_cache': {
                'hits': self.cache_stats['memory_hits'],
                'misses': self.cache_stats['memory_misses'],
                'hit_rate': self.cache_stats['memory_hits'] / total_memory_requests if total_memory_requests > 0 else 0,
                'entries': len(self.memory_cache)
            },
            'query_cache': {
                'hits': self.cache_stats['query_hits'],
                'misses': self.cache_stats['query_misses'],
                'hit_rate': self.cache_stats['query_hits'] / total_query_requests if total_query_requests > 0 else 0,
                'entries': len(self.query_cache)
            }
        }

# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()

def get_performance_optimizer() -> PerformanceOptimizer:
    return performance_optimizer
