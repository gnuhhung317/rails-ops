import logging
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.routes_demo import router as demo_router
from src.api.routes_product import router as product_router
from src.engine.lifecycle import (
    IncidentLifecycleManager,
    InvalidStateTransitionError,
)

logger = logging.getLogger("compressorguard.api")
_DEFAULT_MANAGER: Optional[IncidentLifecycleManager] = None


def get_default_manager() -> IncidentLifecycleManager:
    """Lazily initializes and returns the shared singleton lifecycle manager."""
    global _DEFAULT_MANAGER
    if _DEFAULT_MANAGER is None:
        _DEFAULT_MANAGER = IncidentLifecycleManager()
    return _DEFAULT_MANAGER


def create_app(manager: Optional[IncidentLifecycleManager] = None) -> FastAPI:
    """
    FastAPI application factory for CompressorGuard Incident Command Console.
    Mounts product domain and demo routes, sets up lifecycle manager singleton,
    and registers domain exception handlers.
    """
    app = FastAPI(
        title="CompressorGuard Incident Command Console API",
        version="2.1.0",
        description="Presentation-agnostic Domain API and Demo Endpoints for Lisbon Metro APU-COMP-01.",
    )

    # Set manager singleton on app state
    app.state.manager = manager if manager is not None else get_default_manager()

    # Mount domain routes and demo controls
    app.include_router(product_router)
    app.include_router(demo_router)

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
