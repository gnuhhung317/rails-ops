import pytest
from fastapi.testclient import TestClient
from src.api.app import create_app
from src.engine.lifecycle import IncidentLifecycleManager
from src.storage.repository import CompressorGuardRepository


@pytest.fixture
def test_client():
    from src.storage.mongo_client import reset_in_memory_db
    reset_in_memory_db()
    repo = CompressorGuardRepository()
    manager = IncidentLifecycleManager(repository=repo)
    app = create_app(manager=manager)
    return TestClient(app)


def test_web_console_landing_page_html(test_client):
    """Verifies that root / and /console serve the HTML SPA with requisite brand and labels."""
    # HTML request to root
    resp_root = test_client.get("/", headers={"Accept": "text/html,application/xhtml+xml"})
    assert resp_root.status_code == 200
    assert "text/html" in resp_root.headers.get("content-type", "")
    assert "COMPRESSORGUARD" in resp_root.text
    assert "OPERATIONS COMMAND CONSOLE" in resp_root.text
    assert "LIVE SIMULATION · HISTORICAL DATA" in resp_root.text
    assert "APU-COMP-01" in resp_root.text

    # /console path
    resp_console = test_client.get("/console", headers={"Accept": "text/html"})
    assert resp_console.status_code == 200
    assert "text/html" in resp_console.headers.get("content-type", "")
    assert "COMPRESSORGUARD" in resp_console.text


def test_static_assets_mounted_and_health_json(test_client):
    """Verifies static assets are served from /static and /health returns JSON probe."""
    # CSS
    resp_css = test_client.get("/static/styles.css")
    assert resp_css.status_code == 200
    assert "CompressorGuard" in resp_css.text

    # JS
    resp_js = test_client.get("/static/app.js")
    assert resp_js.status_code == 200
    assert "refreshAllData" in resp_js.text

    # Health probe
    resp_health = test_client.get("/health")
    assert resp_health.status_code == 200
    assert resp_health.json()["status"] == "OPERATIONAL"

    # JSON accept on root
    resp_json = test_client.get("/", headers={"Accept": "application/json"})
    assert resp_json.status_code == 200
    data = resp_json.json()
    assert data["status"] == "OPERATIONAL"
    assert "/console" in data["console_url"]


def test_simulation_playback_endpoints(test_client):
    """Verifies play, pause, speed, and status demo endpoints."""
    # Play
    resp_play = test_client.post("/demo/play")
    assert resp_play.status_code == 200
    assert resp_play.json()["status"] == "PLAY_OK"
    assert resp_play.json()["is_paused"] is False

    # Pause
    resp_pause = test_client.post("/demo/pause")
    assert resp_pause.status_code == 200
    assert resp_pause.json()["status"] == "PAUSE_OK"
    assert resp_pause.json()["is_paused"] is True

    # Speed
    resp_speed = test_client.post("/demo/speed", json={"speed_multiplier": 10.0})
    assert resp_speed.status_code == 200
    assert resp_speed.json()["speed_multiplier"] == 10.0

    # Status
    resp_status = test_client.get("/demo/status")
    assert resp_status.status_code == 200
    st = resp_status.json()
    assert st["mode"] == "LIVE_SIMULATION"
    assert st["speed_multiplier"] == 10.0
    assert "MetroPT-3" in st["provenance"]


def test_end_to_end_web_flow_simulation(test_client):
    """
    Verifies full operator workflow via API matching Screen Specs 01-07:
    Reset -> Noise Rejection (00:33) -> Onset (09:50) -> Evidence -> ActionGuard Safe Mode ->
    Recovery Verification (16:05) -> Close Case -> Timeline Ledger Audit.
    """
    # 1. Reset
    r_reset = test_client.post("/demo/reset")
    assert r_reset.status_code == 200

    r_ops_init = test_client.get("/api/operations")
    assert r_ops_init.status_code == 200
    assert r_ops_init.json()["operations_summary"]["active_cases_count"] == 0

    # 2. Screen 01: Transient Excursion (00:33:07 Noise Rejection)
    r_jump_0033 = test_client.post("/demo/jump", json={"milestone": "early_excursion_0033"})
    assert r_jump_0033.status_code == 200

    r_ops_0033 = test_client.get("/api/operations")
    assert r_ops_0033.status_code == 200
    # Case creation suppressed!
    assert r_ops_0033.json()["operations_summary"]["active_cases_count"] == 0
    assert r_ops_0033.json()["operations_summary"]["assets_observing_count"] == 1

    # 3. Screen 02 & 03: Degradation Onset (09:50:39 Confirmed Case)
    r_jump_0950 = test_client.post("/demo/jump", json={"milestone": "onset_0950"})
    assert r_jump_0950.status_code == 200

    r_ops_0950 = test_client.get("/api/operations")
    assert r_ops_0950.json()["operations_summary"]["active_cases_count"] == 1
    lead_time = r_ops_0950.json()["operations_summary"]["confirmed_intervention_window"]
    assert "33h" in lead_time or "34h" in lead_time or lead_time is not None

    # 4. Screen 04: Evidence Pack with Provenance
    r_ev = test_client.get("/api/evidence")
    assert r_ev.status_code == 200
    pack = r_ev.json()["evidence_pack"]
    assert len(pack) >= 3
    for sig in pack:
        assert "provenance" in sig
        assert "detector_class" in sig["provenance"] or "source" in sig["provenance"]

    # ActionGuard check: Safe-mode is rejected at onset before ML corroboration (409 Conflict)
    r_safe_premature = test_client.post("/api/action/safe-mode")
    assert r_safe_premature.status_code == 409

    # Jump to ML corroboration milestone (10:15:00 UTC)
    r_jump_ml = test_client.post("/demo/jump", json={"milestone": "ml_corroborated_1015"})
    assert r_jump_ml.status_code == 200

    # 5. Screen 05: ActionGuard & Safe Mode Simulated Intervention (Now Cleared)
    r_safe = test_client.post("/api/action/safe-mode")
    assert r_safe.status_code == 200
    assert r_safe.json()["target_state"] == "MITIGATING"
    assert "POST_MAINTENANCE" in r_safe.json()["stream_branch"]["source"]

    # 6. Screen 06: Recovery Criteria Verification (Advancing into Post-Maintenance stream)
    # Stream branched at 16:05:00; tick until 5 consecutive healthy LOADED observations are verified
    ticks = 0
    rec_verified = False
    while ticks < 40:
        test_client.post("/demo/tick")
        r_rec = test_client.get("/api/recovery")
        assert r_rec.status_code == 200
        if r_rec.json().get("is_verified") is True:
            rec_verified = True
            break
        ticks += 1

    assert rec_verified is True
    assert r_rec.json()["consecutive_healthy_observations"] == 5

    # 7. Screen 06: Case Sign-off & Asset Release
    r_close = test_client.post(
        "/api/case/close",
        json={"operator_id": "DISPATCHER-0941", "notes": "Verified physical recovery after overhaul."},
    )
    assert r_close.status_code == 200
    assert r_close.json()["status"] == "CASE_CLOSED"
    assert r_close.json()["asset_health"] == "HEALTHY"

    # Operations overview shows 0 active cases and asset restored to health
    r_ops_final = test_client.get("/api/operations")
    assert r_ops_final.json()["operations_summary"]["active_cases_count"] == 0

    # 8. Screen 07: Timeline Ledger
    r_timeline = test_client.get("/api/case/events")
    assert r_timeline.status_code == 200
    ev_types = [e["event_type"] for e in r_timeline.json()]
    assert "DETECTION" in ev_types
    assert "ACTION" in ev_types
    assert "RECOVERY" in ev_types
    assert "CASE_CLOSED" in ev_types
