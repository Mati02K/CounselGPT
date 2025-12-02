from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator

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
    Exposes /metrics endpoint with http_requests_total counter
    """
    instrumentator = Instrumentator(
        should_group_status_codes=False,  # Keep exact status codes (200, 404, 500, etc.)
        should_ignore_untemplated=False,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=[],
        inprogress_name="http_requests_inprogress",
        inprogress_labels=True,
    )
    
    # Add request counter with status codes
    instrumentator.add(
        instrumentator.metrics.requests(
            metric_name="http_requests",  # Will create http_requests_total
            metric_doc="Total HTTP requests",
            metric_namespace="",
            metric_subsystem="",
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
        )
    )
    
    # Add latency histogram
    instrumentator.add(
        instrumentator.metrics.latency(
            metric_name="http_request_duration_seconds",
            metric_doc="HTTP request latency",
            metric_namespace="",
            metric_subsystem="",
            should_include_handler=True,
            should_include_method=True,
            should_include_status=True,
        )
    )
    
    instrumentator.instrument(app).expose(app, endpoint="/metrics")
