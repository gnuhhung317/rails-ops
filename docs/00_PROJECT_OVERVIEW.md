# 00. Tổng quan Dự án & Bối cảnh Kỹ thuật (Project Overview & Boundaries)

> **Dự án:** CompressorGuard — Industrial Operations Command Platform (MUGVN Hackathon 2026: MongoDB + Datadog)  
> **Đội thi:** Flex · **Liên hệ:** `duchung04st@gmail.com` · **Repository:** [https://github.com/gnuhhung317/rails-ops](https://github.com/gnuhhung317/rails-ops)

---

## 1. Bài toán Thực tế & Bối cảnh Vận hành

### 1.1. Tầm quan trọng của Hệ thống Khí nén (APU Compressor) trong Đường sắt Đô thị
Trong hệ thống đầu máy toa xe đường sắt đô thị (Metro / EMU), **Phân hệ Cung cấp Khí nén Phụ trợ (Auxiliary Pneumatic Unit - APU)** đóng vai trò sống còn đối với an toàn chạy tàu:
- **Hệ thống phanh chính:** Duy trì áp suất dự trữ trong các bình chứa khí (Main Reservoirs) để nhả phanh và thực hiện hãm dừng đoàn tàu. Mất áp suất khí nén dẫn đến kích hoạt phanh khẩn cấp tự động (fail-safe emergency brake), gây dừng tàu đột ngột giữa hầm hoặc trên cầu cạn.
- **Cơ cấu đóng mở cửa toa xe (Pneumatic Door System):** Cần áp lực khí ổn định để phục vụ hàng ngàn lượt hành khách mỗi ga.
- **Hệ thống treo khí nén (Air Suspension Bellows):** Cân bằng tải trọng động giữa các toa xe khi tàu vào cua hoặc tăng tốc.

### 1.2. Hạn chế của Giám sát Cơ học Truyền thống
Hiện tại, hầu hết các đoàn tàu thương mại dựa vào **Rơ-le Áp suất Thấp cơ học (Low Pressure Switch - LPS)**. Thiết bị này chỉ kích hoạt khi áp suất trong hệ thống tụt xuống dưới ngưỡng nguy hiểm (thường dưới 7.0 bar). 
- Khi rơ-le LPS nhảy, sự cố đã phát triển thành lỗi nghiêm trọng (catastrophic failure), buộc đoàn tàu phải dừng khẩn cấp và phong tỏa tuyến đường ray.
- Doanh nghiệp vận hành phải chịu chi phí kéo tàu cứu hộ đắt đỏ, vi phạm SLA chạy tàu với cơ quan quản lý giao thông và gây gián đoạn giao thông đô thị diện rộng.

---

## 2. Nguồn gốc Dữ liệu & Bối cảnh Minh họa

### 2.1. Bộ Dữ liệu Thực nghiệm MetroPT-3 (Nature Scientific Data / UCI)
Toàn bộ dữ liệu cảm biến trong dự án CompressorGuard được lấy trực tiếp từ **MetroPT-3 Dataset** — bộ dữ liệu thực nghiệm chuẩn công nghiệp công bố trên tạp chí *Nature Scientific Data* (2022) và lưu trữ tại UCI Machine Learning Repository:
- **Quy mô:** $1.516.948$ bản ghi cảm biến đo ở tần số 1Hz từ tháng 02/2020 đến tháng 08/2020.
- **Hiện tượng vật lý:** Ghi nhận thực tế các sự cố rò rỉ khí nén, suy giảm hiệu suất van xả nước ngưng (drain valve) và hỏng hóc nhiệt động học của máy nén khí đoàn tàu.
- **Triết lý Zero Fake Telemetry:** 100% dữ liệu cảm biến truyền qua hệ thống trong các kịch bản demo và phân tích đều là dữ liệu đo đạc thực tế, tuyệt đối không sử dụng các hàm sinh ngẫu nhiên (`Math.random()`) để tạo biểu đồ giả tạo.

### 2.2. Bối cảnh Minh họa Tuyến Metro Số 1 TP.HCM (Illustrative Domain Mapping)
Để thể hiện trọn vẹn giá trị ứng dụng thực tế trong bối cảnh hạ tầng giao thông Việt Nam:
- Dự án xây dựng một **kịch bản ánh xạ nghiệp vụ minh họa (Illustrative Case Study)** cho Tuyến Đường sắt Đô thị Bến Thành – Suối Tiên (Metro Tuyến 1, TP.HCM) với các thực thể minh họa như Đoàn tàu `TRAIN-302`, Máy nén `APU-COMP-01`, và Depot bảo trì Long Bình.
- **Lưu ý minh bạch:** Đây là mô hình nghiên cứu giải pháp và diễn tập tình huống kỹ thuật cho cuộc thi Hackathon, **không phải** là hợp đồng dịch vụ công nghệ thông tin đã ký kết hoặc triển khai chính thức trên hệ thống phần cứng đang chạy khách của Ban Quản lý Đường sắt Đô thị (MAUR) hay Công ty TNHH MTV Đường sắt Đô thị số 1 (HURC1).

---

## 3. Ranh giới Hệ thống (Scope Boundaries)

| Hạng mục | CompressorGuard THỰC HIỆN | HỆ THỐNG KHÔNG THỰC HIỆN |
| :--- | :--- | :--- |
| **Thu thập Dữ liệu** | Nhận dòng dữ liệu cảm biến chuỗi thời gian tần số 1Hz qua bộ phát lại (Replay Engine) hoặc API stream. | Không đấu nối trực tiếp vào cáp vật lý RS-485/CAN bus trên đoàn tàu đang chở khách. |
| **Phân tích Bất thường** | Phát hiện sớm hiện tượng rò rỉ khí qua sụt áp van `DV_pressure` và mô hình Unsupervised Isolation Forest trước 33h 52m. | Không thay thế các rơ-le ngắt an toàn phần cứng (hardware interlock) chuẩn SIL-4. |
| **Hỗ trợ Ra quyết định** | Cung cấp bảng kiểm tra an toàn ActionGuard (5 pre-flight checks), gợi ý SOP sửa chữa và hỗ trợ điều độ viên lập Work Order. | Không tự động can thiệp điều khiển đoàn tàu (auto-pilot) hoặc tự động thay đổi lịch chạy tàu mà không có con người duyệt. |
| **Nghiệm thu Phục hồi** | Đo đạc 5 chu kỳ nạp liên tiếp (`LOADED`) đạt áp suất và nhiệt độ chuẩn từ dữ liệu lịch sử sau mốc bảo trì. | Không thay thế biên bản nghiệm thu cơ khí vật lý có chữ ký của kỹ sư tại Depot. |

---

## 4. Ma trận Trạng thái Tính năng (Feature Implementation Matrix)

| Module / Tính năng | Trạng thái Hiện tại | Bằng chứng Triển khai / Ghi chú |
| :--- | :--- | :--- |
| **Time Series Stream Ingest** | `Implemented` | Lưu trữ `measurements` trên MongoDB Time Series Collection với TTL 7 ngày trên `ingested_at`. |
| **Multi-Detector Suite** | `Implemented` | 4 detector: Rule-based `DV_pressure`, Drift `Oil_temp`, Isolation Forest, Mechanical `LPS`. |
| **Evidence Fusion Engine** | `Implemented` | Ma trận tính điểm hợp nhất độ tin cậy giữa vật lý ($60\%$) và mô hình ML ($40\%$). |
| **ActionGuard Safety Interlock** | `Implemented` | Bộ 5 kiểm tra an toàn nghiêm ngặt trước khi cấp phép chuyển sang Safe Mode. |
| **MongoDB Rolling Analytics** | `Implemented` | Aggregation Pipeline `$setWindowFields` 60s và `$facet` phân tích duty cycle. |
| **Datadog Observability** | `Implemented` | 15 DogStatsD custom metrics, APM distributed tracer span (<15ms sample latency), 8 widgets dashboard, 3 monitors. |
| **Operator Web Console v3.0** | `Implemented` | Giao diện Single-Page tiếng Việt chuẩn công nghiệp, multi-sensor strip charts, 3-pane workbench. |
| **Depot ERP Integration** | `Designed` | Cấu trúc schema `WorkOrderRequest` sẵn sàng kết nối webhook tới hệ thống SAP/Maximo. |
| **Edge Hardware Packaging** | `Proposed` | Triển khai container hóa trên phần cứng nhúng đặt trực tiếp tại buồng điều khiển toa xe (APU Cabinet). |
| **LLM Maintenance RAG Assistant**| `Deferred` | Truy vấn cẩm nang bảo trì PDF bằng vector search, hoãn lại để tập trung vào an toàn dữ liệu số học. |
| **Autonomous Train Braking** | `Out of Scope` | Tự động kích hoạt phanh cơ khí thuộc thẩm quyền độc quyền của hệ thống bảo vệ tàu tự động ATP/ATO (SIL-4). |
