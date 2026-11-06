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

### 🎯 Chiến Lược Ngữ Cảnh Kép (Dual-Context Pitching Strategy):
Hệ thống kết hợp chặt chẽ giữa 2 tầng ngữ cảnh để vừa đảm bảo độ tin cậy khoa học, vừa gây ấn tượng thực chiến tại thị trường Việt Nam:
1. **Tầng Kỹ Thuật Đối Chứng (Technical Ground Truth — Châu Âu / EUR €):** Sử dụng tập dữ liệu thực 1.5M mẫu từ **Lisbon Metro (MetroPT-3)** để chứng minh vật lý suy thoái van xả (+23.75σ) và lead-time 33h 52m không thể chối cãi.
2. **Tầng Kinh Tế Triển Khai Thực Chiến (Commercial Deployment Horizon — Việt Nam / VNĐ ₫):** Ưu tiên quy đổi và mô hình hóa giá trị kinh tế theo **VNĐ (Việt Nam Đồng)**, dựa trên bài toán vận hành thực tế của **Hà Nội Metro (Tuyến 2A Cát Linh - Hà Đông & Tuyến 3)** và **TP.HCM Metro (Tuyến 1 Bến Thành - Suối Tiên)** trước cột mốc hết hạn bảo hành nhà thầu vào cuối năm 2026.

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
| **Level 2** | **Hanoi Metro (Tuyến 2A & Tuyến 3)** *(Báo cáo Thành phố 01/2026 & 05/2026)* | **Quy mô kinh tế & Chu kỳ bảo dưỡng thực tế:**<br>• Lũy kế đến 30/04/2026: **>493,000 lượt tàu chạy**, phục vụ **>62.2 triệu lượt khách** trên 2 tuyến (Tuyến 2A: 13 đoàn tàu, Tuyến 3 trên cao: 10 đoàn tàu).<br>• Năm 2025: Tuyến 2A đạt 161,611 lượt tàu, 1,756,495 train-km, 20.68 triệu khách, doanh thu vé đạt 97.78 tỷ VNĐ (~55,650 VNĐ/train-km).<br>• **Tài liệu Kỹ thuật Gốc:** [*Sổ tay YN-007 (Chương 7: Hệ thống hãm và cấp khí)*](https://www.scribd.com/document/788322712/YN-007-Chuong-7-H%E1%BB%87-th%E1%BB%91ng-ham-va-c%E1%BA%A5p-khi-S%E1%BB%95-tay-%C4%91ao-t%E1%BA%A1o) quy định tại Bảng 7-17 (trang 7-60): Kiểm tra/bổ sung dầu bôi trơn **6 tháng**; Vệ sinh bộ làm mát, kiểm tra công tắc áp suất, thay lõi lọc khí & lọc dầu/gioăng **1 năm**.<br>• **Điểm nóng 2026:** Ngày 14/01/2026, UBND TP. Hà Nội chỉ đạo lập kế hoạch đại tu giữa kỳ cho 13 đoàn tàu Tuyến 2A, ưu tiên chuyển giao công nghệ và các giải pháp quản lý bảo trì tích hợp. Tháng 10/2026 ký thỏa thuận 200 đoàn tàu Alstom Metropolis kèm chuyển giao công nghệ. |
| **Level 2.5** | **HCMC Metro (Tuyến 1 Bến Thành - Suối Tiên)** *(MAUR & Báo cáo Chính phủ 2026)* | **Áp lực chuyển giao & Hết hạn bảo hành cuối 2026:**<br>• Phục vụ **>30.35 triệu lượt khách** (01/2025 – đầu tháng 06/2026) với 17 đoàn tàu Hitachi (51 toa).<br>• **Tài liệu Kỹ thuật Gốc:** [*Kế hoạch Bảo dưỡng Dự án UMRT L1-CP3-GL-O&M-PLN-00001-D-R0 (Rev D)*](https://www.scribd.com/document/845060878/UMRTL1-CP3-GL-O-M-PLN-00001-D-R0-Submission-of-Maintenance-Plan-Rev-D-en-VN-B%E1%BA%A3o-D%C6%B0%E1%BB%A1ng) tại Bảng T5.1 (trang 32–33) quy định các mốc bảo dưỡng máy nén khí: **1 tuần** (trực quan), **1 tháng** (hiệu năng), và **4 năm** (đại tu trong xưởng depot).<br>• **Thời điểm then chốt:** Bảo hành của nhà thầu hết hạn vào **cuối năm 2026**. Đề án chuyển giao công nghệ (09/2026) đặt mục tiêu kỹ sư Việt Nam làm chủ **90%** quy trình bảo dưỡng.<br>• Ngày 17/07/2026: MAUR ký MoU với GTEL về ứng dụng AI, IoT, Big Data, Digital Twin trong vận hành bảo trì đường sắt đô thị (mục tiêu 200 km trước năm 2030, vốn >20 tỷ USD). |
| **Level 3** | **Singapore LTA & SMRT (2025)** *(Chế tài pháp lý & Phạt gián đoạn)* | **Rủi ro tài chính do sự cố kỹ thuật:**<br>• Tháng 07/2025: LTA phạt SMRT **2.4 triệu SGD (S$2.4M)** sau sự cố tê liệt tuyến East-West Line tháng 09/2024 và yêu cầu đầu tư thêm ít nhất **600,000 SGD** vào năng lực đại tu và dự phòng phụ tùng. |
| **Level 4** | **SNCF (Đường sắt Quốc gia Pháp)** *(Digitalisation 2023–2026)* | **Hiệu quả thực chiến CBM trên đầu máy toa xe:**<br>• Giám sát 8,000 biến/đoàn tàu (2,000 real-time), 1,100+ đoàn tàu trang bị IoT.<br>• Giảm sự cố kỹ thuật 50%, giảm sự cố chết máy (breakdowns) hơn 50% đến 66%.<br>• Chi phí bảo dưỡng giảm 20%, số lần vào xưởng giảm 30%.<br>• **Tăng +30% độ sẵn sàng (Availability)** của hạm đội tàu ngoại ô Paris (giảm tàu nằm bãi từ 9 xuống 6–7 đoàn). |
| **Level 5** | **Alstom HealthHub** *(Báo cáo Giải pháp 2023–2026)* | **KPI bảo dưỡng số hóa đường sắt:**<br>• Giảm thời gian chết (Train downtime) lên tới **-30%**.<br>• Giảm chi phí vật tư (Material cost) lên tới **-20%**.<br>• Giảm lỗi lặp lại (Recurring faults) lên tới **-50%**.<br>• Case Dubai Tram (2023): Tăng hiệu suất dịch vụ hành khách lên 40% sau 1 năm triển khai real-time monitoring. |
| **Level 6** | **Knorr-Bremse AirSupply Smart** *(Tài liệu Kỹ thuật 2022–2026)* | **Chuẩn mực giám sát máy nén khí thông minh:**<br>• Tích hợp giám sát tình trạng (Condition Monitoring) dựa trên áp suất, dòng biến tần và nhiệt độ, khẳng định phát hiện suy thoái sớm là cốt lõi để ngăn ngừa sự cố bất ngờ. |
| **Level 7** | **Shanghai Metro (Tuyến 17 - Air Supply Unit)** *(Nghiên cứu 2026)* | **Khẳng định tính trọng yếu của APU:**<br>• Nghiên cứu chuyên biệt tối ưu chi phí O&M của cụm cấp khí nén VV120 bằng RCM: chứng minh suy thoái vòng bi động cơ và thoái hóa gioăng xilanh áp suất thấp là 2 nguyên nhân cốt lõi cần phát hiện sớm. |

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

### 8.3 So Sánh Chi Phí Can Thiệp Cụ Thể (Reactive Overhaul vs. Planned Intervention)

Dựa trên dữ liệu tổng hợp chi phí kỹ thuật đường sắt (2026), sự chênh lệch giữa can thiệp sớm và để sự cố phát tác trên tuyến là một đòn bẩy tài chính khổng lồ:

| Hạng mục chi phí | Can thiệp Chủ động tại Depot (Planned PdM) | Sự cố Buộc Rút Tàu Trên Tuyến (In-Service Failure) |
| :--- | :---: | :---: |
| **Nhân công chẩn đoán & sửa chữa** | €150 – €300 (ca ngày/đêm định kỳ) | €500 – €2,000 (tăng ca đêm khẩn cấp) |
| **Cứu hộ, dồn tàu & kéo về depot** | €0 (tự di chuyển trong ca trống) | €500 – €5,000 (phụ thuộc vào vị trí & mức độ tắc nghẽn) |
| **Phụ tùng thay thế & Logistics** | €100 – €500 (thay phớt/van, kho sẵn) | €500 – €3,000 (hỏng lây xilanh/cháy motor, cước hỏa tốc) |
| **Điều hành & khôi phục dịch vụ** | €0 (không ảnh hưởng biểu đồ) | €500 – €5,000 (điều độ lại toàn tuyến) |
| **Rủi ro chế tài & bồi thường hành khách** | €0 | €0 – €20,000+ (phạt hợp đồng / bồi thường EU 2021/782) |
| **TỔNG CHI PHÍ ƯỚC TÍNH MỖI SỰ CỐ** | **€250 – €800** | **€2,000 – €35,000+** |

### 8.4 Mô Hình Định Lượng Kinh Tế Đường Sắt Đô Thị Việt Nam (Đơn Vị VNĐ ₫)
*(Phục vụ trực tiếp cho Chiến lược Pitching & Kế hoạch Thương mại hóa nội địa)*

Để ban giám khảo và đối tác vận hành metro tại Việt Nam (Hanoi Metro, MAUR TP.HCM) hình dung rõ rệt tác động tài chính, CompressorGuard thiết lập bảng quy đổi giá trị sang **Việt Nam Đồng (VNĐ)** (tỷ giá tham chiếu $1\text{ EUR} \approx 27.500\text{ VNĐ}$):

#### A. So sánh chi phí can thiệp sự cố trực tiếp (VNĐ):
| Hạng mục chi phí | Can thiệp Chủ động tại Depot (Planned PdM) | Sự cố Buộc Rút Tàu Trên Tuyến (In-Service Failure) |
| :--- | :---: | :---: |
| **Nhân công chẩn đoán & xử lý** | 4.100.000 – 8.200.000 VNĐ | 13.700.000 – 55.000.000 VNĐ (tăng ca đêm khẩn) |
| **Cứu hộ kéo tàu & dồn đường xưởng** | 0 VNĐ (tự hành về depot ca trống) | 13.700.000 – 137.500.000 VNĐ (kéo tàu tắc hầm) |
| **Phụ tùng, gioăng van & logistics** | 2.700.000 – 13.700.000 VNĐ (thay gioăng van sấy) | 13.700.000 – 82.500.000 VNĐ (cháy motor/xilanh, cước gấp) |
| **Tái lập điều hành & biểu đồ chạy tàu** | 0 VNĐ (không chậm giờ) | 13.700.000 – 137.500.000 VNĐ (xáo trộn lịch toàn tuyến) |
| **Rủi ro đền bù / thiệt hại doanh thu** | 0 VNĐ | 0 – 550.000.000+ VNĐ (hàng vạn khách ùn ứ) |
| **TỔNG TỔN THẤT ƯỚC TÍNH / SỰ CỐ** | **6.800.000 – 22.000.000 VNĐ** | **55.000.000 – 962.500.000+ VNĐ** |

> **Đòn bẩy kinh tế:** Phát hiện suy thoái sớm 33h 52m giúp chuyển sự cố từ nhánh **chết máy trên tuyến (>50–900 triệu VNĐ)** về nhánh **sửa chữa định kỳ ban đêm (~7–20 triệu VNĐ)**, tiết kiệm **hơn 90%** tổng chi phí khắc phục.

#### B. Ba kịch bản giá trị bảo vệ hằng năm cho Hạm đội Metro Việt Nam:
*(Quy mô 23 đoàn tàu Hà Nội hoặc 17 đoàn tàu TP.HCM)*

| Tham số kịch bản | Kịch Bản Thận Trọng (Conservative) | Kịch Bản Cơ Sở (Base Metro Case) | Kịch Bản Nghiêm Trọng (Severe Incident) |
| :--- | :---: | :---: | :---: |
| **Giả định sự cố tránh được** | Tránh 2 ca hỏng van nhỏ được sửa ban ngày | Tránh 4 ca sự cố hủy chuyến giờ thấp điểm | Tránh 1 ca sập áp phanh chết máy giữa hầm giờ cao điểm |
| **Tổn thất downtime tránh được** | 132.000.000 VNĐ (8 giờ) | 825.000.000 VNĐ (48 giờ) | 3.300.000.000 VNĐ (24 giờ cao điểm) |
| **Tiết kiệm phụ phí sửa chữa khẩn cấp** | 13.700.000 VNĐ | 55.000.000 VNĐ | 233.750.000 VNĐ |
| **Tiết kiệm giờ kỹ sư điều tra (17 phút/ca)** | 4.100.000 VNĐ | 9.600.000 VNĐ | 22.000.000 VNĐ |
| **TỔNG GIÁ TRỊ TRÁNH THẤT THOÁT / NĂM** | **~150.000.000 VNĐ** | **~890.000.000 VNĐ** | **~3.550.000.000 VNĐ (3.55 tỷ VNĐ)** |

#### C. Lợi ích "Hạm đội bóng ma" (Shadow Fleet) tránh CapEx:
* Mua mới 1 đoàn tàu metro 4 toa tại Việt Nam có giá từ **200 – 250 tỷ VNĐ** (\$8M – \$10M) với thời gian đặt hàng từ 2–3 năm.
* Tăng **2% khả năng sẵn sàng (Availability)** trên hạm đội 23 đoàn tàu tại Hà Nội mang lại giá trị tương đương **0.46 đoàn tàu vận hành thực tế** (~100 tỷ VNĐ giá trị tài sản khai thác) hoàn toàn không phát sinh vốn đầu tư công.

---

### 8.5 Chu Kỳ Bảo Dưỡng Máy Nén Khí Thực Tế & Công Thức Chuyển Đổi Sang CBM
*(Đối chiếu trực tiếp Sổ tay YN-007, Kế hoạch UMRT L1 và Chuẩn Knorr-Bremse)*

Thay vì áp đặt một chu kỳ bảo dưỡng cứng nhắc, CompressorGuard liên kết giữa **Chu kỳ định kỳ theo tài liệu kỹ thuật (Time-based)** và **Tình trạng suy thoái cảm biến thực tế (Condition-based)**:

1. **Chu kỳ định kỳ theo Tài liệu Kỹ thuật Dự án Việt Nam:**
   * **Tuyến 2A Cát Linh – Hà Đông (Sổ tay YN-007, Bảng 7-17):**
     * Kiểm tra mức dầu: Hàng ngày, hàng tháng.
     * Kiểm tra & bổ sung dầu bôi trơn: **6 tháng**.
     * Vệ sinh bộ làm mát, đo kiểm công tắc áp suất, thay lõi lọc khí & bộ lọc dầu/gioăng: **1 năm**.
   * **Tuyến 1 Bến Thành – Suối Tiên (Hitachi, Kế hoạch UMRT L1, Bảng T5.1):**
     * Kiểm tra trực quan: **1 tuần**.
     * Kiểm tra hiệu năng: **1 tháng**.
     * Đại tu xưởng (Depot Overhaul): **4 năm**.
2. **Chuẩn mực OEM Knorr-Bremse (Máy nén trục vít SKP & Piston VV120-T):**
   * Giới hạn thay dầu & bộ lọc kết tụ: **1.500 giờ vận hành thực tế (operating hours)** hoặc **tối đa 12 tháng**.
3. **Công thức động tính thời điểm đến hạn bảo dưỡng/thay dầu trong CompressorGuard:**
   $$T_{\text{due}} = \min\left(\frac{1500 - H_{\text{used}}}{h_{\text{daily}}},\ 12 - M_{\text{elapsed}}\right)$$
   * $H_{\text{used}}$: Số giờ chạy thực tế của máy nén khí (đo qua sensor dòng điện/áp suất khi máy nén đóng tải).
   * $h_{\text{daily}}$: Số giờ chạy trung bình mỗi ngày theo biểu đồ chạy tàu.
   * $M_{\text{elapsed}}$: Số tháng đã trôi qua kể từ lần bảo dưỡng gần nhất.
   * **Cơ chế CBM:** Khi CompressorGuard phát hiện nhiệt độ dầu leo dốc ($+5.71\sigma$, đạt $74.9^\circ\text{C}$ như Failure #3), hệ thống cảnh báo dầu đang thoái hóa nhiệt sớm trước mốc 1.500 giờ, tự động rút ngắn $T_{\text{due}}$ để ngăn bó kẹt xilanh.

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
10. **Singapore LTA — Quyết định xử phạt SMRT S$2.4M & Yêu cầu đầu tư đại tu phụ tùng (07/2025):**  
    Land Transport Authority enforcement action on East-West Line disruption.
11. **UITP — Global Metro Figures 2024 (Thống kê mạng lưới metro toàn cầu, phát hành 05/2025):**  
    Báo cáo thống kê 247 mạng lưới metro tại 202 vùng đô thị, phục hồi sản lượng và tăng trưởng 37% mạng lưới Trung Quốc.
12. **European Union — Regulation (EU) 2021/782 (Điều ước bồi thường chậm trễ tàu chở khách):**  
    Quy định mức bồi thường 25% (trễ 60–119 phút) và 50% (trễ ≥120 phút) giá vé hành khách.
13. **HCMC MAUR & GTEL — Biên bản ghi nhớ MoU Hệ thống số hóa & Vận hành bảo trì Metro (17/07/2026):**  
    Kế hoạch hợp tác AI, IoT, Digital Twin cho 6 tuyến metro 200 km (>20 tỷ USD) tại TP.HCM.
14. **Knorr-Bremse — AirSupply Smart & Embedded Rail Compressor Condition Monitoring (2022–2026):**  
    Tài liệu kỹ thuật chuẩn công nghiệp về giám sát tình trạng cụm cấp khí nén đoàn tàu.
15. **Hanoi Metro Tuyến 2A — Sổ tay Đào tạo Kỹ thuật YN-007 (Chương 7: Hệ thống hãm và cấp khí):**  
    [https://www.scribd.com/document/788322712/YN-007-Chuong-7-H%E1%BB%87-th%E1%BB%91ng-ham-va-c%E1%BA%A5p-khi-S%E1%BB%95-tay-%C4%91ao-t%E1%BA%A1o](https://www.scribd.com/document/788322712/YN-007-Chuong-7-H%E1%BB%87-th%E1%BB%91ng-ham-va-c%E1%BA%A5p-khi-S%E1%BB%95-tay-%C4%91ao-t%E1%BA%A1o) (Bảng 7-17, trang 7-60).
16. **TP.HCM Metro Tuyến 1 — Kế hoạch Bảo dưỡng Đoàn tàu UMRT L1-CP3-GL-O&M-PLN-00001-D-R0 (Rev D):**  
    [https://www.scribd.com/document/845060878/UMRTL1-CP3-GL-O-M-PLN-00001-D-R0-Submission-of-Maintenance-Plan-Rev-D-en-VN-B%E1%BA%A3o-D%C6%B0%E1%BB%A1ng](https://www.scribd.com/document/845060878/UMRTL1-CP3-GL-O-M-PLN-00001-D-R0-Submission-of-Maintenance-Plan-Rev-D-en-VN-B%E1%BA%A3o-D%C6%B0%E1%BB%A1ng) (Bảng T5.1, trang 32–33).
17. **Báo cáo Nghiên cứu Thị trường & Kinh tế Vận hành Đường sắt Đô thị (Deep Research Phần 1):**  
    [https://chatgpt.com/share/6ad32e70-51d8-83ec-9827-be65fabe85a9](https://chatgpt.com/share/6ad32e70-51d8-83ec-9827-be65fabe85a9)
18. **Báo cáo Nghiên cứu Chu kỳ Bảo dưỡng Máy nén khí Metro Việt Nam & Knorr-Bremse (Deep Research Phần 2):**  
    [https://chatgpt.com/share/6ad333ef-1e48-83ec-a42c-5d56d35ad3d0](https://chatgpt.com/share/6ad333ef-1e48-83ec-a42c-5d56d35ad3d0)

---
*Tài liệu được thiết lập theo quy chuẩn kỹ thuật và kinh tế vận hành đường sắt công nghiệp.*
