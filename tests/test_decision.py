from datetime import datetime
import pytest

from src.domain.enums import (
    OperatingRegime,
    AssetHealthState,
    IncidentAction,
    IncidentLifecycleState,
    OperationalConfidence,
    DetectorStatus,
    Severity,
    EvidenceCode,
)
from src.domain.models import EvidenceState, DetectorResult, IncidentContext
from src.engine.decision import DecisionEngine

def test_decision_healthy():
    engine = DecisionEngine()
    state = EvidenceState(
        asset_id="APU-COMP-01",
        timestamp=datetime.now(),
        regime=OperatingRegime.LOADED,
        signals=[]
    )
    decision = engine.evaluate(state)
    assert decision.asset_health == AssetHealthState.HEALTHY
    assert decision.incident_action == IncidentAction.NONE
    assert decision.operational_confidence == OperationalConfidence.NONE

def test_decision_early_warning():
    engine = DecisionEngine()
    state = EvidenceState(
        asset_id="APU-COMP-01",
        timestamp=datetime.now(),
        regime=OperatingRegime.LOADED,
        signals=[
            DetectorResult(
                detector_id="pressure_anomaly",
                evidence_code=EvidenceCode.PRESSURE_ELEVATED,
                status=DetectorStatus.TRIGGERED,
                severity=Severity.LOW,
                observed_value=0.6,
                baseline_value=-0.0164,
                sigma_deviation=6.6
            )
        ]
    )
    decision = engine.evaluate(state)
    assert decision.asset_health == AssetHealthState.DEGRADING
    assert decision.incident_action == IncidentAction.NONE
    assert decision.operational_confidence == OperationalConfidence.LOW

def test_decision_incident_created_no_prior_incident():
    engine = DecisionEngine()
    state = EvidenceState(
        asset_id="APU-COMP-01",
        timestamp=datetime.now(),
        regime=OperatingRegime.LOADED,
        signals=[
            DetectorResult(
                detector_id="pressure_anomaly",
                evidence_code=EvidenceCode.PRESSURE_SEVERE,
                status=DetectorStatus.TRIGGERED,
                severity=Severity.HIGH,
                observed_value=2.4
            ),
            DetectorResult(
                detector_id="thermal_stress",
                evidence_code=EvidenceCode.THERMAL_STRESS_ELEVATED,
                status=DetectorStatus.TRIGGERED,
                severity=Severity.MEDIUM,
                observed_value=71.5
            ),
            DetectorResult(
                detector_id="temporal_persistence",
                evidence_code=EvidenceCode.TEMPORAL_STEP_CONFIRMED,
                status=DetectorStatus.CONFIRMED,
                severity=Severity.HIGH,
                observed_value=2.4
            )
        ]
    )
    decision = engine.evaluate(state, incident_context=None)
    assert decision.asset_health == AssetHealthState.CRITICAL
    assert decision.incident_action == IncidentAction.CREATE
    assert decision.operational_confidence == OperationalConfidence.MEDIUM

def test_decision_incident_tracking_with_active_incident():
    engine = DecisionEngine()
    state = EvidenceState(
        asset_id="APU-COMP-01",
        timestamp=datetime.now(),
        regime=OperatingRegime.LOADED,
        signals=[
            DetectorResult(
                detector_id="pressure_anomaly",
                evidence_code=EvidenceCode.PRESSURE_SEVERE,
                status=DetectorStatus.TRIGGERED,
                severity=Severity.HIGH
            ),
            DetectorResult(
                detector_id="thermal_stress",
                evidence_code=EvidenceCode.THERMAL_STRESS_ELEVATED,
                status=DetectorStatus.TRIGGERED,
                severity=Severity.MEDIUM
            ),
            DetectorResult(
                detector_id="temporal_persistence",
                evidence_code=EvidenceCode.TEMPORAL_STEP_CONFIRMED,
                status=DetectorStatus.CONFIRMED,
                severity=Severity.HIGH
            )
        ]
    )
    ctx = IncidentContext(
        active_incident_id="APU-INC-20200605-01",
        lifecycle_state=IncidentLifecycleState.DETECTED
    )
    decision = engine.evaluate(state, incident_context=ctx)
    assert decision.asset_health == AssetHealthState.CRITICAL
    # Incident already active -> do not duplicate CREATE
    assert decision.incident_action == IncidentAction.NONE
    assert decision.operational_confidence == OperationalConfidence.MEDIUM

def test_decision_high_confidence_investigating_with_ml():
    engine = DecisionEngine()
    state = EvidenceState(
        asset_id="APU-COMP-01",
        timestamp=datetime.now(),
        regime=OperatingRegime.LOADED,
        signals=[
            DetectorResult(
                detector_id="pressure_anomaly",
                evidence_code=EvidenceCode.PRESSURE_SEVERE,
                status=DetectorStatus.TRIGGERED,
                severity=Severity.HIGH
            ),
            DetectorResult(
                detector_id="thermal_stress",
                evidence_code=EvidenceCode.THERMAL_STRESS_SEVERE,
                status=DetectorStatus.TRIGGERED,
                severity=Severity.HIGH
            ),
            DetectorResult(
                detector_id="isolation_forest",
                evidence_code=EvidenceCode.ML_CORROBORATED,
                status=DetectorStatus.CORROBORATED,
                severity=Severity.HIGH,
                observed_value=0.38,
                baseline_value=0.35
            )
        ]
    )
    ctx = IncidentContext(
        active_incident_id="APU-INC-20200605-01",
        lifecycle_state=IncidentLifecycleState.DETECTED
    )
    decision = engine.evaluate(state, incident_context=ctx)
    assert decision.asset_health == AssetHealthState.CRITICAL
    assert decision.incident_action == IncidentAction.UPDATE_INVESTIGATING
    assert decision.operational_confidence == OperationalConfidence.HIGH

def test_decision_reactive_lps():
    engine = DecisionEngine()
    state = EvidenceState(
        asset_id="APU-COMP-01",
        timestamp=datetime.now(),
        regime=OperatingRegime.LOADED,
        signals=[
            DetectorResult(
                detector_id="reactive_lps",
                evidence_code=EvidenceCode.LPS_TRIGGERED,
                status=DetectorStatus.TRIGGERED,
                severity=Severity.HIGH
            )
        ]
    )
    ctx = IncidentContext(
        active_incident_id="APU-INC-20200605-01",
        lifecycle_state=IncidentLifecycleState.INVESTIGATING
    )
    decision = engine.evaluate(state, incident_context=ctx)
    assert decision.asset_health == AssetHealthState.CRITICAL
    assert decision.incident_action == IncidentAction.UPDATE_INVESTIGATING
    assert decision.operational_confidence == OperationalConfidence.CRITICAL_REACTIVE


@pytest.mark.parametrize("lifecycle_state", [
    IncidentLifecycleState.RESOLVED,
    IncidentLifecycleState.FAILED,
    IncidentLifecycleState.ESCALATED,
])
def test_decision_inactive_states_allow_new_incident_creation(lifecycle_state):
    engine = DecisionEngine()
    state = EvidenceState(
        asset_id="APU-COMP-01",
        timestamp=datetime.now(),
        regime=OperatingRegime.LOADED,
        signals=[
            DetectorResult(
                detector_id="pressure_anomaly",
                evidence_code=EvidenceCode.PRESSURE_SEVERE,
                status=DetectorStatus.TRIGGERED,
                severity=Severity.HIGH,
                observed_value=2.5,
            ),
            DetectorResult(
                detector_id="thermal_stress",
                evidence_code=EvidenceCode.THERMAL_STRESS_ELEVATED,
                status=DetectorStatus.TRIGGERED,
                severity=Severity.MEDIUM,
            ),
            DetectorResult(
                detector_id="temporal_persistence",
                evidence_code=EvidenceCode.TEMPORAL_STEP_CONFIRMED,
                status=DetectorStatus.CONFIRMED,
                severity=Severity.HIGH,
            ),
        ]
    )
    ctx = IncidentContext(
        active_incident_id="APU-INC-20200605-01",
        lifecycle_state=lifecycle_state
    )
    dec = engine.evaluate(state, incident_context=ctx)
    assert dec.incident_action == IncidentAction.CREATE

