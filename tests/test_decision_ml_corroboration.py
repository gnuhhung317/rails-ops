from datetime import datetime
import pytest
from src.domain.enums import (
    OperatingRegime,
    AssetHealthState,
    IncidentAction,
    OperationalConfidence,
    DetectorStatus,
    Severity,
    EvidenceCode,
    IncidentLifecycleState,
)
from src.domain.models import EvidenceState, DetectorResult, IncidentContext
from src.engine.decision import DecisionEngine

def test_ml_cannot_create_case_on_its_own():
    engine = DecisionEngine()
    
    # EvidenceState containing ML trigger only (no physical severe pressure or temporal step)
    ml_only_state = EvidenceState(
        asset_id="APU-COMP-01",
        timestamp=datetime(2020, 6, 5, 9, 30, 0),
        regime=OperatingRegime.LOADED,
        signals=[
            DetectorResult(
                detector_id="isolation_forest",
                evidence_code=EvidenceCode.ML_CORROBORATED,
                status=DetectorStatus.CORROBORATED,
                severity=Severity.HIGH,
                observed_value=0.38,
                baseline_value=0.35,
            )
        ]
    )
    
    decision = engine.evaluate(ml_only_state, incident_context=None)
    # INVARIANT: ML CANNOT CREATE A CASE!
    assert decision.incident_action == IncidentAction.NONE
    assert decision.asset_health != AssetHealthState.CRITICAL

def test_ml_escalates_confidence_and_recommends_mitigation_when_case_active():
    engine = DecisionEngine()
    
    # Confirmed case already active, now ML corroborates
    ml_corroborated_state = EvidenceState(
        asset_id="APU-COMP-01",
        timestamp=datetime(2020, 6, 5, 10, 15, 0),
        regime=OperatingRegime.LOADED,
        signals=[
            DetectorResult(
                detector_id="pressure_anomaly",
                evidence_code=EvidenceCode.PRESSURE_SEVERE,
                status=DetectorStatus.CONFIRMED,
                severity=Severity.CRITICAL,
                observed_value=2.18,
                baseline_value=0.0,
                sigma_deviation=23.75,
            ),
            DetectorResult(
                detector_id="thermal_stress",
                evidence_code=EvidenceCode.THERMAL_STRESS_SEVERE,
                status=DetectorStatus.CONFIRMED,
                severity=Severity.HIGH,
                observed_value=74.97,
                baseline_value=60.0,
                sigma_deviation=5.71,
            ),
            DetectorResult(
                detector_id="isolation_forest",
                evidence_code=EvidenceCode.ML_CORROBORATED,
                status=DetectorStatus.CORROBORATED,
                severity=Severity.HIGH,
                observed_value=0.382,
                baseline_value=0.350,
            ),
        ]
    )
    
    inc_ctx = IncidentContext(
        active_incident_id="CASE-20200605-01",
        lifecycle_state=IncidentLifecycleState.DETECTED,
    )
    
    decision = engine.evaluate(ml_corroborated_state, incident_context=inc_ctx)
    assert decision.incident_action == IncidentAction.UPDATE_INVESTIGATING
    assert decision.operational_confidence == OperationalConfidence.HIGH
    assert decision.recommended_action == IncidentAction.EXECUTE_MITIGATION
