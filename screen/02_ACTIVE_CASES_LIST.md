# SCREEN 02 — INCIDENT & CASE QUEUE (v3.0 ENTERPRISE CASE MANAGEMENT)
> **Mục tiêu:** Quản lý hàng đợi hồ sơ sự cố vận hành (`Operational Case Queue`) theo chuẩn ITSM / Industrial APM (Datadog Incidents / Siemens Senseye), kết hợp bộ lọc đa chiều, trạng thái tiếp nhận của chuyên viên (`Acknowledge Status`), tiến độ kiểm định `ActionGuard (x/5)`, và trạng thái lệnh điều động bảo trì (`Work Order Status`).
> **Bất biến nghiệp vụ cốt lõi:** Thực thi nghiêm ngặt quy tắc **"Tối đa một Active Case trên một Asset tại một thời điểm (`Single Active Case Invariant`)"**.

---

## 1. BỐ CỤC GIAO DIỆN (ENTERPRISE INCIDENT QUEUE WIREFRAME)

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [CG] COMPRESSORGUARD // OPERATIONS COMMAND CONSOLE    [ LIVE SIMULATION · HISTORICAL DATA · 0.1 Hz ]         │
│ Scope: Linha Azul Fleet / Incident Queue              Event Clock: 2020-06-05 10:15:00 UTC | [🗄️ Valid. Ref] │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ NAV: [1. FLEET & TELEMETRY MATRIX]    [★ 2. INCIDENT QUEUE (1 OPEN)]    [3. CASE INVESTIGATION WORKBENCH]    │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ QUEUE FILTER & GOVERNANCE BAR:                                                                               │
│ [🔍 Search Case ID, Train, Asset...]  Phase: [All Open ▼]  Ack: [All ▼]  Severity: [All ▼]  Single-Case: [✓] │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ ACTIVE OPERATIONAL CASES (1 OPEN)                                                                            │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│ Case ID & Priority │ Asset & Train   │ Lifecycle & Ack Status   │ Evidence & Guard │ Lead Window │ Actions   │
│ ───────────────────┼─────────────────┼──────────────────────────┼──────────────────┼─────────────┼────────── │
│ 🔴 APU-INC-20200605│ APU-COMP-01     │ Phase: [INVESTIGATING]   │ DV: +23.75σ      │ ⏱️ 33h 52m  │ [Ack ✓]   │
│    P1-CRITICAL     │ Train #302      │ Ack:   [ACKED: DISP-0941]│ Oil: +5.71σ      │ (2032 mins  │ [👉 Open  │
│    Opened 09:50:39 │ Linha Azul / APU│ WO:    [WO-302 DRAFTED]  │ IF:  0.382 (✓)   │  to LPS=1)  │ Workbench]│
│                    │                 │                          │ Guard: 5/5 PASS  │             │           │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ SELECTED CASE QUICK PREVIEW & OPERATOR TRIAGE BAR (INLINE DRAWER / EXPANDABLE ROW)                           │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│ • Summary:          Confirmed severe step degradation in DV_pressure with thermal stress drift.              │
│ • Operational Risk: Pneumatic line pressure collapse risk -> Emergency train stoppage in tunnel if unmitigated│
│ • Quick Triage:     [✓ Acknowledged by DISPATCHER-0941]   [📝 Add Quick Note]   [🛠️ Go to 3-Pane Workbench] │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ HISTORICAL RESOLVED & CLOSED CASES ARCHIVE (AUDITABLE POST-MORTEM LEDGER)                                    │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│ Case ID            │ Asset & Train   │ Root Cause Classification     │ Closed At (UTC)  │ Verified │ Dossier │
│ ───────────────────┼─────────────────┼───────────────────────────────┼──────────────────┼──────────┼──────── │
│ 🟢 CASE-20200512-04│ APU-COMP-01/#302│ OIL_FILTER_DIFFERENTIAL_DRIFT │ 2020-05-13 14:20 │ 5/5 PASS │ [View]  │
│ 🟢 CASE-20200420-01│ APU-COMP-02/#301│ CAUDAL_FLOWMETER_SENSOR_DRIFT │ 2020-04-20 09:15 │ 5/5 PASS │ [View]  │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. NGUYÊN TẮC QUẢN TRỊ TICKET & VAI TRÒ OPERATOR (v3.0)

### 2.1. Thực Thi Bất Biến Siemens (`Single Active Case Invariant`)
- Mỗi tài sản vật lý (`APU-COMP-01`) chỉ có tối đa **01 hồ sơ sự cố đang mở (`phase not in ['RESOLVED', 'CLOSED']`)** tại mọi thời điểm.
- Khi có thêm bằng chứng mới phát sinh (nhiệt độ dầu tăng vượt ngưỡng lúc `10:15:00` hoặc điểm số ML Isolation Forest vượt `0.35`), hệ thống **tuyệt đối không đẻ thêm ticket trùng lặp** mà tự động gắn thêm bằng chứng vào `Evidence Chain` và nâng cấp `phase` của Case hiện hành từ `DETECTED` lên `INVESTIGATING`.

### 2.2. Cơ Chế Triage & Tiếp Nhận Hồ Sơ Thực Thụ (`UNACKNOWLEDGED` $\rightarrow$ `ACKNOWLEDGED`)
- Khi hệ thống vừa phát hiện sự cố ở mốc `09:50:39 UTC`, hồ sơ mang trạng thái tiếp nhận `UNACKNOWLEDGED` (nhấp nháy cảnh báo yêu cầu chuyên viên ca trực xác nhận).
- Chuyên viên điều độ có thể bấm **`[ Acknowledge Case ]`** ngay trên hàng đợi (gọi `POST /api/case/acknowledge`) để:
  1. Gán định danh người chịu trách nhiệm xử lý (`acknowledged_by: "DISPATCHER-0941"`).
  2. Gán mức độ ưu tiên vận hành (`priority: "P1-CRITICAL"`).
  3. Ghi sự kiện `OPERATOR_ACK` vào sổ cái kiểm toán `CaseEvent`.

### 2.3. Hiển Thị Trạng Thái Động Của `ActionGuard` & `Work Order` Ngay Trên Hàng Đợi
- Thay vì luôn ghi dòng chữ tĩnh *"5 Safety Checks Cleared"*, cột **Evidence & Guard** hiển thị chính xác số lượng điều kiện đạt được tại thời điểm thực:
  - Ở mốc `09:50:39` (`DETECTED`): Hiển thị `Guard: 4/5 (Awaiting ML Corroboration)`.
  - Ở mốc `10:15:00` (`INVESTIGATING`): Hiển thị `Guard: 5/5 PASS (Ready for Safe Mode)`.

---

## 3. RÀNG BUỘC DỮ LIỆU ĐỘNG (`GET /api/case` & `GET /api/action/guard-status`)

```json
{
  "active_cases": [
    {
      "incident_id": "APU-INC-20200605-01",
      "asset_id": "APU-COMP-01",
      "train_id": "TRAIN-302",
      "fleet_name": "Metro Fleet (Linha Azul)",
      "lifecycle_state": "INVESTIGATING",
      "asset_health": "CRITICAL",
      "operational_confidence": "HIGH",
      "acknowledged": true,
      "acknowledged_by": "DISPATCHER-0941",
      "priority": "P1-CRITICAL",
      "work_order_status": "WO-302 DRAFTED (Depot Oriente)",
      "lead_time": {
        "lead_time_minutes": 2032,
        "lead_time_formatted": "33h 52m",
        "conventional_alert_timestamp": "2020-06-06T19:42:19Z",
        "earliest_detection_timestamp": "2020-06-05T09:50:39Z"
      },
      "action_guard_summary": {
        "passed_count": 5,
        "total_checks": 5,
        "is_permitted": true
      },
      "summary": "Confirmed severe step degradation in DV_pressure with thermal stress drift."
    }
  ]
}
```
