"""
Targeted Empirical Challenge Harness for Milestone 1 (Challenger 2).
Focus: Data Consistency, Persistence, Singleton Guarantee, Backward Compatibility, and Shift Handover Ordering.

STRICT INVARIANT: Standalone Python script. DO NOT run full repo pytest.
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime, timezone

# Windows UTF-8 stdout configuration
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Ensure fast loading with demo slice
demo_slice = REPO_ROOT / "dataset" / "MetroPT3-demo-slice.csv"
if demo_slice.exists():
    os.environ["TELEMETRY_CSV"] = str(demo_slice)

# Disable DD trace network flush
os.environ["DD_TRACE_ENABLED"] = "false"
os.environ["DD_INSTRUMENTATION_TELEMETRY_ENABLED"] = "false"

from fastapi.testclient import TestClient
from src.api.app import create_app
from src.domain.registry import AssetRegistry
from src.storage.mongo_client import (
    InMemoryDatabase,
    is_mongo_available,
    get_mongo_db,
    reset_in_memory_db,
)
from src.storage.repository import CompressorGuardRepository


def print_section(title: str):
    print("\n" + "=" * 70)
    print(f" CHALLENGE TEST: {title}")
    print("=" * 70)


# =============================================================================
# CHALLENGE 1: Persistence Across Repository Resets & In-Memory vs Real Mongo
# =============================================================================
def challenge_1_persistence_and_repository_resets():
    print_section("1. Persistence Across Repository Resets & Storage Engines")
    mongo_up = is_mongo_available()
    print(f"[*] Live MongoDB Available: {mongo_up}")

    # Test 1.1: Custom In-Memory Database Persistence Across Repository Instances
    print("[*] Testing custom InMemoryDatabase re-instantiation...")
    custom_db = InMemoryDatabase("test_challenge_db")
    repo1 = CompressorGuardRepository(db=custom_db)

    # Verify initial seeding occurred
    initial_configs = repo1.get_all_component_configs()
    assert len(initial_configs) == 4, f"Expected 4 default configs, got {len(initial_configs)}"

    # Update component config in repo1
    repo1.save_component_config("APU-DRY-LP49", {
        "leak_pressure_threshold_bar": 0.089,
        "oil_temp_threshold_c": 71.2,
        "maintenance_notes": "Adversarial persistence test check",
        "last_updated_by": "Challenger 2",
    })

    # Save a custom SOP in repo1
    repo1.save_sop("SOP-CHALLENGE-01", {
        "title": "Challenger SOP Title",
        "category": "Test Category",
        "priority": "P1",
        "steps": [{"step_number": 1, "action": "Test step"}],
    })

    # Save a custom shift handover in repo1
    h_id = repo1.save_shift_handover({
        "handover_id": "HND-CHALLENGE-001",
        "shift_name": "Ca 3 (22:00 – 06:00)",
        "outgoing_operator": "Operator A",
        "incoming_operator": "Operator B",
        "handover_notes": "Night shift test handover",
        "timestamp": "2026-11-08T00:00:00Z",
    })

    # Now create repo2 pointing to the SAME custom_db (simulating server reboot / worker restart)
    print("[*] Creating repo2 with same db instance (simulating worker restart)...")
    repo2 = CompressorGuardRepository(db=custom_db)

    # Check if repo2 still has updated values (did _init_enterprise_collections overwrite?)
    cfg = repo2.get_component_config("APU-DRY-LP49")
    assert cfg is not None, "Config APU-DRY-LP49 missing in repo2"
    assert cfg.get("leak_pressure_threshold_bar") == 0.089, (
        f"Data loss! Expected 0.089, got {cfg.get('leak_pressure_threshold_bar')}"
    )
    assert cfg.get("oil_temp_threshold_c") == 71.2, (
        f"Data loss! Expected 71.2, got {cfg.get('oil_temp_threshold_c')}"
    )
    print("  [PASS] Component config survived repository re-instantiation without overwrite.")

    sop = repo2.get_sop("SOP-CHALLENGE-01")
    assert sop is not None, "SOP-CHALLENGE-01 missing in repo2"
    assert sop.get("title") == "Challenger SOP Title"
    print("  [PASS] Custom SOP survived repository re-instantiation.")

    recent_h = repo2.get_recent_shift_handovers(limit=5)
    assert any(h.get("handover_id") == "HND-CHALLENGE-001" for h in recent_h), (
        "Handover HND-CHALLENGE-001 missing in repo2"
    )
    print("  [PASS] Shift handover survived repository re-instantiation.")

    # Test 1.2: Default get_mongo_db() backend behavior
    print("[*] Testing default get_mongo_db() backend...")
    default_db = get_mongo_db()
    repo_default = CompressorGuardRepository(db=default_db)
    all_sops = repo_default.get_all_sops()
    assert len(all_sops) >= 3, f"Expected >= 3 default SOPs in default db, got {len(all_sops)}"
    print(f"  [PASS] Default DB contains {len(all_sops)} SOPs.")


# =============================================================================
# CHALLENGE 2: Genuine Singleton Guarantees for AssetRegistry
# =============================================================================
def challenge_2_singleton_across_modules():
    print_section("2. AssetRegistry Singleton Guarantees Across Modules")

    # 2.1 Identity check in same module
    reg1 = AssetRegistry.get_default()
    reg2 = AssetRegistry.get_default()
    assert reg1 is reg2, "reg1 and reg2 are not the same object in memory!"
    print("  [PASS] Identity check reg1 is reg2 passed.")

    # 2.2 Re-import from sys.modules
    import importlib
    reg_module = importlib.import_module("src.domain.registry")
    reg3 = reg_module.AssetRegistry.get_default()
    assert reg1 is reg3, "AssetRegistry across re-import is NOT the same object!"
    print("  [PASS] Cross-import module identity reg1 is reg3 passed.")

    # 2.3 State mutation propagation through singleton
    test_note = f"Mutated by challenger test at {time.time()}"
    reg1.update_component("APU-COMP-01", {"maintenance_notes": test_note})
    assert reg3.get_component("APU-COMP-01").maintenance_notes == test_note, (
        "Mutation on reg1 was not reflected on reg3!"
    )
    print("  [PASS] In-place mutation on reg1 immediately observable on reg3.")

    # 2.4 Singleton reset behavior
    print("[*] Testing reset_default()...")
    reg_reset = AssetRegistry.reset_default()
    assert reg_reset is not reg1, "reset_default() must create a new instance!"
    reg4 = AssetRegistry.get_default()
    assert reg4 is reg_reset, "get_default() after reset must return new instance!"
    # The note should be restored to default
    assert reg4.get_component("APU-COMP-01").maintenance_notes != test_note, (
        "reset_default() did not restore default component attributes!"
    )
    print("  [PASS] reset_default() correctly replaced singleton with clean default state.")


# =============================================================================
# CHALLENGE 3: GET /api/operations Backward Compatibility
# =============================================================================
def challenge_3_operations_backward_compatibility():
    print_section("3. GET /api/operations Backward Compatibility")
    app = create_app()
    with TestClient(app) as client:
        resp = client.get("/api/operations")
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        data = resp.json()

        # 3.1 Verify existing required top-level fields
        required_fields = [
            "fleet",
            "train",
            "subsystem",
            "asset",
            "operations_summary",
            "active_case",
        ]
        for f in required_fields:
            assert f in data, f"CRITICAL: Field '{f}' missing in GET /api/operations response!"
            print(f"  [PASS] Verified top-level field '{f}' is present.")

        # 3.2 Deep check of 'fleet'
        fleet = data["fleet"]
        assert isinstance(fleet, dict), "'fleet' must be a dict"
        assert fleet.get("fleet_id") == "FLEET-METRO-01", f"Unexpected fleet_id: {fleet.get('fleet_id')}"
        assert "train_ids" in fleet, "'train_ids' missing in fleet"
        assert "Depot Long Bình" in str(fleet.get("depot_location", "")), "Depot location mismatch"

        # 3.3 Deep check of 'train'
        train = data["train"]
        assert isinstance(train, dict), "'train' must be a dict"
        assert train.get("train_id") == "TRAIN-302", f"Unexpected train_id: {train.get('train_id')}"
        assert "health_status" in train, "'health_status' missing in train"
        assert "speed_kmh" in train, "'speed_kmh' missing in train"
        assert "brake_pressure_bar" in train, "'brake_pressure_bar' missing in train"

        # 3.4 Deep check of 'subsystem'
        sub = data["subsystem"]
        assert isinstance(sub, dict), "'subsystem' must be a dict"
        assert sub.get("subsystem_id") == "SUB-APU-01", f"Unexpected subsystem_id: {sub.get('subsystem_id')}"
        assert sub.get("subsystem_code") == "APU"

        # 3.5 Deep check of 'asset'
        asset = data["asset"]
        assert isinstance(asset, dict), "'asset' must be a dict"
        assert asset.get("asset_id") == "APU-COMP-01", f"Unexpected asset_id: {asset.get('asset_id')}"
        assert "service_role" in asset, "'service_role' missing in asset"

        # 3.6 Deep check of 'operations_summary'
        summary = data["operations_summary"]
        assert isinstance(summary, dict), "'operations_summary' must be a dict"
        assert "monitored_assets_count" in summary
        assert "active_cases_count" in summary
        assert "simulation_mode" in summary
        assert summary.get("simulation_mode") == "LIVE_SIMULATION"

        # 3.7 Verify coexistence with new enterprise fields
        assert "trains" in data, "'trains' array missing"
        assert len(data["trains"]) == 3, f"Expected 3 trains, got {len(data['trains'])}"
        assert "kpis" in data, "'kpis' missing"
        assert "hero_banner" in data, "'hero_banner' missing"
        print("  [PASS] Complete schema compatibility verified: both legacy and new enterprise fields co-exist without collision.")


# =============================================================================
# CHALLENGE 4: Multiple Shift Handovers & Order Preservation
# =============================================================================
def challenge_4_shift_handover_multiple_and_ordering():
    print_section("4. POST /api/shift/handover Multiple Submissions & Ordering")
    app = create_app()
    with TestClient(app) as client:
        # Step 4.1: Submit multiple handovers with distinct seconds
        operators = [
            ("Hùng Bùi (NV-0941)", "Trần Văn Nam (NV-1082)", "Ca 2 (14:00 – 22:00)", "Bàn giao ca 2 lần 1"),
            ("Trần Văn Nam (NV-1082)", "Lê Hoàng Long (NV-1105)", "Ca 3 (22:00 – 06:00)", "Bàn giao ca 3 đêm"),
            ("Lê Hoàng Long (NV-1105)", "Hùng Bùi (NV-0941)", "Ca 1 (06:00 – 14:00)", "Bàn giao lại ca sáng"),
        ]

        handover_ids = []
        for out_op, in_op, shift, notes in operators:
            payload = {
                "operator_name": out_op,
                "incoming_operator": in_op,
                "shift_name": shift,
                "depot_location": "Depot Long Bình",
                "handover_notes": notes,
                "acknowledged_active_cases": ["APU-INC-20200605-01"],
            }
            time.sleep(1.05)
            resp = client.post("/api/shift/handover", json=payload)
            assert resp.status_code == 200, f"Handover failed: {resp.text}"
            res_data = resp.json()
            h_id = res_data["handover_id"]
            handover_ids.append(h_id)
            print(f"  [*] Created handover: {h_id} | {out_op} -> {in_op} | {shift}")

        # Verify all handover IDs are distinct
        assert len(handover_ids) == len(set(handover_ids)), (
            f"Handover IDs collided! {handover_ids}"
        )
        print("  [PASS] All handover IDs are unique when submitted with >= 1s intervals.")

        # Step 4.2: Verify repository retrieval preserves descending chronological order
        mgr = app.state.manager
        repo = mgr.repository
        recent_handovers = repo.get_recent_shift_handovers(limit=10)
        print(f"[*] Retrieved {len(recent_handovers)} handovers from repository.")

        # Verify timestamps are descending
        timestamps = [h.get("timestamp") for h in recent_handovers if h.get("timestamp")]
        print(f"[*] Timestamps order (top 4): {timestamps[:4]}")
        for i in range(len(timestamps) - 1):
            assert timestamps[i] >= timestamps[i + 1], (
                f"Ordering violation! Timestamp {timestamps[i]} is older than {timestamps[i+1]}"
            )
        print("  [PASS] Shift handovers correctly ordered in descending chronological order ($sort timestamp: -1).")

        # Step 4.3: Verify GET /api/shift/current reports the most recent handover time
        shift_resp = client.get("/api/shift/current")
        assert shift_resp.status_code == 200
        shift_data = shift_resp.json()
        assert shift_data.get("last_handover_time") == timestamps[0], (
            f"GET /api/shift/current last_handover_time mismatch! Expected {timestamps[0]}, got {shift_data.get('last_handover_time')}"
        )
        print("  [PASS] GET /api/shift/current accurately references newest handover timestamp.")

        # Step 4.4: Adversarial Stress Test - Sub-second Rapid Handovers (ID Collision Analysis)
        print("\n[*] Adversarial Stress Test: Sub-second rapid handover submissions...")
        rapid_ids = []
        for i in range(3):
            rapid_payload = {
                "operator_name": "Hùng Bùi (NV-0941)",
                "incoming_operator": f"Test In {i}",
                "shift_name": "Ca 2",
                "handover_notes": f"Rapid note {i}",
            }
            r_resp = client.post("/api/shift/handover", json=rapid_payload)
            assert r_resp.status_code == 200
            rapid_ids.append(r_resp.json()["handover_id"])
        
        print(f"[*] Rapid handover IDs generated: {rapid_ids}")
        distinct_ids = set(rapid_ids)
        if len(distinct_ids) < len(rapid_ids):
            print("  [VULNERABILITY CONFIRMED] Sub-second rapid handovers generated DUPLICATE handover_id!")
            print(f"  [DETAILS] {len(rapid_ids)} rapid submissions produced only {len(distinct_ids)} distinct ID(s): {rapid_ids}")
            print("  [ROOT CAUSE] handover_id generator uses second resolution: f'HND-{now.strftime(\"%Y%m%d%H%M%S\")}'")
            print("  [BLAST RADIUS] Rapid handovers within the same second overwrite previous handovers in Mongo/InMemory via update_one upsert.")
        else:
            print("  [PASS] Rapid handover IDs were unique.")


# =============================================================================
# CHALLENGE 5: Edge Cases, Input Validation, and Error Boundaries
# =============================================================================
def challenge_5_adversarial_edge_cases():
    print_section("5. Adversarial Edge Cases & Error Boundaries")
    app = create_app()
    with TestClient(app) as client:
        # 5.1 Empty string validation on shift handover
        bad_payloads = [
            {"incoming_operator": "   ", "handover_notes": "Note"},
            {"incoming_operator": "Valid Op", "handover_notes": "   "},
            {"incoming_operator": "", "handover_notes": ""},
        ]
        for p in bad_payloads:
            r = client.post("/api/shift/handover", json=p)
            assert r.status_code == 400, f"Expected 400 for payload {p}, got {r.status_code}"
        print("  [PASS] Shift handover rejects empty/whitespace-only operator and notes with 400.")

        # 5.2 Negative or zero thresholds on component update
        bad_thresholds = [
            {"leak_pressure_threshold_bar": 0.0},
            {"leak_pressure_threshold_bar": -0.05},
            {"oil_temp_threshold_c": 0.0},
            {"oil_temp_threshold_c": -10.0},
        ]
        for bt in bad_thresholds:
            r = client.put("/api/components/APU-DRY-LP49", json=bt)
            assert r.status_code == 400, f"Expected 400 for payload {bt}, got {r.status_code}"
        print("  [PASS] Component update rejects non-positive thresholds with 400.")

        # 5.3 Non-existent component ID lookup and update
        r404_get = client.get("/api/components/NON_EXISTENT_999")
        assert r404_get.status_code == 404, f"Expected 404, got {r404_get.status_code}"
        r404_put = client.put("/api/components/NON_EXISTENT_999", json={"maintenance_depot": "Depot X"})
        assert r404_put.status_code == 404, f"Expected 404, got {r404_put.status_code}"
        print("  [PASS] Non-existent component correctly returns 404.")

        # 5.4 Non-existent SOP lookup
        r404_sop = client.get("/api/sop/SOP-NONEXISTENT")
        assert r404_sop.status_code == 404, f"Expected 404, got {r404_sop.status_code}"
        print("  [PASS] Non-existent SOP correctly returns 404.")


def main():
    print("=" * 70)
    print(" STARTING ADVERSARIAL CHALLENGER 2 VERIFICATION SUITE")
    print("=" * 70)
    
    challenge_1_persistence_and_repository_resets()
    challenge_2_singleton_across_modules()
    challenge_3_operations_backward_compatibility()
    challenge_4_shift_handover_multiple_and_ordering()
    challenge_5_adversarial_edge_cases()

    print("\n" + "=" * 70)
    print(" ALL CHALLENGE SUITES COMPLETED EMPIRICALLY!")
    print("=" * 70)


if __name__ == "__main__":
    main()
