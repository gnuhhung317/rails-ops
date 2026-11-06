from typing import List, Optional
from pydantic import BaseModel


# --- Error Schemas ---
class ErrorResponse(BaseModel):
    error: str
    detail: str


# --- Product API Schemas ---
class LeadTimeInfo(BaseModel):
    lead_time_minutes: Optional[int] = None
    lead_time_formatted: Optional[str] = None
    conventional_alert_timestamp: Optional[str] = None
    earliest_detection_timestamp: Optional[str] = None


class IncidentResponse(BaseModel):
    incident_id: Optional[str] = None
    asset_id: str = "APU-COMP-01"
    lifecycle_state: str
    asset_health: str
    operational_confidence: str
    lead_time: LeadTimeInfo
    runtime_warning: Optional[dict] = None
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    priority: str = "P2-WARNING"
    work_order: Optional[dict] = None
    summary: str


class EvidenceSignalItem(BaseModel):
    code: str
    signal_name: str
    observed_value: float
    baseline_value: float
    unit: str
    sigma_deviation: Optional[float] = None
    status: str
    is_primary: bool
    provenance: dict = {}


class PersistenceInfo(BaseModel):
    confirmed: bool
    recent_observations: int
    required_observations: int


class EvidenceResponse(BaseModel):
    incident_id: str
    regime: str
    evidence_pack: List[EvidenceSignalItem]
    persistence: PersistenceInfo


class StreamBranchInfo(BaseModel):
    source: str
    offset_timestamp: str


class SafeModeRequest(BaseModel):
    operator_id: str = "DISPATCHER-0941"


class SafeModeResponse(BaseModel):
    action_id: str
    operator_id: Optional[str] = "DISPATCHER-0941"
    status: str
    execution_mode: str
    target_state: str
    stream_branch: StreamBranchInfo


class LatestTelemetry(BaseModel):
    dv_pressure_bar: float
    oil_temp_c: float
    regime: str


class RecoveryCriteriaInfo(BaseModel):
    dv_pressure_max: float
    oil_temp_max: float
    required_regime: str


class RecoveryResponse(BaseModel):
    incident_id: str
    is_recovering: bool
    is_verified: bool
    consecutive_healthy_observations: int
    target_healthy_observations: int
    latest_telemetry: LatestTelemetry
    criteria: RecoveryCriteriaInfo


# --- Demo Simulation Schemas ---
class ResetRequest(BaseModel):
    milestone: Optional[str] = None


class ResetResponse(BaseModel):
    status: str = "RESET_OK"
    milestone: Optional[str] = None


class TickResponse(BaseModel):
    status: str = "TICK_OK"
    lifecycle_state: str


class JumpRequest(BaseModel):
    milestone: str


class JumpResponse(BaseModel):
    status: str = "JUMP_OK"
    milestone: str
    lifecycle_state: str


# --- Operations & Case Governance Schemas ---
class OperationsSummaryInfo(BaseModel):
    monitored_assets_count: int = 1
    active_cases_count: int = 0
    assets_observing_count: int = 0
    scenario_name: str = "Failure #3 — Air Leak"
    simulation_mode: str = "LIVE_SIMULATION"
    confirmed_intervention_window: Optional[str] = None


class OperationsResponse(BaseModel):
    fleet: dict
    train: dict
    subsystem: dict
    asset: dict
    operations_summary: OperationsSummaryInfo
    active_case: Optional[dict] = None


class CaseEventItem(BaseModel):
    event_id: str
    case_id: str = "APU-INC-20200605-01"
    event_time: str
    event_type: str
    phase: str
    title: str
    detail: str
    actor: str
    source: str
    provenance: dict = {}


class CaseCloseRequest(BaseModel):
    operator_id: str = "DISPATCHER-0941"
    notes: Optional[str] = ""


class CaseCloseResponse(BaseModel):
    status: str
    operator_id: str
    notes: str
    lifecycle_state: str
    asset_health: str


class ValidationReferenceResponse(BaseModel):
    scenario_id: str
    scenario_name: str
    dataset_source: str
    historical_period: str
    reported_failure_mode: str
    reported_failure_start: str
    conventional_lps_breach: str
    online_detector_confirmation: str
    confirmed_intervention_window_minutes: int
    confirmed_intervention_window_formatted: str
    maintenance_summary: str


# --- Simulation Playback & Pacing Schemas ---
class SimulationSpeedRequest(BaseModel):
    speed_multiplier: float


class SimulationPlaybackResponse(BaseModel):
    status: str
    is_paused: bool
    speed_multiplier: Optional[float] = None


class SimulationStatusResponse(BaseModel):
    scenario_name: str
    is_paused: bool
    speed_multiplier: float
    current_event_time: Optional[str] = None
    total_points_emitted: int
    mode: str = "LIVE_SIMULATION"
    provenance: str = "MetroPT-3 Historical Telemetry"


# --- Production Operator Workflow, ActionGuard & MongoDB Analytics Schemas ---
class ActionGuardCheckItemSchema(BaseModel):
    id: str
    label: str
    passed: bool
    current_value: Optional[str] = None


class ActionGuardStatusResponse(BaseModel):
    is_permitted: bool
    passed_count: int = 0
    total_checks: int = 5
    denial_reason: Optional[str] = ""
    checklist: List[ActionGuardCheckItemSchema] = []


class CaseAcknowledgeRequest(BaseModel):
    operator_id: str = "DISPATCHER-0941"
    priority: str = "P1-CRITICAL"
    note: Optional[str] = ""


class CaseAcknowledgeResponse(BaseModel):
    status: str
    case_id: str
    operator_id: str
    priority: str
    acknowledged: bool
    event_id: str


class CaseNoteRequest(BaseModel):
    operator_id: str = "DISPATCHER-0941"
    note: str


class CaseNoteResponse(BaseModel):
    status: str
    event_id: str
    operator_id: str
    note: str
    event_time: str


class WorkOrderRequest(BaseModel):
    operator_id: str = "DISPATCHER-0941"
    playbook_id: str = "PB-APU-03-AIR-LEAK"
    target_depot: str = "DEPOT-LONGBINH-01"
    maintenance_window: str = "NEXT_TERMINAL_STOP"
    instructions: str = "Inspect discharge valve seal and pneumatic air leak prior to LPS threshold breach."


class WorkOrderResponse(BaseModel):
    work_order_id: str
    case_id: str
    asset_id: str
    operator_id: str
    playbook_id: str
    target_depot: str
    maintenance_window: str
    instructions: str
    status: str
    created_at: str
    event_id: str


class FalsePositiveRequest(BaseModel):
    operator_id: str = "DISPATCHER-0941"
    reason: str = "Sensor calibration transient verified by field technician."


class FalsePositiveResponse(BaseModel):
    status: str
    operator_id: str
    reason: str
    lifecycle_state: str
    asset_health: str
    event_id: str


class ScenarioSwitchRequest(BaseModel):
    scenario_id: str


class ScenarioSwitchResponse(BaseModel):
    status: str
    scenario_id: str
    scenario_name: str
    stream_start: str
    stream_end: str
    milestones: dict = {}


class ScenariosCatalogResponse(BaseModel):
    active_scenario_id: str
    scenarios: List[dict]


class TelemetryWindowResponse(BaseModel):
    asset_id: str
    count: int
    window_size: int
    points: List[dict]


class TelemetryAnalyticsResponse(BaseModel):
    asset_id: str
    regime_analytics: dict
    fingerprint_matches: List[dict]
    top_diagnosis: Optional[dict] = None
    alert_fatigue_protection: dict


