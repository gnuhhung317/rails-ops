import pytest
from src.engine.lifecycle import IncidentLifecycleManager
from src.domain.scenarios import FAILURE_1_SCENARIO, FAILURE_4_SCENARIO, HEALTHY_SCENARIO
from src.domain.enums import IncidentLifecycleState, AssetHealthState


def test_healthy_scenario_remains_strictly_healthy():
    manager = IncidentLifecycleManager(scenario=HEALTHY_SCENARIO)
    manager.reset()
    for _ in range(50):
        pt = manager.tick()
        if pt is None:
            break
        assert manager.has_active_case() is False
        assert manager.lifecycle_state == IncidentLifecycleState.NONE
        assert manager.asset_health == AssetHealthState.HEALTHY


def test_failure_1_scenario_loads_and_advances():
    manager = IncidentLifecycleManager(scenario=FAILURE_1_SCENARIO)
    manager.reset()
    pt = manager.tick()
    assert pt is not None
    assert pt.asset_id == "APU-COMP-01"


def test_failure_4_scenario_loads_and_advances():
    manager = IncidentLifecycleManager(scenario=FAILURE_4_SCENARIO)
    manager.reset()
    pt = manager.tick()
    assert pt is not None
    assert pt.asset_id == "APU-COMP-01"
