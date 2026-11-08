"""
Adversarial Empirical Challenge Suite for Milestone 2 (Frontend DOM Structure & CSS Styling).
Author: Challenger 1 (teamwork_challenger_m2_1)
"""

import sys
import os
import re
from html.parser import HTMLParser
from bs4 import BeautifulSoup

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HTML_PATH = os.path.join(WORKSPACE, "src", "static", "index.html")
CSS_PATH = os.path.join(WORKSPACE, "src", "static", "styles.css")

TECHNICAL_TOKENS = {
    "APU-COMP-01", "APU-DRY-LP49", "APU-RES-TP3", "APU-SW-LPS",
    "TRAIN-301", "TRAIN-302", "TRAIN-303", "NV-0941", "HÙNG", "BÙI",
    "APU", "TCMS", "HMI", "SLA", "APM", "TP3", "LP49", "LPS", "OCC", "HURC1",
    "P1", "P2", "P3", "SOP", "SOP-01", "SOP-02", "SOP-03", "SOP-04",
    "DV_PRESSURE", "OIL_TEMP", "MOTOR_CURRENT", "TP_PRESSURE",
    "LOADED", "UNLOADED", "PASS", "FAIL", "LIVE", "SIMULATION", "HISTORICAL", "DATA",
    "SHIFT", "S", "+", "->", "➔", "—", "-", "/", ":", "1X", "5X", "20X", "60X", "300X",
    "BAR", "°C", "A", "H", "M", "33H", "52M", "+2.19"
}

def clean_word_count(text):
    clean = re.sub(r'[\(\)\[\]\{\}\.,:;!\?_\\/\-➔➔\+—]', ' ', text)
    words = [w for w in clean.split() if w.strip()]
    content_words = []
    for w in words:
        if w.upper() in TECHNICAL_TOKENS:
            continue
        if re.match(r'^[0-9]+(\.[0-9]+)?(h|m|s|bar|°C|A|x)?$', w, re.IGNORECASE):
            continue
        if re.match(r'^(P[1-9]|SOP-[0-9]+|TRAIN-[0-9]+|APU-[A-Z0-9\-]+|NV-[0-9]+)$', w, re.IGNORECASE):
            continue
        content_words.append(w)
    return len(content_words), content_words

class StrictTagParser(HTMLParser):
    VOID_TAGS = {
        'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
        'link', 'meta', 'param', 'source', 'track', 'wbr'
    }

    def __init__(self):
        super().__init__()
        self.stack = []
        self.tag_mismatches = []
        self.unclosed_tags = []
        self.stray_closing_tags = []
        self.all_ids = []
        self.duplicate_ids = set()
        self._seen_ids = set()

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        elem_id = attr_dict.get('id')
        if elem_id:
            self.all_ids.append(elem_id)
            if elem_id in self._seen_ids:
                self.duplicate_ids.add(elem_id)
            self._seen_ids.add(elem_id)

        if tag.lower() not in self.VOID_TAGS:
            self.stack.append((tag.lower(), self.getpos()))

    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        if tag_lower in self.VOID_TAGS:
            return

        if not self.stack:
            self.stray_closing_tags.append((tag_lower, self.getpos()))
            return

        last_tag, last_pos = self.stack[-1]
        if last_tag == tag_lower:
            self.stack.pop()
        else:
            found_idx = None
            for idx in range(len(self.stack) - 1, -1, -1):
                if self.stack[idx][0] == tag_lower:
                    found_idx = idx
                    break
            if found_idx is not None:
                for i in range(len(self.stack) - 1, found_idx, -1):
                    self.unclosed_tags.append(self.stack[i])
                self.stack = self.stack[:found_idx]
            else:
                self.stray_closing_tags.append((tag_lower, self.getpos()))

    def finalize(self):
        while self.stack:
            self.unclosed_tags.append(self.stack.pop())

def main():
    print("=" * 80)
    print(" ADVERSARIAL CHALLENGE SUITE: MILESTONE 2 (DOM & CSS)")
    print("=" * 80)

    if not os.path.exists(HTML_PATH):
        print(f"[CRITICAL FAIL] File not found: {HTML_PATH}")
        sys.exit(1)

    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")
    errors = []
    warnings = []

    # -------------------------------------------------------------
    # 1. HTML Tag & DOM Syntax Integrity
    # -------------------------------------------------------------
    print("\n--- [TEST 1] HTML Tag Balance & ID Uniqueness ---")
    parser = StrictTagParser()
    parser.feed(html_content)
    parser.finalize()

    if parser.unclosed_tags:
        for t, pos in parser.unclosed_tags[:5]:
            errors.append(f"Unclosed tag <{t}> opened at line {pos[0]}, col {pos[1]}")
        print(f"  [FAIL] Found {len(parser.unclosed_tags)} unclosed tags")
    else:
        print("  [PASS] Zero unclosed tags found.")

    if parser.stray_closing_tags:
        for t, pos in parser.stray_closing_tags[:5]:
            errors.append(f"Stray closing tag </{t}> at line {pos[0]}, col {pos[1]}")
        print(f"  [FAIL] Found {len(parser.stray_closing_tags)} stray closing tags")
    else:
        print("  [PASS] Zero stray closing tags found.")

    if parser.duplicate_ids:
        for dup in sorted(parser.duplicate_ids):
            errors.append(f"Duplicate element ID: #{dup}")
        print(f"  [FAIL] Duplicate IDs found: {parser.duplicate_ids}")
    else:
        print(f"  [PASS] All {len(parser.all_ids)} element IDs are unique across DOM.")

    # -------------------------------------------------------------
    # 2. Screen 1: Isolation & Leak Detection
    # -------------------------------------------------------------
    print("\n--- [TEST 2] Screen 1 (#view-fleet) Isolation & Leaks ---")
    view_fleet = soup.find(id="view-fleet")
    if not view_fleet:
        errors.append("Missing #view-fleet container")
        print("  [FAIL] #view-fleet container missing")
    else:
        fleet_canvases = view_fleet.find_all("canvas")
        if fleet_canvases:
            errors.append(f"Canvas element leaked into #view-fleet: {[c.get('id') for c in fleet_canvases]}")
            print(f"  [FAIL] Canvas leaked into Screen 1: {fleet_canvases}")
        else:
            print("  [PASS] Zero <canvas> elements in Screen 1.")

        leaked_charts = view_fleet.find_all(id=re.compile(r'chart-(dv|oil|current|tp)'))
        if leaked_charts:
            errors.append(f"Wave chart container leaked into Screen 1: {[c.get('id') for c in leaked_charts]}")
            print(f"  [FAIL] Leaked wave charts in Screen 1: {leaked_charts}")
        else:
            print("  [PASS] Zero wave chart containers in Screen 1.")

        leaked_sigma = view_fleet.find_all(id=re.compile(r'(if-read|if-fill|suppression-stream|sigma)'))
        if leaked_sigma:
            errors.append(f"Sigma / Isolation Forest widget leaked into Screen 1: {[s.get('id') for s in leaked_sigma]}")
            print(f"  [FAIL] Leaked sigma widgets in Screen 1: {leaked_sigma}")
        else:
            print("  [PASS] Zero sigma / Isolation Forest widgets in Screen 1.")

        hero = view_fleet.find(id="hero-p1-banner")
        if not hero:
            errors.append("Missing #hero-p1-banner in Screen 1")
            print("  [FAIL] Missing #hero-p1-banner")
        else:
            hero_text = hero.get_text()
            if "TRAIN-302" not in hero_text:
                errors.append("Hero banner does not mention TRAIN-302")
            if "33h 52m" not in hero_text and "33 giờ 52" not in hero_text:
                errors.append("Hero banner does not mention 33h 52m safety buffer")
            btn_goto_warroom = hero.find(id="btn-hero-goto-warroom")
            if not btn_goto_warroom:
                errors.append("Hero banner missing #btn-hero-goto-warroom")
            print("  [PASS] Hero banner structure, safety buffer, and CTA validated.")

        kpi_grid = view_fleet.find(id="fleet-kpi-grid")
        if not kpi_grid:
            errors.append("Missing #fleet-kpi-grid in Screen 1")
            print("  [FAIL] Missing #fleet-kpi-grid")
        else:
            kpi_cards = kpi_grid.find_all(class_=re.compile(r'fleet-kpi-card'))
            if len(kpi_cards) != 4:
                errors.append(f"Expected 4 KPI cards in Screen 1, found {len(kpi_cards)}")
                print(f"  [FAIL] Found {len(kpi_cards)} KPI cards (expected 4)")
            else:
                kpi_text = kpi_grid.get_text()
                if "3/3" not in kpi_text:
                    errors.append("KPI grid missing 3/3 total trains")
                if "Long Bình" not in kpi_text:
                    errors.append("KPI grid missing Depot Long Bình")
                print("  [PASS] 4 KPI cards (3/3, 2, 1, Long Bình) verified.")

        fleet_grid = view_fleet.find(id="fleet-cards-grid") or view_fleet.find(id="fleet-grid")
        if not fleet_grid:
            errors.append("Missing #fleet-cards-grid in Screen 1")
            print("  [FAIL] Missing #fleet-cards-grid")
        else:
            train_cards = fleet_grid.find_all(attrs={"data-train-card": True})
            if len(train_cards) != 3:
                errors.append(f"Expected 3 train cards in #fleet-cards-grid, found {len(train_cards)}")
                print(f"  [FAIL] Found {len(train_cards)} train cards (expected 3)")
            else:
                card_texts = [c.get_text() for c in train_cards]
                has_301 = any("301" in t for t in card_texts)
                has_302 = any("302" in t for t in card_texts)
                has_303 = any("303" in t for t in card_texts)
                if not (has_301 and has_302 and has_303):
                    errors.append("Fleet cards missing one of TRAIN-301, 302, 303")
                print("  [PASS] 3 Fleet Cards for TRAIN-301, TRAIN-302, TRAIN-303 verified.")

    topbar_btn = soup.find(id="btn-toggle-replay") or soup.find(id="btn-quick-simulation")
    if not topbar_btn:
        errors.append("Missing quick simulation button on Topbar")
        print("  [FAIL] Missing Topbar quick simulation button")
    else:
        print(f"  [PASS] Topbar quick simulation button present: #{topbar_btn.get('id')}")

    # -------------------------------------------------------------
    # 3. Screen 2: Master-Detail & 6 Form Inputs
    # -------------------------------------------------------------
    print("\n--- [TEST 3] Screen 2 (#view-assets) Master-Detail & Form ---")
    view_assets = soup.find(id="view-assets")
    if not view_assets:
        errors.append("Missing #view-assets container")
        print("  [FAIL] Missing #view-assets")
    else:
        md_layout = view_assets.find(id="asset-master-detail") or view_assets.find(class_=re.compile(r'asset-master-detail'))
        if not md_layout:
            errors.append("Missing #asset-master-detail layout in Screen 2")
            print("  [FAIL] Missing #asset-master-detail")
        else:
            print("  [PASS] #asset-master-detail layout container found.")

        tree = view_assets.find(id="asset-tree-container") or view_assets.find(id="asset-tree")
        if not tree:
            errors.append("Missing #asset-tree-container / #asset-tree")
            print("  [FAIL] Missing asset tree container")
        else:
            tree_text = tree.get_text()
            required_tree_nodes = ["Metro Line 1", "TRAIN-301", "TRAIN-302", "TRAIN-303", "APU", "APU-COMP-01", "APU-DRY-LP49", "APU-RES-TP3", "APU-SW-LPS"]
            missing_nodes = [node for node in required_tree_nodes if node not in tree_text]
            if missing_nodes:
                errors.append(f"Asset tree missing nodes: {missing_nodes}")
                print(f"  [FAIL] Asset tree missing nodes: {missing_nodes}")
            else:
                print("  [PASS] Asset tree hierarchy (Line 1 -> 3 Trains -> APU -> 4 subcomponents) verified.")

        form = view_assets.find(id="asset-config-form")
        if not form:
            errors.append("Missing #asset-config-form in Screen 2")
            print("  [FAIL] Missing #asset-config-form")
        else:
            required_inputs = [
                ("leak pressure threshold", ["cfg-leak-threshold", "leak_pressure_threshold_bar"]),
                ("oil temp threshold", ["cfg-oil-threshold", "cfg-oil-temp-threshold", "oil_temp_threshold_c"]),
                ("maintenance depot", ["cfg-depot", "maintenance_depot"]),
                ("transient filter", ["cfg-transient-filter", "transient_filter"]),
                ("supervision priority", ["cfg-supervision-prio", "cfg-supervision-priority", "supervision_priority"]),
                ("maintenance notes", ["cfg-maint-notes", "cfg-maintenance-notes", "maintenance_notes"])
            ]
            for label, identifiers in required_inputs:
                elem = None
                for ident in identifiers:
                    elem = form.find(id=ident) or form.find(attrs={"name": ident})
                    if elem:
                        break
                if not elem:
                    errors.append(f"Missing form input for {label} (checked {identifiers})")
                    print(f"  [FAIL] Missing input: {label}")
                else:
                    print(f"  [PASS] Form input found: {label} ({elem.get('id') or elem.get('name')})")

            save_btn = form.find(id="btn-save-asset-config") or form.find(lambda el: el.name == "button" and "Lưu" in el.get_text())
            if not save_btn:
                errors.append("Missing #btn-save-asset-config in Screen 2 form")
                print("  [FAIL] Missing #btn-save-asset-config")
            else:
                print("  [PASS] Save button #btn-save-asset-config verified.")

    # -------------------------------------------------------------
    # 4. Screen 3: War Room, Mimic & 4 Stacked Charts
    # -------------------------------------------------------------
    print("\n--- [TEST 4] Screen 3 (#view-workbench) War Room & Mimic ---")
    view_workbench = soup.find(id="view-workbench")
    if not view_workbench:
        errors.append("Missing #view-workbench container")
        print("  [FAIL] Missing #view-workbench")
    else:
        header = view_workbench.find(id="warroom-header")
        if not header:
            errors.append("Missing #warroom-header in Screen 3")
            print("  [FAIL] Missing #warroom-header")
        else:
            hdr_text = header.get_text()
            if "APU-INC-20200605-01" not in hdr_text:
                errors.append("War room header missing incident ID APU-INC-20200605-01")
            if "33h 52m" not in hdr_text and "33 giờ 52" not in hdr_text:
                errors.append("War room header missing safety buffer 33h 52m")
            if "+2.19" not in hdr_text and "2.19" not in hdr_text:
                errors.append("War room header missing brake margin +2.19 bar")
            btn_vr = header.find(id="btn-warroom-vr") or header.find(id="btn-toggle-vr")
            if not btn_vr:
                errors.append("War room header missing Layer C toggle button #btn-warroom-vr")
            print("  [PASS] War Room header (Incident, buffer, brake margin, Layer C toggle) verified.")

        mimic = view_workbench.find(id="apu-schematic")
        if not mimic:
            errors.append("Missing synoptic flow mimic #apu-schematic in Screen 3")
            print("  [FAIL] Missing #apu-schematic")
        else:
            mimic_text = mimic.get_text()
            if "APU-COMP-01" not in mimic_text and "MÁY NÉN" not in mimic_text.upper():
                errors.append("Mimic missing compressor representation")
            if "LP49" not in mimic_text:
                errors.append("Mimic missing LP49 dryer/drain valve representation")
            if "TP3" not in mimic_text:
                errors.append("Mimic missing TP3 main reservoir representation")
            print("  [PASS] Pneumatic Flow Mimic #apu-schematic verified.")

        chart_canvases = [
            ("chart-dv", view_workbench.find(id="chart-dv")),
            ("chart-oil", view_workbench.find(id="chart-oil")),
            ("chart-current", view_workbench.find(id="chart-current")),
            ("chart-tp", view_workbench.find(id="chart-tp"))
        ]
        missing_charts = [cid for cid, elem in chart_canvases if not elem]
        if missing_charts:
            errors.append(f"Missing chart canvases in Screen 3: {missing_charts}")
            print(f"  [FAIL] Missing chart canvases: {missing_charts}")
        else:
            print("  [PASS] All 4 chart canvases (chart-dv, chart-oil, chart-current, chart-tp) present in Screen 3.")

        stepper = view_workbench.find(id="wb-focus-tabs") or view_workbench.find(class_=re.compile(r'stepper'))
        if not stepper:
            errors.append("Missing 5-step stepper in Screen 3")
            print("  [FAIL] Missing 5-step stepper")
        else:
            step_buttons = stepper.find_all(class_=re.compile(r'(step-pill|wb-step-btn)')) or stepper.find_all("button")
            if len(step_buttons) < 5:
                errors.append(f"Expected at least 5 steps in stepper, found {len(step_buttons)}")
                print(f"  [FAIL] Stepper has only {len(step_buttons)} steps")
            else:
                print(f"  [PASS] 5-step stepper layout with {len(step_buttons)} steps verified.")

    # -------------------------------------------------------------
    # 5. Screen 4: Settings & Shift Logs
    # -------------------------------------------------------------
    print("\n--- [TEST 5] Screen 4 (#view-settings) Shift & Ledger ---")
    view_settings = soup.find(id="view-settings")
    if not view_settings:
        errors.append("Missing #view-settings container")
        print("  [FAIL] Missing #view-settings")
    else:
        op_card = view_settings.find(id="shift-operator-card")
        if not op_card:
            errors.append("Missing #shift-operator-card in Screen 4")
            print("  [FAIL] Missing #shift-operator-card")
        else:
            op_text = op_card.get_text()
            if "Hùng Bùi" not in op_text and "NV-0941" not in op_text:
                errors.append("Shift operator card missing operator Hùng Bùi (NV-0941)")
            if "Ca 1" not in op_text and "Shift 1" not in op_text and "06:00" not in op_text:
                errors.append("Shift operator card missing Ca 1 / 06:00 - 14:00")
            btn_handover = op_card.find(id="btn-open-handover") or op_card.find(id="btn-shift-handover")
            if not btn_handover:
                errors.append("Missing handover button in Shift card")
            print("  [PASS] Shift operator card for Hùng Bùi (NV-0941) verified.")

        ledger = view_settings.find(id="audit-ledger-panel") or view_settings.find(id="audit-ledger-table")
        if not ledger:
            errors.append("Missing audit ledger in Screen 4")
            print("  [FAIL] Missing audit ledger")
        else:
            print("  [PASS] Audit ledger panel / table verified.")

        sop_panel = view_settings.find(id="sop-playbooks-panel") or view_settings.find(id="sop-playbooks-list")
        if not sop_panel:
            errors.append("Missing SOP Playbooks section in Screen 4")
            print("  [FAIL] Missing SOP Playbooks section")
        else:
            print("  [PASS] SOP Playbooks section verified.")

        sim_panel = view_settings.find(id="sim-control-panel")
        if not sim_panel:
            errors.append("Missing simulation control panel in Screen 4")
            print("  [FAIL] Missing simulation control panel")
        else:
            sim_text = sim_panel.get_text()
            if "1x" not in sim_text and "300x" not in sim_text:
                errors.append("Simulation panel missing speed controls (1x..300x)")
            print("  [PASS] Simulation control panel verified.")

    # -------------------------------------------------------------
    # 6. Industrial Word Budgets & Headings Stress Testing
    # -------------------------------------------------------------
    print("\n--- [TEST 6] Industrial Word Budget Stress Testing ---")
    all_buttons = soup.find_all("button")
    button_violations = []
    for btn in all_buttons:
        raw_text = btn.get_text(separator=' ').strip()
        count, words = clean_word_count(raw_text)
        btn_id = btn.get("id") or btn.get("class") or "unnamed-button"
        if count > 3:
            button_violations.append((btn_id, raw_text, count, words))

    if button_violations:
        for b_id, b_text, c, w in button_violations:
            errors.append(f"Button word budget violation ({c} words > 3): [{b_id}] '{b_text}' -> content words: {w}")
        print(f"  [FAIL] Found {len(button_violations)} button word budget violations:")
        for b_id, b_text, c, w in button_violations[:5]:
            print(f"    - [{b_id}] '{b_text}' ({c} words: {w})")
    else:
        print(f"  [PASS] All {len(all_buttons)} buttons strictly conform to <= 3 words budget.")

    # Check Headings (h1, h2, h3, h4)
    heading_analysis = []
    all_headings = soup.find_all(["h1", "h2", "h3", "h4"])
    for h in all_headings:
        raw_text = h.get_text(separator=' ').strip()
        count, words = clean_word_count(raw_text)
        h_id = h.get("id") or h.get("class") or h.name
        heading_analysis.append((h.name, h_id, raw_text, count, words))

    print(f"\n  [INFO] Total Headings inspected: {len(heading_analysis)}")
    for tag, h_id, text, c, w in heading_analysis:
        status_tag = "OK" if c <= 3 else "OVER_BUDGET"
        print(f"    [{status_tag}] <{tag}> [{h_id}] '{text}' -> {c} content words: {w}")

    # -------------------------------------------------------------
    # 7. CSS File Integrity & Dimensions
    # -------------------------------------------------------------
    print("\n--- [TEST 7] CSS File Integrity & Dimensions ---")
    if not os.path.exists(CSS_PATH):
        errors.append(f"Missing CSS file: {CSS_PATH}")
        print(f"  [FAIL] Missing CSS file: {CSS_PATH}")
    else:
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            css_content = f.read()

        open_braces = css_content.count("{")
        close_braces = css_content.count("}")
        if open_braces != close_braces:
            errors.append(f"Unbalanced braces in CSS: {open_braces} open vs {close_braces} close")
            print(f"  [FAIL] Unbalanced CSS braces: {open_braces} open vs {close_braces} close")
        else:
            print(f"  [PASS] CSS braces balanced ({open_braces} rules).")

        chart_heights = re.findall(r'(\.chart-[a-zA-Z0-9\-_]+|\.warroom-charts|canvas)[\s\S]*?height:\s*([0-9]+px)', css_content)
        print(f"  [INFO] Chart height rules in CSS: {chart_heights[:5]}")

        md_matches = re.findall(r'(\.asset-master-detail|\.asset-tree-col|\.asset-detail-col)[\s\S]*?(grid-template-columns|width|flex)[\s\S]*?;', css_content)
        print(f"  [INFO] Master-Detail rules in CSS: {len(md_matches)} rules")

    print("\n" + "=" * 80)
    print(f" SUMMARY: {len(errors)} ERRORS, {len(warnings)} WARNINGS")
    print("=" * 80)
    if errors:
        for e in errors:
            print(f"  [ERROR] {e}")
        return False
    else:
        print("  ALL EMPIRICAL DOM & CSS CHECKS PASSED SUCCESSFULLY!")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
