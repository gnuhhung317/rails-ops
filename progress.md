# Progress Log: CompressorGuard Reasoning Engine Stabilization

## Session Summary (Initial Assessment & Plan Setup)
- **Time**: 2026-10-05T22:16:00+07:00
- **Action**: Đã tiến hành review toàn bộ 15 điểm rà soát từ người dùng, đối chiếu với code hiện tại và dataset `MetroPT3(AirCompressor).csv`.
- **Key Findings**:
  - Dữ liệu 191 sample liên tiếp tại cửa sổ 09:48:30 - 10:20:00 đều là `LOADED`, không có gap -> xác nhận `allowed_regime_gaps=0` là tối ưu.
  - Tại 09:50, `Oil_temperature` là ~71-73 °C (`THERMAL_STRESS_ELEVATED`), đạt `SEVERE` (>74 °C) sau ~10:00 -> điều kiện `has_any_thermal` trong `confirmed_degradation` là hoàn toàn chính xác.
  - Phân tích nguyên nhân `test_decision.py` fail là do thiếu `evidence_code` trong khởi tạo mock detector result.
  - Đã khởi tạo `findings.md` và `task_plan.md`.

## Implementation & Stabilization Phase
- **Time**: 2026-10-05T22:34:00+07:00
- **Actions Completed**:
  - **Phase 1**: Thêm `EvidenceCode` enum (`enums.py`), `IncidentContext` model (`models.py`), cập nhật `DetectorResult` và `BaseDecisionEngine` contract (`contracts.py`).
  - **Phase 2**: Refactor `PressureAnomalyDetector` và `ThermalStressDetector` sử dụng `latest` telemetry thay vì `min()`. Chuẩn hóa `TemporalStepDetector` dùng `mean(recent) - mean(past)` kèm kiểm tra persistence floor trên các recent samples để loại bỏ false positive từ nhiễu spike 1-sample tại 00:33:07. Chuẩn hóa `IsolationForestDetector` với hệ số scale 10x cho `decision_function`, ngưỡng `score_threshold=0.35` (tại 10:15 đạt score 0.382 > 0.35, tại 00:33 là 0.0).
  - **Phase 3**: Refactor `DecisionEngine.evaluate()` nhận `IncidentContext`. Triển khai đúng ma trận ưu tiên:
    - Chưa có incident: `confirmed_degradation` (`PRESSURE_SEVERE` + `THERMAL_STRESS_*` + `TEMPORAL_STEP_CONFIRMED`) -> `IncidentAction.CREATE`.
    - Đã có incident: duy trì `CRITICAL`, confidence `MEDIUM`, không spam `CREATE`.
    - Khi có ML corroboration (`PRESSURE_SEVERE` + `THERMAL_STRESS_SEVERE` + `ML_CORROBORATED`): `IncidentAction.UPDATE_INVESTIGATING`, `OperationalConfidence.HIGH`.
    - Khi có LPS (`LPS_TRIGGERED`): `IncidentAction.UPDATE_INVESTIGATING`, `OperationalConfidence.CRITICAL_REACTIVE`.
  - **Phase 4**: Chuyển `CSV_PATH` sang relative path tự động resolve từ project root; thêm explicit sort timestamp `.sort_values("timestamp").reset_index(drop=True)` trong `ReplayEngine.load_data()`. Tạo unit test suite `tests/test_regime.py`.
  - **Phase 5**: Viết lại `tests/test_decision.py` với 6 test cases bao phủ đầy đủ lifecycle và context. Cập nhật `tests/test_golden_path.py` đồng bộ với `IncidentContext`.
- **Test Suite Results**:
  - `pytest tests/test_regime.py tests/test_decision.py tests/test_golden_path.py -s`:
    - **12/12 passed** (0 failed, 100% pass rate in 136.56s).
    - Cả 2 lần chạy mô phỏng Failure #3 đều giống hệt nhau (`m1 == m2`), khẳng định 100% deterministic reproducibility.

## Task 3: Domain API & Demo Endpoints Implementation
- **Time**: 2026-10-07T00:54:00+07:00
- **Actions Completed**:
  - **Integration Test**: Tạo `tests/test_api_vertical_slice.py` bao phủ trọn vẹn 10 bước của 90-second Golden Path, cùng các negative test cases (invalid milestone -> 400 Bad Request, invalid safe-mode state transition -> 409 Conflict).
  - **TDD Workflow**: Chạy RED trước khi triển khai (xác nhận `ModuleNotFoundError: No module named 'src.api'`), sau đó chuyển sang GREEN khi triển khai xong `src/api/`.
  - **Pydantic Schemas (`src/api/schemas.py`)**: Định nghĩa các schemas đồng bộ chặt chẽ với `docs/PRODUCT_UX_SPEC.md` v2.1: `IncidentResponse`, `LeadTimeInfo`, `EvidenceResponse`, `EvidenceSignalItem`, `PersistenceInfo`, `SafeModeResponse`, `RecoveryResponse`, `LatestTelemetry`, `RecoveryCriteriaInfo`, `ResetRequest`, `ResetResponse`, `TickResponse`, `JumpRequest`, `JumpResponse`, `ErrorResponse`.
  - **Product Domain Endpoints (`src/api/routes_product.py`)**:
    - `GET /api/incident`: Trả về current incident state, asset health, confidence, lead time (33h 52m / 2032 min).
    - `GET /api/evidence`: Trả về thermodynamics evidence pack (+23.75σ pressure, +5.71σ thermal drift, temporal persistence).
    - `POST /api/action/safe-mode`: Kích hoạt an toàn chuyển hướng sang nhánh post-maintenance, trả về 409 Conflict với payload `{"error": "INVALID_STATE_TRANSITION", "detail": ...}` nếu không đúng trạng thái.
    - `GET /api/recovery`: Trả về tiến độ kiểm định evaluation windows (0/5 -> 5/5) và telemetry mới nhất.
  - **Demo Endpoints (`src/api/routes_demo.py`)**:
    - `POST /demo/reset`: Reset stream và vị trí mô phỏng (tùy chọn jump tới milestone `onset_0950`).
    - `POST /demo/tick`: Tịnh tiến 1 bước telemetry (10s), idempotent khi đã `RESOLVED`.
    - `POST /demo/jump`: Nhảy trực tiếp tới milestone lịch sử, trả về 400 Bad Request với `{"error": "INVALID_ARGUMENT", "detail": ...}` nếu milestone không hợp lệ.
  - **FastAPI Application Factory (`src/api/app.py`)**: `create_app()` khởi tạo hoặc inject singleton `IncidentLifecycleManager`, mount routers và cài đặt custom exception handlers cho `InvalidStateTransitionError` (409) và `ValueError` (400).
- **Verification**:
  - `python -m pytest tests/test_api_vertical_slice.py -v`: 3/3 passed in 8.15s.
  - Toàn bộ suite hồi quy (23 tests): 23/23 passed in 26.43s.

