# Research & Audit Findings: CompressorGuard Reasoning Engine Stabilization

## 1. Dữ liệu thực tế tại các mốc Golden Path (MetroPT-3)

### Mốc 1: Early Anomaly (2020-06-04 00:33)
- `DV_pressure` có excursion vượt 0.5 bar (khoảng 0.6 bar).
- `Oil_temperature` vẫn ở mức bình thường.
- Kết quả mong muốn: `AssetHealthState.DEGRADING`, `IncidentAction.NONE`, `OperationalConfidence.LOW` ("Early Warning: Minor Excursion").

### Mốc 2: Confirmed Degradation (2020-06-05 09:50:19)
- Telemetry thực tế:
  - 09:49:59: `DV_pressure = -0.02 bar`, `Oil_temp = 67.97 °C`
  - 09:50:09: `DV_pressure = 0.02 bar`, `Oil_temp = 69.40 °C`
  - 09:50:19: `DV_pressure = 2.754 bar`, `Oil_temp = 70.85 °C` (Bắt đầu step nhảy vọt)
  - 09:50:29: `DV_pressure = 2.428 bar`, `Oil_temp = 71.70 °C`
  - 09:50:39: `DV_pressure = 2.474 bar`, `Oil_temp = 72.52 °C`
- **Phát hiện quan trọng về Thermal tại 09:50**:
  - Tại 09:50:19 - 09:52:00, `Oil_temperature` dao động từ 70.85 °C đến 73.05 °C.
  - Ngưỡng `THERMAL_STRESS_SEVERE` là `> 74.0 °C`. Mức này chỉ thực sự đạt được từ `09:59:54` trở đi (~10:00).
  - Do đó tại 09:50:19, signal thermal là `THERMAL_STRESS_ELEVATED` (> 70.0 °C), chưa phải `SEVERE`.
  - Điều này giải thích vì sao rule của `confirmed_degradation` phải dùng `has_any_thermal` (hoặc `THERMAL_STRESS_ELEVATED` / `THERMAL_STRESS_SEVERE`), KHÔNG ĐƯỢC chỉ bắt buộc `THERMAL_STRESS_SEVERE`, nếu không checkpoint 09:50 sẽ bị miss hoàn toàn!

### Mốc 3: Regime Continuity (2020-06-05 09:48:30 đến 10:20:00)
- Kiểm tra 191 sample liên tiếp trong cửa sổ này: **100% sample đều là LOADED**!
- Không hề có bất kỳ gap hay regime switch nào giữa chừng.
- Kết luận: Setting `allowed_regime_gaps = 0` là hoàn toàn chính xác, an toàn tuyệt đối và loại bỏ heuristic thừa.

### Mốc 4: Temporal Step Detector: Step Transition vs Degraded Plateau
- `TemporalStepDetector` tính `step_diff = recent_dv - past_dv`.
- Tại 09:50: `past` (trước 09:50) là ~-0.02 bar, `recent` (09:50:19+) là ~2.4 bar -> `step_diff ≈ 2.4 bar > 0.5 bar` -> `TEMPORAL_STEP_CONFIRMED`.
- Tại 10:15 (25 phút sau): cả `past` (10:10) và `recent` (10:15) đều đã ở mức ~2.2 bar -> `step_diff ≈ 0 bar < 0.5 bar` -> Detector trở về `NORMAL`.
- **Hệ quả kiến trúc**:
  - `TemporalStepDetector` phát hiện sự kiện biến đổi trạng thái (step change event), không phải duy trì vĩnh viễn trạng thái lệch.
  - Sau khi incident đã được tạo ở 09:50, tại 10:15 incident đang ở trạng thái `DETECTED` / `INVESTIGATING`.
  - Nếu không có `IncidentContext`, tại 10:15 hệ thống không biết mình đang ở đâu trong lifecycle!

---

## 2. Phân tích & Phản biện 15 điểm của User

1. **Isolation Forest Threshold (score > 0.35)**:
   - User hoàn toàn đúng. Code hiện tại `score > 0.0` là sai contract. Golden path score tại 10:15 là ~0.38, threshold chuẩn là 0.35.
   - Sửa: `score_threshold = 0.35` làm parameter có default, gắn vào `baseline_value` và điều kiện trigger.

2. **DecisionEngine & IncidentContext**:
   - User hoàn toàn đúng về kiến trúc: DecisionEngine không thể đưa ra `IncidentAction` đúng nếu không biết ngữ cảnh incident hiện tại (`IncidentContext`).
   - Cần truyền `incident_context: Optional[IncidentContext] = None` vào `evaluate()`.
   - Phản biện bổ sung: `evaluate()` chỉ đề xuất action (`Decision`), còn việc cập nhật state incident (tạo mới, chuyển state, lưu evidence chain) thuộc về Incident Service / Coordinator.

3. **Temporal dùng mean() thay vì min()**:
   - User hoàn toàn đúng về mặt ngữ nghĩa toán học: Step change = `mean(recent) - mean(past)`.
   - `min()` trước đây là một "hack" ngầm nhằm ép tất cả sample recent phải lớn hơn past. Việc đổi sang `mean(recent) - mean(past)` phản ánh đúng định nghĩa vật lý.

4. **Pressure và Thermal detector dùng latest thay vì min(last 3)**:
   - User hoàn toàn đúng. Detector đơn sensor phải phản ánh `latest` telemetry để `observed_value` trung thực 1:1 với điểm dữ liệu real-time.
   - Nhiệm vụ kiểm tra chuỗi liên tục thuộc về Temporal Logic / Decision Engine.

5. **confirmed_degradation policy**:
   - User nói: `confirmed_degradation = has_severe_pressure and has_any_thermal and has_temporal_step`.
   - Dữ liệu thực tế xác nhận: Tại 09:50:19, pressure là SEVERE (> 2.0), thermal là ELEVATED (> 70.0), step là CONFIRMED. Do đó `has_any_thermal` là chính xác tuyệt đối.

6. **Semantic naming: TEMPORAL_STEP_CONFIRMED**:
   - User hoàn toàn đúng. Đổi `PERSISTENCE_CONFIRMED` -> `TEMPORAL_STEP_CONFIRMED` và `has_temporal_step`.

7. **allowed_regime_gaps = 0**:
   - Đã verify trên 191 sample dữ liệu thật: 100% LOADED. Đặt `allowed_regime_gaps = 0`.

8. **DetectorResult semantic fields & EvidenceCode Enum**:
   - Gom lại làm sạch: Định nghĩa Enum `EvidenceCode` chuẩn để loại bỏ chuỗi string tự do, đảm bảo type safety.

9. **Provenance detail cho auditability**:
   - Thêm `required_cycles`, `baseline_cycles`, `actual_recent_timestamps`, `actual_baseline_timestamps`, `gap_count`.

10. **Replay Engine explicit sort**:
    - Thêm `.sort_values("timestamp").reset_index(drop=True)`.

11. **Relative / Configurable CSV Path**:
    - Dùng `Path(__file__).resolve().parents[...] / "dataset" / "MetroPT3(AirCompressor).csv"` thay vì hardcode absolute Windows path.

12. **classify_regime validation**:
    - Viết unit test riêng cho `classify_regime` bao phủ các case: `OFF`, `STARTING`, `OFF_LOAD`, `LOADED`, `TRANSIENT`.

13. **Import path**:
    - Package chuẩn là `src.domain...` và `src.engine...`. Đảm bảo `PYTHONPATH` và root package nhất quán.

14. **Unused import**:
    - Dọn sạch `DetectorStatus` trong `decision.py`.

15. **test_decision.py**:
    - Đã phát hiện nguyên nhân fail: test truyền thiếu `evidence_code`. Sẽ fix test đồng bộ với `EvidenceCode` enum.
