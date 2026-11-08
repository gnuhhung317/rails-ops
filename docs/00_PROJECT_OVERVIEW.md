# 00. Tổng quan Dự án & Ranh giới Vận hành

> **Dự án:** CompressorGuard — Hệ thống Giám sát & Quản lý Vận hành Máy nén khí Đoàn tàu (MUGVN Hackathon 2026: MongoDB + Datadog)  
> **Đội thi:** Flex · **Liên hệ:** `duchung04st@gmail.com` · **Mã nguồn:** [https://github.com/gnuhhung317/rails-ops](https://github.com/gnuhhung317/rails-ops)

---

## 1. Bài toán Thực tế & Bối cảnh Vận hành

### 1.1. Tầm quan trọng của Máy nén khí Đoàn tàu Đô thị
Trong các đoàn tàu chạy điện (Metro/EMU), phân hệ khí nén phụ trợ (APU) giữ vai trò then chốt đối với sự an toàn của toàn bộ chuyến tàu:
- **Hệ thống phanh an toàn:** Giữ áp lực khí nén ổn định trong các bình chứa để nhả phanh khi chạy và hãm dừng đoàn tàu khi vào ga. Nếu mất áp suất khí, tàu sẽ tự động kích hoạt phanh khẩn cấp để chống trôi, khiến tàu dừng đột ngột giữa hầm ngầm hoặc trên cầu cạn.
- **Hệ thống đóng mở cửa toa xe:** Đòi hỏi nguồn khí nén liên tục và tin cậy để đóng mở cửa an toàn cho hàng ngàn lượt hành khách lên xuống tại mỗi ga.
- **Bầu treo khí nén giảm xóc:** Giúp toa xe luôn êm ái, cân bằng tải trọng khi tàu chở đông người hoặc vào các khúc cua gấp.

### 1.2. Hạn chế của Rơ-le Cơ học Truyền thống
Các đoàn tàu thương mại hiện nay chủ yếu dựa vào rơ-le áp suất thấp cơ học (LPS). Thiết bị này chỉ bật tín hiệu báo động khi áp suất trong hệ thống đã tụt xuống dưới ngưỡng nguy hiểm (dưới 7,0 bar).
- Khi rơ-le cơ học nhảy, sự cố đã phát triển thành hỏng hóc nghiêm trọng. Tàu buộc phải dừng khẩn cấp giữa tuyến và phong tỏa đường ray.
- Đơn vị vận hành phải cử phương tiện đến kéo tàu về xưởng sửa chữa, làm xáo trộn lịch chạy tàu toàn tuyến và phát sinh chi phí cứu hộ tốn kém.

---

## 2. Nguồn gốc Dữ liệu & Bối cảnh Minh họa

### 2.1. Dữ liệu Thực nghiệm MetroPT-3
Toàn bộ dữ liệu cảm biến trong dự án được lấy trực tiếp từ **MetroPT-3** — bộ dữ liệu thực nghiệm chuẩn công nghiệp công bố trên tạp chí khoa học *Nature Scientific Data* (2022) và lưu trữ tại kho dữ liệu UCI:
- **Quy mô dữ liệu:** Gồm 1.516.948 điểm đo cảm biến với tần suất 1 giây mỗi mẫu từ tháng 02 đến tháng 08 năm 2020.
- **Hiện tượng vật lý thực tế:** Ghi lại chân thực các diễn biến rò rỉ khí nén, sụt áp van xả và hiện tượng máy nén khí bị quá nhiệt ngoài thực địa.
- **100% dữ liệu cảm biến thật:** Toàn bộ tín hiệu cảm biến đưa vào hệ thống đều là số đo thực tế, tuyệt đối không dùng các hàm ngẫu nhiên để vẽ đồ thị giả tạo.

### 2.2. Bối cảnh Minh họa Tuyến Metro Số 1 TP.HCM
Để gắn liền giải pháp với bài toán thực tiễn của giao thông đô thị Việt Nam:
- Nhóm xây dựng kịch bản minh họa ứng dụng cho Tuyến Đường sắt Đô thị Bến Thành – Suối Tiên (Metro Tuyến 1, TP.HCM) với các thực thể giả định như đoàn tàu `TRAIN-302`, máy nén `APU-COMP-01`, và xưởng bảo dưỡng Depot Long Bình.
- **Ghi chú minh bạch:** Đây là kịch bản nghiên cứu kỹ thuật và diễn tập tình huống cho cuộc thi Hackathon, không phải hợp đồng dịch vụ đã triển khai chính thức trên các đoàn tàu thương mại đang vận hành chở khách của MAUR hay HURC1.

---

## 3. Ranh giới và Giới hạn của Hệ thống

| Lĩnh vực | Những việc CompressorGuard THỰC HIỆN | Những việc Hệ thống KHÔNG THỰC HIỆN |
| :--- | :--- | :--- |
| **Thu thập Dữ liệu** | Nhận dòng dữ liệu cảm biến đo đạc từng giây từ bộ phát mô phỏng hoặc qua các cổng API chuẩn. | Không đấu nối vật lý trực tiếp vào cáp tín hiệu trên đoàn tàu đang chở khách ngoài tuyến. |
| **Phân tích Bất thường** | Bắt sớm hiện tượng rò rỉ khí qua sụt áp van xả và mô hình học máy trước 33 giờ 52 phút. | Không thay thế các rơ-le ngắt an toàn phần cứng chuẩn đường sắt. |
| **Hỗ trợ Ra Quyết định** | Tự động kiểm tra 5 điều kiện an toàn, gợi ý quy trình bảo dưỡng và hỗ trợ lập lệnh sửa chữa. | Không tự ý can thiệp điều khiển đoàn tàu mà luôn cần con người (điều độ viên) phê duyệt. |
| **Nghiệm thu Phục hồi** | Đo đạc và xác minh 5 chu kỳ nạp tải liên tiếp đạt chuẩn áp suất và nhiệt độ sau khi sửa chữa. | Không thay thế biên bản bàn giao cơ khí có chữ ký thực tế của kỹ sư tại xưởng. |

---

## 4. Tình trạng Hiện thực hóa Các Tính năng

| Nhóm Tính năng | Trạng thái Thực tế | Chi tiết Triển khai trong Mã nguồn |
| :--- | :---: | :--- |
| **Lưu trữ dữ liệu cảm biến 1Hz** | `Đã hoàn thành` | Bảng chuỗi thời gian MongoDB (`measurements`) với cơ chế tự hủy sau 7 ngày. |
| **Cụm 4 bộ phát hiện sự cố** | `Đã hoàn thành` | Kết hợp quy tắc sụt áp van xả, trôi nhiệt độ dầu, học máy Isolation Forest và rơ-le cơ học LPS. |
| **Bộ hợp nhất chứng cứ** | `Đã hoàn thành` | Phối hợp độ tin cậy giữa mô hình vật lý (60%) và mô hình học máy (40%). |
| **Bộ kiểm tra an toàn vận hành** | `Đã hoàn thành` | Rà soát tự động 5 điều kiện an toàn bắt buộc trước khi cho phép chuyển chế độ xử lý. |
| **Thống kê vi phân cửa sổ trượt** | `Đã hoàn thành` | Sử dụng `$setWindowFields` 60 giây và `$facet` phân tích tỷ lệ chu kỳ nạp tải trên MongoDB. |
| **Đài quan sát Datadog** | `Đã hoàn thành` | 15 chỉ số vận hành DogStatsD, đo độ trễ APM (~11,2 mili-giây), 8 khung hiển thị và 3 bộ cảnh báo. |
| **Bàn điều độ trung tâm Web Console** | `Đã hoàn thành` | Giao diện web thuần tiếng Việt, hiển thị biểu đồ đa kênh và bàn làm việc 3 bước cho điều độ viên. |
| **Kết nối hệ thống xưởng bảo dưỡng** | `Đã thiết kế` | Cấu trúc dữ liệu lệnh công tác sẵn sàng kết nối API tới phần mềm quản lý bảo trì (ERP/CMMS). |
| **Đóng gói phần cứng trên tàu** | `Đề xuất tương lai` | Đóng gói giải pháp vào máy tính nhúng lắp đặt trực tiếp tại tủ điện buồng lái. |
| **Trợ lý AI tra cứu sổ tay kỹ thuật** | `Tạm hoãn` | Tra cứu cẩm nang bảo dưỡng PDF bằng AI, tạm hoãn để ưu tiên độ chuẩn xác của số liệu vật lý. |
| **Tự động kích hoạt phanh tàu** | `Ngoại phạm vi` | Việc hãm phanh trực tiếp thuộc thẩm quyền tuyệt đối của hệ thống an toàn chuyên trách trên đoàn tàu. |
