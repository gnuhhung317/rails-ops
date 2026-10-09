# CompressorGuard — Findings & Research Ledger
> **Purpose:** Persistent working memory for domain insights, engineering findings, rail economics benchmarks, and architectural precedents.

---

## 1. Physical Domain & Ground Truth (MetroPT-3)
- **Dataset Source:** Nature Scientific Data (2022) / UCI Machine Learning Repository.
- **Asset:** Air Production Unit (APU) on Lisbon Metro train. 1,516,948 samples @ 1 Hz.
- **Ground Truth Failure #3 Consequence:** The dataset paper explicitly confirms that severe air degradation caused pneumatic pressure collapse, forcing the train to be removed from revenue tracks (*"train had to be removed from tracks"*).
- **Golden Milestones (Deterministic):**
  - Confirmed degradation detected: `2020-06-05 09:50:39 UTC` (Discharge valve pressure `DV_pressure` jumps to 2.1856 bar, $+23.75\sigma$).
  - Thermal drift: Oil temperature `Oil_temp` drifts to 74.97°C, $+5.71\sigma$.
  - Conventional alarm: Low Pressure Switch `LPS = 1` trips at `2020-06-06 19:42:19 UTC`.
  - **Confirmed Intervention Window:** Exactly **33 hours 52 minutes** (2032 minutes).
  - Recovery ground truth: June 8, 2020 16:05:00 onwards (Post-maintenance telemetry).

---

## 2. Predictive Maintenance Economics & Rail Benchmarks
- **Value Pools (7 Groups):**
  1. Avoided downtime (NIST: 52.7% more unplanned downtime in reactive vs predictive; DOE: 35-45% reduction).
  2. Lower maintenance cost (IBM: 18-31% reduction, DOE: 25-30% reduction).
  3. Avoided emergency & overtime labor (Shift to non-revenue night maintenance windows).
  4. Spare parts inventory optimization (Advance procurement of pilot valve seals, eliminating rush freight).
  5. Higher fleet availability ("Shadow Fleet" capacity without new CapEx).
  6. Asset lifetime extension / CapEx deferral (Preventing thermal breakdown of oil and cylinder seizure).
  7. Safety & service disruption risk avoidance (Preserving SIL-2 pneumatic braking and door actuation).

- **Verified Rail & Metro Benchmarks:**
  - **SNCF (France):** 1,100+ trains with CBM/IoT $\rightarrow$ Breakdowns reduced by >50% to 66%, maintenance costs down 20%, depot visits down 30%, Paris fleet availability **+30%** (offline trainsets reduced from 9 to 6-7).
  - **Alstom HealthHub:** Train downtime down to **-30%**, material cost down to **-20%**, recurring faults down to **-50%**.
  - **Hanoi Metro (Line 2A 2025):** 1.756M train-km, 161,611 trips, 13.68M passengers, 97.78B VND ticket revenue. Modeled revenue exposure $\approx 55,650\text{ VND/train-km}$.
  - **Shanghai Metro Line 17 (2026):** Confirms Air Supply Units (VV120) as critical rolling stock subsystems requiring RCM optimization.

---

## 3. Product & Architectural Principles
- **Intellectual Honesty Triad:**
  - **Observed:** 33h 52m lead time derived directly from sensor data.
  - **Modeled:** Estimated avoided downtime value via configurable scenario parameters ($T_{\text{downtime}} \times C_{\text{hour}}$). Labeled as `Estimated Avoided Cost (Scenario Model)` — never fake "realized cash".
  - **Verified:** Physical recovery verified via 5/5 consecutive loaded observations ($\text{DV} < 0.05\text{ bar}$, $\text{Oil} < 67^\circ\text{C}$).
- **Asset Hierarchy:** `FLEET` $\rightarrow$ `TRAIN` $\rightarrow$ `APU` $\rightarrow$ `COMPRESSOR`. Value propagates upward.
- **Operational Case Funnel:** 1,000 spikes $\rightarrow$ 100 excursions $\rightarrow$ 20 confirmed $\rightarrow$ 15 actionable cases $\rightarrow$ 12 safe mode interventions $\rightarrow$ 10 verified recoveries $\rightarrow$ measurable value.
- **Explainability Economics:** 4-card evidence pack reduces investigation time from 20 minutes to 3 minutes (17 minutes saved per incident).

---

## 4. Industrial Precedents & Fleet-Centric Case Architecture
- **Industrial Standards:**
  - **Siemens Senseye:** Asset hierarchy (Site $\rightarrow$ Line $\rightarrow$ Asset); Single Active Case Invariant ("Only one open case per asset at a time"); Evidence dossier attached to Case.
  - **IBM Maximo:** Asset hierarchy, health, risk, and criticality as decision-making context for maintenance work orders.
  - **Alstom HealthHub:** Predictive maintenance positioned alongside fleet availability and downtime elimination.
  - **Datadog Incidents:** Timeline as the single source of truth for chronological investigation, status changes, actions, and remediation.

- **Strict 3-Tier Data Separation:**
  1. **Layer A — Business Context (Asset Registry):** Fleet, Train, APU, Compressor, Criticality.
  2. **Layer B — Observed Telemetry & Computed State:** Sensor readings, regime, sigmas, anomaly scores.
  3. **Layer C — Validation Reference (Ground Truth):** Maintenance reports used strictly for post-hoc validation; never leaked into online detection.

- **Dual-Clock Live Simulation Architecture:**
  - `event_time`: Original historical timestamp from MetroPT-3 (`2020-06-05 09:50:39 UTC`), preserved for all temporal reasoning, gap detection, and lead time calculation.
  - `simulation_time`: Wall-clock replay pacing (1x, 10x, 60x), pacing by $\Delta\text{event\_time}$ respecting variable sampling & gaps $>30$s.
  - Header badge: `[ LIVE SIMULATION · HISTORICAL DATA ] Scenario: Failure #3`.

- **Functional Role of Machine Learning (Isolation Forest):**
  - Model trained on February `LOADED` baseline using 5 features (`DV_pressure`, `H1`, `Oil_temp`, `Motor_current`, `TP3`) with threshold 0.35.
  - **Role:** Independent Corroboration. It does NOT create cases on its own; it increases decision confidence for mitigation recommendation.

- **ActionGuard & Recovery Truthfulness:**
  - `ActionGuard` checks 5 policy conditions before allowing safe-mode simulated intervention.
  - Stream branches to real post-maintenance telemetry (June 8, 2020 16:05:00 UTC).
  - Recovery verifies that telemetry satisfies operational criteria (5/5 healthy LOADED observations), rather than claiming physical railway certification.
  - `CaseEvent` ledger provides an immutable append-only chronology of the entire operational incident.
