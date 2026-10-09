# CompressorGuard

> **Industrial Operations Command Platform for Urban Transit Rail**  
> *Lisbon Metro (Linha Azul) · Asset `APU-COMP-01` · MUGVN Hackathon 2026*  
> **Core Promise:** Detect earlier → Prove why → Act safely → Verify recovery → Quantify value.

[![MongoDB Atlas Multi-Modal](https://img.shields.io/badge/MongoDB-Time--Series%20%2B%20Document-green.svg)](https://www.mongodb.com/atlas)
[![Datadog Unified Observability](https://img.shields.io/badge/Datadog-APM%20Tracing%20%2B%20DogStatsD-purple.svg)](https://www.datadoghq.com)
[![Zero Fake Telemetry](https://img.shields.io/badge/Evaluation%20Gate%201-Zero%20Fake%20Telemetry-blue.svg)](docs/PITCH_DECK_AND_DEMO_RUNBOOK.md)
[![Closed-Loop Recovery](https://img.shields.io/badge/Evaluation%20Gate%205-5%2F5%20Verified%20Recovery-teal.svg)](docs/PITCH_DECK_AND_DEMO_RUNBOOK.md)

---

## 🚀 1-Click Turnkey Demo Launcher

Launch the complete full-stack platform (FastAPI backend + Vanilla SPA Command Console + Replay Engine + Browser Auto-Open) with a single command:

### On Windows:
Double-click `demo.bat` or run in terminal:
```cmd
demo.bat
```

### On macOS / Linux / Cross-Platform:
```bash
python run_demo.py
```

The server initializes at `http://localhost:8000/` and opens your default browser automatically.

- **Operations Command Console:** `http://localhost:8000/` or `http://localhost:8000/console`
- **Interactive OpenAPI Documentation:** `http://localhost:8000/docs`
- **Health Probe:** `http://localhost:8000/health`
- **Prometheus / Datadog Metrics:** `http://localhost:8000/metrics`

---

## 🏆 Key Achievements & Proven Impact

| Metric | Measured Result | Operational Significance |
|:---|:---|:---|
| **Early Warning Lead Time** | **33 hours 52 minutes** | Onset at `09:50:39 June 5` vs. Low Pressure Switch alert at `19:42:49 June 6` |
| **Quantified Economic Value** | **€193,600** ($210,000+) | €73,600 delay penalty avoidance + €120,000 catastrophic compressor overhaul avoidance |
| **False Positive Rejection** | **00:33:07 transient noise suppressed** | 65.4σ transient pressure excursion rejected; zero false line stoppages |
| **ActionGuard Safety Policy** | **5 transparent pre-flight checks** | Blocks premature intervention (HTTP 409) until multi-sensor & ML consensus is verified |
| **Closed-Loop Recovery** | **5/5 consecutive LOADED cycles** | Verifies physical recovery (<0.05 bar DV pressure, <67°C oil temp) before dispatch sign-off |
| **Data Integrity Standard** | **100% Real Historical Provenance** | Streamed from 1,516,948 rows of peer-reviewed MetroPT3 data; zero synthetic data |

---

## 🧭 Documentation Navigator

- 🎤 **[Pitch Deck & Judge Demo Runbook](docs/PITCH_DECK_AND_DEMO_RUNBOOK.md):** 3-minute pitch script, defense against the 5 toughest judge questions, and step-by-step click guide.
- 💶 **[Rail Economics & Value Model](docs/RAIL_ECONOMICS_AND_VALUE_MODEL.md):** Formal mathematical models for delay penalties, asset overhaul avoidance, and ROI formulas.
- 📐 **[Screen & UX Architecture Specs](screen/01..07.md):** Detailed specs for Fleet Overview, Active Case Workspace, ActionGuard Drawer, and Ground Truth Reference.
- 📖 **[Master Context & Architecture SSOT](master_context.md):** Complete architectural Single Source of Truth, persona definition, and subsystem designs.

---

## 🛡️ The 5 Industrial Evaluation Gates

CompressorGuard provides an automated verification runner ensuring zero regression across the 5 core industrial gates:

```bash
python scripts/verify_evaluation_gates.py
```

| Evaluation Gate | Requirement | Automated Test |
|:---|:---|:---|
| **Gate 1: Zero Fake Telemetry** | 100% telemetry sourced from historical CSV; strict Layer A/B/C separation | `pytest tests/test_evaluation_gates.py::test_gate_1_zero_fake_telemetry` |
| **Gate 2: Dual-Clock Semantics** | Historical event_time preserved; simulation pacing respects speed multiplier | `pytest tests/test_evaluation_gates.py::test_gate_2_dual_clock_semantics` |
| **Gate 3: Multi-Sensor Decision** | Physics-first multi-sensor engine; ML acts strictly as independent corroborator | `pytest tests/test_evaluation_gates.py::test_gate_3_decision_engine_and_ml_role` |
| **Gate 4: ActionGuard Safety** | Rejects premature actions (HTTP 409); verifies 5 pre-flight criteria | `pytest tests/test_evaluation_gates.py::test_gate_4_action_guard_safety_checks` |
| **Gate 5: Closed-Loop Recovery** | Requires 5 consecutive healthy LOADED cycles before release sign-off | `pytest tests/test_evaluation_gates.py::test_gate_5_closed_loop_recovery` |

---

## 🧪 Running the Full Automated Test Suite

CompressorGuard includes 96+ automated tests covering domain contracts, detectors, fusion, state machine, ActionGuard, MongoDB persistence, Datadog observability, and Web Console integration:

```bash
# Run the 5 Evaluation Gates
pytest tests/test_evaluation_gates.py -v

# Run the full test suite
pytest -q
```

---

## 🏛️ System Architecture

```text
MetroPT-3 Replay Stream (1,516,948 rows · Lisbon Metro Linha Azul)
       │
       ├── Operating Regime Classifier (STANDBY / LOADED / UNLOADED / STARTING)
       │
       ├── Physical Detectors (Pressure Step + Thermal Stress Drift + Temporal Filter)
       │        │
       │        └── Independent ML Corroborator (Isolation Forest, Anomaly Score 0..1)
       │
       ▼
Evidence Fusion Engine (Deterministic Evidence State & Sensor Provenance)
       │
       ▼
Decision Engine (Operational Confidence: LOW / MEDIUM / HIGH)
       │
       ├── ActionGuard (5 Pre-Flight Safety Policy Verifications)
       │        │
       │        └── Safe Mode Intervention Branch (Depot Maintenance Stream)
       │
       ▼
RecoveryVerifier (5 Consecutive Healthy LOADED Observation Cycles)
       │
       ├── Operations Command Console (Vanilla Modern SPA, Dual-Clock Pacing, Live Audit Ledger)
       ├── MongoDB Atlas (Time Series Collections + Document Case Ledger + Transactional Integrity)
       └── Datadog Unified Observability (DogStatsD Custom Metrics + APM Distributed Tracing)
```

---

## 👥 Hackathon Team & Credits
- **Project:** CompressorGuard
- **Hackathon:** MUGVN Hackathon 2026 (MongoDB + Datadog)
- **Target Application:** Lisbon Metro (Metropolitano de Lisboa) · Linha Azul
- **Dataset:** MetroPT-3 Benchmark (Air Compressor Predictive Maintenance Dataset)
