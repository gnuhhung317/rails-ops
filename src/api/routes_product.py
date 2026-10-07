from fastapi import APIRouter, Depends

from src.api.dependencies import get_manager
from src.api.schemas import (
    IncidentResponse,
    EvidenceResponse,
    SafeModeResponse,
    RecoveryResponse,
    ErrorResponse,
)
from src.engine.lifecycle import IncidentLifecycleManager

router = APIRouter(prefix="/api", tags=["Product Domain"])


@router.get("/incident", response_model=IncidentResponse)
def get_incident(manager: IncidentLifecycleManager = Depends(get_manager)) -> IncidentResponse:
    """Returns the current incident state matching the product domain schema."""
    return manager.get_incident_payload()


@router.get("/evidence", response_model=EvidenceResponse)
def get_evidence(manager: IncidentLifecycleManager = Depends(get_manager)) -> EvidenceResponse:
    """Returns the current evidence pack with thermodynamics and persistence."""
    return manager.get_evidence_payload()


@router.post(
    "/action/safe-mode",
    response_model=SafeModeResponse,
    responses={409: {"model": ErrorResponse, "description": "Invalid state transition"}},
)
def trigger_safe_mode(
    manager: IncidentLifecycleManager = Depends(get_manager),
) -> SafeModeResponse:
    """Triggers reversible safe mode, transitioning state to MITIGATING and branching stream."""
    return manager.trigger_safe_mode()


@router.get("/recovery", response_model=RecoveryResponse)
def get_recovery(manager: IncidentLifecycleManager = Depends(get_manager)) -> RecoveryResponse:
    """Returns physical recovery tracking status against evaluation window criteria."""
    return manager.get_recovery_payload()
