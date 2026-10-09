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

