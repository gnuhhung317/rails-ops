# COMPRESSORGUARD — OPERATIONS CONSOLE SCREEN SPECIFICATIONS
> **Document Type:** UI/UX Screen Architecture & Design System  
> **Status:** Active Normative Specification (v2.3 Fleet-Centric Alignment)  
> **Target:** Operations Command Platform for Critical Rail Fleet Assets  
> **Domain Standards:** Aligned with Siemens Senseye, IBM Maximo, Alstom HealthHub, and Datadog Incident Timelines

---

## 1. TRIẾT LÝ ĐIỀU HÀNH & CẤU TRÚC ĐIỀU HƯỚNG TỔNG THỂ

Thay vì nhồi nhét tất cả biểu đồ, bảng số liệu và nút bấm lên một dashboard phẳng (Dashboard Flat Anti-Pattern), CompressorGuard tổ chức không gian làm việc của chuyên viên vận hành (Fleet Operations Specialist) theo **Cấu trúc phân cấp hạm đội chuẩn Enterprise APM**:

```text
OPERATIONS COMMAND CONSOLE
│
├── 📂 [NAV 1] OPERATIONS / FLEET ASSETS LANDING (Screen 01)
│   └── Cây phân cấp hạm đội: Metro Fleet (Linha Azul) ──► Train #302 ──► APU ──► APU-COMP-01
│       ├── Bộ đếm vận hành thực tế: 1 Monitored Asset | 0/1 Active Cases | 1 Train At Risk
│       ├── Giám sát điều kiện tức thời (Current Condition & Context: LOADED / UNLOADED)
│       └── Trình diễn chống báo động ảo lúc 00:33:07 (Noise Rejection Demo — Case creation suppressed)
│
├── 🚨 [NAV 2] ACTIVE CASES LIST (Screen 02)
│   └── Thực thi bất biến Siemens: "Chỉ tối đa một Active Case trên một Asset tại một thời điểm"
│   └── CASE-20200605-01: Confirmed Discharge Valve Leakage (Lead Time: 33h 52m Confirmed Intervention Window)
│
└── 🛠️ [NAV 3] CASE WORKSPACE (Screens 03 - 07)
    ├── Tab 1: WHAT CHANGED? (Screen 03)
    │   └── Cấu trúc 4 tầng: Observed Data ──► Operational Condition ──► Business Context ──► Validation Ref
    ├── Tab 2: WHY? (EVIDENCE DOSSIER) (Screen 04)
    │   └── 4 Thẻ bằng chứng có Provenance (Áp suất +23.75σ, Nhiệt độ +5.71σ, Bước nhảy 3 chu kỳ)
    │   └── Kiểm chứng đa biến độc lập bởi Isolation Forest (5 features, LOADED baseline, vai trò Corroboration)
    ├── Tab 3: WHAT DID WE DO? (Screen 05)
    │   └── Hàng rào ActionGuard 5 điều kiện chính sách ──► Kích hoạt Safe Mode mô phỏng (Simulated Intervention)
    │   └── Rẽ nhánh con trỏ dữ liệu sang phân đoạn thực tế sau bảo trì (Post-Maintenance Historical Segment)
    ├── Tab 4: DID IT WORK? (Screen 06)
    │   └── Recovery Criteria Verified (5/5 healthy observations trong LOADED: DV < 0.05 bar, Oil < 67°C)
    │   └── Nghiệm thu đóng hồ sơ (POST /api/case/close) ──► Giải phóng Asset về trạng thái HEALTHY
    ├── Tab 5: CASE TIMELINE (Screen 07)
    │   └── Sổ cái CaseEvent dạng append-only (Quan sát ──► Xác nhận ──► ML ──► Can thiệp ──► LPS ──► Hồi phục)
    └── 🗄️ VALIDATION REFERENCE DRAWER (Ngăn kéo đối chứng độc lập)
        └── Báo cáo bảo dưỡng thực tế Failure #3 (Air Leak / High Stress) từ dataset MetroPT-3 để đối chứng
```

---

## 2. DANH MỤC CÁC TỆP ĐẶC TẢ MÀN HÌNH

| Mã màn hình | Tên tệp đặc tả | Trọng tâm giải quyết |
| :---: | :--- | :--- |
| **SCREEN 01** | [`01_OPERATIONS_NAV_AND_ASSET_OVERVIEW.md`](./01_OPERATIONS_NAV_AND_ASSET_OVERVIEW.md) | Operations Landing Page: Cây phân cấp Hạm đội $\rightarrow$ Tàu $\rightarrow$ APU $\rightarrow$ Máy nén, bộ đếm vận hành trung thực, demo chống báo động giả lúc `00:33:07`. |
| **SCREEN 02** | [`02_ACTIVE_CASES_LIST.md`](./02_ACTIVE_CASES_LIST.md) | Bảng danh sách Hồ sơ sự cố đang hoạt động, thực thi bất biến Siemens (1 Asset = tối đa 1 Active Case), liên kết trực tiếp vào cây phân cấp hạm đội. |
| **SCREEN 03** | [`03_CASE_WORKSPACE_WHAT_CHANGED.md`](./03_CASE_WORKSPACE_WHAT_CHANGED.md) | Phân tầng 4 khối: Observed $\rightarrow$ Operational Condition $\rightarrow$ Business Context $\rightarrow$ Validation Reference; Cửa sổ can thiệp xác nhận $33\text{h } 52\text{m}$. |
| **SCREEN 04** | [`04_CASE_WORKSPACE_WHY_EVIDENCE.md`](./04_CASE_WORKSPACE_WHY_EVIDENCE.md) | Bộ 4 thẻ bằng chứng vật lý kèm Provenance chi tiết; ML Isolation Forest độc lập kiểm chứng trên 5 features có tải. |
| **SCREEN 05** | [`05_CASE_WORKSPACE_WHAT_DID_WE_DO.md`](./05_CASE_WORKSPACE_WHAT_DID_WE_DO.md) | Hàng rào ActionGuard 5 điều kiện, can thiệp mô phỏng an toàn, rẽ nhánh dữ liệu thực tế sau bảo trì ngày 08/06/2020. |
| **SCREEN 06** | [`06_CASE_WORKSPACE_DID_IT_WORK.md`](./06_CASE_WORKSPACE_DID_IT_WORK.md) | Kiểm chứng tiêu chí hồi phục (Recovery Criteria Verified 5/5 observations có tải), thủ tục đóng Case và giải phóng tài sản. |
| **SCREEN 07** | [`07_CASE_TIMELINE_HISTORY.md`](./07_CASE_TIMELINE_HISTORY.md) | Sổ cái `CaseEvent` biên niên sử từng giây theo chuẩn Datadog: Lưu vết tự động từ quan sát ban đầu, can thiệp, còi LPS cho tới đóng Case. |
