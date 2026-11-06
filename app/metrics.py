from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "path", "status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency", ["method", "path"])


def metrics_response() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
