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
    Exposes /metrics endpoint automatically
    """
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
