# CompressorGuard — Documentation Archive

Thư mục này chứa toàn bộ các tài liệu nghiên cứu tiền trạm, bản nháp đặc tả thế hệ 1 (v1), và nhật ký phiên làm việc trong quá trình xây dựng dự án **CompressorGuard**.

> [!IMPORTANT]
> **Single Source of Truth (SSOT):**  
> Toàn bộ tri thức, hợp đồng domain, số liệu vật lý thực tế từ MetroPT-3, và lộ trình tích hợp MongoDB / Datadog đã được hợp nhất hoàn chỉnh vào:  
> 👉 [`master_context.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/master_context.md) (tại root của repository).  
> 
> Mọi AI agent hoặc kỹ sư tiếp nối dự án **BẮT BUỘC** đọc `master_context.md` làm tài liệu chuẩn mực duy nhất.

---

## Cấu trúc lưu trữ

### 1. `research/` — Nghiên cứu & Chiến lược ban đầu
Chứa các bản nghiên cứu khả thi, phân tích tập dữ liệu MetroPT-3 và định hướng chiến lược cuộc thi:
- [`master-spec.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/docs/archive/research/master-spec.md): Bản phác thảo đặc tả kỹ thuật và nghiệp vụ v1.5 (trước khi đóng băng Vertical Slice v2.1).
- [`data-feasibility.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/docs/archive/research/data-feasibility.md): Báo cáo khả thi dữ liệu MetroPT-3 và kiểm chứng 33h 52m lead time.
- [`how-to-win.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/docs/archive/research/how-to-win.md): Ghi chú chiến lược trình bày, tư duy hackathon và so sánh tiếp cận.
- [`compressorguard_plan.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/docs/archive/research/compressorguard_plan.md): Kế hoạch dự án sơ khởi.

### 2. `specs-v1/` — Đặc tả phân mảnh thế hệ 1
Các tài liệu đặc tả từng phần riêng lẻ trước khi được tổng hợp vào Phần 3, 4, 5 của `master_context.md`:
- `architecture.md`, `detection.md`, `evidence-model.md`, `decision-matrix.md`
- `product.md`, `product-thesis-and-golden-experience.md`, `demo-scenario.md`, `validation.md`

### 3. `session-logs/` — Nhật ký phiên làm việc
Nhật ký thực thi, task plan, findings và progress log từ các phiên ổn định lõi suy luận backend (05–07/10/2026):
- `task_plan.md`, `findings.md`, `progress.md`, `report.md`

---
*Lưu trữ nhằm bảo toàn lịch sử phát triển Git mà không làm loãng context của AI và developer.*
