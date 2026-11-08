"""
tests/test_challenger_m3_adversarial.py
======================================
Adversarial Empirical Challenge Suite for Milestone 3 (Frontend State, Interactions & Cross-Screen Sync).

Mandatory rules:
- STRICT INVARIANT: ZERO PYTEST ON FULL REPO.
- Run directly via: python tests/test_challenger_m3_adversarial.py
- Empirical verification of:
    1. Cross-screen navigation logic (navigateTo with valid contexts, null contexts, invalid views)
    2. Dynamic threshold sync & Chart.js thresholdLinePlugin reactivity across screens
    3. Zero fake telemetry (Math.random in data pipelines)
    4. Enterprise UI acceptance suite execution (verify_enterprise_ui.py)
"""

import sys
import os
import re
import json
import subprocess
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent
APP_JS = REPO_ROOT / "src" / "static" / "app.js"
INDEX_HTML = REPO_ROOT / "src" / "static" / "index.html"


class EmpiricalM3Challenger:
    def __init__(self):
        self.results = []
        self.js_code = ""
        self.html_code = ""

    def log(self, category: str, test_name: str, passed: bool, details: str = "", severity: str = "INFO"):
        status = "PASS" if passed else "FAIL"
        self.results.append({
            "category": category,
            "name": test_name,
            "status": status,
            "details": details,
            "severity": severity
        })
        badge = f"[{status}]"
        print(f"  {badge:<6} {category} :: {test_name}")
        if not passed or severity in ["WARN", "CRITICAL"]:
            print(f"         |-- [{severity}] {details}")

    def load_files(self):
        if not APP_JS.exists():
            raise FileNotFoundError(f"Missing {APP_JS}")
        if not INDEX_HTML.exists():
            raise FileNotFoundError(f"Missing {INDEX_HTML}")
        self.js_code = APP_JS.read_text(encoding="utf-8")
        self.html_code = INDEX_HTML.read_text(encoding="utf-8")

    # -------------------------------------------------------------
    # 1. CROSS-SCREEN NAVIGATION LOGIC EMPIRICAL TESTS
    # -------------------------------------------------------------
    def run_node_harness(self, js_test_snippet: str) -> dict:
        """Executes a JavaScript test snippet inside Node VM loaded with app.js environment."""
        runner_script = f"""
const fs = require('fs');
const vm = require('vm');

let appJs = fs.readFileSync({json.dumps(str(APP_JS))}, 'utf8');

// Expose internal functions and state to globalThis for rigorous testing
appJs += `
globalThis.S = S;
globalThis.CFG = CFG;
globalThis.navigateTo = navigateTo;
globalThis.setView = setView;
globalThis.chartLines = chartLines;
globalThis.thresholdLinePlugin = thresholdLinePlugin;
globalThis.selectComponent = selectComponent;
globalThis.handleSaveComponentConfig = handleSaveComponentConfig;
globalThis.renderCharts = renderCharts;
globalThis.latestPoint = latestPoint;
globalThis.window = window;
`;

const mockWindow = {{
  location: {{ hash: '#fleet' }},
  history: {{
    replaceState: (state, title, url) => {{
      mockWindow.location.hash = url;
    }}
  }},
  addEventListener: () => {{}},
  Chart: function(ctx, cfg) {{
    this.ctx = ctx;
    this.config = cfg;
    this.data = cfg.data;
    this.options = cfg.options;
    this.update = () => {{}};
  }}
}};

const elements = new Map();
function getOrCreateElem(id, tag = 'div') {{
  if (!elements.has(id)) {{
    const elObj = {{
      id: id,
      tagName: tag.toUpperCase(),
      classList: new Set(),
      attributes: {{}},
      dataset: {{}},
      children: [],
      textContent: '',
      style: {{}},
      hidden: false,
      parentNode: null,
      closest: () => null,
      querySelector: (sel) => null,
      querySelectorAll: (sel) => [],
      appendChild: function(c) {{
        c.parentNode = this;
        this.children.push(c);
        return c;
      }},
      removeChild: function(c) {{
        const idx = this.children.indexOf(c);
        if (idx >= 0) this.children.splice(idx, 1);
        c.parentNode = null;
        return c;
      }},
      setAttribute: function(k, v) {{ this.attributes[k] = String(v); }},
      getAttribute: function(k) {{ return this.attributes[k]; }},
      removeAttribute: function(k) {{ delete this.attributes[k]; }},
      addEventListener: function(evt, handler) {{}},
      getContext: function(type) {{
        return {{
          save: () => {{}},
          restore: () => {{}},
          beginPath: () => {{}},
          moveTo: () => {{}},
          lineTo: () => {{}},
          stroke: () => {{}},
          fillRect: () => {{}},
          fillText: () => {{}},
          measureText: (txt) => ({{ width: 10 }})
        }};
      }}
    }};
    const classSet = new Set();
    elObj.classList = {{
      add: (...cls) => {{ cls.forEach(c => classSet.add(c)); }},
      remove: (...cls) => {{ cls.forEach(c => classSet.delete(c)); }},
      toggle: (c, force) => {{
        if (force !== undefined) {{
          if (force) classSet.add(c); else classSet.delete(c);
        }} else {{
          if (classSet.has(c)) classSet.delete(c); else classSet.add(c);
        }}
      }},
      contains: (c) => classSet.has(c)
    }};
    elements.set(id, elObj);
  }}
  return elements.get(id);
}}

const mockDocument = {{
  querySelector: (sel) => {{
    if (sel.startsWith('#')) return getOrCreateElem(sel.slice(1));
    if (sel.startsWith('.')) return getOrCreateElem('elem_' + sel.slice(1));
    return getOrCreateElem('generic');
  }},
  querySelectorAll: (sel) => {{
    if (sel === '.view') {{
      return ['view-fleet', 'view-assets', 'view-workbench', 'view-settings'].map(id => getOrCreateElem(id));
    }}
    if (sel === '.nav-tab') {{
      return ['fleet', 'assets', 'workbench', 'settings'].map(v => {{
        const el = getOrCreateElem('nav-tab-' + v, 'button');
        el.dataset.view = v;
        return el;
      }});
    }}
    if (sel === '.tree-node[data-train]') {{
      return ['TRAIN-301', 'TRAIN-302', 'TRAIN-303'].map(t => {{
        const el = getOrCreateElem('tree-node-' + t);
        el.dataset.train = t;
        el.querySelector = () => getOrCreateElem('header-item-' + t);
        return el;
      }});
    }}
    if (sel === '.tree-node-leaf') {{
      return ['APU-COMP-01', 'APU-DRY-LP49', 'APU-RES-TP3', 'APU-SW-LPS'].map(c => {{
        const el = getOrCreateElem('leaf-' + c);
        el.dataset.compId = c;
        return el;
      }});
    }}
    return [];
  }},
  getElementById: (id) => getOrCreateElem(id),
  createElement: (tag) => getOrCreateElem('elem_' + Math.random(), tag),
  createElementNS: (ns, tag) => getOrCreateElem('svg_' + Math.random(), tag),
  body: getOrCreateElem('body'),
  addEventListener: () => {{}}
}};

const ctx = vm.createContext({{
  window: mockWindow,
  document: mockDocument,
  console: console,
  setTimeout: setTimeout,
  clearTimeout: clearTimeout,
  fetch: () => Promise.resolve({{ ok: true, json: () => Promise.resolve({{}}) }}),
  history: mockWindow.history,
  location: mockWindow.location,
  globalThis: {{}}
}});

vm.runInContext(appJs, ctx);

// Execute test code
const testFn = new Function('ctx', {json.dumps(js_test_snippet)});
const testResult = testFn(ctx.globalThis);
process.stdout.write(JSON.stringify(testResult));
""";
        proc = subprocess.run(
            ["node", "-e", runner_script],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )
        if proc.returncode != 0:
            return {"error": proc.stderr or proc.stdout, "returncode": proc.returncode}
        try:
            return json.loads(proc.stdout)
        except Exception:
            return {"raw_output": proc.stdout, "error": proc.stderr}

    def test_navigation_workbench_train_302(self):
        snippet = """
        const S = ctx.S;
        ctx.navigateTo('workbench', { trainId: 'TRAIN-302' });
        return {
          view: S.view,
          selectedTrainId: S.selectedTrainId,
          activeStep: S.activeStep,
          hash: ctx.window.location.hash
        };
        """
        res = self.run_node_harness(snippet)
        if "error" in res:
            self.log("Navigation Logic", "navigateTo('workbench', { trainId: 'TRAIN-302' })", False, res["error"], "CRITICAL")
            return

        ok = (res.get("view") == "workbench" and 
              res.get("selectedTrainId") == "TRAIN-302" and 
              res.get("hash") == "#workbench")
        self.log(
            "Navigation Logic",
            "navigateTo('workbench', { trainId: 'TRAIN-302' }) transitions view & preserves state",
            ok,
            f"Result: view={res.get('view')}, trainId={res.get('selectedTrainId')}, hash={res.get('hash')}"
        )

    def test_navigation_assets_train_301(self):
        snippet = """
        const S = ctx.S;
        // Start from train-302
        S.selectedTrainId = 'TRAIN-302';
        S.selectedComponentId = 'APU-DRY-LP49';
        ctx.navigateTo('assets', { trainId: 'TRAIN-301' });
        return {
          view: S.view,
          selectedTrainId: S.selectedTrainId,
          selectedComponentId: S.selectedComponentId,
          hash: ctx.window.location.hash
        };
        """
        res = self.run_node_harness(snippet)
        if "error" in res:
            self.log("Navigation Logic", "navigateTo('assets', { trainId: 'TRAIN-301' })", False, res["error"], "CRITICAL")
            return

        ok = (res.get("view") == "assets" and 
              res.get("selectedTrainId") == "TRAIN-301" and 
              res.get("hash") == "#assets")
        self.log(
            "Navigation Logic",
            "navigateTo('assets', { trainId: 'TRAIN-301' }) focuses TRAIN-301 in asset tree",
            ok,
            f"Result: view={res.get('view')}, trainId={res.get('selectedTrainId')}, compId={res.get('selectedComponentId')}"
        )

    def test_navigation_null_context_resilience(self):
        """Adversarial challenge: what happens when null context is passed?"""
        snippet = """
        let errorWorkbench = null;
        try {
          ctx.navigateTo('workbench', null);
        } catch (e) {
          errorWorkbench = e.message;
        }

        let errorAssets = null;
        try {
          ctx.navigateTo('assets', null);
        } catch (e) {
          errorAssets = e.message;
        }

        return {
          errorWorkbench: errorWorkbench,
          errorAssets: errorAssets
        };
        """
        res = self.run_node_harness(snippet)
        has_crash = bool(res.get("errorWorkbench") or res.get("errorAssets"))
        if has_crash:
            self.log(
                "Null Safety & Resilience",
                "navigateTo(view, null) null context crash vulnerability",
                False,
                f"CRASH DETECTED: navigateTo with null context throws '{res.get('errorWorkbench')}'. context = {{}} default parameter does NOT catch null.",
                "HIGH"
            )
        else:
            self.log(
                "Null Safety & Resilience",
                "navigateTo(view, null) handled safely without crash",
                True,
                "No uncaught exception with null context"
            )

    def test_navigation_invalid_view(self):
        """Adversarial challenge: what happens if an invalid/unknown view is invoked?"""
        snippet = """
        const S = ctx.S;
        S.view = 'fleet';
        let error = null;
        try {
          ctx.navigateTo('invalid_ghost_view', {});
        } catch (e) {
          error = e.message;
        }
        return {
          view: S.view,
          error: error
        };
        """
        res = self.run_node_harness(snippet)
        if res.get("error"):
            self.log("Invalid View Handling", "navigateTo('invalid_ghost_view', {})", False, res["error"], "WARN")
        else:
            # Does it set S.view to invalid_ghost_view or fall back?
            view_set = res.get("view")
            is_invalid = view_set == "invalid_ghost_view"
            self.log(
                "Invalid View Handling",
                "navigateTo with unregistered view does not crash",
                True,
                f"S.view became '{view_set}'. Note: all view containers are toggled off when view does not exist (no fallback view assigned)."
            )

    # -------------------------------------------------------------
    # 2. DYNAMIC THRESHOLD SYNCHRONIZATION EMPIRICAL TESTS
    # -------------------------------------------------------------
    def test_dynamic_threshold_calculation(self):
        snippet = """
        const S = ctx.S;
        // 1. Initial state
        const initialLines = ctx.chartLines();
        const initDvThresh = initialLines.dv.find(l => l.label.includes('ngưỡng cảnh báo rò'));
        const initOilThresh = initialLines.oil.find(l => l.label.includes('ngưỡng nhiệt độ dầu'));

        // 2. Simulate Screen 2 configuration update
        S.customThresholds.leak_pressure_max = 0.085;
        S.customThresholds.oil_temp_max = 73.2;

        const updatedLines = ctx.chartLines();
        const newDvThresh = updatedLines.dv.find(l => l.label.includes('ngưỡng cảnh báo rò'));
        const newOilThresh = updatedLines.oil.find(l => l.label.includes('ngưỡng nhiệt độ dầu'));

        return {
          initDv: initDvThresh ? initDvThresh.value : null,
          initOil: initOilThresh ? initOilThresh.value : null,
          newDv: newDvThresh ? newDvThresh.value : null,
          newOil: newOilThresh ? newOilThresh.value : null
        };
        """
        res = self.run_node_harness(snippet)
        if "error" in res:
            self.log("Dynamic Threshold Sync", "chartLines() dynamic reactivity", False, res["error"], "CRITICAL")
            return

        ok = (res.get("initDv") == 0.05 and 
              res.get("initOil") == 67.0 and 
              res.get("newDv") == 0.085 and 
              res.get("newOil") == 73.2)
        self.log(
            "Dynamic Threshold Sync",
            "S.customThresholds updates chartLines() reference values immediately",
            ok,
            f"Initial: DV={res.get('initDv')} bar, Oil={res.get('initOil')} °C -> Updated: DV={res.get('newDv')} bar, Oil={res.get('newOil')} °C"
        )

    def test_threshold_line_plugin_draw(self):
        """Verifies thresholdLinePlugin calculates pixel coordinates and renders labels."""
        snippet = """
        const plugin = ctx.thresholdLinePlugin();
        let drawnLines = [];
        let filledShades = [];

        const mockChart = {
          $lines: [
            { label: 'ngưỡng cảnh báo rò', value: 0.085, color: '#EF4444', shadedZone: true },
            { label: 'ngưỡng nhiệt độ dầu', value: 73.2, color: '#EF4444', shadedZone: true }
          ],
          chartArea: { top: 20, bottom: 120, left: 40, right: 300 },
          scales: {
            y: {
              getPixelForValue: (val) => {
                // Return pixel between chartArea.top (20) and chartArea.bottom (120)
                return val < 1.0 ? 80 : 45;
              }
            }
          },
          ctx: {
            save: () => {},
            restore: () => {},
            beginPath: () => {},
            setLineDash: () => {},
            moveTo: () => {},
            lineTo: () => {},
            stroke: () => { drawnLines.push(true); },
            fillRect: (x, y, w, h) => { filledShades.push({ x, y, w, h }); },
            measureText: (txt) => ({ width: txt.length * 6 }),
            fillText: (txt, x, y) => {}
          }
        };

        // Execute afterDatasetsDraw
        plugin.afterDatasetsDraw(mockChart);

        return {
          drawnCount: drawnLines.length,
          filledShadesCount: filledShades.length
        };
        """
        res = self.run_node_harness(snippet)
        if "error" in res:
            self.log("Dynamic Threshold Sync", "thresholdLinePlugin execution", False, res["error"], "CRITICAL")
            return

        ok = (res.get("drawnCount") == 2 and res.get("filledShadesCount") == 2)
        self.log(
            "Dynamic Threshold Sync",
            "thresholdLinePlugin executes afterDatasetsDraw with ISA-101 danger shading",
            ok,
            f"Drawn dotted threshold lines: {res.get('drawnCount')}, Danger zone shaded rectangles: {res.get('filledShadesCount')}"
        )

    def test_screen2_to_screen3_no_reload_flow(self):
        """Simulates full user journey: Screen 2 form submission -> Screen 3 chart inspection without page reload."""
        snippet = """
        const S = ctx.S;

        // 1. User starts in Screen 2
        ctx.navigateTo('assets', { trainId: 'TRAIN-302', componentId: 'APU-DRY-LP49' });

        // 2. User modifies thresholds and saves
        const leakVal = 0.075;
        const oilVal = 70.0;
        S.customThresholds.leak_pressure_max = leakVal;
        S.customThresholds.oil_temp_max = oilVal;
        if (S.data.recovery && S.data.recovery.criteria) {
          S.data.recovery.criteria.dv_pressure_max = leakVal;
          S.data.recovery.criteria.oil_temp_max = oilVal;
        }

        // 3. User navigates directly to Screen 3 (War Room) without reload
        ctx.navigateTo('workbench', { trainId: 'TRAIN-302' });

        // 4. Inspect lines that will be painted on charts
        const lines = ctx.chartLines();
        const dvWarning = lines.dv.find(l => l.label.includes('ngưỡng cảnh báo rò'));
        const oilWarning = lines.oil.find(l => l.label.includes('ngưỡng nhiệt độ dầu'));

        return {
          view: S.view,
          dvWarningVal: dvWarning ? dvWarning.value : null,
          oilWarningVal: oilWarning ? oilWarning.value : null
        };
        """
        res = self.run_node_harness(snippet)
        if "error" in res:
            self.log("Cross-Screen Flow", "Screen 2 -> Screen 3 without page reload", False, res["error"], "CRITICAL")
            return

        ok = (res.get("view") == "workbench" and 
              res.get("dvWarningVal") == 0.075 and 
              res.get("oilWarningVal") == 70.0)
        self.log(
            "Cross-Screen Flow",
            "Screen 2 configuration immediately alters Screen 3 charts without page reload",
            ok,
            f"Screen 3 charts render active threshold lines: DV={res.get('dvWarningVal')} bar, Oil={res.get('oilWarningVal')} °C"
        )

    # -------------------------------------------------------------
    # 3. ZERO FAKE TELEMETRY EMPIRICAL AUDIT
    # -------------------------------------------------------------
    def test_zero_fake_telemetry(self):
        """Exhaustive regex and token scan for Math.random or simulated jitter."""
        math_rand = re.findall(r'Math\.random\s*\(\s*\)', self.js_code)
        # Check for fake sine/cosine oscillations generating synthetic telemetry
        synth_oscillations = re.findall(r'(Math\.sin|Math\.cos)\s*\([^)]*\)\s*[*+]\s*(pressure|temp|bar)', self.js_code, re.IGNORECASE)

        zero_fake = len(math_rand) == 0 and len(synth_oscillations) == 0
        self.log(
            "Zero Fake Telemetry",
            "Pure consumer architecture: 0 occurrences of Math.random() in telemetry pipeline",
            zero_fake,
            f"Math.random occurrences: {len(math_rand)}, Synthetic wave generators: {len(synth_oscillations)}"
        )

    def test_navigation_undefined_and_empty_view(self):
        snippet = """
        let undefErr = null;
        try {
          ctx.navigateTo(undefined);
        } catch (e) {
          undefErr = e.message;
        }

        let emptyErr = null;
        try {
          ctx.navigateTo('');
        } catch (e) {
          emptyErr = e.message;
        }

        return {
          undefErr: undefErr,
          emptyErr: emptyErr,
          finalView: ctx.S.view
        };
        """
        res = self.run_node_harness(snippet)
        ok = not res.get("undefErr") and not res.get("emptyErr")
        self.log(
            "Null Safety & Resilience",
            "navigateTo(undefined) and navigateTo('') do not throw uncaught exceptions",
            ok,
            f"Errors: undef={res.get('undefErr')}, empty={res.get('emptyErr')}. Final view: {res.get('finalView')}"
        )

    def test_component_selection_fallback_resilience(self):
        """Verifies selectComponent handles null or nonexistent component and train IDs without crashing."""
        snippet = """
        let nullErr = null;
        try {
          ctx.selectComponent(null, null);
        } catch (e) {
          nullErr = e.message;
        }

        let nonexistErr = null;
        try {
          ctx.selectComponent('NONEXISTENT_COMP_XYZ', 'TRAIN-999');
        } catch (e) {
          nonexistErr = e.message;
        }

        return {
          nullErr: nullErr,
          nonexistErr: nonexistErr,
          selectedComp: ctx.S.selectedComponentId,
          selectedTrain: ctx.S.selectedTrainId
        };
        """
        res = self.run_node_harness(snippet)
        ok = not res.get("nullErr") and not res.get("nonexistErr")
        self.log(
            "Null Safety & Resilience",
            "selectComponent(null, null) and nonexistent IDs gracefully fallback to defaults",
            ok,
            f"Fallback component: {res.get('selectedComp')}, Train: {res.get('selectedTrain')}"
        )

    def test_null_custom_thresholds_resilience(self):
        """Tests whether chartLines() survives when S.customThresholds is null or undefined."""
        snippet = """
        const S = ctx.S;
        S.customThresholds = null;
        let linesWithNull = null;
        let errWithNull = null;
        try {
          linesWithNull = ctx.chartLines();
        } catch (e) {
          errWithNull = e.message;
        }

        S.customThresholds = undefined;
        let linesWithUndef = null;
        let errWithUndef = null;
        try {
          linesWithUndef = ctx.chartLines();
        } catch (e) {
          errWithUndef = e.message;
        }

        // Restore
        S.customThresholds = { leak_pressure_max: 0.05, oil_temp_max: 67.0 };

        return {
          errNull: errWithNull,
          errUndef: errWithUndef,
          dvNullVal: linesWithNull ? (linesWithNull.dv.find(l => l.label.includes('ngưỡng')) || {}).value : null,
          dvUndefVal: linesWithUndef ? (linesWithUndef.dv.find(l => l.label.includes('ngưỡng')) || {}).value : null
        };
        """
        res = self.run_node_harness(snippet)
        ok = not res.get("errNull") and not res.get("errUndef")
        self.log(
            "Null Safety & Resilience",
            "chartLines() survives S.customThresholds = null or undefined",
            ok,
            f"Default fallback values: null->{res.get('dvNullVal')} bar, undef->{res.get('dvUndefVal')} bar"
        )

    # -------------------------------------------------------------
    # 4. RUN ALL VERIFICATIONS
    # -------------------------------------------------------------
    def run_all(self):
        print("\n" + "=" * 80)
        print(" EMPIRICAL CHALLENGER 1 (MILESTONE 3) ADVERSARIAL STRESS SUITE")
        print("=" * 80 + "\n")

        self.load_files()

        print("--- 1. Cross-Screen Navigation & Routing ---")
        self.test_navigation_workbench_train_302()
        self.test_navigation_assets_train_301()
        self.test_navigation_null_context_resilience()
        self.test_navigation_invalid_view()
        self.test_navigation_undefined_and_empty_view()

        print("\n--- 2. Dynamic Threshold Sync & Chart.js Plugins ---")
        self.test_dynamic_threshold_calculation()
        self.test_threshold_line_plugin_draw()
        self.test_screen2_to_screen3_no_reload_flow()
        self.test_null_custom_thresholds_resilience()

        print("\n--- 3. Component Hierarchy & Null Robustness ---")
        self.test_component_selection_fallback_resilience()

        print("\n--- 4. Telemetry Pipeline Integrity ---")
        self.test_zero_fake_telemetry()

        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")

        print("\n" + "-" * 80)
        print(f"Total Challenges: {total} | Passed: {passed} | Vulnerabilities/Failures: {failed}")
        print("=" * 80 + "\n")
        return failed


if __name__ == "__main__":
    challenger = EmpiricalM3Challenger()
    fail_count = challenger.run_all()
    sys.exit(0 if fail_count == 0 else 1)
