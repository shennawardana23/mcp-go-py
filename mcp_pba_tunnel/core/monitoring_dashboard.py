import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import threading
from mcp_pba_tunnel.core.performance_monitor import get_performance_monitor, start_monitoring, get_performance_report

logger = logging.getLogger(__name__)

class MonitoringDashboard:
    """Web-based monitoring dashboard for enhanced MCP-PBA-TUNNEL"""

    def __init__(self):
        self.dashboard_active = False
        self.dashboard_thread: Optional[threading.Thread] = None
        self.update_interval = 10  # seconds

    def start_dashboard(self, host: str = "0.0.0.0", port: int = 8080):
        """Start the monitoring dashboard server"""
        if self.dashboard_active:
            logger.warning("Monitoring dashboard already active")
            return

        self.dashboard_active = True
        self.dashboard_thread = threading.Thread(
            target=self._dashboard_server,
            args=(host, port)
        )
        self.dashboard_thread.daemon = True
        self.dashboard_thread.start()
        logger.info(f"Started monitoring dashboard on {host}:{port}")

    def stop_dashboard(self):
        """Stop the monitoring dashboard server"""
        self.dashboard_active = False
        if self.dashboard_thread and self.dashboard_thread.is_alive():
            self.dashboard_thread.join(timeout=5.0)
        logger.info("Stopped monitoring dashboard")

    def _dashboard_server(self, host: str, port: int):
        """Simple HTTP server for the dashboard"""
        import http.server
        import socketserver
        from urllib.parse import urlparse, parse_qs

        class DashboardHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                """Handle GET requests"""
                parsed_url = urlparse(self.path)
                path = parsed_url.path
                query_params = parse_qs(parsed_url.query)

                try:
                    if path == '/':
                        self._serve_dashboard()
                    elif path == '/api/metrics':
                        self._serve_metrics(query_params)
                    elif path == '/api/health':
                        self._serve_health()
                    elif path == '/api/tools':
                        self._serve_tools()
                    else:
                        self._serve_not_found()
                except Exception as e:
                    self._serve_error(str(e))

            def _serve_dashboard(self):
                """Serve the main dashboard page"""
                html = self._generate_dashboard_html()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(html.encode())

            def _serve_metrics(self, query_params):
                """Serve performance metrics"""
                format_type = query_params.get('format', ['json'])[0]

                try:
                    report = get_performance_report()

                    self.send_response(200)
                    if format_type == 'json':
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(report, indent=2, default=str).encode())
                    else:
                        self.send_header('Content-type', 'text/plain')
                        self.end_headers()
                        text_report = self._generate_text_report(report)
                        self.wfile.write(text_report.encode())

                except Exception as e:
                    self._serve_error(f"Failed to get metrics: {e}")

            def _serve_health(self):
                """Serve system health status"""
                try:
                    health_status = self._get_health_status()

                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(health_status, indent=2).encode())

                except Exception as e:
                    self._serve_error(f"Failed to get health status: {e}")

            def _serve_tools(self):
                """Serve tool usage statistics"""
                try:
                    report = get_performance_report()
                    tools_data = report.get('tool_metrics', {})

                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(tools_data, indent=2).encode())

                except Exception as e:
                    self._serve_error(f"Failed to get tool statistics: {e}")

            def _serve_not_found(self):
                """Serve 404 response"""
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Not Found')

            def _serve_error(self, message: str):
                """Serve error response"""
                error_response = {
                    'error': 'Dashboard Error',
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                }

                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(error_response, indent=2).encode())

            def _generate_dashboard_html(self) -> str:
                """Generate HTML dashboard"""
                return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced MCP-PBA-TUNNEL Dashboard</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            color: #333;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #007bff;
        }}
        .metric-title {{
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
        .status-good {{ color: #28a745; }}
        .status-warning {{ color: #ffc107; }}
        .status-critical {{ color: #dc3545; }}
        .refresh-btn {{
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            margin: 10px;
        }}
        .tabs {{
            display: flex;
            margin-bottom: 20px;
        }}
        .tab {{
            padding: 10px 20px;
            background: #e9ecef;
            border: none;
            cursor: pointer;
            border-radius: 4px 4px 0 0;
        }}
        .tab.active {{
            background: #007bff;
            color: white;
        }}
        .tab-content {{
            display: none;
        }}
        .tab-content.active {{
            display: block;
        }}
        .tools-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .tools-table th, .tools-table td {{
            padding: 8px 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .tools-table th {{
            background-color: #f8f9fa;
        }}
        .alerts {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }}
        .alerts h3 {{
            margin-top: 0;
            color: #856404;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Enhanced MCP-PBA-TUNNEL Dashboard</h1>
            <p>Real-time performance monitoring and system metrics</p>
            <button class="refresh-btn" onclick="refreshDashboard()">🔄 Refresh</button>
        </div>

        <div id="alerts" class="alerts" style="display: none;">
            <h3>⚠️ Alerts</h3>
            <div id="alerts-content"></div>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="showTab('overview')">Overview</button>
            <button class="tab" onclick="showTab('tools')">Tools</button>
            <button class="tab" onclick="showTab('performance')">Performance</button>
        </div>

        <div id="overview" class="tab-content active">
            <div class="metrics-grid" id="metrics-grid">
                <div class="metric-card">
                    <div class="metric-title">Memory Usage</div>
                    <div class="metric-value" id="memory-usage">--</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">CPU Usage</div>
                    <div class="metric-value" id="cpu-usage">--</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Cache Hit Rate</div>
                    <div class="metric-value" id="cache-rate">--</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Memory Entries</div>
                    <div class="metric-value" id="memory-entries">--</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Query Time</div>
                    <div class="metric-value" id="query-time">--</div>
                </div>
                <div class="metric-card">
                    <div class="metric-title">Throughput</div>
                    <div class="metric-value" id="throughput">--</div>
                </div>
            </div>
        </div>

        <div id="tools" class="tab-content">
            <table class="tools-table">
                <thead>
                    <tr>
                        <th>Tool Name</th>
                        <th>Calls</th>
                        <th>Avg Response (ms)</th>
                        <th>Success Rate</th>
                        <th>Last Used</th>
                    </tr>
                </thead>
                <tbody id="tools-table-body">
                    <tr><td colspan="5">Loading...</td></tr>
                </tbody>
            </table>
        </div>

        <div id="performance" class="tab-content">
            <div id="performance-details">
                <h3>Detailed Performance Metrics</h3>
                <pre id="performance-text">Loading detailed metrics...</pre>
            </div>
        </div>
    </div>

    <script>
        let currentTab = 'overview';

        function showTab(tabName) {{
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});

            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            document.querySelector(`[onclick="showTab('${{tabName}}')"]`).classList.add('active');

            currentTab = tabName;
            refreshDashboard();
        }}

        function refreshDashboard() {{
            fetch('/api/metrics')
                .then(response => response.json())
                .then(data => {{
                    updateMetrics(data);
                    updateTools(data.tool_metrics || {{}});
                    if (currentTab === 'performance') {{
                        updatePerformanceDetails(data);
                    }}
                }})
                .catch(error => {{
                    console.error('Error refreshing dashboard:', error);
                }});
        }}

        function updateMetrics(data) {{
            const overview = data.system_overview || {{}};

            document.getElementById('memory-usage').textContent = `{{overview.memory_usage_percent || 0}}%`;
            document.getElementById('cpu-usage').textContent = `{{overview.cpu_usage_percent || 0}}%`;
            document.getElementById('cache-rate').textContent = `{{overview.cache_hit_rate_percent || 0}}%`;
            document.getElementById('memory-entries').textContent = overview.memory_entries_count || 0;
            document.getElementById('query-time').textContent = `{{overview.average_query_time_ms || 0}}ms`;
            document.getElementById('throughput').textContent = `{{overview.throughput_operations_per_second || 0}} ops/sec`;

            // Update status colors
            updateMetricStatus('memory-usage', overview.memory_usage_percent || 0, 80, 90);
            updateMetricStatus('cpu-usage', overview.cpu_usage_percent || 0, 70, 85);
            updateMetricStatus('cache-rate', overview.cache_hit_rate_percent || 0, 50, 30, true);
        }}

        function updateMetricStatus(elementId, value, warningThreshold, criticalThreshold, invert = false) {{
            const element = document.getElementById(elementId);
            element.classList.remove('status-good', 'status-warning', 'status-critical');

            let status = 'good';
            if (invert) {{
                if (value < criticalThreshold) status = 'critical';
                else if (value < warningThreshold) status = 'warning';
            }} else {{
                if (value > criticalThreshold) status = 'critical';
                else if (value > warningThreshold) status = 'warning';
            }}

            element.classList.add(`status-{{status}}`);
        }}

        function updateTools(tools) {{
            const tbody = document.getElementById('tools-table-body');

            if (Object.keys(tools).length === 0) {{
                tbody.innerHTML = '<tr><td colspan="5">No tool metrics available</td></tr>';
                return;
            }}

            const rows = Object.entries(tools).map(([name, stats]) => `
                <tr>
                    <td>{{name}}</td>
                    <td>{{stats.call_count || 0}}</td>
                    <td>{{Math.round(stats.average_response_time || 0)}}</td>
                    <td>{{Math.round(stats.success_rate || 0)}}%</td>
                    <td>{{new Date(stats.last_used).toLocaleTimeString()}}</td>
                </tr>
            `).join('');

            tbody.innerHTML = rows;
        }}

        function updatePerformanceDetails(data) {{
            const element = document.getElementById('performance-text');
            element.textContent = JSON.stringify(data, null, 2);
        }}

        // Auto-refresh every 30 seconds
        setInterval(refreshDashboard, 30000);

        // Initial load
        refreshDashboard();
    </script>
</body>
</html>
'''

            def _get_health_status(self) -> Dict[str, Any]:
                """Get system health status"""
                try:
                    report = get_performance_report()

                    if 'error' in report:
                        return {
                            'status': 'error',
                            'message': report['error'],
                            'timestamp': datetime.now().isoformat()
                        }

                    overview = report['system_overview']

                    # Simple health check based on metrics
                    issues = []
                    if overview['memory_usage_percent'] > 90:
                        issues.append('High memory usage')
                    if overview['cpu_usage_percent'] > 85:
                        issues.append('High CPU usage')
                    if overview['cache_hit_rate_percent'] < 30:
                        issues.append('Low cache hit rate')
                    if overview['error_rate_percent'] > 10:
                        issues.append('High error rate')

                    status = 'healthy' if not issues else 'warning'

                    return {
                        'status': status,
                        'issues': issues,
                        'metrics_summary': {
                            'memory_usage': f"{overview['memory_usage_percent']".1f"}%",
                            'cpu_usage': f"{overview['cpu_usage_percent']".1f"}%",
                            'cache_hit_rate': f"{overview['cache_hit_rate_percent']".1f"}%",
                            'error_rate': f"{overview['error_rate_percent']".1f"}%"
                        },
                        'timestamp': datetime.now().isoformat()
                    }

                except Exception as e:
                    return {
                        'status': 'error',
                        'message': str(e),
                        'timestamp': datetime.now().isoformat()
                    }

            def _generate_text_report(self, report: Dict[str, Any]) -> str:
                """Generate text format performance report"""
                lines = []
                lines.append("ENHANCED MCP-PBA-TUNNEL PERFORMANCE REPORT")
                lines.append("=" * 50)

                overview = report.get('system_overview', {})
                lines.append(f"Memory Usage: {overview.get('memory_usage_percent', 0)".1f"}%")
                lines.append(f"CPU Usage: {overview.get('cpu_usage_percent', 0)".1f"}%")
                lines.append(f"Memory Entries: {overview.get('memory_entries_count', 0)}")
                lines.append(f"Cache Hit Rate: {overview.get('cache_hit_rate_percent', 0)".1f"}%")
                lines.append(f"Query Time: {overview.get('average_query_time_ms', 0)".0f"}ms")
                lines.append(f"Throughput: {overview.get('throughput_operations_per_second', 0)".1f"} ops/sec")

                tool_metrics = report.get('tool_metrics', {})
                if tool_metrics:
                    lines.append(f"\nTool Metrics ({len(tool_metrics)} tools):")
                    for tool_name, stats in tool_metrics.items():
                        lines.append(f"  {tool_name}: {stats.get('call_count', 0)} calls, "
                                   f"{stats.get('average_response_time', 0)".0f"}ms avg, "
                                   f"{stats.get('success_rate', 0)".1f"}% success")

                return '\n'.join(lines)

        # Start the HTTP server
        with socketserver.TCPServer((host, port), DashboardHandler) as httpd:
            logger.info(f"Dashboard server running on {host}:{port}")
            while self.dashboard_active:
                httpd.handle_request()

# Global dashboard instance
monitoring_dashboard = MonitoringDashboard()

def get_monitoring_dashboard() -> MonitoringDashboard:
    """Get global monitoring dashboard instance"""
    return monitoring_dashboard

def start_dashboard(host: str = "0.0.0.0", port: int = 8080):
    """Start global monitoring dashboard"""
    monitoring_dashboard.start_dashboard(host, port)

def stop_dashboard():
    """Stop global monitoring dashboard"""
    monitoring_dashboard.stop_dashboard()
