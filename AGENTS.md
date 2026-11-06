# AGENTS.md — CompressorGuard Agent Guidelines & Working Rules

> **Target Project:** CompressorGuard — Industrial Operations Command Platform (MUGVN Hackathon 2026: MongoDB + Datadog)  
> **Workspace:** `d:\Code\Projects\self-projects\iot-hackathon`

---

## ⚠️ CRITICAL INSTRUCTION: DO NOT RUN PYTEST (KHÔNG CHẠY PYTEST)

- **TUYỆT ĐỐI KHÔNG TỰ Ý CHẠY `pytest` TRONG MỌI PHIÊN LÀM VIỆC:**
  - Tập dữ liệu gốc `MetroPT3(AirCompressor).csv` có hơn 1.5 triệu dòng (~145MB). Việc chạy toàn bộ test suite `pytest` sẽ đọc lại dữ liệu, khởi tạo pipeline phân tích và tiêu tốn nhiều phút/CPU, gây treo hoặc timeout background task.
  - Toàn bộ backend domain logic, 4 detector, ActionGuard, MongoDB repository và Datadog APM tracing đã được kiểm chứng ổn định ở các vòng kiểm thử trước (bao gồm `test_production_backend_v3.py`).
  - **Quy tắc:** Chỉ chạy test khi có yêu cầu rõ ràng từ người dùng. Nếu cần kiểm tra một logic nhỏ hoặc syntax, hãy dùng static analysis, review code hoặc kiểm tra unit test đơn lẻ có mock nhẹ (ví dụ `pytest tests/test_single_unit.py -k name`), KHÔNG bao giờ chạy lệnh `pytest` trần trên toàn bộ dự án.

---

## 1. Project Invariants & Core Philosophy

1. **Zero Fake Telemetry:** 100% dữ liệu cảm biến lấy từ bộ dữ liệu thực `MetroPT-3` (Nature Scientific Data / UCI). Tuyệt đối không sinh dữ liệu ngẫu nhiên giả tạo (`Math.random()`).
2. **Decoupled Producer–Consumer Live Mechanism (ThreatLens-Style):**
   - *"The Dashboard Does Not Trigger Telemetry."*
   - Dashboard là đài quan sát thuần túy, không dùng `setInterval` gọi `POST /demo/tick` kéo dữ liệu.
   - Luồng dữ liệu được bơm bởi Background Stream Worker hoặc script phát độc lập, lưu trực tiếp vào MongoDB.
3. **Phân Định 3 Tầng Dữ Liệu Nghiêm Ngặt:**
   - **Layer A — Business Context (Asset Registry):** Phân cấp Hạm đội $\rightarrow$ Đoàn tàu $\rightarrow$ Phân hệ APU $\rightarrow$ Máy nén khí.
   - **Layer B — Observed Telemetry & Computed State:** Dữ liệu cảm biến trực tiếp, sigmas, chế độ `LOADED` / `UNLOADED`, điểm anomaly.
   - **Layer C — Validation Reference (Ground Truth):** Báo cáo bảo trì lịch sử (Failure #3 Air Leak) nằm riêng trong Drawer đối chứng, tuyệt đối không rò rỉ vào detector online.
4. **Dual-Clock Architecture:**
   - `event_time`: Giữ nguyên mốc thời gian lịch sử gốc (tháng 6/2020) cho mọi suy luận vật lý và tính toán lead time.
   - `simulation_time`: Điều tiết nhịp phát dòng theo tốc độ mô phỏng (1x..300x).
   - Nhãn minh bạch: `[ LIVE SIMULATION · HISTORICAL DATA ]`.
5. **Human-in-the-Loop Incident Governance:**
   - Không làm hệ thống tự động chạy hết (auto-pilot).
   - Operator là trung tâm chỉ huy qua 4 bước: **Acknowledge & Triage** $\rightarrow$ **Forensic Notes & Depot Work Order** $\rightarrow$ **ActionGuard Pre-Flight (5/5 PASS) & Safe Mode** $\rightarrow$ **5-Sample Loaded Recovery Table & Sign-Off**.
6. **Zero Hardcoded UI Data (100% Data-Driven):**
   - Tuyệt đối không viết cứng số liệu cảm biến hoặc trạng thái `✓ PASS` trong HTML/template. Mọi dữ liệu phải render động từ API (`/api/telemetry/window`, `/api/action/guard-status`, `/api/case`, `/api/recovery`).
7. **Tách Biệt UI Vận Hành và Demo Controls:**
   - Mọi nút bấm mô phỏng (`Play/Pause`, `Speed`, `Scenario Switcher`, `Bookmarks`) nằm trong **Replay Studio Drawer** (`Shift + S`), không đặt ở thanh Header vận hành chính.

---

## 2. Normative Specifications Reference

Mọi thay đổi về kiến trúc, backend API và giao diện UI/UX bắt buộc phải tham chiếu và tuân thủ các đặc tả sau:
- **Đặc tả UI/UX v3.0 Chuẩn:** [`docs/superpowers/specs/2026-10-11-prod-ready-ux-and-mechanism-design.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/docs/superpowers/specs/2026-10-11-prod-ready-ux-and-mechanism-design.md)
- **Đặc tả Sản phẩm Tổng thể (v3.0):** [`docs/PRODUCT_UX_SPEC.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/docs/PRODUCT_UX_SPEC.md)
- **Kiến trúc Hệ thống:** [`docs/ARCHITECTURE.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/docs/ARCHITECTURE.md)
- **Đặc tả 7 Màn hình:** [`screen/01_OPERATIONS_NAV_AND_ASSET_OVERVIEW.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/screen/01_OPERATIONS_NAV_AND_ASSET_OVERVIEW.md) đến [`screen/07_CASE_TIMELINE_HISTORY.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/screen/07_CASE_TIMELINE_HISTORY.md)
- **Master Roadmap:** [`task_plan.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/task_plan.md)

---

## 3. Current Project State & Focus

- **Backend Domain & Multi-Modal Storage (Phases 1-4):** Hoàn tất và đã kiểm chứng (`test_production_backend_v3.py`).
- **Giao diện Web Console (Phase 5):** Đang trong giai đoạn hiện thực hóa UI/UX v3.0 (Zero-hardcode, Chart.js multi-sensor strip charts, 3-pane workbench, Replay Studio Drawer, Human-in-the-Loop forms). Giao diện mẫu v2.3 cũ đã được gỡ bỏ để thay thế bằng bản v3.0 chuẩn.
