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
  - **Alstom HealthHub:** Train downtime down to **-30%**, material cost down to **-20%**, recurring faults down to **-50%**; Dubai Tram passenger service performance +40%.
  - **Knorr-Bremse AirSupply Smart:** Embedded condition monitoring for compressors proves early temperature/pressure drift is industry standard for APU degradation.
  - **Singapore LTA & SMRT (2025):** S$2.4M fine on SMRT for East-West Line disruption + S$600k mandated investment in overhaul planning & spares.
  - **Hanoi Metro (Line 2A & 3 to 2026):** Cumulative >493,000 trips, 62.2M passengers across 23 trains. Jan 2026 mandate: mid-term overhaul for 13 Line 2A trains, prioritizing technology transfer and integrated maintenance. Oct 2026: 200 Alstom trainsets agreement.
  - **Hanoi Metro YN-007 Maintenance Manual:** [Scribd YN-007](https://www.scribd.com/document/788322712/YN-007-Chuong-7-H%E1%BB%87-th%E1%BB%91ng-ham-va-c%E1%BA%A5p-khi-S%E1%BB%95-tay-%C4%91ao-t%E1%BA%A1o) (Table 7-17, p. 7-60): Daily/monthly oil check, 6-month oil replenishment, 1-year cooler cleaning, pressure switch calibration, air filter and oil filter/gasket replacement.
  - **HCMC Metro Line 1 (2026):** >30.35M passengers. Critical inflection: contractor warranty expires late 2026, requiring local mastery of 90% maintenance technologies. July 2026: MAUR-GTEL MoU on AI/IoT/Digital Twin O&M for 200 km network.
  - **HCMC Metro Maintenance Plan UMRT L1:** [Scribd UMRT L1 Plan](https://www.scribd.com/document/845060878/UMRTL1-CP3-GL-O-M-PLN-00001-D-R0-Submission-of-Maintenance-Plan-Rev-D-en-VN-B%E1%BA%A3o-D%C6%B0%E1%BB%A1ng) (Table T5.1, p. 32-33): 1-week visual, 1-month performance check, 4-year depot overhaul.
  - **Knorr-Bremse SKP/VV120 CBM Formula:** 1,500 operating hours or max 12 months for oil/filter change: $T_{\text{due}} = \min((1500 - H_{\text{used}})/h_{\text{daily}}, 12 - M_{\text{elapsed}})$. Early thermal drift ($>67^\circ\text{C}$) dynamically shortens $T_{\text{due}}$.
  - **Cost Leverage (Reactive vs Planned):** Planned depot intervention €250–€800 (6.8M–22M VNĐ) vs. in-service failure €2,000–€35,000+ (55M–962M VNĐ).
  - **Deep Research Links:** [Part 1: Transit Economics & Vietnam](https://chatgpt.com/share/6ad32e70-51d8-83ec-9827-be65fabe85a9) | [Part 2: Compressor Manuals & CBM](https://chatgpt.com/share/6ad333ef-1e48-83ec-a42c-5d56d35ad3d0).

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

---

## 5. Architectural Gap Analysis: v2.3 Prototype vs. v3.0 Production-Ready UI/UX

- **Diagnostic Date:** 2026-10-11 (`docs/superpowers/specs/2026-10-11-prod-ready-ux-and-mechanism-design.md`).
- **Core Diagnosis:** Giao diện v2.3 hoàn thành 98/98 test theo tiêu chuẩn "Prototype Demo", nhưng không đạt tiêu chuẩn "Industrial Operations Command Console":
  1. **Header Clutter:** Nút nhảy mốc thời gian (`00:33`, `09:50`, `10:15`, `16:05`) nằm trên Header chính tạo cảm giác chuyển slide thay vì hệ thống SCADA/APM thực.
     - *v3.0 Fix:* Đưa toàn bộ transport controls và scenario selector vào **Replay Studio Drawer** (`Shift + S`).
  2. **Static Hardcoded Data:** ~90% số liệu đo lường (`2.1856 bar`, `74.97 °C`, `-0.016 bar`, và 5 dấu `✓ PASS` của ActionGuard) bị fix cứng trong HTML.
     - *v3.0 Fix:* 100% data-driven binding từ `/api/telemetry/window` và `/api/action/guard-status`.
  3. **Absence of Real-time Time Series Charts:** Không có strip charts trực quan hóa áp suất, nhiệt độ, dòng điện và vùng tải (`LOADED`).
     - *v3.0 Fix:* Tích hợp biểu đồ Chart.js đồng bộ đa kênh với shading trạng thái mang tải.
  4. **Lack of Human-in-the-Loop Governance:** Hệ thống tự động chuyển trạng thái thiếu thao tác điều độ.
     - *v3.0 Fix:* Bổ sung quy trình 4 bước: Acknowledge & Claim -> Forensic Note & Depot Work Order -> ActionGuard 5-check Safe Mode -> 5-Sample Loaded Verification & Root-Cause Sign-Off.
  5. **Decoupled Architecture:** Thay vì client gọi `POST /demo/tick` kéo dữ liệu, áp dụng kiến trúc *ThreatLens Decoupled Producer-Consumer* (Backend Stream Worker độc lập, UI quan sát thuần túy).
