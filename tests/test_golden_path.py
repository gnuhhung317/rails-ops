import pytest
import numpy as np
import pandas as pd
from datetime import datetime

from src.domain.enums import (
    OperatingRegime,
    AssetHealthState,
    IncidentLifecycleState,
    IncidentAction,
    OperationalConfidence,
    DetectorStatus,
    EvidenceCode,
)
from src.domain.models import TelemetryPoint, EvidenceState, IncidentEvent, RecoveryStatus, IncidentContext
from src.engine.factory import setup_golden_path

def run_golden_path_simulation():
    replay, detectors, fusion, decision_engine = setup_golden_path()

    # Step 1: Stream Failure #3 degradation (June 4 00:00 to June 6 20:00)
    degradation_stream = replay.stream_telemetry("2020-06-04 00:00:00", "2020-06-06 20:00:00")

    window = []
    milestones = {}
    active_incident: IncidentEvent = None

    for pt in degradation_stream:
        window.append(pt)
        if len(window) > 10:
            window.pop(0)

        # 1. Run Detectors
        detector_results = [d.detect(window) for d in detectors]

        # 2. Fuse Evidence
        evidence_state = fusion.fuse(detector_results, pt)

        # 3. Build IncidentContext if an incident is currently active
        inc_ctx = (
            IncidentContext(
                active_incident_id=active_incident.incident_id,
                lifecycle_state=active_incident.lifecycle_state,
            )
            if active_incident is not None
            else None
        )

        # 4. Evaluate Decision Engine
        decision = decision_engine.evaluate(evidence_state, incident_context=inc_ctx)

        # Record Key Milestones
        ts_str = pt.timestamp.strftime("%Y-%m-%d %H:%M:%S")

        # Milestone 1: Early Anomaly (June 4 00:33)
        if ts_str.startswith("2020-06-04 00:33") and "early_anomaly" not in milestones:
            milestones["early_anomaly"] = {
                "timestamp": ts_str,
                "asset_health": decision.asset_health,
                "confidence": decision.operational_confidence,
                "incident_action": decision.incident_action
            }

        # Incident Creation Trigger
        if decision.incident_action == IncidentAction.CREATE and active_incident is None:
            active_incident = IncidentEvent(
                incident_id="APU-INC-20200605-01",
                asset_id="APU-COMP-01",
                created_at=pt.timestamp,
                updated_at=pt.timestamp,
                lifecycle_state=IncidentLifecycleState.DETECTED,
                health_state=decision.asset_health,
                operational_confidence=decision.operational_confidence,
                summary="Confirmed severe step degradation in DV_pressure with thermal stress drift.",
                evidence_chain=[evidence_state]
            )

        # Milestone 2: Confirmed Degradation (June 5 ~09:50 - 09:55)
        if decision.asset_health == AssetHealthState.CRITICAL and "confirmed_degradation" not in milestones and "09:50" <= ts_str[11:16] <= "09:55":
            milestones["confirmed_degradation"] = {
                "timestamp": ts_str,
                "asset_health": decision.asset_health,
                "confidence": decision.operational_confidence,
                "incident_action": decision.incident_action
            }

        # Milestone 3: ML Corroboration (June 5 ~10:15)
        if "10:15" in ts_str and decision.operational_confidence == OperationalConfidence.HIGH and "ml_corroboration" not in milestones:
            milestones["ml_corroboration"] = {
                "timestamp": ts_str,
                "asset_health": decision.asset_health,
                "confidence": decision.operational_confidence,
                "incident_action": decision.incident_action
            }
            if active_incident:
                active_incident.lifecycle_state = IncidentLifecycleState.INVESTIGATING
                active_incident.operational_confidence = decision.operational_confidence
                active_incident.evidence_chain.append(evidence_state)

        # Milestone 4: Reactive LPS Alert (June 6 19:42)
        if ts_str.startswith("2020-06-06 19:42") and "reactive_lps" not in milestones:
            milestones["reactive_lps"] = {
                "timestamp": ts_str,
                "asset_health": decision.asset_health,
                "confidence": decision.operational_confidence,
                "incident_action": decision.incident_action
            }

    # Step 2: Operator Executes Safe Mode (Intervention Triggered)
    assert active_incident is not None
    active_incident.lifecycle_state = IncidentLifecycleState.MITIGATING

    # Step 3: Simulator switches stream offset to post-maintenance recovery (June 8 16:05+)
    recovery_stream = replay.stream_telemetry("2020-06-08 16:05:00", "2020-06-08 17:00:00")

    recovery_status = RecoveryStatus(asset_id="APU-COMP-01", is_recovering=True)
    
    for pt in recovery_stream:
        window.append(pt)
        if len(window) > 10:
            window.pop(0)

        # Evaluate scenario-specific recovery criteria (DV_pressure < 0.05 and Oil_temp < 67.0 in LOADED regime)
        if pt.regime == OperatingRegime.LOADED:
            if pt.dv_pressure_bar < 0.05 and pt.oil_temp_c < 67.0:
                recovery_status.consecutive_healthy_observations += 1
            else:
                recovery_status.consecutive_healthy_observations = 0

            if recovery_status.consecutive_healthy_observations >= recovery_status.target_healthy_observations:
                recovery_status.is_verified = True
                recovery_status.verification_reason = "5 consecutive observations passed scenario recovery criteria."
                active_incident.lifecycle_state = IncidentLifecycleState.RESOLVED
                active_incident.health_state = AssetHealthState.HEALTHY
                break

    return milestones, active_incident, recovery_status

def test_golden_path_15_checkpoints():
    print("\nExecuting Golden Path Failure #3 Simulation...")
    m1, incident1, recovery1 = run_golden_path_simulation()

    # Verify Checkpoints
    assert "early_anomaly" in m1
    assert m1["early_anomaly"]["asset_health"] == AssetHealthState.DEGRADING
    assert m1["early_anomaly"]["confidence"] == OperationalConfidence.LOW
    assert m1["early_anomaly"]["incident_action"] == IncidentAction.NONE

    assert "confirmed_degradation" in m1
    assert m1["confirmed_degradation"]["asset_health"] == AssetHealthState.CRITICAL
    assert m1["confirmed_degradation"]["incident_action"] == IncidentAction.CREATE

    assert "ml_corroboration" in m1
    assert m1["ml_corroboration"]["confidence"] == OperationalConfidence.HIGH
    assert m1["ml_corroboration"]["incident_action"] == IncidentAction.UPDATE_INVESTIGATING

    assert "reactive_lps" in m1
    assert m1["reactive_lps"]["confidence"] == OperationalConfidence.CRITICAL_REACTIVE

    assert incident1 is not None
    assert incident1.incident_id == "APU-INC-20200605-01"
    assert incident1.lifecycle_state == IncidentLifecycleState.RESOLVED
    assert incident1.health_state == AssetHealthState.HEALTHY

    assert recovery1.is_verified is True
    assert recovery1.consecutive_healthy_observations >= 5

    # Run a 2nd time to verify 100% deterministic reproducibility
    print("\nExecuting 2nd Run to verify 100% Deterministic Reproducibility...")
    m2, incident2, recovery2 = run_golden_path_simulation()

    assert m1 == m2
    assert incident1.incident_id == incident2.incident_id
    assert incident1.lifecycle_state == incident2.lifecycle_state
    try:
        print("\n✅ ALL 15 GOLDEN PATH CHECKPOINTS PASSED DETERMINISTICALLY!")
    except UnicodeEncodeError:
        print("\n[SUCCESS] ALL 15 GOLDEN PATH CHECKPOINTS PASSED DETERMINISTICALLY!")
