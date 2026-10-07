from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from src.domain.enums import (
    OperatingRegime,
    AssetHealthState,
    IncidentLifecycleState,
    IncidentAction,
    OperationalConfidence,
    DetectorStatus,
    Severity,
    EvidenceCode,
)

class IncidentContext(BaseModel):
    active_incident_id: Optional[str] = None
    lifecycle_state: IncidentLifecycleState = IncidentLifecycleState.NONE

class TelemetryPoint(BaseModel):
    asset_id: str = "APU-COMP-01"
    timestamp: datetime
    tp2_bar: float
    tp3_bar: float
    h1_bar: float
    dv_pressure_bar: float
    reservoirs_bar: float
    oil_temp_c: float
    motor_current_a: float
    comp_val: float
    dv_electric: float
    towers_val: float
    mpg_val: float
    lps_active: float
    pressure_switch: float
    oil_level_low: float
    caudal_impulses: float
    regime: Optional[OperatingRegime] = None

class DetectorResult(BaseModel):
    detector_id: str
    evidence_code: EvidenceCode = EvidenceCode.NORMAL
    status: DetectorStatus
    severity: Severity = Severity.NONE
    observed_value: float = 0.0
    baseline_value: float = 0.0
    sigma_deviation: float = 0.0
    provenance: Dict[str, Any] = Field(default_factory=dict)

class EvidenceState(BaseModel):
    asset_id: str = "APU-COMP-01"
    timestamp: datetime
    regime: OperatingRegime
    signals: List[DetectorResult] = Field(default_factory=list)

class Decision(BaseModel):
    asset_health: AssetHealthState
    incident_action: IncidentAction
    operational_confidence: OperationalConfidence
    ui_action: str
    reason: str
    evidence_state: EvidenceState

class IncidentEvent(BaseModel):
    incident_id: str
    asset_id: str = "APU-COMP-01"
    created_at: datetime
    updated_at: datetime
    lifecycle_state: IncidentLifecycleState
    health_state: AssetHealthState
    operational_confidence: OperationalConfidence
    summary: str
    evidence_chain: List[EvidenceState] = Field(default_factory=list)

class RecoveryStatus(BaseModel):
    asset_id: str = "APU-COMP-01"
    is_recovering: bool = False
    consecutive_healthy_observations: int = 0
    target_healthy_observations: int = 5
    is_verified: bool = False
    verification_reason: str = ""

    # Internal-only legacy alias
    @property
    def consecutive_healthy_cycles(self) -> int:
        return self.consecutive_healthy_observations

    @property
    def target_healthy_cycles(self) -> int:
        return self.target_healthy_observations
