import time

from fastapi import Request, Response
from prometheus_client import Counter, Histogram, generate_latest

# 🔹 Metrikler
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Request latency in seconds",
    ["endpoint"]
)


def setup_metrics(app):
    """
    Uygulamaya Prometheus metrics middleware ve /metrics endpoint ekler
    """

    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
        REQUEST_LATENCY.labels(endpoint=request.url.path).observe(process_time)

        return response

    @app.get("/metrics")
    def metrics():
        return Response(generate_latest(), media_type="text/plain")
