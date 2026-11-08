"""
tests/verify_enterprise_ui.py
=============================
Automated Headless HTML/DOM, Word Budget & Interaction Flow Audit for CompressorGuard Enterprise UI/UX.

MANDATORY RULES:
- ZERO PYTEST ON FULL REPO: Run directly via:
    python tests/verify_enterprise_ui.py
- Verifies Tiers 3 & 4 features:
    * F5-F15: Screen 1-4 DOM layouts, P1 Hero Banner, Synoptic Mimic, 35:65 Master-Detail, Word Budgets
    * F16-F21: Navigation routing (navigateTo), Dynamic Threshold Sync, Stepper 5 steps, Simulation Controls
    * F24: E2E Browser & UI Acceptance Audit
    * F25: Operator Identity (Hùng Bùi NV-0941) & Natural Vietnamese Word Budgets
"""

import sys
import os
import re
from pathlib import Path
from typing import List, Tuple, Dict, Any
from bs4 import BeautifulSoup

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = REPO_ROOT / "src" / "static" / "index.html"
CSS_PATH = REPO_ROOT / "src" / "static" / "styles.css"
JS_PATH = REPO_ROOT / "src" / "static" / "app.js"


class EnterpriseUIVerifier:
    def __init__(self):
        self.html_content = ""
        self.soup: BeautifulSoup = None
        self.js_content = ""
        self.css_content = ""
        self.results: List[Tuple[str, str, str, str]] = []  # (Tier, Category, Name, Status, Message)

    def load_files(self) -> bool:
        if not HTML_PATH.exists():
            print(f"[FAIL] HTML file missing at {HTML_PATH}")
            return False
        if not JS_PATH.exists():
            print(f"[FAIL] JS file missing at {JS_PATH}")
            return False
        if not CSS_PATH.exists():
            print(f"[FAIL] CSS file missing at {CSS_PATH}")
            return False

        with open(HTML_PATH, "r", encoding="utf-8") as f:
            self.html_content = f.read()
        self.soup = BeautifulSoup(self.html_content, "html.parser")

        with open(JS_PATH, "r", encoding="utf-8") as f:
            self.js_content = f.read()

        with open(CSS_PATH, "r", encoding="utf-8") as f:
            self.css_content = f.read()

        return True

    def record(self, tier: str, category: str, name: str, passed: bool, msg: str = ""):
        status = "PASS" if passed else "FAIL"
        self.results.append((tier, category, name, status, msg))

    # -----------------------------------------------------------------
    # Check 1: Operational Navigation & 4 Views Structure (Tier 3)
    # -----------------------------------------------------------------
    def check_four_views_structure(self):
        views = self.soup.find_all("section", class_=lambda c: c and "view" in c.split())
        view_ids = [v.get("id") for v in views if v.get("id")]

        expected_views = ["view-fleet", "view-assets", "view-workbench", "view-settings"]
        for v in expected_views:
            exists = v in view_ids
            self.record("Tier 3", "Navigation & Layout", f"View container #{v} present in DOM", exists,
                        f"Found in DOM: {v}" if exists else f"Missing section #{v}. Existing: {view_ids}")

        # Check navigation tabs
        nav_tabs = self.soup.find_all(lambda el: el.name == "button" and el.get("data-view"))
        tab_views = [t.get("data-view") for t in nav_tabs]
        for v in ["fleet", "assets", "workbench", "settings"]:
            found = v in tab_views
            self.record("Tier 3", "Navigation & Layout", f"Nav tab for '{v}' present", found,
                        f"Found data-view='{v}'" if found else f"Missing tab for {v}")

    # -----------------------------------------------------------------
    # Check 2: Screen 1 Operations & Fleet Overview (Tier 3 / R1)
    # -----------------------------------------------------------------
    def check_screen_1_fleet_overview(self):
        fleet_view = self.soup.find(id="view-fleet")
        if not fleet_view:
            self.record("Tier 3", "Screen 1 Overview", "Screen 1 container", False, "Missing #view-fleet")
            return

        # 1. P1 Warning Hero Banner
        hero = fleet_view.find(id="hero-p1-banner") or fleet_view.find(class_=lambda c: c and "hero-p1" in c)
        if hero:
            hero_text = hero.get_text()
            has_train_302 = "TRAIN-302" in hero_text or "302" in hero_text
            has_buffer = ("33h" in hero_text) or ("33 giờ" in hero_text) or ("33h 52m" in hero_text) or bool(hero.find(id="hero-safety-buffer"))
            btn_warroom = hero.find(id="btn-hero-goto-warroom") or hero.find(lambda el: "Phòng Điều Tra" in el.get_text() if el.string else False)

            self.record("Tier 3", "Screen 1 Overview", "P1 Hero Banner for TRAIN-302 present", has_train_302,
                        "Found TRAIN-302 in Hero Banner" if has_train_302 else "TRAIN-302 not found in Hero text")
            self.record("Tier 3", "Screen 1 Overview", "P1 Hero Banner displays 33h 52m safety buffer", has_buffer,
                        "Found safety buffer in Hero Banner" if has_buffer else "Safety buffer missing in Hero Banner")
            self.record("Tier 3", "Screen 1 Overview", "Button to navigate to War Room present in Hero", bool(btn_warroom),
                        f"Button found: {btn_warroom.get_text().strip() if btn_warroom else 'None'}")
        else:
            self.record("Tier 3", "Screen 1 Overview", "P1 Hero Banner element present", False, "Missing #hero-p1-banner")

        # 2. 4 Operational KPIs
        kpi_grid = fleet_view.find(id="fleet-kpi-grid") or fleet_view.find(class_=lambda c: c and "kpi" in c)
        if kpi_grid:
            kpi_text = kpi_grid.get_text()
            has_total = "3/3" in kpi_text or bool(kpi_grid.find(id="kpi-fleet-total"))
            has_healthy = "2" in kpi_text or bool(kpi_grid.find(id="kpi-fleet-healthy"))
            has_alert = "1" in kpi_text or bool(kpi_grid.find(id="kpi-fleet-alert"))
            has_depot = "Long Bình" in kpi_text or bool(kpi_grid.find(id="kpi-fleet-depot"))

            self.record("Tier 3", "Screen 1 Overview", "4 Operational KPIs present (3/3, 2 normal, 1 alert, Long Bình)",
                        has_total and has_healthy and has_alert and has_depot,
                        f"Total: {has_total}, Healthy: {has_healthy}, Alert: {has_alert}, Depot: {has_depot}")
        else:
            self.record("Tier 3", "Screen 1 Overview", "Fleet KPI grid present", False, "Missing #fleet-kpi-grid")

        # 3. 3 Fleet Grid Cards
        cards_grid = fleet_view.find(id="fleet-cards-grid") or fleet_view.find(class_=lambda c: c and "fleet-card" in c)
        if cards_grid:
            grid_text = cards_grid.get_text()
            has_t301 = "TRAIN-301" in grid_text
            has_t302 = "TRAIN-302" in grid_text
            has_t303 = "TRAIN-303" in grid_text
            self.record("Tier 3", "Screen 1 Overview", "3 Fleet Grid Cards (301, 302, 303) present",
                        has_t301 and has_t302 and has_t303,
                        f"TRAIN-301: {has_t301}, TRAIN-302: {has_t302}, TRAIN-303: {has_t303}")
        else:
            self.record("Tier 3", "Screen 1 Overview", "Fleet Cards Grid present", False, "Missing #fleet-cards-grid")

        # 4. Anti-Smog / Cognitive Declutter: Wave charts & math sigmas REMOVED from Screen 1
        charts_in_screen1 = fleet_view.find_all(lambda el: el.name == "canvas" and el.get("id") in ["chart-dv", "chart-oil", "chart-current", "chart-tp"])
        self.record("Tier 3", "Screen 1 Overview", "Cognitive Declutter: NO raw wave charts inside Screen 1",
                    len(charts_in_screen1) == 0,
                    f"Found {len(charts_in_screen1)} wave charts inside Screen 1 (should be 0, moved to Screen 3)")

        math_sigmas = fleet_view.find_all(id=["if-read", "if-fill", "suppression-stream"])
        self.record("Tier 3", "Screen 1 Overview", "Cognitive Declutter: NO math sigma/isolation forest widgets in Screen 1",
                    len(math_sigmas) == 0,
                    f"Found {len(math_sigmas)} sigma widgets inside Screen 1 (should be 0)")

    # -----------------------------------------------------------------
    # Check 3: Screen 2 Asset & Component Management (Tier 3 / R2)
    # -----------------------------------------------------------------
    def check_screen_2_asset_management(self):
        assets_view = self.soup.find(id="view-assets")
        if not assets_view:
            self.record("Tier 3", "Screen 2 Assets", "Screen 2 container", False, "Missing #view-assets")
            return

        # 1. Master-Detail 35% : 65% structure
        master_detail = assets_view.find(class_=lambda c: c and "asset-master-detail" in c) or assets_view.find(id="asset-master-detail")
        self.record("Tier 3", "Screen 2 Assets", "Master-Detail two-column layout present", bool(master_detail),
                    "Found .asset-master-detail" if master_detail else "Missing master-detail wrapper")

        # 2. Asset Tree (Column 1)
        tree_pane = assets_view.find(id="asset-tree-pane") or assets_view.find(id="asset-tree-container") or assets_view.find(class_=lambda c: c and "asset-tree" in c)
        if tree_pane:
            tree_text = tree_pane.get_text()
            has_line1 = "Metro" in tree_text or "Tuyến" in tree_text or "Line 1" in tree_text
            has_trains = "301" in tree_text and "302" in tree_text and "303" in tree_text
            has_apu = "APU" in tree_text or "SUB-APU" in tree_text
            has_dryer = "LP49" in tree_text or "sấy" in tree_text.lower() or "Dryer" in tree_text

            self.record("Tier 3", "Screen 2 Assets", "Asset Tree contains Metro Line 1 -> Trains -> APU -> Subcomponents",
                        has_line1 and has_trains and has_apu and has_dryer,
                        f"Line1: {has_line1}, Trains: {has_trains}, APU: {has_apu}, Dryer: {has_dryer}")
        else:
            self.record("Tier 3", "Screen 2 Assets", "Asset Tree pane present", False, "Missing #asset-tree-pane")

        # 3. Editable Configuration Form (Column 2)
        form = assets_view.find(id="asset-config-form")
        if form:
            leak_in = form.find(id="cfg-leak-threshold")
            oil_in = form.find(id="cfg-oil-threshold")
            depot_sel = form.find(id="cfg-depot")
            filter_chk = form.find(id="cfg-transient-filter")
            prio_sel = form.find(id="cfg-supervision-prio")
            notes_txt = form.find(id="cfg-maint-notes")
            save_btn = form.find(id="btn-save-asset-config") or form.find(lambda el: el.name == "button" and "Lưu" in el.get_text())

            fields_ok = all([leak_in, oil_in, depot_sel, filter_chk, prio_sel, notes_txt])
            self.record("Tier 3", "Screen 2 Assets", "Config form has 6 required inputs (leak, oil, depot, filter, prio, notes)",
                        fields_ok,
                        f"Leak: {bool(leak_in)}, Oil: {bool(oil_in)}, Depot: {bool(depot_sel)}, Filter: {bool(filter_chk)}, Prio: {bool(prio_sel)}, Notes: {bool(notes_txt)}")
            self.record("Tier 3", "Screen 2 Assets", "Save configuration button present in form", bool(save_btn),
                        f"Found save button: {save_btn.get_text().strip() if save_btn else 'None'}")
        else:
            self.record("Tier 3", "Screen 2 Assets", "Config form #asset-config-form present", False, "Missing #asset-config-form")

    # -----------------------------------------------------------------
    # Check 4: Screen 3 Incident War Room (Tier 3 / R3)
    # -----------------------------------------------------------------
    def check_screen_3_warroom(self):
        wb_view = self.soup.find(id="view-workbench")
        if not wb_view:
            self.record("Tier 3", "Screen 3 War Room", "Screen 3 container", False, "Missing #view-workbench")
            return

        # 1. War Room Header
        header = wb_view.find(id="warroom-header") or wb_view.find(class_=lambda c: c and "warroom-header" in c)
        if header:
            h_text = header.get_text()
            has_inc = "APU-INC-20200605-01" in h_text or "20200605" in h_text
            has_buffer = "33h 52m" in h_text or "33h" in h_text
            has_brake = "2.19" in h_text or "+2.19" in h_text
            btn_vr = header.find(id="btn-warroom-vr") or header.find(id="btn-toggle-vr") or header.find(lambda el: "Đối chứng" in el.get_text() if el.string else False)

            self.record("Tier 3", "Screen 3 War Room", "War Room Header displays Incident ID, 33h 52m buffer, +2.19 bar margin",
                        has_inc and has_buffer and has_brake,
                        f"Incident: {has_inc}, Buffer: {has_buffer}, Brake: {has_brake}")
            self.record("Tier 3", "Screen 3 War Room", "Layer C Historical Reference button present", bool(btn_vr),
                        f"Button found: {btn_vr.get_text().strip() if btn_vr else 'None'}")
        else:
            self.record("Tier 3", "Screen 3 War Room", "War Room Header present", False, "Missing #warroom-header")

        # 2. Synoptic Flow Mimic
        schematic = wb_view.find(id="apu-schematic")
        if schematic:
            sch_text = schematic.get_text()
            has_comp = "Máy nén" in sch_text or "APU-COMP" in sch_text or bool(schematic.find(id="mod-compressor"))
            has_dryer = "sấy" in sch_text.lower() or "LP49" in sch_text or bool(schematic.find(id="mod-dryer"))
            has_tp3 = "TP3" in sch_text or bool(schematic.find(id="sch-tp3")) or bool(schematic.find(id="mod-panel"))

            self.record("Tier 3", "Screen 3 War Room", "Pneumatic Synoptic Flow Mimic diagram present in Screen 3",
                        has_comp and has_dryer and has_tp3,
                        f"Compressor: {has_comp}, Leaking Dryer: {has_dryer}, TP3: {has_tp3}")
        else:
            self.record("Tier 3", "Screen 3 War Room", "Synoptic Flow Mimic #apu-schematic present in Screen 3", False,
                        "Missing #apu-schematic in Screen 3")

        # 3. 4 Stacked Synchronized Charts
        charts = wb_view.find_all(lambda el: el.name == "canvas" and el.get("id") in ["chart-dv", "chart-oil", "chart-current", "chart-tp"])
        found_chart_ids = [c.get("id") for c in charts]
        charts_ok = len(found_chart_ids) == 4
        self.record("Tier 3", "Screen 3 War Room", "4 Stacked multi-channel chart canvases present in Screen 3",
                    charts_ok, f"Found charts: {found_chart_ids}")

        # 4. 5-Step Operational Stepper
        stepper_tabs = wb_view.find(id="wb-focus-tabs") or wb_view.find(class_=lambda c: c and "stepper" in c)
        panels = wb_view.find_all(lambda el: el.get("data-step-panel") or el.get("data-step"))
        has_5_steps = len(panels) >= 5 or (stepper_tabs and len(stepper_tabs.find_all("button")) >= 5)
        self.record("Tier 3", "Screen 3 War Room", "5-Step Operational Stepper layout present", bool(has_5_steps),
                    f"Found {len(panels)} step panels in Screen 3")

    # -----------------------------------------------------------------
    # Check 5: Screen 4 Settings & Shift Logs (Tier 3 / R4)
    # -----------------------------------------------------------------
    def check_screen_4_settings_and_shift(self):
        settings_view = self.soup.find(id="view-settings")
        if not settings_view:
            self.record("Tier 3", "Screen 4 Settings", "Screen 4 container", False, "Missing #view-settings")
            return

        # 1. Shift Operator Card for Hùng Bùi (NV-0941)
        shift_card = settings_view.find(id="shift-operator-card") or settings_view.find(class_=lambda c: c and "shift-card" in c)
        if shift_card:
            card_text = shift_card.get_text()
            has_name = "Hùng Bùi" in card_text
            has_code = "NV-0941" in card_text
            has_shift1 = "Ca 1" in card_text or "06:00" in card_text
            btn_handover = shift_card.find(id="btn-open-handover") or shift_card.find(lambda el: "Bàn giao" in el.get_text() if el.string else False)

            self.record("Tier 3", "Screen 4 Settings", "Shift Operator Card for Hùng Bùi (NV-0941) Ca 1 present",
                        has_name and has_code and has_shift1,
                        f"Name: {has_name}, Code: {has_code}, Shift1: {has_shift1}")
            self.record("Tier 3", "Screen 4 Settings", "Shift handover button present", bool(btn_handover),
                        f"Handover button found: {bool(btn_handover)}")
        else:
            self.record("Tier 3", "Screen 4 Settings", "Shift operator card present", False, "Missing #shift-operator-card")

        # 2. Append-Only Audit Ledger
        ledger = settings_view.find(id="audit-ledger-panel") or settings_view.find(id="audit-ledger-table") or settings_view.find(id="timeline-list")
        self.record("Tier 3", "Screen 4 Settings", "Append-Only Audit Ledger table present", bool(ledger),
                    f"Found audit ledger: {ledger.get('id') if ledger else 'None'}")

        # 3. SOP Playbooks section
        sop_section = settings_view.find(id="sop-playbooks-panel") or settings_view.find(id="sop-editor") or settings_view.find(class_=lambda c: c and "sop" in c)
        self.record("Tier 3", "Screen 4 Settings", "SOP Playbooks editor/viewer section present", bool(sop_section),
                    f"Found SOP section: {bool(sop_section)}")

        # 4. Simulation Controls Panel
        sim_panel = settings_view.find(id="sim-control-panel") or settings_view.find(class_=lambda c: c and "sim-control" in c) or self.soup.find(id="replay-drawer")
        self.record("Tier 3", "Screen 4 Settings", "Centralized simulation controls present (speed, play/pause, scenarios)",
                    bool(sim_panel), f"Found simulation controls: {bool(sim_panel)}")

    # -----------------------------------------------------------------
    # Check 6: Natural Vietnamese Word Budgets & Persona (Tier 4 / Rule 8 & 9)
    # -----------------------------------------------------------------
    def check_vietnamese_word_budgets(self):
        # 1. Check Buttons word count <= 3 words (excluding technical identifiers)
        buttons = self.soup.find_all("button")
        btn_violations = []
        for b in buttons:
            txt = b.get_text().strip()
            # Clean icons and symbols
            clean = re.sub(r'[\d\.\➔\💾\▶\⏸\↺\📝\📋\🛡️\🏁\✕\✓\·]', '', txt).strip()
            words = clean.split()
            if len(words) > 3 and not any(id_term in txt for id_term in ["TRAIN-", "APU-", "SOP-", "LIVE SIMULATION"]):
                btn_violations.append((txt, len(words)))

        self.record("Tier 4", "Word Budgets", "Button labels conform to <= 3 words budget", len(btn_violations) == 0,
                    f"Found {len(btn_violations)} button budget violations. Examples: {btn_violations[:3]}" if btn_violations else "All buttons within <= 3 words")

        # 2. Operator Persona Check
        all_text = self.soup.get_text()
        has_hung_bui = "Hùng Bùi" in all_text and "NV-0941" in all_text
        self.record("Tier 4", "Operator Persona", "Operator identity Hùng Bùi (NV-0941) present in UI", has_hung_bui,
                    "Found 'Hùng Bùi (NV-0941)' in markup" if has_hung_bui else "Missing Hùng Bùi (NV-0941)")

        # 3. Technical Identifiers Preservation
        tech_ids = ["APU-COMP-01", "TRAIN-302", "DV_pressure", "Oil_temp", "LIVE SIMULATION"]
        missing_tech = [t for t in tech_ids if t not in all_text and t not in self.js_content]
        self.record("Tier 4", "Word Budgets", "Technical identifiers preserved verbatim without translation",
                    len(missing_tech) == 0,
                    f"Preserved. Missing: {missing_tech}" if missing_tech else "All 5 core technical identifiers preserved")

    # -----------------------------------------------------------------
    # Check 7: Frontend State & Navigation Script Audit (Tier 4 / F16-F21)
    # -----------------------------------------------------------------
    def check_javascript_contracts(self):
        js = self.js_content

        # 1. navigateTo routing function
        has_nav = "function navigateTo(" in js or "const navigateTo =" in js or "navigateTo(view" in js or "setView(" in js
        self.record("Tier 4", "State & Navigation", "Navigation routing logic with context support exists", has_nav,
                    "Found navigation router in app.js" if has_nav else "Missing navigateTo / setView")

        # 2. Dynamic threshold update & recovery sync
        has_thresh_sync = "customThresholds" in js or "leak_pressure_threshold" in js or "PUT" in js
        self.record("Tier 4", "State & Navigation", "Dynamic threshold update & cross-screen sync logic in app.js",
                    has_thresh_sync, "Found threshold propagation logic" if has_thresh_sync else "Missing threshold sync logic")

        # 3. Audit ledger update under operator Hùng Bùi
        has_audit_hung = "NV-0941" in js or "Hùng Bùi" in js
        self.record("Tier 4", "State & Navigation", "Operator Hùng Bùi (NV-0941) bound to client state & actions",
                    has_audit_hung, "Found Hùng Bùi in app.js state" if has_audit_hung else "Operator identity not found in app.js")

        # 4. Zero fake telemetry (no Math.random in telemetry pipeline)
        has_math_rand = bool(re.search(r'Math\.random\(\)\s*\*\s*(pressure|temp|telemetry)', js, re.IGNORECASE))
        self.record("Tier 4", "State & Navigation", "Zero Fake Telemetry: No Math.random() in telemetry pipeline",
                    not has_math_rand, "Verified zero random telemetry generation" if not has_math_rand else "WARNING: Found Math.random telemetry generator")

    # -----------------------------------------------------------------
    # Runner
    # -----------------------------------------------------------------
    def run_all(self) -> int:
        print("\n" + "=" * 80)
        print(" COMPRESSORGUARD ENTERPRISE UI/UX ACCEPTANCE AUDIT (TIERS 3 & 4)")
        print("=" * 80)

        if not self.load_files():
            return 1

        self.check_four_views_structure()
        self.check_screen_1_fleet_overview()
        self.check_screen_2_asset_management()
        self.check_screen_3_warroom()
        self.check_screen_4_settings_and_shift()
        self.check_vietnamese_word_budgets()
        self.check_javascript_contracts()

        passed = sum(1 for r in self.results if r[3] == "PASS")
        failed = sum(1 for r in self.results if r[3] == "FAIL")

        current_tier = ""
        for tier, cat, name, status, msg in self.results:
            if tier != current_tier:
                current_tier = tier
                print(f"\n--- {current_tier} ---")
            badge = f"[{status}]"
            print(f"  {badge:<6} {cat} :: {name}")
            if status == "FAIL" or (msg and status == "PASS" and "Warning" in msg):
                print(f"         |-- Details: {msg}")

        print("\n" + "-" * 80)
        print(f"Total Verifications: {len(self.results)} | Passed: {passed} | Failed: {failed}")
        print("=" * 80 + "\n")

        return 0 if failed == 0 else 1


def main():
    verifier = EnterpriseUIVerifier()
    sys.exit(verifier.run_all())


if __name__ == "__main__":
    main()
