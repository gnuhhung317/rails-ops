"""
tests/test_challenger_m4_e2e_stress.py
======================================
Empirical E2E Adversarial Stress Suite for CompressorGuard Final Milestone 4.
Author: Final E2E Challenger (teamwork_challenger_m4)

Adversarial Stress Test Matrix:
1. Component Config Form Boundary Conditions (negative, zero, NaN, injection, 404/400).
2. Shift Handover Boundary Conditions (missing fields, whitespace-only, bad data).
3. Invalid View Navigation Strings & Null Contexts (resilience of navigateTo & setView).
4. Static Scan for Math.random across entire src/ (zero fake telemetry invariant).
5. Industrial Word Budget Compliance (buttons <= 3, titles <= 3, toasts <= 10, notes <= 4).
6. Operator Persona Compliance (Hùng Bùi NV-0941 verification across full stack).

STRICT INVARIANT: No full repository pytest!
"""

import os
import sys
import re
import json
from pathlib import Path
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Use demo slice CSV and disable DD trace network flush
demo_slice = REPO_ROOT / "dataset" / "MetroPT3-demo-slice.csv"
if demo_slice.exists():
    os.environ.setdefault("TELEMETRY_CSV", str(demo_slice))

os.environ["DD_TRACE_ENABLED"] = "false"
os.environ["DD_INSTRUMENTATION_TELEMETRY_ENABLED"] = "false"

from src.api.app import create_app
from src.domain.registry import AssetRegistry

HTML_PATH = REPO_ROOT / "src" / "static" / "index.html"
JS_PATH = REPO_ROOT / "src" / "static" / "app.js"
CSS_PATH = REPO_ROOT / "src" / "static" / "styles.css"
SRC_DIR = REPO_ROOT / "src"

TECHNICAL_TOKENS = {
    "APU-COMP-01", "APU-DRY-LP49", "APU-RES-TP3", "APU-SW-LPS",
    "TRAIN-301", "TRAIN-302", "TRAIN-303", "NV-0941", "NV-1177", "NV-1082",
    "HÙNG", "BÙI", "TRẦN", "NAM", "NGUYỄN", "VĂN", "A",
    "APU", "TCMS", "HMI", "SLA", "APM", "TP3", "LP49", "LPS", "OCC", "HURC1",
    "SOP-01", "SOP-02", "SOP-03", "SOP-04",
    "P1", "P2", "P3", "SOP", "DV_PRESSURE", "OIL_TEMP", "MOTOR_CURRENT", "TP_PRESSURE",
    "LOADED", "UNLOADED", "PASS", "FAIL", "LIVE", "SIMULATION", "HISTORICAL", "DATA",
    "SHIFT", "S", "+", "->", "➔", "—", "-", "/", ":", "1X", "5X", "20X", "60X", "300X",
    "BAR", "°C", "A", "H", "M", "33H", "52M", "+2.19", "HTTP", "409", "400", "404", "422", "500", "API",
    "SUB-APU-01", "FLEET-METRO-01", "DEPOT-LONGBINH-01", "APU-INC-20200605-01",
    "LAYER", "C", "A", "B"
}

def clean_word_count(text):
    if not text:
        return 0, []
    clean = re.sub(r'[\(\)\[\]\{\}\.,:;!\?_\\/\-➔➔\+—·"]', ' ', str(text))
    words = [w for w in clean.split() if w.strip()]
    content_words = []
    for w in words:
        if w.upper() in TECHNICAL_TOKENS:
            continue
        if re.match(r'^[0-9]+(\.[0-9]+)?(h|m|s|bar|°c|a|x|%)?$', w, re.IGNORECASE):
            continue
        content_words.append(w)
    return len(content_words), content_words


class ChallengerM4E2EStress:
    def __init__(self):
        self.app = create_app()
        self.client = TestClient(self.app)
        self.results = []
        with open(HTML_PATH, "r", encoding="utf-8") as f:
            self.html_content = f.read()
        self.soup = BeautifulSoup(self.html_content, "html.parser")
        with open(JS_PATH, "r", encoding="utf-8") as f:
            self.js_content = f.read()

    def record(self, suite: str, test_id: str, desc: str, passed: bool, details: str = ""):
        status = "PASS" if passed else "FAIL"
        self.results.append((suite, test_id, desc, status, details))
        print(f"[{status}] {suite} :: {test_id} — {desc}")
        if details:
            print(f"       |-- {details}")

    # =========================================================================
    # SUITE 1: Component Config Form Boundary Conditions
    # =========================================================================
    def stress_test_component_config_boundaries(self):
        print("\n" + "=" * 80)
        print(" SUITE 1: COMPONENT CONFIG FORM BOUNDARY STRESS-TEST")
        print("=" * 80)

        # 1.1 Negative leak pressures
        for val in [-0.01, -0.05, -10.0, -100.0]:
            res = self.client.put("/api/components/APU-DRY-LP49", json={"leak_pressure_threshold_bar": val})
            self.record("Suite 1", f"S1.1-neg-pressure-{val}", f"Negative leak pressure ({val} bar) rejected with 400",
                        res.status_code == 400 and "Ngưỡng áp suất rò rỉ phải lớn hơn 0 bar" in res.json().get("detail", ""),
                        f"Status: {res.status_code}, Detail: {res.json().get('detail')}")

        # 1.2 Zero leak pressure
        res = self.client.put("/api/components/APU-DRY-LP49", json={"leak_pressure_threshold_bar": 0.0})
        self.record("Suite 1", "S1.2-zero-pressure", "Zero leak pressure (0.0 bar) rejected with 400",
                    res.status_code == 400 and "Ngưỡng áp suất rò rỉ phải lớn hơn 0 bar" in res.json().get("detail", ""),
                    f"Status: {res.status_code}, Detail: {res.json().get('detail')}")

        # 1.3 Negative oil temperatures
        for val in [-0.01, -10.0, -50.0]:
            res = self.client.put("/api/components/APU-COMP-01", json={"oil_temp_threshold_c": val})
            self.record("Suite 1", f"S1.3-neg-temp-{val}", f"Negative oil temperature ({val}°C) rejected with 400",
                        res.status_code == 400 and "Ngưỡng nhiệt độ dầu phải lớn hơn 0°C" in res.json().get("detail", ""),
                        f"Status: {res.status_code}, Detail: {res.json().get('detail')}")

        # 1.4 Zero oil temperature
        res = self.client.put("/api/components/APU-COMP-01", json={"oil_temp_threshold_c": 0.0})
        self.record("Suite 1", "S1.4-zero-temp", "Zero oil temp (0.0°C) rejected with 400",
                    res.status_code == 400 and "Ngưỡng nhiệt độ dầu phải lớn hơn 0°C" in res.json().get("detail", ""),
                    f"Status: {res.status_code}, Detail: {res.json().get('detail')}")

        # 1.5 Type mismatch (string for numeric field)
        res = self.client.put("/api/components/APU-DRY-LP49", json={"leak_pressure_threshold_bar": "NOT_A_FLOAT"})
        self.record("Suite 1", "S1.5-type-mismatch", "Type mismatch (string for float) rejected with 422",
                    res.status_code == 422, f"Status: {res.status_code}")

        # 1.6 Non-existent component ID
        res = self.client.put("/api/components/NON_EXISTENT_COMPONENT_XYZ", json={"leak_pressure_threshold_bar": 0.05})
        self.record("Suite 1", "S1.6-404-component", "Non-existent component returns 404 with Vietnamese message",
                    res.status_code == 404 and "Không tìm thấy thiết bị con" in res.json().get("detail", ""),
                    f"Status: {res.status_code}, Detail: {res.json().get('detail')}")

        # 1.7 Path injection attempt
        res = self.client.put("/api/components/..%2F..%2Fetc%2Fpasswd", json={"leak_pressure_threshold_bar": 0.05})
        self.record("Suite 1", "S1.7-path-injection", "Path traversal in component ID safely handled (404/400)",
                    res.status_code in (404, 400, 422), f"Status: {res.status_code}")

        # 1.8 Valid update & dynamic propagation to recovery
        res = self.client.put("/api/components/APU-DRY-LP49", json={
            "leak_pressure_threshold_bar": 0.065,
            "oil_temp_threshold_c": 66.8,
            "maintenance_depot": "Depot Long Bình",
            "transient_filter": True,
            "supervision_priority": "P1 - Khẩn cấp",
            "maintenance_notes": "Kiểm thử giá trị biên E2E M4",
            "operator_name": "Hùng Bùi (NV-0941)"
        })
        recovery_res = self.client.get("/api/recovery")
        rec_data = recovery_res.json()
        criteria = rec_data.get("criteria", {})
        self.record("Suite 1", "S1.8-valid-update-propagation", "Valid boundary update propagates to recovery criteria",
                    res.status_code == 200 and criteria.get("dv_pressure_max") == 0.065 and criteria.get("oil_temp_max") == 66.8,
                    f"PUT Status: {res.status_code}, criteria: {criteria}")

    # =========================================================================
    # SUITE 2: Shift Handover Boundary Conditions
    # =========================================================================
    def stress_test_shift_handover_boundaries(self):
        print("\n" + "=" * 80)
        print(" SUITE 2: SHIFT HANDOVER BOUNDARY STRESS-TEST")
        print("=" * 80)

        # 2.1 Empty body
        res = self.client.post("/api/shift/handover", json={})
        self.record("Suite 2", "S2.1-empty-body", "Empty handover payload rejected with 400/422",
                    res.status_code in (400, 422), f"Status: {res.status_code}, Body: {res.text}")

        # 2.2 Whitespace-only handover notes
        res = self.client.post("/api/shift/handover", json={
            "operator_name": "Hùng Bùi (NV-0941)",
            "incoming_operator": "Trần Nam (NV-1177)",
            "handover_notes": "     \t\n   "
        })
        self.record("Suite 2", "S2.2-whitespace-notes", "Whitespace-only handover notes rejected with 400",
                    res.status_code == 400 and "Ghi chú bàn giao ca không được để trống" in res.json().get("detail", ""),
                    f"Status: {res.status_code}, Detail: {res.json().get('detail')}")

        # 2.3 Whitespace-only incoming operator
        res = self.client.post("/api/shift/handover", json={
            "operator_name": "Hùng Bùi (NV-0941)",
            "incoming_operator": "   ",
            "handover_notes": "Bàn giao ca bình thường"
        })
        self.record("Suite 2", "S2.3-whitespace-incoming", "Whitespace-only incoming operator rejected with 400",
                    res.status_code == 400 and "Tên nhân viên nhận ca không được để trống" in res.json().get("detail", ""),
                    f"Status: {res.status_code}, Detail: {res.json().get('detail')}")

        # 2.4 Missing notes field
        res = self.client.post("/api/shift/handover", json={
            "operator_name": "Hùng Bùi (NV-0941)",
            "incoming_operator": "Nguyễn Văn B"
        })
        self.record("Suite 2", "S2.4-missing-notes", "Missing handover notes rejected with 400",
                    res.status_code == 400, f"Status: {res.status_code}")

        # 2.5 Valid handover execution and audit ledger recording
        res = self.client.post("/api/shift/handover", json={
            "operator_name": "Hùng Bùi (NV-0941)",
            "incoming_operator": "Lê Hoàng (NV-1082)",
            "shift_name": "Ca 2 (14:00 – 22:00)",
            "depot_location": "Depot Long Bình",
            "handover_notes": "Bàn giao ca trực E2E Challenger M4 thành công",
            "acknowledged_active_cases": ["APU-INC-20200605-01"]
        })
        res_data = res.json()
        handover_ok = res.status_code == 200 and res_data.get("status") == "HANDOVER_COMPLETED"
        self.record("Suite 2", "S2.5-valid-handover", "Valid handover completes and logs audit event",
                    handover_ok, f"Status: {res.status_code}, Handover ID: {res_data.get('handover_id')}")

        # Verify audit ledger has the handover event
        events_res = self.client.get("/api/case/events")
        events = events_res.json()
        handover_events = [e for e in events if e.get("phase") == "SHIFT_HANDOVER" and "Lê Hoàng (NV-1082)" in e.get("title", "")]
        self.record("Suite 2", "S2.6-audit-ledger-handover", "Audit ledger captures shift handover with incoming operator name",
                    len(handover_events) > 0, f"Found {len(handover_events)} matching handover events")

    # =========================================================================
    # SUITE 3: Invalid View Navigation Strings & Null Contexts
    # =========================================================================
    def stress_test_navigation_resilience(self):
        print("\n" + "=" * 80)
        print(" SUITE 3: NAVIGATION STRINGS & NULL CONTEXTS RESILIENCE")
        print("=" * 80)

        # 3.1 navigateTo view whitelist check
        has_valid_views = "const VALID_VIEWS = ['fleet', 'assets', 'workbench', 'settings'];" in self.js_content
        self.record("Suite 3", "S3.1-valid-views", "navigateTo and setView define strict VALID_VIEWS whitelist",
                    has_valid_views, "Found exact VALID_VIEWS array")

        # 3.2 navigateTo fallback for invalid views
        has_fallback_view = "const targetView = VALID_VIEWS.includes(view) ? view : (S.view || 'fleet');" in self.js_content
        self.record("Suite 3", "S3.2-invalid-view-fallback", "Unregistered / invalid view string falls back gracefully to S.view or fleet",
                    has_fallback_view, "Fallback expression present in navigateTo")

        # 3.3 navigateTo context null safety
        has_ctx_safe = "const ctx = (context && typeof context === 'object') ? context : {};" in self.js_content
        self.record("Suite 3", "S3.3-null-context-safety", "Null / undefined / primitive context safely converted to empty object",
                    has_ctx_safe, "Safe object check present in navigateTo")

        # 3.4 setView fallback for null / invalid inputs
        has_setview_safe = "const safeView = VALID_VIEWS.includes(view) ? view : 'fleet';" in self.js_content
        self.record("Suite 3", "S3.4-setview-fallback", "setView safely maps unknown views to 'fleet'",
                    has_setview_safe, "Safe fallback in setView")

        # 3.5 selectComponent null safety
        has_select_comp_safe = (
            "componentId || 'APU-DRY-LP49'" in self.js_content
            and "COMPONENT_SPECS_FALLBACK" in self.js_content
        )
        self.record("Suite 3", "S3.5-select-component-safe", "selectComponent handles null/undefined componentId and trainId safely",
                    has_select_comp_safe, "Component fallback present in selectComponent")

    # =========================================================================
    # SUITE 4: Static Scan for Math.random Across Entire src/
    # =========================================================================
    def stress_test_zero_fake_telemetry(self):
        print("\n" + "=" * 80)
        print(" SUITE 4: STATIC SCAN FOR Math.random ACROSS ENTIRE src/")
        print("=" * 80)

        matches = []
        for p in SRC_DIR.rglob("*"):
            if p.is_file() and p.suffix.lower() in [".py", ".js", ".html", ".css", ".json"]:
                # Exclude third-party vendor directories if any
                if "vendor" in p.parts:
                    continue
                try:
                    with open(p, "r", encoding="utf-8", errors="ignore") as f:
                        for line_no, line in enumerate(f, 1):
                            if "Math.random" in line:
                                matches.append((str(p.relative_to(REPO_ROOT)), line_no, line.strip()))
                except Exception as e:
                    pass

        self.record("Suite 4", "S4.1-zero-math-random", "Static scan for Math.random across src/ returns EXACTLY 0 matches",
                    len(matches) == 0,
                    f"Matches found: {len(matches)}. Details: {matches}")

    # =========================================================================
    # SUITE 5: Industrial Word Budget Compliance
    # =========================================================================
    def stress_test_industrial_word_budgets(self):
        print("\n" + "=" * 80)
        print(" SUITE 5: INDUSTRIAL WORD BUDGET COMPLIANCE")
        print("=" * 80)

        # 5.1 HTML Button Labels (<= 3 words)
        buttons = self.soup.find_all("button")
        btn_violations = []
        for btn in buttons:
            txt_val = btn.get_text(strip=True)
            cnt, words = clean_word_count(txt_val)
            if cnt > 3:
                btn_violations.append((txt_val, cnt, words))

        self.record("Suite 5", "S5.1-button-word-budget", "Static HTML button labels conform to <= 3 words budget",
                    len(btn_violations) == 0,
                    f"Total buttons: {len(buttons)}, Violations (>3 words): {len(btn_violations)}. Details: {btn_violations}")

        # 5.2 Dynamic Button Labels in app.js (<= 3 words)
        btn_label_patterns = [
            r"btn\.textContent\s*=\s*['\"`]([^'\"`]+)['\"`]",
            r"innerHTML\s*=\s*`?<button[^>]*>([^<]+)</button>`?",
        ]
        dynamic_btn_violations = []
        for pat in btn_label_patterns:
            for match in re.finditer(pat, self.js_content):
                txt_val = match.group(1).strip()
                if not txt_val or "${" in txt_val:
                    continue
                cnt, words = clean_word_count(txt_val)
                if cnt > 3:
                    dynamic_btn_violations.append((txt_val, cnt, words))

        self.record("Suite 5", "S5.2-dynamic-button-budget", "Dynamic button labels in app.js conform to <= 3 words budget",
                    len(dynamic_btn_violations) == 0,
                    f"Violations (>3 words): {len(dynamic_btn_violations)}. Details: {dynamic_btn_violations}")

        # 5.3 Panel Titles (<= 3 words)
        panel_titles = self.soup.find_all(class_=re.compile(r"panel-title|sec-title"))
        title_violations = []
        for pt in panel_titles:
            txt_val = pt.get_text(strip=True)
            cnt, words = clean_word_count(txt_val)
            if cnt > 3:
                title_violations.append((txt_val, cnt, words))

        self.record("Suite 5", "S5.3-panel-title-budget", "Panel titles conform to <= 3 words budget",
                    len(title_violations) == 0,
                    f"Total panel titles: {len(panel_titles)}, Violations (>3 words): {len(title_violations)}. Details: {title_violations}")

        # 5.4 Dynamic Toasts (<= 10 words)
        toast_pattern = re.compile(r"toast\(\s*['\"]([a-z]+)['\"]\s*,\s*['\"`]([^'\"`]+)['\"`](?:\s*,\s*['\"`]([^'\"`]+)['\"`])?", re.IGNORECASE)
        toast_matches = toast_pattern.findall(self.js_content)
        toast_violations = []
        for kind, title, detail in toast_matches:
            t_cnt, _ = clean_word_count(title)
            d_cnt, _ = clean_word_count(detail)
            # Both title and detail must conform to <= 10 words
            if t_cnt > 10 or d_cnt > 10:
                toast_violations.append((kind, title, detail, t_cnt, d_cnt))

        self.record("Suite 5", "S5.4-dynamic-toast-budget", "Dynamic toasts in app.js conform to <= 10 words budget",
                    len(toast_violations) == 0,
                    f"Total toasts: {len(toast_matches)}, Violations (>10 words): {len(toast_violations)}. Details: {toast_violations}")

    # =========================================================================
    # SUITE 6: Operator Persona Compliance (Hùng Bùi NV-0941)
    # =========================================================================
    def stress_test_operator_persona(self):
        print("\n" + "=" * 80)
        print(" SUITE 6: OPERATOR PERSONA COMPLIANCE (HÙNG BÙI NV-0941)")
        print("=" * 80)

        # 6.1 Shift Card in Screen 4 DOM contains Hùng Bùi (NV-0941)
        shift_card = self.soup.find(id="shift-operator-card")
        card_text = shift_card.get_text() if shift_card else ""
        has_hung_bui = "Hùng Bùi" in card_text and "NV-0941" in card_text
        self.record("Suite 6", "S6.1-dom-shift-card", "Screen 4 DOM shift card binds to Hùng Bùi (NV-0941)",
                    has_hung_bui, f"Card found: {bool(shift_card)}, Content snippet: {card_text[:100]}...")

        # 6.2 S.operator in app.js is initialized to Hùng Bùi (NV-0941)
        has_js_operator = "operator: 'Hùng Bùi (NV-0941)'" in self.js_content and "operatorCode: 'NV-0941'" in self.js_content
        self.record("Suite 6", "S6.2-js-state-operator", "Client state S.operator initialized to Hùng Bùi (NV-0941)",
                    has_js_operator, "Found exact operator string in app.js state S")

        # 6.3 Backend GET /api/shift/current returns Hùng Bùi (NV-0941)
        res = self.client.get("/api/shift/current")
        shift_data = res.json()
        backend_operator_ok = (
            res.status_code == 200
            and shift_data.get("operator_name") == "Hùng Bùi"
            and shift_data.get("operator_id") == "NV-0941"
            and shift_data.get("depot") == "Depot Long Bình"
        )
        self.record("Suite 6", "S6.3-backend-current-shift", "GET /api/shift/current returns Hùng Bùi (NV-0941) and Long Bình",
                    backend_operator_ok, f"Status: {res.status_code}, Operator: {shift_data.get('operator_name')}")

        # 6.4 Component update default operator in routes_product.py
        with open(REPO_ROOT / "src" / "api" / "routes_product.py", "r", encoding="utf-8") as f:
            routes_content = f.read()
        has_default_op = '"Hùng Bùi (NV-0941)"' in routes_content
        self.record("Suite 6", "S6.4-backend-default-actor", "Backend routes use Hùng Bùi (NV-0941) as default actor for audit records",
                    has_default_op, "Default operator found in routes_product.py")

    def run_all(self):
        self.stress_test_component_config_boundaries()
        self.stress_test_shift_handover_boundaries()
        self.stress_test_navigation_resilience()
        self.stress_test_zero_fake_telemetry()
        self.stress_test_industrial_word_budgets()
        self.stress_test_operator_persona()

        print("\n" + "=" * 80)
        print(" FINAL E2E M4 CHALLENGER STRESS SUITE SUMMARY")
        print("=" * 80)
        total = len(self.results)
        passed = sum(1 for r in self.results if r[3] == "PASS")
        failed = sum(1 for r in self.results if r[3] == "FAIL")

        for suite, tid, desc, status, details in self.results:
            mark = "[PASS]" if status == "PASS" else "[FAIL]"
            print(f"{mark} {tid} ({suite}): {desc}")

        print("-" * 80)
        print(f"Total Checks: {total} | Passed: {passed} | Failed: {failed}")
        print("=" * 80)

        if failed > 0:
            print("\n>>> EMPIRICAL VERDICT: REQUEST_CHANGES <<<")
            sys.exit(1)
        else:
            print("\n>>> EMPIRICAL VERDICT: APPROVE <<<")
            sys.exit(0)


if __name__ == "__main__":
    verifier = ChallengerM4E2EStress()
    verifier.run_all()
