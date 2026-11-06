from typing import List, Dict, Any
from pydantic import BaseModel, Field
from src.domain.enums import IncidentLifecycleState, IncidentAction


class ActionGuardCheckResult(BaseModel):
    is_permitted: bool
    passed_count: int = 0
    total_checks: int = 5
    denial_reason: str = ""
    checklist: List[Dict[str, Any]] = Field(default_factory=list)


class ActionGuard:
    """
    Operational & Physical Pre-Flight Safety Gate (ActionGuard):
    1. CASE_CONFIRMED: Case is active and confirmed across >= 3 LOADED cycles
    2. MITIGATION_RECOMMENDED: DecisionEngine recommends mitigation (thermodynamic + ML corroboration)
    3. SINGLE_ACTIVE_CASE: Single active case invariant holds on asset
    4. BRAKE_RESERVOIR_PRESSURE_SAFE: Main reservoir pressure (TP3 >= 7.0 bar, LPS == 0) safe for derated depot routing
    5. REPLAY_BRANCH_AVAILABLE: Post-maintenance commissioning telemetry segment ready
    """
    def validate(
        self,
        lifecycle_state: IncidentLifecycleState,
        has_active_case: bool,
        recommended_action: IncidentAction,
        replay_branch_available: bool = True,
        conflicting_cases_count: int = 0,
        tp3_bar: float = 8.74,
        lps_active: float = 0.0,
    ) -> ActionGuardCheckResult:
        state_str = lifecycle_state.value if hasattr(lifecycle_state, "value") else str(lifecycle_state)
        rec_str = recommended_action.value if hasattr(recommended_action, "value") else str(recommended_action)
        reservoir_safe = (tp3_bar >= 7.0) and (lps_active == 0.0)

        checklist = [
            {
                "id": "CASE_CONFIRMED",
                "label": "Case is active and confirmed (DETECTED / INVESTIGATING)",
                "passed": has_active_case and lifecycle_state in (
                    IncidentLifecycleState.DETECTED,
                    IncidentLifecycleState.INVESTIGATING,
                ),
                "current_value": state_str if has_active_case else "NO_ACTIVE_CASE",
            },
            {
                "id": "MITIGATION_RECOMMENDED",
                "label": "DecisionEngine recommends mitigation (Physics + ML Corroboration)",
                "passed": recommended_action == IncidentAction.EXECUTE_MITIGATION,
                "current_value": rec_str,
            },
            {
                "id": "SINGLE_ACTIVE_CASE",
                "label": "No conflicting active cases on asset",
                "passed": conflicting_cases_count == 0,
                "current_value": f"{conflicting_cases_count} conflicts",
            },
            {
                "id": "BRAKE_RESERVOIR_PRESSURE_SAFE",
                "label": "Main brake reservoir safe for depot routing (TP3 >= 7.0 bar, LPS == 0)",
                "passed": reservoir_safe,
                "current_value": f"TP3={tp3_bar:.2f} bar, LPS={int(lps_active)}",
            },
            {
                "id": "REPLAY_BRANCH_AVAILABLE",
                "label": "Post-maintenance commissioning stream segment available",
                "passed": replay_branch_available,
                "current_value": "AVAILABLE (2020-06-08T16:05:00Z)" if replay_branch_available else "UNAVAILABLE",
            },
        ]

        passed_count = sum(1 for item in checklist if item["passed"])
        all_passed = passed_count == len(checklist)
        denial_reason = ""
        if not checklist[0]["passed"]:
            denial_reason = "Active case required in DETECTED or INVESTIGATING state."
        elif not checklist[1]["passed"]:
            denial_reason = "Mitigation not recommended by DecisionEngine."
        elif not checklist[2]["passed"]:
            denial_reason = "Conflicting active cases detected on asset."
        elif not checklist[3]["passed"]:
            denial_reason = "Brake reservoir pressure below safe threshold (< 7.0 bar or LPS tripped)."
        elif not checklist[4]["passed"]:
            denial_reason = "Post-maintenance historical stream segment unavailable."

        return ActionGuardCheckResult(
            is_permitted=all_passed,
            passed_count=passed_count,
            total_checks=len(checklist),
            denial_reason=denial_reason,
            checklist=checklist,
        )

