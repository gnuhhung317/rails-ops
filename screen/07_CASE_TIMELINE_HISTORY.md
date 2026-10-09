# SCREEN 07 — CASE TIMELINE & AUDIT HISTORY (CASEEVENT LEDGER)
> **Mục tiêu:** Cung cấp biên niên sử sự cố theo dòng thời gian chuẩn Datadog Incident Timeline. Sổ cái sự kiện `CaseEvent` dạng append-only lưu vết tự động mọi quan sát thực tế, phán đoán của động cơ, hành động của người điều độ, mốc còi cũ và nghiệm thu phục hồi.

---

## 1. BỐ CỤC GIAO DIỆN (ASCII WIREFRAME)

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ CASE WORKSPACE // CASE-20200605-01: APU-COMP-01 (TRAIN #302)                            [STATUS: CLOSED]│
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [1. WHAT CHANGED?]   [2. WHY? (EVIDENCE)]   [3. WHAT DID WE DO?]   [4. DID IT WORK?]   [★ 5. TIMELINE] │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                        │
│  SỔ CÁI SỰ KIỆN VÒNG ĐỜI SỰ CỐ (APPEND-ONLY CASEEVENT AUDIT LEDGER — DATADOG APM PATTERN)               │
│  ────────────────────────────────────────────────────────────────────────────────────────────────────  │
│                                                                                                        │
│  ● 2020-06-04 00:33:07 UTC  [ 🟡 OBSERVATION — TRANSIENT NOISE SUPPRESSED ]                            │
│  │   Actor: CompressorGuard Engine          Source: PressureAnomalyDetector     Phase: OBSERVING       │
│  │   Detail: Transient pressure spike of 0.52 bar (+4.21σ); thermal normal; case creation suppressed.  │
│  │                                                                                                     │
│  ● 2020-06-05 09:50:39 UTC  [ 🔴 CASE_CREATED — CONFIRMED DEGRADATION DETECTED ]                       │
│  │   Actor: CompressorGuard Engine          Source: PressureAnomalyDetector     Phase: DETECTED        │
│  │   Detail: Discharge pressure jumped to 2.1856 bar (+23.75σ) sustained 3 loaded cycles. Case opened.│
│  │                                                                                                     │
│  ● 2020-06-05 10:15:00 UTC  [ ⚠️ CORROBORATION — MULTIVARIATE ML CONFIRMED ]                           │
│  │   Actor: ML Analytics Pipeline           Source: IsolationForestModel        Phase: INVESTIGATING   │
│  │   Detail: Oil temp 74.97°C (+5.71σ); IF score 0.382 > 0.35 on 5 loaded features. Confidence elevated│
│  │                                                                                                     │
│  ● 2020-06-05 10:15:05 UTC  [ 💡 DECISION — MITIGATION RECOMMENDED ]                                   │
│  │   Actor: DecisionEngine                  Source: FusionRuleEngine            Phase: INVESTIGATING   │
│  │   Detail: 3 physical signals confirmed + ML corroborated -> ActionGuard recommends Safe Mode.       │
│  │                                                                                                     │
│  ● 2020-06-05 10:15:20 UTC  [ ⚡ ACTION — SAFE MODE SIMULATED INTERVENTION ]                            │
│  │   Actor: DISPATCHER-0941 (Operator)      Source: ActionGuard                 Phase: MITIGATING      │
│  │   Detail: ActionGuard checks cleared (5/5). Stream branched to post-maintenance segment (08/06).   │
│  │                                                                                                     │
│  ● 2020-06-06 19:42:19 UTC  [ ⏱️ BENCHMARK_LPS — CONVENTIONAL ALARM MILESTONE ]                        │
│  │   Actor: Benchmark Reference             Source: MetroPT-3 Historical Stream Phase: MITIGATING      │
│  │   Detail: Mechanical LPS=1 tripped in unmitigated baseline. Confirmed Intervention Window: 33h 52m! │
│  │                                                                                                     │
│  ● 2020-06-08 16:05:50 UTC  [ 🟢 RECOVERY — RECOVERY CRITERIA VERIFIED ]                               │
│  │   Actor: RecoveryVerifier                Source: RecoveryCriteriaPolicy      Phase: RESOLVED        │
│  │   Detail: 5/5 consecutive loaded observations verified (DV: -0.016 bar, Oil: 64.1°C).               │
│  │                                                                                                     │
│  ● 2020-06-08 16:06:10 UTC  [ 🔒 CASE_CLOSED — OPERATOR SIGN-OFF & ASSET RELEASED ]                    │
│  │   Actor: DISPATCHER-0941 (Operator)      Source: POST /api/case/close        Phase: CLOSED          │
│  │   Detail: Operator signed off case. Asset APU-COMP-01 released back to HEALTHY on Operations Landing│
│                                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Ý NGHĨA QUẢN TRỊ VẬN HÀNH (OPERATIONAL GOVERNANCE)

1. **Thực thể dữ liệu thật (Real Domain Entity):** 
   - `CaseEvent` không phải là văn bản tĩnh viết sẵn trong frontend.
   - Nó là một danh sách bản ghi có cấu trúc (`timestamp`, `event_type`, `title`, `detail`, `actor`, `source`, `case_phase`) được sinh ra tự động trong suốt quá trình chạy mô phỏng.
2. **Minh chứng "Không Phải Kịch Bản Hardcode":**
   - Giám khảo có thể đối chiếu từng dòng sự kiện với các mốc dữ liệu thực tế: Từ lúc phát hiện sớm, ML xác nhận, lệnh bấm của operator, mốc còi cơ học, cho đến khi hồi phục.
   - Sổ cái này tương thích hoàn toàn nếu chạy trên các kịch bản khác (Failure #1, Failure #4, hoặc Chu kỳ vận hành bình thường).

---

## 3. RÀNG BUỘC DỮ LIỆU (DATA BINDING CONTRACT — `GET /api/case/events`)

```json
{
  "case_id": "CASE-20200605-01",
  "events": [
    {
      "timestamp": "2020-06-04T00:33:07Z",
      "event_type": "OBSERVATION",
      "title": "Transient Pressure Excursion",
      "detail": "Transient spike of 0.52 bar observed; thermal normal; case creation suppressed to prevent alert fatigue.",
      "actor": "CompressorGuard Engine",
      "source": "PressureAnomalyDetector",
      "case_phase": "OBSERVING"
    },
    {
      "timestamp": "2020-06-05T09:50:39Z",
      "event_type": "CASE_CREATED",
      "title": "Confirmed Degradation Detected",
      "detail": "Discharge pressure 2.18 bar sustained across 3 loaded cycles (+23.75σ). Operational Case opened.",
      "actor": "CompressorGuard Engine",
      "source": "PressureAnomalyDetector",
      "case_phase": "DETECTED"
    },
    {
      "timestamp": "2020-06-05T10:15:00Z",
      "event_type": "CORROBORATION",
      "title": "Multivariate Corroboration Confirmed",
      "detail": "Oil temp reached 74.97°C (+5.71σ); Isolation Forest score 0.382 > 0.35. Escalated to INVESTIGATING.",
      "actor": "ML Pipeline",
      "source": "IsolationForestModel",
      "case_phase": "INVESTIGATING"
    },
    {
      "timestamp": "2020-06-05T10:15:05Z",
      "event_type": "DECISION",
      "title": "Mitigation Recommended",
      "detail": "Multi-signal physics + ML corroboration established; DecisionEngine recommends Safe Mode.",
      "actor": "DecisionEngine",
      "source": "FusionRuleEngine",
      "case_phase": "INVESTIGATING"
    },
    {
      "timestamp": "2020-06-05T10:15:20Z",
      "event_type": "ACTION",
      "title": "Safe Mode Simulated Intervention",
      "detail": "Operator verified ActionGuard conditions and executed simulated isolation. Stream branched to post-maintenance telemetry.",
      "actor": "DISPATCHER-0941",
      "source": "ActionGuard",
      "case_phase": "MITIGATING"
    },
    {
      "timestamp": "2020-06-06T19:42:19Z",
      "event_type": "BENCHMARK_LPS",
      "title": "Reactive Benchmark Reached",
      "detail": "Mechanical Low Pressure Switch (LPS=1) tripped in historical unmitigated baseline. Confirmed lead time: 33h 52m.",
      "actor": "Benchmark Tracker",
      "source": "MetroPT-3 Baseline",
      "case_phase": "MITIGATING"
    },
    {
      "timestamp": "2020-06-08T16:05:50Z",
      "event_type": "RECOVERY",
      "title": "Recovery Criteria Verified",
      "detail": "5/5 consecutive loaded observations verified (DV < 0.05 bar, Oil < 67°C).",
      "actor": "RecoveryVerifier",
      "source": "RecoveryCriteriaPolicy",
      "case_phase": "RESOLVED"
    },
    {
      "timestamp": "2020-06-08T16:06:10Z",
      "event_type": "CASE_CLOSED",
      "title": "Operator Sign-off & Asset Released",
      "detail": "Operator signed off case. Asset APU-COMP-01 released back to HEALTHY on Operations Landing Page.",
      "actor": "DISPATCHER-0941",
      "source": "POST /api/case/close",
      "case_phase": "CLOSED"
    }
  ]
}
```
