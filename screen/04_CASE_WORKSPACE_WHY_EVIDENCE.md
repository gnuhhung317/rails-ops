# SCREEN 04 — CASE WORKSPACE: WHY? (EVIDENCE DOSSIER WITH PROVENANCE)
> **Mục tiêu:** Trả lời câu hỏi thứ hai của chuyên viên vận hành: **"Tại sao tôi phải tin hệ thống? Bằng chứng vật lý nào chứng minh đây không phải là lỗi cảm biến ngẫu nhiên?"**  
> **Nguyên tắc:** **Evidence Provenance > Anomaly Score** (Mỗi bằng chứng đều mang xuất xứ nguồn, phương pháp đánh giá và mốc thời gian rõ ràng).

---

## 1. BỐ CỤC GIAO DIỆN (ASCII WIREFRAME)

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ CASE WORKSPACE // CASE-20200605-01: APU-COMP-01 (TRAIN #302)                         [STATUS: CRITICAL]│
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ [1. WHAT CHANGED?]   [★ 2. WHY? (EVIDENCE)]   [3. WHAT DID WE DO?]   [4. DID IT WORK?]   [5. TIMELINE] │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                        │
│  BỘ BẰNG CHỨNG NHIỆT ĐỘNG LỰC HỌC TƯƠNG QUAN KÈM NGUỒN GỐC (EVIDENCE PACK WITH PROVENANCE)              │
│  ────────────────────────────────────────────────────────────────────────────────────────────────────  │
│  Regime Kiểm Chứng: LOADED (Dòng điện mô-tơ > 0.5A) | Đánh giá độc lập tách biệt khỏi lúc không tải     │
│                                                                                                        │
│  ┌──────────────────────────────┐  ┌──────────────────────────────┐  ┌──────────────────────────────┐  │
│  │ THẺ A: ÁP SUẤT KHÍ XẢ        │  │ THẺ B: NHIỆT ĐỘ DẦU MÁY      │  │ THẺ C: BƯỚC NHẢY BỀN VỮNG    │  │
│  │                              │  │                              │  │                              │  │
│  │   2.1856 bar [ ▲ +23.75σ ]   │  │   74.97 °C   [ ▲ +5.71σ ]    │  │   3 / 3 Chu Kỳ [ CONFIRMED ] │  │
│  │   Baseline: -0.016 ± 0.09    │  │   Baseline: 54.98 ± 3.5 °C   │  │   Delta Ngưỡng: > 0.5 bar    │  │
│  │   Status: CRITICAL           │  │   Status: SEVERE             │  │   Status: PERSISTENT         │  │
│  │   ────────────────────────── │  │   ────────────────────────── │  │   ────────────────────────── │  │
│  │   SOURCE: PressureAnomalyDet │  │   SOURCE: ThermalDriftDet    │  │   SOURCE: TemporalStepDet    │  │
│  │   METHOD: Loaded-regime base │  │   METHOD: Cumulative drift   │  │   METHOD: Cycle persistence │  │
│  │   TIME:   09:50:39 UTC       │  │   TIME:   09:50:39 UTC       │  │   TIME:   09:50:39 UTC       │  │
│  │   REGIME: LOADED             │  │   REGIME: LOADED             │  │   REGIME: LOADED             │  │
│  └──────────────────────────────┘  └──────────────────────────────┘  └──────────────────────────────┘  │
│                                                                                                        │
│  ┌──────────────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ THẺ D: KIỂM CHỨNG ĐA BIẾN ĐỘC LẬP BỞI MACHINE LEARNING (MULTIVARIATE CORROBORATION)               │  │
│  │                                                                                                  │  │
│  │   Mô hình: Isolation Forest | Features: 5 Telemetry Signals (DV, H1, Oil_temp, Motor_current, TP3)│  │
│  │   Anomaly Score: 0.382   [ ▲ VƯỢT NGƯỠNG KIỂM CHỨNG 0.350 ]    Trạng thái: [ CORROBORATED ]       │  │
│  │   ────────────────────────────────────────────────────────────────────────────────────────────   │  │
│  │   SOURCE: IsolationForestModel               METHOD: 5-Feature Multivariate Boundary             │  │
│  │   TIME:   2020-06-05 09:50:39 UTC            REGIME: LOADED                                      │  │
│  │   VAI TRÒ NGHIỆP VỤ: Độc lập kiểm chứng (Independent Corroboration).                             │  │
│  │   "ML không tự tạo Case. ML phối hợp với 3 tín hiệu vật lý để nâng cao độ tin cậy quyết định!"   │  │
│  └──────────────────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                                        │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ CHUỖI NHÂN QUẢ NHIỆT ĐỘNG LỰC HỌC (THERMODYNAMIC CAUSAL CHAIN)                                         │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                        │
│  [Van xả tháp sấy hở]                                                                                  │
│          │                                                                                             │
│          ▼                                                                                             │
│  [Khí nén phun ra ngoài] ──► [Áp suất DV_pressure nhảy vọt lên 2.18 bar (+23.75σ)]                    │
│          │                                                                                             │
│          ▼                                                                                             │
│  [Máy nén phải bơm bù]   ──► [Chu kỳ nạp kéo dài, dòng mô-tơ duy trì liên tục]                         │
│          │                                                                                             │
│          ▼                                                                                             │
│  [Ma sát nhiệt tích tụ]  ──► [Nhiệt độ dầu Oil_temp bốc cao lên 74.97°C (+5.71σ)]                     │
│          │                                                                                             │
│          ▼                                                                                             │
│  [Dầu mất độ nhớt]       ──► [CẢNH BÁO: Bó kẹt cơ học & sập áp phanh sau 33h 52m nếu không cách ly!]   │
│                                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. NỘI DUNG NHẬN THỨC CỦA OPERATOR (COGNITIVE PROGRESSION)

1. **Có xuất xứ dữ liệu (Provenance):** Mỗi bằng chứng ghi rõ thuật toán sinh ra (`SOURCE`), phương pháp so sánh (`METHOD`), thời điểm kiểm tra (`TIMESTAMP`), và chế độ (`REGIME`).
2. **Vai trò chuẩn mực của ML:** 
   - Mô hình Isolation Forest không phải là "vị cứu tinh toàn năng tự tạo case".
   - Nó sử dụng đúng **5 đặc trưng vật lý có tải** (`DV_pressure`, `H1`, `Oil_temp`, `Motor_current`, `TP3`) để kiểm chứng xem trạng thái tổng thể có lệch chuẩn không.
   - Khi cả 3 tín hiệu vật lý + ML đồng thuận $\rightarrow$ Quyết định chuyển từ chẩn đoán sang khuyến nghị can thiệp (`Mitigation Recommended`).

---

## 3. RÀNG BUỘC DỮ LIỆU (DATA BINDING CONTRACT — `GET /api/evidence`)

```json
{
  "case_id": "CASE-20200605-01",
  "operating_regime": "LOADED",
  "evidence_pack": [
    {
      "code": "PRESSURE_SEVERE",
      "signal_name": "Discharge Valve Pressure (DV_pressure)",
      "observed_value": 2.1856,
      "baseline_value": -0.0164,
      "unit": "bar",
      "sigma_deviation": 23.75,
      "status": "CRITICAL",
      "is_primary": true,
      "provenance": {
        "source": "PressureAnomalyDetector",
        "method": "Loaded-regime baseline deviation",
        "timestamp": "2020-06-05T09:50:39Z",
        "regime": "LOADED"
      }
    },
    {
      "code": "THERMAL_STRESS_DRIFT",
      "signal_name": "Compressor Oil Temperature (Oil_temp)",
      "observed_value": 74.97,
      "baseline_value": 54.98,
      "unit": "°C",
      "sigma_deviation": 5.71,
      "status": "SEVERE",
      "is_primary": false,
      "provenance": {
        "source": "ThermalDriftDetector",
        "method": "Cumulative thermal stress drift",
        "timestamp": "2020-06-05T09:50:39Z",
        "regime": "LOADED"
      }
    },
    {
      "code": "TEMPORAL_STEP_CONFIRMED",
      "signal_name": "Temporal Step Persistence",
      "observed_value": 2.202,
      "baseline_value": 0.0,
      "unit": "bar_diff",
      "sigma_deviation": 0.0,
      "status": "CONFIRMED",
      "is_primary": false,
      "provenance": {
        "source": "TemporalStepDetector",
        "method": "Consecutive loaded cycle persistence (3/3)",
        "timestamp": "2020-06-05T09:50:39Z",
        "regime": "LOADED"
      }
    },
    {
      "code": "MULTIVARIATE_CORROBORATION",
      "signal_name": "Multivariate Isolation Forest",
      "observed_value": 0.382,
      "baseline_value": 0.350,
      "unit": "score",
      "sigma_deviation": null,
      "status": "CORROBORATED",
      "is_primary": false,
      "provenance": {
        "source": "IsolationForestModel",
        "method": "5-feature boundary evaluation on LOADED baseline",
        "timestamp": "2020-06-05T09:50:39Z",
        "regime": "LOADED",
        "role": "Independent corroboration (elevates mitigation confidence)"
      }
    }
  ]
}
```
