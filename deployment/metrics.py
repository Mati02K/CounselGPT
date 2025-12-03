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
    from logging import getLogger
    logger = getLogger("metrics")
    
    logger.info("Initializing Prometheus metrics instrumentation...")
    
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
    
    # Instrument the app (collects metrics)
    # This also automatically adds http_request_duration_seconds histogram
    instrumentator.instrument(app)
    
    # Manually expose /metrics endpoint to ensure it's registered correctly
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from starlette.responses import Response

    @app.get("/metrics", include_in_schema=True)
    def metrics_endpoint():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
    
    logger.info("Prometheus metrics initialized and exposed at /metrics (manual route)")
