# SCREEN 06 — CASE WORKSPACE: DID IT WORK? (RECOVERY CRITERIA VERIFIED)
> **Mục tiêu:** Trả lời câu hỏi quan trọng nhất của chuyên viên và ban giám khảo: **"Nó có hiệu quả thật không? Bằng chứng nào chứng minh chuỗi dữ liệu đã thỏa mãn tiêu chuẩn phục hồi và sự cố có thể kết thúc?"**  
> **Nguyên tắc:** **Recovery Criteria Verified (5/5 Healthy Observations Trong Chế Độ LOADED)** — Hệ thống chứng minh dữ liệu cảm biến thỏa mãn đầy đủ tiêu chí phục hồi toán lý, không nhận vơ chứng chỉ kiểm định cơ khí vật lý.

---

## 1. BỐ CỤC GIAO DIỆN (ASCII WIREFRAME)

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ CASE WORKSPACE // CASE-20200605-01: APU-COMP-01 (TRAIN #302)                         [STATUS: RESOLVED]│
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [1. WHAT CHANGED?]   [2. WHY? (EVIDENCE)]   [3. WHAT DID WE DO?]   [★ 4. DID IT WORK?]   [5. TIMELINE] │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                        │
│  TIẾN TRÌNH KIỂM CHỨNG TIÊU CHÍ PHỤC HỒI (RECOVERY CRITERIA VERIFICATION PROGRESS)                     │
│  ────────────────────────────────────────────────────────────────────────────────────────────────────  │
│  Tiêu chuẩn: Đạt đủ 5 Quan sát lành mạnh liên tiếp (5/5 Consecutive Observations) trong chế độ LOADED │
│  Quy tắc nghiêm ngặt: Nếu vi phạm ở mẫu thứ 4/5, bộ đếm lập tức RESET VỀ 0/5!                          │
│                                                                                                        │
│  THANH TIẾN ĐỘ KIỂM CHỨNG:                                                                             │
│  [ ✓ MẪU 1 ] ──► [ ✓ MẪU 2 ] ──► [ ✓ MẪU 3 ] ──► [ ✓ MẪU 4 ] ──► [ ✓ MẪU 5 ]  [ 5 / 5 ĐẠT TIÊU CHUẨN ]│
│                                                                                                        │
│  ┌──────────────────────────────────────────────┐   ┌───────────────────────────────────────────────┐  │
│  │ 1. ÁP SUẤT XẢ THÁP SẤY (DV_PRESSURE)         │   │ 2. NHIỆT ĐỘ DẦU MÁY NÉN (OIL_TEMP)            │  │
│  │                                              │   │                                               │  │
│  │   -0.016 bar   [ 🟢 THỎA MÃN TIÊU CHÍ ]      │   │   64.1 °C   [ 🟢 THỎA MÃN TIÊU CHÍ ]          │  │
│  │   Ngưỡng tối đa cho phép: < 0.050 bar        │   │   Ngưỡng trần cho phép: < 67.0 °C             │  │
│  │                                              │   │                                               │  │
│  │   Đánh giá: Áp suất buồng xả duy trì ở mức   │   │   Đánh giá: Nhiệt độ dầu hạ nhiệt ổn định     │  │
│  │   chân không bình thường lúc mang tải!       │   │   dưới ngưỡng sôi thoái hóa chất bôi trơn!    │  │
│  └──────────────────────────────────────────────┘   └───────────────────────────────────────────────┘  │
│                                                                                                        │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ 🏆 KẾT LUẬN NGHIỆM THU DỮ LIỆU (RECOVERY CRITERIA VERIFIED):                                     │  │
│  │                                                                                                  │  │
│  │  CHUỖI VIỄN THÁM ĐÃ ĐẠT TIÊU CHUẨN PHỤC HỒI TOÀN DIỆN VÀO LÚC 2020-06-08 16:05:50 UTC!           │  │
│  │  Đủ 5/5 quan sát mang tải liên tiếp thỏa mãn cả 2 ngưỡng vật lý khắt khe (DV < 0.05, Oil < 67).   │  │
│  │  Hồ sơ sự cố sẵn sàng để người điều độ ký duyệt đóng (Sign-off) và giải phóng tài sản hạm đội.   │  │
│  └──────────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                        │
│  HÀNH ĐỘNG ĐÓNG HỒ SƠ & BÀN GIAO XƯỞNG (CASE SIGN-OFF & ASSET RELEASE)                                 │
│  ────────────────────────────────────────────────────────────────────────────────────────────────────  │
│                                                                                                        │
│  ┌──────────────────────────────────────────┐     ┌─────────────────────────────────────────────────┐  │
│  │ [ 📄 XUẤT POST-MORTEM VERIFICATION AUDIT]│     │ [ 🔒 ĐÓNG CASE & GIẢI PHÓNG ASSET VỀ GIÁM SÁT ] │  │
│  └──────────────────────────────────────────┘     └─────────────────────────────────────────────────┘  │
│                                                   (Gọi POST /api/case/close — Chỉ hợp lệ khi verified) │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. NỘI DUNG NHẬN THỨC CỦA OPERATOR (COGNITIVE PROGRESSION)

1. **Nuance ngôn ngữ trung thực:** 
   - Thay vì tuyên bố to tát "PHYSICAL RECOVERY VERIFIED / SAFETY CLEARANCE CERTIFIED" (dễ bị chuyên gia đường sắt chất vấn vì chúng ta chưa trực tiếp kiểm định chiếc van vật lý ngoài ray).
   - Hệ thống dùng thuật ngữ chính xác: **RECOVERY CRITERIA VERIFIED (5/5 healthy LOADED observations)** — Khẳng định rằng *chuỗi viễn thám thực tế đã thỏa mãn toàn bộ tiêu chí phục hồi*.
2. **Bắt buộc chế độ có tải (`LOADED`):** Việc máy nén phải chạy mang tải (`Motor_current > 0.5A`) mới đếm quan sát loại bỏ hoàn toàn khả năng máy đang tắt nên giả vờ mát mẻ.
3. **Thủ tục đóng Case (`POST /api/case/close`):**
   - Chỉ được phép gọi khi `is_verified == true`. Nếu bấm trước đó, API lập tức từ chối bằng **HTTP 409 Conflict**.
   - Khi đóng Case: Trạng thái chuyển thành `CLOSED`, tài sản `APU-COMP-01` mở khóa và quay về `HEALTHY` trên Operations Landing Page.

---

## 3. RÀNG BUỘC DỮ LIỆU (DATA BINDING CONTRACT — `GET /api/recovery` & `POST /api/case/close`)

```json
// GET /api/recovery Response
{
  "case_id": "CASE-20200605-01",
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
  },
  "verification_timestamp": "2020-06-08T16:05:50Z"
}

// POST /api/case/close Response (Success)
{
  "case_id": "CASE-20200605-01",
  "status": "CLOSED",
  "asset_id": "APU-COMP-01",
  "asset_health": "HEALTHY",
  "closed_at": "2020-06-08T16:06:10Z",
  "closed_by": "DISPATCHER-0941",
  "summary": "Recovery criteria verified across 5 consecutive loaded observations. Asset released back to revenue service."
}
```
