from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_manager
from src.api.schemas import (
    IncidentResponse,
    EvidenceResponse,
    SafeModeResponse,
    RecoveryResponse,
    ErrorResponse,
    OperationsResponse,
    OperationsSummaryInfo,
    CaseEventItem,
    CaseCloseRequest,
    CaseCloseResponse,
    ValidationReferenceResponse,
)
from src.domain.enums import IncidentLifecycleState
from src.domain.registry import AssetRegistry
from src.engine.lifecycle import IncidentLifecycleManager

router = APIRouter(prefix="/api", tags=["Product Domain"])


@router.get("/operations", response_model=OperationsResponse)
def get_operations(manager: IncidentLifecycleManager = Depends(get_manager)) -> OperationsResponse:
    """Returns the operations command overview with asset hierarchy and active case."""
    registry = AssetRegistry.get_default()
    has_active = manager.has_active_case()
    is_observing = manager.lifecycle_state == IncidentLifecycleState.NONE

    lead_time_val = None
    if has_active:
        payload = manager.get_incident_payload()
        lead_time_val = payload.get("lead_time", {}).get("lead_time_formatted")

    summary = OperationsSummaryInfo(
        monitored_assets_count=1,
        active_cases_count=1 if has_active else 0,
        assets_observing_count=1 if is_observing else 0,
        scenario_name="Failure #3 — Air Leak" if manager.scenario.scenario_id == "failure_3" else manager.scenario.name,
        simulation_mode="LIVE_SIMULATION",
        confirmed_intervention_window=lead_time_val,
    )

    return OperationsResponse(
        fleet=registry.fleets["FLEET-METRO-01"].model_dump(),
        train=registry.trains["TRAIN-302"].model_dump(),
        subsystem=registry.subsystems["SUB-APU-01"].model_dump(),
        asset=registry.assets["APU-COMP-01"].model_dump(),
        operations_summary=summary,
        active_case=manager.get_incident_payload() if has_active else None,
    )


@router.get("/incident", response_model=IncidentResponse)
@router.get("/case", response_model=IncidentResponse)
def get_incident(manager: IncidentLifecycleManager = Depends(get_manager)) -> IncidentResponse:
    """Returns the current incident state matching the product domain schema."""
    return manager.get_incident_payload()


@router.get("/evidence", response_model=EvidenceResponse)
def get_evidence(manager: IncidentLifecycleManager = Depends(get_manager)) -> EvidenceResponse:
    """Returns the current evidence pack with thermodynamics and persistence."""
    return manager.get_evidence_payload()


@router.get("/case/events", response_model=List[CaseEventItem])
@router.get("/timeline", response_model=List[CaseEventItem])
def get_case_events(manager: IncidentLifecycleManager = Depends(get_manager)) -> List[CaseEventItem]:
    """Returns the append-only operational timeline ledger."""
    return [CaseEventItem(**e) for e in manager.get_case_events()]


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


@router.post(
    "/case/close",
    response_model=CaseCloseResponse,
    responses={409: {"model": ErrorResponse, "description": "Recovery criteria not verified"}},
)
def close_case(
    body: Optional[CaseCloseRequest] = None,
    manager: IncidentLifecycleManager = Depends(get_manager),
) -> CaseCloseResponse:
    """Closes an active operational case after recovery has been verified."""
    op_id = body.operator_id if body and body.operator_id else "DISPATCHER-0941"
    notes = body.notes if body and body.notes else ""
    try:
        res = manager.close_case(operator_id=op_id, notes=notes)
        return CaseCloseResponse(**res)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/recovery", response_model=RecoveryResponse)
def get_recovery(manager: IncidentLifecycleManager = Depends(get_manager)) -> RecoveryResponse:
    """Returns physical recovery tracking status against evaluation window criteria."""
    return manager.get_recovery_payload()


@router.get("/validation-reference", response_model=ValidationReferenceResponse)
def get_validation_reference() -> ValidationReferenceResponse:
    """Returns the ground truth validation reference (historical failure report)."""
    registry = AssetRegistry.get_default()
    ref = registry.get_validation_reference("SCENARIO-FAIL-03")
    return ValidationReferenceResponse(**ref.model_dump())
