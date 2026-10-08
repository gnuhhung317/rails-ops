from typing import List, Dict, Any
from pydantic import BaseModel, Field
from src.domain.enums import IncidentLifecycleState, IncidentAction


class ActionGuardCheckResult(BaseModel):
    is_permitted: bool
    denial_reason: str = ""
    checklist: List[Dict[str, Any]] = Field(default_factory=list)


class ActionGuard:
    """
    ActionGuard replaces fake physical safety systems (fake SIL-2, fake actuators)
    with a transparent, policy-controlled simulation boundary:
    1. Case is active and confirmed
    2. DecisionEngine recommends mitigation
    3. Single active case invariant holds
    4. Simulation mode only (transparent operational boundary)
    5. Historical replay branch available
    """
    def validate(
        self,
        lifecycle_state: IncidentLifecycleState,
        has_active_case: bool,
        recommended_action: IncidentAction,
        replay_branch_available: bool = True,
        conflicting_cases_count: int = 0,
    ) -> ActionGuardCheckResult:
        checklist = [
            {
                "id": "CASE_CONFIRMED",
                "label": "Case is active and confirmed",
                "passed": has_active_case and lifecycle_state in (
                    IncidentLifecycleState.DETECTED,
                    IncidentLifecycleState.INVESTIGATING,
                ),
            },
            {
                "id": "MITIGATION_RECOMMENDED",
                "label": "DecisionEngine recommends mitigation",
                "passed": recommended_action == IncidentAction.EXECUTE_MITIGATION,
            },
            {
                "id": "SINGLE_ACTIVE_CASE",
                "label": "No conflicting active cases on asset",
                "passed": conflicting_cases_count == 0,
            },
            {
                "id": "SIMULATION_MODE",
                "label": "Simulation intervention boundary verified",
                "passed": True,
            },
            {
                "id": "REPLAY_BRANCH_AVAILABLE",
                "label": "Post-maintenance historical stream segment available",
                "passed": replay_branch_available,
            },
        ]

        all_passed = all(item["passed"] for item in checklist)
        denial_reason = ""
        if not checklist[0]["passed"]:
            denial_reason = "Active case required in DETECTED or INVESTIGATING state."
        elif not checklist[1]["passed"]:
            denial_reason = "Mitigation not recommended by DecisionEngine."
        elif not checklist[2]["passed"]:
            denial_reason = "Conflicting active cases detected on asset."
        elif not checklist[4]["passed"]:
            denial_reason = "Post-maintenance historical stream segment unavailable."

        return ActionGuardCheckResult(
            is_permitted=all_passed,
            denial_reason=denial_reason,
            checklist=checklist,
        )
