# Task Plan: CompressorGuard Reasoning Engine Stabilization

## Problem Statement & Objective
Khắc phục triệt để 3 lỗi P0 kiến trúc và toàn bộ 15 điểm rà soát được đưa ra trong critique:
1. Sửa Isolation Forest trigger contract (`score > 0.35` thay vì `> 0.0`).
2. Tái cấu trúc DecisionEngine có nhận `IncidentContext` để phân định rõ ràng các lifecycle transition (`CREATE`, `UPDATE_INVESTIGATING`, `CRITICAL_REACTIVE`, v.v.).
3. Chuẩn hóa detectors: Pressure & Thermal dùng `latest` telemetry; Temporal dùng `mean(recent) - mean(past)`; đổi tên `TEMPORAL_STEP_CONFIRMED`.
4. Chuẩn hóa `EvidenceCode` enum, tăng tính chặt chẽ cho model contract và audit provenance.
5. Sửa tính portable và reproducible của ReplayEngine (loại bỏ hardcoded Windows path, sort timestamp tường minh).
6. Viết bộ test suite hoàn chỉnh bao gồm `test_regime.py`, fix `test_decision.py`, và chạy `test_golden_path.py` 2 lần liên tiếp để đảm bảo 100% deterministic.

---

## Phase Breakdown

### Phase 1: Domain Contracts & Model Hardening
- [x] 1.1 Thêm `EvidenceCode` enum vào [enums.py](file:///d:/Code/Projects/self-projects/iot-hackathon/src/domain/enums.py) (bao gồm `PRESSURE_SEVERE`, `PRESSURE_HIGH`, `PRESSURE_ELEVATED`, `THERMAL_STRESS_SEVERE`, `THERMAL_STRESS_ELEVATED`, `TEMPORAL_STEP_CONFIRMED`, `ML_CORROBORATED`, `LPS_TRIGGERED`, `NORMAL`).
- [x] 1.2 Tạo `IncidentContext` model trong [models.py](file:///d:/Code/Projects/self-projects/iot-hackathon/src/domain/models.py) (`active_incident_id`, `lifecycle_state`).
- [x] 1.3 Cập nhật `DetectorResult` trong [models.py](file:///d:/Code/Projects/self-projects/iot-hackathon/src/domain/models.py) dùng `EvidenceCode`.
- [x] 1.4 Cập nhật `BaseDecisionEngine` trong [contracts.py](file:///d:/Code/Projects/self-projects/iot-hackathon/src/domain/contracts.py) để nhận `incident_context: Optional[IncidentContext] = None`.
- **Status**: complete

### Phase 2: Detectors Refactoring & Semantic Alignment
- [x] 2.1 Cập nhật [detectors.py](file:///d:/Code/Projects/self-projects/iot-hackathon/src/engine/detectors.py):
  - `PressureAnomalyDetector`: dùng `latest.dv_pressure_bar` thay vì `min()`.
  - `ThermalStressDetector`: dùng `latest.oil_temp_c` thay vì `min()`.
  - `TemporalStepDetector`: dùng `mean(recent) - mean(past)`, đặt `allowed_regime_gaps=0`, kiểm tra persistence floor trên các recent samples, emit `TEMPORAL_STEP_CONFIRMED`, bổ sung đầy đủ provenance (cycles, timestamps, gap count).
  - `IsolationForestDetector`: chuẩn hóa scale 10x cho `decision_function`, nhận `score_threshold=0.35`, trigger `if score > self.score_threshold`, baseline_value gán `self.score_threshold`.
- **Status**: complete

### Phase 3: Decision Engine Refactoring
- [x] 3.1 Cập nhật [decision.py](file:///d:/Code/Projects/self-projects/iot-hackathon/src/engine/decision.py):
  - Nhận `incident_context: Optional[IncidentContext] = None`.
  - Sửa `confirmed_degradation = (has_severe_pressure and has_any_thermal and has_temporal_step)`.
  - Bổ sung tracking trạng thái severe khi incident đã active (`confirmed_degradation or (has_active_incident and has_severe_pressure and has_any_thermal)`).
  - Rule 2 (ML Corroboration) yêu cầu `has_severe_pressure and has_severe_thermal and has_ml` theo đúng Table 3 của frozen spec.
  - Logic phân loại hành vi theo ngữ cảnh:
    - Nếu chưa có incident: `confirmed_degradation` -> `IncidentAction.CREATE`.
    - Nếu đã có incident: duy trì `CRITICAL`, confidence `MEDIUM`, không trigger `CREATE` lặp lại (`IncidentAction.NONE`).
    - Khi có ML corroboration: `IncidentAction.UPDATE_INVESTIGATING` với `OperationalConfidence.HIGH`.
    - Khi có LPS: `IncidentAction.UPDATE_INVESTIGATING` với `OperationalConfidence.CRITICAL_REACTIVE`.
- **Status**: complete

### Phase 4: Replay Engine Portability & Upstream Validation
- [x] 4.1 Cập nhật [replay.py](file:///d:/Code/Projects/self-projects/iot-hackathon/src/engine/replay.py):
  - Dùng `pathlib.Path` tính relative path mặc định tới `dataset/MetroPT3(AirCompressor).csv`.
  - Đảm bảo `self.df.sort_values("timestamp").reset_index(drop=True)`.
- [x] 4.2 Tạo file test `tests/test_regime.py` kiểm tra phân loại `classify_regime` trên tất cả các nhánh (`OFF`, `STARTING`, `OFF_LOAD`, `LOADED`, `TRANSIENT`).
- **Status**: complete

### Phase 5: Verification & End-to-End Determinism
- [x] 5.1 Cập nhật `tests/test_decision.py` truyền đúng `EvidenceCode` và test các kịch bản có/không có `IncidentContext`.
- [x] 5.2 Cập nhật `tests/test_golden_path.py` đồng bộ với contract mới (`IncidentContext`, `TEMPORAL_STEP_CONFIRMED`, `score_threshold=0.35`).
- [x] 5.3 Chạy toàn bộ pytest suite (12 tests) và kiểm tra 2 lần liên tiếp để đảm bảo 100% deterministic passing.
- **Status**: complete

### Phase 6: Domain API & Demo Endpoints (Task 3)
- [x] 6.1 Tạo integration test suite `tests/test_api_vertical_slice.py` bao phủ 10 bước golden path cùng các negative test cases.
- [x] 6.2 Thực thi TDD RED và xác nhận fail collection.
- [x] 6.3 Tạo Pydantic schemas tại `src/api/schemas.py` tuân thủ PRODUCT_UX_SPEC v2.1.
- [x] 6.4 Triển khai Product Domain Endpoints tại `src/api/routes_product.py` (`/api/incident`, `/api/evidence`, `/api/action/safe-mode`, `/api/recovery`).
- [x] 6.5 Triển khai Demo Simulation Endpoints tại `src/api/routes_demo.py` (`/demo/reset`, `/demo/tick`, `/demo/jump`).
- [x] 6.6 Triển khai FastAPI Application Factory tại `src/api/app.py` với exception handling cho `InvalidStateTransitionError` (409) và `ValueError` (400).
- [x] 6.7 Thực thi TDD GREEN và xác minh 100% test pass.
- **Status**: complete

