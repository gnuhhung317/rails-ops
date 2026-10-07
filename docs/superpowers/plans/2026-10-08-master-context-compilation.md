# Master Context Compilation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Trích xuất và tổng hợp toàn bộ tri thức dự án từ hội thoại đối sánh hackathon (`7d83d7ab-bacd-4905-bb22-054ce9d029ee`), dữ liệu vật lý MetroPT-3, Master Spec, Product/UX Spec, và mã nguồn Vertical Slice Backend v2.1 thành một tài liệu duy nhất `d:/Code/Projects/self-projects/iot-hackathon/master_context.md`, có khả năng cập nhật/append dần, giúp bất kỳ AI agent nào đọc xong cũng hiểu trọn vẹn 100% ngữ cảnh để tiếp tục triển khai.

**Architecture:** Thiết kế tài liệu theo cấu trúc phân tầng nhận thức (Cognitive Hierarchy) gồm 7 phần cốt lõi: (1) Executive Identity & Core Promise, (2) Strategic Hackathon Post-Mortem & Mental Model, (3) Physical Ground Truth & Telemetry Dossier, (4) Product Thesis & 90s Golden Experience Spec, (5) Backend Domain Architecture & Vertical Slice v2.1, (6) Master Spec Technology Blueprint (MongoDB & Datadog), (7) Phased Execution Roadmap & Rules of Engagement. Tài liệu được định dạng Markdown chuẩn, có neo liên kết dữ liệu thực tế và schema hợp đồng API bất biến.

**Tech Stack:** Markdown, Python 3.12 (để kiểm tra tính toàn vẹn và trích xuất số liệu chính xác), MetroPT-3 dataset, FastAPI, MongoDB Time Series, Datadog.

---

## User Review Required

> [!IMPORTANT]
> **Vị trí và định dạng tệp:** Tệp tổng hợp sẽ được đặt tại `d:/Code/Projects/self-projects/iot-hackathon/master_context.md`. Tệp được thiết kế ở dạng **Modular & Appendable Markdown** — các phần đã đóng băng (như Ground Truth vật lý, Backend Vertical Slice v2.1, Post-Mortem so sánh) được cố định rõ ràng, và có các placeholder có cấu trúc để append tiếp khi hoàn thành tích hợp MongoDB, Datadog và Frontend UI.

> [!NOTE]
> **Mục tiêu tương thích đa AI:** Tài liệu được viết bằng tiếng Việt và tiếng Anh kết hợp chuẩn mực kỹ thuật (giữ nguyên các thuật ngữ domain, schema JSON, metric vật lý, prompt/command) để cả Claude, GPT-4o, hay Gemini khi nạp vào context đều nắm bắt được đầy đủ mà không bị "semantic loss".

---

## Proposed Changes & File Mapping

```text
d:/Code/Projects/self-projects/iot-hackathon/
├── master_context.md                                   # [NEW] Single-source-of-truth Master Context cho toàn bộ dự án
└── docs/superpowers/plans/
    └── 2026-10-08-master-context-compilation.md        # [NEW] Bản kế hoạch writing-plans này
```

---

## Cấu Trúc Chi Tiết Của `master_context.md` Sẽ Được Xây Dựng

1. **Phần 1: Executive Summary & Project North Star**
   - Tên dự án: **CompressorGuard — Real-time Compressor Operations & Incident Response System**.
   - Cuộc thi: MUGVN Hackathon 2026 (MongoDB + Datadog).
   - Core Promise: **Detect earlier → Prove why → Act safely → Verify recovery.**
   - Persona: Fleet Operations Specialist (Lisbon Metro APU).
   - 3 Killer Claims: 33h 52m Lead Time; Bằng chứng nhiệt động lực học có cấu trúc > Anomaly Score; Closed-loop Physical Recovery Verification từ dữ liệu thật.
   - Strict Anti-Scope (những thứ cấm làm để tránh loãng).

2. **Phần 2: Hackathon Strategy & Comparative Post-Mortem (`hackathon/` vs `iot-hackathon/`)**
   - Đúc kết từ hội thoại: *Tại sao ThreatLens AI SOC Copilot gây ấn tượng mạnh?* (Surface-first, Narrative-driven, Ingest $\rightarrow$ Correlation $\rightarrow$ Investigation $\rightarrow$ Action).
   - Đúc kết từ `iot-hackathon/`: Sức nặng kỹ thuật cao nhưng ban đầu mắc bẫy "Engine is smart, trust me".
   - Định luật cốt lõi: **Feature $\neq$ Capability $\neq$ Product $\neq$ Demo $\neq$ Engineering**.
   - 5 Cổng đánh giá của Giám khảo: G1 Business (20s) $\rightarrow$ G2 Detection (Proof) $\rightarrow$ G3 Investigation (Why) $\rightarrow$ G4 Response (Action) $\rightarrow$ G5 Technology (Fit).
   - Chiến lược chiến thắng: Không làm dự án "nhiều công nghệ nhất", làm dự án kể được câu chuyện vận hành khép kín trong 90 giây.

3. **Phần 3: Physical Domain & Ground Truth Dataset (MetroPT-3)**
   - Hồ sơ tập dữ liệu UCI MetroPT-3 (1.5M rows @ 1Hz, 208MB CSV).
   - Thiết bị: Air Production Unit (APU) tàu điện ngầm Lisbon.
   - Danh mục cảm biến và ý nghĩa vật lý (`TP2`, `TP3`, `H1`, `DV_pressure`, `Oil_temp`, `Motor_current`, các van khí).
   - Các chế độ vận hành: `LOADED`, `UNLOADED`, `STANDBY`/`OFF`.
   - Mốc sự cố vàng 05-06/06/2020:
     - Onset vật lý: 05/06/2020 09:50:39 (`DV_pressure` nhảy vọt $+23.75\sigma$, `Oil_temp` trôi dạt $+5.71\sigma$).
     - Còi cơ học truyền thống: 06/06/2020 19:42:19 (`LPS = 1`).
     - Lead Time thực chứng: **33 giờ 52 phút** (2032 phút).
     - Phân đoạn hồi phục sau bảo trì: 08/06/2020 16:05:00+ (áp suất về $-0.016\text{ bar}$, nhiệt độ dầu $< 67^\circ\text{C}$).

4. **Phần 4: Product Thesis & 90-Second Golden Experience Spec**
   - Nguyên lý: *"Spec the experience, not the interface"*.
   - Tiến trình 5 câu hỏi nhận thức của Giám khảo trong 90 giây:
     - 00-15s: Who am I?
     - 15-35s: What happened & How early?
     - 35-55s: Why trust?
     - 55-75s: What can I do?
     - 75-90s: Did it work?
   - 4 Tầng phân cấp thông tin (Progressive Disclosure): Tier 1 (Peripheral Awareness), Tier 2 (Factual Decision Basis), Tier 3 (On-Demand Trust Verification), Tier 4 (Background Substance).
   - Storyboard chi tiết từng giây và layout wireframe của Incident Command Console.

5. **Phần 5: Backend Domain Architecture & Vertical Slice v2.1 (Đã hoàn thiện & kiểm chứng)**
   - 8 Invariants bất biến của hệ thống.
   - Tách biệt rõ ràng các tầng trách nhiệm:
     - Detectors (5 thuật toán vật lý + thống kê + Isolation Forest).
     - Evidence Fusion (`EvidenceState` đa tín hiệu).
     - Decision Engine (Ma trận quyết định tất định).
     - Domain Recovery Policy (`RecoveryCriteria` & `RecoveryVerifier` với quy tắc reset sau suýt thành công).
     - Lifecycle Orchestration (`IncidentLifecycleManager` điều phối replay cursor & máy trạng thái tường minh).
   - Hợp đồng REST API đóng băng:
     - Product Endpoints: `GET /api/incident`, `GET /api/evidence`, `POST /api/action/safe-mode`, `GET /api/recovery`.
     - Demo Controls: `POST /demo/reset`, `POST /demo/tick`, `POST /demo/jump`.
     - Error handling: HTTP 409 Conflict cho chuyển đổi trạng thái phi pháp; HTTP 400 Bad Request cho milestone sai.
   - Kết quả kiểm thử: 12/12 test cases passed, tính tất định 100% giữa 2 lần chạy.

6. **Phần 6: Master Spec Technology Blueprint (MongoDB & Datadog Integration)**
   - Yêu cầu bắt buộc MongoDB:
     - Time Series collection: `measurements` (timeField: `timestamp`, metaField: `metadata`).
     - Aggregation Pipeline: `$setWindowFields` tính rolling baseline, delta, sigma.
     - Document Collections: `incidents`, `evidence_records`, `assets`.
     - TTL & Lifecycle: `expireAfterSeconds`.
     - Biện minh "Why MongoDB?": Khả năng hợp nhất dữ liệu chuỗi thời gian vận hành và trạng thái sự cố có cấu trúc.
   - Yêu cầu bắt buộc Datadog:
     - Custom metrics qua DogStatsD: `compressorguard.dv_pressure`, `oil_temp`, `anomaly_score`.
     - APM & Tracing: `dd-trace` gắn vào FastAPI endpoints.
     - Log Management: JSON structured logs tương quan với Trace ID.
     - Dashboards & Monitors cho sự cố và độ trễ.
   - Vector Search (P1) & RCA Synthesis (P2).

7. **Phần 7: Strategic Roadmap & Hướng Dẫn Dành Cho AI Agent Tiếp Theo**
   - Trạng thái hiện tại: Vertical Slice Backend v2.1 đã hoàn thành 100%.
   - Nhiệm vụ kế tiếp theo thứ tự ưu tiên:
     1. Tích hợp MongoDB Time Series & Aggregation Pipeline ($setWindowFields).
     2. Tích hợp Datadog Observability (Metrics, Logs, Traces, Monitors).
     3. Xây dựng giao diện Frontend Incident Command Console (tuân thủ nghiêm ngặt PRODUCT_UX_SPEC.md).
     4. Demo Hardening & Pitch Deck rehearsal (kịch bản trình diễn 1 lệnh không lỗi).
   - Bộ quy tắc ứng xử (Rules of Engagement) cho AI tiếp theo: Không vi phạm 8 invariants; Không bịa telemetry; Không phá vỡ hợp đồng API đã đóng băng.

---

## Task-by-Task Implementation Plan

### Task 1: Khởi tạo khung tài liệu `master_context.md` và viết Phần 1 (Executive Summary) & Phần 2 (Hackathon Strategy & Comparative Post-Mortem)

Trích xuất toàn bộ phân tích chiều sâu từ hội thoại `7d83d7ab-bacd-4905-bb22-054ce9d029ee`, báo cáo 30KB (`step_102_full_report.md`), và các phản hồi chiến lược của User về so sánh 2 project.

**Files:**
- Create: `d:/Code/Projects/self-projects/iot-hackathon/master_context.md`

- [ ] **Step 1: Viết Phần 1 - Executive Identity, Core Promise, 3 Killer Claims, Anti-Scope**
- [ ] **Step 2: Viết Phần 2 - So sánh đối đầu ThreatLens vs CompressorGuard, Phân biệt Feature/Capability/Product/Demo/Engineering, 5 Cổng đánh giá Giám khảo**
- [ ] **Step 3: Kiểm tra tính mạch lạc và độ súc tích của Phần 1 & 2**

---

### Task 2: Soạn thảo Phần 3 - Physical Domain & Ground Truth Dataset (MetroPT-3)

Tổng hợp toàn bộ thông số kỹ thuật cảm biến, các chế độ vận hành (LOADED/UNLOADED), mốc sự cố vàng Onset (05/06 09:50:39), LPS cơ học (06/06 19:42:19), Lead Time 33h 52m, và phân đoạn hồi phục 08/06 16:05:00 từ `findings.md` và `data-feasibility.md`.

**Files:**
- Modify: `d:/Code/Projects/self-projects/iot-hackathon/master_context.md`

- [ ] **Step 1: Tổng hợp bảng đặc tả 15 sensor và phân loại van/áp suất/nhiệt độ/dòng điện**
- [ ] **Step 2: Đặc tả chi tiết cơ chế suy thoái vật lý (Discharge valve leak $\rightarrow$ áp suất tăng $\rightarrow$ nhiệt độ tăng $\rightarrow$ sập áp toàn hệ thống)**
- [ ] **Step 3: Ghi nhận chính xác số liệu đối chứng tại các mốc thời gian Golden Path**

---

### Task 3: Soạn thảo Phần 4 - Product Thesis & 90-Second Golden Experience Spec

Chuyển tải nguyên vẹn tinh thần "Spec the experience, not the interface", tiến trình nhận thức 5 câu hỏi của Giám khảo, 4 tầng thông tin (Tiers 1-4), và Layout Wireframe của Incident Command Console từ `docs/PRODUCT_UX_SPEC.md` và `docs/product-thesis-and-golden-experience.md`.

**Files:**
- Modify: `d:/Code/Projects/self-projects/iot-hackathon/master_context.md`

- [ ] **Step 1: Trình bày bảng Cognitive Progression 90 giây theo từng mốc thời gian**
- [ ] **Step 2: Chi tiết hóa 4 Tiers phân cấp thông tin và dữ liệu hiển thị tương ứng**
- [ ] **Step 3: Vẽ diagram ASCII Layout Console và luồng tương tác người dùng**

---

### Task 4: Soạn thảo Phần 5 - Backend Domain Architecture & Vertical Slice v2.1

Ghi nhận toàn bộ hiện trạng kỹ thuật đã kiểm chứng: 8 Invariants, kiến trúc các tầng (`detectors`, `fusion`, `decision`, `recovery`, `lifecycle`), hợp đồng REST API đóng băng kèm mẫu JSON payload thực tế và xử lý lỗi HTTP 409/400.

**Files:**
- Modify: `d:/Code/Projects/self-projects/iot-hackathon/master_context.md`

- [ ] **Step 1: Liệt kê chi tiết 8 Invariants bất biến đã được thẩm định trong codebase**
- [ ] **Step 2: Vẽ sơ đồ kiến trúc các tầng domain và luồng dữ liệu ReplayEngine $\rightarrow$ Detectors $\rightarrow$ Fusion $\rightarrow$ Decision $\rightarrow$ Lifecycle $\rightarrow$ RecoveryVerifier**
- [ ] **Step 3: Ghi đầy đủ API Contract cho 4 Product endpoints và 3 Demo endpoints kèm ví dụ JSON chính xác**

---

### Task 5: Soạn thảo Phần 6 - Master Spec Technology Blueprint (MongoDB & Datadog)

Trích xuất và cấu trúc hóa các yêu cầu bắt buộc của MUGVN Hackathon từ `master-spec.md`: Mô hình Time Series Collection, Aggregation Pipeline (`$setWindowFields`), TTL, chiến lược Datadog (Metrics, Logs, APM, Monitors), và luận điểm biện minh "Why MongoDB?".

**Files:**
- Modify: `d:/Code/Projects/self-projects/iot-hackathon/master_context.md`

- [ ] **Step 1: Đặc tả kiến trúc MongoDB Time Series, schema tài liệu, và pipeline `$setWindowFields`**
- [ ] **Step 2: Đặc tả kiến trúc Datadog (DogStatsD, APM tracing, Structured logging, Dashboard)**
- [ ] **Step 3: Đưa ra câu trả lời chuẩn mực cho câu hỏi bảo vệ: "Why MongoDB?", "Why AI?"**

---

### Task 6: Soạn thảo Phần 7 - Strategic Roadmap, Guidelines & Tự động kiểm tra tính toàn vẹn

Định hình lộ trình thực thi tiếp theo cho các AI agent khác, thiết lập các quy tắc bất khả xâm phạm (Rules of Engagement), và chạy script kiểm tra tính đầy đủ của tài liệu.

**Files:**
- Modify: `d:/Code/Projects/self-projects/iot-hackathon/master_context.md`
- Copy plan: `d:/Code/Projects/self-projects/iot-hackathon/docs/superpowers/plans/2026-10-08-master-context-compilation.md`

- [ ] **Step 1: Viết lộ trình các bước tiếp theo (MongoDB $\rightarrow$ Datadog $\rightarrow$ UI Console $\rightarrow$ Demo Polish)**
- [ ] **Step 2: Thiết lập bảng Hướng dẫn nhận thức & Rules of Engagement cho AI kế tiếp**
- [ ] **Step 3: Lưu bản kế hoạch writing-plans vào thư mục `docs/superpowers/plans/`**
- [ ] **Step 4: Chạy kiểm tra kích thước, số lượng từ và tính đầy đủ của các neo dữ liệu trong `master_context.md`**

---

## Verification Plan

### Automated Verification
```bash
python -c "
import os
path = r'd:\Code\Projects\self-projects\iot-hackathon\master_context.md'
assert os.path.exists(path), 'File master_context.md does not exist!'
size = os.path.getsize(path)
print(f'master_context.md exists, size: {size} bytes')
assert size > 25000, f'File size {size} is too small for a comprehensive master context!'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
for kw in ['33h 52m', 'MetroPT-3', 'ThreatLens', 'CompressorGuard', 'RecoveryCriteria', 'GET /api/incident', 'setWindowFields', 'Datadog']:
    assert kw in content, f'Missing keyword: {kw}'
print('All critical domain checkpoints verified successfully.')
"
```

### Manual Review
- Đảm bảo tài liệu đọc liền mạch, tổ chức markdown trực quan với headers, code blocks, JSON schemas, Mermaid diagram.
- Xác nhận rằng một AI độc lập khi đọc tệp này sẽ có đủ toàn bộ tri thức mà không cần đọc lại các file lẻ tẻ.
