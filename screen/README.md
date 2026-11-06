# COMPRESSORGUARD — OPERATIONS CONSOLE SCREEN SPECIFICATIONS (v3.0 PRODUCTION-READY)
> **Document Type:** Production UI/UX Screen Architecture & Human-in-the-Loop Design System  
> **Status:** Active Normative Specification (v3.0 Production-Ready Alignment)  
> **Target:** Operations Command Platform for Critical Rail Fleet Assets  
> **Domain Standards:** Aligned with Datadog Infrastructure & Incident Management, Siemens Senseye PdM, and IBM Maximo

---

## 1. TRIẾT LÝ GIAO DIỆN PRODUCTION-READY & KIẾN TRÚC ĐIỀU HƯỚNG (v3.0)

Phiên bản v3.0 loại bỏ triệt để phong cách "Auto-Pilot / Slide thuyết trình tĩnh" (không còn thanh nút nhảy milestone chiếm mặt tiền Header, không còn số liệu hardcode tĩnh trong HTML, không còn luồng tự chạy thiếu vắng vai trò người điều độ). Thay vào đó, CompressorGuard được thiết kế như một **Industrial SaaS Operations Console** mật độ cao (High-Density Operations UI):

1. **Tách biệt giao diện vận hành chính và `🎛️ Replay Studio Drawer`:**
   - Giao diện chính là không gian làm việc thuần túy của **Fleet Operations Specialist**.
   - Mọi công cụ điều khiển mô phỏng (`Play/Pause`, `Step +10s`, `Speed 1x..300x`, `Scenario Switcher`, `Diagnostic Bookmarks`) được đóng gói vào ngăn kéo thu gọn **Replay Studio Drawer** ở góc dưới bên phải (`Shift + S`).
2. **100% Data-Driven Telemetry & Synchronized Strip Charts:**
   - Mọi con số đo lường, biểu đồ chuỗi thời gian đa kênh (`DV_pressure`, `Oil_temp`, `Motor_current`, `IF Score`) và trạng thái kiểm định `ActionGuard (PASS/FAIL)` đều đọc trực tiếp từ API thời gian thực (`/api/telemetry/window`, `/api/action/guard-status`, `/api/evidence`, `/api/recovery`).
3. **Human-in-the-Loop Incident Governance:**
   - Chuyên viên điều độ thực sự nắm quyền chỉ huy qua chuỗi thao tác nghiệp vụ: **Triage & Acknowledge Case** $\rightarrow$ **Log Forensic Note** $\rightarrow$ **Chọn Playbook & Lập lệnh điều động xưởng (`Work Order`)** $\rightarrow$ **Kiểm định `ActionGuard` động (`5/5 PASS`) & Kích hoạt `Safe Mode`** $\rightarrow$ **Kiểm chứng bảng `5/5 mẫu LOADED` & Ký duyệt đóng hồ sơ (`Root-Cause Sign-Off`)**.

```text
OPERATIONS COMMAND CONSOLE (v3.0 HIGH-DENSITY WORKSPACE)
│
├── 📂 [NAV 1] FLEET OPERATIONS & LIVE TELEMETRY MATRIX (Screen 01)
│   ├── KPI Strip động 100%: Monitored Assets | Active Cases | Observing | Regime | Lead Window
│   ├── Split View (5:7):
│   │   ├── Trái: Filterable Fleet Asset Grid & Hierarchy Tree (Search, Filter by Health/Regime/Depot)
│   │   └── Phải: Multi-Channel Synchronized Strip Charts (DV_pressure, Oil_temp, Motor_current + LOADED shading)
│   └── Dưới: Real-Time Anomaly & Suppression Event Stream (Tự động bắt và giải thích xung nhiễu 00:33:07)
│
├── 🚨 [NAV 2] INCIDENT & CASE QUEUE (Screen 02)
│   ├── Thanh bộ lọc ITSM/APM: Filter theo Phase, Severity, Ack Status (Unacked/Acked), Operator, Search
│   ├── Bảng Active Operational Cases (Thực thi bất biến Siemens: Tối đa 1 Active Case / Asset)
│   └── Bảng Past Resolved Cases (Hỗ trợ mở lại Post-Mortem Audit Dossier)
│
├── 🛠️ [NAV 3] 3-PANE CASE INVESTIGATION WORKBENCH (Screens 03 - 07)
│   ├── CỘT TRÁI (3/12): Asset Context & 4-Signal Evidence Provenance Matrix (Screens 03 & 04)
│   │   └── Định danh Case, SLA Countdown (33h 52m), 4 Thẻ Bằng Chứng động từ /api/evidence
│   ├── CỘT GIỮA (5/12): Forensic Telemetry Charts, Causal Chain & Recovery Verifier (Screens 03, 04, 06)
│   │   ├── Sub-view A: Đồ thị tương quan vật lý + Lưu đồ Chuỗi Nhân Quả Nhiệt Động Lực Học
│   │   └── Sub-view B: Live Recovery Verification Table (5 mẫu LOADED liên tiếp: DV < 0.05 bar, Oil < 67°C)
│   └── CỘT PHẢI (4/12): Operator Command Console, Dynamic ActionGuard & Audit Ledger (Screens 05, 06, 07)
│       ├── Bước 1: Acknowledge & Triage Case + Forensic Note Input
│       ├── Bước 2: Dynamic ActionGuard 5-Check Live Gate (Hiển thị rõ PASS/FAIL từng điều kiện)
│       ├── Bước 3: Playbook Selection (SOP-APU-ISO-04) + Depot Work Order + Execute Safe Mode
│       ├── Bước 4: Root-Cause Classification + Engineering Sign-Off & Close Case
│       └── Bước 5: Live Append-Only CaseEvent Audit Stream (Chuẩn Datadog Incident Timeline)
│
└── 🗄️ ON-DEMAND DRAWERS (Tách biệt khỏi luồng vận hành chính)
    ├── Drawer 1: Validation Reference Drawer (Đối chứng Ground Truth UCI MetroPT-3 Failure #3)
    └── Drawer 2: Replay & Scenario Studio Drawer (Chuyển đổi 4 kịch bản, Play/Pause/Speed, Bookmarks)
```

---

## 2. DANH MỤC CÁC TỆP ĐẶC TẢ MÀN HÌNH (v3.0)

| Mã màn hình | Tên tệp đặc tả | Trọng tâm nâng cấp Production-Ready (v3.0) |
| :---: | :--- | :--- |
| **SCREEN 01** | [`01_OPERATIONS_NAV_AND_ASSET_OVERVIEW.md`](./01_OPERATIONS_NAV_AND_ASSET_OVERVIEW.md) | **Fleet Grid & Live Strip Charts:** Gỡ thanh milestone khỏi Header; bổ sung bảng lọc hạm đội, biểu đồ 3 kênh thời gian thực (`DV`, `Oil`, `Current`) và bảng log chặn báo động giả động (`00:33:07`). |
| **SCREEN 02** | [`02_ACTIVE_CASES_LIST.md`](./02_ACTIVE_CASES_LIST.md) | **Enterprise Incident Queue:** Bổ sung bộ lọc Ticket, trạng thái tiếp nhận (`UNACKNOWLEDGED` / `ACKNOWLEDGED`), mã phiếu bảo trì (`Work Order`), và tiến độ `ActionGuard (x/5)`. |
| **SCREEN 03** | [`03_CASE_WORKSPACE_WHAT_CHANGED.md`](./03_CASE_WORKSPACE_WHAT_CHANGED.md) | **Workbench — Telemetry & Impact View:** Xóa bỏ số liệu hardcode; liên kết 100% với `/api/telemetry/window` và `/api/case`; hiển thị biểu đồ bước nhảy áp suất và độ trôi nhiệt. |
| **SCREEN 04** | [`04_CASE_WORKSPACE_WHY_EVIDENCE.md`](./04_CASE_WORKSPACE_WHY_EVIDENCE.md) | **Workbench — 4-Signal Evidence Provenance Matrix:** Hiển thị động trạng thái 4 detector + đồ thị điểm số `IsolationForestDetector` trên **5 features** mang tải (`LOADED`). |
| **SCREEN 05** | [`05_CASE_WORKSPACE_WHAT_DID_WE_DO.md`](./05_CASE_WORKSPACE_WHAT_DID_WE_DO.md) | **Workbench — Operator Triage, Playbook & Live ActionGuard:** Hiển thị trạng thái `PASS/FAIL` thực tế của 5 cổng `ActionGuard` + Form chọn Playbook `SOP-APU-ISO-04` và lập `Work Order`. |
| **SCREEN 06** | [`06_CASE_WORKSPACE_DID_IT_WORK.md`](./06_CASE_WORKSPACE_DID_IT_WORK.md) | **Workbench — Live 5-Sample Recovery Table & Sign-Off:** Bảng theo dõi trực tiếp 5 mẫu `LOADED` liên tiếp sau bảo trì + Form ký duyệt nguyên nhân gốc (`Root Cause Sign-Off`). |
| **SCREEN 07** | [`07_CASE_TIMELINE_HISTORY.md`](./07_CASE_TIMELINE_HISTORY.md) | **Workbench — Append-Only `CaseEvent` Audit Ledger:** Ghi nhận cả sự kiện tự động của máy và thao tác của Operator (`ACK`, `NOTE`, `WORK_ORDER`, `ACTION`, `CLOSE`), hỗ trợ lọc & xuất báo cáo. |
