# COMPRESSORGUARD — MASTER CONTEXT & PRODUCT DOSSIER
## The Canonical Single Source of Truth (SSOT) for MUGVN Hackathon 2026 & Future LLM Agents

> **Document Type:** Master System Dossier, Architecture Catalog & Agent Context  
> **Target Audience:** Any AI/LLM Agent, System Architect, or Hackathon Judge taking over CompressorGuard  
> **Status:** Production-Ready & Formally Verified (98/98 Pytest Passed)  
> **Core Value Proposition:** **Detect earlier → Prove why → Act safely → Verify recovery → Quantify value.**  
> **Mandatory Rule for LLMs:** Do NOT restart from generic hackathon or anomaly detection advice. Adhere strictly to the facts, contracts, and ADRs defined in this dossier.

---

## TABLE OF CONTENTS

1. [0. System Identity & Profile](#0-system-identity--profile)
2. [1. Executive Thesis & The Fundamental Difference](#1-executive-thesis--the-fundamental-difference)
3. [2. Ground Truth Dataset & Physical Asset (MetroPT-3)](#2-ground-truth-dataset--physical-asset-metropt-3)
4. [3. The Golden Path (Failure #3) — Exact Facts & Frozen Milestones](#3-the-golden-path-failure-3--exact-facts--frozen-milestones)
5. [4. Architectural Pillars & Semantic Contracts](#4-architectural-pillars--semantic-contracts)
6. [5. Comprehensive Architectural Decision Records (ADRs)](#5-comprehensive-architectural-decision-records-adrs)
7. [6. Mandatory Technology Blueprint: MongoDB Atlas & Datadog](#6-mandatory-technology-blueprint-mongodb-atlas--datadog)
8. [7. Public REST API Contracts & Schemas](#7-public-rest-api-contracts--schemas)
9. [8. Complete Codebase Repository Map](#8-complete-codebase-repository-map)
10. [9. Rail Economics & Operational Value Model](#9-rail-economics--operational-value-model)
11. [10. Demo Strategy, 5 Judging Gates & Attack Scenarios](#10-demo-strategy-5-judging-gates--attack-scenarios)
12. [11. Known Pitfalls, Fixed Bugs & System Invariants](#11-known-pitfalls-fixed-bugs--system-invariants)
13. [12. Strict Rules of Engagement for the Next AI](#12-rules-of-engagement-for-the-next-ai)

---

# 0. SYSTEM IDENTITY & PROFILE

- **Product Name:** **CompressorGuard**
- **Product Category:** Evidence-Driven Closed-Loop Operational Case Platform for Physical Fleet Assets.
- **Hackathon:** **MUGVN Hackathon 2026** (Track: IoT / Real-Time Operations).
- **Mandatory Partner Technologies:**
  - **MongoDB Atlas:** Time Series telemetry store (`measurements`), `$setWindowFields` rolling window aggregations, operational case ledger (`operational_cases`), and event chronology (`case_events`).
  - **Datadog:** Unified Observability Control Plane (DogStatsD custom metrics, APM distributed tracing with FastAPI spans, structured JSON logging with `dd.trace_id`, Monitors, and Operations Dashboard).
- **Monitored Physical Asset:** **Air Production Unit (APU)** Compressor (`APU-COMP-01`) on Lisbon Metro Trainset #302 (Linha Azul).
- **Current Engineering Status:** **Phase 6 Complete — 98/98 unit and regression tests passing.** Clean FastAPI backend + Zero-Build High-Performance Modern SPA Web Console.

---

# 1. EXECUTIVE THESIS & THE FUNDAMENTAL DIFFERENCE

## 1.1 The Core Problem in Physical Asset Operations
In urban rail operations, an APU failure is not an abstract telemetry spike; it is a **service-halting emergency**. If the compressor's discharge valve fails, pneumatic pressure drops, failsafe friction brakes clamp down, doors fail to open, and the train becomes dead on the tracks (*"train had to be removed from revenue tracks"*), stranding thousands of passengers and paralyzing the entire subway line.

Traditional monitoring operates on **reactive mechanical relays** (e.g., Low Pressure Switch `LPS = 1`), which only trip when the air pressure has already collapsed below 7.0 bar. At that point, catastrophic disruption has already occurred.

## 1.2 The Fundamental Difference: Operations System vs. ML Toy
Most hackathon projects build a generic pipeline:
$$\text{Sensors} \longrightarrow \text{ML Model} \longrightarrow \text{Anomaly Score} \longrightarrow \text{Dashboard Chart}$$
This fails in physical industry because:
1. **Uninterpretable:** Operators will not remove a train from revenue service based on an opaque "anomaly probability = 0.87".
2. **Trigger-Happy:** Single threshold spikes or transient startups create alert fatigue ("crying wolf").
3. **Open-Loop:** They stop at alerting and never execute safe intervention or verify asset recovery.

**CompressorGuard replaces this with an evidence-driven closed-loop operational hierarchy:**
$$\text{Telemetry} \longrightarrow \text{Operating Context} \longrightarrow \text{Observation} \longrightarrow \text{Evidence} \longrightarrow \text{Decision} \longrightarrow \text{Action} \longrightarrow \text{Verification} \longrightarrow \text{Business Impact}$$

| Dimension | Generic Anomaly Project | CompressorGuard |
|---|---|---|
| **Core Claim** | "AI predicts failures." (Overclaim) | "Detects confirmed degradation earlier, proves why, acts safely, and verifies recovery." |
| **First Anomaly** | Fires alert immediately (Cry wolf). | Classifies as Early Weak Excursion; accumulates multi-sensor evidence without alarming. |
| **ML Role** | Autonomous alert creator (Black box). | Independent multivariate corroboration to raise decision confidence. |
| **Action** | None / Generic Jira ticket. | Policy-guarded simulated Safe Mode intervention (`ActionGuard`). |
| **Closure** | Operator marks "resolved" manually. | Verifies 5/5 consecutive healthy physical cycles on post-maintenance telemetry. |
| **Value** | Fake claimed savings ("We saved $10M"). | Distinct triad: **Observed** (33h 52m) vs **Modeled** (Scenario cost) vs **Verified** (5/5 recovery). |

---

# 2. GROUND TRUTH DATASET & PHYSICAL ASSET (METROPT-3)

- **Dataset Provenance:** Nature Scientific Data (2022) / UCI Machine Learning Repository.
- **Physical Equipment:** Knorr-Bremse style rotary compressor powering the Lisbon Metro APU.
- **Data Volume:** **1,516,948 samples @ 1 Hz**, spanning February to August 2020.
- **Temporal Nature:** Historical recorded telemetry with a median interval of ~10s and **~331 temporal gaps > 30s**.
- **Regimes of Operation:**
  - `OFF`: Motor stopped, no pressure generated.
  - `STARTING`: Inrush current, rapid pressure ramp-up.
  - `OFF_LOAD`: Compressor idling, bypass valve open.
  - `LOADED`: Active pumping against train reservoir; high load, active thermal generation.
  - `TRANSIENT`: Transition states between loading and unloading.
- **The 4 Dataset Scenarios:**
  - **Failure #3 (Golden Path):** Severe air leak and thermal stress (June 4 – June 8, 2020). Primary demo target.
  - **Failure #1 (Generalization Validation):** Air leak failure (March 2020).
  - **Failure #4 (Generalization Validation):** Oil leak failure (July 2020).
  - **Healthy Baseline (Negative Validation):** Defect-free operational window (February 2020).
  - **Failure #2 (EXCLUDED):** Explicitly excluded due to maintenance log/timestamp anomaly in the paper.

---

# 3. THE GOLDEN PATH (FAILURE #3) — EXACT FACTS & FROZEN MILESTONES

All timestamps, physical values, sigmas, and lead times below are **empirical facts derived directly from `MetroPT3(AirCompressor).csv`**. They are validation targets, NOT hardcoded engine outputs.

```
+-------------------------------------------------------------------------------------------------------------+
|                                        THE GOLDEN PATH TIMELINE (FAILURE #3)                                |
+-------------------------------------------------------------------------------------------------------------+
| June 4 00:33:07 UTC  -->  EARLY EXCURSION: DV_pressure > 0.5 bar (~67h before LPS). Refusal to cry wolf!     |
| June 5 09:50:39 UTC  -->  CONFIRMED DEGRADATION: DV=2.1856 bar (+23.75σ), Oil=74.97°C (+5.71σ), 3-step persistence |
|                           --> DECISION ENGINE OPENS CASE: APU-INC-20200605-01 (CONFIRMED)                   |
| June 5 10:15:00 UTC  -->  ML CORROBORATION: Isolation Forest = 0.382 > 0.35 (5 features). Confidence -> HIGH  |
|                           --> Safe Mode Intervention Recommended                                            |
| June 5 10:16:00 UTC  -->  SAFE MODE SIMULATED INTERVENTION: ActionGuard validates 5 gates -> Stream branches|
| June 6 19:42:19 UTC  -->  REACTIVE LPS MILESTONE: Line pressure < 7.0 bar trips mechanical relay (LPS=1)   |
|                           --> CONFIRMED INTERVENTION WINDOW = 33 HOURS 52 MINUTES (2032 MINUTES)            |
| June 8 16:05:00 UTC  -->  POST-MAINTENANCE RECOVERY: RecoveryVerifier tracks 5/5 healthy LOADED observations|
|                           --> CASE CLOSED: Asset APU-COMP-01 released back to HEALTHY service               |
+-------------------------------------------------------------------------------------------------------------+
```

### Milestone 1: Early Weak Excursion (Noise Rejection)
- **Timestamp:** `2020-06-04 00:33:07 UTC` (~67 hours before LPS).
- **Physical Signal:** Discharge valve pressure `DV_pressure` crosses 0.5 bar.
- **Engine Behavior:** Classified as `Transient Anomaly Excursion`. System **deliberately refuses to escalate or open an incident**.
- **Operational Principle:** A single sensor spike without thermal corroboration or temporal persistence is insufficient evidence. This proves **false-positive resistance**.

### Milestone 2: Confirmed Degradation (Incident Onset)
- **Timestamp:** `2020-06-05 09:50:39 UTC`.
- **Pressure Evidence:** $\text{DV\_pressure} = 2.1856\text{ bar}$ (Loaded baseline: $\mu = -0.0164, \sigma = 0.0927$) $\rightarrow \mathbf{+23.75\sigma}$.
- **Thermal Evidence:** $\text{Oil\_temp} = 74.97^\circ\text{C}$ (Loaded baseline: $\mu = 54.98^\circ\text{C}, \sigma = 3.50^\circ\text{C}$) $\rightarrow \mathbf{+5.71\sigma}$.
- **Temporal Evidence:** `TEMPORAL_STEP_CONFIRMED` sustained across 3 consecutive loaded observation cycles.
- **Decision Engine Action:** Sole authority creates **Operational Case** `APU-INC-20200605-01` in state `DETECTED / CONFIRMED`.

### Milestone 3: Independent ML Corroboration
- **Timestamp:** `2020-06-05 10:15:00 UTC`.
- **Model:** Isolation Forest trained on February defect-free LOADED data with `random_state = 42`.
- **Features (5 LOADED Signals):** `DV_pressure`, `H1` (analog motor current), `Oil_temp`, `Motor_current`, `TP3` (pneumatic line pressure).
- **ML Score:** $\mathbf{0.382 > 0.35}$ (Trigger threshold).
- **Policy Result:** Raises operational confidence to `HIGH`; recommends `EXECUTE_MITIGATION`. **ML does NOT create the case; it corroborates the physical evidence.**

### Milestone 4: Conventional Reactive Alert (Baseline Benchmark)
- **Timestamp:** `2020-06-06 19:42:19 UTC`.
- **Physical Trigger:** Reservoir pressure collapses below 7.0 bar, tripping the mechanical Low Pressure Switch (`LPS = 1`).
- **Lead-Time Calculation:**
  $$\Delta T = \text{Timestamp}_{\text{LPS}} - \text{Timestamp}_{\text{Detection}} = 2032\text{ minutes} = \mathbf{33\text{ hours } 52\text{ minutes}}$$
- **Rule:** This duration must be derived dynamically by subtracting datetime milestones, **NEVER hardcoded as a static string or integer**.

### Milestone 5: Simulated Safe Mode & Recovery Verification
- **Simulated Intervention:** Operator triggers Safe Mode. `ActionGuard` checks 5 policy conditions and branches replay stream to post-maintenance segment (`2020-06-08 16:05:00 UTC`).
- **Recovery Criteria:** Telemetry must satisfy:
  $$\text{DV\_pressure} < 0.05\text{ bar} \quad \text{AND} \quad \text{Oil\_temp} < 67.0^\circ\text{C}$$
  strictly within the **`LOADED` regime for 5 consecutive observations**.
- **Case Sign-off:** Upon verification, operator executes `POST /api/case/close`, recording final audit sign-off and releasing asset back to `HEALTHY`.

---

# 4. ARCHITECTURAL PILLARS & SEMANTIC CONTRACTS

## 4.1 Strict 3-Tier Data Separation
The system prevents ground truth leakage by strictly enforcing three isolated data layers:

| Layer | Component | Nature & Source | Forbidden Action |
|---|---|---|---|
| **Layer A: Business Context** | `AssetRegistry` | Static fleet hierarchy: Linha Azul $\rightarrow$ Train #302 $\rightarrow$ APU $\rightarrow$ Compressor. | Never convert into dynamic sensor readings. |
| **Layer B: Observed / Computed State** | Detectors, Fusion, Engine | Sensor readings, regimes, sigmas, IF scores, active cases. | Never leak ground truth maintenance logs. |
| **Layer C: Validation Reference** | Historical Failure Reports | Ground truth from dataset paper (*"train had to be removed from tracks"*). | **Never leak into online detector algorithms.** |

## 4.2 Dual-Clock Live Simulation Architecture
To present an honest, deterministic demo without pretending historical data is a live IoT feed:
1. **`event_time` (Historical Clock):** Original 2020 timestamp from dataset. Preserved across all detectors, temporal step calculations, gap handling, and lead-time derivation.
2. **`simulation_time` (Pacing Clock):** Wall-clock replay ticker with configurable speed multipliers (1x, 10x, 60x, 300x) that respects the true $\Delta t$ between samples.
3. **UI Transparency Badge:** Prominently labeled `[ LIVE SIMULATION · HISTORICAL DATA ] Scenario: Failure #3`.

## 4.3 Asset-Centric Case Model (Siemens Senseye Invariant)
- **Hierarchy:** `FLEET` $\rightarrow$ `TRAIN` $\rightarrow$ `APU` $\rightarrow$ `COMPRESSOR` $\rightarrow$ `CASE` $\rightarrow$ `EVIDENCE` $\rightarrow$ `ACTION` $\rightarrow$ `RECOVERY`.
- **Senseye Invariant:** **Maximum one active operational case per physical asset at any time.**
- If an asset already has an open case, subsequent anomalies update the existing investigation dossier; they never spawn duplicate uncoordinated cases.

## 4.4 ActionGuard Policy Barrier
Before any simulated Safe Mode action or stream branching is permitted, `ActionGuard` enforces 5 non-negotiable checks:
1. `CASE_CONFIRMED`: Active case must exist in `DETECTED` or `INVESTIGATING`.
2. `MITIGATION_RECOMMENDED`: DecisionEngine must have formally recommended `EXECUTE_MITIGATION`.
3. `SINGLE_ACTIVE_CASE`: No conflicting open cases on the asset.
4. `SIMULATION_MODE`: System must be in declared simulation mode.
5. `REPLAY_BRANCH_AVAILABLE`: Post-maintenance historical segment must be configured.

## 4.5 Append-Only CaseEvent Ledger
Every milestone generates an immutable event (`EVT-001`, `EVT-002`, ...) recorded in MongoDB `case_events` and surfaced via `/api/case/events` and `/api/timeline`.

---

# 5. COMPREHENSIVE ARCHITECTURAL DECISION RECORDS (ADRs)

- **ADR-001: Evidence Before Policy.** Detectors only emit observations; they never create incidents, set severity, or execute actions. `DecisionEngine` is the sole policy authority.
- **ADR-002: Machine Learning as Corroborator.** Isolation Forest is an independent multivariate sanity check ($IF > 0.35$ on 5 features). It never creates incidents independently and has no synthetic sigma conversions.
- **ADR-003: Separation of State Dimensions.** Asset Health (`HEALTHY`, `DEGRADING`, `CRITICAL`), Operating Regime (`OFF`, `LOADED`, etc.), and Case Phase (`CONFIRMED`, `PROTECTING`, `VERIFYING`, `RESOLVED`) are strictly separate state machines.
- **ADR-004: Explicit Deterministic Historical Replay.** Replay is implemented as an iterator stream over sorted telemetry. No fake live streams or stochastic delays in unit tests.
- **ADR-005: MongoDB Multi-Modal Storage.** Raw high-frequency telemetry lives in MongoDB Time Series (`measurements`); state and audit logs live in document collections (`operational_cases`, `case_events`). Window aggregations use `$setWindowFields`.
- **ADR-006: Datadog as Observability Control Plane.** Datadog monitors the health and performance of CompressorGuard (metrics, APM traces, structured JSON logs with trace correlation); it does not replace the physical physics engine.
- **ADR-007: Rejection of Time Series Change Streams.** Time Series change streams are rejected to eliminate unnecessary distributed race conditions during demo execution.
- **ADR-008: Dynamic Lead-Time Derivation.** Lead time is derived dynamically ($\text{Timestamp}_{\text{LPS}} - \text{Timestamp}_{\text{Detection}}$); hardcoding 2032 minutes in code is strictly prohibited.
- **ADR-009: Observation-Oriented Public Semantics.** Public APIs expose high-level physical observations and provenances; internal implementation details (window lengths, raw sample indices) are encapsulated.
- **ADR-010: Single Active Case Invariant.** Enforce Siemens Senseye pattern: only 1 active operational case per asset.
- **ADR-011: Five-Gate ActionGuard Policy.** Safe mode execution requires 5 verified criteria before allowing telemetry stream branching.
- **ADR-012: Append-Only CaseEvent Ledger.** All incident phase changes and interventions are written to an immutable timeline ledger.
- **ADR-013: Post-Maintenance Stream Branching.** Safe mode simulates intervention by branching replay to the verified post-maintenance telemetry segment (June 8, 2020).
- **ADR-014: Zero-Build High-Performance SPA Console.** Operations console is implemented in lightweight vanilla JS, CSS, and HTML served directly by FastAPI. Zero Node/npm build steps required for instant deployment.

---

# 6. MANDATORY TECHNOLOGY BLUEPRINT: MONGODB ATLAS & DATADOG

## 6.1 MongoDB Atlas Architecture
1. **Time Series Collection (`measurements`):**
   - Options: `timeField: "timestamp"`, `metaField: "metadata"`, `granularity: "seconds"`.
   - Document Schema:
     ```json
     {
       "timestamp": "ISODate(2020-06-05T09:50:39Z)",
       "metadata": { "asset_id": "APU-COMP-01", "scenario": "failure_3" },
       "dv_pressure_bar": 2.1856,
       "oil_temp_c": 74.97,
       "motor_current_a": 6.82,
       "regime": "LOADED"
     }
     ```
   - **CRITICAL TTL INVARIANT:** In MongoDB Time Series, never set an aggressive TTL (e.g., 30 days) on historical `timestamp` (year 2020), as MongoDB's TTL reaper will immediately wipe historical data. TTL must only be placed on real-world ingestion time (`ingested_at`).
2. **Rolling Window Aggregation (`$setWindowFields`):**
   - Evaluates 600-second sliding windows for rolling average pressure and oil temperature partitioned by `metadata.asset_id`.
3. **Document Collections:**
   - `operational_cases`: Upserted case state indexed by `case_id` and `asset_id`.
   - `case_events`: Append-only event history indexed by `case_id` and `event_time`.
4. **Testing Fallback:** `InMemoryCollection` and `InMemoryDatabase` allow 100% offline testing without an active MongoDB cluster.

## 6.2 Datadog Observability Control Plane
1. **DogStatsD Custom Metrics (`compressorguard.*`):**
   - `telemetry.pressure_bar` (Gauge)
   - `telemetry.oil_temperature_c` (Gauge)
   - `ml.anomaly_score` (Gauge)
   - `incident.lead_time_seconds` (Gauge: 121,920s)
   - `recovery.consecutive_observations` (Gauge: 0 to 5)
   - `case.lifecycle_state` (Gauge)
2. **APM Distributed Tracing (`ddtrace`):**
   - FastAPI tracing middleware emits spans for all API endpoints.
   - Core engine spans: `pipeline.tick`, `detector.evaluate`, `ml.inference`, `decision.evaluate`, `action.safe_mode`, all on service `compressorguard`. Datadog derives the APM metric as `trace.<service>.<operation>.duration`, so operation names deliberately do **not** repeat the service prefix — `trace.compressorguard.detector.evaluate.duration` is what the dashboard queries. `tests/test_datadog_config_contract.py` enforces that agreement.
3. **Structured JSON Logging:**
   - `DatadogJSONFormatter` automatically injects `dd.trace_id`, `dd.span_id`, `dd.service`, `dd.env` into every log entry.
4. **Monitors & Dashboard (`datadog/`):**
   - `datadog/monitors.json`: Configured monitors for early pressure breaches and verified recovery.
   - `datadog/dashboard.json`: 8-widget APM dashboard displaying fleet status, thermodynamic trends, and ML corroboration.

---

# 7. PUBLIC REST API CONTRACTS & SCHEMAS

All endpoints are hosted via FastAPI under `/api`:

### 1. Operations Overview: `GET /api/operations`
Returns fleet hierarchy, honest counts, and active case summary.
```json
{
  "fleet": { "fleet_id": "FLEET-METRO-01", "name": "Linha Azul Fleet" },
  "train": { "train_id": "TRAIN-302", "name": "Trainset #302" },
  "asset": { "asset_id": "APU-COMP-01", "name": "APU Air Compressor #1" },
  "operations_summary": {
    "monitored_assets_count": 1,
    "active_cases_count": 1,
    "assets_observing_count": 0,
    "scenario_name": "Failure #3 - Air Leak",
    "simulation_mode": "LIVE_SIMULATION",
    "confirmed_intervention_window": "33h 52m (2032 min)"
  },
  "active_case": { ... }
}
```

### 2. Operational Case: `GET /api/case` (Alias: `GET /api/incident`)
Returns active case details, lead time, and health state.

### 3. Evidence Pack: `GET /api/evidence`
Returns the 4-card evidence pack with complete thermodynamic provenance.
- Pressure observation (+23.75σ)
- Thermal stress observation (+5.71σ)
- Temporal step observation (3 cycles confirmed)
- ML corroboration (Isolation Forest = 0.382)

### 4. Case Event Ledger: `GET /api/case/events` (Alias: `GET /api/timeline`)
Returns chronological append-only audit trail (`EVT-001`, `EVT-002`, ...).

### 5. Safe Mode Intervention: `POST /api/action/safe-mode`
Triggers simulated safe mode intervention protected by `ActionGuard`. Transitions state to `MITIGATING` and branches telemetry stream to post-maintenance segment.

### 6. Recovery Progress: `GET /api/recovery`
Returns progress toward the 5/5 healthy loaded observation criteria.

### 7. Close Case: `POST /api/case/close`
Closes verified operational case. Rejects with `HTTP 409 Conflict` if recovery criteria are not verified.

### 8. Validation Reference: `GET /api/validation-reference`
Returns historical Lisbon Metro failure report (Layer C) for ground truth verification.

### 9. Demo Controls: `POST /demo/play`, `POST /demo/pause`, `POST /demo/speed`, `GET /demo/status`
Controls playback pacing without polluting product domain APIs.

---

# 8. COMPLETE CODEBASE REPOSITORY MAP

All source code is located in `d:\Code\Projects\self-projects\iot-hackathon`:

```
iot-hackathon/
├── datadog/
│   ├── dashboard.json               # Datadog 8-widget APM dashboard layout
│   └── monitors.json                # Datadog alerting monitors spec
├── docs/
│   ├── PITCH_DECK_AND_DEMO_RUNBOOK.md # 3-minute pitch deck & live script
│   ├── PRODUCT_UX_SPEC.md           # UI/UX specification & 4-tier design
│   └── RAIL_ECONOMICS_AND_VALUE_MODEL.md # 7 value pools & economic math
├── screen/                          # Detailed specs for Screens 01 to 07
├── scripts/
│   ├── ingest_historical_to_mongo.py # Batch ingestion script for Atlas
│   └── verify_evaluation_gates.py   # Automated G1-G5 audit script
├── src/
│   ├── api/
│   │   ├── app.py                   # FastAPI app factory, routes, static mount
│   │   ├── dependencies.py          # Lifecycle manager dependency injection
│   │   ├── routes_demo.py           # Demo playback control endpoints
│   │   ├── routes_product.py        # Core operational domain endpoints
│   │   └── schemas.py               # Pydantic v2 domain schemas
│   ├── domain/
│   │   ├── contracts.py             # Abstract base classes (BaseDetector, etc.)
│   │   ├── enums.py                 # Enums (HealthState, Regimes, Severity, etc.)
│   │   ├── models.py                # TelemetryPoint, EvidenceState, CaseEvent
│   │   ├── registry.py              # Asset hierarchy & ValidationReference
│   │   └── scenarios.py             # Scenario definitions (#1, #3, #4, healthy)
│   ├── engine/
│   │   ├── action_guard.py          # 5-condition policy barrier for Safe Mode
│   │   ├── benchmark.py             # Dynamic lead-time calculator
│   │   ├── decision.py              # DecisionEngine policy evaluation matrix
│   │   ├── detectors.py             # Pressure, Thermal, Temporal, IF detectors
│   │   ├── factory.py               # Golden Path component assembler
│   │   ├── fusion.py                # Multi-sensor evidence fusion engine
│   │   ├── lifecycle.py             # Orchestrator for streaming, state & audit
│   │   ├── recovery.py              # RecoveryVerifier (5/5 healthy loaded criteria)
│   │   ├── regime.py                # Operating regime classifier
│   │   ├── replay.py                # Raw CSV loader & chronological streamer
│   │   └── simulation.py            # Dual-clock simulation runner
│   ├── observability/
│   │   ├── logger.py                # Datadog structured JSON logging formatter
│   │   ├── metrics.py               # DogStatsD metrics client with safe fallback
│   │   └── tracer.py                # APM distributed tracing & middleware
│   ├── static/
│   │   ├── app.js                   # Modern SPA reactivity engine & event loop
│   │   ├── index.html               # APM-grade dark mode Operations Console
│   │   └── styles.css               # Carbon theme, pulse effects, drawers
│   └── storage/
│       ├── mongo_client.py          # MongoDB Atlas client & In-Memory fallback
│       └── repository.py            # Time series & document repository methods
├── tests/                           # 98 comprehensive pytest files
├── demo.bat                         # 1-Click launcher for Windows
└── run_demo.py                      # Interactive CLI & web server runner
```

---

# 9. RAIL ECONOMICS & OPERATIONAL VALUE MODEL

To satisfy industrial commercialization criteria, CompressorGuard establishes an honest, rigorous economic framework.

## 9.1 The Triad of Intellectual Honesty
1. **Observed (Empirical Sensor Truth):**
   - Confirmed lead time: **33 hours 52 minutes**.
   - Thermodynamic deviations: $+23.75\sigma$ pressure, $+5.71\sigma$ thermal.
2. **Modeled (Scenario Economic Parameters):**
   - Configurable scenario cost model: $\text{Avoided Cost} = T_{\text{downtime}} \times C_{\text{hour}} + C_{\text{rush\_parts}} + C_{\text{emergency\_labor}}$.
   - Labeled transparently as `Modeled Scenario Estimate`, never misrepresented as realized bank deposits.
3. **Verified (Empirical Post-Action Telemetry):**
   - Physical recovery verified via 5/5 consecutive loaded observations ($\text{DV} < 0.05\text{ bar}$, $\text{Oil} < 67^\circ\text{C}$).

## 9.2 The 7 Rail Value Pools
1. **Avoided Unplanned Downtime:** NIST benchmark shows 52.7% more downtime in reactive vs. predictive maintenance.
2. **Maintenance Cost Reduction:** IBM Maximo & DOE benchmarks indicate 18–31% direct maintenance savings.
3. **Elimination of Emergency Overtime:** Shifts repairs into scheduled depot night windows.
4. **Supply Chain Optimization:** Advance procurement of pilot valves and seal kits eliminates rush air freight.
5. **Fleet Availability ("Shadow Fleet"):** Unlocking availability without purchasing additional multi-million dollar trainsets (SNCF increased availability by +30%).
6. **CapEx Deferral & Asset Longevity:** Preventing oil thermal breakdown and cylinder seizure extends APU lifespan.
7. **Service Continuity & Public Trust:** Eliminates tunnel stall events and passenger evacuation safety hazards.

---

# 10. DEMO STRATEGY, 5 JUDGING GATES & ATTACK SCENARIOS

## 10.1 The 5 Evaluation Gates of Judges
Every hackathon judge evaluates projects across 5 progressive gates:
```
[ G1: Business Consequence ] -> [ G2: Detection Proof ] -> [ G3: Physics Why ] -> [ G4: Safe Response ] -> [ G5: Tech Fit ]
(Understood in 20 sec?)       (33h 52m dynamic lead?)    (Thermodynamic proof)    (ActionGuard & 5/5)   (MongoDB + Datadog)
```

## 10.2 The 3-Minute Demo Script (The 7 Golden Moments)
1. **Moment 1 (0:00–0:25) — Fleet Normal & Business Problem:** Show Linha Azul fleet hierarchy. Explain that APU compressor failure clamps failsafe brakes and halts the subway line.
2. **Moment 2 (0:25–0:50) — Noise Rejection at 00:33:07:** Advance replay to June 4 00:33. Show DV spike > 0.5 bar. Point out that the system **deliberately does not open an incident** because a single spike is insufficient evidence (refusal to cry wolf).
3. **Moment 3 (0:50–1:20) — Confirmed Degradation at 09:50:39:** Advance to June 5 09:50. Show discharge valve pressure jump (+23.75σ) paired with thermal drift (+5.71σ) across 3 loaded cycles. DecisionEngine opens Case `APU-INC-20200605-01`. Hero metric: **33h 52m confirmed intervention window**.
4. **Moment 4 (1:20–1:45) — ML Corroboration at 10:15:00:** Show Isolation Forest score = 0.382 > 0.35. Clarify that ML provides independent multivariate corroboration; it does not replace physical explainability.
5. **Moment 5 (1:45–2:15) — Safe Mode Intervention:** Inspect `ActionGuard` 5-gate checklist. Click "Simulate Safe Mode Intervention". Stream branches to post-maintenance historical telemetry.
6. **Moment 6 (2:15–2:40) — Recovery Verification & Sign-off:** Observe the recovery progress bar fill 5/5 consecutive healthy loaded cycles. Click "Sign Off & Close Case" to release asset back to `HEALTHY`.
7. **Moment 7 (2:40–3:00) — Datadog & MongoDB Proof:** Show Datadog dashboard with real APM spans and metrics; show MongoDB `$setWindowFields` aggregation.

## 10.3 Judge Attack Scenarios & Ironclad Responses

- **Q: "Isn't this just simple thresholding?"**
  - **A:** *"No. At 00:33 on June 4, the pressure breached 0.5 bar, but the system refused to trigger. We require multi-signal evidence: loaded-regime pressure deviation (+23.75σ), thermal drift (+5.71σ), temporal step persistence across 3 loaded cycles, and independent multivariate corroboration via Isolation Forest before the DecisionEngine recommends action."*
- **Q: "Why do you need Machine Learning if physics rules already work?"**
  - **A:** *"Physical detectors explain individual univariate deviations. The Isolation Forest evaluates the joint multivariate relationship across 5 loaded variables. It acts as an independent corroborator, raising decision confidence to HIGH without becoming an uninterpretable black box."*
- **Q: "Did your software prevent the physical failure in 2020?"**
  - **A:** *"No, this is historical replay. We do not claim physical actuation or financial savings. We demonstrate that we detected confirmed degradation 33 hours and 52 minutes before the reactive LPS switch tripped, simulated a safe-mode intervention, and verified recovery against strict operational criteria."*
- **Q: "Why MongoDB and not a traditional relational database?"**
  - **A:** *"MetroPT-3 produces 1.5 million telemetry points with irregular intervals. MongoDB Time Series collections handle native high-frequency time-series storage, `$setWindowFields` computes sliding-window statistics directly in the data layer, and flexible document collections maintain the operational case ledger and event timeline."*
- **Q: "Why Datadog instead of just showing charts on your UI?"**
  - **A:** *"Datadog serves as our operational control plane. It decouples fleet observability from the local application, streaming custom DogStatsD metrics, correlating distributed APM traces across FastAPI endpoints, and structuring logs with trace IDs for industrial compliance."*

---

# 11. KNOWN PITFALLS, FIXED BUGS & SYSTEM INVARIANTS

### 1. The MongoDB 2020 Historical TTL Trap
- **Trap:** Setting `expireAfterSeconds: 30 * 86400` on the `timestamp` field of historical data (year 2020).
- **Consequence:** MongoDB's background TTL thread sees `timestamp` is in 2020 (over 30 days old) and deletes all telemetry immediately upon insertion!
- **Invariant:** TTL must strictly be applied to real-world ingestion time (`ingested_at`), never historical `event_time`.

### 2. Temporal Gap Integrity (~331 Gaps > 30s)
- **Trap:** Treating $N$ filtered samples as $N$ continuous seconds.
- **Consequence:** Because MetroPT-3 has 331 gaps > 30s and periods of `TRANSIENT` or `OFF_LOAD`, counting samples without checking timestamps creates false temporal continuity.
- **Invariant:** `TemporalStepDetector` must check actual timestamp deltas and enforce regime continuity.

### 3. ML Scope Invariant
- **Trap:** Letting ML create incidents or inventing fake sigma values for Isolation Forest.
- **Invariant:** $IF > 0.35$ on 5 LOADED features with `random_state = 42`. ML only corroborates; it never creates cases independently.

### 4. Dynamic Milestone Derivation
- **Trap:** Hardcoding `33h 52m` or `2032` in the codebase.
- **Invariant:** The lead time must be derived dynamically: $\text{Timestamp}_{\text{LPS}} - \text{Timestamp}_{\text{Detection}}$.

---

# 12. RULES OF ENGAGEMENT FOR THE NEXT AI

When continuing work on CompressorGuard:

1. **Do NOT write generic hackathon boilerplate.** Assume the architecture above is fully built and verified (98/98 tests passing).
2. **Preserve the Epistemic Triad:** Never mix `Observed` telemetry with `Modeled` economics or `ValidationReference` ground truth.
3. **Respect the Decision Authority:** Detectors observe, Evidence explains, DecisionEngine decides. Never place incident creation logic inside a detector.
4. **Preserve the Siemens Senseye Invariant:** Maximum one active operational case per asset.
5. **Enforce Epistemic Tagging:** In all architectural audits, categorize findings as:
   - `FACT`: Empirical reality from dataset or verified test code.
   - `DECISION / ADR`: Deliberate design choices.
   - `ASSUMPTION`: Working hypotheses awaiting real data proof.
   - `BUG`: Concrete implementation defects.
   - `RISK`: Operational or demonstration hazards.
   - `PROPOSAL`: Unimplemented suggestions.
6. **Prioritize Real-World Defensibility:** Always ask:
   > *"Does this make CompressorGuard more credible to a technically sophisticated hackathon judge, or does it merely make the codebase bigger?"*

---

### SINGLE-SENTENCE NORTH STAR
> **CompressorGuard is an evidence-driven closed-loop operational case platform that transforms raw physical telemetry into a defensible decision, a safe intervention, verified recovery, and measurable fleet availability.**
