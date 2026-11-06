from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import get_manager
from src.api.schemas import (
    IncidentResponse,
    EvidenceResponse,
    SafeModeRequest,
    SafeModeResponse,
    RecoveryResponse,
    ErrorResponse,
    OperationsResponse,
    OperationsSummaryInfo,
    CaseEventItem,
    CaseCloseRequest,
    CaseCloseResponse,
    ValidationReferenceResponse,
    ActionGuardStatusResponse,
    CaseAcknowledgeRequest,
    CaseAcknowledgeResponse,
    CaseNoteRequest,
    CaseNoteResponse,
    WorkOrderRequest,
    WorkOrderResponse,
    FalsePositiveRequest,
    FalsePositiveResponse,
    ScenarioSwitchRequest,
    ScenarioSwitchResponse,
    ScenariosCatalogResponse,
    TelemetryWindowResponse,
    TelemetryAnalyticsResponse,
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
        scenario_name="Failure #3 - Air Leak" if manager.scenario.scenario_id == "failure_3" else manager.scenario.name,
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


@router.get("/action/guard-status", response_model=ActionGuardStatusResponse)
def get_action_guard_status(
    manager: IncidentLifecycleManager = Depends(get_manager),
) -> ActionGuardStatusResponse:
    """Returns live 4-check ActionGuard safety evaluation including physical brake reservoir pressure."""
    return ActionGuardStatusResponse(**manager.get_action_guard_status())


@router.post(
    "/action/safe-mode",
    response_model=SafeModeResponse,
    responses={409: {"model": ErrorResponse, "description": "Invalid state transition"}},
)
def trigger_safe_mode(
    payload: Optional[SafeModeRequest] = None,
    manager: IncidentLifecycleManager = Depends(get_manager),
) -> SafeModeResponse:
    """Triggers reversible safe mode, transitioning state to MITIGATING and branching stream."""
    op_id = payload.operator_id if payload and payload.operator_id else "DISPATCHER-0941"
    res = manager.trigger_safe_mode(operator_id=op_id)
    return SafeModeResponse(**res)


@router.post(
    "/case/acknowledge",
    response_model=CaseAcknowledgeResponse,
    responses={409: {"model": ErrorResponse, "description": "Active case required"}},
)
def acknowledge_case(
    body: Optional[CaseAcknowledgeRequest] = None,
    manager: IncidentLifecycleManager = Depends(get_manager),
) -> CaseAcknowledgeResponse:
    """Operator acknowledges the active case, assigns priority, and logs an audit event."""
    op_id = body.operator_id if body and body.operator_id else "DISPATCHER-0941"
    priority = body.priority if body and body.priority else "P1-CRITICAL"
    note = body.note if body and body.note else ""
    res = manager.acknowledge_case(operator_id=op_id, priority=priority, note=note)
    return CaseAcknowledgeResponse(**res)


@router.post("/case/notes", response_model=CaseNoteResponse)
def add_case_note(
    body: CaseNoteRequest,
    manager: IncidentLifecycleManager = Depends(get_manager),
) -> CaseNoteResponse:
    """Appends an operator shift handover / diagnostic note to the case audit ledger."""
    res = manager.add_case_note(operator_id=body.operator_id, note=body.note)
    return CaseNoteResponse(**res)


@router.post(
    "/case/work-order",
    response_model=WorkOrderResponse,
    responses={409: {"model": ErrorResponse, "description": "Invalid state for work order"}},
)
def create_work_order(
    body: Optional[WorkOrderRequest] = None,
    manager: IncidentLifecycleManager = Depends(get_manager),
) -> WorkOrderResponse:
    """Dispatches a structured maintenance work order (Step 1 of 2-step maintenance workflow)."""
    req = body or WorkOrderRequest()
    res = manager.create_work_order(
        operator_id=req.operator_id,
        playbook_id=req.playbook_id,
        target_depot=req.target_depot,
        maintenance_window=req.maintenance_window,
        instructions=req.instructions,
    )
    return WorkOrderResponse(**res)


@router.post(
    "/case/false-positive",
    response_model=FalsePositiveResponse,
    responses={409: {"model": ErrorResponse, "description": "Invalid state for false-positive override"}},
)
def mark_false_positive(
    body: Optional[FalsePositiveRequest] = None,
    manager: IncidentLifecycleManager = Depends(get_manager),
) -> FalsePositiveResponse:
    """Marks an active case as a false positive with operator audit provenance."""
    req = body or FalsePositiveRequest()
    res = manager.mark_false_positive(operator_id=req.operator_id, reason=req.reason)
    return FalsePositiveResponse(**res)


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


@router.get("/telemetry/window", response_model=TelemetryWindowResponse)
def get_telemetry_window(
    limit: int = Query(default=60, ge=1, le=500),
    manager: IncidentLifecycleManager = Depends(get_manager),
) -> TelemetryWindowResponse:
    """Returns recent telemetry window enriched with MongoDB $setWindowFields rolling statistics."""
    return TelemetryWindowResponse(**manager.get_telemetry_window_payload(limit=limit))


@router.get("/telemetry/analytics", response_model=TelemetryAnalyticsResponse)
def get_telemetry_analytics(
    manager: IncidentLifecycleManager = Depends(get_manager),
) -> TelemetryAnalyticsResponse:
    """Returns MongoDB $facet/$group regime analytics, failure fingerprint matches, and suppressed signal stats."""
    return TelemetryAnalyticsResponse(**manager.get_telemetry_analytics_payload())


@router.get("/scenarios", response_model=ScenariosCatalogResponse)
def get_scenarios(
    manager: IncidentLifecycleManager = Depends(get_manager),
) -> ScenariosCatalogResponse:
    """Returns available historical scenarios and active scenario ID."""
    return ScenariosCatalogResponse(**manager.get_scenarios_payload())


@router.post("/operations/scenario", response_model=ScenarioSwitchResponse)
def switch_scenario(
    body: ScenarioSwitchRequest,
    manager: IncidentLifecycleManager = Depends(get_manager),
) -> ScenarioSwitchResponse:
    """Switches the active historical replay scenario and resets lifecycle state."""
    res = manager.switch_scenario(scenario_id=body.scenario_id)
    return ScenarioSwitchResponse(**res)


@router.get("/validation-reference", response_model=ValidationReferenceResponse)
def get_validation_reference() -> ValidationReferenceResponse:
    """Returns the ground truth validation reference (historical failure report)."""
    registry = AssetRegistry.get_default()
    ref = registry.get_validation_reference("SCENARIO-FAIL-03")
    return ValidationReferenceResponse(**ref.model_dump())

