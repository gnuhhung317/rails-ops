import pytest
from src.domain.scenarios import FAILURE_3_SCENARIO
from src.engine.lifecycle import IncidentLifecycleManager
from src.domain.enums import AssetHealthState, IncidentLifecycleState


def test_early_excursion_matches_actual_dataset_telemetry():
    manager = IncidentLifecycleManager(scenario=FAILURE_3_SCENARIO)
    manager.reset()
    manager.jump_to_milestone("early_excursion_0033")

    pt = manager.current_point
    assert pt is not None
    assert "2020-06-04 00:33:07" in str(pt.timestamp)
    # The actual sensor value in MetroPT-3 is ~6.046 bar, not synthetic 0.52 bar!
    assert round(pt.dv_pressure_bar, 2) == 6.05

    # State truth: transient excursion is observed, asset is marked DEGRADING, but NO case created
    assert manager.lifecycle_state == IncidentLifecycleState.NONE
    assert manager.asset_health == AssetHealthState.DEGRADING
    assert manager.active_incident is None
    assert manager.has_active_case() is False
