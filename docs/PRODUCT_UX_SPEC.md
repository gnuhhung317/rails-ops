# CompressorGuard: Product & UX Specification (Operations Command Platform)

> **Document Version:** 3.0 (Production-Ready Operations Console & Human-in-the-Loop Governance)  
> **Target:** Operations Command Platform for Critical Rail Fleet Assets  
> **Core Promise:** **Detect earlier → Prove why → Act safely → Verify recovery.**

---

## 1. Product Thesis (The North Star)

* **Category:** Production-Grade Operations Command Platform for Rail Fleet Critical Physical Assets (Not an auto-pilot slideshow, not a flat IoT sensor dump, not an unverified anomaly scoring utility).
* **Target User & Persona:** Fleet Operations Specialist / Rail Transit Dispatcher responsible for Lisbon Metro train lines (`Linha Azul`).
* **The Business & Operational Spine:**
  $$\text{Fleet} \longrightarrow \text{Train} \longrightarrow \text{APU} \longrightarrow \text{Compressor} \longrightarrow \text{Case} \longrightarrow \text{Evidence} \longrightarrow \text{Triage \& Playbook} \longrightarrow \text{ActionGuard} \longrightarrow \text{Recovery} \longrightarrow \text{Sign-Off}$$
  - **Fleet:** Where leadership and dispatch monitor transit service continuity across active trainsets.
  - **Asset:** Where physical component degradation occurs and telemetry is sampled every 10 seconds.
  - **Case:** The structured, single-instance unit of operational work assigned to and acknowledged by a dispatcher.
  - **Evidence:** The 4-signal thermodynamic & multivariate provenance that earns operator trust.
  - **Triage & Action:** Human-in-the-Loop acknowledgment, maintenance work-order drafting, and policy-governed safe simulation intervention (`ActionGuard`).
  - **Verification & Sign-Off:** Proof of telemetry stabilization across 5 consecutive `LOADED` observations before operator root-cause sign-off and asset release.
* **Strict Separation of 3 Data Layers:**
  1. **Layer A — Business Context (Asset Registry):** Fleet, Train, APU, Compressor, Criticality, Line Assignment, Depot.
  2. **Layer B — Observed Telemetry & Computed State:** Real-time rolling sensor facts, sigmas, operating regimes (`LOADED` vs `UNLOADED`), detector states, and corroboration scores.
  3. **Layer C — Validation Reference (Ground Truth):** Historical maintenance reports (`Failure #3 Air Leak`) isolated in an on-demand Audit Drawer, strictly decoupled from online detectors.
* ** strict Separation of Product UI vs. Simulation Harness:**
  - **Primary Product UI:** 100% authentic Industrial Operations Console. No hardcoded telemetry values, no pitch-deck paragraphs, and no "jump to milestone" buttons cluttering the main navigation header.
  - **Collapsible Replay Studio Drawer:** All simulation transport controls (`Play/Pause`, `Step 10s`, `Speed 1x..300x`, `Scenario Selector`, and `Diagnostic Bookmarks`) live inside a collapsible bottom-right developer/demo drawer (`🎛️ Replay Studio` / `Shift+S`).
* **The 3 Unforgettable Claims:**
  1. **33 hours 52 minutes Confirmed Intervention Window:** Calculated deterministically from confirmed degradation detection (`2020-06-05 09:50:39 UTC`) to reactive Low Pressure Switch alert (`2020-06-06 19:42:19 UTC`).
  2. **Evidence Provenance > Anomaly Score:** 4-signal structured cross-sensor thermodynamics with explicit source provenance: Pressure ($+23.75\sigma$), Thermal drift ($+5.71\sigma$), Temporal 3-cycle step persistence, plus **Multivariate Isolation Forest (5 features in LOADED regime) as independent corroboration**.
  3. **Closed-Loop Recovery Verification:** Operator playbook execution verified by `ActionGuard` branches to real post-maintenance telemetry (`2020-06-08 16:05:00 UTC`); Case can be signed off and closed only when 5 consecutive healthy `LOADED` observations are verified.
* **Strict Anti-Scope (Noise to Avoid):**
  - No hardcoded telemetry numbers or hardcoded `✓ PASS` checklists in frontend templates.
  - No exposed demo/milestone jump bars inside the primary operator header.
  - No LLM Chatbots or conversational Q&A widgets.
  - No fake `[🔴 LIVE]` badges (labeled honestly as `[ LIVE SIMULATION · HISTORICAL DATA ]`).
  - No fake SIL-2 or track gradient sensors.

---

## 2. Cognitive & Operational Workflow (Human-in-the-Loop Progression)

An operator or technical evaluator interacting with the console experiences a real, data-driven command workflow:

```text
[STAGE 1: CONTINUOUS FLEET MONITORING & NOISE SUPPRESSION]
 └──► Operator views live multi-channel strip charts (DV_pressure, Oil_temp, Motor_current)
      and the Filterable Fleet Asset Grid.
 └──► At 2020-06-04 00:33:07 UTC, a transient pressure spike occurs in LOADED regime.
      Temporal persistence is 1/3 (< 3 required) and thermal drift is absent.
      Engine logs a SUPPRESSED entry to the Real-Time Anomaly Watchlist. Zero false cases opened.

[STAGE 2: CASE DETECTION & OPERATOR TRIAGE]
 └──► At 2020-06-05 09:50:39 UTC, DV_pressure breach (> 2.0 bar) persists across 3 consecutive
      LOADED cycles. Engine opens CASE-20200605-01 (Phase: DETECTED, Status: UNACKNOWLEDGED)
      and computes the 33h 52m Confirmed Intervention Window.
 └──► Operator clicks [ Acknowledge & Claim Case ], assigns priority P1-CRITICAL, and inspects
      the 3-Pane Case Investigation Workbench.
 └──► At this point (09:50:39), Dynamic ActionGuard shows 4/5 checks PASS and 1/5 FAIL
      (MITIGATION_RECOMMENDED = FAIL, awaiting multivariate corroboration).

[STAGE 3: MULTIVARIATE CORROBORATION & PLAYBOOK PREPARATION]
 └──► At 2020-06-05 10:15:00 UTC, cumulative Oil_temp drift (+5.71σ) and Multivariate
      Isolation Forest (score 0.382 > 0.35 on 5 loaded features) corroborate the physical fault.
 └──► Case escalates to INVESTIGATING. Dynamic ActionGuard updates live to 5/5 PASS.
 └──► Operator logs a forensic note, selects Playbook SOP-APU-ISO-04 (Dryer Tower Isolation),
      assigns Depot Oriente, and dispatches [ Execute Safe Mode Intervention ].

[STAGE 4: CLOSED-LOOP RECOVERY VERIFICATION & SIGN-OFF]
 └──► Stream branches to real post-maintenance telemetry (2020-06-08 16:05:00 UTC).
      RecoveryVerifier evaluates consecutive LOADED samples against DV < 0.05 bar & Oil < 67.0 °C.
 └──► Live Recovery Table populates Sample #1 through Sample #5 -> Status: RESOLVED (5/5 Verified).
 └──► Operator selects Confirmed Root Cause (Desiccant Drain Valve Leak), enters sign-off notes,
      and clicks [ Sign Off & Close Case ] -> Asset APU-COMP-01 returns to HEALTHY service.
```

---

## 3. Information Hierarchy & High-Density Workspace Layout

The UI is organized into a clean, high-density **Industrial Dark Operations Console** with 4 tiers of information disclosure:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ TIER 1: GLOBAL COMMAND BAR & KPI STRIP (Immediate Operational Posture)                 │
│ • Breadcrumb Scope: Linha Azul Fleet / Train #302 / SUB-APU-01 / APU-COMP-01           │
│ • Honest Stream Badge: [ LIVE SIMULATION · HISTORICAL DATA · 0.1 Hz ]                  │
│ • Live Dynamic KPIs: Monitored Assets | Active Cases | Observing | Regime | Lead Time  │
│ • Utility Triggers: [ Shift: DISPATCHER-0941 ] [ 🗄️ Validation Ref ] [ 🎛️ Replay Studio ]│
├────────────────────────────────────────────────────────────────────────────────────────┤
│ TIER 2: 3-PANE CASE INVESTIGATION WORKBENCH (Primary Operator Workspace)               │
│ • LEFT PANE (3 cols) — Case Context & 4-Signal Evidence Provenance Cards:              │
│     Live values, baselines, sigmas, and detector provenance (Pressure, Thermal,        │
│     Temporal Persistence, and 5-Feature Isolation Forest Corroboration).               │
│ • CENTER PANE (5 cols) — Synchronized Multi-Sensor Strip Charts & Recovery Monitor:    │
│     Rolling time-series chart with LOADED regime shading + Live 5/5 Recovery Table.    │
│ • RIGHT PANE (4 cols) — Operator Command Console, Live ActionGuard & Audit Stream:     │
│     Acknowledge button, Forensic Note input, Live 5-Check ActionGuard Gate (PASS/FAIL),│
│     SOP Playbook & Work Order selector, Safe Mode trigger, Sign-Off form, & CaseEvents.│
├────────────────────────────────────────────────────────────────────────────────────────┤
│ TIER 3: ON-DEMAND DRAWERS (Strictly Isolated from Operational Telemetry)               │
│ • Drawer A — Validation Reference Drawer: UCI MetroPT-3 Failure #3 ground truth audit. │
│ • Drawer B — Replay & Scenario Studio Drawer: Play/Pause, Step, Speed (1x..300x),      │
│   Scenario Switcher (Failure #3, #1, #4, Healthy), and Diagnostic Bookmarks.           │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ TIER 4: DATA & OBSERVABILITY BACKBONE                                                  │
│ • 1.5M raw CSV sensor points via HistoricalScenarioStream & ReplayEngine               │
│ • MongoDB Atlas Time Series (`measurements`) & Document Store (`operational_cases`)    │
│ • Datadog APM distributed traces and DogStatsD operational metrics                     │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Formal Case Lifecycle, Human-in-the-Loop Governance & ActionGuard

The operational Case follows a strict state machine combining automated physics detection with explicit operator governance:

```mermaid
stateDiagram-v2
    [*] --> NONE: ScenarioStream Initialized
    NONE --> OBSERVING: 00:33:07 (Transient spike; 1/3 cycles -> Auto-suppressed in Watchlist)
    OBSERVING --> DETECTED: 09:50:39 (DV > 2.0 bar sustained across 3 loaded cycles -> Case Opened)
    DETECTED --> DETECTED: POST /api/case/acknowledge (Operator claims case & sets P1 priority)
    DETECTED --> INVESTIGATING: 10:15:00 (Thermal drift + ML IF corroboration > 0.35)
    INVESTIGATING --> INVESTIGATING: POST /api/case/work-order (Operator selects SOP & Depot)
    INVESTIGATING --> MITIGATING: POST /api/action/safe-mode (ActionGuard 5/5 PASS verified)
    MITIGATING --> VERIFYING_RECOVERY: First tick of post-maintenance stream (08/06 16:05+)
    VERIFYING_RECOVERY --> VERIFYING_RECOVERY: Evaluating LOADED samples (Violation -> reset 0/5)
    VERIFYING_RECOVERY --> RESOLVED: 5/5 Consecutive healthy LOADED observations verified
    RESOLVED --> CLOSED: POST /api/case/close (Operator root-cause sign-off & asset release)
    CLOSED --> [*]
```

### Dynamic ActionGuard Pre-Flight Checks (`GET /api/action/guard-status`):
Unlike static UI mockups, the console evaluates and renders the live status (`PASS` vs `FAIL`) of all 5 checks at every tick:
1. `CASE_CONFIRMED`: Current lifecycle state is `DETECTED` or `INVESTIGATING`.
2. `MITIGATION_RECOMMENDED`: `DecisionEngine` recommends `EXECUTE_MITIGATION` (requires multi-sensor persistence + ML corroboration; evaluates to `FAIL` at `09:50:39` and transitions to `PASS` at `10:15:00`).
3. `SINGLE_ACTIVE_CASE`: Asset has no conflicting open cases (`conflicting_cases_count == 0`).
4. `SIMULATION_MODE`: Confirms execution within the audit-controlled simulation boundary.
5. `REPLAY_BRANCH_AVAILABLE`: Post-maintenance telemetry segment (`2020-06-08 16:05:00 UTC`) is indexed and ready.

---

## 5. Domain REST API Contracts

### 5.1 `GET /api/operations` (Fleet Operations & Asset Matrix)
```json
{
  "fleet": {
    "fleet_id": "FLEET-METRO-01",
    "name": "Metro Fleet (Linha Azul)",
    "operator_name": "Metro do Porto / CP",
    "depot_location": "Depot Oriente"
  },
  "train": {
    "train_id": "TRAIN-302",
    "model": "Series 300 EMU",
    "service_status": "REVENUE_SERVICE"
  },
  "subsystem": {
    "subsystem_id": "SUB-APU-01",
    "name": "Air Production Unit"
  },
  "asset": {
    "asset_id": "APU-COMP-01",
    "name": "Air Compressor Unit #01",
    "criticality": "CRITICAL",
    "discharge_valve_model": "Knorr-Bremse LP49"
  },
  "operations_summary": {
    "monitored_assets_count": 1,
    "active_cases_count": 1,
    "assets_observing_count": 0,
    "scenario_name": "Failure #3 - Air Leak",
    "simulation_mode": "LIVE_SIMULATION",
    "confirmed_intervention_window": "33h 52m"
  },
  "active_case": {
    "incident_id": "APU-INC-20200605-01",
    "asset_id": "APU-COMP-01",
    "lifecycle_state": "INVESTIGATING",
    "asset_health": "CRITICAL",
    "operational_confidence": "HIGH",
    "acknowledged": true,
    "acknowledged_by": "DISPATCHER-0941",
    "selected_playbook": "SOP-APU-ISO-04"
  }
}
```

### 5.2 `GET /api/telemetry/window?limit=60` (Live Rolling Time-Series Window)
```json
{
  "asset_id": "APU-COMP-01",
  "scenario_id": "failure_3",
  "current_event_time": "2020-06-05T09:50:39Z",
  "baselines": {
    "dv_pressure_loaded_mean": -0.0164,
    "dv_pressure_severe_threshold": 2.0,
    "oil_temp_loaded_mean": 54.98,
    "oil_temp_severe_threshold": 74.0,
    "if_corroboration_threshold": 0.35
  },
  "points": [
    {
      "timestamp": "2020-06-05T09:50:39Z",
      "regime": "LOADED",
      "dv_pressure_bar": 2.1856,
      "oil_temp_c": 74.97,
      "motor_current_a": 6.84,
      "tp2_bar": 8.91,
      "tp3_bar": 8.74,
      "h1_bar": -0.012,
      "lps_active": 0.0,
      "if_anomaly_score": 0.382
    }
  ]
}
```

### 5.3 `GET /api/incident` (or `/api/case` — Active Case Dossier)
```json
{
  "incident_id": "APU-INC-20200605-01",
  "asset_id": "APU-COMP-01",
  "lifecycle_state": "INVESTIGATING",
  "asset_health": "CRITICAL",
  "operational_confidence": "HIGH",
  "acknowledged": true,
  "acknowledged_by": "DISPATCHER-0941",
  "priority": "P1-CRITICAL",
  "work_order": {
    "work_order_id": "WO-20200605-302",
    "playbook_id": "SOP-APU-ISO-04",
    "target_depot": "Depot Oriente",
    "status": "READY_FOR_DISPATCH"
  },
  "lead_time": {
    "lead_time_minutes": 2032,
    "lead_time_formatted": "33h 52m",
    "conventional_alert_timestamp": "2020-06-06T19:42:19Z",
    "earliest_detection_timestamp": "2020-06-05T09:50:39Z"
  },
  "summary": "Confirmed severe step degradation in DV_pressure with thermal stress drift."
}
```

### 5.4 `GET /api/evidence` (Live 4-Signal Evidence Pack With Provenance)
```json
{
  "incident_id": "APU-INC-20200605-01",
  "regime": "LOADED",
  "evidence_pack": [
    {
      "code": "PRESSURE_SEVERE",
      "signal_name": "Discharge Valve Pressure",
      "observed_value": 2.1856,
      "baseline_value": -0.0164,
      "unit": "bar",
      "sigma_deviation": 23.75,
      "status": "CRITICAL",
      "is_primary": true,
      "provenance": {
        "source": "PressureAnomalyDetector",
        "method": "Loaded-regime baseline (sigma > 20.0)",
        "event_time": "2020-06-05T09:50:39Z",
        "regime": "LOADED"
      }
    },
    {
      "code": "THERMAL_STRESS_SEVERE",
      "signal_name": "Compressor Oil Temperature",
      "observed_value": 74.97,
      "baseline_value": 54.98,
      "unit": "°C",
      "sigma_deviation": 5.71,
      "status": "SEVERE",
      "is_primary": false,
      "provenance": {
        "source": "ThermalStressDetector",
        "method": "Loaded-regime thermal drift (sigma > 5.0)",
        "event_time": "2020-06-05T10:15:00Z",
        "regime": "LOADED"
      }
    },
    {
      "code": "TEMPORAL_STEP_CONFIRMED",
      "signal_name": "Temporal Persistence Tracking",
      "observed_value": 2.202,
      "baseline_value": 0.0,
      "unit": "bar_diff",
      "sigma_deviation": 0.0,
      "status": "CONFIRMED",
      "is_primary": false,
      "provenance": {
        "source": "TemporalStepDetector",
        "method": "Consecutive loaded cycle persistence (3/3)",
        "event_time": "2020-06-05T09:50:39Z",
        "regime": "LOADED"
      }
    },
    {
      "code": "MULTIVARIATE_CORROBORATED",
      "signal_name": "Multivariate Isolation Forest",
      "observed_value": 0.382,
      "baseline_value": 0.35,
      "unit": "score",
      "sigma_deviation": null,
      "status": "CORROBORATED",
      "is_primary": false,
      "provenance": {
        "source": "IsolationForestDetector",
        "method": "Multivariate boundary on 5 loaded features (DV, H1, Oil, Current, TP3)",
        "event_time": "2020-06-05T10:15:00Z",
        "regime": "LOADED",
        "role": "Independent corroboration (elevates mitigation confidence)"
      }
    }
  ],
  "persistence": {
    "confirmed": true,
    "recent_observations": 3,
    "required_observations": 3
  }
}
```

### 5.5 `GET /api/action/guard-status` & `POST /api/action/safe-mode`
```json
// GET /api/action/guard-status
{
  "is_permitted": true,
  "denial_reason": "",
  "checklist": [
    {"id": "CASE_CONFIRMED", "label": "Case is active and confirmed", "passed": true},
    {"id": "MITIGATION_RECOMMENDED", "label": "DecisionEngine recommends mitigation", "passed": true},
    {"id": "SINGLE_ACTIVE_CASE", "label": "No conflicting active cases on asset", "passed": true},
    {"id": "SIMULATION_MODE", "label": "Simulation intervention boundary verified", "passed": true},
    {"id": "REPLAY_BRANCH_AVAILABLE", "label": "Post-maintenance historical stream segment available", "passed": true}
  ]
}

// POST /api/action/safe-mode
{
  "action_id": "ACT-SM-001",
  "operator_id": "DISPATCHER-0941",
  "playbook_id": "SOP-APU-ISO-04",
  "status": "ACTIVATED",
  "execution_mode": "SIMULATION_BRANCH",
  "target_state": "MITIGATING",
  "stream_branch": {
    "source": "METROPT-3_POST_MAINTENANCE",
    "offset_timestamp": "2020-06-08T16:05:00Z"
  }
}
```

### 5.6 `GET /api/recovery` & `POST /api/case/close`
```json
// GET /api/recovery
{
  "incident_id": "APU-INC-20200605-01",
  "is_recovering": true,
  "is_verified": true,
  "consecutive_healthy_observations": 5,
  "target_healthy_observations": 5,
  "latest_telemetry": {
    "dv_pressure_bar": -0.0164,
    "oil_temp_c": 64.12,
    "regime": "LOADED"
  },
  "criteria": {
    "dv_pressure_max": 0.05,
    "oil_temp_max": 67.0,
    "required_regime": "LOADED"
  }
}

// POST /api/case/close
{
  "status": "CASE_CLOSED",
  "case_id": "APU-INC-20200605-01",
  "operator_id": "DISPATCHER-0941",
  "root_cause": "DESICCANT_DRAIN_VALVE_LEAK",
  "notes": "Verified 5/5 healthy LOADED observations post-overhaul. Released to revenue service.",
  "lifecycle_state": "RESOLVED",
  "asset_health": "HEALTHY"
}
```

### 5.7 `GET /api/case/events` (Chronological CaseEvent Audit Ledger)
Includes both automated engine events (`OBSERVATION`, `DETECTION`, `CORROBORATION`, `DECISION`, `RECOVERY`) and human-in-the-loop operator events (`OPERATOR_ACK`, `FORENSIC_NOTE`, `WORK_ORDER_CREATED`, `ACTION`, `CASE_CLOSED`).

---

## 6. Isolated Simulation & Replay Studio Controls (`/demo/*`)

Simulation controls govern the dual-clock `SimulationRunner` from inside the collapsible **Replay Studio Drawer** (`🎛️ Replay Studio`), keeping the main operator UI clean and production-authentic:

* **`GET /api/scenarios` & `POST /api/operations/scenario`**: Switches the active telemetry scenario (`failure_3`, `failure_1`, `failure_4`, `healthy_baseline`).
* **`POST /demo/play` / `POST /demo/pause` / `POST /demo/speed`**: Controls continuous real-time stream pacing (`1x`, `10x`, `60x`, `300x`).
* **`POST /demo/tick`**: Advances the simulation cursor by one 10-second historical observation.
* **`POST /demo/reset` & `POST /demo/jump`**: Diagnostic bookmark seeking (`early_excursion_0033`, `onset_0950`, `ml_corroborated_1015`, `lps_reactive_1942`, `post_maintenance_1605`) for automated tests and evaluator spot-checks.
