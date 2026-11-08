# TEST_READY.md — CompressorGuard Enterprise Verification Suite

> **Target Project:** CompressorGuard — Industrial Operations Command Platform (MUGVN Hackathon 2026)  
> **Workspace:** `d:\Code\Projects\self-projects\iot-hackathon`  
> **Target Persona:** Operator Hùng Bùi (`NV-0941`) — OCC HURC1, Metro Line 1  
> **Published At:** 2026-11-08T00:08:00Z  
> **Author:** E2E Test Writer (`teamwork_test_writer_e2e`)

---

## 1. Executive Summary & Verification Philosophy

The CompressorGuard Enterprise test harness is established under the **Dual Track Engineering Principle**:
- **Implementation Track:** Feature workers build Domain models (M1), DOM layouts & CSS (M2), and Client State & Sync (M3).
- **Verification Track:** The test writer formulates strict, requirement-driven, opaque-box test suites that act as both specification gates and automated acceptance criteria.

### ⚠️ Critical Invariant: Zero Pytest on Full Repo
- Blanket invocations of `pytest` against the entire repository are **strictly prohibited**.
- The full physical dataset `dataset/MetroPT3(AirCompressor).csv` has >1,516,000 rows (~145MB), which causes multi-minute dataset loading and background process hangs if discovered en masse.
- All enterprise tests are **isolated, self-contained, and run in <20 seconds** via targeted Python or targeted pytest commands.

---

## 2. Test Inventory & Coverage Across Tiers 1–4

| Tier | Scope | Target Features | Primary Verification Tool | Test File / Command |
|---|---|---|---|---|
| **Tier 1: Core Domain & Static Verification** | Python AST, syntax, type validation, schema imports | **F1**, **F2**, **F22** | Python Bytecode Compiler | `python -m py_compile src/domain/registry.py src/api/routes_product.py src/api/schemas.py` |
| **Tier 2: Backend REST APIs & Dynamic Propagation** | Operations overview, 3 fleet trains, 4 KPIs, P1 Hero Banner, APU Component CRUD, Dynamic threshold propagation to recovery verifier, and Audit ledger for Hùng Bùi (NV-0941) | **F3**, **F4**, **F23** | FastAPI TestClient Runner | `python tests/test_enterprise_endpoints.py`<br>`pytest tests/test_enterprise_endpoints.py -v` |
| **Tier 3: Frontend DOM & Industrial Slate Design** | 4 operational views, P1 Warning Hero Banner, 3 Fleet Grid Cards, Cognitive declutter (no raw waves/sigmas in Screen 1), Master-Detail 35:65 layout, Synoptic Flow Mimic, 4 stacked charts, 5-step stepper, Shift Card for Hùng Bùi (NV-0941), Simulation controls | **F5**–**F15**, **F24** | Headless DOM & AST Auditor (BeautifulSoup) | `python tests/verify_enterprise_ui.py` |
| **Tier 4: State, Cross-Screen Sync & Live Simulation** | Context navigation (`navigateTo`), Dynamic threshold sync, Shift handover, Zero fake telemetry (`Math.random()`), and Industrial Vietnamese Word Budgets ($\le 3$ words for titles/buttons, $\le 4$ words for notes, $\le 10$ words for toasts) | **F16**–**F21**, **F25** | Static JS AST & DOM Verifier | `python tests/verify_enterprise_ui.py` |

---

## 3. Targeted Runner Commands & Verification Procedures

### 3.1. Tier 1: Static Compilation Verification
Run syntax validation across modified backend files:
```powershell
cd 'd:\Code\Projects\self-projects\iot-hackathon'
python -m py_compile src/domain/registry.py src/api/routes_product.py src/api/schemas.py
```
*Expected Result:* Return code `0` with zero output (clean compilation).

---

### 3.2. Tier 2: Enterprise API & Dynamic Propagation Suite
Run the targeted backend endpoint test suite:
```powershell
cd 'd:\Code\Projects\self-projects\iot-hackathon'
python tests/test_enterprise_endpoints.py
```
*Alternative via targeted pytest:*
```powershell
cd 'd:\Code\Projects\self-projects\iot-hackathon'
pytest tests/test_enterprise_endpoints.py -v
```

#### Test Suite Breakdown (8 Tests):
1. `test_operations_overview_hierarchy_and_backward_compatibility`: Preserves existing `fleet`, `train`, `subsystem`, `asset`, `operations_summary`.
2. `test_operations_fleet_grid_trains`: Validates `trains` array contains `TRAIN-301`, `TRAIN-302` (Warning P1), and `TRAIN-303`.
3. `test_operations_kpis_and_p1_hero_banner`: Validates 4 KPIs (3/3, 2 normal, 1 alert, Long Bình) and Hero Banner for TRAIN-302 (33h 52m buffer).
4. `test_components_catalog_endpoint`: Validates `GET /api/components` lists 4 APU components (`APU-COMP-01`, `APU-DRY-LP49`, `APU-RES-TP3`, `APU-SW-LPS`).
5. `test_single_component_detail_and_404`: Validates `GET /api/components/{id}` and 404 for unknown IDs.
6. `test_component_config_update_and_dynamic_propagation`: Validates `PUT /api/components/APU-DRY-LP49` updates thresholds, dynamically propagates to `GET /api/recovery`, and appends an audit record under Hùng Bùi (`NV-0941`).
7. `test_sop_playbooks_endpoint`: Validates `GET /api/sop` returns standard operating procedures.
8. `test_shift_management_endpoints`: Validates `GET /api/shift/current` returns Hùng Bùi (`NV-0941`), and `POST /api/shift/handover` records handover.

---

### 3.3. Tiers 3 & 4: Headless DOM, Word Budget & Interaction Flow Audit
Run the automated DOM auditor:
```powershell
cd 'd:\Code\Projects\self-projects\iot-hackathon'
python tests/verify_enterprise_ui.py
```

#### Verification Breakdown (26 Checks):
- **Navigation & Layout (6 checks):** 4 view containers (`#view-fleet`, `#view-assets`, `#view-workbench`, `#view-settings`), 4 navigation tabs.
- **Screen 1 Overview (5 checks):** P1 Hero Banner for TRAIN-302, 33h 52m buffer, War Room button, 4 KPIs, 3 Fleet Grid Cards, Cognitive declutter (0 wave charts and 0 sigma widgets in Screen 1).
- **Screen 2 Asset Management (3 checks):** Master-Detail 35:65 layout, Asset Tree hierarchy, Config form with 6 inputs and save button.
- **Screen 3 Incident War Room (4 checks):** War Room Header (+2.19 bar margin, 33h 52m, Layer C button), Synoptic Flow Mimic, 4 stacked chart canvases (~110px each), 5-step stepper.
- **Screen 4 Settings & Shift (4 checks):** Shift Operator Card for Hùng Bùi (`NV-0941`), Audit Ledger table, SOP Playbooks panel, Centralized simulation controls.
- **Word Budgets & Persona (3 checks):** Button word budgets ($\le 3$ words), Operator persona Hùng Bùi (`NV-0941`), Technical identifiers preservation.
- **State & Navigation Script (4 checks):** Navigation routing with context (`navigateTo`), Dynamic threshold sync, Operator binding, Zero fake telemetry (`Math.random()`).

---

## 4. Baseline Pre-Implementation Benchmark Results

Execution results recorded prior to Milestone 1, 2, and 3 implementation:

### 4.1. Tier 2 Endpoint Run Baseline
```
==============================================================================
 COMPRESSORGUARD ENTERPRISE ENDPOINT TEST RUNNER (TIER 2)
==============================================================================
  [PASS] Operations Hierarchy & Backward Compatibility
  [FAIL] Operations Fleet Grid Trains (301, 302, 303): Missing 'trains' list in /api/operations
  [FAIL] Operations KPIs & P1 Hero Banner: Missing 'kpis' in /api/operations
  [FAIL] APU Components Catalog: GET /api/components returned 404
  [FAIL] Single Component Detail & 404 Handling: Expected 200 for APU-DRY-LP49, got 404
  [FAIL] Component Config Update & Dynamic Propagation: PUT /api/components/APU-DRY-LP49 failed with 404
  [FAIL] SOP Playbooks Catalog: GET /api/sop failed with 404
  [FAIL] Shift Management for Hùng Bùi (NV-0941): GET /api/shift/current failed with 404
------------------------------------------------------------------------------
Total Tests: 8 | Passed: 1 | Failed: 7
==============================================================================
```

### 4.2. Tiers 3 & 4 DOM & Word Budget Run Baseline
```
==============================================================================
 COMPRESSORGUARD ENTERPRISE UI/UX ACCEPTANCE AUDIT (TIERS 3 & 4)
==============================================================================
--- Tier 3 ---
  [PASS] Navigation & Layout :: View container #view-fleet present in DOM
  [FAIL] Navigation & Layout :: View container #view-assets present in DOM
  [PASS] Navigation & Layout :: View container #view-workbench present in DOM
  [FAIL] Navigation & Layout :: View container #view-settings present in DOM
  [PASS] Navigation & Layout :: Nav tab for 'fleet' present
  [FAIL] Navigation & Layout :: Nav tab for 'assets' present
  [PASS] Navigation & Layout :: Nav tab for 'workbench' present
  [FAIL] Navigation & Layout :: Nav tab for 'settings' present
  [FAIL] Screen 1 Overview :: P1 Hero Banner element present
  [FAIL] Screen 1 Overview :: 4 Operational KPIs present (3/3, 2 normal, 1 alert, Long Bình)
  [FAIL] Screen 1 Overview :: Fleet Cards Grid present
  [FAIL] Screen 1 Overview :: Cognitive Declutter: NO raw wave charts inside Screen 1
  [FAIL] Screen 1 Overview :: Cognitive Declutter: NO math sigma/isolation forest widgets in Screen 1
  [FAIL] Screen 2 Assets :: Screen 2 container
  [FAIL] Screen 3 War Room :: War Room Header present
  [FAIL] Screen 3 War Room :: Synoptic Flow Mimic #apu-schematic present in Screen 3
  [FAIL] Screen 3 War Room :: 4 Stacked multi-channel chart canvases present in Screen 3
  [PASS] Screen 3 War Room :: 5-Step Operational Stepper layout present
  [FAIL] Screen 4 Settings :: Screen 4 container

--- Tier 4 ---
  [FAIL] Word Budgets :: Button labels conform to <= 3 words budget
  [FAIL] Operator Persona :: Operator identity Hùng Bùi (NV-0941) present in UI
  [PASS] Word Budgets :: Technical identifiers preserved verbatim without translation
  [PASS] State & Navigation :: Navigation routing logic with context support exists
  [FAIL] State & Navigation :: Dynamic threshold update & cross-screen sync logic in app.js
  [FAIL] State & Navigation :: Operator Hùng Bùi (NV-0941) bound to client state & actions
  [PASS] State & Navigation :: Zero Fake Telemetry: No Math.random() in telemetry pipeline
------------------------------------------------------------------------------
Total Verifications: 26 | Passed: 8 | Failed: 18
==============================================================================
```

---

## 5. Implementation Roadmap & Quality Gates

The test harness provides immediate, unambiguous feedback for each implementation milestone:
- **Milestone 1 Gate:** All 8 tests in `tests/test_enterprise_endpoints.py` must pass (`8/8 PASS`).
- **Milestone 2 Gate:** All Tier 3 checks in `tests/verify_enterprise_ui.py` must pass (`19/19 PASS`).
- **Milestone 3 Gate:** All Tier 4 checks in `tests/verify_enterprise_ui.py` must pass (`7/7 PASS`).
- **Final Acceptance (M4):** Combined 34/34 checks passing with 0 errors and zero full-repo pytest calls.
