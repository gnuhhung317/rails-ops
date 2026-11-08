# 05. Theo dõi Vận hành Hệ thống với Datadog

> **Mục tiêu tài liệu:** Trả lời 3 câu hỏi thực tế cho người vận hành:  
> 1. Datadog đang theo dõi những thông số nào?  
> 2. Hệ thống cảnh báo tự động những vấn đề gì?  
> 3. Người vận hành nhìn thấy các thông tin đó ở đâu?

---

## 1. Datadog Đóng Vai trò Gì Trong Hệ thống?

Trong giải pháp CompressorGuard, toàn bộ việc phát hiện lỗi, đánh giá an toàn và quản lý ca sự cố được xử lý trực tiếp bởi mã nguồn ứng dụng Python. 

**Datadog đóng vai trò là đài theo dõi và quan sát tập trung**, giúp kỹ sư và người vận hành:
- Nắm bắt tức thời tình trạng máy nén qua biểu đồ thời gian thực.
- Nhận cảnh báo tự động qua các kênh thông báo khi có bất thường nghiêm trọng.
- Theo dõi thời gian thực thi của từng công đoạn để đảm bảo phần mềm hoạt động trơn tru.

---

## 2. Ba Câu hỏi Vận hành Cốt lõi

### Câu hỏi 1: Datadog Đang Theo dõi Những Thông số Nào?
Thông qua cơ chế phát số liệu DogStatsD (`src/observability/metrics.py`), hệ thống gửi về Datadog các nhóm chỉ số thực tế sau:
- **Số liệu cảm biến thời gian thực:** Áp suất van xả (`telemetry.dv_pressure_bar`), nhiệt độ dầu cacte máy nén (`telemetry.oil_temp_c`), dòng điện động cơ (`telemetry.motor_current_a`), áp suất mạch khí sau bộ sấy (`telemetry.tp3_bar`) và trạng thái rơ-le an toàn cơ học (`telemetry.lps_active`).
- **Chỉ số từ mô hình học máy:** Điểm bất thường đa biến (`ml.anomaly_score`) và mức độ đồng thuận giữa học máy và quy tắc vật lý (`ml.physics_agreement`).
- **Chỉ số hỗ trợ vận hành:** Số lượng xung áp suất thoáng qua đã bị lọc bỏ (`signals.suppressed_total`), thời gian cảnh báo trước tính toán được (`incident.lead_time_seconds`), và tiến độ nghiệm thu sau bảo trì (`recovery.consecutive_observations`).

### Câu hỏi 2: Hệ thống Giúp Phát hiện Tự động Những Vấn đề Gì?
Trong tệp cấu hình `datadog/monitors.json`, hệ thống thiết lập sẵn 3 bộ cảnh báo tự động:
1. **Cảnh báo rò rỉ khí van xả nghiêm trọng:** Kích hoạt khi độ sụt áp van xả vượt quá $2,0$ bar liên tục trong chu kỳ máy nén nạp tải. Đây là cảnh báo quan trọng nhất để kịp thời đưa tàu về xưởng trước khi hệ thống cạn khí.
2. **Cảnh báo sai lệch giữa học máy và vật lý:** Kích hoạt khi mô hình học máy và các cảm biến nhiệt động học vật lý đưa ra nhận định trái ngược nhau (mức đồng thuận $< 0,5$). Cảnh báo này giúp kỹ sư rà soát lại cảm biến hoặc cập nhật lại mô hình trước khi phát sinh sai số lớn.
3. **Thông báo nghiệm thu thành công sau sửa chữa:** Kích hoạt khi máy nén hoàn thành đủ 5 chu kỳ nạp tải liên tiếp đạt chuẩn áp suất và nhiệt độ sau khi đoàn tàu được bảo trì. Thông báo này báo cho điều độ viên biết tàu đã sẵn sàng đóng ca sự cố và đưa vào khai thác trở lại.

### Câu hỏi 3: Người Vận hành Nhìn thấy Thông tin Đó ở Đâu?
Trên bảng điều khiển tập trung cấu hình tại `datadog/dashboard.json`, người vận hành theo dõi 8 khung hiển thị trực quan:
1. Biểu đồ áp suất van xả (`DV_pressure`) so với đường chuẩn bình thường và ngưỡng rò rỉ 2,0 bar.
2. Biểu đồ nhiệt độ dầu máy nén so với ngưỡng quá nhiệt 74°C.
3. Biểu đồ áp suất mạch khí sau bộ sấy (`TP3`) và tiếp điểm rơ-le cơ học LPS.
4. Điểm số bất thường của mô hình học máy và mức độ đồng thuận với quy tắc vật lý.
5. Số lượng xung áp suất nhiễu đã được lọc bỏ để tránh làm phiền điều độ viên.
6. Tiến độ nghiệm thu sau bảo trì (đếm chuỗi từ 1 đến 5 chu kỳ nạp đạt chuẩn).
7. Mẫu đo thời gian chạy của các bước xử lý (APM Tracing).
8. Đồng hồ hiển thị thời gian can thiệp sớm (tính bằng giờ).

> **Ghi chú minh bạch về hiệu năng APM:**  
> Trong giao diện mẫu và API trạng thái, hệ thống có hiển thị mẫu phân bổ thời gian thực thi của các khâu xử lý (như đọc dữ liệu, chạy bộ phát hiện, kiểm tra an toàn) với mức tham chiếu xấp xỉ 11,2 mili-giây. Đây là số liệu minh họa qua API trạng thái trong môi trường thử nghiệm, giúp người dùng hình dung năng lực xử lý thời gian thực của ứng dụng.
