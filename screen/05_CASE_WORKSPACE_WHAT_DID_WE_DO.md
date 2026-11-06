# SCREEN 05 — CASE INVESTIGATION WORKBENCH: WHAT DID WE DO? (DYNAMIC ACTIONGUARD & PLAYBOOK CONSOLE)
> **Mục tiêu:** Trả lời câu hỏi thứ ba của chuyên viên điều độ: **"Hàng rào chính sách an toàn `ActionGuard` đang đánh giá những điều kiện nào theo thời gian thực, và chuyên viên cần chọn Playbook / Lệnh điều động xưởng (`Work Order`) nào trước khi kích hoạt can thiệp mô phỏng?"**  
> **Cải tiến cốt lõi v3.0 (Xoá bỏ cảm giác Auto-Pilot):**
> 1. **Dynamic ActionGuard Checklist (`GET /api/action/guard-status`):** Tuyệt đối không hardcode 5 nhãn `✓ PASS` tĩnh! Giao diện hiển thị trạng thái thật của từng điều kiện (`PASS` màu xanh hoặc `FAIL` màu đỏ/vàng kèm lý do từ chối cụ thể như khi đang ở mốc `09:50:39` chưa có ML corroboration).
> 2. **Human-in-the-Loop Playbook & Work Order Form:** Chuyên viên điều độ thực hiện tuần tự: (1) Tiếp nhận Case (`Acknowledge`), (2) Chọn quy trình chuẩn (`SOP-APU-ISO-04`), (3) Chọn xưởng tiếp nhận (`Depot Oriente`) & lập `Maintenance Work Order`, rồi mới (4) Bấm thực thi `Safe Mode Simulated Intervention`.

---

## 1. BỐ CỤC GIAO DIỆN (3-PANE WORKBENCH — VIEW 3: DYNAMIC ACTIONGUARD & PLAYBOOK DISPATCH)

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ WORKBENCH // APU-INC-20200605-01 · Train #302 (APU-COMP-01)   [PHASE: INVESTIGATING]  [ACKED: DISP-0941 ✓]  │
│ Sub-View Focus: [1. WHAT CHANGED?]  [2. WHY? (EVIDENCE)]  [★ 3. PLAYBOOK & GUARD]  [4. RECOVERY]  [5. AUDIT] │
├───────────────────────────────────────────────────┬──────────────────────────────────────────────────────────┤
│ LEFT & CENTER PANE (7 COLS):                      │ RIGHT PANE (5 COLS):                                     │
│ DYNAMIC ACTIONGUARD 5 PRE-FLIGHT SAFETY CHECKS    │ HUMAN-IN-THE-LOOP PLAYBOOK & WORK ORDER CONSOLE          │
│ (Bound live to GET /api/action/guard-status)      │ (Requires Operator Selection + 5/5 ActionGuard PASS)     │
│ ───────────────────────────────────────────────── │ ──────────────────────────────────────────────────────── │
│ Gate Status: [🟢 5 / 5 CHECKS PASSED — PERMITTED] │ STEP 1: OPERATOR ACKNOWLEDGMENT & TRIAGE                 │
│ (At 09:50 onset: 4/5 Passed, Check #2 = FAIL)     │ • Status:   [✓ ACKNOWLEDGED BY DISPATCHER-0941]          │
│                                                   │ • Priority: [P1-CRITICAL (33h 52m Lead Window)]          │
│ ┌───────────────────────────────────────────────┐ │                                                          │
│ │ [✓ PASS] 1. CASE_CONFIRMED                    │ │ STEP 2: SELECT MITIGATION PLAYBOOK & DEPOT WORK ORDER    │
│ │   Active case in DETECTED or INVESTIGATING    │ │ • Standard Operating Playbook:                           │
│ │   Current: INVESTIGATING (APU-INC-20200605-01)│ │   [SOP-APU-ISO-04: Dryer Tower #2 Isolation & Overhaul ▼]│
│ ├───────────────────────────────────────────────┤ │ • Target Maintenance Depot:                              │
│ │ [✓ PASS] 2. MITIGATION_RECOMMENDED            │ │   [Depot Oriente (Linha Azul Terminal)                 ▼]│
│ │   DecisionEngine recommends EXECUTE_MITIGATION│ │ • Scheduled Intervention Window:                         │
│ │   Current: EXECUTE_MITIGATION (IF 0.382>0.35) │ │   [Next Terminal Turnaround (Within 33h 52m Window)    ▼]│
│ ├───────────────────────────────────────────────┤ │ • Dispatcher Work Order Instructions:                    │
│ │ [✓ PASS] 3. SINGLE_ACTIVE_CASE                │ │   ┌────────────────────────────────────────────────────┐ │
│ │   Zero conflicting open cases on APU-COMP-01  │ │   │Isolate desiccant drain valve DV-02; replace seal   │ │
│ │   Current: 0 conflicts verified               │ │   │and verify loaded pressure < 0.05 bar post-overhaul.│ │
│ ├───────────────────────────────────────────────┤ │   └────────────────────────────────────────────────────┘ │
│ │ [✓ PASS] 4. SIMULATION_MODE                   │ │   [📋 Save / Update Work Order (WO-20200605-302)]        │
│ │   Audit-controlled simulation boundary active │ │                                                          │
│ │   Current: LIVE_SIMULATION                    │ │ STEP 3: DISPATCH SAFE MODE SIMULATED INTERVENTION        │
│ ├───────────────────────────────────────────────┤ │ • Stream Branch Target: METROPT-3_POST_MAINTENANCE       │
│ │ [✓ PASS] 5. REPLAY_BRANCH_AVAILABLE           │ │ • Historical Segment:   2020-06-08 16:05:00 UTC          │
│ │   Post-maintenance telemetry segment indexed  │ │                                                          │
│ │   Current: 2020-06-08 16:05:00 UTC READY      │ │ ┌──────────────────────────────────────────────────────┐ │
│ └───────────────────────────────────────────────┘ │ │ ⚡ [ EXECUTE SAFE MODE & BRANCH TO POST-MAINTENANCE ]│ │
│                                                   │ └──────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────┴──────────────────────────────────────────────────────────┘
```

---

## 2. CƠ CHẾ KIỂM ĐỊNH ĐỘNG & CHỐNG BẤM NHẦM (POLICY GOVERNANCE)

### 2.1. Biến Thiên Trạng Thái Thật Của `ActionGuard` Theo Thời Gian
- **Khi chưa có sự cố (`NONE` / `00:33:07`):**
  - `Check #1 (CASE_CONFIRMED)`: `✗ FAIL` (`Current: NONE`).
  - `Check #2 (MITIGATION_RECOMMENDED)`: `✗ FAIL` (`Current: NONE`).
  - Nút thực thi bị khóa hoàn toàn kèm thông báo: *"No active confirmed case on asset."*
- **Khi mới phát hiện bước nhảy áp suất (`DETECTED` / `09:50:39`):**
  - `Check #1 (CASE_CONFIRMED)`: `✓ PASS` (`Current: DETECTED`).
  - `Check #2 (MITIGATION_RECOMMENDED)`: `✗ FAIL` (`Current: MONITOR_CLOSELY — Awaiting thermal drift & ML corroboration`).
  - Nếu chuyên viên cố tình gọi `POST /api/action/safe-mode` lúc này, Backend trả về **HTTP 409 Conflict** và giao diện giải thích rõ ràng điều kiện số 2 chưa đạt.
- **Khi đã có kiểm chứng đa biến (`INVESTIGATING` / `10:15:00`):**
  - Cả 5/5 điều kiện chuyển sang `✓ PASS`. Form thực thi bước 3 mở khóa để chuyên viên kích hoạt.

### 2.2. Trung Thực Tuyệt Đối Về Bản Chất Rẽ Nhánh (`Stream Branching`)
- Hệ thống ghi rõ: Hành động kích hoạt Safe Mode thực hiện **lập phiếu điều động bảo trì (`Work Order`)** và **rẽ nhánh con trỏ luồng dữ liệu (`Replay Stream Branch`)** sang phân đoạn viễn thám thực tế sau khi đoàn tàu được bảo dưỡng tại xưởng vào ngày `08/06/2020 16:05:00 UTC`.

---

## 3. RÀNG BUỘC DỮ LIỆU ĐỘNG (`GET /api/action/guard-status` & `POST /api/action/safe-mode`)

```json
{
  "guard_status": {
    "is_permitted": true,
    "denial_reason": "",
    "checklist": [
      {
        "id": "CASE_CONFIRMED",
        "label": "Case is active and confirmed",
        "passed": true
      },
      {
        "id": "MITIGATION_RECOMMENDED",
        "label": "DecisionEngine recommends mitigation",
        "passed": true
      },
      {
        "id": "SINGLE_ACTIVE_CASE",
        "label": "No conflicting active cases on asset",
        "passed": true
      },
      {
        "id": "SIMULATION_MODE",
        "label": "Simulation intervention boundary verified",
        "passed": true
      },
      {
        "id": "REPLAY_BRANCH_AVAILABLE",
        "label": "Post-maintenance historical stream segment available",
        "passed": true
      }
    ]
  },
  "safe_mode_response": {
    "action_id": "ACT-SM-001",
    "operator_id": "DISPATCHER-0941",
    "status": "ACTIVATED",
    "execution_mode": "SIMULATION_BRANCH",
    "target_state": "MITIGATING",
    "stream_branch": {
      "source": "METROPT-3_POST_MAINTENANCE",
      "offset_timestamp": "2020-06-08T16:05:00Z"
    }
  }
}
```
