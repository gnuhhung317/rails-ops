import pytest
from src.engine.lifecycle import IncidentLifecycleManager
from src.domain.enums import IncidentLifecycleState, AssetHealthState
from src.domain.scenarios import FAILURE_3_SCENARIO


def test_no_active_case_in_initial_none_state():
    manager = IncidentLifecycleManager(scenario=FAILURE_3_SCENARIO)
    manager.reset()

    # Initial state must have zero active cases
    assert manager.has_active_case() is False
    assert manager.get_active_case() is None
    payload = manager.get_incident_payload()
    assert payload["incident_id"] is None or payload["lifecycle_state"] == "NONE"
    assert payload["lead_time"]["lead_time_formatted"] is None


def test_closed_case_projects_zero_active_cases():
    manager = IncidentLifecycleManager(scenario=FAILURE_3_SCENARIO)
    manager.reset()
    manager.jump_to_milestone("onset_0950")
    assert manager.has_active_case() is True

    # Trigger safe mode and verify recovery
    manager.jump_to_milestone("ml_corroborated_1015")
    manager.trigger_safe_mode()

    # Fast forward through recovery (up to 50 ticks)
    ticks = 0
    while ticks < 50 and not manager.recovery_verifier.is_verified:
        manager.tick()
        ticks += 1

    assert manager.recovery_verifier.is_verified is True

    # Close case with operator sign-off
    res = manager.close_case(operator_id="DISPATCHER-0941", notes="Verified recovery complete.")
    assert res["status"] == "CASE_CLOSED"

    # Invariant: Once closed, case is NOT active, active cases count is 0
    assert manager.has_active_case() is False
    assert manager.get_active_case() is None
    assert manager.lifecycle_state == IncidentLifecycleState.RESOLVED
    assert manager.asset_health == AssetHealthState.HEALTHY
