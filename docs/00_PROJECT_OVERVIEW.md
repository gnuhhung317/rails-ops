# 00. Tổng quan Dự án CompressorGuard

> **Dự án:** CompressorGuard — Hệ thống Giám sát & Quản lý Vận hành Máy nén khí Đoàn tàu (MUGVN Hackathon 2026: MongoDB + Datadog)  
> **Đội thi:** Flex · **Liên hệ:** `duchung04st@gmail.com` · **Mã nguồn:** [https://github.com/gnuhhung317/rails-ops](https://github.com/gnuhhung317/rails-ops)

---

## 1. CompressorGuard Là Gì?
CompressorGuard là ứng dụng hỗ trợ kỹ sư và điều độ viên đường sắt đô thị phát hiện sớm các hư hỏng trên máy nén khí phụ trợ (APU) của đoàn tàu. 

Hệ thống theo dõi liên tục dữ liệu đo đạc cảm biến từng giây, phát hiện sớm hiện tượng rò rỉ khí nén và quá nhiệt trước khi rơ-le an toàn cơ học bị ngắt, giúp đơn vị vận hành có đủ thời gian chủ động đưa đoàn tàu về xưởng sửa chữa mà không làm gián đoạn lịch chạy tàu.

---

## 2. Dữ liệu Đến Từ Đâu?
Toàn bộ dữ liệu cảm biến trong hệ thống được lấy trực tiếp từ **MetroPT-3** — bộ dữ liệu thực nghiệm chuẩn công nghiệp công bố trên tạp chí *Nature Scientific Data* (2022) và lưu trữ tại kho dữ liệu UCI:
- Gồm **1.516.948 điểm đo cảm biến** đo đạc thực tế ở tần suất 1 giây mỗi mẫu trên đoàn tàu Metro do Porto (Bồ Đào Nha) từ tháng 02 đến tháng 08 năm 2020.
- Ghi nhận chân thực các sự cố rò rỉ khí nén van xả và quá nhiệt máy nén ngoài thực địa.
- **100% dữ liệu cảm biến thật:** Toàn bộ tín hiệu cảm biến đưa vào hệ thống đều là số đo thực tế, tuyệt đối không dùng các hàm ngẫu nhiên để tạo đồ thị giả tạo.

---

## 3. Hệ thống Đã Làm Được Những Gì?
1. **Lưu trữ và phân tích chuỗi thời gian trên MongoDB:** Lưu trữ 1,5 triệu điểm đo cảm biến; thực hiện tính toán độ lệch chuẩn trong 60 giây (`$setWindowFields`) và phân loại chu kỳ chạy có tải/không tải (`$facet` + `$group`) trực tiếp trong cơ sở dữ liệu.
2. **Cụm 6 bộ phát hiện độc lập:** Kết hợp quy tắc vật lý (sụt áp van xả `DV_pressure > 2.0 bar`), ứng suất nhiệt dầu máy nén, tính bền bỉ qua 3 chu kỳ nạp, mô hình học máy Isolation Forest và rơ-le cơ học LPS.
3. **Cảnh báo sớm sự cố số 3 trước 33 giờ 52 phút:** Phát hiện rò rỉ khí từ lúc 09:50:39 ngày 05/06/2020, tạo ra cửa sổ can thiệp an toàn gần 34 tiếng đồng hồ trước khi rơ-le cơ học LPS bị sụt áp lúc 19:42:19 ngày 06/06/2020.
4. **Hỗ trợ điều độ viên xử lý sự cố:** Tự động rà soát 5 điều kiện kỹ thuật an toàn (ActionGuard) trước khi cho phép điều độ viên đưa tàu về chế độ an toàn, và tự động nghiệm thu 5 chu kỳ nạp tải liên tiếp đạt chuẩn sau khi sửa chữa.
5. **Theo dõi vận hành qua Datadog:** Thu thập các chỉ số cảm biến qua DogStatsD, thiết lập 3 bộ cảnh báo tự động và 8 khung hiển thị trực quan trên bảng điều khiển trung tâm.
6. **Đạt 5/5 cổng kiểm định tự động (Evaluation Gates 5/5 PASS):** Được kiểm chứng độc lập trên toàn bộ 1,5 triệu dòng dữ liệu MetroPT-3 mà không phát sinh báo động giả trong điều kiện bình thường.

---

## 4. Những Gì Hệ Thống Chưa Làm Được (Ranh giới Thử nghiệm)?
- **Chưa kết nối phần cứng trên tàu thật:** Hệ thống vận hành bằng cách phát lại dữ liệu cảm biến lịch sử qua phần mềm mô phỏng; chưa đấu nối cáp vật lý trực tiếp lên các đoàn tàu thương mại đang chở khách.
- **Bối cảnh Metro Tuyến 1 TP.HCM là giả định nghiệp vụ:** Các thông tin như đoàn tàu `TRAIN-302`, điều độ viên, Depot Long Bình và lịch trình chạy tàu Bến Thành – Suối Tiên là kịch bản giả định phục vụ cuộc thi Hackathon, không phải hợp đồng ký kết triển khai thực tế của MAUR hay HURC1.
- **Không thay thế hệ thống phanh an toàn tự động (SIL-4):** Hệ thống chỉ đóng vai trò cảnh báo sớm và hỗ trợ ra quyết định bảo dưỡng; việc điều khiển đoàn tàu và kích hoạt phanh khẩn cấp thuộc thẩm quyền tuyệt đối của hệ thống điều khiển tàu chuyên dụng.
