"""
RailOps VN -- Console Journey Verifier (HTTP, against a live server)

Drives the complete operator workflow through the public API only, exactly the way
the Operations Command Console does, and asserts each evaluation gate on the way.

    python run_demo.py                 # in one terminal
    python scripts/verify_console_journey.py   # in another

Exit code 0 means: premature intervention rejected, case detected from real CSV
telemetry, ActionGuard 5/5, recovery verified, case signed off and closed.
"""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime

BASE = os.environ.get("CONSOLE_BASE_URL", "http://127.0.0.1:8000")
OPERATOR = "DISPATCHER-0941"

RESULTS = []


def _call(method, path, payload=None, timeout=60):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        BASE + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"} if data else {},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8") or "{}"
        try:
            return exc.code, json.loads(body)
        except json.JSONDecodeError:
            return exc.code, {"raw": body}
    except urllib.error.URLError as exc:
        raise SystemExit(
            f"[FATAL] Cannot reach {BASE} ({exc.reason}).\n"
            "Start the console first:  python run_demo.py"
        )


def get(path):
    status, body = _call("GET", path)
    if status != 200:
        raise SystemExit(f"[FATAL] GET {path} -> HTTP {status}: {body}")
    return body


def post(path, payload=None):
    return _call("POST", path, payload if payload is not None else {})


def check(label, condition, evidence=""):
    RESULTS.append((label, bool(condition), evidence))
    mark = "[OK]  " if condition else "[FAIL]"
    print(f"  {mark} {label}" + (f"  --  {evidence}" if evidence else ""))
    return bool(condition)


def tick_until(path_predicate, max_ticks=400, label=""):
    """POST /demo/tick repeatedly until the predicate over live API state is true."""
    for _ in range(max_ticks):
        if path_predicate():
            return True
        status, _ = post("/demo/tick")
        if status != 200:
            return False
    return path_predicate()


def main():
    print("=" * 72)
    print("RAILOPS VN -- OPERATIONS CONSOLE JOURNEY VERIFICATION")
    print(f"Target: {BASE}")
    print("=" * 72)

    probe = get("/health")
    print(f"\n[SERVER] {probe.get('name')} status={probe.get('status')}")

    # ---------------------------------------------------------------- step 0
    print("\n[STEP 0] Reset stream and confirm clean, case-free baseline.")
    post("/demo/reset")
    case = get("/api/case")
    check("Baseline lifecycle_state is NONE", case["lifecycle_state"] == "NONE",
          case["lifecycle_state"])

    # ---------------------------------------------------------------- step 1
    print("\n[STEP 1] Human-in-the-Loop gate: premature Safe Mode must be refused.")
    status, body = post("/api/action/safe-mode", {"operator_id": OPERATOR})
    check("Premature safe-mode returns HTTP 409", status == 409,
          str(body.get("detail", body))[:90])
    check("Asset stays in revenue service after refusal",
          get("/api/case")["lifecycle_state"] == "NONE")

    # ---------------------------------------------------------------- step 2
    print("\n[STEP 2] Replay real MetroPT-3 telemetry to the failure onset milestone.")
    status, _ = post("/demo/jump", {"milestone": "onset_0950"})
    check("Jump to onset_0950 accepted", status == 200)

    detected = tick_until(
        lambda: get("/api/case")["lifecycle_state"] in ("DETECTED", "INVESTIGATING"),
        label="detection",
    )
    case = get("/api/case")
    check("Decision Engine opens a case from live telemetry", detected,
          f"state={case['lifecycle_state']}")
    check("Case carries a real incident id", bool(case.get("incident_id")),
          str(case.get("incident_id")))
    check("Lead window quantified vs conventional brake-pressure alarm",
          bool((case.get("lead_time") or {}).get("lead_time_formatted")),
          str((case.get("lead_time") or {}).get("lead_time_formatted")))

    ev = get("/api/evidence")
    cards = ev.get("evidence_pack") or []
    check("Evidence pack produced for the operator", len(cards) >= 3,
          f"{len(cards)} evidence cards")

    tel = get("/api/telemetry/window?limit=120")
    points = tel.get("points") or []
    check("Strip-chart window served from replayed telemetry",
          len(points) > 0 and all("timestamp" in p for p in points),
          f"{len(points)} frames")
    check("Rolling statistics present per frame",
          all("rolling_avg_dv" in p and "rolling_std_dv" in p for p in points),
          "rolling_avg_dv / rolling_std_dv")
    last = points[-1] if points else {}
    check("Dual-clock: physical event_time stays historical while ingest time is now",
          str(last.get("timestamp", "")).startswith("2020")
          and str(last.get("ingested_at", "")).startswith(str(datetime.utcnow().year)),
          f"event_time={last.get('timestamp')} ingested_at={last.get('ingested_at')}")

    # ---------------------------------------------------------------- step 3
    print("\n[STEP 3] Operator actions: acknowledge, forensic note, depot work order.")
    status, _ = post("/api/case/acknowledge", {"operator_id": OPERATOR, "priority": "P1-CRITICAL"})
    check("Acknowledge accepted", status == 200)
    status, _ = post("/api/case/notes", {"operator_id": OPERATOR,
                                         "note": "Thermal drift corroborated; depot notified."})
    check("Forensic note appended to ledger", status == 200)
    status, _ = post("/api/case/work-order", {"operator_id": OPERATOR})
    check("Depot work order raised", status == 200)
    check("Console reflects acknowledgement", get("/api/case")["acknowledged"] is True)

    # ---------------------------------------------------------------- step 4
    print("\n[STEP 4] ML corroboration milestone, then ActionGuard 5/5 and Safe Mode.")
    status, _ = post("/demo/jump", {"milestone": "ml_corroborated_1015"})
    check("Jump to ml_corroborated_1015 accepted", status == 200)

    permitted = tick_until(lambda: get("/api/action/guard-status")["is_permitted"],
                           max_ticks=200, label="guard")
    guard = get("/api/action/guard-status")
    check("ActionGuard reaches 5/5 after corroboration", permitted,
          f"{guard['passed_count']}/{guard['total_checks']} "
          f"denial={str(guard.get('denial_reason'))[:60]}")

    status, body = post("/api/action/safe-mode", {"operator_id": OPERATOR})
    check("Safe Mode permitted once guards pass", status == 200, str(body)[:80])
    check("Lifecycle moved to MITIGATING and stream branched to post-maintenance",
          get("/api/case")["lifecycle_state"] in ("MITIGATING", "VERIFYING_RECOVERY"),
          get("/api/case")["lifecycle_state"])

    # ---------------------------------------------------------------- step 5
    print("\n[STEP 5] Recovery verification: 5 consecutive healthy LOADED samples.")
    verified = tick_until(lambda: get("/api/recovery")["is_verified"],
                          max_ticks=400, label="recovery")
    rec = get("/api/recovery")
    check("Recovery verifier confirms asset health", verified,
          f"{rec['consecutive_healthy_observations']}/{rec['target_healthy_observations']} "
          f"healthy LOADED observations")

    status, body = post("/api/case/close", {"operator_id": OPERATOR,
                                            "root_cause": "DV discharge-valve seal leak",
                                            "notes": "Recovery criteria satisfied"})
    check("Root-cause sign-off closes the case", status == 200, str(body)[:80])
    final = get("/api/case")
    check("Case closed and asset released back to HEALTHY service",
          final["lifecycle_state"] in ("RESOLVED", "NONE")
          and final["asset_health"] == "HEALTHY",
          f"state={final['lifecycle_state']} health={final['asset_health']}")

    ledger = get("/api/case/events")
    check("Append-only CaseEvent ledger recorded the full journey", len(ledger) >= 6,
          f"{len(ledger)} events")

    # ---------------------------------------------------------------- summary
    passed = sum(1 for _, ok, _ in RESULTS if ok)
    total = len(RESULTS)
    print("\n" + "=" * 72)
    if passed == total:
        print(f"[SUCCESS] CONSOLE JOURNEY GREEN -- {passed}/{total} assertions passed.")
        print("          Detect -> Prove -> Act safely -> Verify recovery -> Sign off.")
    else:
        print(f"[FAILURE] {total - passed} of {total} assertions failed:")
        for label, ok, evidence in RESULTS:
            if not ok:
                print(f"          - {label} ({evidence})")
    print("=" * 72)
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
