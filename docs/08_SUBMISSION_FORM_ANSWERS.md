# 08. Ngân hàng Câu trả lời Google Form Nộp bài (Submission Form Answers)

> **Dành cho Đội thi Flex:** Sao chép và dán trực tiếp vào biểu mẫu nộp bài chính thức của MUGVN Hackathon 2026.  
> **Nguyên tắc biên soạn:** Tiếng Việt tự nhiên, chuẩn văn phong kỹ thuật công nghiệp Việt Nam, khiêm tốn, trung thực tuyệt đối với dữ liệu thực tế và tập trung vào 3 điều người chấm thi cần biết.

---

### Mục 1: Tên Đội thi
```text
Flex
```

### Mục 2: Email Người đại diện
```text
duchung04st@gmail.com
```

### Mục 3: Tên Đề tài / Giải pháp
```text
CompressorGuard — Giám sát Vận hành & Cảnh báo Sớm Sự cố Máy nén khí Đoàn tàu Đô thị (Metro APU)
```

### Mục 4: Link GitHub Repository
```text
https://github.com/gnuhhung317/rails-ops
```

### Mục 5: Link Video Demo (YouTube / Google Drive)
```text
[DÁN LINK VIDEO DEMO CỦA BẠN TẠI ĐÂY - Video quay màn hình 2:30 - 3:00 phút theo kịch bản docs/DEMO_VIDEO_SCRIPT.md]
```

### Mục 6: Tóm tắt Bài toán & Đối tượng Phục vụ (Dưới 200 từ)
```text
Trên các đoàn tàu đô thị (Metro/EMU), máy nén khí phụ trợ (APU) giữ vai trò sống còn để tạo khí nén cho hệ thống phanh an toàn và cơ cấu đóng mở cửa toa xe. Nếu mất áp suất khí, tàu sẽ bị kích hoạt phanh khẩn cấp và phải dừng đột ngột giữa tuyến. Các đoàn tàu hiện nay chủ yếu dựa vào rơ-le áp suất thấp cơ học (LPS) để ngắt bảo vệ. Tuy nhiên, khi rơ-le này nhảy thì áp suất đã tụt xuống mức nguy hiểm, tàu đã bị sự cố nặng, gây đình trệ lịch chạy tàu và phát sinh chi phí kéo tàu cứu hộ tốn kém.

CompressorGuard được xây dựng nhằm hỗ trợ các kỹ sư bảo trì và điều độ viên tại các xưởng bảo dưỡng đường sắt đô thị (như Tuyến Metro số 1 Bến Thành – Suối Tiên). Ứng dụng theo dõi liên tục dữ liệu đo đạc cảm biến từng giây, phát hiện sớm các dấu hiệu rò rỉ khí nén và quá nhiệt trước khi rơ-le cơ học bị ngắt, mang lại thời gian báo trước lên đến 33 giờ 52 phút để đội ngũ vận hành chủ động xếp lịch đưa tàu về xưởng sửa chữa trong giờ bảo dưỡng đêm.
```

### Mục 7: Ứng dụng của MongoDB trong Giải pháp
```text
MongoDB đóng vai trò là nền tảng quản lý toàn bộ dữ liệu đo đạc và thông tin vận hành của hệ thống:

1. Bảng dữ liệu chuỗi thời gian (Time Series Collection `measurements`): Lưu trữ toàn bộ 1,5 triệu điểm đo cảm biến 1Hz từ bộ dữ liệu thực tế MetroPT-3 với cấu trúc phân loại `metadata.asset_id`. Bảng dữ liệu gốc này được bảo toàn nguyên vẹn trường thời gian đo gốc (`timestamp`) phục vụ tính toán vật lý. Bảng lưu trữ tín hiệu bất thường (`anomaly_signals`) được cài đặt chỉ mục tự hủy 7 ngày trên thời gian chạy thực nghiệm (`ingested_at`).

2. Thống kê nhanh bằng cửa sổ trượt (`$setWindowFields`): Tính toán tức thời giá trị trung bình và độ lệch chuẩn của độ sụt áp van xả (DV_pressure) cùng nhiệt độ dầu trong 60 giây gần nhất, giúp phát hiện rung động bất thường ngay trong cơ sở dữ liệu mà không cần kéo dữ liệu thô về ứng dụng.

3. Phân tích chu kỳ làm việc đa chiều (`$facet` kết hợp `$group`): Phân loại tỷ lệ thời gian máy nén chạy có tải hay không tải, cùng mức nhiệt độ trung bình ở từng chế độ để người vận hành nắm được hiệu suất hoạt động của máy.

4. Quản lý ca sự cố và sổ cái kiểm toán: Sử dụng các bảng dữ liệu thông thường (`operational_cases`, `case_events`, `failure_fingerprints`) để lưu trữ quy trình xử lý sự cố và ghi nhận nhật ký thao tác bất biến của điều độ viên.
```

### Mục 8: Ứng dụng của Datadog trong Giải pháp
```text
Datadog đóng vai trò là đài quan sát độ tin cậy và theo dõi vận hành tập trung của hệ thống:

1. Theo dõi các chỉ số đo lường qua DogStatsD: Thu thập và hiển thị các nhóm chỉ số gồm tín hiệu cảm biến thời gian thực, điểm số bất thường từ mô hình học máy, số lượng xung nhiễu đã lọc, thời gian can thiệp sớm và tiến độ phục hồi sau sửa chữa.

2. Cảnh báo tự động qua 3 bộ giám sát cấu hình sẵn: Cảnh báo rò rỉ khí nghiêm trọng khi máy nén nạp tải (DV_pressure > 2,0 bar), cảnh báo sai lệch khi mô hình học máy không đồng thuận với quy luật vật lý, và thông báo tự động khi máy nén hoàn thành 5 chu kỳ nạp tải đạt chuẩn sau sửa chữa.

3. Bảng điều khiển quan sát tập trung: Thiết lập 8 khung hiển thị trực quan đồng bộ giữa số liệu cảm biến ngoài thực địa, ngưỡng an toàn và trạng thái đánh giá của mô hình học máy.

4. Minh họa độ trễ xử lý (APM Tracing): Tích hợp thư viện `ddtrace` gắn vết phân tán để đo lường thời gian thực thi của từng công đoạn xử lý dữ liệu.
```

### Mục 9: Kiến trúc Kỹ thuật & Luồng Dữ liệu
```text
Hệ thống được thiết kế theo cấu trúc module gọn gàng, phân định rõ ràng giữa các phần việc:

1. Bộ phát dữ liệu mô phỏng: Giữ nguyên mốc thời gian lịch sử để tính toán vật lý, đồng thời điều tiết nhịp phát theo tốc độ mô phỏng. 100% dữ liệu cảm biến lấy từ bộ dữ liệu thực nghiệm MetroPT-3 nổi tiếng trong ngành đường sắt, hoàn toàn không sinh số ngẫu nhiên.

2. Cụm 6 bộ phát hiện độc lập: Kết hợp quy tắc vật lý (sụt áp van xả DV_pressure > 2,0 bar), ứng suất nhiệt dầu máy nén, tính bước nhảy bền bỉ qua 3 chu kỳ nạp, thống kê theo chế độ chạy, mô hình học máy Isolation Forest (phát hiện bất thường đa biến), và rơ-le áp suất thấp cơ học LPS.

3. Động cơ ra quyết định theo chính sách vận hành: Đánh giá tình huống theo 6 nhánh chính sách rõ ràng, loại bỏ hoàn toàn các cảnh báo giả do rung lắc hay thay đổi tải tức thời.

4. Kiểm tra an toàn trước khi xử lý (ActionGuard): Tự động rà soát 5 điều kiện bắt buộc (bao gồm áp suất mạch xả khí sau bộ sấy TP3 >= 7,0 bar và rơ-le an toàn chưa ngắt) trước khi cho phép điều độ viên đưa tàu về chế độ an toàn.

5. Bàn điều độ trung tâm: Giao diện web trực quan, thuần tiếng Việt chuyên ngành, hiển thị biểu đồ đa cảm biến theo thời gian thực và bàn làm việc 3 bước cho điều độ viên.
```

### Mục 10: Kết quả Đo kiểm & Tính Thực chứng (Verification)
```text
Toàn bộ giải pháp đã vượt qua 5 cổng kiểm định tự động trên toàn bộ 1,5 triệu điểm đo của bộ dữ liệu MetroPT-3:

- Cổng 1 (Không báo giả): Tỷ lệ báo động giả bằng 0% trong suốt tháng vận hành bình thường nhờ cơ chế lọc nhiễu và kiểm tra tính bền bỉ qua các chu kỳ nạp tải.
- Cổng 2 (Cảnh báo sớm): Phát hiện chính xác hiện tượng rò rỉ khí van xả từ 09:50:39 ngày 05/06/2020, tạo ra khoảng thời gian báo trước là 33 giờ 52 phút trước khi rơ-le cơ học LPS bị sụt áp ngắt lúc 19:42:19 ngày 06/06/2020.
- Cổng 3 (Bảo đảm an toàn): Kiểm tra đạt 5/5 điều kiện kỹ thuật trước khi cho phép điều độ viên đưa tàu về chế độ an toàn.
- Cổng 4 (Nghiệm thu sau sửa chữa): Tự động xác minh 5 chu kỳ nạp tải liên tiếp đạt chuẩn áp suất và nhiệt độ sau khi đoàn tàu được bảo trì tại xưởng.
- Cổng 5 (Hiệu năng mượt mà): Đáp ứng mượt mà nhịp dữ liệu thời gian thực từng giây.
- Tính toàn vẹn của cấu trúc chuỗi thời gian và các phép tính vi phân trên MongoDB được kiểm chứng độc lập trên cơ sở dữ liệu thật bằng công cụ `verify_mongodb_timeseries.py`.
```

### Mục 11: Link Tài liệu Kỹ thuật Chi tiết (Notion Hub)
```text
https://app.notion.com/p/3efe9491252a813cba59ea755fe0347d?pvs=204
```
