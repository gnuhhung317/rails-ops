import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app


def test_api_vertical_slice_golden_path():
    """
    Comprehensive vertical slice integration test validating the 10-step Golden Path sequence
    across domain API endpoints and demo simulation controls.
    """
    app = create_app()
    client = TestClient(app)

    # 1. Reset demo to onset milestone: POST /demo/reset, body {"milestone": "onset_0950"} -> 200 OK.
    reset_resp = client.post("/demo/reset", json={"milestone": "onset_0950"})
    assert reset_resp.status_code == 200
    reset_data = reset_resp.json()
    assert reset_data.get("status") == "RESET_OK"
    assert reset_data.get("milestone") == "onset_0950"

    # 2. GET /api/incident -> asset_id == "APU-COMP-01", lifecycle_state == "DETECTED",
    #    lead_time["lead_time_formatted"] == "33h 52m", lead_time["lead_time_minutes"] == 2032.
    inc_resp = client.get("/api/incident")
    assert inc_resp.status_code == 200
    inc_data = inc_resp.json()
    assert inc_data["incident_id"] == "APU-INC-20200605-01"
    assert inc_data["asset_id"] == "APU-COMP-01"
    assert inc_data["lifecycle_state"] == "DETECTED"
    assert inc_data["lead_time"]["lead_time_formatted"] == "33h 52m"
    assert inc_data["lead_time"]["lead_time_minutes"] == 2032
    assert "summary" in inc_data

    # Attempt safe-mode before ML corroboration -> 409 Conflict
    sm_onset_resp = client.post("/api/action/safe-mode")
    assert sm_onset_resp.status_code == 409
    sm_onset_data = sm_onset_resp.json()
    assert sm_onset_data.get("error") == "INVALID_STATE_TRANSITION"

    # 3. GET /api/evidence -> regime == "LOADED", contains PRESSURE_SEVERE with sigma_deviation > 20.0.
    ev_resp = client.get("/api/evidence")
    assert ev_resp.status_code == 200
    ev_data = ev_resp.json()
    assert ev_data["regime"] == "LOADED"
    assert "evidence_pack" in ev_data
    pressure_sig = next(
        (s for s in ev_data["evidence_pack"] if "PRESSURE_SEVERE" in s["code"]),
        None,
    )
    assert pressure_sig is not None, "Evidence pack must contain PRESSURE_SEVERE"
    assert pressure_sig["sigma_deviation"] > 20.0
    assert pressure_sig["is_primary"] is True

    # Signal: Temporal persistence signal is included in evidence_pack
    temporal_sig = next(
        (s for s in ev_data["evidence_pack"] if "TEMPORAL_STEP_CONFIRMED" in s["code"]),
        None,
    )
    assert temporal_sig is not None, "Evidence pack must contain TEMPORAL_STEP_CONFIRMED"
    assert temporal_sig["signal_name"] == "Temporal Persistence Tracking"
    assert temporal_sig["unit"] == "bar_diff"
    assert temporal_sig["status"] == "CONFIRMED"
    assert temporal_sig["is_primary"] is False

    # Check persistence block using observation terminology
    assert "persistence" in ev_data
    assert ev_data["persistence"]["confirmed"] is True
    assert ev_data["persistence"]["recent_observations"] == 3
    assert ev_data["persistence"]["required_observations"] == 3

    # 4. POST /demo/jump, body {"milestone": "ml_corroborated_1015"} -> 200 OK.
    #    GET /api/incident now reflects lifecycle_state == "INVESTIGATING".
    jump_resp = client.post("/demo/jump", json={"milestone": "ml_corroborated_1015"})
    assert jump_resp.status_code == 200
    jump_data = jump_resp.json()
    assert jump_data.get("status") == "JUMP_OK"
    assert jump_data.get("milestone") == "ml_corroborated_1015"

    inc_resp = client.get("/api/incident")
    assert inc_resp.status_code == 200
    inc_data = inc_resp.json()
    assert inc_data["lifecycle_state"] == "INVESTIGATING"

    # 5. Negative Test: POST /demo/jump, body {"milestone": "fabricated_recovered"} -> 400 Bad Request.
    bad_jump = client.post("/demo/jump", json={"milestone": "fabricated_recovered"})
    assert bad_jump.status_code == 400
    bad_jump_data = bad_jump.json()
    assert bad_jump_data.get("error") == "INVALID_ARGUMENT"
    assert "detail" in bad_jump_data

    # 6. POST /api/action/safe-mode -> 200 OK, returns status == "ACTIVATED", execution_mode == "SIMULATION_BRANCH".
    sm_resp = client.post("/api/action/safe-mode")
    assert sm_resp.status_code == 200
    sm_data = sm_resp.json()
    assert sm_data["status"] == "ACTIVATED"
    assert sm_data["execution_mode"] == "SIMULATION_BRANCH"
    assert sm_data["target_state"] == "MITIGATING"
    assert "stream_branch" in sm_data

    # 7. Negative Test: Calling POST /api/action/safe-mode again -> 409 Conflict.
    sm_neg_resp = client.post("/api/action/safe-mode")
    assert sm_neg_resp.status_code == 409
    sm_neg_data = sm_neg_resp.json()
    assert sm_neg_data.get("error") == "INVALID_STATE_TRANSITION"
    assert "detail" in sm_neg_data

    # 8. POST /demo/tick multiple times until recovery verified (up to 50 ticks).
    #    GET /api/recovery shows is_verified == True, consecutive_healthy_observations == 5.
    ticks = 0
    rec_data = None
    while ticks < 50:
        tick_resp = client.post("/demo/tick")
        assert tick_resp.status_code == 200
        tick_data = tick_resp.json()
        assert tick_data.get("status") == "TICK_OK"
        ticks += 1

        rec_resp = client.get("/api/recovery")
        assert rec_resp.status_code == 200
        rec_data = rec_resp.json()
        if rec_data.get("is_verified") is True:
            break

    assert rec_data is not None
    assert rec_data["is_verified"] is True
    assert rec_data["consecutive_healthy_observations"] == 5
    assert rec_data["target_healthy_observations"] == 5

    # 9. GET /api/incident reflects lifecycle_state == "RESOLVED", asset_health == "HEALTHY".
    inc_final_resp = client.get("/api/incident")
    assert inc_final_resp.status_code == 200
    inc_final_data = inc_final_resp.json()
    assert inc_final_data["lifecycle_state"] == "RESOLVED"
    assert inc_final_data["asset_health"] == "HEALTHY"

    # 10. POST /demo/tick after RESOLVED -> 200 OK (idempotent no-op).
    post_resolve_tick = client.post("/demo/tick")
    assert post_resolve_tick.status_code == 200
    post_tick_data = post_resolve_tick.json()
    assert post_tick_data.get("status") == "TICK_OK"
    assert post_tick_data.get("lifecycle_state") == "RESOLVED"


def test_api_reset_default_and_invalid():
    """Test reset with default (no body) and reset with invalid milestone."""
    app = create_app()
    client = TestClient(app)

    # Reset without body
    resp_no_body = client.post("/demo/reset")
    assert resp_no_body.status_code == 200
    assert resp_no_body.json().get("status") == "RESET_OK"

    # Reset with invalid milestone -> 400 Bad Request
    resp_bad = client.post("/demo/reset", json={"milestone": "non_existent_milestone"})
    assert resp_bad.status_code == 400
    assert resp_bad.json().get("error") == "INVALID_ARGUMENT"


def test_safe_mode_invalid_transition_from_none_state():
    """Test triggering safe mode from NONE initial state returns 409 Conflict."""
    app = create_app()
    client = TestClient(app)

    # Initial state is NONE
    resp = client.post("/api/action/safe-mode")
    assert resp.status_code == 409
    data = resp.json()
    assert data.get("error") == "INVALID_STATE_TRANSITION"
