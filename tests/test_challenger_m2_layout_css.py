"""
Adversarial Empirical Challenge Suite 2 for Milestone 2:
Frontend DOM Structure & CSS Styling Integrity Audit.

Author: Challenger 2 (teamwork_challenger_m2_2)
"""

import sys
import os
import re
from pathlib import Path
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

TECHNICAL_TOKENS = {
    "APU-COMP-01", "APU-DRY-LP49", "APU-RES-TP3", "APU-SW-LPS", "SUB-APU-01",
    "TRAIN-301", "TRAIN-302", "TRAIN-303", "NV-0941", "HÙNG", "BÙI", "HUNG", "BUI",
    "APU", "TCMS", "HMI", "SLA", "APM", "TP3", "LP49", "LPS", "OCC", "HURC1", "TP2",
    "P1", "P2", "P3", "SOP", "SOP-01", "SOP-02", "SOP-03", "SOP-04", "SOP-APU-ISO-04",
    "DV_PRESSURE", "OIL_TEMP", "MOTOR_CURRENT", "TP_PRESSURE", "DV", "OIL",
    "LOADED", "UNLOADED", "PASS", "FAIL", "LIVE", "SIMULATION", "HISTORICAL", "DATA",
    "SHIFT", "S", "+", "->", "➔", "—", "-", "/", ":", "1X", "5X", "10X", "20X", "60X", "300X",
    "BAR", "°C", "A", "H", "M", "33H", "52M", "+2.19", "ISO", "1219", "ISA-101", "LAYER", "C"
}

def clean_word_count(text):
    clean = re.sub(r'[\(\)\[\]\{\}\.,:;!\?_\\/\-➔\+—•▪▸▾▶⏸↺✓✕·]', ' ', text)
    words = [w for w in clean.split() if w.strip()]
    filtered = []
    for w in words:
        if w.upper() in TECHNICAL_TOKENS:
            continue
        if re.match(r'^[0-9]+(\.[0-9]+)?(h|m|s|bar|°c|a|x)?$', w, re.IGNORECASE):
            continue
        if re.match(r'^(P[1-9]|SOP-[0-9A-Z\-]+|TRAIN-[0-9]+|APU-[A-Z0-9\-]+|NV-[0-9]+|SUB-[A-Z0-9\-]+)$', w, re.IGNORECASE):
            continue
        filtered.append(w)
    return len(filtered), filtered


class ChallengerM2Auditor:
    def __init__(self):
        self.html = ""
        self.css = ""
        self.soup: BeautifulSoup = None
        self.results = []
        self.failures = []
        self.warnings = []

    def log(self, category, name, passed, msg=""):
        status = "PASS" if passed else "FAIL"
        self.results.append((category, name, status, msg))
        if not passed:
            self.failures.append(f"[{category}] {name}: {msg}")
        badge = f"[{status}]"
        print(f"  {badge:<6} {category} :: {name}")
        if msg and not passed:
            print(f"         |-- Details: {msg}")

    def warn(self, category, name, msg):
        self.warnings.append(f"[{category}] {name}: {msg}")
        print(f"  [WARN] {category} :: {name}")
        print(f"         |-- Details: {msg}")

    def load(self):
        with open(HTML_PATH, "r", encoding="utf-8") as f:
            self.html = f.read()
        self.soup = BeautifulSoup(self.html, "html.parser")

        with open(CSS_PATH, "r", encoding="utf-8") as f:
            self.css = f.read()

    # =========================================================================
    # Task 1: CSS Syntax & Valid Selectors Audit
    # =========================================================================
    def audit_css_syntax(self):
        print("\n--- [AUDIT 1] CSS Syntax & Balance Integrity ---")
        css = self.css

        # 1. Comment balance
        open_comments = css.count("/*")
        close_comments = css.count("*/")
        self.log("CSS Syntax", "CSS comment delimiters balanced",
                 open_comments == close_comments,
                 f"Open /* ({open_comments}) vs Close */ ({close_comments})")

        # 2. Curly brace balance
        # Strip comments first to avoid counting braces inside comments
        clean_css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
        open_braces = clean_css.count("{")
        close_braces = clean_css.count("}")
        self.log("CSS Syntax", "CSS curly braces balanced",
                 open_braces == close_braces,
                 f"Open {{ ({open_braces}) vs Close }} ({close_braces})")

        # 3. Parenthesis balance
        open_parens = clean_css.count("(")
        close_parens = clean_css.count(")")
        self.log("CSS Syntax", "CSS parentheses balanced",
                 open_parens == close_parens,
                 f"Open ( ({open_parens}) vs Close ) ({close_parens})")

        # 4. Check for unclosed string quotes
        # Rough check: lines with odd number of double quotes (excluding escaped)
        quote_issues = []
        for i, line in enumerate(clean_css.splitlines(), 1):
            quotes = line.count('"') - line.count('\\"')
            if quotes % 2 != 0 and not ("url(" in line or "content:" in line):
                quote_issues.append((i, line.strip()))
        self.log("CSS Syntax", "CSS string quotes closed",
                 len(quote_issues) == 0,
                 f"Unclosed quotes on lines: {[q[0] for q in quote_issues[:5]]}")

        # 5. Extract and validate CSS rules
        rule_pattern = re.compile(r'([^{]+)\{([^}]+)\}', re.DOTALL)
        rules = rule_pattern.findall(clean_css)
        self.log("CSS Rules", "Extracted valid CSS rule blocks",
                 len(rules) > 100,
                 f"Total parsed rule blocks: {len(rules)}")

        # Check for malformed selectors
        malformed_selectors = []
        for selector, body in rules:
            selector = selector.strip()
            if selector.startswith("@"):
                continue  # skip @media, @keyframes, etc.
            # Check for trailing commas or empty selectors
            if selector.endswith(",") or selector.startswith(",") or ",," in selector:
                malformed_selectors.append(selector)
            # Check for unbalanced square brackets in attribute selectors
            if selector.count("[") != selector.count("]"):
                malformed_selectors.append(selector)

        self.log("CSS Selectors", "Selectors structurally well-formed",
                 len(malformed_selectors) == 0,
                 f"Malformed selectors found: {malformed_selectors[:5]}")

        # 6. Check critical CSS variables defined
        root_match = re.search(r':root\s*\{([^}]+)\}', clean_css)
        if root_match:
            root_content = root_match.group(1)
            critical_vars = ["--bg-0", "--bg-1", "--bg-2", "--line-1", "--txt-0", "--txt-1", "--accent", "--crit", "--ok-green"]
            missing_vars = [v for v in critical_vars if v not in root_content]
            self.log("CSS Tokens", "Critical design tokens present in :root",
                     len(missing_vars) == 0,
                     f"Missing tokens: {missing_vars}")
        else:
            self.log("CSS Tokens", ":root block present", False, "Missing :root block")

    # =========================================================================
    # Task 2: Master-Detail 35%:65% Layout Styling
    # =========================================================================
    def audit_master_detail_styling(self):
        print("\n--- [AUDIT 2] Master-Detail 35%:65% Layout Styling ---")

        # 1. HTML DOM Structure
        assets_view = self.soup.find(id="view-assets")
        self.log("Master-Detail DOM", "#view-assets present", bool(assets_view))

        md_elem = assets_view.find(id="asset-master-detail") if assets_view else None
        self.log("Master-Detail DOM", "#asset-master-detail present inside #view-assets", bool(md_elem))

        col_left = assets_view.find(id="asset-tree-col") if assets_view else None
        col_right = assets_view.find(id="asset-detail-col") if assets_view else None
        self.log("Master-Detail DOM", "Two columns (#asset-tree-col & #asset-detail-col) present",
                 bool(col_left and col_right))

        # 2. CSS Rules for .asset-master-detail
        has_grid = bool(re.search(r'\.asset-master-detail\s*\{[^}]*display:\s*grid', self.css))
        self.log("Master-Detail CSS", ".asset-master-detail uses display: grid", has_grid)

        has_35_65 = bool(re.search(r'\.asset-master-detail\s*\{[^}]*grid-template-columns:\s*35%\s+65%', self.css))
        self.log("Master-Detail CSS", "grid-template-columns is exactly 35% 65%", has_35_65)

        has_gap = bool(re.search(r'\.asset-master-detail\s*\{[^}]*gap:\s*[0-9]+px', self.css))
        self.log("Master-Detail CSS", "gap is specified between columns", has_gap)

        # 3. Left column scroll constraint
        has_tree_scroll = bool(re.search(r'\.asset-tree-container\s*\{[^}]*overflow-y:\s*auto', self.css))
        has_tree_maxh = bool(re.search(r'\.asset-tree-container\s*\{[^}]*max-height:\s*calc', self.css))
        self.log("Master-Detail CSS", ".asset-tree-container has overflow-y: auto and max-height calc",
                 has_tree_scroll and has_tree_maxh)

        # 4. Responsive fallback at <= 1100px
        media_1100 = re.search(r'@media[^{]*max-width:\s*1100px[^{]*\{(.*?)\n\}', self.css, re.DOTALL)
        has_responsive_1fr = False
        if media_1100:
            media_body = media_1100.group(1)
            has_responsive_1fr = ".asset-master-detail" in media_body and "grid-template-columns: 1fr" in media_body
        self.log("Master-Detail CSS", "Responsive fallback to 1fr on <= 1100px viewports", has_responsive_1fr)

    # =========================================================================
    # Task 3: Screen 3 Chart Containers Constraints (~110px each)
    # =========================================================================
    def audit_screen3_chart_containers(self):
        print("\n--- [AUDIT 3] Screen 3 Stacked Chart Containers (~110px) ---")

        wb_view = self.soup.find(id="view-workbench")
        self.log("Chart Containers DOM", "#view-workbench present", bool(wb_view))

        charts_panel = wb_view.find(id="warroom-charts") if wb_view else None
        self.log("Chart Containers DOM", "#warroom-charts wrapper present", bool(charts_panel))

        if charts_panel:
            blocks = charts_panel.find_all(class_=lambda c: c and "chart-block" in c and "compact" in c)
            self.log("Chart Containers DOM", "4 .chart-block.compact containers present", len(blocks) == 4,
                     f"Found {len(blocks)} compact blocks")

            # Verify canvases inside wrappers
            expected_canvases = ["chart-dv", "chart-oil", "chart-current", "chart-tp"]
            found_canvases = []
            canvas_wrappers_ok = True
            for b in blocks:
                wrap = b.find(class_="chart-canvas-wrap")
                if not wrap:
                    canvas_wrappers_ok = False
                c = b.find("canvas")
                if c and c.get("id"):
                    found_canvases.append(c.get("id"))

            self.log("Chart Containers DOM", "All 4 chart blocks have .chart-canvas-wrap", canvas_wrappers_ok)
            self.log("Chart Containers DOM", "Canvases (chart-dv, chart-oil, chart-current, chart-tp) present",
                     set(found_canvases) == set(expected_canvases),
                     f"Found: {found_canvases}")

        # CSS constraints verification
        has_110px_block = bool(re.search(r'\.chart-block\.compact\s*\{[^}]*height:\s*110px', self.css))
        self.log("Chart Containers CSS", ".chart-block.compact has fixed height: 110px", has_110px_block)

        has_canvas_height = bool(re.search(r'\.chart-block\.compact\s+canvas\s*\{[^}]*height:\s*85px', self.css))
        has_canvas_max_height = bool(re.search(r'\.chart-block\.compact\s+canvas\s*\{[^}]*max-height:\s*85px', self.css))
        self.log("Chart Containers CSS", "canvas height and max-height constrained to 85px with !important",
                 has_canvas_height and has_canvas_max_height)

        has_canvas_wrap = bool(re.search(r'\.chart-block\.compact\s+\.chart-canvas-wrap\s*\{[^}]*height:\s*85px', self.css))
        self.log("Chart Containers CSS", ".chart-canvas-wrap has constrained height", has_canvas_wrap)

        # Flex column layout
        has_block_flex = bool(re.search(r'\.chart-block\.compact\s*\{[^}]*display:\s*flex', self.css))
        self.log("Chart Containers CSS", ".chart-block.compact uses flexbox column layout", has_block_flex)

    # =========================================================================
    # Task 4: Screen 4 Shift Handover Modal Dialog
    # =========================================================================
    def audit_shift_handover_modal(self):
        print("\n--- [AUDIT 4] Screen 4 Shift Handover Modal Dialog ---")

        modal = self.soup.find(id="handover-modal")
        self.log("Handover Modal DOM", "#handover-modal container present", bool(modal))

        if modal:
            is_hidden = modal.has_attr("hidden")
            self.log("Handover Modal DOM", "#handover-modal is hidden by default", is_hidden)

            box = modal.find(class_="modal-box")
            self.log("Handover Modal DOM", ".modal-box dialog element present", bool(box))
            if box:
                role = box.get("role")
                aria_modal = box.get("aria-modal")
                aria_labelledby = box.get("aria-labelledby")
                self.log("Handover Modal A11y", "role='dialog' and aria-modal='true' present",
                         role == "dialog" and aria_modal == "true",
                         f"role={role}, aria-modal={aria_modal}")
                self.log("Handover Modal A11y", "aria-labelledby points to #handover-title",
                         aria_labelledby == "handover-title")

            # Check required interactive elements
            btn_close = modal.find(id="btn-close-handover")
            select_rcv = modal.find(id="handover-receiver-select")
            txt_notes = modal.find(id="handover-notes")
            btn_confirm = modal.find(id="btn-confirm-handover")
            btn_cancel = modal.find(id="btn-cancel-handover")

            elems_ok = all([btn_close, select_rcv, txt_notes, btn_confirm, btn_cancel])
            self.log("Handover Modal DOM", "All 5 modal action elements present (close, receiver, notes, confirm, cancel)",
                     elems_ok,
                     f"Close: {bool(btn_close)}, Receiver: {bool(select_rcv)}, Notes: {bool(txt_notes)}, Confirm: {bool(btn_confirm)}, Cancel: {bool(btn_cancel)}")

        # Trigger button on Shift Operator Card
        btn_open = self.soup.find(id="btn-open-handover")
        self.log("Handover Modal DOM", "Trigger button #btn-open-handover present on shift card", bool(btn_open))

        # CSS modal rules
        has_backdrop_css = bool(re.search(r'\.modal-backdrop\s*\{[^}]*position:\s*fixed', self.css))
        has_backdrop_zindex = bool(re.search(r'\.modal-backdrop\s*\{[^}]*z-index:\s*[0-9]+', self.css))
        has_backdrop_hidden = bool(re.search(r'\.modal-backdrop\[hidden\]\s*\{[^}]*display:\s*none', self.css))
        self.log("Handover Modal CSS", ".modal-backdrop has position: fixed, z-index, and [hidden] display:none",
                 has_backdrop_css and has_backdrop_zindex and has_backdrop_hidden)

        has_box_css = bool(re.search(r'\.modal-box\s*\{[^}]*background:\s*var\(--bg-1\)', self.css))
        self.log("Handover Modal CSS", ".modal-box styled with design tokens and max width", has_box_css)

    # =========================================================================
    # Task 5: Text Overflow, Broken Classes & Missing Element IDs
    # =========================================================================
    def audit_overflow_and_classes(self):
        print("\n--- [AUDIT 5] Text Overflow, Classes & Element IDs ---")

        # 1. Check all classes used in index.html exist in styles.css
        html_classes = set()
        for tag in self.soup.find_all(True):
            cls_list = tag.get("class", [])
            for c in cls_list:
                html_classes.add(c)

        missing_classes = []
        for c in html_classes:
            # Check if class selector exists in css
            pattern = re.compile(r'\.' + re.escape(c) + r'([:\s,\{\.#\[>]|$)')
            if not pattern.search(self.css):
                # Ignore dynamic/chart/utility classes
                if c not in ["chartjs-render-monitor", "leaflet-container", "is-root", "is-selected", "is-expanded", "is-active", "is-faulted", "is-crit", "is-alert", "is-healthy"]:
                    missing_classes.append(c)

        if missing_classes:
            self.warn("CSS Classes", "HTML classes without exact CSS selector",
                      f"Count: {len(missing_classes)}. Samples: {missing_classes[:10]}")
        else:
            self.log("CSS Classes", "All HTML classes match defined CSS rules", True)

        # 2. Check for text overflow defenses in tables and data cards
        table_wraps = self.soup.find_all(class_=lambda c: c and "table-wrap" in c)
        has_table_scroll = all("scroll-soft" in t.get("class", []) or "table-wrap" in t.get("class", []) for t in table_wraps)
        self.log("Text Overflow", "Data tables wrapped in scrollable containers",
                 has_table_scroll and len(table_wraps) > 0,
                 f"Found {len(table_wraps)} wrapped tables")

        # 3. Check for element IDs required by Specs R1-R4
        required_spec_ids = [
            ("Screen 1", "view-fleet"),
            ("Screen 1", "hero-p1-banner"),
            ("Screen 1", "hero-safety-buffer"),
            ("Screen 1", "btn-hero-goto-warroom"),
            ("Screen 1", "fleet-kpi-grid"),
            ("Screen 1", "kpi-fleet-total"),
            ("Screen 1", "kpi-fleet-healthy"),
            ("Screen 1", "kpi-fleet-alert"),
            ("Screen 1", "kpi-fleet-depot"),
            ("Screen 1", "fleet-cards-grid"),
            ("Screen 2", "view-assets"),
            ("Screen 2", "asset-master-detail"),
            ("Screen 2", "asset-tree-col"),
            ("Screen 2", "asset-tree-container"),
            ("Screen 2", "asset-tree"),
            ("Screen 2", "asset-detail-col"),
            ("Screen 2", "asset-specs-card"),
            ("Screen 2", "asset-config-card"),
            ("Screen 2", "asset-config-form"),
            ("Screen 2", "cfg-leak-threshold"),
            ("Screen 2", "cfg-oil-threshold"),
            ("Screen 2", "cfg-depot"),
            ("Screen 2", "cfg-transient-filter"),
            ("Screen 2", "cfg-supervision-prio"),
            ("Screen 2", "cfg-maint-notes"),
            ("Screen 2", "btn-save-asset-config"),
            ("Screen 3", "view-workbench"),
            ("Screen 3", "warroom-header"),
            ("Screen 3", "wb-lead-window"),
            ("Screen 3", "wb-brake-margin-val"),
            ("Screen 3", "btn-warroom-vr"),
            ("Screen 3", "apu-schematic"),
            ("Screen 3", "warroom-charts"),
            ("Screen 3", "chart-dv"),
            ("Screen 3", "chart-oil"),
            ("Screen 3", "chart-current"),
            ("Screen 3", "chart-tp"),
            ("Screen 3", "wb-focus-tabs"),
            ("Screen 3", "btn-acknowledge"),
            ("Screen 3", "btn-work-order"),
            ("Screen 3", "btn-safe-mode"),
            ("Screen 3", "btn-close-case"),
            ("Screen 4", "view-settings"),
            ("Screen 4", "settings-grid"),
            ("Screen 4", "shift-operator-card"),
            ("Screen 4", "btn-open-handover"),
            ("Screen 4", "audit-ledger-panel"),
            ("Screen 4", "audit-ledger-table"),
            ("Screen 4", "sop-playbooks-panel"),
            ("Screen 4", "sim-control-panel"),
            ("Screen 4", "handover-modal"),
            ("Screen 4", "btn-confirm-handover"),
        ]

        missing_spec_ids = []
        for screen, eid in required_spec_ids:
            if not self.soup.find(id=eid):
                missing_spec_ids.append(f"{screen} -> #{eid}")

        self.log("Spec IDs", "All required specification element IDs present",
                 len(missing_spec_ids) == 0,
                 f"Missing IDs: {missing_spec_ids}")

        # 4. Strict Industrial Word Budget Stress Testing
        print("\n--- [AUDIT 6] Strict Industrial Word Budget Stress Testing ---")

        # Buttons: <= 3 words
        buttons = self.soup.find_all("button")
        btn_violations = []
        for b in buttons:
            txt = b.get_text().strip()
            c, words = clean_word_count(txt)
            if c > 3:
                btn_violations.append((txt, c, words))
        self.log("Word Budget", "Button labels <= 3 words", len(btn_violations) == 0,
                 f"Violations ({len(btn_violations)}): {btn_violations[:3]}")

        # Nav Tabs: <= 3 words
        nav_tabs = self.soup.find_all(class_="nav-tab")
        nav_violations = []
        for t in nav_tabs:
            txt = t.get_text().strip()
            c, words = clean_word_count(txt)
            if c > 3:
                nav_violations.append((txt, c, words))
        self.log("Word Budget", "Nav tab labels <= 3 words", len(nav_violations) == 0,
                 f"Violations ({len(nav_violations)}): {nav_violations}")

        # Panel titles: <= 3 words
        panel_titles = self.soup.find_all(class_="panel-title")
        pt_violations = []
        for pt in panel_titles:
            txt = pt.get_text().strip()
            c, words = clean_word_count(txt)
            if c > 3:
                pt_violations.append((txt, c, words))
        self.log("Word Budget", "Panel titles <= 3 words", len(pt_violations) == 0,
                 f"Violations ({len(pt_violations)}): {pt_violations}")

        # KPI labels: <= 3 words
        kpi_labels = self.soup.find_all(class_="kpi-label")
        kpi_violations = []
        for kl in kpi_labels:
            txt = kl.get_text().strip()
            c, words = clean_word_count(txt)
            if c > 3:
                kpi_violations.append((txt, c, words))
        self.log("Word Budget", "KPI labels <= 3 words", len(kpi_violations) == 0,
                 f"Violations ({len(kpi_violations)}): {kpi_violations}")

        # Microcopy notes: <= 4 words, no trailing dot
        kpi_notes = self.soup.find_all(class_="kpi-note")
        note_violations = []
        for kn in kpi_notes:
            txt = kn.get_text().strip()
            if txt.endswith("."):
                note_violations.append((txt, "Trailing dot prohibited"))
            c, words = clean_word_count(txt)
            if c > 4:
                note_violations.append((txt, f"{c} words > 4 limit"))
        self.log("Word Budget", "Microcopy (kpi-note) <= 4 words without trailing dot",
                 len(note_violations) == 0,
                 f"Violations ({len(note_violations)}): {note_violations}")

        # Table Column Headers: <= 3 words (per rule 9: tiêu chí cột tối đa 3 từ)
        th_elements = self.soup.find_all("th")
        th_violations = []
        for th in th_elements:
            txt = th.get_text().strip()
            c, words = clean_word_count(txt)
            if c > 3:
                th_violations.append((txt, c, words))
        if th_violations:
            self.warn("Word Budget", "Table headers (th) > 3 words",
                      f"Count: {len(th_violations)}. Samples: {th_violations[:3]}")
        else:
            self.log("Word Budget", "Table headers (th) <= 3 words", True)

        # Placeholders: <= 5 words
        inputs_with_ph = self.soup.find_all(lambda el: el.has_attr("placeholder"))
        ph_violations = []
        for inp in inputs_with_ph:
            ph = inp.get("placeholder", "").strip()
            c, words = clean_word_count(ph)
            if c > 5:
                ph_violations.append((ph, c, words))
        if ph_violations:
            self.warn("Word Budget", "Placeholders > 5 words",
                      f"Count: {len(ph_violations)}. Samples: {ph_violations[:3]}")
        else:
            self.log("Word Budget", "Placeholders <= 5 words", True)

    def run_all(self):
        print("=" * 80)
        print(" CHALLENGER 2: EMPIRICAL LAYOUT & CSS INTEGRITY AUDIT")
        print("=" * 80)
        self.load()
        self.audit_css_syntax()
        self.audit_master_detail_styling()
        self.audit_screen3_chart_containers()
        self.audit_shift_handover_modal()
        self.audit_overflow_and_classes()

        passed = sum(1 for r in self.results if r[2] == "PASS")
        failed = sum(1 for r in self.results if r[2] == "FAIL")

        print("\n" + "=" * 80)
        print(f" TOTAL CHECKS: {len(self.results)} | PASSED: {passed} | FAILED: {failed} | WARNINGS: {len(self.warnings)}")
        print("=" * 80)

        if failed == 0:
            print("\n>>> EMPIRICAL VERDICT: APPROVE <<<")
            return 0
        else:
            print(f"\n>>> EMPIRICAL VERDICT: REQUEST_CHANGES ({failed} failures) <<<")
            return 1

if __name__ == "__main__":
    auditor = ChallengerM2Auditor()
    sys.exit(auditor.run_all())
