import pytest
from src.domain.enums import IncidentLifecycleState, IncidentAction
from src.engine.action_guard import ActionGuard, ActionGuardCheckResult

def test_action_guard_five_criteria_validation():
    guard = ActionGuard()
    
    # 1. Rejects if case is not in valid phase
    res_invalid_phase = guard.validate(
        lifecycle_state=IncidentLifecycleState.NONE,
        has_active_case=False,
        recommended_action=IncidentAction.EXECUTE_MITIGATION,
        replay_branch_available=True,
    )
    assert res_invalid_phase.is_permitted is False
    assert "Active case required" in res_invalid_phase.denial_reason

    # 2. Rejects if mitigation not recommended by DecisionEngine
    res_no_rec = guard.validate(
        lifecycle_state=IncidentLifecycleState.DETECTED,
        has_active_case=True,
        recommended_action=IncidentAction.NONE,
        replay_branch_available=True,
    )
    assert res_no_rec.is_permitted is False
    assert "Mitigation not recommended" in res_no_rec.denial_reason

    # 3. Permits when all 5 criteria satisfied
    res_valid = guard.validate(
        lifecycle_state=IncidentLifecycleState.INVESTIGATING,
        has_active_case=True,
        recommended_action=IncidentAction.EXECUTE_MITIGATION,
        replay_branch_available=True,
    )
    assert res_valid.is_permitted is True
    assert len(res_valid.checklist) == 5
    assert all(item["passed"] for item in res_valid.checklist)
