import json
from pathlib import Path
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.engine.lifecycle import IncidentLifecycleManager
from src.observability.metrics import DatadogMetricsClient
from src.storage.mongo_client import reset_in_memory_db
from src.storage.repository import CompressorGuardRepository


def _create_isolated_client() -> TestClient:
    reset_in_memory_db()
    repo = CompressorGuardRepository()
    metrics = DatadogMetricsClient(buffer_only=True)
    manager = IncidentLifecycleManager(repository=repo, metrics_client=metrics)
    app = create_app(manager=manager)
    return TestClient(app)


def test_mongodb_ttl_safety_and_three_aggregation_pipelines():
    """
    Verifies:
    1. No TTL index on historical `timestamp` in `measurements` (fixes 2020 TTL wipe bug).
    2. 7-day TTL index on `ingested_at` in `anomaly_signals`.
    3. Pipeline #1 ($setWindowFields) rolling stats via GET /api/telemetry/window.
    4. Pipeline #2 ($facet + $group) regime duty cycle & safety envelope via GET /api/telemetry/analytics.
    5. Pipeline #3 (failure_fingerprints cosine similarity matching) via GET /api/telemetry/analytics.
    """
    client = _create_isolated_client()
    manager: IncidentLifecycleManager = client.app.state.manager
    db = manager.repository.db

    # 1. Verify measurements index has NO expireAfterSeconds on historical timestamp
    meas_indexes = db["measurements"].index_information()
    assert any("timestamp" in str(idx) for idx in meas_indexes.values())
    for idx_info in meas_indexes.values():
        assert "expireAfterSeconds" not in idx_info

    # 2. Verify anomaly_signals has 7-day TTL index on wall-clock ingested_at
    sig_indexes = db["anomaly_signals"].index_information()
    ttl_indexes = [
        info for info in sig_indexes.values() if info.get("expireAfterSeconds") == 604800
    ]
    assert len(ttl_indexes) == 1
    assert ttl_indexes[0]["key"] == [("ingested_at", 1)]

    # 3. Jump to ML corroboration milestone (10:15) so telemetry and signals are ingested
    resp = client.post("/demo/reset", json={"milestone": "ml_corroborated_1015"})
    assert resp.status_code == 200

    # 4. Pipeline #1: GET /api/telemetry/window ($setWindowFields)
    win_resp = client.get("/api/telemetry/window?limit=25")
    assert win_resp.status_code == 200
    win_data = win_resp.json()
    assert win_data["asset_id"] == "APU-COMP-01"
    assert win_data["count"] > 0
    first_pt = win_data["points"][-1]
    assert "rolling_avg_dv" in first_pt
    assert "rolling_std_dv" in first_pt
    assert "rolling_avg_oil_temp" in first_pt

    # 5. Pipeline #2 & #3: GET /api/telemetry/analytics ($facet/$group + fingerprint similarity)
    ana_resp = client.get("/api/telemetry/analytics")
    assert ana_resp.status_code == 200
    ana_data = ana_resp.json()
    assert ana_data["asset_id"] == "APU-COMP-01"

    regime_ana = ana_data["regime_analytics"]
    assert regime_ana["total_samples_analyzed"] > 0
    assert regime_ana["loaded_duty_cycle_pct"] > 0.0
    assert len(regime_ana["regime_breakdown"]) >= 1
    assert "min_tp3_bar" in regime_ana

    # Verify failure fingerprint match ranks Failure #3 Air Leak #1 during Failure #3 degradation
    top_diag = ana_data["top_diagnosis"]
    assert top_diag is not None
    assert top_diag["fingerprint_id"] == "FP-METROPT3-FAIL-03"
    assert top_diag["similarity_score"] > 0.5
    assert top_diag["recommended_playbook"] is not None


def test_alert_fatigue_suppression_persisted_in_mongodb():
    """
    Verifies that transient spikes (such as 00:33:07 early excursion) are suppressed
    from opening a case and persisted as SUPPRESSED_TRANSIENT in anomaly_signals.
    """
    client = _create_isolated_client()

    # Jump to early excursion at 00:33:07
    resp = client.post("/demo/jump", json={"milestone": "early_excursion_0033"})
    assert resp.status_code == 200

    # Case must NOT be opened (state remains NONE)
    inc_resp = client.get("/api/incident")
    assert inc_resp.status_code == 200
    assert inc_resp.json()["lifecycle_state"] == "NONE"

    # Analytics must show suppressed transient signals in MongoDB
    ana_resp = client.get("/api/telemetry/analytics")
    assert ana_resp.status_code == 200
    fatigue = ana_resp.json()["alert_fatigue_protection"]
    assert fatigue["suppressed_transients_count"] >= 1
    assert len(fatigue["recent_suppressed_signals"]) >= 1
    sig0 = fatigue["recent_suppressed_signals"][0]
    assert sig0.get("status") == "SUPPRESSED_TRANSIENT" or sig0.get("disposition") == "SUPPRESSED_TRANSIENT"


def test_human_in_the_loop_operator_workflow_and_action_guard():
    """
    Verifies the complete Human-in-the-Loop operator workflow:
    - Causal runtime_warning vs Counterfactual lead_time
    - Live ActionGuard 5-check status including physical brake pressure (tp3_bar >= 7.0)
    - Acknowledge case -> Add shift note -> Create Work Order (Step 1) -> Safe Mode (Step 2)
    - False-positive operator override path
    """
    client = _create_isolated_client()

    # 1. Jump to onset_0950 (DETECTED)
    client.post("/demo/reset", json={"milestone": "onset_0950"})
    inc = client.get("/api/incident").json()
    assert inc["lifecycle_state"] == "DETECTED"
    assert inc["acknowledged"] is False
    # Causal runtime warning must be present and non-negative without look-ahead bias
    assert inc["runtime_warning"]["is_warning_active"] is True
    assert inc["runtime_warning"]["elapsed_warning_minutes"] >= 0
    assert inc["runtime_warning"]["brake_reservoir_tp3_bar"] >= 7.0
    # Counterfactual benchmark preserved
    assert inc["lead_time"]["lead_time_minutes"] == 2032
    assert inc["lead_time"]["lead_time_formatted"] == "33h 52m"

    # 2. Check ActionGuard at DETECTED -> denied because ML corroboration not yet reached
    guard_det = client.get("/api/action/guard-status").json()
    assert guard_det["is_permitted"] is False
    assert guard_det["total_checks"] == 5
    brake_check = next(c for c in guard_det["checklist"] if c["id"] == "BRAKE_RESERVOIR_PRESSURE_SAFE")
    assert brake_check["passed"] is True

    # 3. Operator acknowledges the case and adds a shift handover note
    ack_resp = client.post(
        "/api/case/acknowledge",
        json={
            "operator_id": "DISPATCHER-LISBON-07",
            "priority": "P1-CRITICAL",
            "note": "Confirmed abnormal DV pressure during morning peak.",
        },
    )
    assert ack_resp.status_code == 200
    assert ack_resp.json()["acknowledged"] is True
    assert ack_resp.json()["priority"] == "P1-CRITICAL"

    note_resp = client.post(
        "/api/case/notes",
        json={
            "operator_id": "DISPATCHER-LISBON-07",
            "note": "Contacted PMO Depot; bay 4 reserved for inspection.",
        },
    )
    assert note_resp.status_code == 200
    assert note_resp.json()["status"] == "NOTE_RECORDED"

    # 4. Jump to ml_corroborated_1015 (INVESTIGATING)
    client.post("/demo/jump", json={"milestone": "ml_corroborated_1015"})
    guard_inv = client.get("/api/action/guard-status").json()
    assert guard_inv["is_permitted"] is True
    assert guard_inv["passed_count"] == 5

    # 5. Step 1 of 2-step maintenance workflow: Dispatch Work Order
    wo_resp = client.post(
        "/api/case/work-order",
        json={
            "operator_id": "DISPATCHER-LISBON-07",
            "playbook_id": "PB-APU-03-AIR-LEAK",
            "target_depot": "PMO-DEPOT-LISBON-01",
            "maintenance_window": "NIGHT_SHIFT_WINDOW",
            "instructions": "Replace air dryer discharge pilot valve seal.",
        },
    )
    assert wo_resp.status_code == 200
    wo_data = wo_resp.json()
    assert wo_data["status"] == "DISPATCHED"
    assert wo_data["playbook_id"] == "PB-APU-03-AIR-LEAK"

    inc_after_wo = client.get("/api/incident").json()
    assert inc_after_wo["acknowledged"] is True
    assert inc_after_wo["work_order"]["work_order_id"] == wo_data["work_order_id"]

    # 6. Test False-Positive Override path on a fresh DETECTED case
    client.post("/demo/reset", json={"milestone": "onset_0950"})
    fp_resp = client.post(
        "/api/case/false-positive",
        json={
            "operator_id": "DISPATCHER-LISBON-07",
            "reason": "Scheduled pneumatic sensor calibration test.",
        },
    )
    assert fp_resp.status_code == 200
    assert fp_resp.json()["status"] == "CLOSED_FALSE_POSITIVE"
    assert fp_resp.json()["lifecycle_state"] == "RESOLVED"


def test_scenario_catalog_and_datadog_ai_observability():
    """
    Verifies:
    - GET /api/scenarios and POST /api/operations/scenario
    - Datadog dashboard.json (8 widgets) and monitors.json (3 monitors incl. AI Observability)
    - DatadogMetricsClient buffer captures telemetry.tp3_bar and ml.* metrics
    """
    client = _create_isolated_client()
    manager: IncidentLifecycleManager = client.app.state.manager

    # 1. Scenarios catalog & switching
    sc_resp = client.get("/api/scenarios")
    assert sc_resp.status_code == 200
    sc_data = sc_resp.json()
    assert sc_data["active_scenario_id"] == "failure_3"
    assert len(sc_data["scenarios"]) == 4

    sw_resp = client.post("/api/operations/scenario", json={"scenario_id": "healthy_baseline"})
    assert sw_resp.status_code == 200
    assert sw_resp.json()["scenario_id"] == "healthy_baseline"

    # Switch back to failure_3 and jump to 10:15
    client.post("/api/operations/scenario", json={"scenario_id": "failure_3"})
    client.post("/demo/jump", json={"milestone": "ml_corroborated_1015"})

    # 2. Check emitted Datadog metrics in buffer
    metric_names = {m["name"] for m in manager.metrics_client.buffered_metrics}
    assert "compressorguard.telemetry.dv_pressure_bar" in metric_names
    assert "compressorguard.telemetry.tp3_bar" in metric_names
    assert "compressorguard.telemetry.lps_active" in metric_names
    assert "compressorguard.ml.anomaly_score" in metric_names
    assert "compressorguard.ml.inference_latency_ms" in metric_names
    assert "compressorguard.ml.physics_agreement" in metric_names
    assert "compressorguard.incident.elapsed_warning_seconds" in metric_names

    # 3. Verify Datadog JSON config files
    dd_dash = json.loads(Path("datadog/dashboard.json").read_text(encoding="utf-8"))
    assert len(dd_dash["widgets"]) == 8

    dd_mons_doc = json.loads(Path("datadog/monitors.json").read_text(encoding="utf-8"))
    dd_mons = dd_mons_doc.get("monitors", dd_mons_doc) if isinstance(dd_mons_doc, dict) else dd_mons_doc
    assert len(dd_mons) == 3
    assert any("AI Observability" in m["name"] for m in dd_mons)
