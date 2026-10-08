from datetime import datetime, timedelta
from typing import Optional
import pytest

from src.domain.enums import OperatingRegime
from src.domain.models import TelemetryPoint
from src.engine.recovery import (
    RecoveryCriteria,
    RecoveryEvaluationResult,
    RecoveryVerifier,
)

_base_timestamp = datetime(2020, 6, 8, 16, 5, 0)
_timestamp_step = 0


@pytest.fixture(autouse=True)
def _reset_timestamp_step():
    global _timestamp_step
    _timestamp_step = 0


def _make_point(
    dv_pressure: float,
    oil_temp: float,
    regime: OperatingRegime,
    timestamp: Optional[datetime] = None,
    ts: Optional[datetime] = None,
) -> TelemetryPoint:
    actual_ts = timestamp or ts
    global _timestamp_step
    if actual_ts is None:
        point_ts = _base_timestamp + timedelta(seconds=10 * _timestamp_step)
        _timestamp_step += 1
    else:
        point_ts = actual_ts

    return TelemetryPoint(
        asset_id="APU-COMP-01",
        timestamp=point_ts,
        tp2_bar=0.0,
        tp3_bar=9.5,
        h1_bar=9.5,
        dv_pressure_bar=dv_pressure,
        reservoirs_bar=9.5,
        oil_temp_c=oil_temp,
        motor_current_a=3.8,
        comp_val=1.0,
        dv_electric=0.0,
        towers_val=1.0,
        mpg_val=1.0,
        lps_active=0.0,
        pressure_switch=0.0,
        oil_level_low=0.0,
        caudal_impulses=1.0,
        regime=regime,
    )


def test_recovery_criteria_policy_initialization():
    criteria = RecoveryCriteria()
    assert criteria.target_healthy_observations == 5
    assert criteria.dv_pressure_max == 0.05
    assert criteria.oil_temp_max == 67.0
    assert criteria.required_regime == OperatingRegime.LOADED
    assert criteria.max_observation_gap_seconds == 30.0

    custom = RecoveryCriteria(
        target_healthy_observations=3,
        dv_pressure_max=0.1,
        oil_temp_max=65.0,
        required_regime=OperatingRegime.OFF_LOAD,
        max_observation_gap_seconds=15.0,
    )
    assert custom.target_healthy_observations == 3
    assert custom.dv_pressure_max == 0.1
    assert custom.oil_temp_max == 65.0
    assert custom.required_regime == OperatingRegime.OFF_LOAD
    assert custom.max_observation_gap_seconds == 15.0


def test_recovery_near_success_reset_invariant():
    verifier = RecoveryVerifier()
    assert verifier.consecutive_healthy_observations == 0
    assert not verifier.is_verified

    # 1. Feeds 4 healthy points -> verifier.consecutive_healthy_observations == 4, is_verified == False
    for _ in range(4):
        result = verifier.evaluate(_make_point(dv_pressure=-0.016, oil_temp=64.0, regime=OperatingRegime.LOADED))
        assert result.is_applicable_regime is True
        assert result.is_observation_healthy is True
        assert result.is_verified is False
    assert verifier.consecutive_healthy_observations == 4
    assert verifier.is_verified is False

    # 2. Feeds 1 unhealthy point (oil_temp=72.0°C > 67.0°C) -> resets immediately
    unhealthy_point = _make_point(dv_pressure=-0.016, oil_temp=72.0, regime=OperatingRegime.LOADED)
    result = verifier.evaluate(unhealthy_point)
    assert result.is_applicable_regime is True
    assert result.is_observation_healthy is False
    assert result.consecutive_healthy_observations == 0
    assert result.is_verified is False
    assert verifier.consecutive_healthy_observations == 0
    assert verifier.is_verified is False

    # 3. Feeds 1 OFF regime point -> suspended (does not increment or reset)
    off_point = _make_point(dv_pressure=-0.016, oil_temp=64.0, regime=OperatingRegime.OFF)
    result = verifier.evaluate(off_point)
    assert result.is_applicable_regime is False
    assert result.is_observation_healthy is False
    assert result.consecutive_healthy_observations == 0
    assert result.is_verified is False
    assert verifier.consecutive_healthy_observations == 0
    assert verifier.is_verified is False

    # 4. Feeds 5 healthy points -> reaches target, verified == True
    for i in range(1, 6):
        result = verifier.evaluate(_make_point(dv_pressure=0.01, oil_temp=63.5, regime=OperatingRegime.LOADED))
        assert result.is_applicable_regime is True
        assert result.is_observation_healthy is True
        assert result.consecutive_healthy_observations == i
        if i < 5:
            assert result.is_verified is False
            assert verifier.is_verified is False
        else:
            assert result.is_verified is True
            assert verifier.is_verified is True

    assert verifier.consecutive_healthy_observations == 5
    assert verifier.is_verified is True


def test_recovery_verifier_dv_pressure_breach():
    verifier = RecoveryVerifier()
    # 2 healthy points
    verifier.evaluate(_make_point(dv_pressure=0.02, oil_temp=60.0, regime=OperatingRegime.LOADED))
    verifier.evaluate(_make_point(dv_pressure=0.03, oil_temp=61.0, regime=OperatingRegime.LOADED))
    assert verifier.consecutive_healthy_observations == 2

    # Breach on dv_pressure (0.08 > 0.05)
    result = verifier.evaluate(_make_point(dv_pressure=0.08, oil_temp=60.0, regime=OperatingRegime.LOADED))
    assert result.is_applicable_regime is True
    assert result.is_observation_healthy is False
    assert result.consecutive_healthy_observations == 0
    assert verifier.consecutive_healthy_observations == 0
    assert verifier.is_verified is False


def test_recovery_verifier_suspension_preserves_counter():
    verifier = RecoveryVerifier()
    # Feed 2 healthy points
    verifier.evaluate(_make_point(dv_pressure=0.01, oil_temp=62.0, regime=OperatingRegime.LOADED))
    verifier.evaluate(_make_point(dv_pressure=0.02, oil_temp=63.0, regime=OperatingRegime.LOADED))
    assert verifier.consecutive_healthy_observations == 2

    # Feed OFF point -> should keep counter at 2
    off_result = verifier.evaluate(_make_point(dv_pressure=0.01, oil_temp=62.0, regime=OperatingRegime.OFF))
    assert off_result.is_applicable_regime is False
    assert verifier.consecutive_healthy_observations == 2

    # Feed STARTING point -> should keep counter at 2
    start_result = verifier.evaluate(_make_point(dv_pressure=0.01, oil_temp=62.0, regime=OperatingRegime.STARTING))
    assert start_result.is_applicable_regime is False
    assert verifier.consecutive_healthy_observations == 2

    # Feed 3 more healthy points -> completes 5
    for _ in range(3):
        verifier.evaluate(_make_point(dv_pressure=0.01, oil_temp=62.0, regime=OperatingRegime.LOADED))
    assert verifier.consecutive_healthy_observations == 5
    assert verifier.is_verified is True


def test_recovery_verifier_reset():
    verifier = RecoveryVerifier()
    for _ in range(5):
        verifier.evaluate(_make_point(dv_pressure=0.01, oil_temp=62.0, regime=OperatingRegime.LOADED))
    assert verifier.consecutive_healthy_observations == 5
    assert verifier.is_verified is True

    verifier.reset()
    assert verifier.consecutive_healthy_observations == 0
    assert verifier.is_verified is False
