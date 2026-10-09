import pytest
from src.domain.enums import IncidentLifecycleState, AssetHealthState, OperationalConfidence
from src.domain.scenarios import (
    ScenarioDefinition,
    FAILURE_3_SCENARIO,
    FAILURE_1_SCENARIO,
    FAILURE_4_SCENARIO,
    HEALTHY_SCENARIO,
)
from src.engine.lifecycle import IncidentLifecycleManager


def test_failure_3_early_excursion_narrative():
    """
    Validates Milestone 1 narrative: early excursion on June 4 00:33:07 (67h 09m prior to LPS).
    The system notices transient anomaly excursion, marks asset as DEGRADING with LOW confidence,
    but refuses to cry wolf (NO incident created).
    """
    manager = IncidentLifecycleManager(scenario=FAILURE_3_SCENARIO)
    manager.reset()

    # Jump to early excursion milestone
    manager.jump_to_milestone("early_excursion_0033")

    # Invariant: transient early excursion must NOT create an incident
    assert manager.active_incident is None
    assert manager.lifecycle_state == IncidentLifecycleState.NONE
    assert manager.asset_health == AssetHealthState.DEGRADING
    assert manager.operational_confidence == OperationalConfidence.LOW
    assert manager.current_decision is not None
    assert "Early Warning Excursion" in manager.current_decision.ui_action


def test_healthy_scenario_no_incidents_created():
    """
    Validates negative control: replaying healthy baseline stream (February 2020)
    never creates false positive incidents. Asset health remains HEALTHY throughout.
    """
    manager = IncidentLifecycleManager(scenario=HEALTHY_SCENARIO)
    manager.reset()

    # Stream 30 samples in healthy baseline
    for _ in range(30):
        pt = manager.tick()
        if pt is None:
            break

    assert manager.active_incident is None
    assert manager.lifecycle_state == IncidentLifecycleState.NONE
    assert manager.asset_health == AssetHealthState.HEALTHY
    assert manager.operational_confidence == OperationalConfidence.NONE


def test_scenario_definition_decoupling_failure_1_and_4():
    """
    Validates that IncidentLifecycleManager cleanly accepts arbitrary ScenarioDefinitions
    (Failure #1 and Failure #4) without modifying domain orchestrator code.
    """
    manager_f1 = IncidentLifecycleManager(scenario=FAILURE_1_SCENARIO)
    assert manager_f1.scenario.scenario_id == "failure_1"
    assert manager_f1.scenario.stream_start == "2020-04-10 00:00:00"
    assert "onset" in manager_f1.milestones

    manager_f4 = IncidentLifecycleManager(scenario=FAILURE_4_SCENARIO)
    assert manager_f4.scenario.scenario_id == "failure_4"
    assert manager_f4.scenario.stream_start == "2020-07-08 00:00:00"
    assert "onset" in manager_f4.milestones
