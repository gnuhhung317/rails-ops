# SCREEN 04 — CASE INVESTIGATION WORKBENCH: WHY? (4-SIGNAL EVIDENCE PROVENANCE MATRIX)
> **Mục tiêu:** Trả lời câu hỏi thứ hai của chuyên viên vận hành trong **3-Pane Case Investigation Workbench**: **"Tại sao hệ thống khẳng định đây là hư hỏng cơ học thật chứ không phải nhiễu cảm biến?"**  
> **Nguyên tắc v3.0:** **Dynamic Evidence Provenance > Static Cards** — Mọi thẻ bằng chứng và biểu đồ đa biến đều được render động từ `GET /api/evidence` và `GET /api/telemetry/window` (hiển thị trạng thái thực tế của cả 4 detector ở từng chu kỳ 10 giây, kèm vai trò kiểm chứng độc lập của **Isolation Forest trên 5 features có tải**).

---

## 1. BỐ CỤC GIAO DIỆN (3-PANE WORKBENCH — VIEW 2: WHY? EVIDENCE PROVENANCE)

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ WORKBENCH // APU-INC-20200605-01 · Train #302 (APU-COMP-01)   [PHASE: INVESTIGATING]  [ACKED: DISP-0941 ✓]  │
│ Sub-View Focus: [1. WHAT CHANGED?]  [★ 2. WHY? (EVIDENCE)]  [3. PLAYBOOK & GUARD]  [4. RECOVERY]  [5. AUDIT] │
├──────────────────────────────────────────┬───────────────────────────────────────────┬───────────────────────┤
│ LEFT & CENTER-LEFT PANE (5 COLS):        │ CENTER-RIGHT PANE (4 COLS):               │ RIGHT PANE (3 COLS):  │
│ 4-SIGNAL DYNAMIC EVIDENCE MATRIX         │ 5-FEATURE ISOLATION FOREST & CAUSAL CHAIN │ PROVENANCE & POLICY   │
│ (Bound to GET /api/evidence)             │ (Bound to GET /api/telemetry/window)      │ AUDIT INSPECTOR       │
│ ──────────────────────────────────────── │ ───────────────────────────────────────── │ ───────────────────── │
│ [CARD A] DISCHARGE PRESSURE (PRIMARY)    │ MULTIVARIATE CORROBORATION (5 FEATURES):  │ SELECTED DETECTOR:    │
│ • Live Reading: 2.1856 bar  [CRITICAL]   │ • Model: IsolationForestDetector          │ IsolationForestDet    │
│ • Deviation:    ▲ +23.75σ (Base: -0.016) │ • Input: 5 telemetry features in LOADED   │                       │
│ • Provenance:   PressureAnomalyDetector  │   regime (DV, H1, Oil_temp, Current, TP3) │ • Role:               │
│ • Method:       Loaded-regime baseline   │ • Live Score: 0.382 (Threshold: > 0.350)  │   Independent         │
│                                          │                                           │   Corroboration Only  │
│ [CARD B] COMPRESSOR OIL TEMPERATURE      │ [Rolling IF Anomaly Score vs 0.35 Bound]  │   (Never opens a case │
│ • Live Reading: 74.97 °C    [SEVERE]     │  0.45 ┤                   ╭─────────────  │   on its own)         │
│ • Deviation:    ▲ +5.71σ (Base: 54.98°C) │  0.35 ┤───────────────────┼─────────────  │                       │
│ • Provenance:   ThermalStressDetector    │  0.15 ┤───────────────────╯               │ • Regime Gate:        │
│ • Method:       Loaded thermal drift     │       09:40             10:15 (Corrob.)   │   Evaluated strictly  │
│                                          │                                           │   when Motor_current  │
│ [CARD C] TEMPORAL STEP PERSISTENCE       │ THERMODYNAMIC CAUSAL CHAIN (LIVE STATE):  │   > 0.50 A (LOADED)   │
│ • Live State:   3 / 3 Cycles [CONFIRMED] │  [1. Desiccant Drain Valve Stuck Open]    │                       │
│ • Step Delta:   +2.202 bar (> 0.50 bar)  │      └──► [2. DV Pressure +23.75σ Breach] │ • Consensus Status:   │
│ • Provenance:   TemporalStepDetector     │           └──► [3. Continuous Over-Pump]  │   3 Physical Signals  │
│ • Method:       Consecutive loaded cycles│                └──► [4. Oil Temp +5.71σ]  │   + ML Corroboration  │
│                                          │                     └──► [5. H1 Collapse] │   => HIGH CONFIDENCE  │
│ [CARD D] MULTIVARIATE ISOLATION FOREST   │                                           │                       │
│ • Live Score:   0.382       [CORROBORATED│                                           │ [👉 Proceed to        │
│ • Threshold:    0.350 (5 features LOADED)│                                           │  Playbook & Guard]    │
└──────────────────────────────────────────┴───────────────────────────────────────────┴───────────────────────┘
```

---

## 2. CƠ CHẾ HIỂN THỊ BẰNG CHỨNG ĐỘNG & VAI TRÒ CHUẨN MỰC CỦA ML

### 2.1. Hiển Thị Động Theo Từng Giai Đoạn Thực Tế (Không Hardcode 4 Thẻ Cố Định)
- Ở mốc **`09:50:39 UTC` (`DETECTED`)**:
  - `Card A (PressureAnomalyDetector)` hiển thị `CRITICAL` (`+23.75σ`).
  - `Card C (TemporalStepDetector)` hiển thị `CONFIRMED` (`3/3 Loaded Cycles`).
  - `Card D (IsolationForestDetector)` hiển thị trạng thái thực tế đang chờ vượt ngưỡng kiểm chứng (`AWAITING_CORROBORATION`), giúp chuyên viên hiểu vì sao hồ sơ đang ở `DETECTED` và `ActionGuard` chưa mở khóa lệnh can thiệp.
- Ở mốc **`10:15:00 UTC` (`INVESTIGATING`)**:
  - `Card B (ThermalStressDetector)` chuyển sang `SEVERE` (`74.97 °C`, `+5.71σ`).
  - `Card D (IsolationForestDetector)` vượt ngưỡng `0.350` (đạt `0.382` trên **5 đặc trưng** trong chế độ `LOADED`: `DV_pressure`, `H1`, `Oil_temp`, `Motor_current`, `TP3`) và chuyển sang `CORROBORATED`.

### 2.2. Xuất Xứ Bằng Chứng Minh Bạch (`Provenance Metadata`)
Mỗi thẻ bằng chứng trong `evidence_pack` bắt buộc hiển thị 4 trường truy xuất nguồn gốc:
- `source`: Tên lớp Detector sinh ra tín hiệu (`PressureAnomalyDetector`, `ThermalStressDetector`, `TemporalStepDetector`, `IsolationForestDetector`).
- `method`: Phương pháp toán lý áp dụng.
- `event_time`: Mốc thời gian lịch sử của mẫu đo (`timestamp`).
- `regime`: Chế độ tải tại thời điểm đánh giá (`LOADED`).

---

## 3. RÀNG BUỘC DỮ LIỆU ĐỘNG (`GET /api/evidence`)

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
        "event_time": "2020-06-05T10:15:00Z",
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
        "event_time": "2020-06-05T10:15:00Z",
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
        "method": "5-feature boundary evaluation on LOADED baseline (5 telemetry signals)",
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
