# Performance Monitoring Guide

## Overview

The Enhanced MCP-PBA-TUNNEL includes comprehensive performance monitoring capabilities to ensure optimal system operation and provide real-time insights into system health and performance metrics.

## Features

### Real-time Metrics Collection

- **System Metrics**: CPU usage, memory consumption, disk I/O
- **Application Metrics**: Memory entries count, relationship count, cache hit rates
- **Performance Metrics**: Query response times, throughput, error rates
- **Tool Metrics**: Individual tool usage statistics and response times

### Alert System

- **Configurable Thresholds**: Set custom warning and critical levels
- **Automatic Alerts**: Real-time notifications for performance issues
- **Multiple Alert Levels**: Warning, critical, and informational alerts

### Web Dashboard

- **Real-time Dashboard**: Live monitoring interface at `http://localhost:8080`
- **Interactive Charts**: Visual representation of metrics over time
- **Multiple Views**: Overview, tools, and detailed performance tabs
- **Auto-refresh**: Updates every 30 seconds automatically

## Quick Start

### 1. Start Performance Monitoring

```python
from mcp_pba_tunnel.core.performance_monitor import start_monitoring

# Start background monitoring with 30-second intervals
start_monitoring(interval_seconds=30)
```

### 2. Start Monitoring Dashboard

```python
from mcp_pba_tunnel.core.monitoring_dashboard import start_dashboard

# Start web dashboard on port 8080
start_dashboard(host="0.0.0.0", port=8080)
```

### 3. View Dashboard

Open your browser and navigate to:

```
http://localhost:8080
```

### 4. Access Programmatic Metrics

```python
from mcp_pba_tunnel.core.performance_monitor import get_performance_report

# Get comprehensive performance report
report = get_performance_report()
print(f"Memory Usage: {report['system_overview']['memory_usage_percent']:.1f}%")
print(f"Cache Hit Rate: {report['system_overview']['cache_hit_rate_percent']:.1f}%")
```

## Dashboard Interface

### Overview Tab

- **Memory Usage**: Current system memory utilization
- **CPU Usage**: Current CPU utilization percentage
- **Cache Hit Rate**: Effectiveness of caching system
- **Memory Entries**: Total number of stored memory entries
- **Query Time**: Average response time for database queries
- **Throughput**: Operations per second

### Tools Tab

- **Tool Usage Statistics**: Individual tool performance metrics
- **Call Counts**: Number of times each tool has been used
- **Response Times**: Average response time per tool
- **Success Rates**: Success rate for each tool
- **Last Used**: When each tool was last accessed

### Performance Tab

- **Detailed JSON Report**: Complete system performance data
- **Trend Analysis**: Performance trends over time
- **Raw Metrics**: Unprocessed performance data

## Configuration

### Alert Thresholds

Configure performance thresholds in your monitoring setup:

```python
from mcp_pba_tunnel.core.performance_monitor import get_performance_monitor

monitor = get_performance_monitor()
monitor.alert_thresholds = {
    'memory_usage': {'warning': 80.0, 'critical': 90.0},
    'cpu_usage': {'warning': 70.0, 'critical': 85.0},
    'cache_hit_rate': {'warning': 50.0, 'critical': 30.0},
    'query_response_time': {'warning': 500.0, 'critical': 2000.0}
}
```

### Monitoring Intervals

Adjust monitoring frequency based on your needs:

```python
# More frequent monitoring (higher resource usage)
start_monitoring(interval_seconds=10)

# Less frequent monitoring (lower resource usage)
start_monitoring(interval_seconds=60)
```

## API Endpoints

### Get Metrics

```http
GET /api/metrics?format=json
```

**Response:**

```json
{
  "system_overview": {
    "memory_usage_percent": 45.2,
    "cpu_usage_percent": 23.1,
    "memory_entries_count": 1250,
    "cache_hit_rate_percent": 87.3,
    "average_query_time_ms": 45,
    "throughput_operations_per_second": 67.8
  },
  "tool_metrics": {
    "enhanced_memory": {
      "call_count": 45,
      "average_response_time": 23.5,
      "success_rate": 100.0
    }
  },
  "monitoring_info": {
    "metrics_count": 150,
    "monitoring_duration_minutes": 75.0
  }
}
```

### Get Health Status

```http
GET /api/health
```

**Response:**

```json
{
  "status": "healthy",
  "issues": [],
  "metrics_summary": {
    "memory_usage": "45.2%",
    "cpu_usage": "23.1%",
    "cache_hit_rate": "87.3%",
    "error_rate": "0.1%"
  }
}
```

### Get Tool Statistics

```http
GET /api/tools
```

**Response:**

```json
{
  "enhanced_memory": {
    "call_count": 45,
    "average_response_time": 23.5,
    "success_rate": 100.0,
    "error_count": 0,
    "last_used": "2024-01-15T14:30:22"
  },
  "code_analysis": {
    "call_count": 12,
    "average_response_time": 156.7,
    "success_rate": 91.7,
    "error_count": 1,
    "last_used": "2024-01-15T14:28:15"
  }
}
```

## Monitoring Tools Integration

### Record Tool Usage

```python
from mcp_pba_tunnel.core.performance_monitor import record_tool_usage

# Record successful tool usage
record_tool_usage("enhanced_memory", response_time=45.2, success=True)

# Record failed tool usage
record_tool_usage("code_analysis", response_time=1200.0, success=False)
```

### Custom Metrics

```python
from mcp_pba_tunnel.core.performance_monitor import get_performance_monitor

monitor = get_performance_monitor()

# Add custom metric tracking
class CustomMetrics:
    def track_custom_metric(self, name: str, value: float):
        # Store custom metrics for your specific use case
        pass

custom_metrics = CustomMetrics()
```

## Performance Optimization Tips

### Based on Monitoring Data

1. **High Memory Usage**
   - Check for memory leaks in long-running processes
   - Increase system memory if consistently above 80%
   - Review memory cleanup intervals

2. **Low Cache Hit Rate**
   - Review cache TTL settings
   - Increase cache size if memory allows
   - Check query patterns for optimization opportunities

3. **High Query Response Times**
   - Review database indexes
   - Check for slow queries in logs
   - Consider query optimization

4. **Low Throughput**
   - Check for system resource constraints
   - Review concurrent connection limits
   - Optimize database connection pooling

## Troubleshooting

### Dashboard Not Loading

1. Check if dashboard is running: `http://localhost:8080`
2. Verify Python process is active
3. Check firewall settings
4. Ensure port 8080 is not in use

### No Metrics Available

1. Verify monitoring is started: `start_monitoring()`
2. Check database connectivity
3. Review error logs
4. Ensure proper permissions

### High Resource Usage

1. Increase monitoring interval: `start_monitoring(interval_seconds=60)`
2. Reduce metrics history retention
3. Check for memory leaks in monitoring code

### Alerts Not Working

1. Verify alert thresholds configuration
2. Check logging configuration
3. Review alert conditions
4. Test with known threshold violations

## Integration with External Systems

### Export to Monitoring Systems

```python
import json
from mcp_pba_tunnel.core.performance_monitor import get_performance_report

# Export metrics for external monitoring
def export_to_external_system():
    report = get_performance_report()

    # Send to your monitoring system (Grafana, Prometheus, etc.)
    # Example: Send to HTTP endpoint
    import requests
    requests.post('https://your-monitoring-endpoint.com/metrics', json=report)

    # Or save to file
    with open('performance_report.json', 'w') as f:
        json.dump(report, f, indent=2)
```

### Custom Alert Handlers

```python
from mcp_pba_tunnel.core.performance_monitor import get_performance_monitor

monitor = get_performance_monitor()

class CustomAlertHandler:
    def __init__(self):
        self.alert_history = []

    def handle_alert(self, alert_message: str, severity: str):
        self.alert_history.append({
            'message': alert_message,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        })

        # Send to external alerting system
        if severity == 'critical':
            self.send_critical_alert(alert_message)
        elif severity == 'warning':
            self.send_warning_alert(alert_message)

    def send_critical_alert(self, message: str):
        # Send critical alert to pager/SMS
        pass

    def send_warning_alert(self, message: str):
        # Send warning to dashboard/email
        pass

# Configure custom alert handler
alert_handler = CustomAlertHandler()
# monitor.set_alert_handler(alert_handler)  # If this method exists
```

## Best Practices

### Monitoring Setup

1. **Start Early**: Begin monitoring during development
2. **Set Appropriate Thresholds**: Configure based on your system capacity
3. **Monitor Key Metrics**: Focus on most important performance indicators
4. **Regular Review**: Review metrics and adjust thresholds as needed

### Performance Optimization

1. **Use Metrics for Guidance**: Let monitoring data drive optimization efforts
2. **Set Baselines**: Establish normal performance ranges
3. **Track Changes**: Monitor impact of code changes
4. **Alert Responsibly**: Set meaningful thresholds to avoid alert fatigue

### Resource Management

1. **Balance Frequency**: Choose appropriate monitoring intervals
2. **Manage History**: Configure appropriate metric retention
3. **System Resources**: Ensure monitoring doesn't impact system performance
4. **Storage Planning**: Consider storage requirements for metrics

This comprehensive monitoring system provides the visibility and control needed to maintain optimal performance of your Enhanced MCP-PBA-TUNNEL system in production environments.
