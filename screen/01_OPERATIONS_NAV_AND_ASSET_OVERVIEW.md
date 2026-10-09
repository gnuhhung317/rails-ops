# SCREEN 01 — OPERATIONS LANDING PAGE & FLEET OVERVIEW
> **Mục tiêu:** Cung cấp góc nhìn bao quát toàn bộ hạm đội tàu (`Fleet Hierarchy`), trạng thái hoạt động thực tế của từng tài sản (`Asset: APU-COMP-01`), và **trình diễn trực tiếp tính năng chống báo động giả (Noise Rejection)** tại mốc thời gian `00:33:07`.
> **Định vị:** Operations Landing Page — Nơi chuyển ngữ câu chuyện từ cảm biến máy móc sang an toàn vận tải hành khách.

---

## 1. BỐ CỤC GIAO DIỆN (ASCII WIREFRAME)

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ COMPRESSORGUARD // OPERATIONS COMMAND CONSOLE         [ LIVE SIMULATION · HISTORICAL DATA ]           │
│ Operator: DISPATCHER-0941                             Scenario: Failure #3 (MetroPT-3 Telemetry)       │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [1 MONITORED ASSET]    [0 ACTIVE CASES]    [1 ASSET OBSERVING]    [REPLAY: FAILURE #3 (2020-06-04)]    │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                        │
│  FLEET ASSET HIERARCHY (CÂY PHÂN CẤP TÀI SẢN VẬN HÀNH)                                                 │
│  ────────────────────────────────────────────────────────────────────────────────────────────────────  │
│  ▼ 🏢 FLEET: Linha Azul (Lisbon Metro Fleet)                                                           │
│     └── ▼ 🚆 TRAIN-302 (Tàu chở khách thương mại — Tuyến Xanh)                                         │
│            └── ▼ ⚙️ APU (Cụm cấp khí nén Air Production Unit)                                          │
│                   └── 🔴 APU-COMP-01 (Máy nén khí Piston #01)                                          │
│                        • Vận hành: LOADED (Current: 6.82 A | Van xả đóng)                              │
│                        • Trạng thái: [🟢 HEALTHY] (Giám sát nền)                                       │
│                        • Hồ sơ sự cố: [ NONE ] (Không có tình huống khẩn cấp)                          │
│                                                                                                        │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ 👁️ SIGNAL OBSERVATION WATCHLIST (PHÒNG NGỪA BÁO ĐỘNG ẢO - NOISE REJECTION DEMO)                        │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                        │
│  Event Time: 2020-06-04 00:33:07 UTC                Status: [🟡 OBSERVING TRANSIENT EXCURSION]         │
│  Simulation Speed: [ 1x ] [ 10x ] [ 60x ▶ ]          Sampling: Preserving historical event delta       │
│                                                                                                        │
│  ┌─────────────────────────────────┐   ┌─────────────────────────────────┐   ┌──────────────────────┐  │
│  │ DISCHARGE PRESSURE (DV)         │   │ THERMAL DRIFT (OIL_TEMP)        │   │ MULTIVARIATE ML (IF) │  │
│  │ Observed: 0.52 bar (+4.21σ)     │   │ Observed: 56.10 °C (+0.32σ)     │   │ Score: 0.182 (<0.35) │  │
│  │ Source:   PressureAnomalyDet    │   │ Source:   ThermalDriftDetector  │   │ Role:  Corroboration │  │
│  │ Status:   TRANSIENT SPIKE       │   │ Status:   NORMAL BASELINE       │   │ Status: NORMAL       │  │
│  └─────────────────────────────────┘   └─────────────────────────────────┘   └──────────────────────┘  │
│                                                                                                        │
│  Persistence Monitor: [ █░░ ] 1/3 Loaded Cycles (Unconfirmed - Spike lasted only 10 seconds)           │
│                                                                                                        │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ ℹ️ SYSTEM REASONING & ANTI-FATIGUE POLICY:                                                       │  │
│  │ "A transient pressure jump of 0.52 bar was detected at 00:33:07 UTC.                             │  │
│  │  However, thermal drift is absent (+0.32σ) and Isolation Forest confirms multivariate normality. │  │
│  │  CASE CREATION IS SUPPRESSED. The asset remains HEALTHY to prevent operator alarm fatigue."       │  │
│  └──────────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Ý NGHĨA KỸ THUẬT & TRẢI NGHIỆM TẠI MÀN HÌNH NÀY

### 2.1 Cây phân cấp tài sản: Fleet là xương sống nghiệp vụ
- Khác với dashboard hiển thị sensor phẳng, cây phân cấp `Fleet -> Train -> APU -> Compressor` trả lời câu hỏi của giám khảo: *"Cảm biến này đang ảnh hưởng đến cái gì trong thực tế vận hành?"*.
- Khi sự cố bùng phát sau này, người điều độ không chỉ nhìn thấy áp suất nhảy vọt, mà nhìn thấy ngay: **Đoàn tàu chở khách Train #302 đang có nguy cơ dừng khẩn cấp giữa hầm**.

### 2.2 Loại bỏ chỉ số giả mạo: "Fleet Health 98%" biến mất
- Con số `Fleet Health: 98%` trước đây bị loại bỏ triệt để vì không có công thức xác thực trong backend và gây nghi ngờ cho giám khảo.
- Thay vào đó là các **Bộ đếm vận hành trung thực (Operational Counters)**:
  * Trạng thái quan sát (00:33): `1 MONITORED ASSET | 0 ACTIVE CASES | 1 ASSET OBSERVING | REPLAY: FAILURE #3`.
  * Khi sự cố được xác nhận (09:50): `1 MONITORED ASSET | 1 ACTIVE CASE | 1 TRAIN AT RISK | 33h 52m CONFIRMED INTERVENTION WINDOW`.

### 2.3 Khoảnh khắc "Đắt Giá" trong Demo (00:33:07 Noise Rejection)
- Thay vì nhảy cóc qua mốc 00:33 bằng nút bấm giả tạo, bộ mô phỏng chạy liên tục qua thời điểm 00:33:07.
- Operator và giám khảo trực tiếp chứng kiến xung áp suất 0.52 bar xuất hiện, hệ thống chuyển sang `OBSERVING`, đếm `1/3 Cycles`, nhận thấy nhiệt độ dầu không đổi và ML bình thường $\rightarrow$ **Tự động ngăn chặn tạo Case**.
- Đây là minh chứng đanh thép rằng hệ thống liên tục suy luận thời gian thực, không phải là một storyboard cứng nhắc.

---

## 3. RÀNG BUỘC DỮ LIỆU (DATA BINDING CONTRACT — `GET /api/operations`)

```json
{
  "fleet_id": "FLEET-METRO-AZUL",
  "fleet_name": "Linha Azul Fleet",
  "summary": {
    "monitored_assets": 1,
    "active_cases": 0,
    "assets_observing": 1,
    "trains_at_risk": 0,
    "replay_scenario": "Failure #3"
  },
  "asset_hierarchy": {
    "train_id": "TRAIN-302",
    "subsystem": "Air Production Unit (APU)",
    "asset_id": "APU-COMP-01",
    "asset_health": "HEALTHY",
    "operating_regime": "LOADED",
    "active_case_id": null,
    "operational_risk": "None — Nominal operation under continuous monitoring"
  },
  "signal_observation": {
    "status": "OBSERVING",
    "event_time": "2020-06-04T00:33:07Z",
    "primary_signal": "dv_pressure",
    "observed_value": 0.52,
    "sigma_deviation": 4.21,
    "persistence": {
      "consecutive_samples": 1,
      "required_samples": 3,
      "confirmed": false
    },
    "reasoning": "Transient excursion observed — thermal drift absent and ML corroborates normality. Case creation suppressed."
  },
  "simulation": {
    "mode": "LIVE_SIMULATION",
    "scenario": "Failure #3 (MetroPT-3)",
    "event_time": "2020-06-04T00:33:07Z",
    "speed": "60x",
    "status": "RUNNING"
  }
}
```
