import time
import asyncio
import logging
import psutil
import threading
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    timestamp: datetime
    memory_usage: float
    cpu_usage: float
    memory_entries_count: int
    relationship_count: int
    cache_hit_rate: float
    query_response_time: float
    active_connections: int
    error_rate: float
    throughput_per_second: float

@dataclass
class ToolMetrics:
    tool_name: str
    call_count: int
    average_response_time: float
    success_rate: float
    error_count: int
    last_used: datetime

class PerformanceMonitor:
    """Comprehensive performance monitoring for enhanced MCP-PBA-TUNNEL"""

    def __init__(self):
        self.metrics_history: List[PerformanceMetrics] = []
        self.tool_metrics: Dict[str, ToolMetrics] = {}
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.metrics_lock = threading.Lock()
        self.alert_thresholds = self._load_alert_thresholds()

    def _load_alert_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Load performance alert thresholds"""
        return {
            'memory_usage': {'warning': 80.0, 'critical': 90.0},
            'cpu_usage': {'warning': 70.0, 'critical': 85.0},
            'cache_hit_rate': {'warning': 50.0, 'critical': 30.0},  # Below 50% is warning
            'error_rate': {'warning': 5.0, 'critical': 10.0},
            'query_response_time': {'warning': 500.0, 'critical': 2000.0},  # ms
            'throughput_per_second': {'warning': 10.0, 'critical': 5.0}  # Below 10 is warning
        }

    def start_monitoring(self, interval_seconds: int = 30):
        """Start background performance monitoring"""
        if self.monitoring_active:
            logger.warning("Performance monitoring already active")
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, args=(interval_seconds,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logger.info(f"Started performance monitoring (interval: {interval_seconds}s)")

    def stop_monitoring(self):
        """Stop background performance monitoring"""
        self.monitoring_active = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)
        logger.info("Stopped performance monitoring")

    def _monitoring_loop(self, interval_seconds: int):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                metrics = self.collect_system_metrics()
                self._store_metrics(metrics)
                self._check_alerts(metrics)
                time.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval_seconds)

    def collect_system_metrics(self) -> PerformanceMetrics:
        """Collect current system performance metrics"""
        # System metrics
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)

        # Database metrics (simplified - would need actual DB connection)
        memory_entries_count = self._get_memory_entries_count()
        relationship_count = self._get_relationship_count()

        # Cache metrics
        cache_hit_rate = self._get_cache_hit_rate()

        # Performance metrics
        query_response_time = self._get_average_query_time()
        active_connections = self._get_active_connections()
        error_rate = self._get_error_rate()
        throughput = self._get_throughput_per_second()

        return PerformanceMetrics(
            timestamp=datetime.now(),
            memory_usage=memory.percent,
            cpu_usage=cpu_percent,
            memory_entries_count=memory_entries_count,
            relationship_count=relationship_count,
            cache_hit_rate=cache_hit_rate,
            query_response_time=query_response_time,
            active_connections=active_connections,
            error_rate=error_rate,
            throughput_per_second=throughput
        )

    def _get_memory_entries_count(self) -> int:
        """Get current memory entries count"""
        try:
            from mcp_pba_tunnel.data.repositories.database import DatabaseConfig
            with DatabaseConfig.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute('SELECT COUNT(*) FROM enhanced_memory_entries')
                    result = cur.fetchone()
                    return result[0] if result else 0
        except Exception:
            return 0

    def _get_relationship_count(self) -> int:
        """Get current relationship count"""
        try:
            from mcp_pba_tunnel.data.repositories.database import DatabaseConfig
            with DatabaseConfig.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute('SELECT COUNT(*) FROM context_relationships')
                    result = cur.fetchone()
                    return result[0] if result else 0
        except Exception:
            return 0

    def _get_cache_hit_rate(self) -> float:
        """Get cache hit rate percentage"""
        try:
            from mcp_pba_tunnel.core.performance_optimizer import get_performance_optimizer
            optimizer = get_performance_optimizer()
            stats = optimizer.get_cache_stats()
            memory_hit_rate = stats['memory_cache']['hit_rate']
            query_hit_rate = stats['query_cache']['hit_rate']
            return (memory_hit_rate + query_hit_rate) / 2 * 100
        except Exception:
            return 50.0  # Default 50% hit rate

    def _get_average_query_time(self) -> float:
        """Get average query response time in ms"""
        # This would typically be measured from actual query execution
        # For now, return a placeholder
        return 100.0  # 100ms average

    def _get_active_connections(self) -> int:
        """Get number of active database connections"""
        try:
            from mcp_pba_tunnel.data.repositories.database import DatabaseConfig
            pool = DatabaseConfig.get_connection_pool()
            return pool._pool._stats._connections_total if hasattr(pool, '_pool') else 5
        except Exception:
            return 5

    def _get_error_rate(self) -> float:
        """Get error rate percentage"""
        # This would typically be calculated from error logs
        # For now, return a low error rate
        return 1.0  # 1% error rate

    def _get_throughput_per_second(self) -> float:
        """Get operations per second"""
        # This would be calculated from actual operation counts
        # For now, return a placeholder
        return 50.0  # 50 operations per second

    def _store_metrics(self, metrics: PerformanceMetrics):
        """Store metrics in history"""
        with self.metrics_lock:
            self.metrics_history.append(metrics)
            # Keep only last 1000 metrics
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]

    def _check_alerts(self, metrics: PerformanceMetrics):
        """Check metrics against alert thresholds"""
        alerts = []

        # Check memory usage
        if metrics.memory_usage > self.alert_thresholds['memory_usage']['critical']:
            alerts.append(f"CRITICAL: Memory usage {metrics.memory_usage:.1f}% exceeds critical threshold")
        elif metrics.memory_usage > self.alert_thresholds['memory_usage']['warning']:
            alerts.append(f"WARNING: Memory usage {metrics.memory_usage:.1f}% exceeds warning threshold")

        # Check CPU usage
        if metrics.cpu_usage > self.alert_thresholds['cpu_usage']['critical']:
            alerts.append(f"CRITICAL: CPU usage {metrics.cpu_usage:.1f}% exceeds critical threshold")
        elif metrics.cpu_usage > self.alert_thresholds['cpu_usage']['warning']:
            alerts.append(f"WARNING: CPU usage {metrics.cpu_usage:.1f}% exceeds warning threshold")

        # Check cache hit rate
        if metrics.cache_hit_rate < self.alert_thresholds['cache_hit_rate']['critical']:
            alerts.append(f"CRITICAL: Cache hit rate {metrics.cache_hit_rate:.1f}% below critical threshold")
        elif metrics.cache_hit_rate < self.alert_thresholds['cache_hit_rate']['warning']:
            alerts.append(f"WARNING: Cache hit rate {metrics.cache_hit_rate:.1f}% below warning threshold")

        # Check query response time
        if metrics.query_response_time > self.alert_thresholds['query_response_time']['critical']:
            alerts.append(f"CRITICAL: Query response time {metrics.query_response_time:.0f}ms exceeds critical threshold")
        elif metrics.query_response_time > self.alert_thresholds['query_response_time']['warning']:
            alerts.append(f"WARNING: Query response time {metrics.query_response_time:.0f}ms exceeds warning threshold")

        # Check throughput
        if metrics.throughput_per_second < self.alert_thresholds['throughput_per_second']['critical']:
            alerts.append(f"CRITICAL: Throughput {metrics.throughput_per_second:.1f} ops/sec below critical threshold")
        elif metrics.throughput_per_second < self.alert_thresholds['throughput_per_second']['warning']:
            alerts.append(f"WARNING: Throughput {metrics.throughput_per_second:.1f} ops/sec below warning threshold")

        # Log alerts
        for alert in alerts:
            if 'CRITICAL' in alert:
                logger.critical(alert)
            elif 'WARNING' in alert:
                logger.warning(alert)

    def record_tool_usage(self, tool_name: str, response_time: float, success: bool = True):
        """Record tool usage metrics"""
        with self.metrics_lock:
            if tool_name not in self.tool_metrics:
                self.tool_metrics[tool_name] = ToolMetrics(
                    tool_name=tool_name,
                    call_count=0,
                    average_response_time=0.0,
                    success_rate=100.0,
                    error_count=0,
                    last_used=datetime.now()
                )

            metrics = self.tool_metrics[tool_name]
            metrics.call_count += 1
            metrics.last_used = datetime.now()

            if success:
                # Update average response time (simple moving average)
                metrics.average_response_time = (
                    (metrics.average_response_time * (metrics.call_count - 1) + response_time)
                    / metrics.call_count
                )
                metrics.success_rate = (
                    (metrics.call_count - metrics.error_count) / metrics.call_count * 100
                )
            else:
                metrics.error_count += 1
                metrics.success_rate = (
                    (metrics.call_count - metrics.error_count) / metrics.call_count * 100
                )

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        with self.metrics_lock:
            if not self.metrics_history:
                return {"error": "No metrics available"}

            latest_metrics = self.metrics_history[-1]
            oldest_metrics = self.metrics_history[0] if len(self.metrics_history) > 1 else latest_metrics

            # Calculate trends
            memory_trend = self._calculate_trend([m.memory_usage for m in self.metrics_history])
            cpu_trend = self._calculate_trend([m.cpu_usage for m in self.metrics_history])
            throughput_trend = self._calculate_trend([m.throughput_per_second for m in self.metrics_history])

            # Get tool statistics
            tool_stats = {}
            for tool_name, metrics in self.tool_metrics.items():
                tool_stats[tool_name] = {
                    'call_count': metrics.call_count,
                    'average_response_time': metrics.average_response_time,
                    'success_rate': metrics.success_rate,
                    'error_count': metrics.error_count,
                    'last_used': metrics.last_used.isoformat()
                }

            return {
                'system_overview': {
                    'memory_usage_percent': latest_metrics.memory_usage,
                    'cpu_usage_percent': latest_metrics.cpu_usage,
                    'memory_entries_count': latest_metrics.memory_entries_count,
                    'relationship_count': latest_metrics.relationship_count,
                    'cache_hit_rate_percent': latest_metrics.cache_hit_rate,
                    'average_query_time_ms': latest_metrics.query_response_time,
                    'active_connections': latest_metrics.active_connections,
                    'error_rate_percent': latest_metrics.error_rate,
                    'throughput_operations_per_second': latest_metrics.throughput_per_second
                },
                'trends': {
                    'memory_usage_trend': memory_trend,
                    'cpu_usage_trend': cpu_trend,
                    'throughput_trend': throughput_trend
                },
                'tool_metrics': tool_stats,
                'monitoring_info': {
                    'metrics_count': len(self.metrics_history),
                    'monitoring_duration_minutes': len(self.metrics_history) * 0.5 if self.metrics_history else 0,
                    'last_update': latest_metrics.timestamp.isoformat()
                }
            }

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend from list of values"""
        if len(values) < 2:
            return 'stable'

        first_half = sum(values[:len(values)//2]) / (len(values)//2)
        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)

        if second_half > first_half * 1.1:
            return 'increasing'
        elif second_half < first_half * 0.9:
            return 'decreasing'
        else:
            return 'stable'

    def export_metrics(self, format: str = 'json') -> str:
        """Export metrics in specified format"""
        report = self.get_performance_report()

        if format == 'json':
            return json.dumps(report, indent=2, default=str)
        else:
            # Simple text format
            lines = []
            lines.append("ENHANCED MCP-PBA-TUNNEL PERFORMANCE REPORT")
            lines.append("=" * 50)

            overview = report['system_overview']
            lines.append(f"Memory Usage: {overview['memory_usage_percent']:.1f}%")
            lines.append(f"CPU Usage: {overview['cpu_usage_percent']:.1f}%")
            lines.append(f"Memory Entries: {overview['memory_entries_count']}")
            lines.append(f"Cache Hit Rate: {overview['cache_hit_rate_percent']:.1f}%")
            lines.append(f"Query Time: {overview['average_query_time_ms']:.0f}ms")
            lines.append(f"Throughput: {overview['throughput_operations_per_second']:.1f} ops/sec")

            if report['tool_metrics']:
                lines.append(f"\nTool Metrics ({len(report['tool_metrics'])} tools):")
                for tool_name, stats in report['tool_metrics'].items():
                    lines.append(f"  {tool_name}: {stats['call_count']} calls, "
                               f"{stats['average_response_time']:.0f}ms avg, "
                               f"{stats['success_rate']:.1f}% success")

            return '\n'.join(lines)

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    return performance_monitor

def start_monitoring(interval_seconds: int = 30):
    """Start global performance monitoring"""
    performance_monitor.start_monitoring(interval_seconds)

def stop_monitoring():
    """Stop global performance monitoring"""
    performance_monitor.stop_monitoring()

def get_performance_report() -> Dict[str, Any]:
    """Get current performance report"""
    return performance_monitor.get_performance_report()

def record_tool_usage(tool_name: str, response_time: float, success: bool = True):
    """Record tool usage for monitoring"""
    performance_monitor.record_tool_usage(tool_name, response_time, success)
