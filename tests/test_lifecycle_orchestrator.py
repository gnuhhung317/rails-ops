import pytest
from src.domain.enums import (
    IncidentLifecycleState,
    AssetHealthState,
    EvidenceCode,
    IncidentAction,
)
from src.engine.lifecycle import IncidentLifecycleManager, InvalidStateTransitionError


def test_exact_state_transitions_and_branching():
    manager = IncidentLifecycleManager()
    manager.reset()

    # Pre-onset initial state
    assert manager.lifecycle_state == IncidentLifecycleState.NONE

    # Invariant: Calling trigger_safe_mode() when in initial state NONE raises InvalidStateTransitionError
    with pytest.raises(InvalidStateTransitionError):
        manager.trigger_safe_mode()

    # 1. Onset at June 5 09:50 -> DETECTED
    manager.jump_to_milestone("onset_0950")
    assert manager.lifecycle_state == IncidentLifecycleState.DETECTED

    # Invariant: evidence_payload extracts real engine values (observed_value > 2.0 bar, sigma > 20.0)
    ev_payload = manager.get_evidence_payload()
    assert ev_payload is not None
    assert "evidence_pack" in ev_payload

    # Signal 1: Pressure anomaly
    pressure_sig = next(
        (s for s in ev_payload["evidence_pack"] if "PRESSURE" in s["code"]),
        None,
    )
    assert pressure_sig is not None, "Expected pressure anomaly signal in evidence pack"
    assert (
        pressure_sig["observed_value"] > 2.0
    ), f"Expected observed_value > 2.0 bar, got {pressure_sig['observed_value']}"
    assert (
        pressure_sig["sigma_deviation"] > 20.0
    ), f"Expected sigma_deviation > 20.0, got {pressure_sig['sigma_deviation']}"
    assert pressure_sig["is_primary"] is True
    assert pressure_sig["unit"] == "bar"

    # Signal 2: Temporal persistence signal is included in evidence_pack
    temporal_sig = next(
        (s for s in ev_payload["evidence_pack"] if s["code"] == EvidenceCode.TEMPORAL_STEP_CONFIRMED.value),
        None,
    )
    assert temporal_sig is not None, "Expected TEMPORAL_STEP_CONFIRMED in evidence pack"
    assert temporal_sig["signal_name"] == "Temporal Persistence Tracking"
    assert temporal_sig["observed_value"] > 2.0
    assert temporal_sig["baseline_value"] == 0.0
    assert temporal_sig["unit"] == "bar_diff"
    assert temporal_sig["sigma_deviation"] == 0.0
    assert temporal_sig["status"] == "CONFIRMED"
    assert temporal_sig["is_primary"] is False

    # Check persistence block using observation terminology
    assert "persistence" in ev_payload
    assert ev_payload["persistence"]["confirmed"] is True
    assert ev_payload["persistence"]["recent_observations"] == 3
    assert ev_payload["persistence"]["required_observations"] == 3

    # Verify incident payload at DETECTED: dynamically derived lead time
    inc_payload = manager.get_incident_payload()
    assert inc_payload["incident_id"] == "APU-INC-20200605-01"
    assert inc_payload["lifecycle_state"] == IncidentLifecycleState.DETECTED.value
    assert inc_payload["lead_time"]["lead_time_formatted"] == "33h 52m"
    assert inc_payload["lead_time"]["lead_time_minutes"] == 2032
    assert inc_payload["lead_time"]["conventional_alert_timestamp"] == "2020-06-06T19:42:19Z"
    assert inc_payload["lead_time"]["earliest_detection_timestamp"] == "2020-06-05T09:50:39Z"

    # 2. ML Corroboration at June 5 10:15 -> INVESTIGATING
    manager.jump_to_milestone("ml_corroborated_1015")
    assert manager.lifecycle_state == IncidentLifecycleState.INVESTIGATING
    inc_payload = manager.get_incident_payload()
    assert inc_payload["lifecycle_state"] == IncidentLifecycleState.INVESTIGATING.value

    # Invariant: Evidence pack contains ML_CORROBORATED code and status CORROBORATED
    ev_payload_1015 = manager.get_evidence_payload()
    assert ev_payload_1015 is not None
    assert "evidence_pack" in ev_payload_1015
    ml_sig = next(
        (s for s in ev_payload_1015["evidence_pack"] if s["code"] == EvidenceCode.ML_CORROBORATED.value),
        None,
    )
    assert ml_sig is not None, "Expected ML_CORROBORATED signal in evidence pack at ml_corroborated_1015"
    assert ml_sig["status"] == "CORROBORATED"

    # 3. Safe Mode trigger -> MITIGATING
    safe_mode_res = manager.trigger_safe_mode()
    assert safe_mode_res["status"] == "ACTIVATED"
    assert safe_mode_res["execution_mode"] == "SIMULATION_BRANCH"
    assert manager.lifecycle_state == IncidentLifecycleState.MITIGATING

    # Invariant: Calling trigger_safe_mode() when in MITIGATING raises InvalidStateTransitionError
    with pytest.raises(InvalidStateTransitionError):
        manager.trigger_safe_mode()

    # 4. First recovery tick -> VERIFYING_RECOVERY
    pt = manager.tick()
    assert pt is not None
    assert manager.lifecycle_state == IncidentLifecycleState.VERIFYING_RECOVERY

    # Invariant: Calling trigger_safe_mode() when in VERIFYING_RECOVERY raises InvalidStateTransitionError
    with pytest.raises(InvalidStateTransitionError):
        manager.trigger_safe_mode()

    # 5. 5 healthy observations verified by RecoveryVerifier -> RESOLVED
    ticks_done = 0
    while manager.lifecycle_state != IncidentLifecycleState.RESOLVED and ticks_done < 100:
        manager.tick()
        ticks_done += 1

    assert manager.lifecycle_state == IncidentLifecycleState.RESOLVED
    assert manager.asset_health == AssetHealthState.HEALTHY

    # Invariant: Calling trigger_safe_mode() when in RESOLVED raises InvalidStateTransitionError
    with pytest.raises(InvalidStateTransitionError):
        manager.trigger_safe_mode()

    # Additional tick when already RESOLVED is a no-op idempotent
    pt_after = manager.tick()
    assert manager.lifecycle_state == IncidentLifecycleState.RESOLVED
    assert manager.asset_health == AssetHealthState.HEALTHY

    # Verify final recovery payload
    rec_payload = manager.get_recovery_payload()
    assert rec_payload["is_verified"] is True
    assert rec_payload["consecutive_healthy_observations"] >= 5


def test_invalid_milestone_raises_error():
    manager = IncidentLifecycleManager()
    with pytest.raises(ValueError):
        manager.jump_to_milestone("invalid_milestone_key")


def test_trigger_safe_mode_in_initial_state_none_raises_error():
    manager = IncidentLifecycleManager()
    manager.reset()
    assert manager.lifecycle_state == IncidentLifecycleState.NONE
    with pytest.raises(InvalidStateTransitionError):
        manager.trigger_safe_mode()


def test_safe_mode_rejected_when_not_recommended_by_decision_engine():
    manager = IncidentLifecycleManager()
    manager.reset()
    manager.jump_to_milestone("onset_0950")
    assert manager.lifecycle_state == IncidentLifecycleState.DETECTED
    # Decision at onset does not recommend mitigation yet
    assert manager.current_decision.recommended_action != IncidentAction.EXECUTE_MITIGATION
    with pytest.raises(InvalidStateTransitionError, match="not recommended mitigation"):
        manager.trigger_safe_mode()

