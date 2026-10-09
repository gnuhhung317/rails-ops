import pytest
from datetime import datetime, timezone
from src.engine.benchmark import BaselineBenchmarkTracker
from src.engine.lifecycle import IncidentLifecycleManager
from src.domain.scenarios import FAILURE_3_SCENARIO


def test_lead_time_returns_none_when_no_active_incident():
    manager = IncidentLifecycleManager(scenario=FAILURE_3_SCENARIO)
    manager.reset()
    # Before detection, lead time must NOT return a hardcoded 33h 52m!
    payload = manager.get_incident_payload()
    assert payload["lead_time"]["lead_time_minutes"] is None
    assert payload["lead_time"]["lead_time_formatted"] is None


def test_dynamic_lead_time_calculation_with_observed_lps():
    tracker = BaselineBenchmarkTracker()
    # Register confirmed onset at June 5 09:50:39
    onset_dt = datetime(2020, 6, 5, 9, 50, 39, tzinfo=timezone.utc)
    # Register historical LPS breached at June 6 19:42:19
    lps_dt = datetime(2020, 6, 6, 19, 42, 19, tzinfo=timezone.utc)

    tracker.record_onset(onset_dt)
    tracker.record_lps_benchmark(lps_dt)

    assert tracker.is_ready is True
    # 2020-06-05 09:50:39 to 2020-06-06 19:42:19 = 33 hours 51 minutes 40 seconds = 2032 minutes (or 2031-2032)
    assert tracker.lead_time_minutes in (2031, 2032)
    assert tracker.formatted_lead_time in ("33h 51m", "33h 52m")


def test_lifecycle_manager_integrates_benchmark_tracker():
    manager = IncidentLifecycleManager(scenario=FAILURE_3_SCENARIO)
    manager.reset()
    manager.jump_to_milestone("onset_0950")

    assert manager.benchmark_tracker is not None
    assert manager.benchmark_tracker.onset_timestamp is not None
    payload = manager.get_incident_payload()
    assert payload["lead_time"]["lead_time_minutes"] is not None
    assert "33h" in payload["lead_time"]["lead_time_formatted"]
