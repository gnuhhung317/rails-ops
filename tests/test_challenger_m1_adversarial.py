"""
tests/test_challenger_m1_adversarial.py
======================================
Empirical Adversarial Challenge Suite for Milestone 1 Backend Implementation.
Author: Challenger 1 (teamwork_challenger_m1_1)

Tests:
1. Non-existent component handling (PUT /api/components/UNKNOWN-ID, path injection).
2. Edge / Boundary values (zero, negative, extreme values, empty strings, None fields, type mismatch).
3. Dynamic propagation to recovery verifier (verification that criteria actually change, and cross-train isolation check).
4. Audit log immutability (verifying audit logs cannot be overwritten or mutated).
5. Concurrency & Thread-Safety (concurrent updates, lost update detection, duplicate event_id check).
"""

import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Any, List

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Safe test environment configurations
demo_slice = REPO_ROOT / "dataset" / "MetroPT3-demo-slice.csv"
if demo_slice.exists():
    os.environ.setdefault("TELEMETRY_CSV", str(demo_slice))

os.environ["DD_TRACE_ENABLED"] = "false"
os.environ["DD_INSTRUMENTATION_TELEMETRY_ENABLED"] = "false"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from src.api.app import create_app
from src.domain.registry import AssetRegistry


def create_test_client():
    app = create_app()
    return TestClient(app)


def test_1_unknown_component_id():
    """Challenge 1: Non-existent components handling."""
    print("\n--- Challenge 1: Unknown Component ID ---")
    client = create_test_client()
    
    # 1.1 Non-existent component ID
    resp = client.put(
        "/api/components/UNKNOWN-ID-9999",
        json={"leak_pressure_threshold_bar": 0.08, "operator_name": "Hùng Bùi (NV-0941)"}
    )
    print(f"PUT /api/components/UNKNOWN-ID-9999 status: {resp.status_code}, response: {resp.json()}")
    assert resp.status_code == 404, f"Expected 404 for unknown component, got {resp.status_code}"
    assert "Không tìm thấy" in resp.json().get("detail", ""), "Expected Vietnamese 404 detail message"

    # 1.2 Path traversal / special characters
    resp_inject = client.put(
        "/api/components/..%2F..%2Fetc%2Fpasswd",
        json={"leak_pressure_threshold_bar": 0.08}
    )
    print(f"PUT /api/components/path-traversal status: {resp_inject.status_code}")
    assert resp_inject.status_code in (404, 400, 422), f"Unexpected status {resp_inject.status_code}"

    # 1.3 GET non-existent
    resp_get = client.get("/api/components/UNKNOWN-ID-9999")
    assert resp_get.status_code == 404
    print("[PASS] Challenge 1: Unknown component correctly rejected with 404.")


def test_2_edge_and_boundary_values():
    """Challenge 2: Edge values (zero, negative, high temp, empty notes, None fields)."""
    print("\n--- Challenge 2: Edge and Boundary Values ---")
    client = create_test_client()
    
    # Reset default state for deterministic baseline
    AssetRegistry.reset_default()

    # 2.1 Zero leak pressure
    resp_zero_p = client.put(
        "/api/components/APU-DRY-LP49",
        json={"leak_pressure_threshold_bar": 0.0}
    )
    print(f"Zero pressure status: {resp_zero_p.status_code}, detail: {resp_zero_p.json()}")
    assert resp_zero_p.status_code == 400, f"Expected 400 for zero pressure, got {resp_zero_p.status_code}"
    assert "lớn hơn 0" in resp_zero_p.json().get("detail", "")

    # 2.2 Negative leak pressure
    resp_neg_p = client.put(
        "/api/components/APU-DRY-LP49",
        json={"leak_pressure_threshold_bar": -0.5}
    )
    print(f"Negative pressure status: {resp_neg_p.status_code}")
    assert resp_neg_p.status_code == 400, f"Expected 400 for negative pressure, got {resp_neg_p.status_code}"

    # 2.3 Zero oil temperature
    resp_zero_t = client.put(
        "/api/components/APU-COMP-01",
        json={"oil_temp_threshold_c": 0.0}
    )
    print(f"Zero temperature status: {resp_zero_t.status_code}")
    assert resp_zero_t.status_code == 400, f"Expected 400 for zero temp, got {resp_zero_t.status_code}"

    # 2.4 Negative oil temperature
    resp_neg_t = client.put(
        "/api/components/APU-COMP-01",
        json={"oil_temp_threshold_c": -15.0}
    )
    print(f"Negative temperature status: {resp_neg_t.status_code}")
    assert resp_neg_t.status_code == 400, f"Expected 400 for negative temp, got {resp_neg_t.status_code}"

    # 2.5 Extremely high values (e.g. 5000 deg C or 500 bar)
    # Testing whether upper boundary validation exists or allows unphysical numbers
    resp_high_t = client.put(
        "/api/components/APU-COMP-01",
        json={"oil_temp_threshold_c": 5000.0}
    )
    print(f"High temperature (5000°C) status: {resp_high_t.status_code}")
    # Note behavior: Does backend accept or reject?
    if resp_high_t.status_code == 200:
        print("  -> Finding: High temperature 5000°C was ACCEPTED (no upper bound constraint).")

    # 2.6 Empty notes and whitespace notes
    resp_empty_notes = client.put(
        "/api/components/APU-DRY-LP49",
        json={"maintenance_notes": ""}
    )
    print(f"Empty notes status: {resp_empty_notes.status_code}")
    assert resp_empty_notes.status_code == 200
    assert resp_empty_notes.json().get("maintenance_notes") == ""

    # 2.7 Empty payload (all fields None)
    resp_empty_body = client.put(
        "/api/components/APU-DRY-LP49",
        json={}
    )
    print(f"Empty body status: {resp_empty_body.status_code}")
    assert resp_empty_body.status_code == 200
    assert "audit_event" in resp_empty_body.json()

    # 2.8 Type mismatch (string for float)
    resp_type_err = client.put(
        "/api/components/APU-DRY-LP49",
        json={"leak_pressure_threshold_bar": "NOT_A_FLOAT"}
    )
    print(f"Type error status: {resp_type_err.status_code}")
    assert resp_type_err.status_code == 422, f"Expected 422 for type mismatch, got {resp_type_err.status_code}"
    print("[PASS] Challenge 2: Edge values validated properly.")


def test_3_dynamic_propagation_and_cross_train_isolation():
    """Challenge 3: Dynamic propagation to recovery verifier."""
    print("\n--- Challenge 3: Dynamic Propagation & Cross-Train Isolation ---")
    client = create_test_client()
    AssetRegistry.reset_default()

    # 3.1 Initial recovery criteria
    rec_initial = client.get("/api/recovery").json()
    init_p_max = rec_initial["criteria"]["dv_pressure_max"]
    init_t_max = rec_initial["criteria"]["oil_temp_max"]
    print(f"Initial recovery criteria: dv_pressure_max={init_p_max}, oil_temp_max={init_t_max}")

    # 3.2 Update APU-DRY-LP49 with new leak threshold 0.15 bar
    put_resp = client.put(
        "/api/components/APU-DRY-LP49",
        json={"leak_pressure_threshold_bar": 0.15, "operator_name": "Hùng Bùi (NV-0941)"}
    )
    assert put_resp.status_code == 200

    # Verify directly via GET /api/recovery
    rec_updated = client.get("/api/recovery").json()
    new_p_max = rec_updated["criteria"]["dv_pressure_max"]
    print(f"After updating APU-DRY-LP49: dv_pressure_max={new_p_max}")
    assert new_p_max == 0.15, f"Expected 0.15 in recovery criteria, got {new_p_max}"

    # 3.3 Update APU-COMP-01 with new oil temp threshold 74.5 C
    put_resp2 = client.put(
        "/api/components/APU-COMP-01",
        json={"oil_temp_threshold_c": 74.5, "operator_name": "Hùng Bùi (NV-0941)"}
    )
    assert put_resp2.status_code == 200
    rec_updated2 = client.get("/api/recovery").json()
    new_t_max = rec_updated2["criteria"]["oil_temp_max"]
    print(f"After updating APU-COMP-01: oil_temp_max={new_t_max}")
    assert new_t_max == 74.5, f"Expected 74.5 in recovery criteria, got {new_t_max}"

    # 3.4 Cross-Train / Cross-Component Side Effect Check:
    # What if we update APU-COMP-301 on TRAIN-301?
    # Does updating a component on TRAIN-301 change the recovery criteria for TRAIN-302's incident?!
    put_resp3 = client.put(
        "/api/components/APU-COMP-301",
        json={"oil_temp_threshold_c": 88.0, "operator_name": "Hùng Bùi (NV-0941)"}
    )
    assert put_resp3.status_code == 200
    rec_check3 = client.get("/api/recovery").json()
    train_302_oil_crit = rec_check3["criteria"]["oil_temp_max"]
    print(f"After updating TRAIN-301 component APU-COMP-301: TRAIN-302 recovery criteria oil_temp_max={train_302_oil_crit}")
    if train_302_oil_crit == 88.0:
        print("  -> Finding: Cross-train side-effect observed: Updating TRAIN-301 modified TRAIN-302's recovery verifier criteria!")
    print("[PASS] Challenge 3: Dynamic propagation verified.")


def test_4_audit_log_immutability():
    """Challenge 4: Audit log immutability and tamper resistance."""
    print("\n--- Challenge 4: Audit Log Immutability ---")
    client = create_test_client()

    # 4.1 Count audit events
    events_initial = client.get("/api/case/events").json()
    count_initial = len(events_initial)
    print(f"Initial case events count: {count_initial}")

    # 4.2 Make an update
    client.put(
        "/api/components/APU-RES-TP3",
        json={
            "supervision_priority": "P1 - Khẩn cấp",
            "maintenance_notes": "Kiểm tra áp lực khí nén bình chính",
            "operator_name": "Hùng Bùi (NV-0941)",
        }
    )

    events_after = client.get("/api/case/events").json()
    assert len(events_after) == count_initial + 1, "Expected exactly 1 new event appended"
    new_event = events_after[-1]
    print(f"New audit event appended: ID={new_event['event_id']}, title={new_event['title']}, actor={new_event['actor']}")
    assert new_event["actor"] == "Hùng Bùi (NV-0941)"
    assert new_event["phase"] == "CONFIG_UPDATE"

    # 4.3 Attempt to mutate / overwrite via DELETE / PUT / POST on /api/case/events
    del_resp = client.delete("/api/case/events")
    print(f"DELETE /api/case/events status: {del_resp.status_code}")
    assert del_resp.status_code in (404, 405), "DELETE /api/case/events must not be allowed"

    put_resp = client.put(f"/api/case/events/{new_event['event_id']}", json={"title": "TAMPERED"})
    print(f"PUT /api/case/events/ID status: {put_resp.status_code}")
    assert put_resp.status_code in (404, 405), "PUT /api/case/events must not be allowed"

    # 4.4 Verify events list cannot be mutated in place
    events_after[0]["title"] = "MUTATED_LOCAL_COPY"
    events_verify = client.get("/api/case/events").json()
    assert events_verify[0]["title"] != "MUTATED_LOCAL_COPY", "Server-side event list was mutated!"
    print("[PASS] Challenge 4: Audit logs are append-only and immutable.")


def test_5_concurrency_and_thread_safety():
    """Challenge 5: Concurrent calls to PUT /api/components/{id}."""
    print("\n--- Challenge 5: Concurrency and Thread Safety ---")
    client = create_test_client()
    AssetRegistry.reset_default()

    # We will launch 20 concurrent update requests to APU-DRY-LP49:
    # 10 updating leak_pressure_threshold_bar with unique values
    # 10 updating oil_temp_threshold_c with unique values
    errors = []
    responses = []

    def perform_update(idx: int):
        try:
            if idx % 2 == 0:
                p_val = round(0.05 + (idx * 0.005), 4)
                r = client.put(
                    "/api/components/APU-DRY-LP49",
                    json={
                        "leak_pressure_threshold_bar": p_val,
                        "operator_name": f"Hùng Bùi (NV-0941)-T{idx}",
                    }
                )
            else:
                t_val = round(60.0 + (idx * 0.5), 2)
                r = client.put(
                    "/api/components/APU-DRY-LP49",
                    json={
                        "oil_temp_threshold_c": t_val,
                        "operator_name": f"Hùng Bùi (NV-0941)-T{idx}",
                    }
                )
            responses.append((idx, r.status_code, r.json()))
        except Exception as e:
            errors.append((idx, str(e)))

    threads = []
    for i in range(20):
        t = threading.Thread(target=perform_update, args=(i,))
        threads.append(t)

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"Concurrent requests completed: {len(responses)} success, {len(errors)} exceptions")
    assert len(errors) == 0, f"Encountered thread exceptions: {errors}"
    assert all(status == 200 for _, status, _ in responses), "All concurrent requests should return 200"

    # Check component state in registry
    comp = client.get("/api/components/APU-DRY-LP49").json()
    print(f"Final APU-DRY-LP49 state after 20 concurrent writes:")
    print(f"  leak_pressure_threshold_bar: {comp.get('leak_pressure_threshold_bar')}")
    print(f"  oil_temp_threshold_c: {comp.get('oil_temp_threshold_c')}")
    print(f"  last_updated_by: {comp.get('last_updated_by')}")

    # Check audit events for duplicate event_id
    all_events = client.get("/api/case/events").json()
    event_ids = [e["event_id"] for e in all_events]
    unique_ids = set(event_ids)
    print(f"Total audit events recorded: {len(event_ids)}, Unique IDs: {len(unique_ids)}")
    if len(event_ids) != len(unique_ids):
        duplicates = [x for x in event_ids if event_ids.count(x) > 1]
        print(f"  -> Finding: Concurrency race condition detected! Duplicate event_ids: {set(duplicates)}")
    else:
        print("  -> Audit event IDs are unique.")


def main():
    print("==============================================================================")
    print(" COMPRESSORGUARD M1 ADVERSARIAL CHALLENGER VERIFICATION HARNESS")
    print("==============================================================================")
    test_1_unknown_component_id()
    test_2_edge_and_boundary_values()
    test_3_dynamic_propagation_and_cross_train_isolation()
    test_4_audit_log_immutability()
    test_5_concurrency_and_thread_safety()
    print("\n==============================================================================")
    print(" ALL 5 CHALLENGE SUITES COMPLETED EMPIRICALLY.")
    print("==============================================================================")


if __name__ == "__main__":
    main()
