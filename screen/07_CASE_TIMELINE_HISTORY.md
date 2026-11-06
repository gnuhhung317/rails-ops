# SCREEN 07 — CASE TIMELINE & IMMUTABLE AUDIT LEDGER (CASEEVENT STREAM)
> **Mục tiêu:** Cung cấp sổ cái kiểm toán bất biến (`Append-Only CaseEvent Audit Ledger`) theo chuẩn Datadog Incident Timeline & Industrial Compliance. Lưu vết đầy đủ cả **sự kiện tự động của hệ thống (`System Detectors & DecisionEngine`)** lẫn **hành động điều hành của con người (`Operator Triage, Notes, Work Order, Safe Mode, Sign-Off`)**.

---

## 1. BỐ CỤC GIAO DIỆN (3-PANE WORKBENCH — VIEW 5: IMMUTABLE CASEEVENT AUDIT LEDGER)

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ WORKBENCH // APU-INC-20200605-01 · Train #302 (APU-COMP-01)   [PHASE: RESOLVED]       [LEDGER: APPEND-ONLY]  │
│ Sub-View Focus: [1. WHAT CHANGED?]  [2. WHY? (EVIDENCE)]  [3. PLAYBOOK & GUARD]  [4. RECOVERY]  [★ 5. AUDIT] │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ LEDGER FILTER & EXPORT TOOLBAR:                                                                              │
│ Actor: [All (System + Operator) ▼]   Type: [All Event Types ▼]   [🔍 Filter events...]   [📥 Export Dossier] │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ CHRONOLOGICAL APPEND-ONLY CASEEVENT AUDIT LEDGER (BOUND TO GET /api/case/events)                             │
│ ──────────────────────────────────────────────────────────────────────────────────────────────────────────── │
│                                                                                                              │
│  ● 2020-06-04 00:33:07 UTC  [ 🟡 OBSERVATION ]      Phase: MONITORING       Actor: system:detector           │
│  │   Title:  Early Excursion Telemetry Observation (Noise Suppressed)                                        │
│  │   Detail: Discharge valve transient pressure excursion observed (6.046 bar, 65.4σ). Insufficient          │
│  │           temporal persistence (1/3 cycles) suppressed case creation.                                     │
│  │                                                                                                           │
│  ● 2020-06-05 09:50:39 UTC  [ 🔴 DETECTION ]        Phase: DETECTED         Actor: system:detector           │
│  │   Title:  Confirmed degradation detected — Case APU-INC-20200605-01 Opened                                │
│  │   Detail: Severe step degradation in DV_pressure (+23.75σ) sustained across 3 consecutive LOADED cycles.  │
│  │                                                                                                           │
│  ● 2020-06-05 09:52:10 UTC  [ 👤 OPERATOR_ACK ]     Phase: DETECTED         Actor: operator:DISPATCHER-0941  │
│  │   Title:  Case Acknowledged & Claimed by Shift Dispatcher                                                 │
│  │   Detail: Priority assigned P1-CRITICAL. Monitoring thermal drift and multivariate ML corroboration.      │
│  │                                                                                                           │
│  ● 2020-06-05 10:15:00 UTC  [ 🔵 CORROBORATION ]    Phase: INVESTIGATING    Actor: system:ml                 │
│  │   Title:  Multivariate Isolation Forest Corroboration (5 Loaded Features)                                 │
│  │   Detail: Isolation Forest exceeded threshold (0.382 > 0.35) with Oil_temp at 74.97°C (+5.71σ).           │
│  │                                                                                                           │
│  ● 2020-06-05 10:15:00 UTC  [ 💡 DECISION ]         Phase: INVESTIGATING    Actor: system:decision_engine    │
│  │   Title:  Operational Policy Evaluation: Mitigation Recommended                                           │
│  │   Detail: Recommended EXECUTE_MITIGATION under ActionGuard (5/5 pre-flight safety criteria satisfied).    │
│  │                                                                                                           │
│  ● 2020-06-05 10:15:15 UTC  [ 📋 WORK_ORDER ]       Phase: INVESTIGATING    Actor: operator:DISPATCHER-0941  │
│  │   Title:  Maintenance Work Order WO-20200605-302 Drafted                                                  │
│  │   Detail: Selected Playbook SOP-APU-ISO-04 for Depot Oriente (Isolate Dryer Tower #2 drain valve).        │
│  │                                                                                                           │
│  ● 2020-06-05 10:15:20 UTC  [ ⚡ ACTION ]           Phase: MITIGATING       Actor: operator:DISPATCHER-0941  │
│  │   Title:  Safe Mode Simulated Intervention Activated                                                      │
│  │   Detail: ActionGuard validated 5 criteria. Branched stream to post-maintenance historical segment.       │
│  │                                                                                                           │
│  ● 2020-06-06 19:42:19 UTC  [ ⏱️ BENCHMARK_LPS ]    Phase: MITIGATING       Actor: system:benchmark_tracker  │
│  │   Title:  Unmitigated Historical LPS Breach Reference                                                     │
│  │   Detail: Conventional low pressure switch tripped in unmitigated baseline (33h 52m after detection).     │
│  │                                                                                                           │
│  ● 2020-06-08 16:05:50 UTC  [ 🟢 RECOVERY ]         Phase: RESOLVED         Actor: system:recovery_verifier  │
│  │   Title:  Recovery Criteria Verified (5/5 healthy LOADED observations)                                    │
│  │   Detail: DV_pressure < 0.05 bar and Oil_temp < 67°C verified across 5 consecutive loaded observations.   │
│  │                                                                                                           │
│  ● 2020-06-08 16:06:10 UTC  [ 🔒 CASE_CLOSED ]      Phase: RESOLVED         Actor: operator:DISPATCHER-0941  │
│      Title:  Case Signed Off & Closed — Asset Released to Revenue Service                                    │
│      Detail: Root cause confirmed (Desiccant Drain Valve Leak). Asset APU-COMP-01 restored to HEALTHY.       │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. GIÁ TRỊ KIỂM TOÁN & QUẢN TRỊ VẬN HÀNH (OPERATIONAL AUDITABILITY)

1. **Sự Kết Hợp Giữa Trí Tuệ Máy (`system:*`) và Trách Nhiệm Con Người (`operator:*`):**
   - Trong môi trường công nghiệp đường sắt, mọi quyết định điều độ đều phải trả lời được câu hỏi kiểm toán: *"Máy đã phát hiện lúc nào, bằng thuật toán gì, và ai là người đã phê duyệt lệnh can thiệp cũng như ký đóng hồ sơ?"*
   - Sổ cái `CaseEvent` phân biệt rõ `actor: "system:detector" / "system:ml"` và `actor: "operator:DISPATCHER-0941"`.
2. **Cơ Chế Append-Only Bất Biến Trên MongoDB (`case_events` collection):**
   - Mọi bản ghi `CaseEvent` chỉ được phép nối thêm (`insert_one`), không bao giờ bị ghi đè hay xóa bỏ trong suốt vòng đời sự cố.
   - Hỗ trợ lọc nhanh theo nhóm sự kiện (`System Only`, `Operator Actions Only`) và xuất toàn bộ hồ sơ sự cố ra định dạng báo cáo hậu kiểm (`Post-Mortem Verification Dossier`).

---

## 3. RÀNG BUỘC DỮ LIỆU ĐỘNG (`GET /api/case/events`)

```json
[
  {
    "event_id": "EVT-001",
    "case_id": "APU-INC-20200605-01",
    "event_time": "2020-06-05T09:50:39",
    "event_type": "DETECTION",
    "phase": "DETECTED",
    "title": "Confirmed degradation detected",
    "detail": "Severe step degradation in DV_pressure with thermal drift sustained across loaded observations. Case opened.",
    "actor": "system:detector",
    "source": "PressureAnomalyDetector",
    "provenance": {}
  },
  {
    "event_id": "EVT-002",
    "case_id": "APU-INC-20200605-01",
    "event_time": "2020-06-05T09:52:10",
    "event_type": "OPERATOR_ACK",
    "phase": "DETECTED",
    "title": "Case Acknowledged by Operator",
    "detail": "Dispatcher DISPATCHER-0941 acknowledged case and assigned priority P1-CRITICAL.",
    "actor": "operator:DISPATCHER-0941",
    "source": "Operations Console",
    "provenance": {"priority": "P1-CRITICAL"}
  },
  {
    "event_id": "EVT-003",
    "case_id": "APU-INC-20200605-01",
    "event_time": "2020-06-05T10:15:00",
    "event_type": "CORROBORATION",
    "phase": "INVESTIGATING",
    "title": "Multivariate Isolation Forest Corroboration",
    "detail": "Isolation Forest exceeded threshold (score > 0.35) on 5 LOADED features. Mitigation recommended.",
    "actor": "system:ml",
    "source": "IsolationForestDetector",
    "provenance": {}
  },
  {
    "event_id": "EVT-004",
    "case_id": "APU-INC-20200605-01",
    "event_time": "2020-06-05T10:15:20",
    "event_type": "ACTION",
    "phase": "MITIGATING",
    "title": "Safe Mode Simulated Intervention",
    "detail": "ActionGuard validated 5 criteria. Branching stream to post-maintenance historical segment.",
    "actor": "operator:DISPATCHER-0941",
    "source": "ActionGuard",
    "provenance": {"playbook_id": "SOP-APU-ISO-04", "depot": "Depot Oriente"}
  },
  {
    "event_id": "EVT-005",
    "case_id": "APU-INC-20200605-01",
    "event_time": "2020-06-08T16:05:50",
    "event_type": "RECOVERY",
    "phase": "RESOLVED",
    "title": "Recovery Criteria Verified (5/5 healthy LOADED observations)",
    "detail": "Discharge valve pressure < 0.05 bar and oil temp < 67°C verified across 5 consecutive loaded observations.",
    "actor": "system:recovery_verifier",
    "source": "RecoveryVerifier",
    "provenance": {}
  },
  {
    "event_id": "EVT-006",
    "case_id": "APU-INC-20200605-01",
    "event_time": "2020-06-08T16:06:10",
    "event_type": "CASE_CLOSED",
    "phase": "RESOLVED",
    "title": "Case Signed Off & Closed",
    "detail": "Operator DISPATCHER-0941 signed off incident. Asset APU-COMP-01 released back to HEALTHY service.",
    "actor": "operator:DISPATCHER-0941",
    "source": "Operations Console",
    "provenance": {"root_cause": "DESICCANT_DRAIN_VALVE_LEAK"}
  }
]
```
