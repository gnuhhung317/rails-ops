# CompressorGuard — Master Task Plan

> **Planning Framework:** `planning-with-files` v2.43.0  
> **Target:** MUGVN Hackathon 2026 (MongoDB + Datadog) & Industrial Commercialization  
> **Core Promise:** Detect earlier → Prove why → Act safely → Verify recovery → Quantify value.  
> **Status:** Active (Aligned with v3.0 Production-Ready Specification — 2026-10-17)

---

## 1. Goal Statement
Chuyển hóa CompressorGuard từ một Vertical Slice Backend thành một **Hệ thống Điều hành Sự cố Vật lý Cấp Công nghiệp (Industrial Operations Command Platform)** hoàn chỉnh: tích hợp mô hình phân cấp hạm đội (Fleet Spine), tách biệt 3 tầng dữ liệu, mô phỏng hai đồng hồ (Dual-Clock Live Simulation), sổ cái sự kiện CaseEvent, nền tảng dữ liệu MongoDB Atlas (Time Series & Document Collections), bảng quan sát Datadog APM/Traces, và giao diện chỉ huy Operations Console v3.0 mật độ cao tuân thủ nguyên tắc **Zero Hardcoded Telemetry & Human-in-the-Loop Governance**.

---

## 2. Invariants & Rules of Engagement
1. **Zero Fake Telemetry:** Dữ liệu cảm biến 100% bắt nguồn từ `MetroPT3(AirCompressor).csv`.
2. **Decoupled Producer–Consumer Live Architecture:** *"The Dashboard Does Not Trigger Telemetry."* Backend Stream Worker nạp dữ liệu độc lập; UI là console quan sát và phản hồi thuần túy.
3. **Phân Định 3 Tầng Dữ Liệu:** Business Context (Asset Registry) $\neq$ Observed Telemetry $\neq$ Validation Reference (Ground Truth).
4. **Dual-Clock Architecture:** Giữ nguyên `event_time` gốc lịch sử cho mọi suy luận và kiểm chứng; điều tiết phát dòng bằng `simulation_time`.
5. **ActionGuard & Single Active Case:** Tuân thủ chuẩn công nghiệp Siemens Senseye (tối đa 1 case/asset; 5 kiểm định an toàn trước khi rẽ nhánh sang dữ liệu sau bảo trì).
6. **Zero Hardcoded UI Data (100% Data-Driven):** Mọi số liệu đo lường, biểu đồ chuỗi thời gian Chart.js và trạng thái cổng kiểm định `PASS/FAIL` đều đọc trực tiếp từ API động.
7. **Tách Bạch UI Vận Hành và Demo Harness:** Toàn bộ công cụ mô phỏng (`Play/Pause`, `Speed`, `Scenario Switcher`, `Bookmarks`) gói gọn trong **Replay Studio Drawer** (`Shift + S`), giải phóng hoàn toàn Header chính.
8. **Tuân Thủ Quy Tắc Agent (AGENTS.md):** Tuyệt đối **không tự ý chạy `pytest`** trần trên toàn bộ dự án vì tập dữ liệu 1.5M dòng gây nghẽn tài nguyên.

---

## 3. Reconciliation & Architectural Diagnosis (v2.3 Prototype vs. v3.0 Production Spec)

> [!IMPORTANT]
> **Giải Quyết Bất Đồng Giữa Lộ Trình Cũ (v2.3) Và Đặc Tả Mới (v3.0 - 11/10/2026):**
> - **Trạng thái ghi nhận trước đó (09/10/2026):** Ghi nhận Phase 1–6 hoàn tất (98/98 test passed) áp dụng cho **bản mẫu sơ khởi (v2.3 prototype)**.
> - **Chẩn đoán kiến trúc ngày 11/10/2026 (`docs/superpowers/specs/2026-10-11-prod-ready-ux-and-mechanism-design.md`):** Bản mẫu v2.3 bộc lộ 5 khiếm khuyết lớn khiến hệ thống giống "slide thuyết trình tự động" thay vì sản phẩm vận hành công nghiệp:
>   1. *Simulation controls chiếm lĩnh Header chính.*
>   2. *Dữ liệu hiển thị trên giao diện bị hardcode tĩnh (~90%).*
>   3. *Thiếu vắng biểu đồ chuỗi thời gian (Time-Series Strip Charts) đa kênh.*
>   4. *Thiếu các bước tác nghiệp thực tế của Operator (Human-in-the-Loop: Acknowledge, Forensic Note, Work Order, Sign-off).*
>   5. *Bố cục 5 sub-tabs rời rạc, nặng tính thuyết trình.*
> - **Quyết định điều chỉnh:**
>   - Gỡ bỏ mã giao diện prototype cũ (`src/static/`).
>   - Backend đã hoàn tất nâng cấp API contracts v3.0 (xác thực tại `tests/test_production_backend_v3.py`).
>   - Mở lại (Re-open) **Phase 5** để hiện thực hóa giao diện chuẩn v3.0.
>   - Điều chỉnh **Phase 6** sang trạng thái chờ hoàn tất Phase 5.

---

## 4. Implementation Phases & Realistic Status

| Phase | Description | Status | Reference / Deliverables |
| :---: | :--- | :---: | :--- |
| **Phase 1** | **Core Domain Backend Vertical Slice v2.1** | `COMPLETE` | Replay, Detectors, Fusion, Decision, RecoveryVerifier frozen. |
| **Phase 1.5** | **Rail Economics & Value Model Specification** | `COMPLETE` | `docs/RAIL_ECONOMICS_AND_VALUE_MODEL.md`, `master_context.md` (Phần 8). |
| **Phase 1.8** | **Fleet-Centric Case Architecture & Docs Alignment** | `COMPLETE` | 3 Data Layers, Dual-Clock Live Simulation, Screen 01-07 Specs, ActionGuard, CaseEvent Ledger, Expanded API Contracts. |
| **Phase 2** | **Backend Domain & API Contract Expansion (P0/P1)** | `COMPLETE` | AssetRegistry, ScenarioStream dual-clock, ActionGuard, CaseEvent ledger, `/api/operations`, `/api/case`, `/api/case/events`, `/api/case/close`. |
| **Phase 3** | **MongoDB Atlas Multi-Modal Integration** | `COMPLETE` | Time Series collection `measurements`, pipeline `$setWindowFields`, `operational_cases`, `case_events`, ingest script. |
| **Phase 4** | **Datadog Unified Observability Integration & v3.0 Backend Contracts** | `COMPLETE` | DogStatsD metrics, APM tracing, JSON logger; v3.0 API endpoints: `/api/telemetry/window`, `/api/telemetry/analytics`, `/api/action/guard-status`, `/api/case/work-order`, verified by `test_production_backend_v3.py`. |
| **Phase 5** | **Operations Command Console Frontend v3.0 (Zero-Hardcode & Human-in-the-Loop)** | `CODED — VERIFYING LIVE` | Xây dựng giao diện v3.0 chuẩn: Chart.js synchronized multi-channel strip charts, 3-pane workbench (Screens 01–07), Replay Studio Drawer (`Shift + S`), 100% data-driven binding, form tương tác Acknowledge / Work Order / Safe Mode / Root-Cause Sign-Off. |
| **Phase 6** | **Production-Ready Demo Hardening & Judging Runbook** | `IN PROGRESS` | Gates G1–G5 re-verified PASS on 1,516,948 rows (2026-11-06). Storytelling artifacts complete: RailOps VN blueprint, shot-by-shot video script, submission checklist, final deck. Remaining: live console rehearsal + record video. |
| **Phase 7** | **RailOps VN Enterprise Positioning & Vietnam Rail Re-Anchor** | `COMPLETE` | `docs/RAILOPS_VN_PLATFORM_BLUEPRINT.md`; Layer A fleet context re-anchored to Metro Line 1 (Bến Thành – Suối Tiên) with Lisbon dataset provenance preserved; standalone IoT producer `scripts/stream_telemetry.py`. |

---

## 5. Phase 5 Detailed Work Breakdown (v3.0 UI Realization)

1. **Task 5.1 — Core Layout & Header Command Strip (`src/static/index.html`):**
   - Breadcrumb phân cấp hạm đội: `Linha Azul / Train #302 / SUB-APU-01 / APU-COMP-01`.
   - Trạng thái luồng: `[ LIVE SIMULATION · HISTORICAL DATA · 0.1 Hz ]`.
   - Dynamic KPI strip: Monitored Assets, Active Cases, Operating Regime, Lead Window.
   - Drawer toggles: `Validation Reference Drawer` & `🎛️ Replay Studio Drawer` (`Shift + S`).
2. **Task 5.2 — Synchronized Strip Charts with Chart.js (`src/static/app.js`):**
   - Đồ thị chuỗi thời gian đa kênh: `DV_pressure`, `Oil_temp`, `Motor_current`.
   - Vùng phủ mờ nhận diện chế độ mang tải `LOADED` vs `UNLOADED`.
   - Đường ngưỡng cảnh báo động đọc từ `baselines`.
3. **Task 5.3 — 3-Pane Incident Investigation Workbench:**
   - **Left Pane:** Bối cảnh tài sản & 4 Thẻ Bằng Chứng động (`/api/evidence`).
   - **Center Pane:** Biểu đồ tương quan nhiệt động học + Bảng kiểm chứng 5 mẫu `LOADED` (`/api/recovery`).
   - **Right Pane:** Thao tác Human-in-the-Loop: Nút Acknowledge, Form Ghi chú điều tra, Bảng kiểm định 5 cổng ActionGuard (`/api/action/guard-status`), Form chọn Playbook/Work Order, Nút kích hoạt Safe Mode, Form ký duyệt Root Cause Sign-Off.
4. **Task 5.4 — Enterprise Replay Studio Drawer:**
   - Đóng gói toàn bộ nút Play/Pause, Speed (1x..300x), Bookmarks mốc sự cố (`00:33`, `09:50`, `10:15`, `16:05`), bộ chọn 4 kịch bản (`failure_3`, `failure_1`, `failure_4`, `healthy_baseline`).

---

## 6. Current Milestone & Next Action
- **Current Milestone:** Backend domain, MongoDB đa mô thức, Datadog observability và hợp đồng API v3.0 đã hoàn tất và kiểm chứng độc lập. Giao diện prototype v2.3 đã được gỡ bỏ; hệ thống đang tập trung nguồn lực xây dựng giao diện vận hành công nghiệp v3.0 (Phase 5).
- **Immediate Next Action:** Triển khai mã nguồn giao diện v3.0 (`src/static/index.html`, `src/static/styles.css`, `src/static/app.js`) tuân thủ nghiêm ngặt đặc tả tại [`docs/superpowers/specs/2026-10-11-prod-ready-ux-and-mechanism-design.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/docs/superpowers/specs/2026-10-11-prod-ready-ux-and-mechanism-design.md).
- **Positioning Action (2026-11-07):** Sản phẩm được định vị lại ở tầm vóc doanh nghiệp — **RailOps VN** là nền tảng, **CompressorGuard** là phân hệ lõi sống còn đã chứng minh end-to-end — neo vào vấn đề đường sắt Việt Nam có thật và kế hoạch triển khai 4 phase (`docs/RAILOPS_VN_PLATFORM_BLUEPRINT.md`).
- **Deadline Guard:** Danh sách artifact bắt buộc và cửa nghiệm thu trước khi nộp tại [`docs/SUBMISSION_CHECKLIST.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/docs/SUBMISSION_CHECKLIST.md). Hạn chót: **2026-11-08 23:59**.
