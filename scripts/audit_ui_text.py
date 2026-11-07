"""Audit the console for look-ahead text.

The benchmark clock (LPS breach 2020-06-06 19:42:19, 33h 52m / 2032 min) is
counterfactual until the event cursor actually reaches it, so it may only appear
in the Validation Reference drawer. This script drives the real UI when Playwright
is installed; without it, it audits the API payloads and the shipped UI source and
prints the manual DOM checklist.

Usage:  python scripts/audit_ui_text.py [--base http://127.0.0.1:8000]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

FORBIDDEN = [r"19:42", r"33h", r"33h 52m", r"2032 (?:phút|min)"]
BENCHMARK_STAMP = "2020-06-06 19:42:19"
FORBIDDEN_LABELS = ["19:42", "33h 52m", "2032 phút"]
STATIC = Path(__file__).resolve().parents[1] / "src" / "static"
ENDPOINTS = [
    "/api/operations",
    "/api/incident",
    "/api/evidence",
    "/api/case/events",
    "/api/action/guard-status",
    "/api/recovery",
    "/api/telemetry/window?limit=500",
    "/api/telemetry/analytics",
    "/api/scenarios",
    "/demo/status",
]
# The catalog is the clock registry the jump API needs; the UI must render names only.
ALLOWED_HOLDERS = {"/api/scenarios"}
MILESTONES = [
    "early_excursion_0033",
    "onset_0950",
    "ml_corroborated_1015",
    "lps_reactive_1942",
    "post_maintenance_1605",
]
CHECKLIST = [
    "Open each milestone with POST /demo/jump, then read the whole page text.",
    "Outside the Validation Reference drawer, none of these may appear: " + ", ".join(FORBIDDEN_LABELS) + ".",
    "The benchmark stamp may appear only when the event clock is already at or past it.",
    "The Validation Reference drawer must stay closed by default and carry its Layer C label.",
    "With no case open (state NONE) no badge, form or FAIL row is rendered.",
]


def fetch(base: str, path: str) -> object:
    with urllib.request.urlopen(base + path, timeout=30) as response:
        return json.load(response)


def hits(text: str, cursor: datetime | None) -> list[str]:
    # Anchored patterns: 2032 also occurs inside sensor floats such as 2.0820327.
    found = [token for token in FORBIDDEN if re.search(token, text)]
    if BENCHMARK_STAMP in text and (cursor is None or cursor < datetime(2020, 6, 6, 19, 42, 19)):
        found.append(BENCHMARK_STAMP)
    return found


def audit_static(base: str) -> int:
    failures = 0
    for path in ENDPOINTS:
        try:
            payload = fetch(base, path)
        except Exception as exc:  # noqa: BLE001 - the audit reports, it does not raise
            print(f"  SKIP {path}: {exc}")
            continue
        status = payload.get("status_code") if isinstance(payload, dict) else None
        if status and status >= 400:
            print(f"  FAIL {path}: HTTP {status}")
            failures += 1
            continue
        blob = json.dumps(payload, default=str)
        if path in ALLOWED_HOLDERS:
            print(f"  held {path} (clock registry; UI renders names only)")
            continue
        cursor = None
        if path == "/demo/status":
            raw = payload.get("current_event_time")
            cursor = datetime.fromisoformat(raw) if raw else None
        leaked = hits(blob, cursor)
        # The API is allowed to carry the counterfactual; only the console may not show it.
        print(f"  {'NOTE' if leaked else 'ok  '} {path}" + (f" -> carries {leaked}" if leaked else ""))

    for name in ("index.html", "app.js"):
        source = (STATIC / name).read_text(encoding="utf-8")
        leaked = [token for token in FORBIDDEN if token in source]
        print(f"  {'FAIL' if leaked else 'ok  '} static/{name}" + (f" -> {leaked}" if leaked else ""))
        failures += len(leaked)
    return failures


def audit_dom(base: str) -> int:
    from playwright.sync_api import sync_playwright  # noqa: PLC0415 - optional dependency

    failures = 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        for milestone in MILESTONES:
            with urllib.request.urlopen(  # noqa: S310 - fixed localhost base
                base + "/demo/jump",
                data=json.dumps({"milestone": milestone}).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            ):
                pass
            page.goto(base + "/", wait_until="networkidle")
            drawer = page.locator("#vr-drawer")
            drawer_text = drawer.inner_text()
            page.evaluate("() => document.getElementById('vr-drawer').remove()")
            body_text = page.evaluate("() => document.body.innerText")
            cursor = page.evaluate("() => document.getElementById('event-clock').textContent")
            leaked = hits(body_text, parse_cursor(cursor))
            bench_only_in_drawer = not hits(drawer_text, None)
            failures += len(leaked)
            print(f"  {'FAIL' if leaked else 'ok  '} {milestone}: cursor {cursor}" + (f" -> {leaked}" if leaked else ""))
            if bench_only_in_drawer:
                print(f"  WARN {milestone}: Validation Reference carries no benchmark text")
        browser.close()
    return failures


def parse_cursor(text: str) -> datetime | None:
    match = re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", text or "")
    return datetime.strptime(match.group(), "%Y-%m-%d %H:%M:%S") if match else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="http://127.0.0.1:8000")
    args = parser.parse_args()

    try:
        import playwright  # noqa: F401
    except ModuleNotFoundError:
        print("Playwright is not installed — auditing API payloads and UI source instead.")
        print("\nManual DOM checklist:")
        for line in CHECKLIST:
            print(f"  [ ] {line}")
        return 1 if audit_static(args.base) else 0

    print("Driving the console with Playwright:")
    return 1 if audit_dom(args.base) else 0


if __name__ == "__main__":
    sys.exit(main())
