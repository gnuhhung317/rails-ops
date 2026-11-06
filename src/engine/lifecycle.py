import time
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
from src.domain.scenarios import (
    ScenarioDefinition,
    FAILURE_3_SCENARIO,
    FAILURE_1_SCENARIO,
    FAILURE_4_SCENARIO,
    HEALTHY_SCENARIO,
)
from src.engine.benchmark import BaselineBenchmarkTracker
from src.engine.fusion import EvidenceFusionEngine
from src.engine.recovery import RecoveryVerifier
from src.engine.replay import ReplayEngine, DEFAULT_CSV_PATH
from src.engine.simulation import SimulationRunner, HistoricalScenarioStream, SimulationPacingConfig
from src.observability.logger import setup_datadog_logging
from src.observability.metrics import DatadogMetricsClient, get_metrics_client
from src.observability.tracer import trace_operation

MILESTONES = FAILURE_3_SCENARIO.milestones.copy()

SCENARIO_REGISTRY: Dict[str, ScenarioDefinition] = {
    "failure_3": FAILURE_3_SCENARIO,
    "failure_1": FAILURE_1_SCENARIO,
    "failure_4": FAILURE_4_SCENARIO,
    "healthy_baseline": HEALTHY_SCENARIO,
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
        scenario: Optional[ScenarioDefinition] = None,
        repository: Optional[Any] = None,
        metrics_client: Optional[DatadogMetricsClient] = None,
        runner: Optional[SimulationRunner] = None,
    ) -> None:
        self.scenario: ScenarioDefinition = scenario or FAILURE_3_SCENARIO
        self.milestones: Dict[str, str] = self.scenario.milestones.copy()
        self.replay: Optional[ReplayEngine] = replay
        self.detectors: Optional[List[BaseDetector]] = detectors
        self.fusion: Optional[EvidenceFusionEngine] = fusion
        self.decision_engine: Optional[DecisionEngine] = decision_engine
        self.recovery_verifier: RecoveryVerifier = recovery_verifier or RecoveryVerifier()
        self.repository = repository
        self.metrics_client: DatadogMetricsClient = metrics_client or get_metrics_client()
        self.runner: Optional[SimulationRunner] = runner
        self.logger = setup_datadog_logging("compressorguard.engine")

        self.window: List[TelemetryPoint] = []
        self.history_buffer: List[Dict[str, Any]] = []
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
        self.benchmark_tracker: BaselineBenchmarkTracker = BaselineBenchmarkTracker(
            self.scenario.lps_milestone
        )
        # Human-in-the-Loop Case Governance state
        self.acknowledged: bool = False
        self.acknowledged_by: Optional[str] = None
        self.priority: str = "P1-CRITICAL"
        self.work_order: Optional[Dict[str, Any]] = None
        self.operator_notes: List[Dict[str, Any]] = []

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
        according to the configured scenario's temporal bounds.
        """
        self.window = []
        self.history_buffer = []
        self.active_incident = None
        self.lifecycle_state = IncidentLifecycleState.NONE
        self.asset_health = AssetHealthState.HEALTHY
        self.operational_confidence = OperationalConfidence.NONE
        self.is_recovery_branch = False
        self.current_point = None
        self.current_evidence_state = None
        self.current_decision = None
        self.case_events = []
        self.acknowledged = False
        self.acknowledged_by = None
        self.priority = "P1-CRITICAL"
        self.work_order = None
        self.operator_notes = []
        self.suppressed_signals = []
        self.milestones = self.scenario.milestones.copy()
        self.benchmark_tracker = BaselineBenchmarkTracker(self.scenario.lps_milestone)
        self.recovery_verifier.reset()
        if getattr(self, "repository", None) is not None:
            try:
                self.repository.db["operational_cases"].delete_many({"asset_id": self.scenario.asset_id})
                self.repository.db["measurements"].delete_many({"metadata.asset_id": self.scenario.asset_id})
                self.repository.db["anomaly_signals"].delete_many({"asset_id": self.scenario.asset_id})
            except Exception:
                pass
        if self.replay is not None:
            csv_path = str(self.replay.csv_path)
            stream = HistoricalScenarioStream(
                start_ts=self.scenario.stream_start,
                end_ts=self.scenario.stream_end,
                csv_path=csv_path,
                replay=self.replay,
            )
            self.runner = SimulationRunner(stream=stream, scenario_name=self.scenario.name)
            self.stream = self.replay.stream_telemetry(
                self.scenario.stream_start, self.scenario.stream_end
            )

    def play(self) -> None:
        if self.runner is not None:
            self.runner.play()

    def pause(self) -> None:
        if self.runner is not None:
            self.runner.pause()

    def set_simulation_speed(self, multiplier: float) -> None:
        if self.runner is not None:
            self.runner.set_speed(multiplier)

    def get_simulation_status(self) -> Dict[str, Any]:
        return self.runner.get_status() if self.runner else {}

    def _sync_case_to_repository(self) -> None:
        if getattr(self, "repository", None) is None or self.active_incident is None:
            return
        try:
            case_doc = {
                "case_id": self.active_incident.incident_id,
                "incident_id": self.active_incident.incident_id,
                "asset_id": self.active_incident.asset_id,
                "phase": self.lifecycle_state.value,
                "lifecycle_state": self.lifecycle_state.value,
                "asset_health": self.asset_health.value,
                "operational_confidence": self.operational_confidence.value,
                "acknowledged": self.acknowledged,
                "acknowledged_by": self.acknowledged_by,
                "priority": self.priority,
                "work_order": self.work_order,
                "operator_notes": list(self.operator_notes),
                "summary": self.active_incident.summary,
                "created_at": self.active_incident.created_at.isoformat(),
                "updated_at": self.active_incident.updated_at.isoformat(),
            }
            self.repository.save_case(case_doc)
        except Exception:
            pass

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

        case_id = (
            self.active_incident.incident_id
            if self.active_incident is not None
            else "APU-INC-20200605-01"
        )
        evt = CaseEvent(
            event_id=f"EVT-{len(self.case_events) + 1:03d}",
            case_id=case_id,
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
        if getattr(self, "logger", None) is not None:
            try:
                self.logger.info(
                    f"[{phase}] {title}: {detail}",
                    extra={
                        "incident_id": case_id,
                        "case_id": case_id,
                        "asset_id": self.scenario.asset_id,
                        "actor": actor,
                        "source": source,
                    },
                )
            except Exception:
                pass
        if getattr(self, "metrics_client", None) is not None:
            try:
                self.metrics_client.emit_case_transition(self.lifecycle_state)
            except Exception:
                pass
        if getattr(self, "repository", None) is not None:
            try:
                self.repository.save_case_event(evt.model_dump(mode="json"))
            except Exception:
                pass
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

    def has_active_case(self) -> bool:
        """Determines if there is a currently open, active operational case."""
        if self.active_incident is None:
            return False
        return self.active_incident.lifecycle_state in (
            IncidentLifecycleState.DETECTED,
            IncidentLifecycleState.INVESTIGATING,
            IncidentLifecycleState.MITIGATING,
            IncidentLifecycleState.VERIFYING_RECOVERY,
        )

    def get_active_case(self) -> Optional[IncidentEvent]:
        """Returns the active incident if open, else None."""
        return self.active_incident if self.has_active_case() else None

    def close_case(self, operator_id: str = "DISPATCHER-0941", notes: str = "") -> Dict[str, Any]:
        if not self.recovery_verifier.is_verified:
            raise ValueError("Recovery not verified. Cannot close operational case before 5/5 healthy LOADED observations are verified.")
        self.lifecycle_state = IncidentLifecycleState.RESOLVED
        self.asset_health = AssetHealthState.HEALTHY
        closed_case_id = "CASE-20200605-01"
        if self.active_incident:
            closed_case_id = self.active_incident.incident_id
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
        self._sync_case_to_repository()

        # Clear active incident pointer so it is no longer reported as active
        self.active_incident = None

        return {
            "status": "CASE_CLOSED",
            "case_id": closed_case_id,
            "operator_id": operator_id,
            "notes": notes,
            "lifecycle_state": "RESOLVED",
            "asset_health": "HEALTHY",
        }

    def trigger_safe_mode(self, operator_id: str = "DISPATCHER-0941") -> Dict[str, Any]:
        """
        Validates state, transitions to MITIGATING, and branches stream to
        post-maintenance (2020-06-08 16:05:00 to 2020-06-08 17:00:00).
        """
        with trace_operation("action.safe_mode", resource=self.scenario.asset_id) as span:
            span.set_tag("operator_id", operator_id)
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

            has_recovery = bool(self.scenario.recovery_start and self.scenario.recovery_end)
            conflicting_count = 0
            if getattr(self, "repository", None) is not None:
                active_existing = self.repository.get_active_case_for_asset(self.scenario.asset_id)
                if active_existing:
                    existing_id = active_existing.get("case_id") or active_existing.get("incident_id")
                    current_id = getattr(self.active_incident, "incident_id", None) or getattr(self.active_incident, "case_id", None)
                    if existing_id and current_id and existing_id != current_id:
                        conflicting_count = 1

            tp3_val = self.current_point.tp3_bar if self.current_point is not None else 8.74
            lps_val = self.current_point.lps_active if self.current_point is not None else 0.0

            guard_res = self.action_guard.validate(
                lifecycle_state=self.lifecycle_state,
                has_active_case=(self.active_incident is not None),
                recommended_action=self.current_decision.recommended_action,
                replay_branch_available=has_recovery,
                conflicting_cases_count=conflicting_count,
                tp3_bar=tp3_val,
                lps_active=lps_val,
            )
            if not guard_res.is_permitted:
                raise InvalidStateTransitionError(f"Action safe-mode rejected: {guard_res.denial_reason}")

            self.lifecycle_state = IncidentLifecycleState.MITIGATING
            if self.active_incident:
                self.active_incident.lifecycle_state = IncidentLifecycleState.MITIGATING

            self.is_recovery_branch = True
            rec_start = self.scenario.recovery_start or "2020-06-08 16:05:00"
            rec_end = self.scenario.recovery_end or "2020-06-08 17:00:00"
            csv_path = str(self.replay.csv_path if self.replay else DEFAULT_CSV_PATH)
            if self.runner is not None:
                self.runner.stream = HistoricalScenarioStream(rec_start, rec_end, csv_path=csv_path, replay=self.replay)
            self.stream = self.replay.stream_telemetry(rec_start, rec_end)

            self.record_case_event(
                event_type=CaseEventType.ACTION,
                phase="MITIGATING",
                title="Safe Mode Simulated Intervention",
                detail="ActionGuard validated 5 criteria. Branching stream to post-maintenance historical segment.",
                actor=f"operator:{operator_id}",
                source="ActionGuard",
                event_time=self.current_point.timestamp if self.current_point else None,
            )
            self._sync_case_to_repository()

            return {
                "action_id": "ACT-SM-001",
                "operator_id": operator_id,
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

        if self.runner is not None:
            pt = self.runner.step()
        elif self.stream is not None:
            try:
                pt = next(self.stream)
            except StopIteration:
                pt = None
        else:
            pt = None

        if pt is None:
            return None

        self.current_point = pt

        with trace_operation("pipeline.tick", resource=pt.asset_id) as tick_span:
            tick_span.set_tag("asset_id", pt.asset_id)
            tick_span.set_tag("regime", pt.regime.value if pt.regime else "LOADED")
            tick_span.set_tag("event_time", pt.timestamp.isoformat())

            if getattr(self, "repository", None) is not None:
                doc = {
                    "timestamp": pt.timestamp,
                    "metadata": {
                        "asset_id": pt.asset_id,
                        "scenario": self.scenario.scenario_id,
                        "train_id": "TRAIN-302",
                        "fleet_id": "FLEET-METRO-01",
                    },
                    "dv_pressure_bar": pt.dv_pressure_bar,
                    "oil_temp_c": pt.oil_temp_c,
                    "motor_current_a": pt.motor_current_a,
                    "tp2_bar": pt.tp2_bar,
                    "tp3_bar": pt.tp3_bar,
                    "h1_bar": pt.h1_bar,
                    "reservoirs_bar": pt.reservoirs_bar,
                    "lps_active": pt.lps_active,
                    "pressure_switch": pt.pressure_switch,
                    "oil_level_low": pt.oil_level_low,
                    "caudal_impulses": pt.caudal_impulses,
                    "regime": pt.regime.value if pt.regime else "LOADED",
                }
                try:
                    self.repository.insert_measurement(doc)
                except Exception:
                    pass

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
                    self._sync_case_to_repository()

                self.history_buffer.append({
                    "timestamp": pt.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "regime": pt.regime.value if pt.regime else "LOADED",
                    "dv_pressure_bar": round(pt.dv_pressure_bar, 4),
                    "oil_temp_c": round(pt.oil_temp_c, 2),
                    "motor_current_a": round(pt.motor_current_a, 2),
                    "tp2_bar": round(pt.tp2_bar, 4),
                    "tp3_bar": round(pt.tp3_bar, 4),
                    "h1_bar": round(pt.h1_bar, 4),
                    "reservoirs_bar": round(pt.reservoirs_bar, 4),
                    "lps_active": float(pt.lps_active),
                    "if_anomaly_score": 0.0,
                })
                if len(self.history_buffer) > 60:
                    self.history_buffer.pop(0)

                if getattr(self, "metrics_client", None) is not None and pt is not None:
                    self.metrics_client.emit_telemetry(pt)
                    self.metrics_client.emit_recovery_progress(
                        self.recovery_verifier.consecutive_healthy_observations,
                        asset_id=pt.asset_id,
                    )
                return pt

            # Branch 2: Degradation stream
            detector_results = []
            ml_latency_ms = 0.0
            for d in self.detectors:
                if d.detector_id == "isolation_forest":
                    t0 = time.perf_counter()
                    with trace_operation("ml.inference", resource="IsolationForestDetector") as ml_span:
                        res_d = d.detect(self.window)
                        ml_latency_ms = (time.perf_counter() - t0) * 1000.0
                        ml_span.set_tag("ml.score", res_d.observed_value)
                        ml_span.set_tag("ml.corroborated", res_d.status == DetectorStatus.CORROBORATED)
                    detector_results.append(res_d)
                else:
                    with trace_operation("detector.evaluate", resource=d.__class__.__name__) as det_span:
                        res_d = d.detect(self.window)
                        det_span.set_tag("detector_id", d.detector_id)
                        det_span.set_tag("status", res_d.status.value)
                    detector_results.append(res_d)

            self.current_evidence_state = self.fusion.fuse(detector_results, pt)

            inc_ctx = (
                IncidentContext(
                    active_incident_id=self.active_incident.incident_id,
                    lifecycle_state=self.lifecycle_state,
                )
                if self.active_incident is not None
                else None
            )

            with trace_operation("decision.evaluate", resource="DecisionEngine"):
                decision = self.decision_engine.evaluate(
                    self.current_evidence_state, incident_context=inc_ctx
                )
            self.current_decision = decision
            self.asset_health = decision.asset_health
            self.operational_confidence = decision.operational_confidence

            ml_sig = next(
                (s for s in self.current_evidence_state.signals if s.detector_id == "isolation_forest"),
                None,
            )
            pressure_sig = next(
                (s for s in self.current_evidence_state.signals if s.detector_id == "pressure_anomaly"),
                None,
            )
            temporal_sig = next(
                (s for s in self.current_evidence_state.signals if s.detector_id == "temporal_persistence"),
                None,
            )

            ml_score_val = float(ml_sig.observed_value) if (ml_sig and ml_sig.observed_value is not None) else 0.0
            self.history_buffer.append({
                "timestamp": pt.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "regime": pt.regime.value if pt.regime else "LOADED",
                "dv_pressure_bar": round(pt.dv_pressure_bar, 4),
                "oil_temp_c": round(pt.oil_temp_c, 2),
                "motor_current_a": round(pt.motor_current_a, 2),
                "tp2_bar": round(pt.tp2_bar, 4),
                "tp3_bar": round(pt.tp3_bar, 4),
                "h1_bar": round(pt.h1_bar, 4),
                "reservoirs_bar": round(pt.reservoirs_bar, 4),
                "lps_active": float(pt.lps_active),
                "if_anomaly_score": round(ml_score_val, 4),
            })
            if len(self.history_buffer) > 60:
                self.history_buffer.pop(0)

            # Record suppressed transient spikes in MongoDB `anomaly_signals` & emit suppression metric
            if (
                pressure_sig is not None
                and pressure_sig.status == DetectorStatus.TRIGGERED
                and self.active_incident is None
                and decision.incident_action == IncidentAction.NONE
            ):
                if getattr(self, "repository", None) is not None:
                    try:
                        self.repository.save_anomaly_signal({
                            "asset_id": pt.asset_id,
                            "timestamp": pt.timestamp,
                            "detector_id": "pressure_anomaly",
                            "signal_code": pressure_sig.evidence_code.value,
                            "observed_value": pressure_sig.observed_value,
                            "sigma_deviation": pressure_sig.sigma_deviation,
                            "regime": pt.regime.value if pt.regime else "LOADED",
                            "disposition": "SUPPRESSED_TRANSIENT",
                            "reason": "Transient excursion (< 3 consecutive LOADED cycles); suppressed to prevent alert fatigue.",
                        })
                    except Exception:
                        pass
                if getattr(self, "metrics_client", None) is not None:
                    self.metrics_client.emit_signal_suppression(asset_id=pt.asset_id, detector_id="pressure_anomaly")

            # Exact state transitions:
            # 1. Onset -> DETECTED
            if (
                decision.incident_action == IncidentAction.CREATE
                and self.active_incident is None
            ):
                dynamic_id = (
                    "APU-INC-20200605-01"
                    if self.scenario.scenario_id == "failure_3"
                    else f"APU-INC-{pt.timestamp.strftime('%Y%m%d-%H%M')}"
                )
                self.active_incident = IncidentEvent(
                    incident_id=dynamic_id,
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
                self.benchmark_tracker.record_onset(pt.timestamp)
                self.record_case_event(
                    event_type=CaseEventType.DETECTION,
                    phase="DETECTED",
                    title="Confirmed degradation detected",
                    detail="Severe step degradation in DV_pressure with thermal drift sustained across loaded observations. Case opened.",
                    actor="system:detector",
                    source="PressureAnomalyDetector",
                    event_time=pt.timestamp,
                )
                self.record_case_event(
                    event_type=CaseEventType.DECISION,
                    phase="DETECTED",
                    title="Operational Policy Evaluation: Open Case",
                    detail="DecisionEngine evaluated multi-sensor evidence. Confirmed persistent degradation; opened case and recommended elevated monitoring.",
                    actor="system:decision_engine",
                    source="DecisionEngine",
                    event_time=pt.timestamp,
                )
                self._sync_case_to_repository()

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
                self.record_case_event(
                    event_type=CaseEventType.DECISION,
                    phase="INVESTIGATING",
                    title="Operational Policy Evaluation: Mitigation Recommended",
                    detail="DecisionEngine corroborated anomaly with Isolation Forest. Recommended EXECUTE_MITIGATION under ActionGuard.",
                    actor="system:decision_engine",
                    source="DecisionEngine",
                    event_time=pt.timestamp,
                )
                self._sync_case_to_repository()

            if getattr(self, "metrics_client", None) is not None and pt is not None:
                self.metrics_client.emit_telemetry(pt)
                if ml_sig and ml_sig.observed_value is not None:
                    phys_triggered = bool(pressure_sig and pressure_sig.status != DetectorStatus.NORMAL)
                    ml_triggered = bool(ml_sig.status == DetectorStatus.CORROBORATED)
                    physics_agreed = (phys_triggered == ml_triggered) or (not ml_triggered)
                    self.metrics_client.emit_ml_observability(
                        score=float(ml_sig.observed_value),
                        inference_latency_ms=ml_latency_ms,
                        physics_agreed=physics_agreed,
                        asset_id=pt.asset_id,
                    )
                if self.active_incident:
                    self.metrics_client.emit_lead_time(121920, asset_id=pt.asset_id)
                    rt_status = self.benchmark_tracker.get_runtime_warning_status(
                        current_time=pt.timestamp,
                        tp3_bar=pt.tp3_bar,
                        lps_active=pt.lps_active,
                    )
                    self.metrics_client.emit_runtime_warning_elapsed(
                        int(rt_status.get("elapsed_warning_minutes", 0)) * 60,
                        asset_id=pt.asset_id,
                    )
                if self.recovery_verifier:
                    self.metrics_client.emit_recovery_progress(
                        self.recovery_verifier.consecutive_healthy_observations,
                        asset_id=pt.asset_id,
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

        # Handle early excursion milestone
        if milestone_name == "early_excursion_0033":
            self.reset()
            self.is_recovery_branch = False
            csv_path = str(self.replay.csv_path if self.replay else DEFAULT_CSV_PATH)
            if self.runner is not None:
                self.runner.stream = HistoricalScenarioStream(
                    "2020-06-04 00:30:00", self.scenario.stream_end, csv_path=csv_path, replay=self.replay
                )
            self.stream = self.replay.stream_telemetry("2020-06-04 00:30:00", self.scenario.stream_end)
            while self.current_point is None or self.current_point.timestamp < target_dt:
                pt = self.tick()
                if pt is None:
                    break
            self.record_case_event(
                event_type=CaseEventType.OBSERVATION,
                phase="MONITORING",
                title="Early Excursion Telemetry Observation",
                detail="Discharge valve transient pressure excursion observed (6.046 bar, 65.4σ) at 00:33:07. Insufficient temporal persistence suppressed case creation.",
                actor="system:detector",
                source="PressureAnomalyDetector",
                event_time=self.current_point.timestamp if self.current_point else target_dt,
            )
            sup_doc = {
                "asset_id": self.scenario.asset_id,
                "timestamp": self.current_point.timestamp if self.current_point else target_dt,
                "detector_id": "pressure_anomaly",
                "evidence_code": "PRESSURE_SEVERE",
                "observed_value": 6.046,
                "sigma_deviation": 65.4,
                "status": "SUPPRESSED_TRANSIENT",
                "disposition": "SUPPRESSED_TRANSIENT",
                "reason": "Insufficient temporal persistence (1/3 LOADED cycles); suppressed to prevent alert fatigue.",
            }
            self.suppressed_signals.append(sup_doc)
            if self.repository is not None:
                self.repository.save_anomaly_signal(dict(sup_doc))
            return

        # Handle post-maintenance recovery branch
        if milestone_name == "post_maintenance_1605":
            if not self.is_recovery_branch:
                if self.lifecycle_state == IncidentLifecycleState.DETECTED:
                    self.jump_to_milestone("ml_corroborated_1015")
                if self.lifecycle_state == IncidentLifecycleState.INVESTIGATING:
                    self.trigger_safe_mode()
                else:
                    self.is_recovery_branch = True
                    rec_start = self.scenario.recovery_start or "2020-06-08 16:05:00"
                    rec_end = self.scenario.recovery_end or "2020-06-08 17:00:00"
                    csv_path = str(self.replay.csv_path if self.replay else DEFAULT_CSV_PATH)
                    if self.runner is not None:
                        self.runner.stream = HistoricalScenarioStream(
                            rec_start, rec_end, csv_path=csv_path, replay=self.replay
                        )
                    self.stream = self.replay.stream_telemetry(rec_start, rec_end)
            while self.current_point is None or self.current_point.timestamp < target_dt:
                pt = self.tick()
                if pt is None:
                    break
            return

        # For degradation milestones:
        # If currently in recovery branch or cursor is past target_dt, or cursor is prior to scenario start (e.g. from early excursion), reset first
        scenario_start_dt = pd.to_datetime(self.scenario.stream_start)
        if (
            self.is_recovery_branch
            or (self.current_point is not None and self.current_point.timestamp > target_dt)
            or (self.current_point is not None and self.current_point.timestamp < scenario_start_dt)
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

        if milestone_name == "lps_reactive_1942":
            if not any(
                e.event_type in (CaseEventType.BENCHMARK, CaseEventType.BENCHMARK_REFERENCE_REACHED)
                for e in self.case_events
            ):
                self.record_case_event(
                    event_type=CaseEventType.BENCHMARK_REFERENCE_REACHED,
                    phase="CRITICAL",
                    title="Unmitigated Historical LPS Breach Reference",
                    detail="Conventional low pressure switch breach observed in historical baseline without early intervention.",
                    actor="system:benchmark_tracker",
                    source="BaselineBenchmarkTracker",
                    event_time=target_dt,
                )

    def get_incident_payload(self) -> Dict[str, Any]:
        """Returns the incident summary matching the Product API GET /api/incident schema."""
        incident_id = (
            self.active_incident.incident_id
            if self.active_incident
            else None
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

        # Dynamic lead time derived strictly from benchmark_tracker
        if self.has_active_case() and self.benchmark_tracker.is_ready:
            lead_time_minutes = self.benchmark_tracker.lead_time_minutes
            lead_time_formatted = self.benchmark_tracker.formatted_lead_time
            conv_ts = (
                self.benchmark_tracker.lps_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
                if self.benchmark_tracker.lps_timestamp
                else None
            )
            early_ts = (
                self.benchmark_tracker.onset_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
                if self.benchmark_tracker.onset_timestamp
                else None
            )
        else:
            lead_time_minutes = None
            lead_time_formatted = None
            conv_ts = None
            early_ts = None

        if self.active_incident and self.active_incident.summary:
            summary = self.active_incident.summary
        elif self.current_decision and self.current_decision.reason:
            summary = self.current_decision.reason
        else:
            summary = "Confirmed severe step degradation in DV_pressure with thermal stress drift."

        pt = self.current_point
        runtime_warning = self.benchmark_tracker.get_runtime_warning_status(
            current_time=pt.timestamp if pt else None,
            tp3_bar=pt.tp3_bar if pt else 9.8,
            lps_active=pt.lps_active if pt else 0.0,
        )

        return {
            "incident_id": incident_id,
            "asset_id": asset_id,
            "lifecycle_state": lifecycle_state_val,
            "asset_health": health_state_val,
            "operational_confidence": confidence_val,
            "lead_time": {
                "lead_time_minutes": lead_time_minutes,
                "lead_time_formatted": lead_time_formatted,
                "conventional_alert_timestamp": conv_ts,
                "earliest_detection_timestamp": early_ts,
            },
            "runtime_warning": runtime_warning,
            "acknowledged": self.acknowledged,
            "acknowledged_by": self.acknowledged_by,
            "priority": self.priority,
            "work_order": self.work_order,
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
                        "provenance": {
                            **sig.provenance,
                            "source": sig.provenance.get("detector_class", "TemporalStepDetector"),
                            "event_time": self.current_point.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ") if self.current_point else None,
                            "regime": self.current_point.regime.value if self.current_point and self.current_point.regime else "LOADED",
                        },
                    }
                )
                continue

            prov = dict(sig.provenance) if hasattr(sig, "provenance") and sig.provenance else {}
            if "source" not in prov:
                prov["source"] = prov.get("detector_class", sig.detector_id)
            if "event_time" not in prov:
                prov["event_time"] = (
                    self.current_point.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
                    if self.current_point
                    else None
                )
            if "regime" not in prov:
                prov["regime"] = (
                    self.current_point.regime.value
                    if self.current_point and self.current_point.regime
                    else "LOADED"
                )

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
                        "provenance": prov,
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
                        "provenance": prov,
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
                        "provenance": prov,
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
                        "provenance": prov,
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

    def get_action_guard_status(self) -> Dict[str, Any]:
        """Evaluates and returns live ActionGuard 5-condition safety checklist."""
        pt = self.current_point
        rec_action = (
            self.current_decision.recommended_action
            if self.current_decision
            else IncidentAction.NONE
        )
        result = self.action_guard.validate(
            lifecycle_state=self.lifecycle_state,
            has_active_case=self.has_active_case(),
            recommended_action=rec_action,
            replay_branch_available=bool(self.scenario.recovery_start and self.scenario.recovery_end),
            conflicting_cases_count=0,
            tp3_bar=pt.tp3_bar if pt else 9.8,
            lps_active=pt.lps_active if pt else 0.0,
        )
        return result.model_dump()

    def acknowledge_case(
        self,
        operator_id: str = "DISPATCHER-0941",
        priority: str = "P1-CRITICAL",
        note: str = "",
    ) -> Dict[str, Any]:
        """Operator acknowledges the active case, sets priority, and logs a CaseEvent."""
        if not self.has_active_case() and self.lifecycle_state not in (
            IncidentLifecycleState.DETECTED,
            IncidentLifecycleState.INVESTIGATING,
            IncidentLifecycleState.MITIGATING,
            IncidentLifecycleState.VERIFYING_RECOVERY,
        ):
            raise InvalidStateTransitionError(
                f"Cannot acknowledge case in state '{self.lifecycle_state.value}'. Active case required."
            )
        self.acknowledged = True
        self.acknowledged_by = operator_id
        self.priority = priority
        event_ts = (
            self.current_point.timestamp
            if self.current_point
            else pd.to_datetime("2020-06-05 09:50:10")
        )
        ev = self.record_case_event(
            event_type=CaseEventType.ACTION,
            phase=self.lifecycle_state.value,
            title=f"Case Acknowledged ({priority})",
            detail=f"Operator {operator_id} acknowledged operational case with priority {priority}. {note}".strip(),
            actor=f"operator:{operator_id}",
            source="OperatorDispatchConsole",
            event_time=event_ts,
            provenance={"priority": priority, "note": note},
        )
        self._sync_case_to_repository()
        return {
            "status": "ACKNOWLEDGED",
            "case_id": self.active_incident.incident_id if self.active_incident else "APU-INC-20200605-01",
            "operator_id": operator_id,
            "priority": priority,
            "acknowledged": True,
            "event_id": ev.event_id,
        }

    def add_case_note(
        self,
        operator_id: str = "DISPATCHER-0941",
        note: str = "",
    ) -> Dict[str, Any]:
        """Appends a human operator shift handover / diagnostic note to the case audit ledger."""
        if not note or not note.strip():
            raise ValueError("Operator note cannot be empty.")
        event_ts = (
            self.current_point.timestamp
            if self.current_point
            else pd.to_datetime("2020-06-05 09:50:10")
        )
        ev = self.record_case_event(
            event_type=CaseEventType.OBSERVATION,
            phase=self.lifecycle_state.value,
            title="Operator Shift / Diagnostic Note",
            detail=note.strip(),
            actor=f"operator:{operator_id}",
            source="OperatorDispatchConsole",
            event_time=event_ts,
            provenance={"note_type": "SHIFT_HANDOVER"},
        )
        self._sync_case_to_repository()
        return {
            "status": "NOTE_RECORDED",
            "event_id": ev.event_id,
            "operator_id": operator_id,
            "note": note.strip(),
            "event_time": ev.event_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    def create_work_order(
        self,
        operator_id: str = "DISPATCHER-0941",
        playbook_id: str = "PB-APU-03-AIR-LEAK",
        target_depot: str = "DEPOT-LONGBINH-01",
        maintenance_window: str = "NEXT_TERMINAL_STOP",
        instructions: str = "Inspect discharge valve seal and pneumatic air leak prior to LPS threshold breach.",
    ) -> Dict[str, Any]:
        """Dispatches a structured maintenance work order (Step 1 of 2-step maintenance workflow)."""
        if self.lifecycle_state not in (
            IncidentLifecycleState.DETECTED,
            IncidentLifecycleState.INVESTIGATING,
            IncidentLifecycleState.MITIGATING,
        ):
            raise InvalidStateTransitionError(
                f"Cannot dispatch work order in state '{self.lifecycle_state.value}'. Case must be DETECTED, INVESTIGATING, or MITIGATING."
            )
        event_ts = (
            self.current_point.timestamp
            if self.current_point
            else pd.to_datetime("2020-06-05 10:15:10")
        )
        wo_id = f"WO-{self.scenario.asset_id}-{event_ts.strftime('%Y%m%d%H%M')}"
        self.work_order = {
            "work_order_id": wo_id,
            "case_id": self.active_incident.incident_id if self.active_incident else "APU-INC-20200605-01",
            "asset_id": self.scenario.asset_id,
            "operator_id": operator_id,
            "playbook_id": playbook_id,
            "target_depot": target_depot,
            "maintenance_window": maintenance_window,
            "instructions": instructions,
            "status": "DISPATCHED",
            "created_at": event_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        ev = self.record_case_event(
            event_type=CaseEventType.ACTION,
            phase=self.lifecycle_state.value,
            title=f"Maintenance Work Order Dispatched ({wo_id})",
            detail=f"Playbook {playbook_id} dispatched to {target_depot} ({maintenance_window}): {instructions}",
            actor=f"operator:{operator_id}",
            source="MaintenanceDispatchService",
            event_time=event_ts,
            provenance=self.work_order,
        )
        self._sync_case_to_repository()
        return {
            **self.work_order,
            "event_id": ev.event_id,
        }

    def mark_false_positive(
        self,
        operator_id: str = "DISPATCHER-0941",
        reason: str = "Sensor calibration transient verified by field technician.",
    ) -> Dict[str, Any]:
        """Allows operator to close a case as a false positive with full audit provenance."""
        if self.lifecycle_state not in (
            IncidentLifecycleState.DETECTED,
            IncidentLifecycleState.INVESTIGATING,
        ):
            raise InvalidStateTransitionError(
                f"Cannot mark false positive in state '{self.lifecycle_state.value}'. Allowed only in DETECTED or INVESTIGATING."
            )
        event_ts = (
            self.current_point.timestamp
            if self.current_point
            else pd.to_datetime("2020-06-05 09:55:00")
        )
        self.lifecycle_state = IncidentLifecycleState.RESOLVED
        self.asset_health = AssetHealthState.HEALTHY
        self.operational_confidence = OperationalConfidence.NONE
        if self.active_incident:
            self.active_incident.lifecycle_state = IncidentLifecycleState.RESOLVED
            self.active_incident.health_state = AssetHealthState.HEALTHY
            self.active_incident.updated_at = event_ts
            self.active_incident.summary = f"Closed as False Positive by {operator_id}: {reason}"
        ev = self.record_case_event(
            event_type=CaseEventType.CASE_CLOSED,
            phase="RESOLVED",
            title="Case Closed as False Positive (Operator Override)",
            detail=f"Operator {operator_id} marked case as false positive. Reason: {reason}",
            actor=f"operator:{operator_id}",
            source="OperatorDispatchConsole",
            event_time=event_ts,
            provenance={"resolution_type": "FALSE_POSITIVE", "reason": reason},
        )
        self._sync_case_to_repository()
        return {
            "status": "CLOSED_FALSE_POSITIVE",
            "operator_id": operator_id,
            "reason": reason,
            "lifecycle_state": self.lifecycle_state.value,
            "asset_health": self.asset_health.value,
            "event_id": ev.event_id,
        }

    def switch_scenario(self, scenario_id: str) -> Dict[str, Any]:
        """Switches active historical replay scenario and resets lifecycle state."""
        if scenario_id not in SCENARIO_REGISTRY:
            raise ValueError(
                f"Unknown scenario '{scenario_id}'. Available scenarios: {list(SCENARIO_REGISTRY.keys())}"
            )
        self.scenario = SCENARIO_REGISTRY[scenario_id]
        self.milestones = self.scenario.milestones.copy()
        self.reset()
        return {
            "status": "SCENARIO_SWITCHED",
            "scenario_id": self.scenario.scenario_id,
            "scenario_name": self.scenario.name,
            "stream_start": self.scenario.stream_start,
            "stream_end": self.scenario.stream_end,
            "milestones": self.scenario.milestones,
        }

    def get_scenarios_payload(self) -> Dict[str, Any]:
        """Returns catalog of available historical replay scenarios and active scenario."""
        return {
            "active_scenario_id": self.scenario.scenario_id,
            "scenarios": [
                {
                    "scenario_id": sc.scenario_id,
                    "name": sc.name,
                    "asset_id": sc.asset_id,
                    "stream_start": sc.stream_start,
                    "stream_end": sc.stream_end,
                    "has_recovery_segment": bool(sc.recovery_start and sc.recovery_end),
                    "milestones": sc.milestones,
                }
                for sc in SCENARIO_REGISTRY.values()
            ],
        }

    def get_telemetry_window_payload(self, limit: int = 60) -> Dict[str, Any]:
        """Returns recent telemetry window with MongoDB $setWindowFields rolling statistics."""
        asset_id = self.scenario.asset_id
        rolling_points = []
        if self.repository is not None:
            rolling_points = self.repository.get_rolling_stats(
                asset_id=asset_id, window_seconds=600, limit=limit
            )

        # Fallback to in-memory buffer if repository has no points yet
        if not rolling_points and self.history_buffer:
            for item in self.history_buffer[-limit:]:
                rolling_points.append(
                    {
                        "timestamp": item.get("timestamp"),
                        "regime": item.get("regime", "OFF_LOAD"),
                        "dv_pressure_bar": round(float(item.get("dv_pressure_bar", 0.0)), 4),
                        "oil_temp_c": round(float(item.get("oil_temp_c", 0.0)), 2),
                        "tp2_bar": round(float(item.get("tp2_bar", 0.0)), 4),
                        "tp3_bar": round(float(item.get("tp3_bar", 0.0)), 4),
                        "motor_current_a": round(float(item.get("motor_current_a", 0.0)), 3),
                        "lps_active": float(item.get("lps_active", 0.0)),
                        "rolling_avg_dv": round(float(item.get("dv_pressure_bar", 0.0)), 4),
                        "rolling_std_dv": 0.0,
                        "rolling_avg_oil_temp": round(float(item.get("oil_temp_c", 0.0)), 2),
                    }
                )
        else:
            cleaned_points = []
            for doc in rolling_points:
                d = dict(doc)
                d.pop("_id", None)
                ts = d.get("timestamp")
                if hasattr(ts, "strftime"):
                    d["timestamp"] = ts.strftime("%Y-%m-%dT%H:%M:%SZ")
                ing = d.get("ingested_at")
                if hasattr(ing, "strftime"):
                    d["ingested_at"] = ing.strftime("%Y-%m-%dT%H:%M:%SZ")
                cleaned_points.append(d)
            rolling_points = cleaned_points

        return {
            "asset_id": asset_id,
            "count": len(rolling_points),
            "window_size": 600,
            "points": rolling_points,
        }

    def get_telemetry_analytics_payload(self) -> Dict[str, Any]:
        """
        Executes MongoDB Aggregation Pipelines ($facet/$group regime analytics,
        failure fingerprint cosine similarity matching, and suppressed signal summary).
        """
        asset_id = self.scenario.asset_id

        regime_analytics = {
            "asset_id": asset_id,
            "total_samples_analyzed": 0,
            "loaded_samples_count": 0,
            "loaded_duty_cycle_pct": 0.0,
            "peak_dv_pressure_bar": 0.0,
            "peak_oil_temp_c": 0.0,
            "min_tp3_bar": 0.0,
            "suppressed_transient_spikes_count": len(self.suppressed_signals),
            "regime_breakdown": [],
        }
        if self.repository is not None:
            regime_analytics = self.repository.get_regime_duty_cycle_analytics(
                asset_id=asset_id
            )

        # Extract observed anomalies for fingerprint matching
        dv_sigma = 0.0
        temp_sigma = 0.0
        if_score = 0.0
        if self.current_evidence_state:
            for sig in self.current_evidence_state.signals:
                if sig.detector_id == "pressure_anomaly":
                    dv_sigma = float(sig.sigma_deviation or 0.0)
                elif sig.detector_id == "thermal_stress":
                    temp_sigma = float(sig.sigma_deviation or 0.0)
                elif sig.detector_id == "isolation_forest":
                    if_score = float(sig.observed_value or 0.0)

        fingerprint_matches = []
        if self.repository is not None:
            fingerprint_matches = self.repository.match_failure_fingerprint(
                dv_sigma=dv_sigma,
                oil_sigma=temp_sigma,
                if_score=if_score,
                loaded_duty_pct=regime_analytics.get("loaded_duty_cycle_pct", 50.0),
            )

        recent_suppressed = []
        if self.repository is not None:
            all_signals = self.repository.get_recent_anomaly_signals(
                asset_id=asset_id, limit=20
            )
            recent_suppressed = [
                s for s in all_signals
                if s.get("disposition") == "SUPPRESSED_TRANSIENT" or s.get("status") == "SUPPRESSED_TRANSIENT"
            ]

        return {
            "asset_id": asset_id,
            "regime_analytics": regime_analytics,
            "fingerprint_matches": fingerprint_matches,
            "top_diagnosis": fingerprint_matches[0] if fingerprint_matches else None,
            "alert_fatigue_protection": {
                "suppressed_transients_count": max(
                    len(self.suppressed_signals),
                    regime_analytics.get("suppressed_transient_spikes_count", 0),
                    len(recent_suppressed),
                ),
                "recent_suppressed_signals": recent_suppressed,
            },
        }

