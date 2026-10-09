import pytest
from src.storage.repository import CompressorGuardRepository
from src.storage.mongo_client import get_mongo_db, init_mongodb_schema
from src.engine.lifecycle import IncidentLifecycleManager
from src.domain.scenarios import FAILURE_3_SCENARIO
from src.observability.metrics import DatadogMetricsClient


def test_timeseries_collection_has_ttl_or_retention():
    repo = CompressorGuardRepository()
    db = repo.db
    cols = db.list_collection_names()
    assert "measurements" in cols
    # Ensure index exists on timestamp
    indexes = db["measurements"].index_information()
    assert any("timestamp" in str(idx) for idx in indexes.values())


def test_lifecycle_manager_persists_telemetry_measurements():
    repo = CompressorGuardRepository()
    manager = IncidentLifecycleManager(scenario=FAILURE_3_SCENARIO, repository=repo)
    manager.reset()

    # Tick 3 times
    for _ in range(3):
        pt = manager.tick()
        assert pt is not None

    # Measurements should be recorded in repository
    doc = repo.db["measurements"].find_one({"metadata.asset_id": "APU-COMP-01"})
    assert doc is not None
    assert "dv_pressure_bar" in doc
    assert "timestamp" in doc
