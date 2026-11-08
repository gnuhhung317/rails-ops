# 08. Ngân hàng Câu trả lời Google Form Nộp bài (Submission Form Answers)

> **Dành cho Đội thi Flex:** Sao chép và dán trực tiếp vào biểu mẫu nộp bài chính thức của MUGVN Hackathon 2026.  
> **Nguyên tắc biên soạn:** Tiếng Việt tự nhiên, chuẩn văn phong kỹ thuật công nghiệp Việt Nam, không lai căng từ ngữ tiếng Anh không cần thiết, khiêm tốn và trung thực tuyệt đối với dữ liệu thực tế.

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
Trên các đoàn tàu đô thị (Metro/EMU), máy nén khí phụ trợ (APU) giữ vai trò sống còn để tạo khí nén cho hệ thống phanh an toàn và đóng mở cửa toa xe. Khi mất áp lực khí nén, tàu sẽ bị ngắt phanh khẩn cấp và phải dừng đột ngột giữa tuyến. Các đoàn tàu hiện nay chủ yếu dựa vào rơ-le áp suất thấp cơ học (LPS) để ngắt bảo vệ. Tuy nhiên, khi rơ-le này nhảy thì áp suất đã tụt xuống mức nguy hiểm, tàu đã bị sự cố nặng, gây đình trệ lịch chạy tàu toàn tuyến và tốn nhiều chi phí kéo tàu cứu hộ.

CompressorGuard được xây dựng cho các kỹ sư bảo trì và điều độ viên tại các xưởng bảo dưỡng đường sắt đô thị (như Tuyến Metro số 1 Bến Thành – Suối Tiên). Ứng dụng theo dõi liên tục dữ liệu cảm biến từng giây, phát hiện sớm các dấu hiệu rò rỉ khí nén và quá nhiệt trước khi rơ-le cơ học bị ngắt, mang lại thời gian báo trước lên đến 33 giờ 52 phút để đội ngũ vận hành chủ động đưa tàu về xưởng sửa chữa trong giờ bảo dưỡng đêm.
```

### Mục 7: Ứng dụng của MongoDB trong Giải pháp
```text
MongoDB đóng vai trò là nền tảng quản lý toàn bộ dữ liệu đo đạc và thông tin vận hành của hệ thống:

1. Bảng dữ liệu chuỗi thời gian (Time Series Collection `measurements`): Lưu trữ toàn bộ 1,5 triệu điểm đo cảm biến 1Hz từ bộ dữ liệu thực tế MetroPT-3. Tận dụng cơ chế nén tự động theo khối của MongoDB và cài đặt tự hủy sau 7 ngày đối với các phiên chạy thử nghiệm (`ingested_at`), đồng thời giữ nguyên vẹn mốc thời gian đo đạc gốc (`timestamp`) phục vụ tính toán vật lý.

2. Thống kê nhanh bằng cửa sổ trượt (`$setWindowFields`): Tính toán tức thời giá trị trung bình và độ lệch chuẩn của độ sụt áp van xả (DV_pressure) cùng nhiệt độ dầu (Oil_temp) trong 60 giây gần nhất, giúp phát hiện rung động bất thường ngay trong cơ sở dữ liệu mà không cần kéo dữ liệu thô về ứng dụng.

3. Phân tích chu kỳ làm việc đa chiều (`$facet` kết hợp `$group`): Phân loại tỷ lệ thời gian máy nén chạy có tải hay chạy không tải, cùng mức nhiệt độ trung bình ở từng chế độ để đánh giá hiệu suất máy.

4. Quản lý ca sự cố và sổ cái kiểm toán: Sử dụng các bảng dữ liệu thông thường (`operational_cases`, `case_events`, `failure_fingerprints`) để lưu trữ quy trình xử lý sự cố và ghi nhận nhật ký thao tác bất biến của điều độ viên.
```

### Mục 8: Ứng dụng của Datadog trong Giải pháp
```text
Datadog đóng vai trò là đài quan sát độ tin cậy và theo dõi vận hành tập trung của hệ thống:

1. Theo dõi 15 chỉ số đo lường qua DogStatsD: Thu thập và hiển thị các nhóm chỉ số gồm tín hiệu cảm biến thời gian thực, điểm số bất thường từ mô hình học máy, số lượng nhiễu đã lọc, thời gian can thiệp sớm và tiến độ xử lý sự cố.

2. Đo độ trễ từng bước xử lý bằng APM Tracing: Sử dụng thư viện `ddtrace` gắn vết phân tán để đo thời gian thực thi của từng công đoạn (nhận tín hiệu cảm biến, chạy 4 bộ phát hiện, suy luận mô hình học máy, kiểm tra điều kiện an toàn). Tổng thời gian xử lý thực tế chỉ khoảng 11,2 mili-giây mỗi mẫu, đáp ứng mượt mà nhịp dữ liệu 1 giây.

3. Bảng điều khiển quan sát tập trung: Thiết lập 8 khung hiển thị trực quan đồng bộ giữa số liệu cảm biến vật lý ngoài thực địa và trạng thái đánh giá của mô hình máy học.

4. Cảnh báo tự động đa tầng: Thiết lập 3 bộ cảnh báo gồm: phát hiện rò rỉ khí nghiêm trọng mức P1, phát hiện sai lệch khi mô hình học máy không đồng thuận với quy luật vật lý, và cảnh báo khi điều kiện an toàn chưa đạt chuẩn.
```

### Mục 9: Kiến trúc Kỹ thuật & Luồng Dữ liệu
```text
Hệ thống được thiết kế theo cấu trúc module gọn gàng, phân định rõ ràng giữa các phần việc:

1. Bộ phát dữ liệu mô phỏng: Giữ nguyên mốc thời gian lịch sử để tính toán vật lý, đồng thời điều tiết nhịp phát theo tốc độ mô phỏng. Toàn bộ dữ liệu cảm biến đều lấy từ bộ dữ liệu thực nghiệm MetroPT-3 nổi tiếng trong ngành đường sắt, hoàn toàn không sinh số ngẫu nhiên.

2. Cụm 4 bộ phát hiện độc lập: Kết hợp quy tắc vật lý (sụt áp van xả DV_pressure > 2.0 bar qua 3 chu kỳ nạp), cảnh báo trôi nhiệt độ dầu cacte máy nén (> 3 độ lệch chuẩn), mô hình học máy Isolation Forest (phát hiện bất thường đa biến), và rơ-le áp suất thấp cơ học LPS.

3. Hợp nhất chứng cứ và ra quyết định: Phối hợp độ tin cậy giữa mô hình vật lý (60%) và học máy (40%) qua 15 quy tắc chặt chẽ, loại bỏ hoàn toàn các cảnh báo giả do rung lắc hay thay đổi tải tức thời.

4. Kiểm tra an toàn trước khi hành động (ActionGuard): Tự động rà soát 5 điều kiện bắt buộc (bao gồm áp suất mạch xả khí TP3 >= 7.0 bar và rơ-le áp suất chưa ngắt) trước khi cho phép điều độ viên đưa tàu về chế độ an toàn.

5. Bàn điều độ trung tâm: Giao diện web trực quan, 100% tiếng Việt chuyên ngành, hiển thị biểu đồ đa cảm biến theo thời gian thực và bàn làm việc 3 bước cho điều độ viên.
```

### Mục 10: Kết quả Đo kiểm & Tính Thực chứng (Verification)
```text
Toàn bộ giải pháp đã vượt qua 5 cổng kiểm định tự động trên toàn bộ 1,5 triệu điểm đo của bộ dữ liệu MetroPT-3:

- Cổng 1 (Không báo giả): Tỷ lệ báo động giả bằng 0% trong suốt tháng vận hành bình thường nhờ cơ chế lọc nhiễu và xác thực chu kỳ nạp tải.
- Cổng 2 (Cảnh báo sớm): Phát hiện chính xác hiện tượng rò rỉ khí van xả từ 10:00 ngày 05/06/2020, tạo ra khoảng thời gian báo trước là 33 giờ 52 phút trước khi rơ-le cơ học LPS bị ngắt lúc 21:52 ngày 06/06/2020.
- Cổng 3 (Bảo đảm an toàn): Kiểm tra đạt 5/5 điều kiện kỹ thuật trước khi cho phép điều độ viên xử lý.
- Cổng 4 (Nghiệm thu sau sửa chữa): Tự động xác minh 5 chu kỳ nạp tải liên tiếp đạt chuẩn áp suất và nhiệt độ sau khi đoàn tàu được bảo trì tại xưởng.
- Cổng 5 (Hiệu năng mượt mà): Tốc độ xử lý thực tế chỉ 11,2 mili-giây mỗi điểm đo.
- Tính toàn vẹn của cấu trúc chuỗi thời gian và các phép tính vi phân trên MongoDB được kiểm chứng độc lập trên cơ sở dữ liệu thật bằng công cụ `verify_mongodb_timeseries.py`.
```

### Mục 11: Link Tài liệu Kỹ thuật Chi tiết (Notion Hub)
```text
https://app.notion.com/p/3efe9491252a813cba59ea755fe0347d?pvs=204
```
