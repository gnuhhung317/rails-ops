# SCREEN 06 — CASE INVESTIGATION WORKBENCH: DID IT WORK? (LIVE RECOVERY VERIFIER & OPERATOR SIGN-OFF)
> **Mục tiêu:** Trả lời câu hỏi thứ tư của chuyên viên điều độ: **"Sau khi bảo trì và đưa máy nén chạy lại dưới tải thực tế (`LOADED`), chuỗi dữ liệu cảm biến có chứng minh thiết bị đã ổn định bền vững qua đủ 5 mẫu liên tiếp để ký duyệt đóng hồ sơ và trả tàu về tuyến không?"**  
> **Cải tiến cốt lõi v3.0:**
> 1. **Xoá bỏ số liệu phục hồi hardcode tĩnh:** Thay vì hiển thị sẵn `-0.016 bar` và `64.12 °C`, giao diện đọc động từng mẫu từ `GET /api/recovery` và `GET /api/telemetry/window` khi con trỏ chạy qua phân đoạn `2020-06-08 16:05:00 UTC`.
> 2. **Bảng Kiểm Chứng 5 Mẫu Mang Tải Trực Tiếp (`5-Sample Loaded Verification Table`) + Form Ký Duyệt Đóng Case (`Engineering Sign-Off Form`):** Chuyên viên theo dõi từng mẫu `#1..#5` được điền dần vào bảng, sau đó chọn **Confirmed Root Cause** và nhập **Sign-Off Notes** trước khi đóng hồ sơ.

---

## 1. BỐ CỤC GIAO DIỆN (3-PANE WORKBENCH — VIEW 4: RECOVERY VERIFICATION & SIGN-OFF)

```text
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ WORKBENCH // APU-INC-20200605-01 · Train #302 (APU-COMP-01)   [PHASE: RESOLVED]       [VERIFIED: 5/5 PASS ✓] │
│ Sub-View Focus: [1. WHAT CHANGED?]  [2. WHY? (EVIDENCE)]  [3. PLAYBOOK & GUARD]  [★ 4. RECOVERY]  [5. AUDIT] │
├───────────────────────────────────────────────────┬──────────────────────────────────────────────────────────┤
│ LEFT & CENTER PANE (7 COLS):                      │ RIGHT PANE (5 COLS):                                     │
│ LIVE 5-SAMPLE LOADED RECOVERY VERIFICATION        │ OPERATOR ROOT-CAUSE CLASSIFICATION & CASE SIGN-OFF FORM  │
│ (Bound live to GET /api/recovery)                 │ (Unlocked strictly when is_verified == true)             │
│ ───────────────────────────────────────────────── │ ──────────────────────────────────────────────────────── │
│ PROGRESS: [✓ #1] ──► [✓ #2] ──► [✓ #3] ──► [✓ #4] ──► [✓ #5]   Status: [🏆 5/5 CRITERIA VERIFIED]            │
│ Rule: Must satisfy 5 consecutive LOADED samples. Any breach immediately resets counter to 0/5.               │
│                                                   │ 1. VERIFICATION GATE STATUS                              │
│ LIVE THRESHOLD GAUGES (LATEST TELEMETRY POINT):   │ • Consecutive Loaded Samples: [ 5 / 5 VERIFIED ✓ ]       │
│ ┌───────────────────────┬───────────────────────┐ │ • DV Pressure Criterion:      [ < 0.050 bar PASS ✓ ]     │
│ │ DV_PRESSURE (LOADED)  │ OIL_TEMP (LOADED)     │ │ • Oil Temp Criterion:         [ < 67.00 °C  PASS ✓ ]     │
│ │ Live: -0.0164 bar     │ Live: 64.12 °C        │ │                                                          │
│ │ Max Allowed: < 0.050  │ Max Allowed: < 67.0°C │ │ 2. CONFIRMED ROOT CAUSE CLASSIFICATION                   │
│ │ Status: [🟢 PASS]     │ Status: [🟢 PASS]     │ │ [Desiccant Drain Valve Mechanical Seal Leak (DV-02)   ▼] │
│ └───────────────────────┴───────────────────────┘ │                                                          │
│                                                   │ 3. RESOLUTION & WORK ORDER COMPLETION CODE               │
│ CONSECUTIVE LOADED OBSERVATIONS LOG:              │ [WO-20200605-302: Valve Replaced & Pressure Tested    ▼] │
│ ┌─────┬─────────────────────┬────────┬──────────┬────────┐                                                   │
│ │ #   │ Timestamp (UTC)     │ Regime │ DV (bar) │ Oil(°C)│ 4. DISPATCHER SIGN-OFF NOTES (REQUIRED FOR AUDIT) │
│ ├─────┼─────────────────────┼────────┼──────────┼────────┤ ┌───────────────────────────────────────────────┐ │
│ │ #1  │ 2020-06-08 16:05:10 │ LOADED │ -0.0171  │ 64.45  │ │Verified 5/5 consecutive LOADED observations   │ │
│ │ #2  │ 2020-06-08 16:05:20 │ LOADED │ -0.0168  │ 64.38  │ │post-maintenance. DV pressure and Oil temp     │ │
│ │ #3  │ 2020-06-08 16:05:30 │ LOADED │ -0.0165  │ 64.29  │ │stabilized within nominal bounds. Releasing    │ │
│ │ #4  │ 2020-06-08 16:05:40 │ LOADED │ -0.0164  │ 64.19  │ │Train #302 back to Line 1 revenue service. │ │
│ │ #5  │ 2020-06-08 16:05:50 │ LOADED │ -0.0164  │ 64.12  │ └───────────────────────────────────────────────┘ │
│ └─────┴─────────────────────┴────────┴──────────┴────────┘                                                   │
│                                                   │ ┌──────────────────────────────────────────────────────┐ │
│                                                   │ │ 🔒 [ SIGN OFF, CLOSE CASE & RELEASE ASSET TO FLEET ] │ │
│                                                   │ └──────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────┴──────────────────────────────────────────────────────────┘
```

---

## 2. CƠ CHẾ KIỂM CHỨNG KHÉP KÍN & KÝ DUYỆT ĐÓNG HỒ SƠ (v3.0)

1. **Đánh giá động theo từng nhịp `tick` (`GET /api/recovery`):**
   - Các đồng hồ đo `latest_telemetry.dv_pressure_bar` và `latest_telemetry.oil_temp_c` cập nhật trực tiếp từ điểm dữ liệu mới nhất.
   - Chỉ những mẫu đo nằm trong chế độ mang tải (`regime == "LOADED"`, tức `Motor_current > 0.5A`) mới được đưa vào bộ đếm `consecutive_healthy_observations`. Nếu máy nén đang nghỉ (`UNLOADED`), bộ đếm giữ nguyên và chờ chu kỳ nạp tải tiếp theo.
   - Nếu bất kỳ mẫu `LOADED` nào vượt ngưỡng (`dv_pressure_bar >= 0.05` hoặc `oil_temp_c >= 67.0`), bộ đếm lập tức reset về `0/5`.
2. **Khoá an toàn trên nút `Close Case` (`POST /api/case/close`):**
   - Khi `is_verified == false` (`0/5` đến `4/5`), nút `[ SIGN OFF, CLOSE CASE & RELEASE ASSET ]` ở trạng thái khóa (`disabled`). Nếu gọi trực tiếp qua API, Backend trả về **HTTP 409 Conflict**.
   - Khi đạt `5/5`, chuyên viên điền phân loại nguyên nhân gốc (`Confirmed Root Cause`) và ghi chú nghiệm thu (`notes`) rồi bấm ký duyệt. Tài sản `APU-COMP-01` lập tức chuyển về `HEALTHY` và hồ sơ lưu vào kho lưu trữ `CLOSED`.

---

## 3. RÀNG BUỘC DỮ LIỆU ĐỘNG (`GET /api/recovery` & `POST /api/case/close`)

```json
{
  "recovery_status": {
    "incident_id": "APU-INC-20200605-01",
    "is_recovering": true,
    "is_verified": true,
    "consecutive_healthy_observations": 5,
    "target_healthy_observations": 5,
    "latest_telemetry": {
      "dv_pressure_bar": -0.0164,
      "oil_temp_c": 64.12,
      "regime": "LOADED"
    },
    "criteria": {
      "dv_pressure_max": 0.05,
      "oil_temp_max": 67.0,
      "required_regime": "LOADED"
    }
  },
  "close_request": {
    "operator_id": "DISPATCHER-0941",
    "notes": "Verified 5/5 consecutive LOADED observations post-maintenance. Releasing Train #302 to service."
  },
  "close_response": {
    "status": "CASE_CLOSED",
    "case_id": "APU-INC-20200605-01",
    "operator_id": "DISPATCHER-0941",
    "notes": "Verified 5/5 consecutive LOADED observations post-maintenance. Releasing Train #302 to service.",
    "lifecycle_state": "RESOLVED",
    "asset_health": "HEALTHY"
  }
}
```
