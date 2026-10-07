from fastapi import Request
from src.engine.lifecycle import IncidentLifecycleManager


def get_manager(request: Request) -> IncidentLifecycleManager:
    """Dependency that retrieves the active IncidentLifecycleManager singleton from app state."""
    return request.app.state.manager
