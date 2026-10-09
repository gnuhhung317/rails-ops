# SCREEN 03 — CASE WORKSPACE: WHAT CHANGED? (ASSET CONDITION → OPERATIONAL IMPACT)
> **Mục tiêu:** Trả lời dứt khoát câu hỏi cốt tử đầu tiên của chuyên viên vận hành: **"Điều gì vừa thay đổi trên đoàn tàu, mức độ nguy cấp ra sao, và chúng ta có bao nhiêu thời gian can thiệp?"**  
> **Nguyên tắc phân tầng:** Tách bạch rõ 4 khối thông tin: **Observed Telemetry $\rightarrow$ Operational Condition $\rightarrow$ Business Context $\rightarrow$ Validation Reference**.

---

## 1. BỐ CỤC GIAO DIỆN (ASCII WIREFRAME)

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ CASE WORKSPACE // CASE-20200605-01: APU-COMP-01 (TRAIN #302)                         [STATUS: CRITICAL]│
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [★ 1. WHAT CHANGED?]   [2. WHY? (EVIDENCE)]   [3. WHAT DID WE DO?]   [4. DID IT WORK?]   [5. TIMELINE] │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                        │
│  🔴 CONFIRMED DEGRADATION DETECTED                      ⏱️ 33H 52M CONFIRMED INTERVENTION WINDOW       │
│  ────────────────────────────────────────────────────────────────────────────────────────────────────  │
│  Confirmed Detection:   2020-06-05 09:50:39 UTC          Conventional Alert (LPS=1): 2020-06-06 19:42  │
│  Current Regime:        LOADED (Train In-Service)        Time Until Pressure Collapse: 2032 Minutes    │
│                                                                                                        │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ KHỐI 1 — DỮ LIỆU CẢM BIẾN QUAN SÁT THỰC TẾ (OBSERVED TELEMETRY)                                        │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                        │
│  ┌──────────────────────────────────────────────┐   ┌───────────────────────────────────────────────┐  │
│  │ ÁP SUẤT VAN XẢ THÁP SẤY (DV_PRESSURE)        │   │ NHIỆT ĐỘ DẦU MÁY NÉN (OIL_TEMP)               │  │
│  │                                              │   │                                               │  │
│  │   2.1856 bar   [ ▲ +23.75σ CRITICAL ]        │   │   74.97 °C   [ ▲ +5.71σ SEVERE ]              │  │
│  │   Baseline nạp: -0.016 ± 0.09 bar            │   │   Baseline nạp: 54.98 ± 3.5 °C                │  │
│  │   Độ lệch cực đại: Van xả bị kẹt hở làm khí  │   │   Hiện tượng trôi dạt: Máy nén bơm bù quá tải │  │
│  │   nén xả tràn ra ngoài trong lúc mang tải.   │   │   sinh nhiệt ma sát nguy cơ sôi loãng dầu.    │  │
│  └──────────────────────────────────────────────┘   └───────────────────────────────────────────────┘  │
│                                                                                                        │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ KHỐI 2 — ĐIỀU KIỆN VẬN HÀNH THIẾT BỊ (OPERATIONAL CONDITION)                                           │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ • Asset Health:     [🔴 CRITICAL] (Suy thoái nhiệt động lực học nghiêm trọng)                          │
│ • Operating Regime: [ LOADED ] (Chế độ mang tải có dòng điện mô-tơ > 0.5A)                             │
│ • Degradation:      [ CONFIRMED ] (Bền vững qua 3 chu kỳ nạp tải, không phải xung nhiễu thoáng qua)    │
│                                                                                                        │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ KHỐI 3 — BỐI CẢNH VẬN TẢI HẠM ĐỘI (BUSINESS CONTEXT)                                                   │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ • Service Unit:     TRAIN-302 (Đoàn tàu thương mại đang đón trả khách — Tuyến Linha Azul)              │
│ • Subsystem:        Air Production Unit (APU) / Hệ thống khí nén phanh và cửa tàu                      │
│ • Operational Risk: Nguy cơ sập áp suất bình chứa chính H1 $\rightarrow$ Tàu dừng khẩn cấp giữa ray hầm │
│ • Confirmed Window: 33 GIỜ 52 PHÚT (Cửa sổ can thiệp trước mốc còi cơ học LPS=1)                       │
│                                                                                                        │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ KHỐI 4 — THAM CHIẾU KIỂM CHỨNG LỊCH SỬ (VALIDATION REFERENCE)                                          │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ • Ground Truth Reference:  Historical Failure #3 — Air Leak / High Stress (MetroPT-3 Dataset Paper)    │
│ • Vai trò đối chứng:       Xác thực độc lập kịch bản lịch sử sau khi hệ thống đã ra quyết định online. │
│ • Nguyên tắc khoa học:     Ground Truth KHÔNG leak ngược vào thuật toán phát hiện của Detector!        │
│                                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. NỘI DUNG NHẬN THỨC CỦA OPERATOR (COGNITIVE PROGRESSION)

1. **Khối 1 (Observed):** Người điều độ thấy chính xác số liệu cảm biến thực tế đo được mà không bị che giấu: $2.1856\text{ bar}$ ($+23.75\sigma$) và $74.97^\circ\text{C}$ ($+5.71\sigma$).
2. **Khối 2 (Operational Condition):** Động cơ phân tích kết luận tình trạng thiết bị: `CRITICAL` và `CONFIRMED` trong đúng chế độ mang tải `LOADED`.
3. **Khối 3 (Business Context):** Người điều độ hiểu tác động đối với dịch vụ hành khách: Đoàn tàu Train #302 đang có nguy cơ dừng chết máy giữa đường hầm, và hệ thống cung cấp **33 giờ 52 phút** để chủ động xử lý trước khi rơ-le LPS hú còi.
4. **Khối 4 (Validation Reference):** Ban giám khảo và thanh tra kỹ thuật thấy rõ kịch bản này đối chứng ăn khớp hoàn toàn với báo cáo bảo dưỡng thực tế Failure #3 của Lisbon Metro, khẳng định tính trung thực trí tuệ tuyệt đối.

---

## 3. RÀNG BUỘC DỮ LIỆU (DATA BINDING CONTRACT)

```json
{
  "case_id": "CASE-20200605-01",
  "what_changed": {
    "observed": {
      "dv_pressure_bar": {"value": 2.1856, "baseline": -0.0164, "sigma": 23.75},
      "oil_temp_c": {"value": 74.97, "baseline": 54.98, "sigma": 5.71}
    },
    "operational_condition": {
      "asset_health": "CRITICAL",
      "operating_regime": "LOADED",
      "degradation_state": "CONFIRMED"
    },
    "business_context": {
      "service_unit": "TRAIN-302",
      "subsystem": "Air Production Unit (APU)",
      "operational_risk": "Pneumatic line pressure collapse risk. Stoppage in tunnel if unaddressed.",
      "confirmed_intervention_window": {
        "minutes": 2032,
        "formatted": "33h 52m",
        "detection_timestamp": "2020-06-05T09:50:39Z",
        "conventional_lps_timestamp": "2020-06-06T19:42:19Z"
      }
    },
    "validation_reference": {
      "ground_truth_report": "Failure #3 — Air Leak / High Stress",
      "source": "MetroPT-3 Maintenance Ledger",
      "usage": "Independent post-hoc validation (zero leakage into online detectors)"
    }
  }
}
```
