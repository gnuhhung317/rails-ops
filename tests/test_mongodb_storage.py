from datetime import datetime, timezone
import pytest

from src.storage.mongo_client import get_mongo_db, init_mongodb_schema, is_mongo_available
from src.storage.repository import CompressorGuardRepository


def test_mongodb_connection_or_fallback_initialization():
    db = get_mongo_db()
    assert db is not None
    collections = init_mongodb_schema(db)
    assert "measurements" in collections
    assert "operational_cases" in collections
    assert "case_events" in collections


def test_repository_telemetry_and_case_lifecycle():
    repo = CompressorGuardRepository()
    
    # Ingest telemetry points
    t1 = datetime(2020, 6, 5, 9, 50, 0, tzinfo=timezone.utc)
    point = {
        "timestamp": t1,
        "metadata": {
            "asset_id": "APU-COMP-01",
            "train_id": "TRAIN-302",
            "fleet_id": "FLEET-METRO-01",
        },
        "dv_pressure_bar": 2.1856,
        "oil_temp_c": 74.97,
        "motor_current_a": 6.8,
        "regime": "LOADED",
    }
    insert_id = repo.insert_measurement(point)
    assert insert_id is not None
    
    # Save operational case
    case_doc = {
        "case_id": "CASE-20200605-01",
        "asset_id": "APU-COMP-01",
        "phase": "CONFIRMED",
        "severity": "CRITICAL",
        "started_at": t1.isoformat(),
        "summary": "Severe discharge valve leakage confirmed",
        "confirmed_intervention_window": "33h 52m",
        "lead_time_minutes": 2032,
    }
    saved_case_id = repo.save_case(case_doc)
    assert saved_case_id == "CASE-20200605-01"
    
    retrieved = repo.get_case("CASE-20200605-01")
    assert retrieved is not None
    assert retrieved["case_id"] == "CASE-20200605-01"
    assert retrieved["phase"] == "CONFIRMED"
    assert retrieved["confirmed_intervention_window"] == "33h 52m"

    # Save case event
    event_doc = {
        "event_id": "EVT-001",
        "case_id": "CASE-20200605-01",
        "event_time": t1.isoformat(),
        "event_type": "DETECTION",
        "phase": "DETECTED",
        "title": "Confirmed degradation detected",
        "detail": "Pressure anomaly confirmed with temporal persistence across LOADED cycles.",
        "actor": "system",
        "source": "PressureAnomalyDetector",
    }
    repo.save_case_event(event_doc)
    events = repo.get_case_events("CASE-20200605-01")
    assert len(events) >= 1
    assert events[0]["event_id"] == "EVT-001"

    # Mark resolved to not conflict with subsequent tests
    case_doc["phase"] = "RESOLVED"
    repo.save_case(case_doc)


def test_repository_rolling_stats_pipeline():
    repo = CompressorGuardRepository()
    
    # Insert multiple measurements for rolling calculation
    base_ts = datetime(2020, 6, 5, 9, 40, 0, tzinfo=timezone.utc)
    points = []
    for i in range(5):
        points.append({
            "timestamp": datetime.fromtimestamp(base_ts.timestamp() + i * 10, tz=timezone.utc),
            "metadata": {"asset_id": "APU-COMP-01", "train_id": "TRAIN-302"},
            "dv_pressure_bar": 2.0 + i * 0.05,
            "oil_temp_c": 70.0 + i * 0.5,
            "regime": "LOADED",
        })
    repo.insert_measurements_batch(points)
    
    stats = repo.get_rolling_stats("APU-COMP-01", window_seconds=600)
    assert isinstance(stats, list)
    assert len(stats) >= 1
    assert "rolling_avg_dv" in stats[0]
    assert "rolling_avg_oil_temp" in stats[0]


def test_lifecycle_manager_persists_events_to_repository():
    from src.engine.lifecycle import IncidentLifecycleManager

    repo = CompressorGuardRepository()
    manager = IncidentLifecycleManager(repository=repo)
    manager.reset()
    manager.jump_to_milestone("onset_0950")

    events = repo.get_case_events("APU-INC-20200605-01")
    assert len(events) >= 1
    assert any(e["event_type"] == "DETECTION" for e in events)

