# TEST_INFRA.md — CompressorGuard Enterprise Test Infrastructure & Philosophy

> **Target Platform:** CompressorGuard — Industrial Operations Command Platform (MUGVN Hackathon 2026: MongoDB + Datadog)  
> **Workspace:** `d:\Code\Projects\self-projects\iot-hackathon`  
> **Target Persona:** Operator Hùng Bùi (`NV-0941`) — Central Operations OCC, Metro Line 1 (HURC1)

---

## 1. Test Philosophy & Dual Track Governance

### 1.1. ⚠️ CRITICAL INVARIANT: ZERO PYTEST ON FULL REPOSITORY
- **Strict Prohibition:** Under NO circumstances should `pytest` be executed against the entire repository root or without an explicit, targeted test path.
- **Root Rationale:**
  - The underlying physical dataset `dataset/MetroPT3(AirCompressor).csv` contains over 1,511,000 telemetry rows (~145 MB).
  - Running a blanket `pytest` discovers multiple legacy data-intensive benchmark suites that ingest and recompute rolling aggregations across the entire CSV, consuming 100% CPU and causing catastrophic background process hangs and timeouts.
- **Enforcement:**
  - All test suites created for the Enterprise UI/UX platform are **100% self-contained and independently executable**.
  - Tests can be launched directly via targeted Python runners (`python tests/<test_file>.py`) or specifically targeted pytest invocations (`pytest tests/<test_file>.py -v`).

### 1.2. Dual Track Testing Framework
Under the Dual Track architecture:
1. **Implementation Track (Feature Workers):** Constructs domain registry models, FastAPI routes, DOM markup, CSS stylesheets, and reactive state management.
2. **Quality & Verification Track (Test Writer):** Formulates opaque-box, contract-driven verification harnesses *in parallel*. Tests act as the canonical specification and gatekeeper.
3. **Escalation vs. Fixing:** The test writer writes and maintains test code only. Implementation defects discovered during test runs are documented with exact reproduction traces and escalated to the respective implementation workers.

### 1.3. Opaque-Box & Requirement-Driven Invariants
- **Zero Fake Telemetry:** Tests verify that telemetry and KPIs are driven by genuine physical models and state machines, not arbitrary `Math.random()`.
- **Identity Integrity:** Every audit log, operator card, and header status must reflect the authorized human-in-the-loop operator **Hùng Bùi (`NV-0941`)**, Shift 1 (06:00 – 14:00), OCC HURC1.
- **Natural Vietnamese Word Budgets (Rules 8 & 9):**
  - Titles / Panels / KPI labels / Buttons: $\le$ 3 words.
  - Microcopy / Notes / Hints: $\le$ 4 words (telegraphic, no trailing periods).
  - Toast notifications / Error messages: $\le$ 10 words (actionable single clause).
  - Immutable Technical Identifiers: Preserved verbatim without translation (`APU-COMP-01`, `TRAIN-302`, `DV_pressure`, `Oil_temp`, `LOADED`/`UNLOADED`, `[ LIVE SIMULATION · HISTORICAL DATA ]`).

---

## 2. Feature Inventory Mapping to Tiers 1–4

The 25 features identified in `PROJECT.md` are mapped into four distinct verification tiers:

| Tier | Scope & Focus | Features Covered | Test Strategy & Tools |
|---|---|---|---|
| **Tier 1: Core Domain & Static Synthesis** | Entity schemas, Registry hierarchy, Python compilation integrity | **F1** (Fleet Model), **F2** (Component Model), **F22** (Static Compilation) | `py_compile`, Type checking, Schema introspection |
| **Tier 2: Backend API & Dynamic Propagation** | REST endpoints, config mutation, dynamic threshold sync, audit event appending | **F3** (REST Endpoints), **F4** (Threshold & Audit Propagation), **F23** (Targeted HTTP API Tests) | FastAPI `TestClient`, targeted script `tests/test_enterprise_endpoints.py` |
| **Tier 3: Frontend DOM & Industrial Design** | 4 operational views, P1 Hero Banner, Synoptic Mimic, 35:65 Master-Detail, Word Budgets | **F5**–**F15** (Screen 1–4 DOM layouts, badges, cards, charts, stepper), **F24** (DOM & Word Budget Audit) | Headless DOM & AST audit script `tests/verify_enterprise_ui.py` |
| **Tier 4: State, Cross-Screen Sync & Live Simulation** | Context navigation (`navigateTo`), Chart.js sync, Stepper transitions, Simulation engine, Zero-Pytest audit | **F16**–**F21** (Navigation, CRUD, Sync, Stepper, SOP/Ledger, Sim Controls), **F25** (Zero-Pytest Integrity) | Automated DOM + JS state contract validation, runner verification |

---

## 3. Test Architecture & Runner Commands

### 3.1. Directory Structure
```
tests/
├── test_enterprise_endpoints.py  # Targeted Backend API & Dynamic Propagation Suite
├── verify_enterprise_ui.py       # Headless DOM, Word Budget & UI Interaction Suite
└── (existing legacy targeted tests...)
```

### 3.2. Targeted Runner Commands

#### 1. Static Compilation Verification (Tier 1)
```powershell
python -m py_compile src/domain/registry.py src/api/routes_product.py src/api/schemas.py
```
*Pass Criteria:* Return code `0` with zero syntax or import errors.

#### 2. Backend Enterprise Endpoints Verification (Tier 2)
```powershell
python tests/test_enterprise_endpoints.py
```
*Or via targeted pytest:*
```powershell
pytest tests/test_enterprise_endpoints.py -v
```
*Pass Criteria:*
- `GET /api/operations` returns 3 trains, 4 KPIs, P1 Hero Banner for TRAIN-302.
- `GET /api/components` lists APU subcomponents (`APU-COMP-01`, `APU-DRY-LP49`, `APU-RES-TP3`, `APU-SW-LPS`).
- `PUT /api/components/{id}` updates configuration and triggers dynamic threshold propagation into `GET /api/recovery`.
- `GET /api/case/events` records immutable audit ledger entry for operator Hùng Bùi (`NV-0941`).
- `GET /api/sop` returns industrial playbooks.
- `GET /api/shift/current` and `POST /api/shift/handover` function without state conflict.

#### 3. Frontend DOM, Word Budget & Interaction Flow Audit (Tier 3 & 4)
```powershell
python tests/verify_enterprise_ui.py
```
*Pass Criteria:*
- All 4 operational views (`#view-fleet`, `#view-assets`, `#view-workbench`, `#view-settings`) present in DOM.
- Screen 1 free of wave charts and $\sigma$ math; P1 Hero Banner and 3 Fleet Grid Cards present.
- Screen 2 contains Master-Detail 35%:65% layout and editable configuration form.
- Screen 3 contains War Room Header, Synoptic Flow Mimic, 4 stacked chart canvases (~110px), and 5-step stepper.
- Screen 4 contains Shift Operator Card for Hùng Bùi (`NV-0941`), Audit Ledger, SOP editor, and Simulation panel.
- 100% compliance with Vietnamese word budgets ($\le 3$ words for titles/buttons, $\le 4$ words for microcopy, $\le 10$ words for toasts).

---

## 4. Defect Escalation Protocol

If any test case fails:
1. **Determine Failure Classification:**
   - *Test harness defect:* Correct the test logic to align with normative specs (`PROJECT.md`, `rearchitect_enterprise_ui_ux_plan.md`).
   - *Implementation defect:* Immediately escalate to the implementing subagent or orchestrator. Do not alter implementation code from the test writer role.
2. **Escalation Payload Format:**
   - Exact endpoint / DOM element / script command.
   - Expected output derived from normative specification.
   - Actual output observed with stack trace or DOM diff.
   - Impacted Feature ID (F1–F25) and Tier (1–4).
