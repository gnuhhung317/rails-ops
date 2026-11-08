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
8. **Ngôn Ngữ Giao Diện: Tiếng Việt Chuẩn (Bắt Buộc):**
   - **Mọi chuỗi hiển thị cho người dùng phải là tiếng Việt chuẩn, có dấu đầy đủ, câu cú tự nhiên, văn phong của một sản phẩm công nghiệp Việt Nam** — bao gồm: nhãn tab/panel/card, tiêu chí cột trong bảng, tên nút, label & placeholder của form, hint, trạng thái (`empty state`), toast, banner cảnh báo, nhãn tooltip, nhãn trục/legend biểu đồ, và mọi dòng mô phỏng (`simulation`) trên header.
   - **Cấm** để sót nhãn tiếng Anh chưa dịch, cấm câu dịch máy vô nghĩa, cấm lẫn lộn hai ngôn ngữ trong cùng một nhãn (trừ trường hợp quy định dưới đây).
   - **Được giữ nguyên (không dịch) vì đó là định danh kỹ thuật, không phải văn bản giao diện:** tên mã (`APU-COMP-01`, `DISPATCHER-0941`, `Failure #3 Air Leak`), acronym ngành (`APU`, `TCMS`, `HMI`, `SLA`, `APM`), tên tín hiệu vật lý gốc của MetroPT-3 (`DV_pressure`, `Oil_temp`), trạng thái máy sinh ra từ backend (`LOADED`/`UNLOADED`, mã HTTP `409`, `PASS`/`FAIL` trong bảng kiểm chứng), tên API/endpoint, và nhãn minh bạch bắt buộc `[ LIVE SIMULATION · HISTORICAL DATA ]`.
   - **Thuật ngữ nhất quán một-một** toàn ứng dụng, không mỗi nơi một kiểu: `lead time` → **Thời gian báo trước**, `lead window` → **Cửa sổ can thiệp**, `anomaly` → **bất thường**, `fleet` → **hạm đội**, `consist` → **đoàn tàu**, `depot` → **xưởng depot / depot bảo trì**, `work order` → **lệnh công tác**, `air leak` → **rò khí**, `recovery` → **nghiệm thu phục hồi**, `guard` → **trực bảo vệ hành động (ActionGuard)**.
   - Khi thêm màn hình/bảng/form mới: **không được tạo bản tiếng Anh "tạm thời"** — chuỗi tiếng Việt phải đi kèm ngay trong lần commit đó.
   - **Bản địa hóa KHÔNG phải dịch nguyên văn.** Tiếng Việt dài hơn tiếng Anh; dịch word-by-word làm màn hình đặc hơn, đi ngược invariant #9. Chuỗi tiếng Việt bắt buộc **ngắn hơn hoặc bằng** bản gốc tiếng Anh về số chữ.
   - Quy tắc này áp dụng cho `src/static/index.html`, `src/static/app.js` và mọi template/API string đổ ra UI; **không** đổi tên biến, hàm, key JSON hay field MongoDB.
9. **Ngân Sách Chữ & Chống Quá Tải Nhận Thức (Anti Feature-Smog):**
   - *Text thừa là quá tải nhận thức, không phải thông tin thêm.* Một màn hình chỉ được nói một điều; muốn nói nhiều điều thì phân cấp, không liệt kê.
   - **Ngân sách chữ bắt buộc** cho mọi chuỗi giao diện:
     - Tiêu đề panel / nhãn KPI / tiêu chí cột / chữ nút / tab: **tối đa 3 từ**.
     - Microcopy (`kpi-note`, `empty-note`, `panel-meta`, hint): **tối đa 4 từ**, văn phong điện tín, **không viết câu đầy đủ, không dấu chấm cuối**.
     - Toast / thông báo lỗi: **một mệnh đề, tối đa 10 từ** — nói cái gì vừa xảy ra và operator nên làm gì; cấm đoạn văn.
     - `placeholder`: tối đa 5 từ. `title`/`aria-label`: tối đa 8 từ.
   - **Một sự kiện chỉ xuất hiện MỘT nơi duy nhất trên màn hình.** Cấm lặp chỉ số giữa các panel. Các vi phạm đã ghi nhận cần xóa khi chạm vào file: **Cửa sổ can thiệp** hiện 3 lần (KPI strip, cột `Lead Window`, `wb-lead`), chart `DV_pressure`/`Oil_temp` nhân đôi giữa Fleet và Workbench, ledger xuất hiện 3 nơi (Workbench `ledger-mini`, Queue archive, Timeline).
   - **Mặc định thu gọn, không mặc định bung hết:** Workbench mở **đúng STEP hiện hành**, không mở cả 5 block; drawer (Replay Studio, Validation Reference) mặc định đóng; chỉ số phụ nằm sau toggle, không nằm sẵn trên màn hình.
   - Khi muốn thêm một widget: phải chỉ ra widget nào bị bớt đi để đổi chỗ, hoặc chứng minh nó ở một tầng chú ý khác. "Thêm cho đầy" là lý do không được chấp nhận.
   - Áp dụng cho cả nội dung do backend sinh ra: chuỗi trạng thái/thông điệp API đổ vào UI cũng phải tuân ngân sách chữ.

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
