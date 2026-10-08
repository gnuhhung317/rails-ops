# CompressorGuard — Final System & Data Specification (v4 FROZEN)

> **Category:** Closed-loop Incident Intelligence System for Physical Assets  
> **Core Promise:** **Detect earlier → Prove why → Act safely → Verify recovery.**

---

## 1. Official Claims & Metrics (Frozen Source of Truth)

### 1.1 Product Claim
> **“CompressorGuard identifies an evolving degradation pattern in MetroPT-3 earlier than a conventional reactive alert, explains the evidence behind the decision, and verifies recovery after an intervention.”**

### 1.2 Quantitative Lead Time & Anomaly Metrics

All metrics are calculated directly from `MetroPT3(AirCompressor).csv` (1,516,948 samples, February baseline in LOADED regime):

| Metric | Timestamp | Value / Lead Time | Meaning & Context |
| :--- | :--- | :--- | :--- |
| **First Abnormal Excursion** | `2020-06-04 00:33:07` | **~67h 09m before LPS** | Single sensor pressure anomaly (`DV_pressure > 0.5` bar). Low confidence, NO incident created. |
| **Confirmed Degradation** | `2020-06-05 09:50:00` | **33h 52m before LPS** | Step change in `DV_pressure` (> 2.0 bar) + thermal drift. Medium confidence, **Incident Created**. |
| **Reactive Baseline Alert** | `2020-06-06 19:42:19` | Baseline (0h 00m) | Traditional low pressure switch threshold (`LPS = 1`, < 7.0 bar). |
| `dv_pressure_bar` Deviation | June 5 09:50 | **+23.75 $\sigma$** | Observed 2.1856 bar vs Healthy LOADED mean -0.0164 ± 0.0927 bar. Primary leak signature. |
| `oil_temp_c` Deviation | June 5 09:50 | **+5.71 $\sigma$** | Observed 74.97 °C vs Healthy LOADED mean 54.98 ± 3.50 °C. Thermal stress corroboration. |

---

## 2. 4-Layer System Architecture

```
                 METROPT-3 TELEMETRY REPLAY / SIMULATOR
                                   │
                                   ▼
                       Telemetry Ingestion Loop
                                   │
                                   ▼
                      MongoDB Time Series Storage
                                   │
                                   ▼
                      Operating Regime Classifier
                                   │
                                   ▼
                       Feature Extraction Engine
                                   │
          ┌────────────────────────┼────────────────────────┐
          ▼                        ▼                        ▼
     Rule Detectors        Temporal Logic           Isolation Forest
     (Pressure & Temp)    (Persistence & Step)     (Multivariate Scorer)
          │                        │                        │
          └────────────────────────┼────────────────────────┘
                                   ▼
                        Evidence Fusion Engine
                                   │ (Calculates Operational Confidence: LOW/MED/HIGH)
                                   ▼
                         Decision Engine
                       (Sole Authority: Matrix)
                       /                      \
                      /                        \
             Asset Health State            Incident Lifecycle
                     │                              │
                     └──────────────┬───────────────┘
                                    ▼
                        Incident Intelligence Workspace
                        (Temporal Evidence Chain + P1 Vector Search)
                                    │
                                    ▼
                         Operator Action (Safe Mode)
                                    │
                                    ▼
                       Dataset-Driven Intervention
                      (Switches Replay Stream Offset)
                                    │
                                    ▼
                         Recovery Verification Engine
                         (Composite Stability Check)
                                    │
                                    ▼
                          INCIDENT RESOLVED
```

### Layer Details:
1. **Layer 1: Detection Engine (Multiple Specialized Detectors)**
   - *Detector A (Pressure Anomaly):* Fast physical signal detection on `dv_pressure_bar`.
   - *Detector B (Thermal Stress):* `oil_temp_c` deviation & thermal drift persistence.
   - *Detector C (Temporal/Persistence):* Distinguishes 10s transient noise from sustained step changes.
   - *Detector D (Regime-Aware Stat):* Deviation calculated strictly vs LOADED/OFF_LOAD regime baseline.
   - *Detector E (Isolation Forest):* Multivariate anomaly corroboration on `[dv_pressure, h1, oil_temp, motor_current, tp3]`.
2. **Layer 2: Evidence Fusion Engine**
   - Fuses independent detectors into **Operational Confidence** (`LOW`, `MEDIUM`, `HIGH`) and builds the **Temporal Evidence Chain**.
3. **Layer 3: Incident Intelligence Layer**
   - Manages Incident Lifecycle (`DETECTED` -> `INVESTIGATING` -> `MITIGATING` -> `VERIFYING_RECOVERY` -> `RESOLVED`).
   - P1: Vector Search on historical incident signature corpus.
4. **Layer 4: Recovery Engine**
   - Handles dataset-driven intervention simulation and evaluates multi-metric recovery conditions (`dv_pressure < 0.05` bar AND `oil_temp < 67` °C for 5 consecutive cycles).

---

## 3. Frozen Detection Decision Matrix (Sole Authority)

All state transitions MUST follow this matrix 1:1:

| Telemetry & Detector Evidence | Asset Health | Incident Lifecycle | Operational Confidence | UI Action / Representation |
| :--- | :--- | :--- | :--- | :--- |
| `dv_pressure` < 0.2 bar AND `oil_temp` < 65°C | `HEALTHY` | `(NO INCIDENT)` | `NONE` | Green status; Fleet normal |
| `dv_pressure` > 0.5 bar for < 3 cycles (transient) | `DEGRADING` | `(NO INCIDENT)` | `LOW` | Yellow badge; "Early Warning: Minor Excursion" |
| `dv_pressure` > 1.0 bar OR `oil_temp` > 70°C for >= 3 cycles | `DEGRADING` | `(NO INCIDENT)` | `MEDIUM` | Yellow status; "Tracking Degradation" |
| `dv_pressure` > 2.0 bar AND `oil_temp` > 74°C for >= 3 cycles | `CRITICAL` | `DETECTED` | `MEDIUM` | Red alert; **Incident Created** (`APU-INC-20200605-01`) |
| `dv_pressure` > 2.0 bar + `oil_temp` > 74°C + ML score > 0.35 | `CRITICAL` | `INVESTIGATING` | **`HIGH`** | Red alert; **Strong Evidence Pack Assembled**; Safe Mode Recommended |
| `LPS == 1` (Line pressure drops below 7.0 bar) | `CRITICAL` | `INVESTIGATING` | **`CRITICAL (REACTIVE)`** | Flashing alert; "Reactive Baseline Alert Active" |
| Operator executes Safe Mode | `RECOVERING` | `MITIGATING` | `PENDING VERIFICATION` | Amber status; "Executing Dataset-Driven Safe Mode Switch" |
| Recovery composite met (5 cycles on post-maint stream) | `HEALTHY` | `RESOLVED` | **`HIGH (VERIFIED)`** | Green checkmark; **Incident Resolved & Recovery Verified** |

---

## 4. Multi-Scenario Validation Matrix

| Scenario Window | Primary Purpose | Detection Verified | Evidence Chain | Recovery Verified |
| :--- | :--- | :---: | :---: | :---: |
| **Failure #3 (June 5–8)** | **Golden Path Demo Scenario** | ✅ Yes | ✅ Yes | ✅ Yes (June 8 16:05+) |
| **Failure #1 (April 18)** | Platform Multi-Failure Test | ✅ Yes | ✅ Yes | N/A (Acute failure) |
| **Failure #4 (July 15)** | Thermal Overheat Test (89.05°C) | ✅ Yes | ✅ Yes | N/A |
| **February 2020** | Healthy False Positive Test | ✅ 0 False Incidents | N/A | N/A |
| **Failure #2 (May 29–30)** | Excluded from evidence | — | — | — (Excluded due to report date anomaly) |

---

## 5. Signature Feature — Temporal Evidence Chain UI Design

The UI Incident Workspace features a dedicated timeline component:

```text
67h09m before reactive alert
        │
        ● Early pressure excursion (DV_pressure > 0.5 bar)
        │
33h52m  ● Confirmed severe step degradation (DV_pressure = 2.18 bar, +23.75σ)
        │
        ● Thermal stress drift (Oil_temperature = 74.97°C, +5.71σ)
        │
        ● Multivariate ML corroboration (Isolation Forest Score = 0.38)
        │
        ▼
        🔴 REACTIVE BASELINE ALERT (LPS = 1, Line Pressure < 7.0 bar)
        │
        │
        ● Operator executed Safe Mode (Dataset-driven stream branch switch)
        │
        ● Recovery evidence verified (DV_pressure = -0.016 bar, Oil_temp = 64.1°C)
        ▼
        ✅ INCIDENT RESOLVED & VERIFIED
```

---

## 6. Scope Governance & Execution Order

### P0 — MUST BUILD (Non-Negotiable)
1. Real MetroPT replay engine & MongoDB Time Series storage
2. Operating regime classifier (`OFF`, `STARTING`, `OFF_LOAD`, `LOADED`, `TRANSIENT`)
3. Regime-aware baseline calculations (LOADED regime baseline)
4. Multi-detector engine (Pressure, Thermal, Temporal, Regime Stat, Isolation Forest)
5. Evidence Fusion Engine & Operational Confidence (`LOW`/`MEDIUM`/`HIGH`)
6. One Decision Engine (1:1 implementation of Detection Decision Matrix)
7. Incident lifecycle state machine (`APU-COMP-01`)
8. Temporal Evidence Chain UI component
9. Dataset-driven intervention simulation (Safe Mode stream branch switch)
10. Telemetry-based recovery verification
11. Datadog APM, Metrics, & Logging integration
12. End-to-end Golden Path demonstration

### P1 — BUILD IF P0 IS STABLE
- Vector Search on MongoDB for historical incident similarity.

### P2 — OPTIONAL WOW
- LLM natural language evidence synthesis.

---
*End of CompressorGuard Final System & Data Specification (v4 FROZEN).*
