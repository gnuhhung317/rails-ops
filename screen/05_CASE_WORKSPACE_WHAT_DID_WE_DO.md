# SCREEN 05 — CASE WORKSPACE: WHAT DID WE DO? (ACTIONGUARD & SIMULATED INTERVENTION)
> **Mục tiêu:** Trả lời câu hỏi thứ ba của chuyên viên: **"Chúng ta có thể làm gì? Quy trình can thiệp có an toàn không và hệ thống đã thực hiện điều gì?"**  
> **Nguyên tắc:** **Policy-Controlled Simulation Intervention** (Hàng rào chính sách ActionGuard kiểm định điều kiện chặt chẽ, không bịa đặt cảm biến độ dốc ray hay cơ cấu chấp hành giả mạo).

---

## 1. BỐ CỤC GIAO DIỆN (ASCII WIREFRAME)

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ CASE WORKSPACE // CASE-20200605-01: APU-COMP-01 (TRAIN #302)                         [STATUS: CRITICAL]│
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [1. WHAT CHANGED?]   [2. WHY? (EVIDENCE)]   [★ 3. WHAT DID WE DO?]   [4. DID IT WORK?]   [5. TIMELINE] │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                        │
│  QUY TRÌNH CAN THIỆP MÔ PHỎNG AN TOÀN (POLICY-CONTROLLED SIMULATED INTERVENTION: SOP-APU-ISO-04)        │
│  ────────────────────────────────────────────────────────────────────────────────────────────────────  │
│  Mục tiêu: Mô phỏng cô lập buồng sấy khí và rẽ nhánh luồng dữ liệu sang phân đoạn sau bảo trì          │
│                                                                                                        │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ HÀNG RÀO KIỂM ĐỊNH CHÍNH SÁCH CAN THIỆP (ACTIONGUARD POLICY PRE-FLIGHT CHECKS)                   │  │
│  │                                                                                                  │  │
│  │   [ ✓ ] 1. Case is Confirmed:           Hồ sơ sự cố đã được xác nhận (Phase: INVESTIGATING)       │  │
│  │   [ ✓ ] 2. Mitigation Recommended:      DecisionEngine đã phát lệnh khuyến nghị can thiệp        │  │
│  │   [ ✓ ] 3. No Conflicting Active Case:  Không có xung đột lệnh trên tài sản APU-COMP-01          │  │
│  │   [ ✓ ] 4. Simulation Mode Only:        Xác nhận môi trường mô phỏng an toàn (Audit-controlled)  │  │
│  │   [ ✓ ] 5. Replay Branch Available:     Phân đoạn dữ liệu sau bảo trì (08/06/2020) sẵn sàng      │  │
│  └──────────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                        │
│  THỰC THI CAN THIỆP MÔ PHỎNG (DISPATCH SIMULATED SAFE MODE)                                            │
│  ────────────────────────────────────────────────────────────────────────────────────────────────────  │
│                                                                                                        │
│  Khuyến nghị hệ thống: Mô phỏng kích hoạt van cô lập Tháp sấy số 2 để bảo vệ áp suất phanh H1.        │
│  Cơ chế rẽ nhánh: Con trỏ ScenarioStream rẽ nhánh (Replay Stream Branch) sang phân đoạn viễn thám     │
│  thực tế sau bảo trì (POST-MAINTENANCE HISTORICAL SEGMENT: 2020-06-08 16:05:00 UTC).                   │
│                                                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐                                  │
│  │  ⚡ [ ACTIVATE SAFE MODE: SIMULATED INTERVENTION ]                │   Authorized: DISPATCHER-0941    │
│  └──────────────────────────────────────────────────────────────────┘   Ledger Event: Appended to DB   │
│                                                                                                        │
│  TRẠNG THÁI HỆ THỐNG SAU KHI BẤM NÚT (STATE TRANSITION):                                               │
│  • Trạng thái vòng đời: Chuyển từ [ INVESTIGATING ] ──► [ MITIGATING ]                                │
│  • Bảo vệ mã lỗi: Bấm đúp hoặc gọi sai thời điểm sẽ bị chặn bởi HTTP 409 Conflict.                   │
│  • Luồng viễn thám mới: Transition to METROPT-3_POST_MAINTENANCE segment.                             │
│                                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. NỘI DUNG NHẬN THỨC CỦA OPERATOR (COGNITIVE PROGRESSION)

1. **Hàng rào ActionGuard thật:** Thay vì bịa ra cảm biến độ dốc ray (`gradient < 1%`) không có trong dữ liệu tàu điện ngầm Lisbon Metro, giao diện hiển thị 5 kiểm định chính sách thực tế của hệ thống.
2. **Trung thực về bản chất rẽ nhánh:** Không nhận vơ rằng "hệ thống AI đã tự động sửa chữa cơ khí chiếc van ngoài đời thực". Hệ thống nêu rõ: **Đây là Simulated Intervention chuyển nhánh sang phân đoạn viễn thám thực tế sau khi đoàn tàu đã được xưởng bảo dưỡng**.
3. **Tính nhân quả khép kín (Closed-Loop Causal Narrative):** Khi chuyên viên kích hoạt Safe Mode, luồng dữ liệu thay đổi thực sự, mở đường cho bước kiểm chứng phục hồi tại Tab 4.

---

## 3. RÀNG BUỘC DỮ LIỆU (DATA BINDING CONTRACT — `POST /api/action/safe-mode`)

```json
{
  "case_id": "CASE-20200605-01",
  "action_guard": {
    "case_confirmed": true,
    "mitigation_recommended": true,
    "no_conflicting_active_case": true,
    "simulation_mode_only": true,
    "replay_branch_available": true,
    "all_passed": true
  },
  "action_result": {
    "action_id": "ACT-SM-001",
    "status": "ACTIVATED",
    "execution_mode": "SIMULATION_BRANCH",
    "target_phase": "MITIGATING",
    "operator_id": "DISPATCHER-0941",
    "stream_branch": {
      "source": "METROPT-3_POST_MAINTENANCE",
      "offset_timestamp": "2020-06-08T16:05:00Z"
    }
  }
}
```
