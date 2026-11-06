# SCREEN 03 — CASE INVESTIGATION WORKBENCH: WHAT CHANGED? (DYNAMIC TELEMETRY & IMPACT)
> **Mục tiêu:** Trả lời câu hỏi cốt tử đầu tiên của chuyên viên điều độ trong **3-Pane Case Investigation Workbench**: **"Điều gì đang thực sự diễn ra trên thiết bị vật lý theo thời gian thực, tác động thế nào tới đoàn tàu, và chúng ta còn bao nhiêu thời gian can thiệp?"**
> **Cải tiến cốt lõi v3.0:**
> 1. **Xoá bỏ 100% số liệu hardcode tĩnh:** Không còn việc in cứng `2.1856 bar` hay `74.97 °C` trong mã HTML. Toàn bộ giá trị hiện tại, độ lệch chuẩn ($\sigma$), ngưỡng baseline và biểu đồ bước nhảy đều được đọc động từ `GET /api/case`, `GET /api/evidence`, và `GET /api/telemetry/window`.
> 2. **Bố cục 3-Pane Investigation Workbench:** Kết hợp ngữ cảnh 4 tầng dữ liệu với đồ thị chuỗi thời gian tương tác ngay trên cùng một không gian làm việc.

---

## 1. BỐ CỤC GIAO DIỆN (3-PANE WORKBENCH — VIEW 1: WHAT CHANGED?)

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ WORKBENCH // APU-INC-20200605-01 · Train #302 (APU-COMP-01)   [PHASE: INVESTIGATING]  [ACKED: DISP-0941 ✓]  │
│ Sub-View Focus: [★ 1. WHAT CHANGED?]  [2. WHY? (EVIDENCE)]  [3. PLAYBOOK & GUARD]  [4. RECOVERY]  [5. AUDIT] │
├───────────────────────────────────┬──────────────────────────────────────────────────┬───────────────────────┤
│ LEFT PANE (3 COLS):               │ CENTER PANE (5 COLS):                            │ RIGHT PANE (4 COLS):  │
│ 4-LAYER CONTEXT & SLA WINDOW      │ LIVE STEP-CHANGE & THERMAL DRIFT TELEMETRY CHART │ OPERATOR TRIAGE &     │
│ ───────────────────────────────── │ ──────────────────────────────────────────────── │ QUICK COMMAND PANEL   │
│ ⏱️ INTERVENTION LEAD WINDOW       │ Synchronized Window (GET /api/telemetry/window): │ ───────────────────── │
│    33h 52m (2,032 mins)           │                                                  │ 1. TRIAGE STATUS      │
│    Onset: 2020-06-05 09:50:39 UTC │ [Chart A: DV_pressure_bar vs Baseline -0.016]    │ • Status: ACKED ✓     │
│    LPS=1: 2020-06-06 19:42:19 UTC │  2.5 ┤               ╭─────────────────────────  │ • Owner:  DISP-0941   │
│                                   │  2.0 ┤───────────────┼─────────────────────────  │ • Prio:   P1-CRITICAL │
│ LAYER 1: OPERATIONAL CONDITION    │  0.0 ┤───────────────╯ (Step onset @ 09:50:39)   │                       │
│ • Health:     [🔴 CRITICAL]       │                                                  │ 2. ADD FORENSIC NOTE  │
│ • Regime:     [LOADED (6.84 A)]   │ [Chart B: Oil_temp_c vs Baseline 54.98 °C]       │ ┌───────────────────┐ │
│ • Confidence: [HIGH (ML+Physics)] │ 75.0 ┤                       ╭─────────────────  │ │DV step confirmed  │ │
│ • Persistence:[3/3 Loaded Cycles] │ 65.0 ┤               ╭───────╯                   │ │across 3 cycles... │ │
│                                   │ 55.0 ┤───────────────╯ (Cumulative friction)     │ └───────────────────┘ │
│ LAYER 2: BUSINESS CONTEXT (FLEET) │                                                  │ [➕ Append to Ledger] │
│ • Fleet:      Metro Line 1 (HURC1)  │ LIVE TELEMETRY DELTA TABLE (DYNAMIC API BINDING):│                       │
│ • Service:    TRAIN-302 (Car 1)   │ ┌──────────────┬───────────┬──────────┬────────┐ │ 3. ACTIONGUARD STATUS │
│ • Subsystem:  SUB-APU-01 (APU)    │ │ Metric       │ Observed  │ Baseline │ Sigma  │ │ • Passed: 5/5 Checks  │
│ • Risk:       H1 brake reservoir  │ ├──────────────┼───────────┼──────────┼────────┤ │ • Next:   Select SOP  │
│               undressure ->       │ │ DV_pressure  │ 2.1856 bar│ -0.0164  │+23.75σ │ │   & Dispatch Safe Mode│
│               Tunnel stoppage     │ │ Oil_temp     │ 74.97 °C  │ 54.98 °C │ +5.71σ │ │ [👉 Open Action Tab]  │
│                                   │ │ Motor_curr   │ 6.84 A    │ > 0.50 A │ LOADED │ │                       │
│ LAYER 3: VALIDATION REFERENCE     │ │ IF ML Score  │ 0.382     │ < 0.350  │ CORROB │ │ 4. RECENT LEDGER      │
│ • Ref ID:     SCENARIO-FAIL-03    │ └──────────────┴───────────┴──────────┴────────┘ │ • 10:15 CORROBORATION │
│ • GroundTruth:Isolated in Drawer  │ (Values update dynamically on every 10s tick)    │ • 09:52 OPERATOR_ACK  │
│   [🗄️ Open Validation Drawer]     │                                                  │ • 09:50 DETECTION     │
└───────────────────────────────────┴──────────────────────────────────────────────────┴───────────────────────┘
```

---

## 2. NGUYÊN TẮC PHÂN TẦNG DỮ LIỆU ĐỘNG (ZERO-HARDCODE ARCHITECTURE)

1. **Tầng 1 — Observed Telemetry & Delta Table (Cột giữa):**
   - Toàn bộ các ô `Observed`, `Baseline`, `Sigma` và đồ thị đường lấy trực tiếp từ mảng `evidence_pack` của `GET /api/evidence` và mảng `points` của `GET /api/telemetry/window`.
   - Khi mô phỏng chạy qua từng chu kỳ 10 giây, con số và đồ thị dịch chuyển thực tế theo đúng dòng CSV `MetroPT3(AirCompressor).csv`.
2. **Tầng 2 — Operational Condition & Intervention Window (Cột trái trên):**
   - Hiển thị trạng thái máy (`asset_health`, `lifecycle_state`, `operational_confidence`) và khoảng thời gian can thiệp xác nhận (`lead_time.lead_time_formatted`) được tính toán động từ `BaselineBenchmarkTracker`.
3. **Tầng 3 — Business Context (Cột trái giữa):**
   - Ánh xạ từ `AssetRegistry` (`TRAIN-302` $\rightarrow$ `SUB-APU-01` $\rightarrow$ `APU-COMP-01`), giải thích tác động vật lý lên hệ thống phanh khí nén đoàn tàu.
4. **Tầng 4 — Validation Reference (Cột trái dưới & Ngăn kéo độc lập):**
   - Liên kết tới `GET /api/validation-reference` để đối chứng độc lập với báo cáo bảo trì lịch sử (`Failure #3 — Air Leak / High Stress`), đảm bảo không bao giờ rò rỉ nhãn Ground Truth vào bộ phát hiện online.

---

## 3. RÀNG BUỘC DỮ LIỆU ĐỘNG (`GET /api/case` + `GET /api/evidence` + `GET /api/telemetry/window`)

```json
{
  "case": {
    "incident_id": "APU-INC-20200605-01",
    "asset_id": "APU-COMP-01",
    "lifecycle_state": "INVESTIGATING",
    "asset_health": "CRITICAL",
    "operational_confidence": "HIGH",
    "lead_time": {
      "lead_time_minutes": 2032,
      "lead_time_formatted": "33h 52m",
      "conventional_alert_timestamp": "2020-06-06T19:42:19Z",
      "earliest_detection_timestamp": "2020-06-05T09:50:39Z"
    }
  },
  "dynamic_telemetry_binding": {
    "source_endpoints": [
      "/api/case",
      "/api/evidence",
      "/api/telemetry/window?limit=60"
    ],
    "hardcoded_ui_values_allowed": false
  }
}
```
