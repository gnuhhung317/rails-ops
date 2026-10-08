from datetime import datetime, timedelta
import pytest

from src.domain.enums import OperatingRegime, DetectorStatus, EvidenceCode
from src.domain.models import TelemetryPoint
from src.engine.detectors import TemporalStepDetector
from src.engine.recovery import RecoveryCriteria, RecoveryVerifier


def _make_point(
    timestamp: datetime,
    regime: OperatingRegime = OperatingRegime.LOADED,
    dv_pressure: float = -0.016,
    oil_temp: float = 64.0,
) -> TelemetryPoint:
    return TelemetryPoint(
        asset_id="APU-COMP-01",
        timestamp=timestamp,
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


def test_recovery_continuity_3_observations_at_10s_succeeds():
    criteria = RecoveryCriteria(target_healthy_observations=3, max_observation_gap_seconds=30.0)
    verifier = RecoveryVerifier(criteria)

    t0 = datetime(2020, 6, 8, 16, 0, 0)

    # 1st observation at t0
    res1 = verifier.evaluate(_make_point(timestamp=t0))
    assert res1.is_applicable_regime is True
    assert res1.is_observation_healthy is True
    assert res1.consecutive_healthy_observations == 1
    assert res1.is_verified is False
    assert verifier.consecutive_healthy_observations == 1
    assert verifier.is_verified is False

    # 2nd observation at t0 + 10s
    t1 = t0 + timedelta(seconds=10)
    res2 = verifier.evaluate(_make_point(timestamp=t1))
    assert res2.is_applicable_regime is True
    assert res2.is_observation_healthy is True
    assert res2.consecutive_healthy_observations == 2
    assert res2.is_verified is False
    assert verifier.consecutive_healthy_observations == 2
    assert verifier.is_verified is False

    # 3rd observation at t0 + 20s
    t2 = t1 + timedelta(seconds=10)
    res3 = verifier.evaluate(_make_point(timestamp=t2))
    assert res3.is_applicable_regime is True
    assert res3.is_observation_healthy is True
    assert res3.consecutive_healthy_observations == 3
    assert res3.is_verified is True
    assert verifier.consecutive_healthy_observations == 3
    assert verifier.is_verified is True


def test_recovery_continuity_broken_by_60s_gap():
    criteria = RecoveryCriteria(target_healthy_observations=3, max_observation_gap_seconds=30.0)
    verifier = RecoveryVerifier(criteria)

    t0 = datetime(2020, 6, 8, 16, 0, 0)

    # 1st observation at t0
    verifier.evaluate(_make_point(timestamp=t0))
    assert verifier.consecutive_healthy_observations == 1

    # 2nd observation at t0 + 10s
    t1 = t0 + timedelta(seconds=10)
    verifier.evaluate(_make_point(timestamp=t1))
    assert verifier.consecutive_healthy_observations == 2

    # 3rd observation after 60s gap (t1 + 60s) -> continuity broken! Streak resets to 1 (not verified)
    t2 = t1 + timedelta(seconds=60)
    res3 = verifier.evaluate(_make_point(timestamp=t2))
    assert res3.is_applicable_regime is True
    assert res3.is_observation_healthy is True
    assert res3.consecutive_healthy_observations == 1
    assert res3.is_verified is False
    assert verifier.consecutive_healthy_observations == 1
    assert verifier.is_verified is False


def test_recovery_regime_gap_over_max_gap_breaks_continuity():
    criteria = RecoveryCriteria(target_healthy_observations=3, max_observation_gap_seconds=30.0)
    verifier = RecoveryVerifier(criteria)

    t0 = datetime(2020, 6, 8, 16, 0, 0)

    # 1st observation at t0
    verifier.evaluate(_make_point(timestamp=t0))
    assert verifier.consecutive_healthy_observations == 1

    # 2nd observation at t0 + 10s
    t1 = t0 + timedelta(seconds=10)
    verifier.evaluate(_make_point(timestamp=t1))
    assert verifier.consecutive_healthy_observations == 2

    # OFF regime observation 60s later -> evaluation suspended
    t2 = t1 + timedelta(seconds=60)
    res_off = verifier.evaluate(_make_point(timestamp=t2, regime=OperatingRegime.OFF))
    assert res_off.is_applicable_regime is False
    assert verifier.consecutive_healthy_observations == 2

    # LOADED observation at t2 + 10s -> gap from last healthy observation is 70s > 30s -> resets streak to 1!
    t3 = t2 + timedelta(seconds=10)
    res_loaded = verifier.evaluate(_make_point(timestamp=t3, regime=OperatingRegime.LOADED))
    assert res_loaded.is_applicable_regime is True
    assert res_loaded.is_observation_healthy is True
    assert res_loaded.consecutive_healthy_observations == 1
    assert res_loaded.is_verified is False
    assert verifier.consecutive_healthy_observations == 1
    assert verifier.is_verified is False


def test_recovery_duplicate_and_retrograde_timestamps_reset_streak():
    criteria = RecoveryCriteria(target_healthy_observations=3, max_observation_gap_seconds=30.0)
    verifier = RecoveryVerifier(criteria)

    t0 = datetime(2020, 6, 8, 16, 0, 0)

    # 1st observation at t0
    res1 = verifier.evaluate(_make_point(timestamp=t0))
    assert res1.consecutive_healthy_observations == 1
    assert res1.is_verified is False

    # 2nd observation at t0 + 10s
    t1 = t0 + timedelta(seconds=10)
    res2 = verifier.evaluate(_make_point(timestamp=t1))
    assert res2.consecutive_healthy_observations == 2
    assert res2.is_verified is False

    # Duplicate timestamp (gap == 0) -> resets streak to 1
    res_dup = verifier.evaluate(_make_point(timestamp=t1))
    assert res_dup.consecutive_healthy_observations == 1
    assert res_dup.is_verified is False
    assert verifier.consecutive_healthy_observations == 1
    assert verifier.is_verified is False

    # Advance to streak 2 again at t1 + 10s
    t2 = t1 + timedelta(seconds=10)
    res3 = verifier.evaluate(_make_point(timestamp=t2))
    assert res3.consecutive_healthy_observations == 2
    assert res3.is_verified is False

    # Retrograde timestamp (gap < 0) -> resets streak to 1
    t_retro = t2 - timedelta(seconds=5)
    res_retro = verifier.evaluate(_make_point(timestamp=t_retro))
    assert res_retro.consecutive_healthy_observations == 1
    assert res_retro.is_verified is False
    assert verifier.consecutive_healthy_observations == 1
    assert verifier.is_verified is False


def test_recovery_exact_boundary_gap_30s():
    criteria = RecoveryCriteria(target_healthy_observations=3, max_observation_gap_seconds=30.0)

    # Subtest 1: gap == 30.0 maintains continuity
    verifier_boundary = RecoveryVerifier(criteria)
    t0 = datetime(2020, 6, 8, 16, 0, 0)
    verifier_boundary.evaluate(_make_point(timestamp=t0))
    assert verifier_boundary.consecutive_healthy_observations == 1

    t1 = t0 + timedelta(seconds=30.0)
    res_30 = verifier_boundary.evaluate(_make_point(timestamp=t1))
    assert res_30.consecutive_healthy_observations == 2
    assert res_30.is_verified is False
    assert verifier_boundary.consecutive_healthy_observations == 2

    t2 = t1 + timedelta(seconds=30.0)
    res_60 = verifier_boundary.evaluate(_make_point(timestamp=t2))
    assert res_60.consecutive_healthy_observations == 3
    assert res_60.is_verified is True
    assert verifier_boundary.consecutive_healthy_observations == 3
    assert verifier_boundary.is_verified is True

    # Subtest 2: gap == 30.1 resets streak to 1
    verifier_over = RecoveryVerifier(criteria)
    verifier_over.evaluate(_make_point(timestamp=t0))
    verifier_over.evaluate(_make_point(timestamp=t0 + timedelta(seconds=10.0)))
    assert verifier_over.consecutive_healthy_observations == 2

    t_over = t0 + timedelta(seconds=10.0) + timedelta(seconds=30.1)
    res_over = verifier_over.evaluate(_make_point(timestamp=t_over))
    assert res_over.consecutive_healthy_observations == 1
    assert res_over.is_verified is False
    assert verifier_over.consecutive_healthy_observations == 1
    assert verifier_over.is_verified is False


def test_recovery_post_verification_gap_resets_is_verified():
    criteria = RecoveryCriteria(target_healthy_observations=3, max_observation_gap_seconds=30.0)
    verifier = RecoveryVerifier(criteria)

    t0 = datetime(2020, 6, 8, 16, 0, 0)

    # 3 consecutive observations achieve verification
    for i in range(3):
        res = verifier.evaluate(_make_point(timestamp=t0 + timedelta(seconds=10 * i)))
    assert res.consecutive_healthy_observations == 3
    assert res.is_verified is True
    assert verifier.consecutive_healthy_observations == 3
    assert verifier.is_verified is True

    # Subsequent observation after gap > 30s (e.g. 40s after last point)
    t_after_gap = t0 + timedelta(seconds=20) + timedelta(seconds=40)
    res_post_gap = verifier.evaluate(_make_point(timestamp=t_after_gap))

    # Streak resets to 1 and is_verified resets back to False
    assert res_post_gap.consecutive_healthy_observations == 1
    assert res_post_gap.is_verified is False
    assert verifier.consecutive_healthy_observations == 1
    assert verifier.is_verified is False


def test_temporal_step_continuity_valid_10s_intervals():
    detector = TemporalStepDetector(
        step_threshold=0.5,
        required_observations=3,
        baseline_observations=5,
        max_observation_gap_seconds=30.0,
    )
    t0 = datetime(2020, 6, 8, 16, 0, 0)
    window = []
    # 5 baseline points with dv=0.0 at 10s intervals
    for i in range(5):
        window.append(_make_point(timestamp=t0 + timedelta(seconds=10 * i), dv_pressure=0.0))
    # 3 step points with dv=1.5 at 10s intervals
    for i in range(5, 8):
        window.append(_make_point(timestamp=t0 + timedelta(seconds=10 * i), dv_pressure=1.5))

    res = detector.detect(window)
    assert res.status == DetectorStatus.CONFIRMED
    assert res.evidence_code == EvidenceCode.TEMPORAL_STEP_CONFIRMED
    assert res.provenance["is_temporally_contiguous"] is True
    assert res.provenance["max_observation_gap_seconds"] == 30.0


def test_temporal_step_broken_by_60s_gap_in_recent():
    detector = TemporalStepDetector(
        step_threshold=0.5,
        required_observations=3,
        baseline_observations=5,
        max_observation_gap_seconds=30.0,
    )
    t0 = datetime(2020, 6, 8, 16, 0, 0)
    window = []
    # 5 baseline points with dv=0.0 at 10s intervals (t0 .. t0+40s)
    for i in range(5):
        window.append(_make_point(timestamp=t0 + timedelta(seconds=10 * i), dv_pressure=0.0))
    # point 6 (+10s -> t0+50s)
    window.append(_make_point(timestamp=t0 + timedelta(seconds=50), dv_pressure=1.5))
    # point 7 (+10s -> t0+60s)
    window.append(_make_point(timestamp=t0 + timedelta(seconds=60), dv_pressure=1.5))
    # point 8 has a 60s gap (+60s -> t0+120s)
    window.append(_make_point(timestamp=t0 + timedelta(seconds=120), dv_pressure=1.5))

    res = detector.detect(window)
    assert res.status == DetectorStatus.NORMAL


def test_temporal_step_gap_plus_regime_change_does_not_pick_old_points():
    detector = TemporalStepDetector(
        step_threshold=0.5,
        required_observations=3,
        baseline_observations=5,
        allowed_regime_gaps=2,
        max_observation_gap_seconds=30.0,
    )
    t0 = datetime(2020, 6, 8, 16, 0, 0)
    window = []
    # 5 baseline points with dv=0.0 at 10s intervals (t0 .. t0+40s)
    for i in range(5):
        window.append(_make_point(timestamp=t0 + timedelta(seconds=10 * i), dv_pressure=0.0))
    # 1 point with dv=1.5 (t0+50s)
    window.append(_make_point(timestamp=t0 + timedelta(seconds=50), dv_pressure=1.5))
    # 5 minutes of OFF regime (point at t0 + 60s and t0 + 350s)
    window.append(_make_point(timestamp=t0 + timedelta(seconds=60), regime=OperatingRegime.OFF))
    # 2 new LOADED points (t0+360s, t0+370s)
    window.append(_make_point(timestamp=t0 + timedelta(seconds=360), dv_pressure=1.5))
    window.append(_make_point(timestamp=t0 + timedelta(seconds=370), dv_pressure=1.5))

    res = detector.detect(window)
    assert res.status == DetectorStatus.NORMAL


def test_temporal_step_duplicate_or_retrograde_timestamps_fail_continuity():
    detector = TemporalStepDetector(
        step_threshold=0.5,
        required_observations=3,
        baseline_observations=5,
        max_observation_gap_seconds=30.0,
    )
    t0 = datetime(2020, 6, 8, 16, 0, 0)

    # Subtest 1: Duplicate timestamp
    window_dup = []
    for i in range(5):
        window_dup.append(_make_point(timestamp=t0 + timedelta(seconds=10 * i), dv_pressure=0.0))
    window_dup.append(_make_point(timestamp=t0 + timedelta(seconds=50), dv_pressure=1.5))
    window_dup.append(_make_point(timestamp=t0 + timedelta(seconds=60), dv_pressure=1.5))
    window_dup.append(_make_point(timestamp=t0 + timedelta(seconds=60), dv_pressure=1.5))  # Duplicate ts

    res_dup = detector.detect(window_dup)
    assert res_dup.status == DetectorStatus.NORMAL

    # Subtest 2: Retrograde timestamp
    window_retro = []
    for i in range(5):
        window_retro.append(_make_point(timestamp=t0 + timedelta(seconds=10 * i), dv_pressure=0.0))
    window_retro.append(_make_point(timestamp=t0 + timedelta(seconds=50), dv_pressure=1.5))
    window_retro.append(_make_point(timestamp=t0 + timedelta(seconds=60), dv_pressure=1.5))
    window_retro.append(_make_point(timestamp=t0 + timedelta(seconds=55), dv_pressure=1.5))  # Retrograde ts

    res_retro = detector.detect(window_retro)
    assert res_retro.status == DetectorStatus.NORMAL

