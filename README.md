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

### Install first (Python 3.12; `run_demo.py` now refuses to start without it)
```bash
python -m pip install -r requirements.txt
```
Versions are pinned to the exact set this build was verified against. `paho-mqtt` is the only
entry not exercised here (no broker in the test environment) — see the note in `requirements.txt`.

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

### Data source: works from a clean clone, no manual step

`dataset/MetroPT3-demo-slice.csv` **is committed** — 286,855 real MetroPT-3 rows (39.5 MB),
cut by `scripts/build_demo_slice.py` from the original file. It keeps the whole
Isolation-Forest baseline month (Feb 2020) plus every scenario window at the original
10 s resolution, so `git clone` → `pip install` → `python run_demo.py` is a complete demo.

That is a claim, not a hope: `python scripts/verify_golden_path_evidence.py` run with
`TELEMETRY_CSV` pointed at the slice produces a `docs/golden_path_evidence_artifact.json`
**byte-identical** to the one produced from the full file (same milestones, same ML scores).
No row is generated, interpolated or reordered — striding was tested and rejected because it
changed ML verdicts, so the baseline month is kept at full resolution.

For the full 1,516,948-row file (208 MB, not in git — GitHub would reject it):

1. Download **MetroPT-3** (Air Compressor Predictive Maintenance Dataset), published in
   *Scientific Data* 2022 — [doi:10.1038/s41597-022-01877-3](https://www.nature.com/articles/s41597-022-01877-3).
2. Save it as `dataset/MetroPT3(AirCompressor).csv` (exact filename — parentheses included). It is
   preferred automatically over the slice; `TELEMETRY_CSV` overrides either way.
3. Expect **1,516,948** rows; Gate 1 prints the count of whichever file is loaded.

If neither file is present, the replay engine stops with the expected paths and the DOI printed —
it does not fail silently and it never substitutes synthetic data.

**Optional but recommended for a judge-grade run:**

| Prerequisite | Env var | Effect if unset |
|:---|:---|:---|
| MongoDB (Atlas or local) | `MONGODB_URI` | Falls back to the in-memory repository; Time Series + `$setWindowFields` demo not visible. `mongodb+srv://…` (Atlas) works directly — `dnspython` is pinned for it, and the verified run used a real `mongod 8.0.37`. `run_demo.py` prints which backend it actually got: `REAL MongoDB Atlas v8.0.37` vs `IN-MEMORY EMULATION`. Put the URI in `.env` (gitignored), never in a commit. |
| Datadog Agent | `DD_API_KEY`, agent on `:8125`/`:8126` | Metrics/traces are dropped with a warning; app still runs. Verified live against `agent 7.85.2`: `agent dogstatsd-stats` lists `compressorguard.telemetry.*` / `ml.*` / `incident.*` tagged `service:compressorguard env:hackathon-2026`, and the APM receiver logs `success:true` for Python spans. |
| MQTT broker (IoT edge path) | `MQTT_BROKER` | Producer falls back to its store-and-forward buffer and keeps publishing to storage. Verified against `eclipse-mosquitto:2` — `mosquitto_sub -t "railops/#" -v` receives the real MetroPT-3 frames on `railops/metro-line-1/APU-COMP-01/telemetry`. |

### Independent telemetry producer (the dashboard never pulls data)

```bash
python scripts/stream_telemetry.py --scenario failure_3 --speed 300 --hours 4
python scripts/stream_telemetry.py --mode remote --play --speed 300   # steer a running server

# the edge path, broker included:
MQTT_BROKER=tcp://localhost:1883 python scripts/stream_telemetry.py --scenario failure_3 --speed 300 --hours 1
```

Writes to MongoDB as a Time Series document (`timestamp` as a BSON datetime plus the `metadata`
metaField) and publishes a separate JSON frame to MQTT — the two shapes are deliberately not shared,
because mongod rejects the bus payload's ISO strings and the emulator does not.


- **Operations Command Console:** `http://localhost:8000/` or `http://localhost:8000/console`
- **Interactive OpenAPI Documentation:** `http://localhost:8000/docs`
- **Health Probe:** `http://localhost:8000/health`
- **Prometheus / Datadog Metrics:** `http://localhost:8000/metrics`

---

## 🏆 Key Achievements & Proven Impact

| Metric | Measured Result | Operational Significance |
|:---|:---|:---|
| **Early Warning Lead Time** | **33 hours 52 minutes** | Onset at `09:50:39 June 5` vs. Low Pressure Switch alert at `19:42:49 June 6` |
| **Avoided Cost (Scenario Model)** | **€193,600** ($210,000+) *projected, not realized* | €73,600 delay penalty + €120,000 catastrophic overhaul avoided — our explicit assumptions, parameterised in [docs/RAIL_ECONOMICS_AND_VALUE_MODEL.md](docs/RAIL_ECONOMICS_AND_VALUE_MODEL.md); no money figure is claimed inside the product |
| **False Positive Rejection** | **00:33:07 transient noise suppressed** | 65.4σ transient pressure excursion rejected; zero false line stoppages |
| **ActionGuard Safety Policy** | **5 transparent pre-flight checks** | Blocks premature intervention (HTTP 409) until multi-sensor & ML consensus is verified |
| **Closed-Loop Recovery** | **5/5 consecutive LOADED cycles** | Verifies physical recovery (<0.05 bar DV pressure, <67°C oil temp) before dispatch sign-off |
| **Data Integrity Standard** | **100% Real Historical Provenance** | Streamed from 1,516,948 rows of peer-reviewed MetroPT3 data; zero synthetic data |

---

## 🧭 Documentation Navigator

- 🎬 **[Demo Video Script](docs/DEMO_VIDEO_SCRIPT.md):** Kịch bản quay video theo từng shot, 10 shot / 5 phút, ánh xạ shot → tiêu chí chấm, 5 lỗi sẽ khiến video bị nhìn là "demo đồ chơi".
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

### Operator journey against a live server

The five gates above test the engine in-process. To prove the same chain through the
**HTTP surface the Operations Console actually uses** — including that a premature
Safe Mode click is refused with `HTTP 409` while the asset stays in revenue service —
start the console and run:

```bash
python run_demo.py                                              # terminal 1
CONSOLE_BASE_URL=http://localhost:8000 \
  python scripts/verify_console_journey.py                      # terminal 2
```

It walks all four Human-in-the-Loop steps (Acknowledge → Forensic Note + Depot Work
Order → ActionGuard 5/5 + Safe Mode → 5-sample Recovery + Root-Cause Sign-Off) and
asserts 23 checks: lead window, evidence pack, rolling statistics, dual-clock
timestamps on the wire, and the append-only `case_events` ledger.

---

## 🧪 Running the Full Automated Test Suite

CompressorGuard ships **119 collected automated tests** (exact count from `pytest --collect-only -q`), covering domain contracts, detectors, fusion, the state machine, ActionGuard, MongoDB persistence, Datadog observability *and the Datadog dashboard/monitor JSON itself*, the MQTT edge publisher **including the mongod-shaped storage document that a real Time Series collection demands**, dataset provisioning for a clean clone, and the operator journey:

> Note: the full suite replays the real 1,516,948-row CSV, so it takes several minutes. For a
> 60-second evidence moment, prefer the two verifiers below — they assert the same guarantees
> against live artefacts rather than against fixtures.

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
