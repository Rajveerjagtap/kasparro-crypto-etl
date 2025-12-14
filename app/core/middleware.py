"""Structured JSON logging middleware for request/response observability."""

import json
import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class StructuredLogger(logging.Logger):
    """Custom logger that outputs structured JSON logs."""

    def _log_json(self, level: str, message: str, **extra) -> None:
        """Log a structured JSON message."""
        log_entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()),
            "level": level,
            "message": message,
            **extra,
        }
        # Use parent's method to actually log
        super().info(json.dumps(log_entry))

    def info_json(self, message: str, **extra) -> None:
        """Log INFO level JSON."""
        self._log_json("INFO", message, **extra)

    def error_json(self, message: str, **extra) -> None:
        """Log ERROR level JSON."""
        self._log_json("ERROR", message, **extra)


# Configure structured logger
def get_structured_logger(name: str = "kasparro.request") -> StructuredLogger:
    """Create and configure a structured JSON logger."""
    logging.setLoggerClass(StructuredLogger)
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False

    return logger  # type: ignore


request_logger = get_structured_logger()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs structured JSON for every HTTP request.

    Logs include:
    - timestamp: ISO format timestamp
    - level: INFO or ERROR
    - path: Request path
    - method: HTTP method
    - status_code: Response status code
    - process_time_ms: Request processing time in milliseconds
    - request_id: UUID for request tracing (generated if not provided)
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Intercept request, time it, and log structured JSON."""
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())

        # Store request_id in request state for downstream use
        request.state.request_id = request_id

        # Record start time
        start_time = time.perf_counter()

        # Process request
        response: Response
        status_code: int
        level: str = "INFO"
        error_detail: str | None = None

        try:
            response = await call_next(request)
            status_code = response.status_code

            if status_code >= 500:
                level = "ERROR"
            elif status_code >= 400:
                level = "WARN"
        except Exception as e:
            # Log exception and re-raise
            status_code = 500
            level = "ERROR"
            error_detail = str(e)
            raise
        finally:
            # Calculate processing time
            process_time_ms = (time.perf_counter() - start_time) * 1000

            # Build log entry
            log_data = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime()),
                "level": level,
                "path": request.url.path,
                "method": request.method,
                "status_code": status_code,
                "process_time_ms": round(process_time_ms, 2),
                "request_id": request_id,
            }

            # Add query params if present
            if request.url.query:
                log_data["query"] = request.url.query

            # Add error detail if present
            if error_detail:
                log_data["error"] = error_detail

            # Log to stdout as JSON
            print(json.dumps(log_data), flush=True)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response


# ============== Metrics Collection ==============


class MetricsCollector:
    """
    Simple in-memory metrics collector for Prometheus-style output.

    Tracks:
    - http_requests_total: Counter by method/status
    - etl_runs_total: Counter by source/status
    - etl_last_duration_seconds: Gauge by source
    """

    def __init__(self):
        self._http_requests: dict[tuple[str, int], int] = {}
        self._etl_runs: dict[tuple[str, str], int] = {}
        self._etl_last_duration: dict[str, float] = {}

    def increment_http_request(self, method: str, status_code: int) -> None:
        """Increment HTTP request counter."""
        key = (method, status_code)
        self._http_requests[key] = self._http_requests.get(key, 0) + 1

    def increment_etl_run(self, source: str, status: str) -> None:
        """Increment ETL run counter."""
        key = (source, status)
        self._etl_runs[key] = self._etl_runs.get(key, 0) + 1

    def set_etl_duration(self, source: str, duration_seconds: float) -> None:
        """Set last ETL duration for a source."""
        self._etl_last_duration[source] = duration_seconds

    def get_prometheus_output(self) -> str:
        """Generate Prometheus-compatible metrics output."""
        lines = []

        # HTTP requests total
        lines.append("# HELP http_requests_total Total number of HTTP requests")
        lines.append("# TYPE http_requests_total counter")
        for (method, status), count in sorted(self._http_requests.items()):
            lines.append(
                f'http_requests_total{{method="{method}",status="{status}"}} {count}'
            )

        lines.append("")

        # ETL runs total
        lines.append("# HELP etl_runs_total Total number of ETL runs")
        lines.append("# TYPE etl_runs_total counter")
        for (source, status), count in sorted(self._etl_runs.items()):
            lines.append(
                f'etl_runs_total{{source="{source}",status="{status}"}} {count}'
            )

        lines.append("")

        # ETL last duration
        lines.append("# HELP etl_last_duration_seconds Duration of last ETL run in seconds")
        lines.append("# TYPE etl_last_duration_seconds gauge")
        for source, duration in sorted(self._etl_last_duration.items()):
            lines.append(
                f'etl_last_duration_seconds{{source="{source}"}} {duration:.3f}'
            )

        return "\n".join(lines)


# Global metrics collector instance
metrics_collector = MetricsCollector()


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware that collects HTTP request metrics."""

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Track HTTP request metrics."""
        response = await call_next(request)

        # Don't track metrics endpoint itself to avoid noise
        if request.url.path != "/metrics":
            metrics_collector.increment_http_request(
                request.method, response.status_code
            )

        return response
