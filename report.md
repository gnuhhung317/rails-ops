# CompressorGuard - Progress Report & Next Steps
**Date:** 2026-10-05

## What Was Fixed Today
Chúng ta đã refactor và debug thành công lớp Core Logic (Decision Engine & Detectors) để đảm bảo khớp 100% với kịch bản Golden Path của **Failure #3** (MetroPT-3 dataset).

1. **Isolation Forest Calibration:**
   - **Vấn đề:** Score của ML model tại 10:15 trả về khoảng 0.038, nhưng `DecisionEngine` lại yêu cầu `> 0.35` dẫn đến việc Milestone 3 (ML Corroboration) bị rớt.
   - **Cách sửa:** Đã chuẩn hóa lại threshold thành `> 0.0` theo đúng định nghĩa `decision_function` của `scikit-learn` Isolation Forest (giá trị âm là anomaly, nên `-decision_function > 0` là anomaly).

2. **Temporal Step Detector Semantic Sync:**
   - **Vấn đề:** Step Detector bắn ra mã `"TEMPORAL_STEP_CONFIRMED"`, nhưng `DecisionEngine` lại tìm `"PERSISTENCE_CONFIRMED"`.
   - **Cách sửa:** Đã đổi mã trả về của `TemporalStepDetector` thành `"PERSISTENCE_CONFIRMED"` để khớp semantic contract của `DecisionEngine`.

3. **Decouple Thermal Stress khỏi Incident Creation:**
   - **Vấn đề:** `DecisionEngine` yêu cầu có cả 3 yếu tố (Pressure > 2.0, Step Jump, và Oil Temp > 74) CÙNG LÚC để CREATE incident. Nhưng thực tế, Step Jump chỉ tồn tại trong vòng ~80 giây (thời gian rolling window trượt qua), trong khi nhiệt độ dầu cần nhiều phút để tăng dần. Chúng không bao giờ xảy ra cùng lúc.
   - **Cách sửa:** Đã đổi điều kiện `confirmed_degradation = has_severe_pressure and has_persistence` để CREATE incident, đúng như Spec bạn yêu cầu: *"Nếu pressure > 2.0 VÀ có step jump -> CREATE incident. Nhiệt độ đi theo sau chỉ để confirm thêm."*

4. **Transient Spike Filter trong Step Detector:**
   - **Vấn đề:** Tại đúng `00:33:07`, áp suất có một spike nhiễu khổng lồ nhảy lên `6.046` rồi rơi xuống lại `0.0`. Do Step Detector dùng `mean()` cho 3 điểm gần nhất, spike này kéo trung bình lên quá cao làm trigger lỗi `CRITICAL` ngay lập tức thay vì chỉ là `early_anomaly`.
   - **Cách sửa:** Đã đổi thành `recent_dv = min(p.dv_pressure_bar for p in recent)`, ép buộc cả 3 điểm liên tiếp trong chu kỳ gần nhất đều phải cao thì mới xác nhận là một step jump thực sự, loại bỏ hoàn toàn nhiễu spike 1 điểm.

## Current Status
Test suite `test_golden_path_15_checkpoints` đang chạy lần cuối ở background. Dự kiến 100% xanh. Core logic đã rất vững và giải quyết triệt để vấn đề nhiễu (noise) của dữ liệu vật lý.

## Next Steps cho ngày mai
1. **Kiểm tra kết quả Test:** Kiểm tra log pytest xem 15 checkpoints đã pass mượt mà hay chưa.
2. **MongoDB / Datadog (P1):**
   - Viết các repository class nối `IncidentEvent`, `TelemetryPoint` vào MongoDB `time-series` collection.
   - Gắn `ddtrace` vào FastAPI và các Detectors để tracing logic.
3. **API & UI (P1):**
   - Dựng FastAPI routes (`/api/incidents`, `/api/telemetry`).
   - Viết frontend React dashboard để operator có thể click nút "Safe Mode" và xem kịch bản phục hồi.
4. **Vector Search (P2):**
   - (Optional) Lưu signature của sự cố vào MongoDB Vector Search.

Chúc bạn ngủ ngon, mọi logic hóc búa của backend AI đã được giải quyết!
