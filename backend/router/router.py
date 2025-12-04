"""
Production-grade adaptive router for CounselGPT
Routes requests to GPU (priority) with CPU fallback based on load
"""

import os
import time
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import httpx

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

# =====================================================
# Configuration
# =====================================================

GPU_URL = os.getenv("GPU_URL", "http://counselgpt-api-gpu:8000")
CPU_URL = os.getenv("CPU_URL", "http://counselgpt-api-cpu:8000")
GPU_MAX_INFLIGHT = int(os.getenv("GPU_MAX_INFLIGHT", "20"))
BACKEND_TIMEOUT = float(os.getenv("BACKEND_TIMEOUT", "60.0"))
HEALTH_CHECK_INTERVAL = int(os.getenv("HEALTH_CHECK_INTERVAL", "10"))
CIRCUIT_BREAKER_THRESHOLD = int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5"))
CIRCUIT_BREAKER_TIMEOUT = int(os.getenv("CIRCUIT_BREAKER_TIMEOUT", "30"))

# =====================================================
# Logging
# =====================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("router")

# =====================================================
# Prometheus Metrics
# =====================================================

# Request metrics
requests_total = Counter(
    'router_requests_total',
    'Total requests routed',
    ['backend', 'status']
)

requests_duration = Histogram(
    'router_request_duration_seconds',
    'Request duration',
    ['backend'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

gpu_queue_size = Gauge(
    'router_gpu_queue_size',
    'Current GPU queue size'
)

gpu_capacity = Gauge(
    'router_gpu_capacity',
    'GPU available capacity'
)

backend_health = Gauge(
    'router_backend_health',
    'Backend health status (1=healthy, 0=unhealthy)',
    ['backend']
)

circuit_breaker_state = Gauge(
    'router_circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=open, 2=half-open)',
    ['backend']
)

fallback_count = Counter(
    'router_fallback_total',
    'Total fallback from GPU to CPU',
    ['reason']
)

# =====================================================
# Circuit Breaker
# =====================================================

class CircuitState(Enum):
    CLOSED = 0      # Normal operation
    OPEN = 1        # Circuit open (failures exceeded threshold)
    HALF_OPEN = 2   # Testing if backend recovered

class CircuitBreaker:
    """Circuit breaker pattern for backend health"""
    
    def __init__(self, name: str, failure_threshold: int = 5, timeout: int = 30):
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED
        
    def record_success(self):
        """Record successful request"""
        if self.state == CircuitState.HALF_OPEN:
            logger.info(f"Circuit breaker {self.name}: HALF_OPEN -> CLOSED (success)")
            self.state = CircuitState.CLOSED
        
        self.failures = 0
        self.last_failure_time = None
        circuit_breaker_state.labels(backend=self.name).set(self.state.value)
    
    def record_failure(self):
        """Record failed request"""
        self.failures += 1
        self.last_failure_time = datetime.now()
        
        if self.failures >= self.failure_threshold and self.state == CircuitState.CLOSED:
            logger.warning(
                f"Circuit breaker {self.name}: CLOSED -> OPEN "
                f"({self.failures} failures)"
            )
            self.state = CircuitState.OPEN
        
        circuit_breaker_state.labels(backend=self.name).set(self.state.value)
    
    def can_attempt(self) -> bool:
        """Check if request can be attempted"""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if timeout elapsed
            if (self.last_failure_time and 
                datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout)):
                logger.info(f"Circuit breaker {self.name}: OPEN -> HALF_OPEN (timeout elapsed)")
                self.state = CircuitState.HALF_OPEN
                circuit_breaker_state.labels(backend=self.name).set(self.state.value)
                return True
            return False
        
        # HALF_OPEN: allow one request to test
        return True

# =====================================================
# Backend Health Monitor
# =====================================================

class BackendHealthMonitor:
    """Monitor backend health with periodic checks"""
    
    def __init__(self, name: str, url: str, check_interval: int = 10):
        self.name = name
        self.url = url
        self.check_interval = check_interval
        self.is_healthy = True
        self.last_check: Optional[datetime] = None
        self.consecutive_failures = 0
        
    async def check_health(self) -> bool:
        """Perform health check"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.url}/health")
                
                if response.status_code == 200:
                    self.is_healthy = True
                    self.consecutive_failures = 0
                    backend_health.labels(backend=self.name).set(1)
                    return True
                else:
                    raise Exception(f"Health check returned {response.status_code}")
                    
        except Exception as e:
            self.consecutive_failures += 1
            logger.warning(
                f"Health check failed for {self.name}: {e} "
                f"({self.consecutive_failures} consecutive failures)"
            )
            
            # Mark unhealthy after 3 consecutive failures
            if self.consecutive_failures >= 3:
                self.is_healthy = False
                backend_health.labels(backend=self.name).set(0)
            
            return False
        finally:
            self.last_check = datetime.now()
    
    async def start_monitoring(self):
        """Start periodic health checks"""
        while True:
            await self.check_health()
            await asyncio.sleep(self.check_interval)

# =====================================================
# FastAPI App
# =====================================================

app = FastAPI(
    title="CounselGPT Router",
    description="Adaptive router with GPU priority, CPU fallback, and user preference support",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# Global State
# =====================================================

# Semaphore to limit GPU concurrency
gpu_semaphore = asyncio.Semaphore(GPU_MAX_INFLIGHT)

# Circuit breakers
gpu_circuit_breaker = CircuitBreaker("gpu", CIRCUIT_BREAKER_THRESHOLD, CIRCUIT_BREAKER_TIMEOUT)
cpu_circuit_breaker = CircuitBreaker("cpu", CIRCUIT_BREAKER_THRESHOLD, CIRCUIT_BREAKER_TIMEOUT)

# Health monitors
gpu_health_monitor = BackendHealthMonitor("gpu", GPU_URL, HEALTH_CHECK_INTERVAL)
cpu_health_monitor = BackendHealthMonitor("cpu", CPU_URL, HEALTH_CHECK_INTERVAL)

# =====================================================
# Startup/Shutdown
# =====================================================

@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    logger.info("🚀 Router starting up...")
    logger.info(f"   GPU URL: {GPU_URL}")
    logger.info(f"   CPU URL: {CPU_URL}")
    logger.info(f"   GPU max inflight: {GPU_MAX_INFLIGHT}")
    logger.info(f"   Backend timeout: {BACKEND_TIMEOUT}s")
    
    # Start health monitoring
    asyncio.create_task(gpu_health_monitor.start_monitoring())
    asyncio.create_task(cpu_health_monitor.start_monitoring())
    
    # Initial health checks
    await gpu_health_monitor.check_health()
    await cpu_health_monitor.check_health()
    
    logger.info("✅ Router ready")

@app.on_event("shutdown")
async def shutdown_event():
    """Graceful shutdown"""
    logger.info("🛑 Router shutting down...")

# =====================================================
# Request Forwarding
# =====================================================

async def forward_request(
    backend_name: str,
    backend_url: str,
    request: Request,
    path: str = "/infer",
) -> JSONResponse:
    """
    Forward HTTP request to backend service
    
    Args:
        backend_name: Name for logging/metrics (gpu/cpu)
        backend_url: Base URL of backend service
        request: Incoming FastAPI request
        path: API path to call
        
    Returns:
        JSONResponse with backend response
        
    Raises:
        HTTPException on backend errors
    """
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient(timeout=BACKEND_TIMEOUT) as client:
            # Get request body
            body = await request.body()
            
            # Prepare headers (remove hop-by-hop headers)
            headers = dict(request.headers)
            headers.pop("host", None)
            headers.pop("connection", None)
            headers.pop("transfer-encoding", None)
            
            # Make backend request
            backend_full_url = f"{backend_url}{path}"
            
            logger.info(f"→ Forwarding to {backend_name}: {request.method} {path}")
            
            response = await client.request(
                method=request.method,
                url=backend_full_url,
                content=body,
                headers=headers,
                params=request.query_params,
            )
            
            # Record metrics
            duration = time.time() - start_time
            requests_duration.labels(backend=backend_name).observe(duration)
            requests_total.labels(backend=backend_name, status=response.status_code).inc()
            
            logger.info(
                f"✓ {backend_name} response: {response.status_code} "
                f"({duration:.2f}s)"
            )
            
            # Parse response
            if "application/json" in response.headers.get("content-type", ""):
                content = response.json()
            else:
                content = response.text
            
            return JSONResponse(
                status_code=response.status_code,
                content=content,
            )
            
    except httpx.TimeoutException as e:
        duration = time.time() - start_time
        requests_duration.labels(backend=backend_name).observe(duration)
        requests_total.labels(backend=backend_name, status=504).inc()
        logger.error(f"✗ {backend_name} timeout after {duration:.2f}s: {e}")
        raise HTTPException(status_code=504, detail=f"{backend_name} timeout")
        
    except httpx.RequestError as e:
        duration = time.time() - start_time
        requests_duration.labels(backend=backend_name).observe(duration)
        requests_total.labels(backend=backend_name, status=502).inc()
        logger.error(f"✗ {backend_name} connection error: {e}")
        raise HTTPException(status_code=502, detail=f"{backend_name} unavailable")
        
    except Exception as e:
        duration = time.time() - start_time
        requests_duration.labels(backend=backend_name).observe(duration)
        requests_total.labels(backend=backend_name, status=500).inc()
        logger.error(f"✗ {backend_name} error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# =====================================================
# Routing Logic
# =====================================================

@app.api_route("/infer", methods=["POST"])
async def infer(request: Request):
    """
    Route inference request with adaptive logic:
    
    Priority 1: Respect user's use_gpu preference
    Priority 2: GPU (if available and healthy)
    Priority 3: CPU (fallback)
    
    Routing decision based on:
    - User's use_gpu flag in request body
    - GPU queue capacity
    - Circuit breaker state
    - Backend health
    """
    
    # Parse request body to check use_gpu preference
    try:
        body_bytes = await request.body()
        body = body_bytes.decode('utf-8')
        import json
        payload = json.loads(body) if body else {}
        use_gpu_requested = payload.get("use_gpu", True)  # Default to True for backward compatibility
    except Exception as e:
        logger.warning(f"Failed to parse request body: {e}, defaulting to GPU priority")
        use_gpu_requested = True
    
    # If user explicitly requests CPU, route to CPU directly
    if not use_gpu_requested:
        logger.info("User requested CPU inference, routing to CPU")
        fallback_count.labels(reason="user_preference").inc()
        try:
            return await forward_request("cpu", CPU_URL, request)
        except HTTPException as e:
            cpu_circuit_breaker.record_failure()
            raise
    
    # User wants GPU - continue with existing GPU-priority logic
    # Update capacity gauge
    gpu_capacity.set(gpu_semaphore._value)
    gpu_queue_size.set(GPU_MAX_INFLIGHT - gpu_semaphore._value)
    
    # Check if we should try GPU
    should_try_gpu = (
        gpu_circuit_breaker.can_attempt() and
        gpu_health_monitor.is_healthy and
        gpu_semaphore._value > 0
    )
    
    if not should_try_gpu:
        # GPU not available - go straight to CPU
        reason = "circuit_open" if not gpu_circuit_breaker.can_attempt() else \
                 "unhealthy" if not gpu_health_monitor.is_healthy else \
                 "queue_full"
        
        logger.info(f"⚠️  Skipping GPU (reason: {reason}), routing to CPU")
        fallback_count.labels(reason=reason).inc()
        
        try:
            return await forward_request("cpu", CPU_URL, request)
        except HTTPException as e:
            cpu_circuit_breaker.record_failure()
            raise
    
    # Try to acquire GPU slot
    acquired = False
    try:
        # Non-blocking acquire with immediate timeout
        acquired = await asyncio.wait_for(
            gpu_semaphore.acquire(),
            timeout=0.001
        )
    except asyncio.TimeoutError:
        # GPU queue full - fallback to CPU
        logger.info("⚠️  GPU queue full, routing to CPU")
        fallback_count.labels(reason="queue_full").inc()
        
        try:
            return await forward_request("cpu", CPU_URL, request)
        except HTTPException as e:
            cpu_circuit_breaker.record_failure()
            raise
    
    # GPU slot acquired - try GPU
    try:
        try:
            response = await forward_request("gpu", GPU_URL, request)
            
            # Check for backend errors that should trigger fallback
            if response.status_code >= 500:
                logger.warning(
                    f"⚠️  GPU returned {response.status_code}, "
                    f"attempting CPU fallback"
                )
                gpu_circuit_breaker.record_failure()
                fallback_count.labels(reason="gpu_error").inc()
                
                # Try CPU
                try:
                    return await forward_request("cpu", CPU_URL, request)
                except HTTPException:
                    cpu_circuit_breaker.record_failure()
                    # Return original GPU error
                    return response
            
            # Success!
            gpu_circuit_breaker.record_success()
            return response
            
        except HTTPException as e:
            # GPU failed - try CPU fallback
            logger.warning(f"⚠️  GPU failed: {e.detail}, attempting CPU fallback")
            gpu_circuit_breaker.record_failure()
            fallback_count.labels(reason="gpu_failed").inc()
            
            try:
                response = await forward_request("cpu", CPU_URL, request)
                cpu_circuit_breaker.record_success()
                return response
            except HTTPException:
                cpu_circuit_breaker.record_failure()
                raise
                
    finally:
        if acquired:
            gpu_semaphore.release()
            gpu_capacity.set(gpu_semaphore._value)
            gpu_queue_size.set(GPU_MAX_INFLIGHT - gpu_semaphore._value)

# =====================================================
# Health & Status Endpoints
# =====================================================

@app.get("/health")
async def health():
    """Router health check"""
    return {
        "status": "healthy",
        "backends": {
            "gpu": {
                "url": GPU_URL,
                "healthy": gpu_health_monitor.is_healthy,
                "circuit_breaker": gpu_circuit_breaker.state.name,
                "available_slots": gpu_semaphore._value,
                "max_slots": GPU_MAX_INFLIGHT,
            },
            "cpu": {
                "url": CPU_URL,
                "healthy": cpu_health_monitor.is_healthy,
                "circuit_breaker": cpu_circuit_breaker.state.name,
            }
        }
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

@app.get("/")
async def root():
    """Router info"""
    return {
        "service": "CounselGPT Router",
        "version": "1.0.0",
        "description": "Adaptive router with GPU priority, CPU fallback, and user preference support",
        "routing_logic": {
            "1": "Respects use_gpu flag in request body",
            "2": "GPU priority (if use_gpu=true and available)",
            "3": "CPU fallback (automatic or if use_gpu=false)"
        },
        "endpoints": {
            "/infer": "POST - Run inference (supports use_gpu flag)",
            "/health": "GET - Health check",
            "/metrics": "GET - Prometheus metrics",
        },
        "config": {
            "gpu_url": GPU_URL,
            "cpu_url": CPU_URL,
            "gpu_max_inflight": GPU_MAX_INFLIGHT,
            "backend_timeout": BACKEND_TIMEOUT,
        }
    }

# =====================================================
# Cache endpoints (proxy to backends)
# =====================================================

@app.post("/cache/clear")
async def clear_cache(request: Request):
    """Clear cache (forwards to GPU backend)"""
    return await forward_request("gpu", GPU_URL, request, "/cache/clear")

@app.get("/cache/stats")
async def cache_stats(request: Request):
    """Get cache stats (forwards to GPU backend)"""
    return await forward_request("gpu", GPU_URL, request, "/cache/stats")

