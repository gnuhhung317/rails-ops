# Fleet-Centric Case Architecture & Documentation Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Synchronize the entire documentation suite (Master Context, Product & UX Spec, Screen Specifications, Findings & Progress) with the newly finalized industrial product vision: elevating Fleet context as the business spine, establishing strict 3-tier data separation, framing live simulation over historical telemetry with dual clocks (`event_time` vs `simulation_time`), formalizing Case semantics and the `CaseEvent` ledger, and aligning the backend domain roadmap.

**Architecture:** The product structure evolves to `Fleet -> Train -> APU -> Compressor -> Current Condition -> Live Simulation -> Case -> Evidence -> Decision -> Action (ActionGuard) -> Recovery Verification -> Operational Impact`. Telemetry is cleanly decoupled from business asset hierarchy and validation ground truth. Live simulation preserves historical `event_time` for auditability while pacing with `simulation_time`.

**Tech Stack:** Markdown normative specifications, FastAPI REST DTOs, Pydantic, Python 3.12, Pytest, MongoDB Atlas, Datadog APM/DogStatsD.

---

### Task 1: Update Master Context (`master_context.md`)

**Files:**
- Modify: `d:/Code/Projects/self-projects/iot-hackathon/master_context.md`

- [ ] **Step 1: Update Section 1 (Executive Summary) & Section 4 (Product Thesis)**
  - Elevate Fleet Context: Incorporate industrial precedents (Siemens Senseye asset hierarchy, IBM Maximo asset risk/criticality, Alstom HealthHub fleet availability).
  - Define the 3 Data Layers:
    * Layer A: Business Context (Fleet, Train, APU, Compressor, Criticality, Service role, Location — Asset Registry).
    * Layer B: Observed / Computed Operational State (Sensor readings, regime, sigmas, anomaly scores).
    * Layer C: Validation / Historical Ground Truth (UCI Failure #3 Maintenance Report — Air leak / High stress).
  - Shift Terminology:
    * "Incident" $\rightarrow$ "Case" (unit of operational work).
    * "Onset" $\rightarrow$ "Confirmed degradation detected" at `2020-06-05 09:50:39 UTC` (detector confirmation, distinct from 10:00 failure report).
    * "Lead Time" $\rightarrow$ "Confirmed Intervention Window: 33h 52m" before reactive low-pressure milestone (`LPS = 1` at `2020-06-06 19:42:19 UTC`).
  - Redefine Live Simulation & Dual-Clock Architecture:
    * `event_time`: Original historical timestamp from MetroPT-3 dataset, used for all temporal reasoning, gap detection, lead time, and recovery verification. Never overwritten.
    * `simulation_time`: Wall-clock replay pacing (1x, 10x, 60x), pacing by $\Delta\text{event\_time}$ respecting variable sampling & gaps $>30$s.
    * Header badge: `[ LIVE SIMULATION · HISTORICAL DATA ] Scenario: Failure #3`.

- [ ] **Step 2: Update Section 5 (Backend Domain Architecture) & Section 7 (Roadmap)**
  - Update DecisionEngine logic:
    * Pressure + Thermal + Temporal $\rightarrow$ Confirmed Degradation $\rightarrow$ Create Case.
    * ML (Isolation Forest on LOADED baseline, 5 features: DV_pressure, H1, Oil_temp, Motor_current, TP3) $\rightarrow$ Independent Corroboration $\rightarrow$ Elevate decision confidence for mitigation. ML does NOT create cases on its own.
  - Detail `ActionGuard` policy:
    * Check 1: Case is confirmed.
    * Check 2: Mitigation recommended.
    * Check 3: No conflicting active case on asset.
    * Check 4: Simulation mode only.
    * Check 5: Replay branch available.
    * Action triggers: `SAFE MODE: SIMULATED INTERVENTION` branching to post-maintenance historical segment (`2020-06-08 16:05:00 UTC`).
  - Detail `RecoveryVerifier` truthfulness:
    * Criteria verified: 5/5 healthy LOADED observations ($\text{DV} < 0.05$ bar, $\text{Oil} < 67^\circ\text{C}$). Telemetry satisfies criteria; does not claim physical rail certification.
  - Detail `CaseEvent` ledger object (append-only audit log):
    * `timestamp`, `event_type` (`OBSERVATION`, `CORROBORATION`, `DECISION`, `ACTION`, `BENCHMARK_LPS`, `RECOVERY`, `CASE_CLOSED`), `title`, `detail`, `actor`, `source`, `case_phase`.
  - Detail API Contract additions:
    * `GET /api/operations`: Fleet, Train, APU, Compressor, health, regime, active_case, operational_impact.
    * `GET /api/case/events`: Timeline event ledger.
    * `POST /api/case/close`: Only allowed when `recovery_verified == True`.
  - Freeze updated roadmap priorities:
    * P0: Product Truth (Excursion replay, temporal semantics, ML corroboration, dynamic 33h52, evidence provenance, case event ledger, historical replay labeled).
    * P1: Product Completeness (Asset hierarchy, Operations API, ActionGuard, Case close, MongoDB, Datadog, Validation reference drawer).
    * P2: Presentation & Pitch.

- [ ] **Step 3: Verify markdown formatting and links**
  Run: Check document rendering and markdown linting.
  Expected: Clean markdown syntax without broken references.

- [ ] **Step 4: Commit**
  ```bash
  git add master_context.md
  git commit -m "docs: align master_context with fleet-centric case architecture and dual-clock simulation"
  ```

---

### Task 2: Update Product & UX Specification (`docs/PRODUCT_UX_SPEC.md`)

**Files:**
- Modify: `d:/Code/Projects/self-projects/iot-hackathon/docs/PRODUCT_UX_SPEC.md`

- [ ] **Step 1: Rewrite Product Thesis & Cognitive Flow**
  - Update Section 1:
    * Category: Operations Command Console for Critical Rail Assets.
    * 3 Killer Claims: Confirmed Intervention Window (33h 52m), Multi-Signal Evidence with Provenance, Closed-Loop Recovery Verification.
    * Strict Separation of 3 Data Layers: Business Context vs Observed Telemetry vs Ground Truth Validation.
  - Update Section 2 (5 Judge Questions):
    * 1. WHO AM I? Operations Specialist monitoring Metro Fleet $\rightarrow$ Train #302 $\rightarrow$ APU-COMP-01.
    * 2. WHAT CHANGED? Confirmed degradation detected at 09:50:39 UTC; 33h 52m confirmed intervention window before reactive LPS.
    * 3. WHY TRUST? 4 Co-located Evidence Cards with explicit source provenance + Isolation Forest independent corroboration (5 features).
    * 4. WHAT CAN I DO? ActionGuard-verified Safe Mode simulated intervention branching to post-maintenance stream.
    * 5. DID IT WORK? Telemetry satisfies recovery criteria (5/5 healthy LOADED observations); Case sign-off.
  - Update Section 3 (Information Hierarchy):
    * Tier 1: Operations scope, asset condition, 33h 52m intervention window, Live Simulation badge (`[ LIVE SIMULATION · HISTORICAL DATA ]`).
    * Tier 2: 4 Evidence cards with source & method provenance, ActionGuard status, Recovery tracker.
    * Tier 3: Validation Reference Drawer (Historical Failure #3 report vs Online decision facts).
    * Tier 4: Background telemetry stream & simulation engine logs.

- [ ] **Step 2: Update API Contract & Schemas in UX Spec**
  - Add `/api/operations` schema specification.
  - Update `/api/incident` (or `/api/case`) with asset hierarchy context (`fleet_name`, `train_id`, `subsystem`, `criticality`).
  - Update `/api/evidence` schema with provenance fields (`source_detector`, `detection_method`, `event_timestamp`, `regime`).
  - Add `/api/case/events` schema specification.
  - Add `/api/case/close` schema specification.

- [ ] **Step 3: Commit**
  ```bash
  git add docs/PRODUCT_UX_SPEC.md
  git commit -m "docs: update PRODUCT_UX_SPEC with fleet operations landing, evidence provenance, and validation reference"
  ```

---

### Task 3: Update Screen Specifications (`screen/*.md`)

**Files:**
- Modify: `d:/Code/Projects/self-projects/iot-hackathon/screen/README.md`
- Modify: `d:/Code/Projects/self-projects/iot-hackathon/screen/01_OPERATIONS_NAV_AND_ASSET_OVERVIEW.md`
- Modify: `d:/Code/Projects/self-projects/iot-hackathon/screen/02_ACTIVE_CASES_LIST.md`
- Modify: `d:/Code/Projects/self-projects/iot-hackathon/screen/03_CASE_WORKSPACE_WHAT_CHANGED.md`
- Modify: `d:/Code/Projects/self-projects/iot-hackathon/screen/04_CASE_WORKSPACE_WHY_EVIDENCE.md`
- Modify: `d:/Code/Projects/self-projects/iot-hackathon/screen/05_CASE_WORKSPACE_WHAT_DID_WE_DO.md`
- Modify: `d:/Code/Projects/self-projects/iot-hackathon/screen/06_CASE_WORKSPACE_DID_IT_WORK.md`
- Modify: `d:/Code/Projects/self-projects/iot-hackathon/screen/07_CASE_TIMELINE_HISTORY.md`

- [ ] **Step 1: Update `screen/README.md`**
  - Update top-level IA diagram to show:
    `OPERATIONS -> FLEET/ASSET HIERARCHY -> ACTIVE CASES -> CASE WORKSPACE (What Changed -> Why/Evidence -> What Did We Do -> Did It Work -> Timeline) + VALIDATION REFERENCE DRAWER`.
  - State clearly that Screen 01 is preserved and elevated as the Operations Landing Page.

- [ ] **Step 2: Update `screen/01_OPERATIONS_NAV_AND_ASSET_OVERVIEW.md`**
  - Replace fake KPI `[FLEET HEALTH: 98%]` with truthful operational counters:
    * Normal: `1 MONITORED ASSET | 0 ACTIVE CASES | 1 ASSET OBSERVING | REPLAY: FAILURE #3`.
    * When confirmed: `1 MONITORED ASSET | 1 ACTIVE CASE | 1 TRAIN AT RISK | 33h 52m CONFIRMED LEAD TIME`.
  - Replace `[🔴 LIVE]` badge with `[ LIVE SIMULATION · HISTORICAL DATA ] Scenario: Failure #3`.
  - Add Fleet Hierarchy tree wireframe:
    `OPERATIONS -> FLEET (Metro Fleet) -> TRAIN-302 -> APU -> APU-COMP-01`.
  - Preserve the 00:33:07 transient excursion observing demo (noise suppression).

- [ ] **Step 3: Update `screen/02_ACTIVE_CASES_LIST.md`**
  - Replace `[FLEET HEALTH: 74%]` with `[ 1 MONITORED ASSET | 1 ACTIVE CASE | 1 TRAIN AT RISK | 33h 52m INTERVENTION WINDOW ]`.
  - Replace `[🔴 LIVE]` badge with `[ LIVE SIMULATION · HISTORICAL DATA ]`.
  - Link Case to Asset Hierarchy (`Metro Fleet / Train #302 / APU-COMP-01`).
  - Reinforce Single Active Case invariant.

- [ ] **Step 4: Update `screen/03_CASE_WORKSPACE_WHAT_CHANGED.md`**
  - Restructure into 4 Distinct Tiers:
    * Block 1 — Observed: `DV_pressure = 2.1856 bar (+23.75σ)`, `Oil_temp = 74.97°C (+5.71σ)`.
    * Block 2 — Operational Condition: Asset Health: CRITICAL, Operating Regime: LOADED, Degradation: CONFIRMED.
    * Block 3 — Business Context: Service Unit: TRAIN-302, Subsystem: APU / Pneumatic, Operational Risk: Potential service disruption, Confirmed intervention window: 33h 52m.
    * Block 4 — Validation Reference: Historical Failure Reference: Failure #3 — Air Leak / High stress.
  - Terminology adjustment: Change `Onset Timestamp` to `Confirmed degradation detected: 2020-06-05 09:50:39 UTC`.

- [ ] **Step 5: Update `screen/04_CASE_WORKSPACE_WHY_EVIDENCE.md`**
  - Add Provenance footer to each evidence card:
    * `SOURCE`: Detector class (e.g., `PressureAnomalyDetector`, `ThermalDriftDetector`).
    * `METHOD`: Loaded-regime baseline evaluation.
    * `TIMESTAMP`: `2020-06-05 09:50:39 UTC`.
    * `REGIME`: `LOADED`.
  - Correct ML Card:
    * Multivariate Corroboration (Isolation Forest).
    * Features: 5 telemetry features (`DV_pressure`, `H1`, `Oil_temp`, `Motor_current`, `TP3`). Remove mention of "15 cảm biến".
    * Threshold: 0.350, Score: 0.382.
    * Explicit Role: Independent corroboration (does not create case on its own; increases decision confidence for mitigation).

- [ ] **Step 6: Update `screen/05_CASE_WORKSPACE_WHAT_DID_WE_DO.md`**
  - Replace fake physical sensors (track gradient, gradient < 1.0%, mechanical actuator) with truthful `ActionGuard`:
    * [ ✓ ] Case is confirmed.
    * [ ✓ ] Mitigation recommended by DecisionEngine.
    * [ ✓ ] No conflicting active case on asset.
    * [ ✓ ] Simulation mode only.
    * [ ✓ ] Replay branch available.
  - Update action execution text:
    `SAFE MODE: SIMULATED INTERVENTION` $\rightarrow$ Branches to `POST-MAINTENANCE HISTORICAL SEGMENT` (`2020-06-08 16:05:00 UTC`).

- [ ] **Step 7: Update `screen/06_CASE_WORKSPACE_DID_IT_WORK.md`**
  - Update title and verification wording:
    `RECOVERY CRITERIA VERIFIED (5/5 healthy LOADED observations)`.
  - Clarify: Telemetry satisfies recovery criteria; do not claim physical certification of the physical train valve.
  - Add `[ 🔒 CLOSE CASE & RELEASE ASSET ]` action calling `POST /api/case/close`.

- [ ] **Step 8: Update `screen/07_CASE_TIMELINE_HISTORY.md`**
  - Transform into formal `CaseEvent` ledger specification:
    * `OBSERVATION`: Confirmed degradation detected (source: pressure detector).
    * `CORROBORATION`: Isolation Forest corroborated (source: ML).
    * `DECISION`: Mitigation recommended (source: DecisionEngine).
    * `ACTION`: Safe Mode simulated intervention (actor: operator).
    * `BENCHMARK`: Reactive LPS observed at 2020-06-06 19:42:19 UTC (lead time 33h 52m confirmed).
    * `RECOVERY`: Recovery criteria verified (5/5 healthy loaded observations).
    * `CASE_CLOSED`: Operator sign-off and asset released.

- [ ] **Step 9: Commit**
  ```bash
  git add screen/*.md
  git commit -m "docs: align screen specs 01-07 with fleet hierarchy, action guard, evidence provenance, and case event ledger"
  ```

---

### Task 4: Update Findings & Progress Ledgers (`findings.md`, `progress.md`)

**Files:**
- Modify: `d:/Code/Projects/self-projects/iot-hackathon/findings.md`
- Modify: `d:/Code/Projects/self-projects/iot-hackathon/progress.md`

- [ ] **Step 1: Update `findings.md`**
  - Document the 3 Data Layers separation principle.
  - Document Industrial Precedents (Siemens Senseye, IBM Maximo, Alstom HealthHub, Datadog Incidents).
  - Document the Dual-Clock Live Simulation architecture (`event_time` vs `simulation_time`, $\Delta\text{event\_time}$ pacing).
  - Document the specific role of ML as Independent Corroboration vs Physics-first detection.

- [ ] **Step 2: Update `progress.md`**
  - Log the review decisions and complete documentation synchronization.

- [ ] **Step 3: Commit**
  ```bash
  git add findings.md progress.md
  git commit -m "docs: update findings and progress ledger with fleet-centric case model and dual-clock simulation"
  ```

---

### Task 5: Plan Backend Domain & API Alignment (Subsequent Implementation Tasks)

**Files:**
- To modify in next implementation phase:
  * `src/domain/models.py` (Add `AssetRegistry`, `AssetHierarchy`, `CaseEvent`, `Provenance`)
  * `src/engine/decision.py` (Tune decision rules: ML elevates confidence, does not create case)
  * `src/engine/lifecycle.py` (Support ActionGuard checks, CaseEvent appending, case close)
  * `src/engine/replay.py` (Abstract `ScenarioStream`, dual-clock pacing logic)
  * `src/api/routes_product.py` (Add `/api/operations`, `/api/case/events`, `/api/case/close`)
  * `src/api/schemas.py` (DTOs for Operations, CaseEvent, Close)
  * `tests/` (Unit & integration test suites for new contracts)

- [ ] **Step 1: Map out exact test cases and signatures for backend alignment**
  - `test_operations_endpoint.py`: Verify `/api/operations` returns asset hierarchy + condition.
  - `test_case_events_endpoint.py`: Verify `/api/case/events` returns append-only timeline ledger.
  - `test_action_guard.py`: Verify ActionGuard rejects illegal actions.
  - `test_case_close.py`: Verify `/api/case/close` only succeeds after `recovery_verified == True`.
  - `test_ml_corroboration_role.py`: Verify DecisionEngine creates case from physics+temporal, and uses ML only to elevate confidence.

---
