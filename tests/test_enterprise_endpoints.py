"""
tests/test_enterprise_endpoints.py
===================================
Targeted Endpoint Verification Suite for CompressorGuard Enterprise UI/UX.

MANDATORY RULES:
- ZERO PYTEST ON FULL REPO: This test file must only be executed directly:
    python tests/test_enterprise_endpoints.py
  or specifically:
    pytest tests/test_enterprise_endpoints.py -v
- Verifies Tier 2 features:
    * F3: Backend REST Endpoints (GET /api/operations, GET /api/components, PUT /api/components/{id}, SOP & Shift)
    * F4: Dynamic Threshold & Audit Propagation (propagation to recovery verifier & audit ledger for Hùng Bùi NV-0941)
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Use demo slice CSV and disable DD trace network flush during local testing
demo_slice = REPO_ROOT / "dataset" / "MetroPT3-demo-slice.csv"
if demo_slice.exists():
    os.environ.setdefault("TELEMETRY_CSV", str(demo_slice))

os.environ["DD_TRACE_ENABLED"] = "false"
os.environ["DD_INSTRUMENTATION_TELEMETRY_ENABLED"] = "false"

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from fastapi.testclient import TestClient
from src.api.app import create_app


_CLIENT = None

def get_client() -> TestClient:
    global _CLIENT
    if _CLIENT is None:
        app = create_app()
        _CLIENT = TestClient(app)
    return _CLIENT


def test_operations_overview_hierarchy_and_backward_compatibility():
    """Validates GET /api/operations preserves backward compatibility for existing consumers."""
    client = get_client()
    resp = client.get("/api/operations")
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()

    # Preserves core hierarchy
    assert "fleet" in data, "Missing 'fleet' in /api/operations"
    assert data["fleet"].get("fleet_id") == "FLEET-METRO-01"
    assert "train" in data, "Missing 'train' in /api/operations"
    assert "subsystem" in data, "Missing 'subsystem' in /api/operations"
    assert "asset" in data, "Missing 'asset' in /api/operations"
    assert "operations_summary" in data, "Missing 'operations_summary' in /api/operations"


def test_operations_fleet_grid_trains():
    """Validates GET /api/operations returns the 3 fleet trains (TRAIN-301, TRAIN-302, TRAIN-303)."""
    client = get_client()
    resp = client.get("/api/operations")
    assert resp.status_code == 200
    data = resp.json()

    assert "trains" in data, "Missing 'trains' list in /api/operations for Fleet Grid Cards"
    trains = {t["train_id"]: t for t in data["trains"]}

    assert "TRAIN-301" in trains, "TRAIN-301 missing in fleet trains"
    assert "TRAIN-302" in trains, "TRAIN-302 missing in fleet trains"
    assert "TRAIN-303" in trains, "TRAIN-303 missing in fleet trains"

    # Status checks
    t301 = trains["TRAIN-301"]
    t302 = trains["TRAIN-302"]
    t303 = trains["TRAIN-303"]

    assert t301.get("status") in ("NORMAL", "OK", "HEALTHY", "REVENUE_SERVICE"), f"Unexpected status for TRAIN-301: {t301.get('status')}"
    assert t303.get("status") in ("NORMAL", "OK", "HEALTHY", "REVENUE_SERVICE"), f"Unexpected status for TRAIN-303: {t303.get('status')}"
    assert t302.get("status") in ("WARNING_P1", "WARNING", "CRITICAL", "LEAKING", "ALERT"), f"Unexpected status for TRAIN-302: {t302.get('status')}"


def test_operations_kpis_and_p1_hero_banner():
    """Validates GET /api/operations returns operational KPIs and P1 warning hero banner."""
    client = get_client()
    resp = client.get("/api/operations")
    assert resp.status_code == 200
    data = resp.json()

    # Operational KPIs
    assert "kpis" in data, "Missing 'kpis' in /api/operations"
    kpis = data["kpis"]
    total = str(kpis.get("total_trains", ""))
    assert "3" in total, f"Expected total trains 3/3, got {total}"
    assert kpis.get("normal_trains") == 2, f"Expected 2 normal trains, got {kpis.get('normal_trains')}"
    assert kpis.get("alerted_trains") == 1 or kpis.get("alert_trains") == 1, "Expected 1 alerted train"
    depot = kpis.get("depot") or kpis.get("standby_depot", "")
    assert "Long Bình" in str(depot), f"Expected Depot Long Bình, got {depot}"

    # P1 Warning Hero Banner
    assert "hero_banner" in data, "Missing 'hero_banner' in /api/operations"
    hero = data["hero_banner"]
    assert hero.get("active") is True or hero.get("is_active") is True, "Hero banner must be active for TRAIN-302"
    assert hero.get("train_id") == "TRAIN-302", f"Expected TRAIN-302 in hero banner, got {hero.get('train_id')}"
    buffer = str(hero.get("safety_buffer", ""))
    assert "33h" in buffer or "33 giờ" in buffer, f"Expected ~33h safety buffer, got {buffer}"


def test_components_catalog_endpoint():
    """Validates GET /api/components returns all 4 APU subcomponents with required attributes."""
    client = get_client()
    resp = client.get("/api/components")
    assert resp.status_code == 200, f"GET /api/components returned {resp.status_code}: {resp.text}"
    components_data = resp.json()

    comp_list = components_data if isinstance(components_data, list) else components_data.get("components", [])
    assert len(comp_list) >= 4, f"Expected at least 4 components, got {len(comp_list)}"

    comp_map = {c["component_id"]: c for c in comp_list}
    expected_ids = ["APU-COMP-01", "APU-DRY-LP49", "APU-RES-TP3", "APU-SW-LPS"]
    for cid in expected_ids:
        assert cid in comp_map, f"Missing component {cid} in /api/components"
        comp = comp_map[cid]
        assert "name" in comp, f"Component {cid} missing 'name'"
        assert "status" in comp or "status_label" in comp, f"Component {cid} missing status"
        assert "leak_pressure_threshold_bar" in comp, f"Component {cid} missing leak_pressure_threshold_bar"
        assert "oil_temp_threshold_c" in comp, f"Component {cid} missing oil_temp_threshold_c"
        assert "maintenance_depot" in comp, f"Component {cid} missing maintenance_depot"


def test_single_component_detail_and_404():
    """Validates GET /api/components/{id} returns details for existing component and 404 for unknown."""
    client = get_client()

    # Valid lookup
    resp = client.get("/api/components/APU-DRY-LP49")
    assert resp.status_code == 200, f"Expected 200 for APU-DRY-LP49, got {resp.status_code}"
    comp = resp.json()
    assert comp["component_id"] == "APU-DRY-LP49"
    assert "LP49" in comp["name"] or "sấy" in comp["name"] or "Dryer" in comp["name"]

    # Invalid lookup
    resp_404 = client.get("/api/components/NON_EXISTENT_COMPONENT_XYZ")
    assert resp_404.status_code == 404, f"Expected 404 for unknown component, got {resp_404.status_code}"


def test_component_config_update_and_dynamic_propagation():
    """
    Validates PUT /api/components/{id} updates config, persists changes,
    propagates thresholds to recovery verification, and appends an audit event for Hùng Bùi (NV-0941).
    """
    client = get_client()

    update_payload: Dict[str, Any] = {
        "leak_pressure_threshold_bar": 0.04,
        "oil_temp_threshold_c": 65.5,
        "maintenance_depot": "Depot Long Bình",
        "transient_filter": True,
        "supervision_priority": "P1 - Khẩn cấp",
        "maintenance_notes": "Kiểm tra định kỳ van xả LP49 và thay gioăng cao su chịu nhiệt",
        "operator_id": "Hùng Bùi (NV-0941)",
    }

    put_resp = client.put("/api/components/APU-DRY-LP49", json=update_payload)
    assert put_resp.status_code == 200, f"PUT /api/components/APU-DRY-LP49 failed with {put_resp.status_code}: {put_resp.text}"
    updated = put_resp.json()
    assert updated.get("leak_pressure_threshold_bar") == 0.04
    assert updated.get("oil_temp_threshold_c") == 65.5
    assert updated.get("maintenance_depot") == "Depot Long Bình"

    # 1. Verify Dynamic Propagation to Recovery Endpoint
    rec_resp = client.get("/api/recovery")
    assert rec_resp.status_code == 200
    rec_data = rec_resp.json()
    # Check criteria in recovery payload
    criteria = rec_data.get("criteria", {})
    if criteria:
        assert criteria.get("dv_pressure_max") == 0.04 or criteria.get("leak_pressure_max") == 0.04, (
            f"Expected dv_pressure_max criteria to propagate to 0.04, got {criteria.get('dv_pressure_max')}"
        )
        assert criteria.get("oil_temp_max") == 65.5, (
            f"Expected oil_temp_max criteria to propagate to 65.5, got {criteria.get('oil_temp_max')}"
        )

    # 2. Verify Audit Ledger records event under operator Hùng Bùi (NV-0941)
    events_resp = client.get("/api/case/events")
    assert events_resp.status_code == 200
    events = events_resp.json()
    matching_events = [
        e for e in events
        if ("Hùng Bùi" in str(e.get("actor", "")) or "NV-0941" in str(e.get("actor", "")))
        and ("APU-DRY-LP49" in str(e) or "cấu hình" in str(e).lower() or "CONFIG" in str(e).upper())
    ]
    assert len(matching_events) >= 1, "Audit ledger must record an event for Hùng Bùi (NV-0941) updating component config"


def test_sop_playbooks_endpoint():
    """Validates GET /api/sop returns list of industrial standard operating procedures."""
    client = get_client()
    resp = client.get("/api/sop")
    assert resp.status_code == 200, f"GET /api/sop failed with {resp.status_code}: {resp.text}"
    sops = resp.json()
    sop_list = sops if isinstance(sops, list) else sops.get("playbooks", [])
    assert len(sop_list) >= 1, "Expected at least one SOP playbook"

    sop_codes = [s.get("sop_id") or s.get("id") or s.get("code") for s in sop_list]
    assert any("SOP-APU" in str(code) for code in sop_codes), f"Expected SOP-APU playbook, got {sop_codes}"


def test_shift_management_endpoints():
    """Validates GET /api/shift/current returns Hùng Bùi NV-0941 and POST /api/shift/handover succeeds."""
    client = get_client()

    # 1. GET Current Shift
    shift_resp = client.get("/api/shift/current")
    assert shift_resp.status_code == 200, f"GET /api/shift/current failed: {shift_resp.text}"
    shift = shift_resp.json()
    assert "Hùng Bùi" in shift.get("operator_name", "") or "NV-0941" in shift.get("operator_code", "") or "NV-0941" in shift.get("operator_id", "")
    assert "Ca 1" in str(shift.get("shift_name", "")) or "06:00" in str(shift.get("shift_time", ""))

    # 2. POST Shift Handover
    handover_payload = {
        "operator_id": "Hùng Bùi (NV-0941)",
        "incoming_operator_id": "NV-1177",
        "incoming_operator_name": "Nguyễn Văn A",
        "notes": "Bàn giao ca trực sáng: tiếp tục giám sát rò rỉ khí TRAIN-302",
    }
    post_resp = client.post("/api/shift/handover", json=handover_payload)
    assert post_resp.status_code in (200, 201), f"POST /api/shift/handover failed with {post_resp.status_code}: {post_resp.text}"


# =====================================================================
# Standalone CLI Test Runner
# =====================================================================
def run_all_tests():
    tests = [
        ("Operations Hierarchy & Backward Compatibility", test_operations_overview_hierarchy_and_backward_compatibility),
        ("Operations Fleet Grid Trains (301, 302, 303)", test_operations_fleet_grid_trains),
        ("Operations KPIs & P1 Hero Banner", test_operations_kpis_and_p1_hero_banner),
        ("APU Components Catalog", test_components_catalog_endpoint),
        ("Single Component Detail & 404 Handling", test_single_component_detail_and_404),
        ("Component Config Update & Dynamic Propagation", test_component_config_update_and_dynamic_propagation),
        ("SOP Playbooks Catalog", test_sop_playbooks_endpoint),
        ("Shift Management for Hùng Bùi (NV-0941)", test_shift_management_endpoints),
    ]

    print("\n" + "=" * 78)
    print(" COMPRESSORGUARD ENTERPRISE ENDPOINT TEST RUNNER (TIER 2)")
    print("=" * 78)

    passed = 0
    failed = 0
    results = []

    for name, test_func in tests:
        try:
            test_func()
            results.append((name, "PASS", ""))
            passed += 1
            print(f"  [PASS] {name}")
        except Exception as e:
            results.append((name, "FAIL", str(e)))
            failed += 1
            print(f"  [FAIL] {name}: {e}")

    print("-" * 78)
    print(f"Total Tests: {len(tests)} | Passed: {passed} | Failed: {failed}")
    print("=" * 78 + "\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
