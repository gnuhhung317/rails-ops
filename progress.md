# CompressorGuard — Session Progress Log
> **Standard:** `planning-with-files` session ledger.

---

## Session: 2026-10-09 — Rail Economics & Value Model Integration

### Completed Actions:
1. **Rà Soát & Đánh Giá Toàn Diện (System Audit):**
   - Đánh giá hiện trạng dự án trên 4 trục: Demo (9.0/10), Business (6.5/10), Operational Realism (7.0/10), Product Maturity (6.0/10).
   - Xác định khoảng cách từ "Anomaly Prototype" sang "Industrial Operational Case".

2. **Chuẩn Hóa Bộ Khung Kinh Tế Đường Sắt (Rail Economics Synthesis):**
   - Tổng hợp 7 Value Pools từ NIST, DOE, IBM, Deloitte, GE Vernova và các case studies đường sắt thực tế (SNCF, Alstom, Hanoi Metro, MetroPT-3 paper, Shanghai Metro).
   - Thiết lập nguyên tắc bất biến: **Observed ≠ Modeled ≠ Verified**.
   - Xây dựng mô hình phân cấp tài sản: `FLEET` $\rightarrow$ `TRAIN` $\rightarrow$ `APU` $\rightarrow$ `COMPRESSOR`.

3. **Cập Nhật & Lưu Trữ Tài Liệu (Documentation SSOT Update):**
   - Tạo mới tệp đặc tả chuẩn: [`docs/RAIL_ECONOMICS_AND_VALUE_MODEL.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/docs/RAIL_ECONOMICS_AND_VALUE_MODEL.md).
   - Cập nhật [`master_context.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/master_context.md) bổ sung Phần 8: Rail Economics & Operational Value Model.
   - Cập nhật [`docs/PRODUCT_UX_SPEC.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/docs/PRODUCT_UX_SPEC.md) bổ sung Business Impact Model vào Phân tầng thông tin Tier 2 & Tier 3.

4. **Khởi Tạo Hệ Thống Kế Hoạch `planning-with-files`:**
   - Tạo [`task_plan.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/task_plan.md) định hình lộ trình master roadmap.
   - Tạo [`findings.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/findings.md) lưu trữ vĩnh viễn các phát hiện kinh tế và benchmark đường sắt.
   - Tạo [`progress.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/progress.md) ghi nhận tiến trình phiên làm việc.

---

## Session: 2026-10-09 — Fleet-Centric Case Architecture & Documentation Alignment

### Completed Actions:
1. **Chiến Lược Nâng Cấp Kiến Trúc Hạm Đội (Fleet Spine Architecture Alignment):**
   - Định hình lại chuỗi giá trị: $\text{Fleet} \rightarrow \text{Train} \rightarrow \text{APU} \rightarrow \text{Compressor} \rightarrow \text{Case} \rightarrow \text{Evidence} \rightarrow \text{Decision} \rightarrow \text{Action} \rightarrow \text{Recovery} \rightarrow \text{Operational Outcome}$.
   - Thiết lập nguyên tắc phân định nghiêm ngặt 3 tầng dữ liệu: **(A) Business Context** (Asset Registry), **(B) Observed Telemetry & Computed State**, và **(C) Validation Reference** (Ground Truth lịch sử không rò rỉ vào detector online).
   - Thiết kế kiến trúc **Hai Đồng Hồ (Dual-Clock Live Simulation)**: Bảo tồn nguyên vẹn `event_time` gốc lịch sử (MetroPT-3), điều tiết luồng phát bằng `simulation_time` theo $\Delta\text{event\_time}$ thực tế (tôn trọng gaps $>30$s), gắn nhãn minh bạch `[ LIVE SIMULATION · HISTORICAL DATA ]`.
   - Chuẩn hóa vai trò của ML (Isolation Forest trên 5 features có tải): **Independent Corroboration** (kiểm chứng độc lập làm tăng độ tin cậy quyết định; không tự ý tạo case).
   - Thiết lập hàng rào chính sách **ActionGuard** 5 điều kiện cho can thiệp mô phỏng (Simulated Intervention) rẽ nhánh sang dữ liệu sau bảo trì ngày 08/06/2020.
   - Chuẩn hóa thuật ngữ nghiệm thu: **Recovery Criteria Verified (5/5 healthy LOADED observations)** và thủ tục đóng Case giải phóng tài sản (`POST /api/case/close`).
   - Khởi tạo sổ cái sự kiện **CaseEvent** dạng append-only lưu vết toàn bộ diễn biến từ quan sát, can thiệp tới hồi phục.

2. **Đồng Bộ Hóa Toàn Diện Hệ Thống Tài Liệu (Full Documentation Synchronization):**
   - [`master_context.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/master_context.md): Cập nhật Phần 1, Phần 4, Phần 5, và Phần 7.
   - [`docs/PRODUCT_UX_SPEC.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/docs/PRODUCT_UX_SPEC.md): Nâng cấp lên Version 2.3.
   - Cập nhật toàn bộ bộ tệp đặc tả màn hình [`screen/`](file:///d:/Code/Projects/self-projects/iot-hackathon/screen/): `screen/01..07.md`.
   - [`findings.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/findings.md): Bổ sung Phần 4 về tiền lệ công nghiệp (Siemens, Maximo, Alstom).

---

## Session: 2026-10-09 — Phase 2: Backend Domain & API Contract Expansion

### Completed Actions:
1. **Asset Hierarchy Registry & Validation Ground Truth (`src/domain/registry.py`):**
   - Triển khai `FleetEntity`, `TrainEntity`, `SubsystemEntity`, `CompressorAssetEntity`.
   - Thiết lập `ValidationReference` tách biệt báo cáo hư hỏng Failure #3 của tập dữ liệu UCI khỏi trạng thái của detector online.
   - Cung cấp singleton `AssetRegistry.get_default()` và phương thức trích xuất cây phân cấp `get_asset_hierarchy_tree()`.
   - Hoàn tất kiểm thử: `tests/test_asset_registry.py` (2/2 passed).

2. **Deterministic Live Simulation Runner (`src/engine/simulation.py`):**
   - Thiết kế giao diện `ScenarioStream` và hiện thực `HistoricalScenarioStream`.
   - Triển khai `SimulationRunner` với cơ chế tính độ trễ $\Delta\text{event\_time} / \text{speed\_multiplier}$ bảo tồn nguyên gốc `event_time`.
   - Hỗ trợ các nút điều khiển tốc độ mô phỏng (1x, 10x, 60x, 300x) với giới hạn `max_step_delay_seconds`.
   - Hoàn tất kiểm thử: `tests/test_simulation_runner.py` (2/2 passed).

3. **Căn Chỉnh Quyết Định & Vai Trò Kiểm Chứng Độc Lập Của ML (`src/engine/decision.py`, `src/engine/detectors.py`):**
   - Đảm bảo Isolation Forest (5 features có tải) chỉ đóng vai trò **Independent Corroboration** nâng mức độ tin cậy quyết định và đề xuất can thiệp, tuyệt đối không tự tạo Case.
   - Bổ sung `provenance` thông tin nguồn gốc cho toàn bộ 4 detector (`PressureAnomalyDetector`, `ThermalStressDetector`, `TemporalStepDetector`, `IsolationForestDetector`).
   - Hoàn tất kiểm thử: `tests/test_decision_ml_corroboration.py` và `tests/test_evidence_provenance.py` (3/3 passed).

4. **Hàng Rào Chính Sách ActionGuard (`src/engine/action_guard.py`):**
   - Triển khai 5 tiêu chí chính sách (`CASE_CONFIRMED`, `MITIGATION_RECOMMENDED`, `SINGLE_ACTIVE_CASE`, `SIMULATION_MODE`, `REPLAY_BRANCH_AVAILABLE`).
   - Tích hợp vào `IncidentLifecycleManager.trigger_safe_mode()`.
   - Hoàn tất kiểm thử: `tests/test_action_guard.py` (1/1 passed).

5. **Sổ Cái Sự Kiện CaseEvent & Đóng Case Nghiệm Thu (`src/engine/lifecycle.py`, `src/domain/models.py`):**
   - Triển khai `CaseEvent` dạng append-only với các loại sự kiện `DETECTION`, `CORROBORATION`, `ACTION`, `RECOVERY`, `CASE_CLOSED`.
   - Triển khai `close_case()` cưỡng chế kiểm tra `recovery_verifier.is_verified == True` (ngăn đóng case sớm).
   - Chuẩn hóa serialization `event_time` thành ISO-8601 string.
   - Hoàn tất kiểm thử: `tests/test_case_events_ledger.py` (2/2 passed).

6. **Mở Rộng Bề Mặt REST API (`src/api/routes_product.py`, `src/api/schemas.py`):**
   - `GET /api/operations`: Cung cấp phân cấp hạm đội + bộ đếm vận hành trung thực + active case.
   - `GET /api/case`: Alias chuẩn nghiệp vụ cho `/api/incident`.
   - `GET /api/case/events` & `GET /api/timeline`: Sổ cái sự kiện vận hành.
   - `POST /api/case/close`: Đóng case có nghiệm thu (trả về 409 nếu chưa thỏa mãn).
   - `GET /api/validation-reference`: Ngăn kéo đối chiếu ground truth lịch sử.
   - Hoàn tất kiểm thử: `tests/test_operations_api.py` (2/2 passed).

7. **Kiểm Chứng Tính Nhất Quán Đặc Tả Màn Hình (`tests/test_screen_spec_consistency.py`):**
   - Kiểm chứng 100% tài liệu `screen/*.md` tuân thủ nguyên tắc trung thực: không fake `[🔴 LIVE]`, không fake 98% fleet health, đúng 5 features cho IF, có ActionGuard và CaseEvent ledger (1/1 passed).

8. **Kiểm Chứng Toàn Diện (Full Regression Suite):**
   - Chạy toàn bộ test suite: **59/59 pytest passed 100% in 100.95s** (zero regression).

---

## Session: 2026-10-09 — Phase 3: MongoDB Atlas Multi-Modal Integration

### Completed Actions:
1. **Thiết Kế Lớp Lưu Trữ Đa Mô Thức (`src/storage/`):**
   - [`src/storage/mongo_client.py`](file:///d:/Code/Projects/self-projects/iot-hackathon/src/storage/mongo_client.py): Kết nối MongoDB Atlas linh hoạt qua biến môi trường `MONGODB_URI` với cơ chế In-Memory fallback tự động khi cluster offline hoặc chạy test cục bộ.
   - Hàm `init_mongodb_schema()` tạo collection Time Series `measurements` (`timeField: "timestamp"`, `metaField: "metadata"`, `granularity: "seconds"`), document collection `operational_cases` và `case_events` với các index tối ưu.
2. **Hiện Thực Repository Pattern (`src/storage/repository.py`):**
   - Triển khai `CompressorGuardRepository` với đầy đủ phương thức nạp telemetry đơn lẻ/hàng loạt, lưu trữ và truy vấn Case theo `case_id`, quản lý sổ cái `case_events`.
   - Triển khai Aggregation Pipeline `$setWindowFields` tính toán giá trị trung bình trượt và độ lệch trượt trong cửa sổ 600 giây (`rolling_avg_dv`, `rolling_avg_oil_temp`).
3. **Liên Kết Với Domain Lifecycle Engine (`src/engine/lifecycle.py`):**
   - Tiêm phụ thuộc `repository` vào `IncidentLifecycleManager`.
   - Tự động đồng bộ hóa các sự kiện phát sinh (`DETECTION`, `CORROBORATION`, `ACTION`, `RECOVERY`, `CASE_CLOSED`) vào collection `case_events`.
   - Cập nhật tài liệu Case vào `operational_cases` khi đóng case.
4. **Script Nạp Dữ Liệu Lịch Sử (`scripts/ingest_historical_to_mongo.py`):**
   - Đọc dữ liệu chuỗi thời gian phân đoạn Failure #3 từ `ReplayEngine` và nạp hàng loạt (batch insert) vào MongoDB `measurements`.
   - Đã kiểm tra thực thi thành công nạp 50 điểm mẫu thử nghiệm.
5. **Kiểm Thử Toàn Diện (Full Regression Suite):**
   - Viết bộ kiểm thử chuyên biệt [`tests/test_mongodb_storage.py`](file:///d:/Code/Projects/self-projects/iot-hackathon/tests/test_mongodb_storage.py) (4/4 passed).
   - Chạy kiểm thử hồi quy toàn bộ hệ thống: **63/63 pytest passed 100%** (zero regression).

---

## Session: 2026-10-09 — Phase 4: Datadog Unified Observability Integration

### Completed Actions:
1. **DogStatsD Custom Metrics (`src/observability/metrics.py`):**
   - Triển khai `DatadogMetricsClient` hỗ trợ DogStatsD với bộ nhớ đệm ngoại tuyến an toàn `buffered_metrics` (zero crash khi agent offline).
   - Đo lường metrics thời gian thực: `compressorguard.telemetry.pressure_bar`, `compressorguard.telemetry.oil_temperature_c`, `compressorguard.ml.anomaly_score`, `compressorguard.incident.lead_time_seconds` (121,920s), `compressorguard.recovery.consecutive_observations`, `compressorguard.case.lifecycle_state`.
2. **APM Distributed Tracing (`src/observability/tracer.py`):**
   - Đóng gói client `ddtrace.tracer` với fallback Span context manager.
   - Thêm FastAPI APM tracing middleware tự động sinh span `fastapi.request` cho toàn bộ endpoint HTTP.
3. **Structured JSON Logging (`src/observability/logger.py`):**
   - Triển khai `DatadogJSONFormatter` tự động gắn `dd.trace_id`, `dd.span_id`, `dd.service`, `dd.env` vào từng log record.
4. **Monitors & Dashboard Definitions (`datadog/`):**
   - [`datadog/monitors.json`](file:///d:/Code/Projects/self-projects/iot-hackathon/datadog/monitors.json): Định nghĩa monitor cảnh báo sớm áp suất (`Early Warning Pressure Breach`) và kiểm chứng hồi phục (`Recovery Criteria Verified`).
   - [`datadog/dashboard.json`](file:///d:/Code/Projects/self-projects/iot-hackathon/datadog/dashboard.json): Layout 6 widget hiển thị tình trạng hạm đội, biểu đồ áp suất, điểm dị thường ML, thời gian can thiệp xác nhận, và chuỗi hồi phục.
5. **Tối Ưu Hóa Tốc Độ Kiểm Thử (Performance Breakthrough):**
   - Khắc phục bottleneck tải lại file CSV (1.5M dòng) bằng cách tái sử dụng instance `ReplayEngine` trong `HistoricalScenarioStream`.
   - Giảm thời gian chạy test suite từ >8 phút xuống còn **21.78 giây** cho 76 test.
6. **Kiểm Thử Toàn Diện (Full Regression Suite):**
   - Viết bộ kiểm thử chuyên biệt [`tests/test_datadog_observability.py`](file:///d:/Code/Projects/self-projects/iot-hackathon/tests/test_datadog_observability.py) (5/5 passed).
   - Chạy kiểm thử hồi quy toàn bộ hệ thống: **76/76 passed in 21.78s** (zero regression).

---

## Session: 2026-10-09 — Phase 5: Operations Command Console Frontend (Web UI)

### Completed Actions:
1. **Kiến Trúc Web Console Hiện Đại Không Cần Build (Zero-Build Modern SPA):**
   - [`src/static/index.html`](file:///d:/Code/Projects/self-projects/iot-hackathon/src/static/index.html): Xây dựng khung giao diện chuẩn Enterprise APM tích hợp Tailwind CSS, fonts Inter & JetBrains Mono, Dark Mode sắc nét.
   - [`src/static/styles.css`](file:///d:/Code/Projects/self-projects/iot-hackathon/src/static/styles.css): Định nghĩa hệ thống màu carbon, hiệu ứng pulse cho trạng thái khẩn cấp, badge trạng thái, thanh cuộn tùy chỉnh và drawer mượt mà.
   - [`src/static/app.js`](file:///d:/Code/Projects/self-projects/iot-hackathon/src/static/app.js): Động cơ SPA phản ứng với state store toàn diện, client API, vòng lặp phát dòng hai đồng hồ, toast alerts, và điều phối các view.
2. **Hiện Thực Hóa 100% Đặc Tả 7 Màn Hình (`screen/01..07.md`):**
   - **Screen 01 (Operations Landing):** Cây phân cấp hạm đội Linha Azul $\rightarrow$ Train #302 $\rightarrow$ APU $\rightarrow$ APU-COMP-01, bộ đếm vận hành trung thực, Panel trình diễn chống báo động ảo lúc 00:33:07 (Noise Rejection Demo).
   - **Screen 02 (Active Cases):** Bất biến Siemens Senseye (tối đa 1 case/asset), thẻ Case đang mở kèm nút mở Workspace, bảng lịch sử Case đã giải quyết.
   - **Screen 03 (What Changed?):** Phân tầng 4 khối thông tin: Observed Telemetry $\rightarrow$ Operational Condition $\rightarrow$ Business Context $\rightarrow$ Validation Reference; Hero metric 33h 52m.
   - **Screen 04 (Why? Evidence):** 4 thẻ bằng chứng vật lý kèm Provenance đầy đủ (Áp suất +23.75σ, Nhiệt độ +5.71σ, Bước nhảy 3/3 chu kỳ, ML Isolation Forest 0.382 trên 5 features có tải) + Sơ đồ chuỗi nhân quả nhiệt động lực học.
   - **Screen 05 (What Did We Do?):** Hàng rào 5 kiểm định ActionGuard + Nút bấm kích hoạt Safe Mode mô phỏng rẽ nhánh sang dữ liệu sau bảo trì ngày 08/06/2020.
   - **Screen 06 (Did It Work?):** Thanh tiến độ kiểm chứng tiêu chí hồi phục 5/5 quan sát mang tải LOADED + Nút nghiệm thu đóng Case và giải phóng tài sản về HEALTHY.
   - **Screen 07 (Case Timeline):** Sổ cái `CaseEvent` biên niên sử kiểu Datadog Incident Timeline.
   - **Validation Reference Drawer:** Ngăn kéo trượt hiển thị chi tiết đối chứng lịch sử Failure #3 từ dataset MetroPT-3.
3. **Mở Rộng Backend API & Static Mounting:**
   - [`src/api/app.py`](file:///d:/Code/Projects/self-projects/iot-hackathon/src/api/app.py): Mount `/static`, cấu hình `GET /` và `GET /console` trả về Web Console SPA, giữ `GET /health` làm JSON health probe.
   - [`src/api/routes_demo.py`](file:///d:/Code/Projects/self-projects/iot-hackathon/src/api/routes_demo.py): Bổ sung `/demo/play`, `/demo/pause`, `/demo/speed`, `/demo/status`.
4. **Tối Ưu Hóa & Khắc Phục Lỗi Tồn Đọng (Bug Fixes & Hardening):**
   - Khắc phục lỗi so sánh offset-naive và offset-aware datetime trong pipeline `$sort` của `InMemoryCollection`.
   - Bổ sung toán tử `$nin` và `$in` trong bộ lọc truy vấn của `InMemoryCollection`.
   - Cập nhật truy vấn `get_active_case_for_asset` loại trừ cả hai trạng thái `RESOLVED` và `CLOSED`.
   - Thêm cơ chế tự động dọn dẹp các Case cũ khi gọi `manager.reset()`.
5. **Kiểm Thử Toàn Diện (Full Regression Suite):**
   - Viết bộ kiểm thử chuyên biệt [`tests/test_web_console_integration.py`](file:///d:/Code/Projects/self-projects/iot-hackathon/tests/test_web_console_integration.py) (4/4 passed).
   - Chạy kiểm thử toàn bộ hệ thống: **91/91 passed in 45.55s** (100% pass rate, zero regression).



---

## Session: 2026-10-17 — Roadmap & v3.0 Production-Ready Specification Reconciliation

### Completed Actions:
1. **Phân Tích & Giải Quyết Bất Đồng Giữa `task_plan.md` và Đặc Tả UI/UX v3.0 (11/10/2026):**
   - Xác định nguyên nhân gốc rễ: Trạng thái Phase 1–6 `COMPLETE` trong `task_plan.md` được lập từ ngày 09/10/2026 cho bản prototype sơ khởi.
   - Bản chẩn đoán ngày 11/10/2026 (`docs/superpowers/specs/2026-10-11-prod-ready-ux-and-mechanism-design.md`) đã chỉ ra 5 khiếm khuyết lớn của giao diện cũ: dữ liệu hardcode tĩnh (~90%), thiếu biểu đồ chuỗi thời gian Chart.js, thiếu tương tác Human-in-the-Loop, và nút điều khiển demo trên header tạo cảm giác auto-pilot slideshow.
   - Mã giao diện cũ đã được thu hồi; backend đã hoàn tất mở rộng các endpoint động v3.0 (`/api/telemetry/window`, `/api/telemetry/analytics`, `/api/action/guard-status`, `/api/case/work-order`) và kiểm chứng qua `tests/test_production_backend_v3.py`.
2. **Cập Nhật Master Roadmap ([`task_plan.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/task_plan.md)):**
   - Giữ Phase 1–4 là `COMPLETE`.
   - Mở lại Phase 5 thành `IN PROGRESS` với phạm vi công việc chi tiết cho giao diện v3.0: Zero Hardcoded Data, Synchronized Strip Charts (Chart.js), 3-Pane Incident Investigation Workbench, Replay Studio Drawer (`Shift + S`), và luồng Human-in-the-Loop 4 bước.
   - Chuyển Phase 6 sang `PENDING PHASE 5`.
3. **Thiết Lập Quy Tắc Cho Agent ([`AGENTS.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/AGENTS.md)):**
   - Cưỡng chế quy tắc: **Không tự ý chạy `pytest` trần** trên toàn bộ repository (tránh nghẽn CPU và timeout do nạp file CSV 1.5 triệu dòng).
   - Thiết lập các nguyên tắc bất biến (Zero Fake Telemetry, Decoupled Producer-Consumer, 3 Data Layers, ActionGuard, Human-in-the-Loop, Zero Hardcoded UI).
4. **Cập Nhật Làm Giàu Sổ Cái Phát Hiện ([`findings.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/findings.md)):**
   - Bổ sung Phần 5 phân tích chi tiết khoảng cách kỹ thuật giữa bản prototype v2.3 và kiến trúc công nghiệp v3.0.


---

## Session: 2026-11-07 — RailOps VN Enterprise Positioning, Vietnam Re-Anchor & Producer Completion

### Critical finding corrected
- **`src/static/` was empty on disk.** Commits `633ec61`/`d5989df` described a finished SPA and "98/98 passing", but the v3.0 interface had been removed on 11/10 and never rebuilt. Recorded start point: commit `f48d74c`, tag `backup/start-point-20261107`.
- **Action:** rebuilt the v3.0 console (`index.html` 31 KB, `styles.css` 33 KB, `app.js` 86 KB) against the real API contracts. Static audit confirms `node --check` clean, all 23 endpoints bound, and **no hardcoded telemetry values**.

### Deliverables added
1. **`docs/RAILOPS_VN_PLATFORM_BLUEPRINT.md`** — platform positioning (RailOps VN ⊃ CompressorGuard), real Vietnamese rail evidence with sources, IoT edge module design, MongoDB/Datadog role justification, 4-phase rollout to ĐSCT Bắc–Nam, rubric mapping 30/30/30/10, and the 4 questions BGK will ask with defenses.
2. **Vietnam re-anchor (Layer A only):** fleet/operator/depot/playbook labels moved from Lisbon Metro to `RailOps VN — Metro Line 1 (Bến Thành – Suối Tiên) · HURC1 · Depot Long Bình`. Physics and dataset provenance untouched; `is_illustrative_context` retained and the note now names MetroPT-3 origin explicitly. Files: `src/domain/registry.py`, `src/api/schemas.py`, `src/api/app.py`, `src/engine/lifecycle.py`, `src/storage/mongo_client.py`, `datadog/*.json`, `screen/*`, pitch runbook.
3. **`scripts/stream_telemetry.py`** — the decoupled IoT/realtime producer referenced by `docs/ARCHITECTURE.md` and the v3.0 spec but never implemented. Dual-clock stamped frames, MongoDB persistence, MQTT edge topic with store-and-forward buffer, plus a `--mode remote` control harness.
4. **`docs/DEMO_VIDEO_SCRIPT.md`** — 10 timed shots (5:00) + 2:30 cut, shot→rubric mapping, banned phrasings, and the 5 failure modes that make a demo read as a toy.
5. **`docs/SUBMISSION_CHECKLIST.md`** — required artifacts vs. evidence, gates command, ranked remaining work against the 08/11 deadline.

### Verification performed
- `python scripts/verify_evaluation_gates.py` → **G1–G5 ALL PASSED**, `ReplayEngine loaded 1,516,948 rows`.
- `python scripts/stream_telemetry.py --scenario failure_3 --speed 300 --hours 0.4` → 146 frames / 5.3 s, transitions `NONE → DETECTED → INVESTIGATING`, real values (`dv=2.316 bar`, `oil=72.35 °C`).
- Targeted tests (per the AGENTS.md no-bare-pytest rule): `test_asset_registry`, `test_registry_boundary`, `test_action_guard`, `test_screen_spec_consistency` → **3/3 then 6/6 passed** after re-anchor fix.
- `datadog/dashboard.json` and `monitors.json` re-validated as parseable JSON after edit.

### Outstanding before submission
- Live click-through of the rebuilt console through all four Human-in-the-Loop steps, then record the demo video.
- Confirm the 12-slide deck artifact is complete.

---

## Session close-out — 2026-11-06 17:38 UTC (Phase 5 verified live, Phase 6 code-complete)

### Deliverables landed this block
- `scripts/build_pitch_deck.py` — deterministic deck generator; regenerated `docs/railops-vn-final-deck.pptx` to **12 slides**, scanned clean of CJK/full-width leftovers (slide 4 header defect fixed).
- `scripts/verify_console_journey.py` — new HTTP-level operator-journey verifier (23 assertions), runnable by anyone with a live server.
- `src/static/vendor/chart.umd.min.js` — Chart.js 4.4.1 vendored; console no longer depends on a CDN at demo time.

### Console verified in a real browser (not just statically)
- Boot: `python -m uvicorn src.api.app:create_app --factory --port 8021` (note: `src.api.app` exposes a factory, so `--factory` is required).
- 6 Chart.js canvases rendering, 42 data-bound nodes, **0 empty bindings**, **0 console errors**.
- Replay Studio drawer: 4 scenarios + 5 dynamically built bookmarks (`early_excursion_0033`, `onset_0950`, `ml_corroborated_1015`, `lps_reactive_1942`, `post_maintenance_1605`); clicking a bookmark and Play/Pause by mouse advanced the cursor to `2020-06-05 09:50:49` with 66 samples emitted.
- Layer C Validation Reference drawer carries the explicit "never fed to detectors" statement.
- Header main strip contains no simulation controls (invariant 7 holds).

### Journey verification result: 23/23 PASSED (17:37 UTC)
Key evidence captured by the run: premature Safe Mode -> **HTTP 409** and asset still in revenue service;
case opened from real CSV telemetry `APU-INC-20200605-01`; **lead_time 33h 52m**; 4 evidence cards;
rolling `rolling_avg_dv`/`rolling_std_dv` per frame; dual clock proven on the wire
(`timestamp` 2020-06-08 vs `ingested_at` 2026-11-06); ActionGuard **5/5**; Safe Mode permitted ->
MITIGATING; recovery **5/5 healthy LOADED**; sign-off -> `RESOLVED` / `HEALTHY`; ledger **10 events**.

### Consistency fixes found by looking rather than assuming
- API version was reported as `2.1.0` by `/health` while the app declared `2.2.0`; both now read from
  a single source (`app.version`) and the app is declared **3.0.0** with the platform-first title.
- Console `<title>` and brand strip now lead with **RAILOPS VN** while CompressorGuard stays the subsystem name.
- Meta description no longer labels the fleet as "Lisbon Metro"; dataset provenance statements elsewhere keep Lisbon verbatim.
- A `PMO-DEPOT-LISBON-01` option seen once in the depot dropdown was stale in-memory state from the prior journey run; after reset the dropdown reads `Depot Long Bình` / `DEPOT-LONGBINH-01` only. No literal remains in `src/`.
- Targeted test `tests/test_asset_registry.py` -> 2 passed (no bare pytest, per AGENTS.md).

### What is genuinely left
1. **Record the 5:00 demo video** — the only required artifact that cannot be automated here.
2. **Push the branch** and confirm judges can open the repository.

---

## 2026-11-06 17:46 UTC — Claim audit against the official rules

### Official requirement reconciliation (`docs/SUBMISSION_CHECKLIST.md`)
Four required artifacts, not three: repository, demo video, slides, **README**. Submission goes
through **https://forms.gle/7JHbcihzVA3uGTPw6** before 2026-11-08 23:59; team size 1–3. All four
now appear in the artifact table with an evidence path.

### Defects found and fixed (docs + deck only, no product code touched)
- Deck slide 3 claimed the 1.541 km North–South line was **under construction**. It is not:
  investment policy approved (NQ 172/2024/QH15), 31/12/2026 groundbreaking target officially
  assessed as "rất khó khăn". Reworded — the corrected claim argues *the design window is
  closing*, which is a stronger impact story than the overstated one.
- Two garbled Vietnamese strings from an earlier edit ("mỗi cách缺一…", "BỐN TỨA ĐIỂM") fixed;
  slide 11 header said "Bốn phase" over a five-row table (phase 0 is already done).
- `docs/PITCH_DECK_AND_DEMO_RUNBOOK.md` told the presenter to point at an **"Economic Value card"
  showing €193,600 in the UI.** No such card exists — verified by grepping `src/`, `scripts/`,
  `data/` for every euro figure: zero hits. That instruction would have failed live on stage, so it
  now points at the audit ledger instead. The euro rows are labelled as our own modelled
  assumptions, matching the rule `docs/RAIL_ECONOMICS_AND_VALUE_MODEL.md` already states
  (label `Estimated Avoided Cost (Scenario Model)`, never `Realized Profit`).
- README table header put €193,600 under **"Measured Result"** — the project's own integrity rule
  forbids that framing. Relabelled "Avoided Cost (Scenario Model) — projected, not realized".

### New deliverable: presenter script embedded in the deck
12 Vietnamese speaker notes (4,970 chars) with cumulative timings summing to exactly 3:00 and one
pre-empted judge question per slide, generated by `SPEAKER_NOTES` in `scripts/build_pitch_deck.py`
so it stays in sync with the slides. This closes the checklist's "read through once at exactly
3 minutes" item — rehearse from Presenter View instead of a second, diverging script.
Verified: 12 slides, notes on every slide, zero CJK residue, table geometry fits inside the canvas.

### Two blockers found that no amount of polishing would have hiding
1. **`git remote -v` is empty.** There is no hosted repository anywhere. The first required
   artifact — a repo the judges can open — has existed only on this machine for all 45 commits.
   Creating and pushing the public repo is a shared-state action, so it needs the owner's go-ahead.
2. **The 208 MB MetroPT-3 CSV is gitignored**, so a fresh clone cannot run. `run_demo.py` already
   fails loudly with the expected path; README now states the source
   (doi:10.1038/s41597-022-01877-3), the exact target filename, and the 1,516,948-row check
   so the person doing the push can verify it in one command instead of discovering it live.

### Fresh-clone readiness (the artifact-1 gap nobody was looking at)
`git ls-files` for every runtime file came back clean **except** the dependency manifest: there was
**no `requirements.txt`, no `pyproject.toml` — nothing**. A judge cloning the repo had no supported
way to install fastapi/uvicorn/pandas/numpy/scikit-learn/pymongo, which quietly invalidates the
"1-click turnkey" headline in README.
- Built `requirements.txt` from the versions actually imported by `src/ scripts/ tests/` and actually
  installed on this machine (Python 3.12.4), so the pins are evidence, not decoration. `paho-mqtt` is
  the one entry **not** exercised here: it isn't installed, so live publish is unverified — recorded as
  🟡 in the checklist instead of ✅. Its `<2` ceiling is forced by `mqtt.Client()` being the 1.x API.
- Verified resolution: `pip install --dry-run -r requirements.txt` solves with only paho-mqtt-1.6.1 to add.
- `run_demo.py` preflight now checks imports **before** the dataset and exits with the exact pip command;
  tested both branches (present → OK; simulated missing → `[ERROR] Missing Python dependencies:
  scikit-learn` + exit 1). Previously a missing package surfaced as a raw ImportError mid-boot.
- `demo.bat` window title still said "CompressorGuard — Lisbon Metro"; now RailOps VN-first, matching
  the branding rule applied to `index.html` and the API metadata.
- Secret scan before any public push: no tracked `.env`/key/token files and no credential-shaped
  literals in non-markdown tracked files. Safe to go public.

### IoT module claim made true instead of restated
The "Module IoT" row was supported by the presence of code, not by execution: `paho-mqtt` had never
been installed here, so `EdgePublisher` had never constructed a real client. Installed 1.6.1 (matching
the pin) and added `tests/test_edge_publisher.py` -> **5 passed**: buffer cap keeps newest frames,
topic equals `railops/{fleet}/{asset}/telemetry`, a live client drains the buffer at QoS 1, and —
against a real paho client pointed at a closed port — an unreachable broker degrades to store-and-forward
without raising. Honest boundary kept in the checklist: **no real-broker round trip**, because this
machine has no mosquitto.
`pytest --collect-only -q` says the suite holds **107** tests, so README's "96+" floor was replaced with
the counted number plus a warning that the full suite replays the 1.5M-row CSV and the two fast
verifiers are the better evidence moment.
Also caught and removed one CJK fragment I had just written into the checklist — the same defect class
I fixed in the deck, which is why the deck scan is now routine before committing docs.

### Regression re-proof after the documentation/launcher/test changes (17:54 UTC)
Restarted the console on a spare port (`/health` -> RailOps VN title, version 3.0.0) and re-ran
`scripts/verify_console_journey.py`: **23/23 again**, same evidence as 17:37 UTC
(409 on premature Safe Mode, `APU-INC-20200605-01`, lead time 33h 52m, dual clock on the wire,
ActionGuard 5/5, recovery 5/5 healthy LOADED, `RESOLVED`/`HEALTHY`, 10 ledger events).
Server stopped after the run; no product code changed between the two runs.
`task_plan.md` Phase 6 now states the real blocker instead of "push the branch": there is no remote.

### Visual QA of the deck — render, don't reason (18:00 UTC)
Exported all 12 slides to PNG through PowerPoint 16 COM and actually looked at each one, instead of
trusting geometry. This was the first time the deck was seen as pixels; every prior "verification"
was coordinate arithmetic.

The render caught a defect arithmetic could not: the `("t", …)` branch in `bullets()`
(scripts/build_pitch_deck.py) built a throwaway textbox and then executed `pass`, so **four content
lines were silently dropped from the deck** while the generator still reported success:
- slide 5 — the Phase 2–4 shared-engine subsystem list, and the MongoDB/Datadog/IoT-edge stack line
- slide 8 — the vibration/acoustic retrofit caveat (Layer C, never leaks into the online detector)
- slide 12 — the explicit rubric mapping (30 Sáng tạo / 30 Kỹ thuật / 30 Tác động / 10 Trình bày)
The slide-12 loss was the expensive one: the deck no longer answered the scoring rubric on the Ask
slide, and nothing in the build output hinted at it. Fixed by rendering `"t"` as an indented sub-line
of the heading above it; re-exported and re-read slides 5, 8, 12 to confirm the text is on screen.

All 12 slides now verified: no overflow past the margins, no clipped table cells, no Vietnamese
diacritic tofu, no CJK. Speaker notes present on 12/12. Committed `docs/railops-vn-final-deck.pdf`
(154 KB) as the font-independent submission artifact so the judges see exactly what was QA'd.
Checklist row 1 commit count corrected 45 -> 49 with the counting command, so it cannot silently rot.
