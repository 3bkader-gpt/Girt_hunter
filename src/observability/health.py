"""Health check HTTP endpoint."""
import json
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

# Global health state
_health_state: dict[str, Any] = {
    "status": "starting",
    "last_check": None,
    "telegram_connected": False,
    "database_connected": False,
    "uptime_seconds": 0,
    "version": "2.0.0",
}
_start_time = datetime.utcnow()


def set_health_status(
    status: str = "healthy",
    telegram_connected: bool | None = None,
    database_connected: bool | None = None,
    last_check: datetime | None = None,
) -> None:
    """Update the health status.
    
    Args:
        status: Overall status (healthy, unhealthy, degraded)
        telegram_connected: Whether Telegram is connected
        database_connected: Whether database is accessible
        last_check: Timestamp of last successful check
    """
    _health_state["status"] = status
    
    if telegram_connected is not None:
        _health_state["telegram_connected"] = telegram_connected
    
    if database_connected is not None:
        _health_state["database_connected"] = database_connected
    
    if last_check is not None:
        _health_state["last_check"] = last_check.isoformat()
    
    # Calculate uptime
    _health_state["uptime_seconds"] = (datetime.utcnow() - _start_time).total_seconds()


def get_health_status() -> dict[str, Any]:
    """Get current health status."""
    _health_state["uptime_seconds"] = (datetime.utcnow() - _start_time).total_seconds()
    return _health_state.copy()


class HealthHandler(BaseHTTPRequestHandler):
    """HTTP handler for health check requests."""
    
    def do_GET(self) -> None:
        """Handle GET requests."""
        if self.path == "/health":
            self._handle_health()
        elif self.path == "/health/live":
            self._handle_liveness()
        elif self.path == "/health/ready":
            self._handle_readiness()
        else:
            self.send_error(404, "Not Found")
    
    def _handle_health(self) -> None:
        """Full health status endpoint."""
        health = get_health_status()
        status_code = 200 if health["status"] == "healthy" else 503
        
        self._send_json(status_code, health)
    
    def _handle_liveness(self) -> None:
        """Kubernetes liveness probe - is the process alive?"""
        self._send_json(200, {"alive": True})
    
    def _handle_readiness(self) -> None:
        """Kubernetes readiness probe - is the service ready to accept traffic?"""
        health = get_health_status()
        is_ready = (
            health["status"] == "healthy"
            and health["telegram_connected"]
            and health["database_connected"]
        )
        
        status_code = 200 if is_ready else 503
        self._send_json(status_code, {"ready": is_ready})
    
    def _send_json(self, status_code: int, data: dict[str, Any]) -> None:
        """Send a JSON response."""
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def log_message(self, format: str, *args: Any) -> None:
        """Suppress default logging to avoid noise."""
        pass


def start_health_server(port: int = 8080) -> threading.Thread:
    """Start the health check HTTP server in a background thread.
    
    Args:
        port: Port to listen on (default: 8080)
        
    Returns:
        The daemon thread running the server
    """
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    
    thread = threading.Thread(
        target=server.serve_forever,
        name="health-server",
        daemon=True,
    )
    thread.start()
    
    return thread
