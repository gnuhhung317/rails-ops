import pytest
from src.engine.action_guard import ActionGuard
from src.engine.lifecycle import IncidentLifecycleManager
from src.domain.enums import IncidentLifecycleState, IncidentAction
from src.domain.scenarios import FAILURE_3_SCENARIO


def test_action_guard_rejects_when_recovery_stream_missing():
    guard = ActionGuard()
    # If scenario has no recovery bounds (e.g. healthy baseline)
    res = guard.validate(
        lifecycle_state=IncidentLifecycleState.INVESTIGATING,
        has_active_case=True,
        recommended_action=IncidentAction.EXECUTE_MITIGATION,
        replay_branch_available=False,
        conflicting_cases_count=0,
    )
    assert res.is_permitted is False
    assert "Post-maintenance historical stream segment unavailable" in res.denial_reason


def test_trigger_safe_mode_accepts_and_records_operator_identity():
    manager = IncidentLifecycleManager(scenario=FAILURE_3_SCENARIO)
    manager.reset()
    manager.jump_to_milestone("ml_corroborated_1015")

    res = manager.trigger_safe_mode(operator_id="DISPATCHER-0941")
    assert res["status"] == "ACTIVATED"
    assert res["operator_id"] == "DISPATCHER-0941"

    # Action event in timeline contains operator identity
    events = manager.get_case_events()
    action_event = next(e for e in events if e["event_type"] == "ACTION")
    assert action_event["actor"] == "operator:DISPATCHER-0941"
