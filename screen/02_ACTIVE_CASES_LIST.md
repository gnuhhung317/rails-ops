# SCREEN 02 — ACTIVE CASES LIST
> **Mục tiêu:** Quản lý danh mục các hồ sơ sự cố vận hành đang hoạt động (`Active Cases`). Thực thi bất biến chuẩn công nghiệp Siemens Senseye: **"Tối đa một Active Case trên một Asset tại một thời điểm"** và kết nối trực tiếp với cây phân cấp tài sản hạm đội.

---

## 1. BỐ CỤC GIAO DIỆN (ASCII WIREFRAME)

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ COMPRESSORGUARD // OPERATIONS COMMAND CONSOLE         [ LIVE SIMULATION · HISTORICAL DATA ]           │
│ Operator: DISPATCHER-0941                             Scenario: Failure #3 (MetroPT-3 Telemetry)       │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [1 MONITORED ASSET]    [1 ACTIVE CASE] ⚠️    [1 TRAIN AT RISK]    [33H 52M CONFIRMED LEAD WINDOW]      │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                        │
│  ACTIVE OPERATIONAL CASES (HỒ SƠ SỰ CỐ ĐANG XỬ LÝ)                                                     │
│  ────────────────────────────────────────────────────────────────────────────────────────────────────  │
│  Bất biến Siemens: "Chỉ một Case mở trên một Asset. Nghiệm thu phục hồi xong mới đóng Case và trả tàu."│
│                                                                                                        │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ CASE ID: CASE-20200605-01   [🔴 CRITICAL]   [PHASE: CONFIRMED]      ⏱️ LEAD WINDOW: 33H 52M       │  │
│  ├──────────────────────────────────────────────────────────────────────────────────────────────────┤  │
│  │ Asset Hierarchy: Metro Fleet (Linha Azul) ──► Train #302 ──► APU ──► APU-COMP-01                 │  │
│  │ Title:           Severe Discharge Valve Degradation with Thermal Drift                           │  │
│  │ Detection:       2020-06-05 09:50:39 UTC (Confirmed across 3 loaded cycles)                      │  │
│  │ Conventional:    Mechanical LPS=1 expected at 2020-06-06 19:42:19 UTC (In 33 hours 52 mins)     │  │
│  │ Operational Risk:Pneumatic line pressure collapse risk. Stoppage in tunnel if unaddressed.      │  │
│  │ Evidence Pack:   [Pressure +23.75σ] [Thermal +5.71σ] [Persistence 3/3] [ML Corroborated 0.382]  │  │
│  │ ActionGuard:     [✓] 5 Safety Checks Cleared — Ready for Safe Mode Simulated Intervention        │  │
│  │                                                                                                  │  │
│  │ [ 👉 OPEN CASE WORKSPACE ]                                            Assigned: DISPATCHER-0941  │  │
│  └──────────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                        │
│  PAST RESOLVED CASES (LỊCH SỬ SỰ CỐ ĐÃ NGHIỆM THU ĐÓNG HỒ SƠ)                                          │
│  ────────────────────────────────────────────────────────────────────────────────────────────────────  │
│  • CASE-20200512-04 | Train #302 (APU-COMP-01) | Oil Filter Replacement | Closed: 2020-05-13 | Verified✓│
│  • CASE-20200420-01 | Train #301 (APU-COMP-02) | Caudal Sensor Calibration | Closed: 2020-04-20 | Verified✓│
│                                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. NGUYÊN TẮC THIẾT KẾ & BẤT BIẾN NGHIỆP VỤ

### 2.1 Bất biến Siemens: Single Active Case Invariant
- **Luật:** `len([c for c in cases if c.asset_id == "APU-COMP-01" and c.phase != "CLOSED"]) <= 1`.
- Nếu có thêm cảnh báo phụ phát sinh khi `CASE-20200605-01` đang mở (ví dụ: nhiệt độ dầu tăng tiếp hoặc tín hiệu rơ-le nhảy), hệ thống **không bao giờ sinh thêm case mới**. Toàn bộ dữ liệu mới sẽ được nối vào **Evidence Chain** và **Timeline Ledger** của Case hiện hành.
- Nhờ đó, người điều độ không bị phân tâm bởi nhiều ticket trùng lặp và không có nguy cơ xung đột lệnh điều khiển thiết bị vật lý.

### 2.2 Đơn vị Nghiệp vụ Vận hành (Operational Case Unit)
- Khác với một anomaly event đơn thuần, một **Case** có:
  - `case_id`: Mã định danh duy nhất.
  - `asset_hierarchy`: Định vị chính xác vị trí trong hạm đội (`Fleet -> Train -> Subsystem -> Asset`).
  - `phase`: Giai đoạn trong vòng đời (`OBSERVING` $\rightarrow$ `CONFIRMED` $\rightarrow$ `PROTECTING` $\rightarrow$ `VERIFYING` $\rightarrow$ `CLOSED`).
  - `confirmed_intervention_window`: Khoảng thời gian can thiệp xác nhận $33\text{h } 52\text{m}$.
  - `assigned_operator`: Chuyên viên chịu trách nhiệm ca trực (`DISPATCHER-0941`).
  - Nút bấm trực diện: `[ OPEN CASE WORKSPACE ]` dẫn vào trung tâm chỉ huy 4 câu hỏi.

---

## 3. RÀNG BUỘC DỮ LIỆU (DATA BINDING CONTRACT)

```json
{
  "active_cases": [
    {
      "case_id": "CASE-20200605-01",
      "asset_hierarchy": {
        "fleet": "Linha Azul",
        "train_id": "TRAIN-302",
        "subsystem": "Air Production Unit (APU)",
        "asset_id": "APU-COMP-01"
      },
      "phase": "CONFIRMED",
      "severity": "CRITICAL",
      "confirmed_detection_timestamp": "2020-06-05T09:50:39Z",
      "conventional_lps_timestamp": "2020-06-06T19:42:19Z",
      "confirmed_intervention_window": {
        "minutes": 2032,
        "formatted": "33h 52m"
      },
      "summary": "Severe Discharge Valve Degradation with Thermal Drift",
      "operational_risk": "Pneumatic line pressure collapse risk. Stoppage in tunnel if unaddressed.",
      "evidence_summary": {
        "pressure_sigma": 23.75,
        "thermal_sigma": 5.71,
        "persistence_cycles": "3/3",
        "ml_corroborated": true
      },
      "action_guard": {
        "can_dispatch_safe_mode": true
      },
      "assigned_operator": "DISPATCHER-0941"
    }
  ],
  "total_active_cases": 1,
  "trains_at_risk": 1
}
```
