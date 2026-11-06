import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from starlette.staticfiles import StaticFiles

from src.api.routes_demo import router as demo_router
from src.api.routes_product import router as product_router
from src.engine.lifecycle import (
    IncidentLifecycleManager,
    InvalidStateTransitionError,
)
from src.observability.logger import setup_datadog_logging
from src.observability.tracer import get_tracer

logger = setup_datadog_logging("compressorguard.api")
_DEFAULT_MANAGER: Optional[IncidentLifecycleManager] = None
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


def get_default_manager() -> IncidentLifecycleManager:
    """Lazily initializes and returns the shared singleton lifecycle manager."""
    global _DEFAULT_MANAGER
    if _DEFAULT_MANAGER is None:
        from src.storage.repository import CompressorGuardRepository
        repo = CompressorGuardRepository()
        _DEFAULT_MANAGER = IncidentLifecycleManager(repository=repo)
    return _DEFAULT_MANAGER


async def _background_stream_worker(app: FastAPI) -> None:
    """Background worker that advances telemetry stream when simulation is playing (unpaused)."""
    try:
        while True:
            mgr: Optional[IncidentLifecycleManager] = getattr(app.state, "manager", None)
            if mgr is not None and mgr.runner is not None and not mgr.runner.is_paused:
                mgr.tick()
                delay = max(0.05, mgr.runner.get_sleep_interval_seconds())
                await asyncio.sleep(delay)
            else:
                await asyncio.sleep(0.25)
    except asyncio.CancelledError:
        pass


def create_app(manager: Optional[IncidentLifecycleManager] = None) -> FastAPI:
    """
    FastAPI application factory for CompressorGuard Incident Command Console.
    Mounts product domain and demo routes, sets up lifecycle manager singleton,
    and registers domain exception handlers.
    """
    @asynccontextmanager
    async def lifespan(app_instance: FastAPI):
        worker_task = asyncio.create_task(_background_stream_worker(app_instance))
        try:
            yield
        finally:
            worker_task.cancel()
            try:
                await worker_task
            except asyncio.CancelledError:
                pass

    app = FastAPI(
        title="CompressorGuard Incident Command Console API",
        version="2.2.0",
        description="Presentation-agnostic Domain API and Demo Endpoints for Lisbon Metro APU-COMP-01.",
        lifespan=lifespan,
    )

    # Set manager singleton on app state
    app.state.manager = manager if manager is not None else get_default_manager()

    # Mount static assets if directory exists
    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    # Datadog APM tracing middleware
    @app.middleware("http")
    async def datadog_apm_middleware(request: Request, call_next):
        tracer = get_tracer()
        with tracer.trace("fastapi.request", resource=f"{request.method} {request.url.path}", service="compressorguard") as span:
            span.set_tag("http.url", str(request.url.path))
            span.set_tag("http.method", request.method)
            response = await call_next(request)
            span.set_tag("http.status_code", response.status_code)
            return response

    # Mount domain routes and demo controls
    app.include_router(product_router)
    app.include_router(demo_router)

    # Health probe
    @app.get("/health")
    def health():
        return {
            "name": "CompressorGuard API",
            "version": "2.1.0",
            "status": "OPERATIONAL",
        }

    # Console landing routes
    @app.get("/")
    @app.get("/console")
    def serve_console(request: Request):
        accept = request.headers.get("accept", "")
        index_file = STATIC_DIR / "index.html"
        if index_file.exists() and ("text/html" in accept or "application/json" not in accept):
            return FileResponse(str(index_file))
        return {
            "name": "CompressorGuard API",
            "version": "2.1.0",
            "status": "OPERATIONAL",
            "console_url": "/console",
        }

    # Exception Handlers
    @app.exception_handler(InvalidStateTransitionError)

    async def invalid_state_transition_handler(
        request: Request, exc: InvalidStateTransitionError
    ) -> JSONResponse:
        logger.warning(
            "Invalid state transition on %s %s: %s", request.method, request.url.path, exc
        )
        return JSONResponse(
            status_code=409,
            content={"error": "INVALID_STATE_TRANSITION", "detail": str(exc)},
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(
        request: Request, exc: ValueError
    ) -> JSONResponse:
        logger.warning(
            "Invalid argument on %s %s: %s", request.method, request.url.path, exc
        )
        return JSONResponse(
            status_code=400,
            content={"error": "INVALID_ARGUMENT", "detail": str(exc)},
        )

    return app
