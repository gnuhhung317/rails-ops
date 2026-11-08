"""
Targeted Verification Suite for Milestone 1 Backend Implementation.
Tests AssetRegistry, Repository Persistence, Schemas, and FastAPI Endpoints.
DO NOT RUN PYTEST on full repository. Run this script directly with python.
"""

import sys
from pathlib import Path

# Configure utf-8 encoding for Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient
from src.api.app import create_app
from src.domain.registry import AssetRegistry
from src.storage.mongo_client import InMemoryDatabase
from src.storage.repository import CompressorGuardRepository


def run_tests():
    print("=== STARTING M1 BACKEND VERIFICATION SUITE ===")
    
    # -------------------------------------------------------------------------
    # 1. AssetRegistry True Singleton & Domain Hierarchy
    # -------------------------------------------------------------------------
    print("\n--- 1. Testing AssetRegistry Singleton & Hierarchy ---")
    reg1 = AssetRegistry.get_default()
    reg2 = AssetRegistry.get_default()
    assert reg1 is reg2, "AssetRegistry.get_default() must return true singleton"
    
    trains = reg1.get_trains()
    assert len(trains) == 3, f"Expected 3 trains, got {len(trains)}"
    train_ids = [t["train_id"] for t in trains]
    assert train_ids == ["TRAIN-301", "TRAIN-302", "TRAIN-303"], f"Unexpected train order: {train_ids}"
    
    t302 = reg1.get_train("TRAIN-302")
    assert t302 is not None
    assert t302.health_status == "WARNING_P1"
    assert t302.brake_pressure_bar == 9.19
    assert t302.brake_safety_margin == "+2.19 bar"
    assert t302.safety_buffer == "33h 52m"
    
    comp_dryer = reg1.get_component("APU-DRY-LP49")
    assert comp_dryer is not None
    assert comp_dryer.status == "LEAKING"
    assert comp_dryer.leak_pressure_threshold_bar == 0.05
    assert comp_dryer.oil_temp_threshold_c == 67.0
    assert comp_dryer.last_updated_by == "Hùng Bùi (NV-0941)"
    
    kpis = reg1.get_operations_kpis()
    assert kpis["total_trains"] == "3/3"
    assert kpis["standby_depot"] == "Depot Long Bình"
    
    hero = reg1.get_hero_banner()
    assert hero["train_id"] == "TRAIN-302"
    assert hero["severity"] == "P1"
    assert hero["action_target"] == "view-workbench"
    
    tree = reg1.get_asset_hierarchy_tree()
    assert "fleet" in tree and "trains" in tree and "components" in tree
    print("[PASS] AssetRegistry unit tests: PASS")

    # -------------------------------------------------------------------------
    # 2. CompressorGuardRepository Persistence (InMemoryDatabase)
    # -------------------------------------------------------------------------
    print("\n--- 2. Testing CompressorGuardRepository Persistence ---")
    test_db = InMemoryDatabase("m1_test_db")
    repo = CompressorGuardRepository(db=test_db)
    
    # Check default seeded items
    configs = repo.get_all_component_configs()
    assert len(configs) >= 4, f"Expected >= 4 configs, got {len(configs)}"
    
    dryer_cfg = repo.get_component_config("APU-DRY-LP49")
    assert dryer_cfg is not None
    assert dryer_cfg["leak_pressure_threshold_bar"] == 0.05
    
    # Save updated config
    repo.save_component_config("APU-DRY-LP49", {
        "leak_pressure_threshold_bar": 0.075,
        "oil_temp_threshold_c": 68.5,
        "last_updated_by": "Hùng Bùi (NV-0941)",
    })
    dryer_cfg_updated = repo.get_component_config("APU-DRY-LP49")
    assert dryer_cfg_updated["leak_pressure_threshold_bar"] == 0.075
    assert dryer_cfg_updated["oil_temp_threshold_c"] == 68.5
    
    # SOP Playbooks
    sops = repo.get_all_sops()
    assert len(sops) >= 3, f"Expected >= 3 SOPs, got {len(sops)}"
    sop1 = repo.get_sop("SOP-APU-ISO-04")
    assert sop1 is not None
    assert sop1["priority"] == "P1"
    
    # Shift handovers
    handovers = repo.get_recent_shift_handovers(limit=5)
    assert len(handovers) >= 1
    new_h_id = repo.save_shift_handover({
        "shift_name": "Ca 2 (14:00 – 22:00)",
        "outgoing_operator": "Hùng Bùi (NV-0941)",
        "incoming_operator": "Trần Văn Nam (NV-1082)",
        "handover_notes": "Bàn giao ca bình thường.",
    })
    assert new_h_id.startswith("HO-")
    handovers_updated = repo.get_recent_shift_handovers(limit=5)
    assert any(h.get("handover_id") == new_h_id for h in handovers_updated)
    print("[PASS] CompressorGuardRepository tests: PASS")

    # -------------------------------------------------------------------------
    # 3. FastAPI Client Endpoints & Cross-Screen Dynamic Propagation
    # -------------------------------------------------------------------------
    print("\n--- 3. Testing REST API Endpoints & Dynamic Propagation ---")
    app = create_app()
    with TestClient(app) as client:
        # 3.1. GET /api/operations (Screen 1)
        res = client.get("/api/operations")
        assert res.status_code == 200, f"GET /api/operations failed: {res.text}"
        ops = res.json()
        assert "fleet" in ops
        assert "train" in ops
        assert "trains" in ops and len(ops["trains"]) == 3
        assert "kpis" in ops
        assert ops["kpis"]["total_trains"] == "3/3 đang chạy"
        assert ops["kpis"]["depot"] == "Depot Long Bình"
        assert "hero_banner" in ops
        assert ops["hero_banner"]["train_id"] == "TRAIN-302"
        assert ops["hero_banner"]["safety_buffer"] == "33h 52m"
        assert ops["hero_banner"]["action_target"] == "view-workbench"
        print("[PASS] GET /api/operations: PASS")

        # 3.2. GET /api/components (Screen 2)
        res = client.get("/api/components")
        assert res.status_code == 200, f"GET /api/components failed: {res.text}"
        comp_list = res.json()
        assert comp_list["total_count"] >= 4
        assert "tree" in comp_list
        assert any(c["component_id"] == "APU-DRY-LP49" for c in comp_list["components"])
        print("[PASS] GET /api/components: PASS")

        # 3.3. GET /api/components/{id} (Screen 2)
        res = client.get("/api/components/APU-DRY-LP49")
        assert res.status_code == 200, f"GET /api/components/APU-DRY-LP49 failed: {res.text}"
        dryer_detail = res.json()
        assert dryer_detail["component_id"] == "APU-DRY-LP49"
        assert dryer_detail["status"] == "LEAKING"
        assert "leak_pressure_threshold_bar" in dryer_detail
        assert "oil_temp_threshold_c" in dryer_detail
        assert "transient_filter" in dryer_detail
        assert "supervision_priority" in dryer_detail
        assert "maintenance_notes" in dryer_detail
        assert dryer_detail["last_updated_by"] == "Hùng Bùi (NV-0941)"
        print("[PASS] GET /api/components/APU-DRY-LP49: PASS")

        # 3.4. PUT /api/components/{id} (Screen 2 -> Screen 3 & Screen 4 propagation)
        put_payload = {
            "leak_pressure_threshold_bar": 0.08,
            "oil_temp_threshold_c": 69.5,
            "maintenance_depot": "Depot Long Bình",
            "transient_filter": True,
            "supervision_priority": "P1 - Khẩn cấp",
            "maintenance_notes": "Kiểm tra van xả pilot và độ màng cao su Viton",
            "operator_name": "Hùng Bùi (NV-0941)",
        }
        res = client.put("/api/components/APU-DRY-LP49", json=put_payload)
        assert res.status_code == 200, f"PUT /api/components/APU-DRY-LP49 failed: {res.text}"
        updated_data = res.json()
        assert updated_data["leak_pressure_threshold_bar"] == 0.08
        assert updated_data["oil_temp_threshold_c"] == 69.5
        assert updated_data["last_updated_by"] == "Hùng Bùi (NV-0941)"
        assert "audit_event" in updated_data
        assert updated_data["audit_event"]["actor"] == "Hùng Bùi (NV-0941)"
        print("[PASS] PUT /api/components/APU-DRY-LP49: PASS")

        # 3.5. Verify Dynamic Propagation on GET /api/recovery (Screen 3)
        res = client.get("/api/recovery")
        assert res.status_code == 200, f"GET /api/recovery failed: {res.text}"
        rec_data = res.json()
        assert rec_data["criteria"]["dv_pressure_max"] == 0.08, (
            f"Dynamic propagation failed! Expected dv_pressure_max=0.08, got {rec_data['criteria']['dv_pressure_max']}"
        )
        assert rec_data["criteria"]["oil_temp_max"] == 69.5, (
            f"Dynamic propagation failed! Expected oil_temp_max=69.5, got {rec_data['criteria']['oil_temp_max']}"
        )
        print("[PASS] Dynamic threshold propagation into /api/recovery: PASS")

        # 3.6. Verify Immutable Audit Ledger on GET /api/case/events (Screen 4)
        res = client.get("/api/case/events")
        assert res.status_code == 200, f"GET /api/case/events failed: {res.text}"
        events = res.json()
        config_update_events = [
            e for e in events 
            if e.get("phase") == "CONFIG_UPDATE" and e.get("actor") == "Hùng Bùi (NV-0941)"
        ]
        assert len(config_update_events) >= 1, "Audit ledger event for config update not found!"
        assert "0.08" in config_update_events[-1]["detail"]
        print("[PASS] Immutable Audit Ledger recording: PASS")

        # 3.7. SOP Playbooks Endpoints: GET/PUT /api/sop (Screen 4)
        res = client.get("/api/sop")
        assert res.status_code == 200
        sops_data = res.json()
        assert sops_data["total_count"] >= 3
        
        res = client.get("/api/sop/SOP-APU-ISO-04")
        assert res.status_code == 200
        assert res.json()["sop_id"] == "SOP-APU-ISO-04"

        res = client.put("/api/sop/SOP-APU-ISO-04", json={"title": "Quy trình cập nhật van xả khí LP49"})
        assert res.status_code == 200
        assert res.json()["title"] == "Quy trình cập nhật van xả khí LP49"
        print("[PASS] SOP endpoints (GET /api/sop, GET /api/sop/{id}, PUT /api/sop/{id}): PASS")

        # 3.8. Shift Handover Endpoints: GET /api/shift/current, POST /api/shift/handover (Screen 4)
        res = client.get("/api/shift/current")
        assert res.status_code == 200
        curr_shift = res.json()
        assert curr_shift["operator_name"] == "Hùng Bùi"
        assert curr_shift["operator_id"] == "NV-0941"

        handover_body = {
            "operator_name": "Hùng Bùi (NV-0941)",
            "incoming_operator": "Trần Văn Nam (NV-1082)",
            "shift_name": "Ca 2 (14:00 – 22:00)",
            "depot_location": "Depot Long Bình",
            "handover_notes": "Sự cố TRAIN-302 đã tạo work order, theo dõi nghiệm thu 5 mẫu tải.",
            "acknowledged_active_cases": ["APU-INC-20200605-01"],
        }
        res = client.post("/api/shift/handover", json=handover_body)
        assert res.status_code == 200, f"Shift handover failed: {res.text}"
        ho_res = res.json()
        assert ho_res["status"] == "HANDOVER_COMPLETED"
        assert ho_res["outgoing_operator"] == "Hùng Bùi (NV-0941)"
        assert ho_res["incoming_operator"] == "Trần Văn Nam (NV-1082)"
        print("[PASS] Shift handover endpoints (GET /api/shift/current, POST /api/shift/handover): PASS")

        # 3.9. Input Validation & Error Handling (400, 404)
        res = client.get("/api/components/NON_EXISTENT_COMP")
        assert res.status_code == 404
        
        res = client.put("/api/components/APU-DRY-LP49", json={"leak_pressure_threshold_bar": -0.5})
        assert res.status_code == 400
        
        res = client.post("/api/shift/handover", json={"incoming_operator": "", "handover_notes": ""})
        assert res.status_code == 400
        print("[PASS] Error handling matrix (400, 404): PASS")

    print("\n=== ALL M1 BACKEND VERIFICATION TESTS PASSED SUCCESSFULLY! ===")


if __name__ == "__main__":
    import os
    run_tests()
    os._exit(0)
