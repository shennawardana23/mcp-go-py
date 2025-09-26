import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from mcp_pba_tunnel.data.repositories.database import DatabaseConfig

logger = logging.getLogger(__name__)

class MemoryCleanupService:
    """Service for cleaning up old memory entries"""

    def __init__(self):
        self.cleanup_interval = 3600  # 1 hour
        self.max_entries_per_conversation = 1000
        self.default_ttl = 86400  # 24 hours

    async def cleanup_expired_entries(self):
        """Clean up entries that have exceeded their TTL"""
        try:
            with DatabaseConfig.get_connection() as conn:
                with conn.cursor() as cur:
                    # Find entries older than TTL
                    cur.execute('''
                        SELECT id, conversation_id, timestamp, ttl_seconds
                        FROM enhanced_memory_entries
                        WHERE timestamp < %s
                    ''', (datetime.now() - timedelta(seconds=self.default_ttl),))

                    expired_entries = cur.fetchall()

                    if expired_entries:
                        # Delete expired entries
                        entry_ids = [entry[0] for entry in expired_entries]
                        cur.execute('DELETE FROM enhanced_memory_entries WHERE id = ANY(%s)', (entry_ids,))

                        # Also delete related relationships
                        cur.execute('DELETE FROM context_relationships WHERE source_memory_id = ANY(%s) OR target_memory_id = ANY(%s)', (entry_ids, entry_ids))

                        conn.commit()
                        logger.info(f"Cleaned up {len(expired_entries)} expired memory entries")

        except Exception as e:
            logger.error(f"Error during memory cleanup: {e}")

    async def cleanup_large_conversations(self):
        """Clean up conversations with too many entries"""
        try:
            with DatabaseConfig.get_connection() as conn:
                with conn.cursor() as cur:
                    # Find conversations with too many entries
                    cur.execute('''
                        SELECT conversation_id, COUNT(*) as entry_count
                        FROM enhanced_memory_entries
                        GROUP BY conversation_id
                        HAVING COUNT(*) > %s
                        ORDER BY entry_count DESC
                    ''', (self.max_entries_per_conversation,))

                    large_conversations = cur.fetchall()

                    for conv_id, count in large_conversations:
                        # Keep only the most important entries
                        cur.execute('''
                            DELETE FROM enhanced_memory_entries
                            WHERE conversation_id = %s
                            AND id NOT IN (
                                SELECT id FROM enhanced_memory_entries
                                WHERE conversation_id = %s
                                ORDER BY importance_score DESC, timestamp DESC
                                LIMIT %s
                            )
                        ''', (conv_id, conv_id, self.max_entries_per_conversation))

                        logger.info(f"Cleaned up conversation {conv_id}: kept {self.max_entries_per_conversation} of {count} entries")

                    if large_conversations:
                        conn.commit()

        except Exception as e:
            logger.error(f"Error during conversation cleanup: {e}")

    async def run_cleanup_cycle(self):
        """Run a complete cleanup cycle"""
        logger.info("Starting memory cleanup cycle")

        await self.cleanup_expired_entries()
        await self.cleanup_large_conversations()

        logger.info("Memory cleanup cycle completed")

    def start_background_cleanup(self):
        """Start background cleanup task"""
        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(self.cleanup_interval)
                    await self.run_cleanup_cycle()
                except Exception as e:
                    logger.error(f"Error in cleanup loop: {e}")
                    await asyncio.sleep(60)  # Wait before retrying

        asyncio.create_task(cleanup_loop())
        logger.info(f"Started background memory cleanup (interval: {self.cleanup_interval}s)")

# Global cleanup service instance
memory_cleanup_service = MemoryCleanupService()
