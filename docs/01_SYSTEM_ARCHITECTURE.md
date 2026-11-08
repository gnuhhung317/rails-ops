# 01. Kiến trúc Hệ thống & Luồng Dữ liệu Thực tế

> **Dự án:** CompressorGuard — Hệ thống Giám sát & Quản lý Vận hành Máy nén khí Đoàn tàu (MUGVN Hackathon 2026: MongoDB + Datadog)  
> **Nguyên tắc:** Trình bày đúng thực tế mã nguồn, mạch lạc, tự nhiên, hạn chế thuật ngữ tiếng Anh không cần thiết.

---

## 1. Kiến trúc Tổng thể của Hệ thống

CompressorGuard được xây dựng theo mô hình **nguyên khối phân tầng gọn nhẹ** bằng Python và FastAPI, giúp toàn bộ hệ thống dễ vận hành, dễ triển khai và có ranh giới rõ ràng giữa xử lý vật lý, phát hiện bất thường, lưu trữ và giao diện điều độ:

```mermaid
flowchart TD
    subgraph Data_Source ["1. Nguồn Dữ liệu Thực tế"]
        CSV["Tập dữ liệu MetroPT-3 (1,5 triệu dòng đo đạc thực địa)"]
    end

    subgraph Replay_Layer ["2. Bộ Phát lại & Điều tiết Mô phỏng"]
        RE["Bộ phát dòng dữ liệu\n- Giữ nguyên mốc giờ đo đạc gốc\n- Điều tiết nhịp phát theo tốc độ chọn"]
    end

    subgraph Core_Engine ["3. Động cơ Phân tích & Quản lý Sự cố"]
        ILM["Bộ quản lý vòng đời sự cố"]
        RC["Bộ phân loại chế độ chạy (Có tải / Không tải / Nghỉ)"]
        
        subgraph Detectors ["Cụm 4 Bộ Phát hiện Độc lập"]
            D1["Quy tắc vật lý (Sụt áp van xả DV_pressure > 2.0 bar)"]
            D2["Trôi nhiệt độ dầu máy nén (Vượt 3 độ lệch chuẩn)"]
            D3["Mô hình học máy Isolation Forest (Bất thường đa biến)"]
            D4["Rơ-le áp suất thấp cơ học LPS (Phát hiện sụt áp khẩn cấp)"]
        end

        EF["Bộ hợp nhất chứng cứ (Vật lý 60% + Học máy 40%)"]
        DE["Động cơ ra quyết định (15 quy tắc vận hành)"]
        AG["Bộ kiểm tra an toàn (5 điều kiện bắt buộc)"]
        SM["Vòng đời xử lý sự cố (6 trạng thái)"]
    end

    subgraph Storage_Observability ["4. Lưu trữ Dữ liệu & Đài Quan sát"]
        REPO["Tầng truy xuất dữ liệu"]
        MDB[("Cơ sở dữ liệu MongoDB\n- Bảng chuỗi thời gian cảm biến\n- Các bảng quản lý sự cố và sổ kiểm toán")]
        MEM[("Bộ nhớ đệm tạm thời\n(Phục vụ chạy thử nhanh không cần cài database)")]
        
        DD["Đài quan sát Datadog\n(Chỉ số DogStatsD + Đo độ trễ từng bước APM)"]
    end

    subgraph Interface_Layer ["5. Giao diện Điều độ Trung tâm"]
        API["Máy chủ FastAPI\n- Nhóm cổng nghiệp vụ vận hành /api\n- Nhóm cổng điều khiển mô phỏng /demo"]
        UI["Bàn điều độ Web Console\n- Đài quan sát trực tiếp thời gian thực\n- Bảng điều khiển mô phỏng nâng cao (Shift+S)\n- Tháp quan sát vận hành Datadog (Shift+D)"]
    end

    CSV --> RE
    RE --> ILM
    ILM --> RC
    RC --> Detectors
    Detectors --> EF
    EF --> DE
    DE --> AG
    AG --> SM
    
    SM --> REPO
    REPO --> MDB
    REPO -.->|Dự phòng khi chưa cấu hình MONGODB_URI| MEM
    
    ILM --> DD
    SM --> API
    REPO --> API
    API --> UI
    UI -.->|Điều khiển mô phỏng qua các cổng /demo| RE
```

---

## 2. Luồng Dữ liệu Thực tế Khi Vận hành

Khi hệ thống hoạt động, dữ liệu chuyển động nhịp nhàng qua 6 bước khép kín:

```mermaid
sequenceDiagram
    autonumber
    participant CSV as Tập dữ liệu MetroPT-3
    participant Engine as Bộ phát & Quản lý vòng đời
    participant Detectors as Cụm phát hiện & Hợp nhất
    participant Decision as Ra quyết định & Kiểm tra an toàn
    participant Mongo as Cơ sở dữ liệu MongoDB
    participant Datadog as Đài quan sát Datadog
    participant UI as Bàn điều độ Web Console

    CSV->>Engine: Đọc điểm đo cảm biến theo từng giây
    Engine->>Detectors: Chuyển các thông số (DV_pressure, Oil_temp, TP2, TP3, H1, dòng điện)
    Detectors->>Decision: Tổng hợp điểm bất thường từ vật lý và học máy
    Decision->>Engine: Cập nhật ca sự cố khi phát hiện bất thường rõ rệt
    Engine->>Mongo: Lưu điểm đo vào bảng chuỗi thời gian & ghi nhật ký kiểm toán
    Engine->>Datadog: Gửi các chỉ số vận hành và đo thời gian xử lý từng khâu
    UI->>Engine: Lấy 100 điểm đo mới nhất để vẽ biểu đồ đa kênh liên tục
    Engine-->>UI: Cung cấp số liệu thời gian thực và cảnh báo cho điều độ viên
```

> **Về công cụ đẩy dữ liệu MQTT:**  
> Dữ liệu được đưa vào hệ thống trực tiếp qua bộ phát dòng mô phỏng hoặc các cổng API. Tệp mã `publish_mqtt.py` trong thư mục `scripts/` chỉ là công cụ bổ trợ độc lập khi người dùng muốn thử nghiệm phát dữ liệu ra một máy chủ MQTT bên ngoài.

---

## 3. Danh mục Các Cổng Giao tiếp API

Toàn bộ các cổng giao tiếp dưới đây đều được xây dựng thực tế trong mã nguồn:

### 3.1. Nhóm Cổng Nghiệp vụ Vận hành (`/api/*`)

| Phương thức | Cổng API | Chức năng Vận hành | Kết quả Trả về |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/operations` | Lấy bức tranh tổng thể toàn tuyến, tình trạng 3 đoàn tàu và cảnh báo ưu tiên | `200 OK` |
| `GET` | `/api/components` | Danh sách 4 cụm thiết bị của máy nén khí và tuổi thọ linh kiện | `200 OK` |
| `GET` | `/api/sop` | Danh mục cẩm nang quy trình xử lý chuẩn khi có sự cố | `200 OK` |
| `GET` | `/api/shift/current` | Thông tin về ca trực hiện tại của điều độ viên | `200 OK` |
| `POST` | `/api/shift/handover` | Lưu biên bản bàn giao ca trực vào hệ thống | `200 OK` |
| `GET` | `/api/incident` hoặc `/api/case` | Chi tiết ca sự cố nghiêm trọng đang xử lý (thời gian báo trước, mức độ lệch) | `200 OK` |
| `GET` | `/api/evidence` | Bằng chứng chẩn đoán tổng hợp từ cả 4 bộ phát hiện | `200 OK` |
| `GET` | `/api/case/events` hoặc `/api/timeline` | Sổ cái kiểm toán lưu vết toàn bộ thao tác xử lý của con người | `200 OK` |
| `GET` | `/api/action/guard-status` | Báo cáo kiểm tra 5 điều kiện an toàn trước khi xử lý | `200 OK` |
| `POST` | `/api/action/safe-mode` | Phê duyệt đưa đoàn tàu về chế độ an toàn để bảo dưỡng | `200 OK` hoặc `409` |
| `POST` | `/api/case/acknowledge` | Điều độ viên tiếp nhận ca sự cố và gán mức ưu tiên | `200 OK` hoặc `409` |
| `POST` | `/api/case/notes` | Bổ sung ghi chú chẩn đoán kỹ thuật vào hồ sơ sự cố | `200 OK` |
| `POST` | `/api/case/work-order` | Lập lệnh công tác bảo trì gửi về xưởng Long Bình | `200 OK` hoặc `409` |
| `POST` | `/api/case/false-positive` | Đánh dấu sự cố là báo động giả (kèm lý do kỹ thuật và chữ ký) | `200 OK` hoặc `409` |
| `POST` | `/api/case/close` | Đóng ca sự cố sau khi đã nghiệm thu máy nén phục hồi ổn định | `200 OK` hoặc `409` |
| `GET` | `/api/recovery` | Bảng nghiệm thu tự động 5 chu kỳ nạp tải liên tiếp sau sửa chữa | `200 OK` |
| `GET` | `/api/telemetry/window` | Cửa sổ trượt 100 điểm đo mới nhất phục vụ vẽ biểu đồ nhiều kênh | `200 OK` |
| `GET` | `/api/telemetry/analytics` | Thống kê độ lệch chuẩn 60 giây và tỷ lệ chu kỳ nạp tải từ MongoDB | `200 OK` |
| `GET` | `/api/scenarios` | Danh mục các tình huống mô phỏng có sẵn | `200 OK` |
| `POST` | `/api/operations/scenario` | Đổi kịch bản vận hành trực tiếp trên màn hình | `200 OK` |
| `GET` | `/api/validation-reference` | Trích xuất báo cáo kỹ thuật đối chứng lịch sử của đợt sự cố thật | `200 OK` |
| `GET` | `/api/observability/datadog-status`| Trạng thái kết nối với Datadog và kết quả đo thời gian xử lý | `200 OK` |

### 3.2. Nhóm Cổng Điều khiển Mô phỏng (`/demo/*`)

| Phương thức | Cổng API | Chức năng Điều khiển |
| :--- | :--- | :--- |
| `POST` | `/demo/tick` | Chuyển tiếp một điểm đo cảm biến tiếp theo (chế độ từng bước) |
| `POST` | `/demo/play` | Bắt đầu phát dòng dữ liệu tự động |
| `POST` | `/demo/pause` | Tạm dừng phát dữ liệu |
| `POST` | `/demo/speed` | Cài đặt tốc độ mô phỏng (từ 1 lần đến 300 lần thời gian thực) |
| `POST` | `/demo/jump` | Nhảy mốc thời gian mô phỏng đến đúng thời điểm mong muốn |
| `GET` | `/demo/status` | Xem trạng thái phát dữ liệu và mốc thời gian hiện tại |
