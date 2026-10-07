import pytest
from src.engine.lifecycle import IncidentLifecycleManager


def run_simulation(manager: IncidentLifecycleManager):
    manager.reset()

    records = []

    # 1. Milestone 1: Onset at 09:50
    manager.jump_to_milestone("onset_0950")
    records.append(
        {
            "milestone": "onset_0950",
            "state": manager.lifecycle_state.value,
            "incident": manager.get_incident_payload(),
            "evidence": manager.get_evidence_payload(),
        }
    )

    # 2. Milestone 2: ML Corroboration at 10:15
    manager.jump_to_milestone("ml_corroborated_1015")
    records.append(
        {
            "milestone": "ml_corroborated_1015",
            "state": manager.lifecycle_state.value,
            "incident": manager.get_incident_payload(),
            "evidence": manager.get_evidence_payload(),
        }
    )

    # 3. Action: Trigger Safe Mode
    sm_result = manager.trigger_safe_mode()
    records.append(
        {
            "action": "trigger_safe_mode",
            "result": sm_result,
            "state": manager.lifecycle_state.value,
        }
    )

    # 4. Advance ticks through recovery stream until RESOLVED
    ticks = 0
    while manager.lifecycle_state.value != "RESOLVED" and ticks < 100:
        manager.tick()
        ticks += 1

    records.append(
        {
            "status": "resolved",
            "ticks": ticks,
            "state": manager.lifecycle_state.value,
            "incident": manager.get_incident_payload(),
            "recovery": manager.get_recovery_payload(),
        }
    )

    return records


def test_deterministic_two_run_replay():
    manager = IncidentLifecycleManager()

    run_a = run_simulation(manager)
    run_b = run_simulation(manager)

    assert run_a == run_b, "Two-run deterministic replay must produce identical simulation outputs across reset cycles"
