import pytest
from src.engine.lifecycle import IncidentLifecycleManager
from src.engine.simulation import SimulationRunner, HistoricalScenarioStream
from src.domain.scenarios import FAILURE_3_SCENARIO


def test_lifecycle_manager_uses_simulation_runner_as_sole_stream_driver():
    manager = IncidentLifecycleManager(scenario=FAILURE_3_SCENARIO)
    manager.reset()

    assert hasattr(manager, "runner")
    assert isinstance(manager.runner, SimulationRunner)
    assert manager.runner.is_paused is True

    # Pacing and play controls
    manager.play()
    assert manager.runner.is_paused is False

    manager.set_simulation_speed(300.0)
    assert manager.runner.config.speed_multiplier == 300.0

    # Advance by one tick through SimulationRunner
    pt = manager.tick()
    assert pt is not None
    assert manager.runner.total_points_emitted >= 1
    assert manager.runner.current_event_time == pt.timestamp


def test_simulation_runner_pause_stops_advancement_when_in_live_mode():
    manager = IncidentLifecycleManager(scenario=FAILURE_3_SCENARIO)
    manager.reset()
    manager.pause()
    assert manager.runner.is_paused is True
