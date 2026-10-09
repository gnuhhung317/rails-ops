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

