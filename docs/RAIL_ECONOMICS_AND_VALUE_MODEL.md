# COMPRESSORGUARD — RAIL ECONOMICS & OPERATIONAL VALUE MODEL
> **Document Type:** Domain Economic Specification & Business Value Framework  
> **Status:** Active & Normative (SSOT Companion to `master_context.md`)  
> **Target:** MUGVN Hackathon 2026 (MongoDB + Datadog) & Industrial Commercialization  
> **Core Principle:** **Observed (Telemetry) ≠ Modeled (Economics) ≠ Verified (Physical Recovery)**

---

## MỤC LỤC TỔNG QUAN

1. [Executive Summary: Từ Anomaly Score Sang Rail Economics](#1-executive-summary)
2. [Bộ Ba Bất Biến Về Tính Trung Thực Trí Tuệ (Intellectual Honesty Triad)](#2-bộ-ba-bất-biến-về-tính-trung-thực-trí-tuệ)
3. [7 Nhóm Giá Trị (Value Pools) Của Bảo Dưỡng Dự Đoán Đường Sắt](#3-7-nhóm-giá-trị-value-pools)
4. [Hệ Thống Dữ Liệu Benchmark Ngành Đường Sắt & Đô Thị (Rail Benchmark Hierarchy)](#4-hệ-thống-dữ-liệu-benchmark-ngành-đường-sắt)
5. [Cây Phân Cấp Tài Sản & Cơ Chế Lan Truyền Rủi Ro (Asset Hierarchy & Value Propagation)](#5-cây-phân-cấp-tài-sản--lan-truyền-rủi-ro)
6. [Operational Case Là Đơn Vị Kinh Tế Cốt Lõi (Case-Centric Value Funnel)](#6-operational-case-là-đơn-vị-kinh-tế-cốt-lõi)
7. [Cơ Chế Kinh Tế Của Tính Tường Minh (Explainability & Trust Economics)](#7-cơ-chế-kinh-tế-của-tính-tường-minh)
8. [Mô Hình Định Lượng Giá Trị CompressorGuard (Configurable Value Model)](#8-mô-hình-định-lượng-giá-trị-compressorguard)
9. [Đặc Tả JSON Schema DTO Cho Business Impact API](#9-đặc-tả-json-schema-dto-cho-business-impact-api)
10. [Danh Mục Tài Liệu Tham Khảo Đã Xác Minh (Verified Reference Links)](#10-danh-mục-tài-liệu-tham-khảo-đã-xác-minh)

---

## 1. EXECUTIVE SUMMARY

Các dự án hackathon hoặc giải pháp IoT công nghiệp thường thất bại trước ban giám khảo và khách hàng doanh nghiệp vì hai thái cực:
1. **Quá thuần kỹ thuật:** Bày ra hàng loạt biểu đồ telemetry, điểm số anomaly, giải thuật phức tạp nhưng không trả lời được: *"Cái này mang lại bao nhiêu tiền và ai quan tâm?"*
2. **Ngụy tạo con số tài chính (Fake Numbers):** Tự ý gán một con số tài chính cứng nhắc (ví dụ: *"Hệ thống tiết kiệm €18,500 cho sự cố này"*) mà không dựa trên ngữ cảnh vận hành cụ thể, khiến các chuyên gia và ban giám khảo mất niềm tin.

**CompressorGuard tiếp cận bằng một triết lý hoàn toàn khác biệt:**
> *"CompressorGuard biến suy thoái thiết bị sớm thành quyết định vận hành có bằng chứng, can thiệp được kiểm chứng, và giá trị kinh tế đo lường được."*  
> **(Turns early machine degradation into an evidence-backed operational decision, a verified intervention, and a measurable business impact).**

Hệ thống không lấy các ví dụ sản xuất dược phẩm (Pharma) hay nhà máy chung chung, mà gắn chặt 100% vào **Kinh tế học Vận hành Đầu máy Toa xe Đường sắt Đô thị (Metro Rolling Stock Economics)** dựa trên dữ liệu thực tế từ **Lisbon Metro (MetroPT-3)**, **Hanoi Metro (Tuyến 2A)**, **SNCF**, **Alstom**, và **Shanghai Metro**.

---

## 2. BỘ BA BẤT BIẾN VỀ TÍNH TRUNG THỰC TRÍ TUỆ
### *(The Intellectual Honesty Triad: Observed ≠ Modeled ≠ Verified)*

Để đảm bảo tính khoa học và thuyết phục tuyệt đối, giao diện và API của CompressorGuard phân định rạch ròi 3 tầng thông tin:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. OBSERVED (Quan sát thực tế từ Telemetry)                                 │
│    • Mốc suy thoái khởi phát: 2020-06-05 09:50:39                          │
│    • Mốc còi cơ học LPS=1 réo: 2020-06-06 19:42:19                          │
│    • Lead Time phát hiện sớm: Đúng 33 Giờ 52 Phút (2032 phút)              │
│    ==> 100% DERIVED TỪ METROPT-3 SENSOR DATA, KHÔNG SUY DIỄN               │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. MODELED (Mô hình hóa kinh tế theo giả định tường minh)                   │
│    • Potential Intervention Window: 33h 52m                                 │
│    • Scenario Modeled Exposure: Downtime Cost/Hour × Avoided Hours          │
│    • Revenue at Risk: Train-km × Revenue/km (Dữ liệu Hanoi Metro)           │
│    ==> CÔNG KHAI THAM SỐ GIẢ ĐỊNH (SCENARIO MODEL), KHÔNG BỊA "MONEY SAVED" │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. VERIFIED (Kiểm chứng phục hồi thực tế)                                   │
│    • Áp suất xả: -0.016 bar (< 0.05 bar)                                    │
│    • Nhiệt độ dầu: 64.1 °C (< 67.0 °C)                                      │
│    • 5/5 observations liên tiếp trong chế độ LOADED                         │
│    ==> 100% XÁC NHẬN TỪ DỮ LIỆU THỰC SAU BẢO TRÌ (2020-06-08)               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. 7 NHÓM GIÁ TRỊ (VALUE POOLS) CỦA BẢO DƯỠNG DỰ ĐOÁN ĐƯỜNG SẮT

Theo tổng hợp từ NIST, DOE, IBM Maximo, Deloitte và GE Vernova, giá trị của bảo dưỡng dự đoán không chỉ gói gọn trong "giảm downtime":

```
Predictive / Prescriptive Maintenance Value Pools (Rail Context)
├── 1. Avoided Downtime (Tránh dừng tàu đột xuất giữa tuyến)
├── 2. Lower Maintenance Cost (Giảm chi phí sửa chữa định kỳ)
├── 3. Lower Emergency / Overtime Cost (Xóa bỏ gọi thợ khẩn cấp & tăng ca đêm)
├── 4. Spare-Parts & Inventory Optimization (Mua sắm chủ động, tránh cước hỏa tốc)
├── 5. Higher Throughput / Fleet Availability (Tăng số đoàn tàu sẵn sàng giờ cao điểm)
├── 6. Asset Lifetime / CapEx Deferral (Kéo dài tuổi thọ cụm máy nén APU)
└── 7. Safety, Environmental & Service-Risk Avoidance (Triệt tiêu rủi ro sập áp phanh)
```

### Chi tiết ứng dụng trong CompressorGuard:

1. **Value Pool #1 — Avoided Downtime:**  
   - Benchmark ngành: Deloitte ước tính unplanned downtime chiếm $50B/năm trong công nghiệp. NIST chỉ ra nhóm phụ thuộc vào Reactive Maintenance chịu **52.7% nhiều unplanned downtime hơn** nhóm dùng Predictive/Preventive; và Predictive giúp giảm tiếp **18.5% downtime** so với Preventive đơn thuần. DOE ghi nhận giảm downtime **35–45%**.
   - *Trong đường sắt:* Tránh tình huống đoàn tàu chết máy giữa hầm do sập áp phanh (`LPS=1`), buộc phải kéo về Depot gây tê liệt tuyến.
2. **Value Pool #2 — Lower Maintenance Cost:**  
   - Benchmark: IBM ghi nhận giảm **18–31%**, DOE ghi nhận giảm **25–30%** tổng chi phí bảo dưỡng.
   - *Trong đường sắt:* Thay vì đại tu toàn bộ cụm APU khi piston bó kẹt do cháy dầu ($75^\circ\text{C}$), kỹ thuật viên chỉ cần thay gioăng làm kín van xả tháp sấy (Seal Replacement).
3. **Value Pool #3 — Avoided Emergency & Overtime Labor:**  
   - Chuyển đổi từ cơ chế hoảng loạn *"Sự cố xảy ra $\rightarrow$ thợ tăng ca đêm $\rightarrow$ chi phí gấp đôi"* sang quy trình chủ động: 33h 52m cho phép điều độ tàu về trạm bảo dưỡng trong **khung giờ ngừng chạy tàu đêm định kỳ (Non-revenue maintenance window)**.
4. **Value Pool #4 — Spare Parts & Supply Chain Optimization:**  
   - Có trước 33h 52m giúp bộ phận kho phụ tùng chuẩn bị sẵn van sấy khí (Air Dryer Pilot Valve) hoặc gioăng O-ring từ kho trung tâm, triệt tiêu phí vận chuyển hỏa tốc (expedited shipping) và giảm tồn kho chết.
5. **Value Pool #5 — Fleet Availability ("Shadow Fleet"):**  
   - Theo Forrester/Augury, cải thiện 5% khả năng sẵn sàng tương đương với một "nhà máy ngầm / đoàn tàu bổ sung" mà không tốn CapEx mua mới.
   - *SNCF minh chứng:* Giảm số tàu nằm bãi sửa chữa tại Paris Nord từ 9 đoàn xuống 6–7 đoàn $\rightarrow$ tăng ngay 2–3 đoàn tàu phục vụ giờ cao điểm.
6. **Value Pool #6 — Asset Lifetime / CapEx Deferral:**  
   - Ngăn chặn hiện tượng dầu bôi trơn thoái hóa nhiệt ($>74.9^\circ\text{C}$), bảo vệ xilanh máy nén, kéo dài chu kỳ đại tu (Overhaul Cycle) của cụm APU từ 4 năm lên 5–6 năm.
7. **Value Pool #7 — Safety & Service Regulatory Penalties:**  
   - Bảo tồn áp suất phanh khí nén an toàn SIL-2, tránh các khoản phạt hợp đồng vận hành giao thông công cộng do hủy chuyến.

---

## 4. HỆ THỐNG DỮ LIỆU BENCHMARK NGÀNH ĐƯỜNG SẮT
### *(Rail Benchmark Hierarchy)*

CompressorGuard thiết lập thứ bậc nguồn số liệu nghiêm ngặt:

| Thứ bậc | Thực thể / Nghiên cứu | Loại số liệu & Ý nghĩa đối chuẩn |
| :---: | :--- | :--- |
| **Level 1** | **MetroPT-3 Dataset (Lisbon Metro)** *(Nature 2022)* | **Ground Truth hậu quả thực tế:** Sự cố Failure #3 ghi nhận rò rỉ khí làm sập áp khiến đoàn tàu bị cưỡng chế dừng hoạt động và kéo khỏi đường ray (*train had to be removed from tracks*). |
| **Level 2** | **Hanoi Metro (Tuyến 2A Cát Linh - Hà Đông)** *(Báo cáo SXKD 2023 & 2025)* | **Quy mô kinh tế vận hành công khai:**<br>• 2025: 161,611 lượt tàu chạy, 1,756,495 train-km, 20.68 triệu hành khách, doanh thu vé Tuyến 2A đạt 97.78 tỷ VNĐ.<br>• Doanh thu/hành khách: ~7,148 VNĐ; Doanh thu/train-km: ~55,650 VNĐ.<br>• Định mức bảo dưỡng định kỳ: 1.0–1.5% nguyên giá TSCĐ; Sửa chữa lớn: 10–30% chi phí khấu hao.<br>• Bài học thực tế: Sự cố ngày 30/05/2025 (17:36) được cô lập điện và chạy quay đầu ngắn (short-turn) trong 25 phút để duy trì dịch vụ. |
| **Level 3** | **SNCF (Đường sắt Quốc gia Pháp)** *(Digitalisation 2023–2026)* | **Hiệu quả thực chiến CBM trên đầu máy toa xe:**<br>• Giám sát 8,000 biến/đoàn tàu (2,000 real-time), 1,100+ đoàn tàu trang bị IoT.<br>• Giảm sự cố kỹ thuật 50%, giảm sự cố chết máy (breakdowns) hơn 50% đến 66%.<br>• Chi phí bảo dưỡng giảm 20%, số lần vào xưởng giảm 30%.<br>• **Tăng +30% độ sẵn sàng (Availability)** của hạm đội tàu ngoại ô Paris. |
| **Level 4** | **Alstom HealthHub** *(Báo cáo Giải pháp 2023–2026)* | **KPI bảo dưỡng số hóa đường sắt:**<br>• Giảm thời gian chết (Train downtime) lên tới **-30%**.<br>• Giảm chi phí vật tư (Material cost) lên tới **-20%**.<br>• Giảm lỗi lặp lại (Recurring faults) lên tới **-50%**. |
| **Level 5** | **Siemens Mobility (RRX Network)** | **Độ tin cậy vận hành đường sắt:**<br>• Chỉ 1 trên 5,800 chuyến tàu bị trễ do bảo dưỡng trong 3.6 triệu km. |
| **Level 6** | **Shanghai Metro (Tuyến 17 - Air Supply Unit)** *(Nghiên cứu 2026)* | **Khẳng định tính trọng yếu của APU:**<br>• Nghiên cứu chuyên biệt tối ưu chi phí O&M của cụm cấp khí nén VV120 Air Supply Units trên tàu metro bằng RCM. |

---

## 5. CÂY PHÂN CẤP TÀI SẢN & CƠ CHẾ LAN TRUYỀN RỦI RO
### *(Asset Hierarchy & Value Propagation)*

Sự cố máy nén không dừng lại ở mức linh kiện đơn lẻ. Giá trị kinh tế được truyền dẫn ngược lên theo chuỗi phân cấp:

```
[ FLEET LEVEL ]       Lisbon Metro Blue Line Fleet (Hạm đội tàu)
      ▲               Impact: Giảm tỷ lệ tàu dự phòng, bảo toàn biểu đồ chạy tàu
      │
[ TRAIN LEVEL ]       Metro Train #302 (Đoàn tàu vận hành)
      ▲               Impact: Nguy cơ chết máy giữa hầm, cứu hộ kéo tàu (€10k-€20k)
      │
[ SUBSYSTEM LEVEL ]   Air Production Unit (APU) (Hệ thống cấp khí nén)
      ▲               Impact: Mất áp suất phanh khí nén, mất điều khiển đóng mở cửa
      │
[ COMPONENT LEVEL ]   Compressor APU-COMP-01 (Máy nén piston & Tháp sấy khí)
                      Root: Rò rỉ van xả tháp sấy (DV_pressure = 2.18 bar, +23.75σ)
```

**Nguyên lý vận hành:**
- *Cảm biến đo đạc tại cấp Component (Compressor)*.
- *Bằng chứng được tổng hợp tại cấp Subsystem (APU)*.
- *Quyết định can thiệp bảo vệ cấp Train (Đoàn tàu)*.
- *Giá trị kinh tế & khả năng sẵn sàng đo lường tại cấp Fleet (Hạm đội)*.

---

## 6. OPERATIONAL CASE LÀ ĐƠN VỊ KINH TẾ CỐT LÕI
### *(Case-Centric Value Funnel)*

Theo nghiên cứu từ các hệ thống APM lớn (như GE Digital / EDP: 450 tài sản, 1,300 mô hình, 570 ca điều tra nhưng chỉ có **25 catches thực sự mang lại tác động kinh tế**), việc chạy theo số lượng "anomaly score" là sai lầm.

CompressorGuard xây dựng **Phễu Lọc Giá Trị Vận Hành (Operational Funnel)**:

```
1,000 Dị thường cảm biến thô (Transient spikes)
  │
  ▼
100 Trạng thái lệch ngưỡng (Threshold excursions)
  │
  ▼
 20 Sự cố được bằng chứng xác nhận (Confirmed by Thermodynamics & Persistence)
  │
  ▼
 15 Hồ sơ vận hành có thể can thiệp (Actionable Operational Cases)
  │
  ▼
 12 Can thiệp chế độ an toàn (Safe Mode Interventions)
  │
  ▼
 10 Kiểm chứng phục hồi hoàn tất (Verified Recoveries)
  │
  ▼
 🏆 CHỈ SỐ KINH TẾ ĐƯỢC BẢO VỆ (MEASURABLE VALUE OUTCOME)
```

Mỗi **Operational Case** là một đơn vị kinh doanh (Business Unit) có chủ sở hữu, mốc thời gian, chi phí rủi ro và kết quả phục hồi.

---

## 7. CƠ CHẾ KINH TẾ CỦA TÍNH TƯỜNG MINH
### *(Explainability & Trust Economics)*

### 7.1 Giá Trị Giảm Giờ Kỹ Sư Điều Tra (Engineering Hours Saved)
* **Quy trình cũ (Hộp đen AI / Cảnh báo thô):**
  - Nhận cảnh báo: *"Anomaly Score = 0.91"*.
  - Chuyên viên mất **20–30 phút** mở từng đồ thị cảm biến thô, đối chiếu chế độ tải, kiểm tra lịch sử để xác minh đây có phải là báo động giả.
* **Quy trình CompressorGuard (Evidence Dossier):**
  - Màn hình dọn sẵn 4 bằng chứng tương quan vật lý ($+23.75\sigma$ áp suất, $+5.71\sigma$ nhiệt độ, 3 chu kỳ kiên định, Isolation Forest $0.382$).
  - Thời gian ra quyết định rút ngắn từ **20 phút xuống 3 phút** (Tiết kiệm 17 phút/sự cố).
  - Định lượng: $17\text{ phút} \times \text{Chi phí chuyên viên/giờ} \times \text{Số lượng sự cố hàng năm}$.

### 7.2 False Positive Rate Là Chỉ Số Sống Còn Của Áp Dụng (Adoption)
Nếu tỷ lệ báo động giả cao, chuyên viên sẽ phớt lờ cảnh báo (*Alert Fatigue*).
- Nghiên cứu của Fiberon / Augury chỉ ra: Tỷ lệ phản hồi cảnh báo đạt **96%** đã chuyển hóa trực tiếp thành $274K tránh thất thoát và 178 giờ tránh downtime.
- Việc CompressorGuard tách biệt nghiêm ngặt chế độ **`LOADED` vs `UNLOADED`** chính là cơ chế bảo vệ lòng tin của operator, đảm bảo tỷ lệ phản hồi hành động đạt tối đa.

---

## 8. MÔ HÌNH ĐỊNH LƯỢNG GIÁ TRỊ COMPRESSORGUARD
### *(Configurable Value Model)*

Thay vì hardcode một con số cố định, CompressorGuard cung cấp **Bộ tham số giả định kinh tế minh bạch** để người dùng hoặc ban giám khảo tự điều chỉnh theo quy mô thực tế:

### 8.1 Công Thức Tính Tổng Thể (The Master Value Formula)
$$\text{Gross Avoided Impact} = V_{\text{downtime}} + V_{\text{emergency\_labor}} + V_{\text{logistics}} + V_{\text{investigation\_hours}}$$

Trong đó:
1. $V_{\text{downtime}} = T_{\text{avoided\_downtime\_hours}} \times C_{\text{downtime\_cost\_per\_hour}}$
2. $V_{\text{emergency\_labor}} = \text{Tiết kiệm phụ phí tăng ca / gọi thợ khẩn cấp đêm}$
3. $V_{\text{logistics}} = \text{Tiết kiệm cước vận chuyển linh kiện hỏa tốc}$
4. $V_{\text{investigation\_hours}} = \Delta t_{\text{investigation}} \times C_{\text{engineer\_hourly\_rate}}$

### 8.2 Ba Kịch Bản Giả Định (Configurable Scenarios Cho Demo/Pitch)

| Tham số kịch bản | Kịch Bản Thận Trọng (Conservative) | Kịch Bản Cơ Sở (Base Metro Case) | Kịch Bản Nghiêm Trọng (Severe Incident) |
| :--- | :---: | :---: | :---: |
| **Ngữ cảnh sự cố** | Thay thế van tại Depot trong ca nghỉ trưa | Hỏng van buộc hủy 2 ca chạy giờ thấp điểm | Chết máy trong hầm giờ cao điểm, phải cứu hộ |
| **Downtime tránh được ($T_{\text{downtime}}$)** | **4 giờ** | **12 giờ** | **24 giờ** |
| **Chi phí giờ dừng tàu ($C_{\text{hour}}$)** | **€1,200 / giờ** | **€2,500 / giờ** | **€5,000 / giờ** |
| **Tổn thất downtime ước tính ($V_{\text{downtime}}$)** | **€4,800** | **€30,000** | **€120,000** |
| **Tiết kiệm sửa chữa khẩn cấp / phụ kiện** | **€500** | **€2,000** | **€8,500** |
| **Tiết kiệm giờ điều tra kỹ thuật (Labor)** | **€150** | **€350** | **€800** |
| **TỔNG GIÁ TRỊ TRÁNH THẤT THOÁT (Gross)** | **€5,450** | **€32,350** | **€129,300** |

> [!IMPORTANT]
> **Quy tắc hiển thị trên giao diện:**
> Bắt buộc ghi nhãn: `Estimated Avoided Cost (Scenario Model)` — **Tuyệt đối không ghi `Realized Profit`** để duy trì tính trung thực trí tuệ cao nhất.

---

## 9. ĐẶC TẢ JSON SCHEMA DTO CHO BUSINESS IMPACT API

Dành cho endpoint `GET /api/incident/business-impact` (hoặc nhúng vào `GET /api/incident`):

```json
{
  "case_id": "APU-CASE-20200605-01",
  "asset_context": {
    "fleet_id": "METRO-LISBON-BLUE",
    "train_id": "TRAIN-302",
    "subsystem": "AIR_PRODUCTION_UNIT",
    "component_id": "APU-COMP-01"
  },
  "operational_window": {
    "observed_lead_time_formatted": "33h 52m",
    "observed_lead_time_minutes": 2032,
    "onset_timestamp": "2020-06-05T09:50:39Z",
    "conventional_lps_timestamp": "2020-06-06T19:42:19Z"
  },
  "economic_model": {
    "scenario_name": "BASE_METRO_DISRUPTION",
    "parameters": {
      "downtime_cost_per_hour_eur": 2500.0,
      "estimated_avoided_downtime_hours": 12.0,
      "emergency_overtime_premium_eur": 2000.0,
      "engineering_minutes_saved": 17.0,
      "engineer_loaded_rate_eur_per_hour": 75.0
    },
    "calculated_impact": {
      "avoided_downtime_value_eur": 30000.0,
      "avoided_emergency_premium_eur": 2000.0,
      "labor_investigation_saved_eur": 21.25,
      "total_gross_avoided_impact_eur": 32021.25
    },
    "disclaimer": "Scenario model projection based on European rail operator benchmarks. Not historical realized cash."
  },
  "recovery_verification": {
    "status": "VERIFIED",
    "consecutive_loaded_observations": 5,
    "recovery_timestamp": "2020-06-08T16:05:50Z"
  }
}
```

---

## 10. DANH MỤC TÀI LIỆU THAM KHẢO ĐÃ XÁC MINH
### *(Verified Reference Links)*

Dưới đây là các tài liệu và nghiên cứu thực tế làm chỗ dựa vững chắc cho toàn bộ mô hình kinh tế của CompressorGuard:

1. **SNCF — Predictive Maintenance & Fleet Availability (+30% availability):**  
   [https://www.groupe-sncf.com/en/innovation/digitalization/predictive-maintenance](https://www.groupe-sncf.com/en/innovation/digitalization/predictive-maintenance)
2. **Alstom — HealthHub / Digital Railway Solutions (Up to -30% downtime):**  
   [https://www.alstom.com/solutions/services/digital-railway-solutions-unlock-higher-asset-availability-reliability-and-performance](https://www.alstom.com/solutions/services/digital-railway-solutions-unlock-higher-asset-availability-reliability-and-performance)
3. **Alstom — HealthHub Customer Case Results (-20% material cost, -50% recurring faults):**  
   [https://www.alstom.com/press-releases-news/2023/2/healthhub-intelligent-way-improve-maintenance](https://www.alstom.com/press-releases-news/2023/2/healthhub-intelligent-way-improve-maintenance)
4. **Alstom — Digital Rail: 30% Less Downtime & Higher Availability:**  
   [https://www.alstom.com/stories/future-rail-digital](https://www.alstom.com/stories/future-rail-digital)
5. **Alstom — Total Cost of Ownership (TCO) & Lifecycle Optimization:**  
   [https://www.alstom.com/press-releases-news/2026/3/total-cost-ownership-how-alstoms-adessia-commuter-trains-provide-best-value-money](https://www.alstom.com/press-releases-news/2026/3/total-cost-ownership-how-alstoms-adessia-commuter-trains-provide-best-value-money)
6. **Hanoi Metro — Báo Cáo Vận Hành 2025 (Doanh thu, Hành khách, Train-km):**  
   [https://metrohanoi.vn/ha-noi-metro-to-chuc-hoi-nghi-trien-khai-nhiem-vu-cong-tac-nam-2026/](https://metrohanoi.vn/ha-noi-metro-to-chuc-hoi-nghi-trien-khai-nhiem-vu-cong-tac-nam-2026/)
7. **Hanoi Metro — Kế Hoạch SXKD 2021–2025 & Cấu Trúc Chi Phí O&M:**  
   [https://metrohanoi.vn/wp-content/uploads/2020/01/K%E1%BA%BF-ho%E1%BA%A1ch-SXKD-v%C3%A0-DTPT-5-n%C4%83m-2021-2025.pdf](https://metrohanoi.vn/wp-content/uploads/2020/01/K%E1%BA%BF-ho%E1%BA%A1ch-SXKD-v%C3%A0-DTPT-5-n%C4%83m-2021-2025.pdf)
8. **MetroPT-3 Dataset — Nature Scientific Data (2022) (Ground truth Failure #3):**  
   [https://www.nature.com/articles/s41597-022-01877-3](https://www.nature.com/articles/s41597-022-01877-3)
9. **Shanghai Metro Line 17 — Air Supply Unit O&M Optimization (2026):**  
   [https://umt1998.tongji.edu.cn/en/article/doi/10.16037/j.1007-869x.20260054](https://umt1998.tongji.edu.cn/en/article/doi/10.16037/j.1007-869x.20260054)

---
*Tài liệu được thiết lập theo quy chuẩn kỹ thuật và kinh tế vận hành đường sắt công nghiệp.*
