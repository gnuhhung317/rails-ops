from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


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


# --- Operations & Fleet Overview Schemas (Screen 1) ---
class OperationsSummaryInfo(BaseModel):
    monitored_assets_count: int = 1
    active_cases_count: int = 0
    assets_observing_count: int = 0
    scenario_name: str = "Failure #3 — Air Leak"
    simulation_mode: str = "LIVE_SIMULATION"
    confirmed_intervention_window: Optional[str] = None


class TrainSummaryItem(BaseModel):
    train_id: str
    fleet_id: str = "FLEET-METRO-01"
    name: str
    route: str = "Bến Thành – Suối Tiên"
    car_number: str = "Toa 1 (Cabin lái điều khiển)"
    service_status: str = "REVENUE_SERVICE"
    health_status: str = "NORMAL"          # "NORMAL" | "WARNING_P1"
    health_label: str = "Bình thường"      # "Bình thường" | "Cảnh báo P1"
    status: str = "NORMAL"
    badge: str = "NORMAL"                 # "NORMAL" | "WARNING"
    speed_kmh: float = 58.0
    brake_pressure_bar: float = 9.20
    brake_safety_margin: str = "+2.20 bar"
    safety_buffer: str = "—"
    subsystem_id: str = "SUB-APU-01"
    depot_location: str = "Depot Long Bình"
    updated_at: Optional[str] = None


class OperationsKPIsResponse(BaseModel):
    total_trains: str = "3/3 đang chạy"
    total_trains_count: int = 3
    running_trains_count: int = 3
    normal_trains: int = 2
    alert_trains: int = 1
    alerted_trains: int = 1               # Đồng bộ bí danh
    depot: str = "Depot Long Bình"
    standby_depot: str = "Depot Long Bình" # Đồng bộ bí danh


class OperationsHeroBannerResponse(BaseModel):
    active: bool = True
    is_active: bool = True                # Đồng bộ bí danh
    train_id: str = "TRAIN-302"
    train_name: str = "Đoàn tàu 302"
    safety_buffer: str = "33h 52m"
    safety_buffer_minutes: int = 2032
    severity: str = "P1"
    priority_label: str = "P1 - CẢNH BÁO RÒ RỈ KHÍ"
    title: str = "CẢNH BÁO P1 — RÒ RỈ KHÍ PHÂN HỆ APU"
    brake_margin: str = "+2.19 bar"
    action_target: str = "view-workbench"
    action_label: str = "Vào Phòng Điều Tra Sự Cố ➔"
    description: str = (
        "Phát hiện rò van xả cụm sấy khí LP49 trên đoàn tàu TRAIN-302. "
        "Áp suất phanh hiện tại 9.19 bar (vùng an toàn +2.19 bar)."
    )


class OperationsResponse(BaseModel):
    fleet: dict
    train: dict
    subsystem: dict
    asset: dict
    operations_summary: OperationsSummaryInfo
    active_case: Optional[dict] = None
    trains: List[Dict[str, Any]] = Field(default_factory=list)
    kpis: Optional[OperationsKPIsResponse] = None
    hero_banner: Optional[OperationsHeroBannerResponse] = None


# --- Asset & Component Management Schemas (Screen 2) ---
class ComponentDetailResponse(BaseModel):
    component_id: str
    asset_id: Optional[str] = None
    subsystem_id: str = "SUB-APU-01"
    train_id: str = "TRAIN-302"
    fleet_id: str = "FLEET-METRO-01"
    name: str
    component_type: str                   # "COMPRESSOR" | "DRYER_DRAIN_VALVE" | "RESERVOIR" | "PRESSURE_SWITCH"
    manufacturer: str = "Knorr-Bremse"
    model_number: str
    installation_date: str = "15/01/2020"
    operating_hours: int = 14280
    rated_pressure_bar: float = 10.0
    criticality: str = "CRITICAL"
    service_role: str = "Main Air Supply"
    service_role_vi: str = "Cấp khí nén hệ thống phanh & treo"
    discharge_valve_model: Optional[str] = None
    status: str = "NORMAL"                # "NORMAL" | "WARNING" | "LEAKING" | "SAFE"
    status_label: str = "Bình thường"
    badge: str = "NORMAL"
    
    # 6 trường cấu hình vận hành có thể chỉnh sửa
    leak_pressure_threshold_bar: float = 0.05
    oil_temp_threshold_c: float = 67.0
    maintenance_depot: str = "Depot Long Bình"
    transient_filter: bool = True
    supervision_priority: str = "P1 - Khẩn cấp"
    maintenance_notes: str = ""
    
    last_updated_by: Optional[str] = "Hùng Bùi (NV-0941)"
    last_updated_at: Optional[str] = None
    latest_reading: Dict[str, Any] = Field(default_factory=dict)
    audit_event: Optional[Dict[str, Any]] = None


class ComponentUpdateRequest(BaseModel):
    leak_pressure_threshold_bar: Optional[float] = None
    oil_temp_threshold_c: Optional[float] = None
    maintenance_depot: Optional[str] = None
    transient_filter: Optional[bool] = None
    supervision_priority: Optional[str] = None
    maintenance_notes: Optional[str] = None
    operator_name: Optional[str] = "Hùng Bùi (NV-0941)"
    operator_id: Optional[str] = "NV-0941"


class ComponentsListResponse(BaseModel):
    train_id: Optional[str] = "TRAIN-302"
    total_count: int
    tree: Dict[str, Any]
    components: List[ComponentDetailResponse]


class ComponentUpdateResponse(BaseModel):
    status: str = "CONFIG_UPDATED"
    message: str = "Cập nhật cấu hình thành công"
    component: ComponentDetailResponse
    audit_event: Optional[Dict[str, Any]] = None


# --- SOP Playbooks Schemas (Screen 4) ---
class SOPStepItem(BaseModel):
    step_number: int
    action: str
    safety_check: Optional[str] = None
    expected_result: Optional[str] = None
    role: Optional[str] = None


class SOPPlaybookResponse(BaseModel):
    sop_id: str
    title: str
    category: str = "Hệ thống khí nén APU"
    version: str = "v2.1"
    effective_date: str = "2024-01-15"
    applicable_component_id: str = "APU-DRY-LP49"
    target_component: Optional[str] = None
    target_depot: str = "Depot Long Bình"
    estimated_duration_minutes: int = 45
    priority: str = "P1"
    maintenance_window: Optional[str] = "NEXT_TERMINAL_STOP"
    safety_warning: Optional[str] = None
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    safety_precautions: List[str] = Field(default_factory=list)
    last_updated_by: Optional[str] = "Hùng Bùi (NV-0941)"
    last_updated_at: Optional[str] = None


class SOPPlaybookUpdateRequest(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    version: Optional[str] = None
    applicable_component_id: Optional[str] = None
    target_component: Optional[str] = None
    target_depot: Optional[str] = None
    estimated_duration_minutes: Optional[int] = None
    priority: Optional[str] = None
    maintenance_window: Optional[str] = None
    safety_warning: Optional[str] = None
    steps: Optional[List[Dict[str, Any]]] = None
    safety_precautions: Optional[List[str]] = None
    operator_name: Optional[str] = "Hùng Bùi (NV-0941)"


class SOPPlaybooksListResponse(BaseModel):
    total_count: int
    playbooks: List[SOPPlaybookResponse]


# --- Shift Operations & Handover Schemas (Screen 4) ---
class CurrentShiftResponse(BaseModel):
    shift_id: str = "SHIFT-20200605-01"
    shift_name: str = "Ca 1 (06:00 – 14:00)"
    operator_name: str = "Hùng Bùi"
    operator_id: str = "NV-0941"
    role: str = "Trực ban Điều hành OCC"
    facility: str = "Trung tâm Điều hành OCC Tuyến Metro Số 1 (HURC1)"
    depot: str = "Depot Long Bình"
    status: str = "Đang chỉ huy trực tiếp"
    active_train_count: int = 3
    active_alert_count: int = 1
    start_time: str = "06:00"
    end_time: str = "14:00"
    handover_pending: bool = False
    last_handover_time: Optional[str] = None


class ShiftHandoverRequest(BaseModel):
    operator_name: Optional[str] = "Hùng Bùi (NV-0941)"
    operator_id: Optional[str] = "NV-0941"
    incoming_operator: Optional[str] = None
    incoming_operator_name: Optional[str] = None
    incoming_operator_id: Optional[str] = "NV-1082"
    shift_name: Optional[str] = "Ca 2 (14:00 – 22:00)"
    depot_location: Optional[str] = "Depot Long Bình"
    handover_notes: Optional[str] = None
    notes: Optional[str] = None
    acknowledged_active_cases: List[str] = Field(default_factory=lambda: ["APU-INC-20200605-01"])


class ShiftHandoverResponse(BaseModel):
    handover_id: str
    status: str = "HANDOVER_COMPLETED"
    message: str = "Bàn giao ca trực thành công"
    timestamp: str
    outgoing_operator: str
    incoming_operator: str
    next_shift: str
    handover_notes: str
    event_id: Optional[str] = None
    active_cases_transferred: List[str] = Field(default_factory=list)


# --- Case Events & Ledger Schemas ---
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


# --- Datadog SRE Observability Schemas ---
class DatadogMonitorItem(BaseModel):
    id: str
    name: str
    query: str
    status: str  # "OK", "ALERT", "WARN", "PENDING"
    threshold: str
    target_channel: str
    description: str


class DatadogAPMSpanItem(BaseModel):
    name: str
    duration_ms: float
    status: str = "ok"


class DatadogStatusResponse(BaseModel):
    connected: bool
    site: str
    dashboard_url: str
    dogstatsd_packets_total: int
    custom_metrics_count: int = 15
    apm_latency_ms: float
    apm_sla_ms: float = 15.0
    apm_spans: List[DatadogAPMSpanItem]
    monitors: List[DatadogMonitorItem]

