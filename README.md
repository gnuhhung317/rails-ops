# RailOps VN — CompressorGuard

> **Industrial Operations Command Platform for Vietnam Urban Rail**
> *Metro Line 1 Bến Thành – Suối Tiên · Asset `APU-COMP-01` (Main Air Compressor) · MUGVN Hackathon 2026*
> **Core Promise:** Detect earlier → Prove why → Act safely → Verify recovery → Quantify value.

> **One-line thesis:** mỗi đoàn tàu metro có một máy nén khí cấp khí cho **phanh, treo khí và cửa** — nó hỏng là tàu **mất phanh và phải rút khỏi tuyến**. CompressorGuard phát hiện lỗi rò khí trên **1.516.948 điểm đo vật lý thật** sớm hơn cách konvensional **33h 52m**, đủ để điều độ viên kéo tàu về depot và sửa trong khoảng trống bảo trì đêm.
>
> **RailOps VN** là nền tảng; **CompressorGuard** là phân hệ lõi sống còn đã chạy thật end-to-end. Kiến trúc và kế hoạch triển khai: **[docs/RAILOPS_VN_PLATFORM_BLUEPRINT.md](docs/RAILOPS_VN_PLATFORM_BLUEPRINT.md)**.

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

- 🚉 **[RailOps VN Platform Blueprint](docs/RAILOPS_VN_PLATFORM_BLUEPRINT.md):** Vấn đề đường sắt Việt Nam có thật, định vị platform ⊃ subsystem, module IoT, kiến trúc realtime MongoDB/Datadog, rollout 4 phase tới ĐSCT Bắc–Nam, ánh xạ rubric 30/30/30/10.
- 🏛️ **[System & Live Stream Architecture (v3.0)](docs/ARCHITECTURE.md):** Kiến trúc luồng Live tách rời (Decoupled Producer–Pipeline–Storage–Observer) theo chuẩn ThreatLens AI.
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

CompressorGuard includes 96+ automated tests covering domain contracts, detectors, fusion, state machine, ActionGuard, MongoDB persistence, Datadog observability, and API integration:

```bash
# Run the 5 Evaluation Gates
pytest tests/test_evaluation_gates.py -v

# Run the full test suite
pytest -q
```

---

## 🏛️ System Architecture (v3.0 Decoupled Live Stream)

```text
[1. INDEPENDENT PRODUCER]
MetroPT-3 Historical Stream (1,516,948 rows · Dual-Clock Background Stream Worker / CLI Streamer)
       │  (The Dashboard does NOT trigger telemetry ticks)
       ▼
[2. REAL-TIME DETECTION & CORRELATION PIPELINE]
       ├── Operating Regime Classifier (STANDBY / LOADED / UNLOADED / STARTING)
       ├── Physical Detectors (Pressure Step + Thermal Stress Drift + Temporal Filter)
       ├── Independent ML Corroborator (Isolation Forest on 5 LOADED features)
       ├── Evidence Fusion & Deterministic Decision Engine
       └── Case Lifecycle Correlator (Enforces Single Active Case per Asset)
       │
       ▼
[3. MULTIMODAL STORAGE & OBSERVABILITY]
       ├── MongoDB Atlas (`measurements` Time-Series + `anomaly_signals` + `incidents` + `case_events`)
       └── Datadog Unified Observability (DogStatsD Custom Metrics + APM Distributed Tracing)
       │
       ▼
[4. OBSERVATIONAL & RESPONSE CONSOLE (Pure Observer + Human-in-the-Loop Actions)]
       ├── DashboardQueryAdapter (Timeframe Windows: 5m / 15m / 1h / 6h / all)
       ├── Live Chart.js Canvases (DV_pressure, Oil_temp, Motor_current, IF Score)
       ├── Dual-Layer View (Correlated Cases vs. Raw Telemetry & Suppressed Signals)
       └── Operator Actions (Acknowledge, Mark False Positive, ActionGuard Safe Mode, 5/5 Recovery Sign-off)
```

---

## 👥 Hackathon Team & Credits
- **Project:** CompressorGuard
- **Hackathon:** MUGVN Hackathon 2026 (MongoDB + Datadog)
- **Target Application:** RailOps VN · Metro Line 1 Bến Thành – Suối Tiên (HURC1) — fleet hierarchy is an *illustrative* Vietnamese mapping of the public MetroPT-3 compressor dataset (see `docs/RAILOPS_VN_PLATFORM_BLUEPRINT.md` §4.1).
- **Dataset:** MetroPT-3 Benchmark (Air Compressor Predictive Maintenance Dataset)
