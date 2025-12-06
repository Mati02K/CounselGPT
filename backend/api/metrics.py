import time
from prometheus_client import Counter, Histogram, Gauge
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# ----------------- METRICS DEFINITIONS -----------------

# HTTP Request Metrics
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "handler", "status"]
)

HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request latencies in seconds",
    ["method", "handler"],
    buckets=(1, 2, 5, 10, 15, 20, 30, 45, 60, 90, 120, 180, 240, 300, 360, 420, 480, 540, 600)  # Up to 10 min
)

HTTP_REQUESTS_INPROGRESS = Gauge(
    "http_requests_inprogress",
    "HTTP requests in progress",
    
    ["method", "handler"]
)

# Inference Metrics
INFERENCE_TIME = Histogram(
    "inference_duration_seconds",
    "Time spent generating model responses",
    buckets=(1, 2, 5, 10, 15, 20, 30, 45, 60, 90, 120, 180, 240, 300, 360, 420, 480, 540, 600)  # Up to 10 min
)

TOKENS_GENERATED = Counter(
    "tokens_generated_total",
    "Total number of tokens generated"
)

CACHE_HITS = Counter(
    "cache_hits_total",
    "Total number of cache hits"
)

CACHE_MISSES = Counter(
    "cache_misses_total",
    "Total number of cache misses"
)

# ----------------- MIDDLEWARE -----------------

class PrometheusMiddleware(BaseHTTPMiddleware):
    """Manual Prometheus middleware to track HTTP requests"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip metrics and health endpoints (health checks create noise)
        if request.url.path in ["/metrics", "/health"]:
            return await call_next(request)
        
        method = request.method
        handler = request.url.path
        
        # Track in-progress requests
        HTTP_REQUESTS_INPROGRESS.labels(method=method, handler=handler).inc()
        
        # Track request duration
        start_time = time.time()
        
        try:
            response = await call_next(request)
            status = response.status_code
        except Exception as e:
            status = 500
            raise
        finally:
            # Record metrics
            duration = time.time() - start_time
            HTTP_REQUEST_DURATION.labels(method=method, handler=handler).observe(duration)
            HTTP_REQUESTS_TOTAL.labels(method=method, handler=handler, status=status).inc()
            HTTP_REQUESTS_INPROGRESS.labels(method=method, handler=handler).dec()
        
        return response

# ----------------- FASTAPI HOOK -----------------

def add_metrics_middleware(app):
    """
    Add manual Prometheus middleware to track HTTP requests
    """
    from logging import getLogger
    logger = getLogger("metrics")
    
    logger.info("Initializing Prometheus metrics middleware...")
    
    # Add our custom middleware
    app.add_middleware(PrometheusMiddleware)
    
    logger.info("Prometheus metrics middleware installed")
