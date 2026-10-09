from typing import Optional, Dict, Any, List
import pandas as pd

from src.domain.contracts import BaseDetector
from src.domain.enums import (
    AssetHealthState,
    IncidentLifecycleState,
    IncidentAction,
    OperationalConfidence,
    DetectorStatus,
    EvidenceCode,
)
from src.domain.models import (
    TelemetryPoint,
    EvidenceState,
    IncidentEvent,
    IncidentContext,
    Decision,
    CaseEvent,
    CaseEventType,
)
from src.engine.action_guard import ActionGuard
from src.engine.decision import DecisionEngine
from src.engine.factory import setup_golden_path
from src.engine.fusion import EvidenceFusionEngine
from src.engine.recovery import RecoveryVerifier
from src.engine.replay import ReplayEngine

MILESTONES = {
    "onset_0950": "2020-06-05 09:50:00",
    "ml_corroborated_1015": "2020-06-05 10:15:00",
    "lps_reactive_1942": "2020-06-06 19:42:19",
    "post_maintenance_1605": "2020-06-08 16:05:00",
}

_CACHED_GOLDEN_PATH = None


def get_shared_golden_path():
    """Lazily loads and caches the shared golden path engine components."""
    global _CACHED_GOLDEN_PATH
    if _CACHED_GOLDEN_PATH is None:
        _CACHED_GOLDEN_PATH = setup_golden_path()
    return _CACHED_GOLDEN_PATH


class InvalidStateTransitionError(Exception):
    """Raised when an invalid lifecycle state transition is requested."""
    pass


class IncidentLifecycleManager:
    """
    Pure domain orchestrator for CompressorGuard incident lifecycle.
    Coordinates the physical telemetry stream, detectors, evidence fusion,
    decision engine, and RecoveryVerifier.

    CRITICAL INVARIANTS:
    1. Does NOT own or duplicate sensor truth. All sensor values, sigmas,
       and decisions come directly from the engine components.
    2. Exact state machine transitions:
       - onset at June 5 09:50 -> DETECTED
       - ML corroboration at June 5 10:15 -> INVESTIGATING
       - Safe Mode trigger -> MITIGATING
       - First recovery tick -> VERIFYING_RECOVERY
       - 5 healthy windows verified by RecoveryVerifier -> RESOLVED
    3. Invalid state transition protection: calling trigger_safe_mode() when
       in MITIGATING, VERIFYING_RECOVERY, or RESOLVED raises InvalidStateTransitionError.
    4. Two-run replay is 100% deterministic.
    """

    def __init__(
        self,
        replay: Optional[ReplayEngine] = None,
        detectors: Optional[List[BaseDetector]] = None,
        fusion: Optional[EvidenceFusionEngine] = None,
        decision_engine: Optional[DecisionEngine] = None,
        recovery_verifier: Optional[RecoveryVerifier] = None,
    ) -> None:
        self.milestones: Dict[str, str] = MILESTONES.copy()
        self.replay: Optional[ReplayEngine] = replay
        self.detectors: Optional[List[BaseDetector]] = detectors
        self.fusion: Optional[EvidenceFusionEngine] = fusion
        self.decision_engine: Optional[DecisionEngine] = decision_engine
        self.recovery_verifier: RecoveryVerifier = recovery_verifier or RecoveryVerifier()

        self.window: List[TelemetryPoint] = []
        self.active_incident: Optional[IncidentEvent] = None
        self.lifecycle_state: IncidentLifecycleState = IncidentLifecycleState.NONE
        self.asset_health: AssetHealthState = AssetHealthState.HEALTHY
        self.operational_confidence: OperationalConfidence = OperationalConfidence.NONE
        self.is_recovery_branch: bool = False
        self.stream = None
        self.current_point: Optional[TelemetryPoint] = None
        self.current_evidence_state: Optional[EvidenceState] = None
        self.current_decision: Optional[Decision] = None
        self.action_guard: ActionGuard = ActionGuard()
        self.case_events: List[CaseEvent] = []

        if (
            self.replay is None
            or self.detectors is None
            or self.fusion is None
            or self.decision_engine is None
        ):
            self.initialize()
        else:
            self.reset()

    def initialize(self) -> None:
        """Initializes replay, detectors, fusion, and decision engine."""
        self.replay, self.detectors, self.fusion, self.decision_engine = get_shared_golden_path()
        self.reset()

    def reset(self) -> None:
        """
        Resets state, recovery verifier, sliding window, and degradation stream
        from 2020-06-05 09:40:00 to 2020-06-06 20:00:00.
        """
        self.window = []
        self.active_incident = None
        self.lifecycle_state = IncidentLifecycleState.NONE
        self.asset_health = AssetHealthState.HEALTHY
        self.operational_confidence = OperationalConfidence.NONE
        self.is_recovery_branch = False
        self.current_point = None
        self.current_evidence_state = None
        self.current_decision = None
        self.case_events = []
        self.recovery_verifier.reset()
        if self.replay is not None:
            self.stream = self.replay.stream_telemetry(
                "2020-06-05 09:40:00", "2020-06-06 20:00:00"
            )

    def record_case_event(
        self,
        event_type: CaseEventType,
        phase: str,
        title: str,
        detail: str,
        actor: str = "system",
        source: str = "CompressorGuard Engine",
        provenance: Optional[Dict[str, Any]] = None,
        event_time: Optional[Any] = None,
    ) -> CaseEvent:
        if event_time is not None:
            ts = pd.to_datetime(event_time)
        elif self.current_point is not None:
            ts = self.current_point.timestamp
        else:
            ts = pd.to_datetime("2020-06-05 09:40:00")

        evt = CaseEvent(
            event_id=f"EVT-{len(self.case_events) + 1:03d}",
            event_time=ts,
            event_type=event_type,
            phase=phase,
            title=title,
            detail=detail,
            actor=actor,
            source=source,
            provenance=provenance or {},
        )
        self.case_events.append(evt)
        return evt

    def get_case_events(self) -> List[Dict[str, Any]]:
        result = []
        for evt in self.case_events:
            d = evt.model_dump()
            if hasattr(d["event_time"], "isoformat"):
                d["event_time"] = d["event_time"].isoformat()
            else:
                d["event_time"] = str(d["event_time"])
            result.append(d)
        return result

    def close_case(self, operator_id: str = "DISPATCHER-0941", notes: str = "") -> Dict[str, Any]:
        if not self.recovery_verifier.is_verified:
            raise ValueError("Recovery not verified. Cannot close operational case before 5/5 healthy LOADED observations are verified.")
        self.lifecycle_state = IncidentLifecycleState.RESOLVED
        self.asset_health = AssetHealthState.HEALTHY
        if self.active_incident:
            self.active_incident.lifecycle_state = IncidentLifecycleState.RESOLVED
            self.active_incident.health_state = AssetHealthState.HEALTHY
            if self.current_point:
                self.active_incident.updated_at = self.current_point.timestamp

        self.record_case_event(
            event_type=CaseEventType.CASE_CLOSED,
            phase="RESOLVED",
            title="Case Signed Off & Closed",
            detail=f"Operator {operator_id} signed off incident. Asset APU-COMP-01 released back to HEALTHY service. Notes: {notes or 'Recovery criteria satisfied'}",
            actor=f"operator:{operator_id}",
            source="Operations Console",
        )
        return {
            "status": "CASE_CLOSED",
            "operator_id": operator_id,
            "notes": notes,
            "lifecycle_state": "RESOLVED",
            "asset_health": "HEALTHY",
        }

    def trigger_safe_mode(self) -> Dict[str, Any]:
        """
        Validates state, transitions to MITIGATING, and branches stream to
        post-maintenance (2020-06-08 16:05:00 to 2020-06-08 17:00:00).
        """
        if self.lifecycle_state not in (
            IncidentLifecycleState.DETECTED,
            IncidentLifecycleState.INVESTIGATING,
        ):
            raise InvalidStateTransitionError(
                f"Action safe-mode is not permitted when incident is in state {self.lifecycle_state.value}."
            )

        if (
            self.current_decision is None
            or self.current_decision.recommended_action != IncidentAction.EXECUTE_MITIGATION
        ):
            raise InvalidStateTransitionError(
                "Action safe-mode rejected: DecisionEngine has not recommended mitigation for current evidence."
            )

        guard_res = self.action_guard.validate(
            lifecycle_state=self.lifecycle_state,
            has_active_case=(self.active_incident is not None),
            recommended_action=self.current_decision.recommended_action,
            replay_branch_available=True,
            conflicting_cases_count=0,
        )
        if not guard_res.is_permitted:
            raise InvalidStateTransitionError(f"Action safe-mode rejected: {guard_res.denial_reason}")

        self.lifecycle_state = IncidentLifecycleState.MITIGATING
        if self.active_incident:
            self.active_incident.lifecycle_state = IncidentLifecycleState.MITIGATING

        self.is_recovery_branch = True
        self.stream = self.replay.stream_telemetry(
            "2020-06-08 16:05:00", "2020-06-08 17:00:00"
        )

        self.record_case_event(
            event_type=CaseEventType.ACTION,
            phase="MITIGATING",
            title="Safe Mode Simulated Intervention",
            detail="ActionGuard validated 5 criteria. Branching stream to post-maintenance historical segment.",
            actor="operator:dispatcher",
            source="ActionGuard",
            event_time=self.current_point.timestamp if self.current_point else None,
        )

        return {
            "action_id": "ACT-SM-001",
            "status": "ACTIVATED",
            "execution_mode": "SIMULATION_BRANCH",
            "target_state": "MITIGATING",
            "stream_branch": {
                "source": "METROPT-3_POST_MAINTENANCE",
                "offset_timestamp": "2020-06-08T16:05:00Z",
            },
        }

    def tick(self) -> Optional[TelemetryPoint]:
        """
        Advances the replay cursor by one telemetry sample (10 seconds).
        - If already RESOLVED: idempotent no-op.
        - If in degradation stream: evaluates detectors, evidence fusion, and decision engine.
        - If in recovery stream: transitions from MITIGATING to VERIFYING_RECOVERY on first recovery point,
          feeds point to RecoveryVerifier, and transitions to RESOLVED (health to HEALTHY) upon verification.
        """
        if self.lifecycle_state == IncidentLifecycleState.RESOLVED:
            return self.current_point

        if self.stream is None:
            return None

        try:
            pt = next(self.stream)
        except StopIteration:
            return None

        self.current_point = pt
        self.window.append(pt)
        if len(self.window) > 10:
            self.window.pop(0)

        # Branch 1: Post-maintenance recovery stream
        if self.is_recovery_branch:
            # First recovery tick: transition from MITIGATING to VERIFYING_RECOVERY
            if self.lifecycle_state == IncidentLifecycleState.MITIGATING:
                self.lifecycle_state = IncidentLifecycleState.VERIFYING_RECOVERY
                if self.active_incident:
                    self.active_incident.lifecycle_state = (
                        IncidentLifecycleState.VERIFYING_RECOVERY
                    )

            self.recovery_verifier.evaluate(pt)
            if self.recovery_verifier.is_verified:
                self.lifecycle_state = IncidentLifecycleState.RESOLVED
                self.asset_health = AssetHealthState.HEALTHY
                if self.active_incident:
                    self.active_incident.lifecycle_state = IncidentLifecycleState.RESOLVED
                    self.active_incident.health_state = AssetHealthState.HEALTHY
                    self.active_incident.updated_at = pt.timestamp
                self.record_case_event(
                    event_type=CaseEventType.RECOVERY,
                    phase="RESOLVED",
                    title="Recovery Criteria Verified (5/5 healthy LOADED observations)",
                    detail="Discharge valve pressure < 0.05 bar and oil temp < 67°C verified across 5 consecutive loaded observations.",
                    actor="system:recovery_verifier",
                    source="RecoveryVerifier",
                    event_time=pt.timestamp,
                )
            return pt

        # Branch 2: Degradation stream
        detector_results = [d.detect(self.window) for d in self.detectors]
        self.current_evidence_state = self.fusion.fuse(detector_results, pt)

        inc_ctx = (
            IncidentContext(
                active_incident_id=self.active_incident.incident_id,
                lifecycle_state=self.lifecycle_state,
            )
            if self.active_incident is not None
            else None
        )

        decision = self.decision_engine.evaluate(
            self.current_evidence_state, incident_context=inc_ctx
        )
        self.current_decision = decision
        self.asset_health = decision.asset_health
        self.operational_confidence = decision.operational_confidence

        # Exact state transitions:
        # 1. Onset at June 5 09:50 -> DETECTED
        if (
            decision.incident_action == IncidentAction.CREATE
            and self.active_incident is None
        ):
            self.active_incident = IncidentEvent(
                incident_id="APU-INC-20200605-01",
                asset_id="APU-COMP-01",
                created_at=pt.timestamp,
                updated_at=pt.timestamp,
                lifecycle_state=IncidentLifecycleState.DETECTED,
                health_state=decision.asset_health,
                operational_confidence=decision.operational_confidence,
                summary="Confirmed severe step degradation in DV_pressure with thermal stress drift.",
                evidence_chain=[self.current_evidence_state],
            )
            self.lifecycle_state = IncidentLifecycleState.DETECTED
            self.record_case_event(
                event_type=CaseEventType.DETECTION,
                phase="DETECTED",
                title="Confirmed degradation detected",
                detail="Severe step degradation in DV_pressure with thermal drift sustained across loaded observations. Case opened.",
                actor="system:detector",
                source="PressureAnomalyDetector",
                event_time=pt.timestamp,
            )

        # 2. ML Corroboration -> INVESTIGATING
        if self.lifecycle_state == IncidentLifecycleState.DETECTED and (
            decision.operational_confidence == OperationalConfidence.HIGH
            or decision.incident_action == IncidentAction.UPDATE_INVESTIGATING
        ):
            self.lifecycle_state = IncidentLifecycleState.INVESTIGATING
            if self.active_incident:
                self.active_incident.lifecycle_state = (
                    IncidentLifecycleState.INVESTIGATING
                )
                self.active_incident.operational_confidence = (
                    decision.operational_confidence
                )
                self.active_incident.updated_at = pt.timestamp
                self.active_incident.evidence_chain.append(
                    self.current_evidence_state
                )
            self.record_case_event(
                event_type=CaseEventType.CORROBORATION,
                phase="INVESTIGATING",
                title="Multivariate Isolation Forest Corroboration",
                detail="Isolation Forest exceeded threshold (score > 0.35) on 5 LOADED features. Mitigation recommended.",
                actor="system:ml",
                source="IsolationForestDetector",
                event_time=pt.timestamp,
            )

        return pt

    def jump_to_milestone(self, milestone_name: str) -> None:
        """
        Validates milestone, seeks stream until timestamp is reached.
        Allowed milestones: onset_0950, ml_corroborated_1015, lps_reactive_1942, post_maintenance_1605.
        """
        if milestone_name not in self.milestones:
            raise ValueError(
                f"Invalid milestone '{milestone_name}'. Allowed milestones: {list(self.milestones.keys())}"
            )

        target_ts_str = self.milestones[milestone_name]
        target_dt = pd.to_datetime(target_ts_str)

        # Handle post-maintenance recovery branch
        if milestone_name == "post_maintenance_1605":
            if not self.is_recovery_branch:
                if self.lifecycle_state == IncidentLifecycleState.DETECTED:
                    self.jump_to_milestone("ml_corroborated_1015")
                if self.lifecycle_state == IncidentLifecycleState.INVESTIGATING:
                    self.trigger_safe_mode()
                else:
                    self.is_recovery_branch = True
                    self.stream = self.replay.stream_telemetry(
                        "2020-06-08 16:05:00", "2020-06-08 17:00:00"
                    )
            while self.current_point is None or self.current_point.timestamp < target_dt:
                pt = self.tick()
                if pt is None:
                    break
            return

        # For degradation milestones:
        # If currently in recovery branch or cursor is past target_dt, reset first
        if self.is_recovery_branch or (
            self.current_point is not None and self.current_point.timestamp > target_dt
        ):
            self.reset()

        if milestone_name == "onset_0950":
            # Seek until onset transition occurs (>= 09:50 and state is DETECTED)
            while (
                self.current_point is None
                or self.current_point.timestamp < target_dt
                or self.lifecycle_state != IncidentLifecycleState.DETECTED
            ):
                pt = self.tick()
                if pt is None:
                    break
            return

        if milestone_name == "ml_corroborated_1015":
            # Seek until ML corroboration occurs (>= 10:15 and state is INVESTIGATING)
            while (
                self.current_point is None
                or self.current_point.timestamp < target_dt
                or self.lifecycle_state != IncidentLifecycleState.INVESTIGATING
            ):
                pt = self.tick()
                if pt is None:
                    break
            return

        # General seek until timestamp reached
        while self.current_point is None or self.current_point.timestamp < target_dt:
            pt = self.tick()
            if pt is None:
                break

    def get_incident_payload(self) -> Dict[str, Any]:
        """Returns the incident summary matching the Product API GET /api/incident schema."""
        incident_id = (
            self.active_incident.incident_id
            if self.active_incident
            else "APU-INC-20200605-01"
        )
        asset_id = "APU-COMP-01"
        lifecycle_state_val = (
            self.lifecycle_state.value
            if hasattr(self.lifecycle_state, "value")
            else str(self.lifecycle_state)
        )
        health_state_val = (
            self.asset_health.value
            if hasattr(self.asset_health, "value")
            else str(self.asset_health)
        )
        confidence_val = (
            self.operational_confidence.value
            if hasattr(self.operational_confidence, "value")
            else str(self.operational_confidence)
        )

        # Dynamic lead time derived from detection timestamp and verified LPS milestone timestamp
        actual_lps_dt = pd.to_datetime(self.milestones["lps_reactive_1942"])
        if self.active_incident and self.active_incident.created_at:
            actual_detection_dt = self.active_incident.created_at
        else:
            actual_detection_dt = pd.to_datetime(self.milestones["onset_0950"])

        delta = actual_lps_dt - actual_detection_dt
        lead_time_minutes = max(0, int(round(delta.total_seconds() / 60.0)))
        lead_hours = lead_time_minutes // 60
        lead_mins = lead_time_minutes % 60
        lead_time_formatted = f"{lead_hours}h {lead_mins:02d}m"

        if self.active_incident and self.active_incident.summary:
            summary = self.active_incident.summary
        elif self.current_decision and self.current_decision.reason:
            summary = self.current_decision.reason
        else:
            summary = "Confirmed severe step degradation in DV_pressure with thermal stress drift."

        return {
            "incident_id": incident_id,
            "asset_id": asset_id,
            "lifecycle_state": lifecycle_state_val,
            "asset_health": health_state_val,
            "operational_confidence": confidence_val,
            "lead_time": {
                "lead_time_minutes": lead_time_minutes,
                "lead_time_formatted": lead_time_formatted,
                "conventional_alert_timestamp": actual_lps_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "earliest_detection_timestamp": actual_detection_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
            "summary": summary,
        }

    def get_evidence_payload(self) -> Dict[str, Any]:
        """Returns the evidence pack matching the Product API GET /api/evidence schema."""
        incident_id = (
            self.active_incident.incident_id
            if self.active_incident
            else "APU-INC-20200605-01"
        )

        if self.current_evidence_state is None:
            return {
                "incident_id": incident_id,
                "regime": "LOADED",
                "evidence_pack": [],
                "persistence": {
                    "confirmed": False,
                    "recent_observations": 0,
                    "required_observations": 3,
                },
            }

        evidence_pack = []
        has_temporal_confirmed = False
        recent_observations = 0
        required_observations = 3

        for sig in self.current_evidence_state.signals:
            if sig.status == DetectorStatus.NORMAL or sig.evidence_code == EvidenceCode.NORMAL:
                continue

            if sig.detector_id == "temporal_persistence":
                has_temporal_confirmed = (
                    sig.evidence_code == EvidenceCode.TEMPORAL_STEP_CONFIRMED
                )
                if has_temporal_confirmed:
                    recent_observations = sig.provenance.get(
                        "recent_observations", sig.provenance.get("required_observations", 3)
                    )
                    required_observations = sig.provenance.get(
                        "required_observations", sig.provenance.get("required_cycles", 3)
                    )
                else:
                    recent_observations = sig.provenance.get("recent_observations", 0)
                    required_observations = sig.provenance.get(
                        "required_observations", sig.provenance.get("required_cycles", 3)
                    )
                evidence_pack.append(
                    {
                        "code": sig.evidence_code.value,
                        "signal_name": "Temporal Persistence Tracking",
                        "observed_value": sig.observed_value,
                        "baseline_value": 0.0,
                        "unit": "bar_diff",
                        "sigma_deviation": 0.0,
                        "status": "CONFIRMED" if has_temporal_confirmed else "TRIGGERED",
                        "is_primary": False,
                    }
                )
                continue

            if sig.detector_id == "pressure_anomaly":
                evidence_pack.append(
                    {
                        "code": sig.evidence_code.value,
                        "signal_name": "Discharge Valve Pressure",
                        "observed_value": sig.observed_value,
                        "baseline_value": sig.baseline_value,
                        "unit": "bar",
                        "sigma_deviation": sig.sigma_deviation,
                        "status": (
                            "CRITICAL"
                            if sig.evidence_code == EvidenceCode.PRESSURE_SEVERE
                            else "TRIGGERED"
                        ),
                        "is_primary": True,
                    }
                )
            elif sig.detector_id == "thermal_stress":
                evidence_pack.append(
                    {
                        "code": sig.evidence_code.value,
                        "signal_name": "Compressor Oil Temperature",
                        "observed_value": sig.observed_value,
                        "baseline_value": sig.baseline_value,
                        "unit": "°C",
                        "sigma_deviation": sig.sigma_deviation,
                        "status": (
                            "SEVERE"
                            if sig.evidence_code == EvidenceCode.THERMAL_STRESS_SEVERE
                            else "ELEVATED"
                        ),
                        "is_primary": False,
                    }
                )
            elif sig.detector_id == "isolation_forest":
                evidence_pack.append(
                    {
                        "code": sig.evidence_code.value,
                        "signal_name": "Multivariate Isolation Forest",
                        "observed_value": sig.observed_value,
                        "baseline_value": sig.baseline_value,
                        "unit": "score",
                        "sigma_deviation": None,
                        "status": "CORROBORATED",
                        "is_primary": False,
                    }
                )
            elif sig.detector_id == "reactive_lps":
                evidence_pack.append(
                    {
                        "code": sig.evidence_code.value,
                        "signal_name": "Low Pressure Switch",
                        "observed_value": sig.observed_value,
                        "baseline_value": sig.baseline_value,
                        "unit": "boolean",
                        "sigma_deviation": None,
                        "status": "CRITICAL",
                        "is_primary": False,
                    }
                )

        regime_val = (
            self.current_point.regime.value
            if self.current_point and self.current_point.regime
            else "LOADED"
        )

        return {
            "incident_id": incident_id,
            "regime": regime_val,
            "evidence_pack": evidence_pack,
            "persistence": {
                "confirmed": has_temporal_confirmed,
                "recent_observations": recent_observations,
                "required_observations": required_observations,
            },
        }

    def get_recovery_payload(self) -> Dict[str, Any]:
        """Returns the recovery tracking status matching GET /api/recovery schema."""
        incident_id = (
            self.active_incident.incident_id
            if self.active_incident
            else "APU-INC-20200605-01"
        )
        criteria = self.recovery_verifier.criteria
        latest_pt = self.current_point

        return {
            "incident_id": incident_id,
            "is_recovering": self.is_recovery_branch,
            "is_verified": self.recovery_verifier.is_verified,
            "consecutive_healthy_observations": self.recovery_verifier.consecutive_healthy_observations,
            "target_healthy_observations": criteria.target_healthy_observations,
            "latest_telemetry": {
                "dv_pressure_bar": (
                    round(latest_pt.dv_pressure_bar, 4) if latest_pt else 0.0
                ),
                "oil_temp_c": round(latest_pt.oil_temp_c, 2) if latest_pt else 0.0,
                "regime": (
                    latest_pt.regime.value
                    if latest_pt and latest_pt.regime
                    else "LOADED"
                ),
            },
            "criteria": {
                "dv_pressure_max": criteria.dv_pressure_max,
                "oil_temp_max": criteria.oil_temp_max,
                "required_regime": (
                    criteria.required_regime.value
                    if hasattr(criteria.required_regime, "value")
                    else str(criteria.required_regime)
                ),
            },
        }
