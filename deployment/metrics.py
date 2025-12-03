from prometheus_client import Counter, Histogram, Info
from prometheus_fastapi_instrumentator import Instrumentator, metrics

# ----------------- METRICS DEFINITIONS -----------------

INFERENCE_TIME = Histogram(
    "inference_duration_seconds",
    "Time spent generating model responses"
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

# ----------------- FASTAPI HOOK -----------------

def add_metrics_middleware(app):
    """
    Attach Prometheus Instrumentator to FastAPI
    Exposes /metrics endpoint with http_requests_total and http_request_duration_seconds
    """
    instrumentator = Instrumentator(
        should_group_status_codes=False,  # Keep exact status codes (200, 404, 500, etc.)
        should_ignore_untemplated=False,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics"],  # Don't track metrics endpoint itself
        inprogress_name="http_requests_inprogress",
        inprogress_labels=True,
    )
    
    # Add custom metric: http_requests_total with status codes
    # This creates a Counter that tracks all requests by method, path, and status
    def http_requests_total() -> callable:
        METRIC = Counter(
            "http_requests_total",
            "Total HTTP requests",
            labelnames=["method", "handler", "status"]
        )
        
        def instrumentation(info: metrics.Info) -> None:
            METRIC.labels(
                method=info.method,
                handler=info.modified_handler,
                status=info.modified_status
            ).inc()
        
        return instrumentation
    
    # Add the custom metric
    instrumentator.add(http_requests_total())
    
    # Instrument the app and expose /metrics endpoint
    # This also automatically adds http_request_duration_seconds histogram
    instrumentator.instrument(app)
    instrumentator.expose(app, endpoint="/metrics", include_in_schema=False)
