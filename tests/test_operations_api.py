from fastapi.testclient import TestClient
from src.api.app import create_app

def test_operations_endpoint_structure():
    app = create_app()
    client = TestClient(app)
    
    resp = client.get("/api/operations")
    assert resp.status_code == 200
    data = resp.json()
    
    # 1. Business context hierarchy
    assert "fleet" in data
    assert data["fleet"]["fleet_id"] == "FLEET-METRO-01"
    assert "train" in data
    assert data["train"]["train_id"] == "TRAIN-302"
    assert "asset" in data
    assert data["asset"]["asset_id"] == "APU-COMP-01"
    
    # 2. Operations metrics (truthful, no hardcoded 98%)
    assert "operations_summary" in data
    ops = data["operations_summary"]
    assert ops["monitored_assets_count"] == 1
    assert ops["active_cases_count"] in (0, 1)
    assert ops["scenario_name"] == "Failure #3 — Air Leak"
    assert ops["simulation_mode"] == "LIVE_SIMULATION"

def test_case_timeline_and_closure_flow():
    app = create_app()
    client = TestClient(app)
    
    client.post("/demo/reset", json={"milestone": "onset_0950"})
    
    # GET /api/case (alias for /api/incident)
    case_resp = client.get("/api/case")
    assert case_resp.status_code == 200
    assert case_resp.json()["lifecycle_state"] == "DETECTED"
    
    # GET /api/case/events
    timeline_resp = client.get("/api/case/events")
    assert timeline_resp.status_code == 200
    events = timeline_resp.json()
    assert len(events) >= 1
    assert any(e["event_type"] == "DETECTION" for e in events)

    # Validation reference endpoint
    val_resp = client.get("/api/validation-reference")
    assert val_resp.status_code == 200
    val_data = val_resp.json()
    assert val_data["scenario_id"] == "SCENARIO-FAIL-03"
    assert val_data["reported_failure_mode"] == "Air leak in Air Production Unit"
