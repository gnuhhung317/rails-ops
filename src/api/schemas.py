from typing import List, Optional
from pydantic import BaseModel


# --- Error Schemas ---
class ErrorResponse(BaseModel):
    error: str
    detail: str


# --- Product API Schemas ---
class LeadTimeInfo(BaseModel):
    lead_time_minutes: int
    lead_time_formatted: str
    conventional_alert_timestamp: str
    earliest_detection_timestamp: str


class IncidentResponse(BaseModel):
    incident_id: str
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


class SafeModeResponse(BaseModel):
    action_id: str
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
