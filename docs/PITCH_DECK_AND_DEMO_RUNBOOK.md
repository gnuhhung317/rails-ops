# CompressorGuard — Pitch Deck & Judge Demonstration Runbook
**Industrial Operations Command Platform for Urban Transit Rail**  
*RailOps VN · Metro Line 1 Bến Thành – Suối Tiên · Asset APU-COMP-01 · MUGVN Hackathon 2026*  
*Telemetry provenance: MetroPT-3 public air-compressor run records (Lisbon Metro). Fleet labels are an illustrative Vietnamese operational mapping — see `docs/RAILOPS_VN_PLATFORM_BLUEPRINT.md` §4.1.*  
*MongoDB Atlas Multi-Modal + Datadog Unified Observability*

---

## Executive Summary

| Dimension | Specification |
|:---|:---|
| **Asset** | `APU-COMP-01` · telemetry provenance = MetroPT-3 public compressor run records (Lisbon Metro); Vietnamese fleet/line labels are an illustrative operational mapping, never a data claim |
| **Historical Scenario** | Scenario Failure #3 (June 5–8, 2020) from `MetroPT3(AirCompressor).csv` |
| **Confirmed Lead Time** | **33 hours 52 minutes** (Onset: 09:50:39 June 5 vs. LPS Alert: 19:42:49 June 6) — measured, and asserted by `scripts/verify_console_journey.py` |
| **Modelled Economic Value** | **€193,600** ($210,000+) avoided cost per event (€73,600 delay + €120,000 overhaul avoided) — **ILLUSTRATIVE business case built on our own assumptions, not a published tariff and not a UI claim** |
| **Data Integrity Guarantee** | **100% Real Historical Telemetry** · Zero synthetic or fabricated sensor data |
| **Core Architecture** | Multi-Sensor Physics + Independent ML Corroboration + ActionGuard Safety Checks + Closed-Loop Recovery Verifier |
| **Tech Stack** | Python 3.12 · FastAPI · MongoDB Atlas (Time Series + Document) · Datadog (DogStatsD + APM Tracing) · Vanilla Modern UI |

---

## 3-Minute Hackathon Pitch Script (Judge Presentation)

> **Script to actually rehearse from:** the per-slide Vietnamese talk track (mốc 0:00→3:00, kèm
> câu trả lời cho từng hỏi khó) is embedded as **speaker notes inside `docs/railops-vn-final-deck.pptx`**
> — regenerate with `python scripts/build_pitch_deck.py`. This section is the English background and
> the narrative logic; it is intentionally *not* the verbatim script, and its timings differ from the deck.
> **Numbers in this section marked `ILLUSTRATIVE` are modelled assumptions, not measured facts — never
> read them out as if they were evidence.** Say "ước tính theo giả định của chúng tôi" or give a range.

### [0:00 – 0:45] Act I: The Real-World Rail Crisis
> *"Judges, imagine it is Friday morning on Metro Line 1, Bến Thành – Suối Tiên. A leading car carries thousands of passengers. Deep within the auxiliary pneumatic system, an air discharge valve suffers a mechanical step degradation.*
>
> *Under conventional SCADA thresholds, nothing triggers. The train keeps running for another **33 hours and 52 minutes** until Saturday evening, when the Low Pressure Switch finally screams—forcing an emergency trackside evacuation, snarling the blue line, and incurring **€73,600 in delay penalties** and **€120,000 in catastrophic compressor rebuild costs**.*
>
> *Why did this happen? Because conventional alarms look at simple single-sensor limits, while modern ML dashboards drown control room dispatchers in false alerts. Today, we introduce **CompressorGuard**."*

### [0:45 – 1:30] Act II: The CompressorGuard Architecture
> *"CompressorGuard bridges the chasm between physical asset engineering and real-time operations command:*
> 1. **Zero Fake Telemetry:** 100% of the 1,516,948 sensor points stream from the peer-reviewed MetroPT-3 run records of a metro main air compressor. Not one value is synthesised.
> 2. **Physics-First Multi-Sensor Decision Engine:** It tracks differential pressure across loaded cycles and thermal drift, rejecting transient noise while isolating true mechanical degradation.
> 3. **Independent ML Corroborator:** An Isolation Forest acts strictly as an objective corroborator—never creating cases alone, but elevating operational confidence to HIGH when physics and ML reach consensus.
> 4. **Multi-Modal MongoDB Data Layer:** Telemetry streams into MongoDB Time Series collections with 1-second bucketing, while operational cases, audit events, and lead-time projections live in resilient document collections with strict single-active-case transactional boundaries.
> 5. **Datadog Unified Observability:** Every physical reading, anomaly score, and decision gate is piped through Datadog DogStatsD and APM Distributed Tracing."*

### [1:30 – 2:15] Act III: The Live Command Demonstration
*(Presenter switches to the live browser console at `http://localhost:8000/`)*
> *"Let's look at the live console:*
> - **00:33:07 — Transient Noise Rejection:** Notice this sudden pressure spike. Conventional anomaly tools panic. CompressorGuard recognizes insufficient regime persistence and suppresses case creation.
> - **09:50:39 — Confirmed Degradation Onset:** As the train enters the morning rush, our detector spots a 2.4 bar pressure loss sustained across loaded cycles. Case `#APU-INC-20200605-01` is automatically opened. Operational confidence: MEDIUM.
> - **10:15:00 — Multi-Sensor Consensus:** Thermal drift combines with ML Isolation Forest corroboration. Operational confidence upgrades to HIGH. The Decision Engine formally recommends mitigation.
> - **ActionGuard Pre-Flight Safety Policy:** Before the operator can push the button, ActionGuard verifies 5 safety criteria—ensuring safe speed, loaded regime, and cross-sensor consensus.
> - **Safe Mode Activation:** We branch into depot servicing.
> - **16:05:00 — Closed-Loop Recovery Verification:** Most platforms assume repairs succeed. CompressorGuard requires **5 consecutive loaded cycles** verifying DV pressure < 0.05 bar and oil temperature < 67°C before allowing the dispatcher to sign off and return the train to passenger service."*

### [2:15 – 3:00] Act IV: Business Impact & Observability ROI
> *"The bottom line for transit operators:*
> - **33h 52m Confirmed Intervention Window:** Depot technicians had an entire weekend day to service the valve in-depot without interrupting revenue service.
> - **€193,600 Direct Savings:** Eliminating line stoppage penalties and saving the compressor core from thermal seizure.
> - **Turnkey Audit Trail:** Every observation, decision, and dispatch override is recorded in an immutable MongoDB ledger and Datadog trace.
>
> *CompressorGuard transforms reactive firefighting into governed, auditable, high-confidence industrial operations. Thank you!"*

---

## The 5 Toughest Judge Questions & Proven Defenses

### Question 1: "Is your telemetry real, or did you generate fake sine waves?"
- **Defense:**
  > *"Every single data point in CompressorGuard originates 100% from the peer-reviewed MetroPT3 dataset recorded on Lisbon Metro's Linha Azul. We enforce this through our automated **Evaluation Gate 1 (Zero Fake Telemetry)**.
  > Furthermore, our architecture strictly isolates Layer A (Fleet Registry), Layer B (Raw Sensor Telemetry), and Layer C (Validation Reference Ground Truth). The engine has zero peek-ahead access to future labels—it operates strictly on causal sliding windows."*

### Question 2: "Why not just train an end-to-end Deep Learning / LLM model?"
- **Defense:**
  > *"In safety-critical rail operations, black-box models are unacceptable to dispatchers. At 00:33:07 in our dataset, a transient sensor excursion hits 65.4σ. An unrestrained ML model would trigger an emergency halt, causing passenger chaos.
  > CompressorGuard uses a **Physics-First Multi-Sensor Engine** backed by thermodynamic regime gating. Isolation Forest is used as an **independent corroborator**, not an autonomous case creator. Safe Mode is only unlocked when thermodynamic physics and statistical ML agree."*

### Question 3: "What prevents a rogue operator or script from shutting down a train at speed?"
- **Defense:**
  > *"We implemented **ActionGuard**, a transparent pre-flight safety policy boundary. Before any intervention branch can execute, ActionGuard evaluates 5 independent prerequisites:
  > 1. Active Case Verification (`lifecycle_state == INVESTIGATING`)
  > 2. Minimum Operational Confidence (`confidence == HIGH`)
  > 3. Decision Engine Policy Alignment (`action == EXECUTE_MITIGATION`)
  > 4. Regime Appropriateness (Rejects during high-speed transit)
  > 5. Corroboration Age (< 600s freshness window)
  > If any prerequisite fails, the system returns an HTTP 409 Conflict with exact forensic failure reasons."*

### Question 4: "How do you know the compressor actually recovered after maintenance?"
- **Defense:**
  > *"Most predictive maintenance platforms fire an alert and wash their hands of the outcome. CompressorGuard implements **Closed-Loop Recovery Verification (Evaluation Gate 5)**.
  > When post-maintenance telemetry begins at 16:05:00, our `RecoveryVerifier` monitors the compressor across the active `LOADED` regime. It requires exactly **5 consecutive healthy observations** satisfying physical baseline criteria (DV pressure < 0.05 bar, Oil temperature < 67°C). Case closure sign-off is cryptographically blocked until this verification completes."*

### Question 5: "How does your storage and observability architecture scale to a 500-train fleet?"
- **Defense:**
  > *"We architected for multi-modal scalability using MongoDB Atlas and Datadog:
  > - **MongoDB Time Series Collections:** Sensor points are ingested into compressed time series buckets partitioned by `asset_id`, with automatic TTL and `$setWindowFields` analytical aggregation.
  > - **MongoDB Document Collections:** `operational_cases` and `case_events` maintain rich, searchable incident ledgers with unique compound indexing enforcing at most 1 active case per asset.
  > - **Datadog Unified Observability:** We stream high-frequency metrics via DogStatsD (`compressorguard.telemetry.dv_pressure_bar`, `compressorguard.ml.physics_agreement`, `compressorguard.recovery.consecutive_observations`) and trace every pipeline tick, detector evaluation and Safe-Mode dispatch via `ddtrace` APM (`trace.compressorguard.detector.evaluate.duration`)."*

---

## Economic ROI & Rail Impact Matrix

> The first two rows are measured from the dataset and reproducible in the console. The three
> euro rows are **our modelled assumptions** (46-minute suspension, penalty and overhaul tariffs
> we invented as an order-of-magnitude case). Say so out loud if a judge asks for the source —
> defending a stated assumption scores better than defending a number that sounds published.

| Category | Without CompressorGuard | With CompressorGuard | Net Benefit |
|:---|:---|:---|:---|
| **Detection Timestamp** | June 6, 2020 at 19:42:49 (LPS Switch) | June 5, 2020 at 09:50:39 (DV Deviation) | **+33h 52m Early Warning** |
| **Operational Impact** | Line stoppage during revenue service | Scheduled maintenance in depot window | **Zero Revenue Disruption** |
| **Delay Penalties** | 46 mins line suspension: **€73,600** | On-time train replacement: **€0** | **€73,600 Saved** |
| **Asset Repair Cost** | Overhaul following thermal seizure: **€140,000** | Discharge valve replacement kit: **€20,000** | **€120,000 Saved** |
| **Total Event Value** | **-€213,600** | **-€20,000** | **€193,600 Net ROI** |

---

## Click-by-Click Live Demo Runbook

### Pre-Flight Setup
1. Open PowerShell or Terminal in `iot-hackathon`.
2. Launch the application:
   ```cmd
   demo.bat
   ```
   *(Or run `python run_demo.py`)*
3. Verify output:
   - Zero Fake Telemetry verified: `MetroPT3(AirCompressor).csv` loaded (1.5M rows).
   - Server active at `http://localhost:8000/`.
   - Browser automatically opens to `http://localhost:8000/`.

---

### Step 1: Monitor Baseline & Rejection of Transient Noise
- **Action:** In the top milestone navigation bar, click **"1. Transient Spike (00:33)"**.
- **Observation:**
  - Historical clock jumps to `2020-06-04 00:33:07`.
  - Discharge valve pressure spikes to `6.046 bar` (65.4σ).
  - **Key Talking Point:** Point to the Case Status badge: `NO ACTIVE CASE / HEALTHY`. Explain that CompressorGuard detects the spike but rejects it because transient duration (< 2 cycles) does not indicate structural valve failure.

---

### Step 2: Confirmed Degradation Onset
- **Action:** Click **"2. Degradation Onset (09:50)"**.
- **Observation:**
  - Clock updates to `2020-06-05 09:50:39`.
  - Discharge valve pressure drops by `2.4 bar` in `LOADED` regime.
  - Active Case Banner appears: **Case `#APU-INC-20200605-01` Opened**.
  - Lifecycle State: `DETECTED`. Health: `DEGRADED`. Confidence: `MEDIUM`.
  - Lead time counter initializes: `33h 52m until conventional LPS failure`.
  - **ActionGuard Status:** Attempting to click "Activate Safe Mode" shows pre-flight check warnings (Mitigation not yet recommended).

---

### Step 3: ML Corroboration & ActionGuard Clearance
- **Action:** Click **"3. ML Corroborated (10:15)"**.
- **Observation:**
  - Clock updates to `2020-06-05 10:15:00`.
  - Thermal Stress Detector spots oil temp drift exceeding +1.5°C/hr.
  - ML Isolation Forest returns anomaly score `0.78` (corroborated).
  - Confidence upgrades to **`HIGH (87%)`**.
  - Recommended Action changes to: **`EXECUTE_MITIGATION`**.
  - **ActionGuard Status:** All 5 safety gates turn green with checkmarks: `PASSED`.

---

### Step 4: Dispatcher Safe Mode Intervention
- **Action:** Click the illuminated button: **"Activate Depot Safe Mode"**.
- **Observation:**
  - Dialog confirms execution.
  - Lifecycle State transitions to: `MITIGATING`.
  - Stream automatically branches into depot maintenance protocol.
  - Datadog trace logs action dispatch with operator tag `DISPATCHER-0941`.

---

### Step 5: Closed-Loop Recovery Verification & Sign-Off
- **Action:** Click **"4. Post-Maintenance (16:05)"**.
- **Observation:**
  - Clock advances to `2020-06-08 16:05:00`.
  - Lifecycle State updates to: `VERIFYING_RECOVERY`.
  - Watch the live Recovery Progress Bar increment: `1/5 -> 2/5 -> ... -> 5/5 healthy LOADED observations`.
  - Once verified, the state badge shifts to green: `RESOLVED`.
  - The **"Sign-Off & Release Asset"** button enables.
- **Action:** Click **"Sign-Off & Release Asset"**.
- **Observation:**
  - Case `#APU-INC-20200605-01` closes.
  - Asset status returns to: `HEALTHY (Revenue Service Authorized)`.
  - The audit ledger gains the operator sign-off event with actor + source; open it with
    `curl -s localhost:8000/api/case/events`.
  - *There is deliberately no savings figure inside the product — the € table below is a modelled
    business case presented separately, not something the console claims.*

---

### Step 6: Observability & Ground Truth Inspection
- **Action:** Click the top-right button: **"Validation Reference Ground Truth"**.
- **Observation:**
  - A slide-out reference drawer opens displaying the official Lisbon Metro paper metadata:
    - *Scenario: Failure #3 (Air Production Unit Discharge Valve Leak)*
    - *Historical LPS Alert: June 6, 2020 at 19:42:49 UTC*
    - *CompressorGuard Early Detection: June 5, 2020 at 09:50:39 UTC*
    - *Verified Lead Time: 33 hours, 52 minutes, 10 seconds*
  - **Key Talking Point:** Show the honest badge `[ LIVE SIMULATION · HISTORICAL DATA ]` and explain that this ground truth is kept strictly in Layer C, proving the engine operated blind during the simulation.

---

## Evaluation Gates Verification Summary

| Gate | Description | Automated Test Command | Result |
|:---|:---|:---|:---:|
| **Gate 1** | **Zero Fake Telemetry** (100% historical CSV provenance) | `pytest tests/test_evaluation_gates.py::test_gate_1_zero_fake_telemetry` | **PASSED** |
| **Gate 2** | **Dual-Clock Semantics** (Event time physics + speed pacing) | `pytest tests/test_evaluation_gates.py::test_gate_2_dual_clock_semantics` | **PASSED** |
| **Gate 3** | **Multi-Sensor Decision Engine** (Physics-first + ML corroborator) | `pytest tests/test_evaluation_gates.py::test_gate_3_decision_engine_and_ml_role` | **PASSED** |
| **Gate 4** | **ActionGuard Safety Checks** (5 pre-flight policy criteria) | `pytest tests/test_evaluation_gates.py::test_gate_4_action_guard_safety_checks` | **PASSED** |
| **Gate 5** | **Closed-Loop Recovery Verification** (5/5 loaded healthy sign-off) | `pytest tests/test_evaluation_gates.py::test_gate_5_closed_loop_recovery` | **PASSED** |

To execute all 5 gates in a single standalone run:
```cmd
python scripts/verify_evaluation_gates.py
```
*(All 5 gates pass with 100% deterministic success).*
