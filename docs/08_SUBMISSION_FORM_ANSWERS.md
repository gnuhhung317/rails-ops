# 08. Ngân hàng Câu trả lời Google Form Nộp bài (Submission Form Answers)

> **Dành cho Đội thi Flex:** Copy-paste trực tiếp vào biểu mẫu nộp bài chính thức của MUGVN Hackathon 2026.  
> **Nguyên tắc:** Ngôn từ kỹ thuật chuẩn xác, khiêm tốn, trung thực, tôn trọng tuyệt đối dữ liệu và mã nguồn thực tế.

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
CompressorGuard — Giám sát Độ tin cậy & Dự báo Sự cố Sớm Máy nén khí Đoàn tàu Đô thị (Metro APU)
```

### Mục 4: Link GitHub Repository
```text
https://github.com/gnuhhung317/rails-ops
```

### Mục 5: Link Video Demo (YouTube / Google Drive)
```text
[DÁN LINK VIDEO DEMO CỦA BẠN TẠI ĐÂY - Quay màn hình 2:30 - 3:00 phút theo kịch bản docs/DEMO_VIDEO_SCRIPT.md]
```

### Mục 6: Tóm tắt Bài toán & Đối tượng Phục vụ (Dưới 200 từ)
```text
Trong hệ thống đầu máy toa xe đường sắt đô thị (Metro/EMU), máy nén khí phụ trợ (APU) giữ vai trò sống còn để duy trì áp lực khí nén cho hệ thống phanh an toàn và cơ cấu đóng mở cửa toa xe. Hiện nay, các đoàn tàu thương mại chủ yếu dựa vào rơ-le áp suất thấp cơ học (Low Pressure Switch - LPS). Khi rơ-le này nhảy, áp suất khí đã tụt xuống mức nguy hiểm, buộc đoàn tàu phải dừng khẩn cấp giữa tuyến, gây ách tắc giao thông đô thị và phát sinh chi phí cứu hộ tốn kém.

CompressorGuard được thiết kế nhằm phục vụ đội ngũ điều độ viên và kỹ sư bảo trì tại các Depot đường sắt đô thị (như Tuyến Metro số 1 Bến Thành – Suối Tiên). Giải pháp theo dõi dòng dữ liệu cảm biến tần số 1Hz, phát hiện sớm các hiện tượng rò rỉ khí nén và suy giảm nhiệt động học trước khi rơ-le cơ học bị ngắt, cung cấp cửa sổ can thiệp an toàn lên tới 33 giờ 52 phút và hỗ trợ điều độ viên ra quyết định bảo trì chủ động.
```

### Mục 7: Ứng dụng của MongoDB trong Giải pháp
```text
MongoDB đóng vai trò là nền tảng lưu trữ dữ liệu vận hành đa tầng cốt lõi của CompressorGuard:
1. Time Series Collection (`measurements`): Lưu trữ dòng dữ liệu cảm biến tần số 1Hz từ hơn 1.5 triệu bản ghi thực tế của bộ dữ liệu MetroPT-3. Tận dụng kiến trúc lưu trữ nén tối ưu (bucketed storage) và thiết lập chỉ mục TTL 7 ngày trên trường thời gian nhận thực tế (`ingested_at`), đồng thời bảo toàn nguyên vẹn trường thời gian lịch sử (`timestamp`) phục vụ suy luận vật lý.
2. Vi phân Dữ liệu Cửa sổ Trượt (`$setWindowFields`): Tính toán tức thời giá trị trung bình trượt và độ lệch chuẩn của độ sụt áp van xả (DV_pressure) và nhiệt độ dầu (Oil_temp) trong cửa sổ 60 giây để phát hiện các dao động bất thường mà không làm quá tải bộ nhớ ứng dụng.
3. Phân tích Chu kỳ Tải Đa chiều (`$facet` + `$group`): Phân tích tỷ trọng hoạt động có tải/không tải (Duty Cycle) và phân bố nhiệt động học phục vụ đánh giá hiệu suất máy nén.
4. Quản trị Dữ liệu Nghiệp vụ & Sổ cái Kiểm toán: Sử dụng các Document Collections (`operational_cases`, `case_events`, `failure_fingerprints`) để duy trì máy trạng thái vòng đời sự cố và lưu vết kiểm toán bất biến (Audit Ledger) cho mọi thao tác của điều độ viên.
```

### Mục 8: Ứng dụng của Datadog trong Giải pháp
```text
Datadog đóng vai trò là Tầng Giám sát Độ tin cậy & Quan sát Hệ thống (Observability & Telemetry Plane):
1. Custom Metrics qua DogStatsD: Thu thập và hiển thị 15 chỉ số đo lường chuẩn hóa thuộc 5 nhóm: Tín hiệu cảm biến thời gian thực, Điểm số bất thường AI/ML, Tỷ lệ triệt tiêu nhiễu xung áp lực, Thời gian cảnh báo sớm (Lead Time), và Trạng thái vòng đời sự cố.
2. Vết Phân tán Toàn trình (APM Distributed Tracing): Tích hợp thư viện ddtrace để đo lường độ trễ thực thi trên từng chặng (đọc cảm biến, đánh giá 4 detector, suy luận Isolation Forest, xác thực an toàn ActionGuard). Kết quả đo kiểm thực tế đạt ~11.2 ms, đảm bảo đáp ứng tốt yêu cầu xử lý thời gian thực 1Hz.
3. Dashboard Chuyên dụng (SRE Watchtower): Thiết lập 8 widget trực quan hóa đồng bộ giữa tín hiệu vật lý và hành vi của mô hình máy học.
4. Hệ thống Cảnh báo Đa ngưỡng (Monitors): Cấu hình 3 bộ giám sát tự động gồm cảnh báo rò rỉ khí nghiêm trọng P1, cảnh báo sai lệch đồng thuận giữa mô hình AI và quy luật vật lý (Detector Disagreement Gauge), và cảnh báo vi phạm chốt chặn an toàn ActionGuard.
```

### Mục 9: Kiến trúc Kỹ thuật & Luồng Dữ liệu
```text
Hệ thống được xây dựng theo mô hình Modular Monolith tách bạch rõ ràng giữa Producer, Pipeline xử lý, Storage và Observer:
1. Producer: Replay Engine vận hành theo cơ chế Dual-Clock, tách biệt nhịp phát mô phỏng và mốc thời gian lịch sử, đảm bảo nguyên tắc Zero Fake Telemetry (100% dữ liệu cảm biến lấy từ bộ dữ liệu thực tế MetroPT-3).
2. Bộ 4 Detector Song song: Kết hợp Rule-based Physical Detector (giám sát độ sụt áp van xả DV_pressure > 2.0 bar trong 3 chu kỳ nạp), Thermodynamic Drift Detector (giám sát trôi nhiệt độ dầu > 3 sigma), Unsupervised Isolation Forest (học máy đa biến không giám sát), và Mechanical LPS Fallback (rơ-le cơ học).
3. Evidence Fusion & Decision Engine: Hợp nhất bằng chứng vật lý (60%) và học máy (40%) qua 15 quy tắc ra quyết định chặt chẽ, loại bỏ hoàn toàn các báo động giả do nhiễu thoáng qua.
4. ActionGuard Pre-Flight Safety: Chốt chặn an toàn kiểm tra nghiêm ngặt 5 điều kiện tiên quyết (bao gồm áp suất mạch xả TP3 >= 7.0 bar và LPS == 1) trước khi cho phép điều độ viên kích hoạt chế độ an toàn (Safe Mode).
5. Web Console v3.0: Giao diện dòng lệnh điều độ hiện đại chuẩn tiếng Việt công nghiệp, tích hợp biểu đồ đa kênh Chart.js và bàn làm việc 3 phân khu.
```

### Mục 10: Kết quả Đo kiểm & Tính Thực chứng (Verification)
```text
Toàn bộ giải pháp đã vượt qua 5 cổng kiểm định tự động (Evaluation Gates 5/5 PASS) trên toàn bộ 1.516.948 bản ghi của MetroPT-3:
- Cổng G1 (Chống báo giả): Tỷ lệ báo giả = 0% trên tập dữ liệu lành mạnh tháng 03/2020 nhờ cơ chế xác nhận chu kỳ nạp tải và bộ lọc chống rung.
- Cổng G2 (Cảnh báo sớm): Phát hiện chính xác sự cố rò rỉ khí van xả từ 10:00 ngày 05/06/2020, tạo ra khoảng thời gian cảnh báo sớm (Lead Time) là 33 giờ 52 phút trước khi rơ-le cơ học LPS bị sụt áp lúc 21:52 ngày 06/06/2020.
- Cổng G3 (Khóa an toàn): ActionGuard xác thực thành công 5/5 điều kiện an toàn trước khi chuyển Safe Mode.
- Cổng G4 (Nghiệm thu phục hồi): Xác minh thành công 5 chu kỳ nạp liên tiếp đạt chuẩn áp suất và nhiệt độ sau khi đoàn tàu được bảo trì tại xưởng.
- Cổng G5 (Hiệu năng): Độ trễ xử lý toàn trình đo được là 11.2 ms/mẫu.
- Tính toàn vẹn của Time Series và Aggregation Pipeline ($setWindowFields, $facet) được kiểm chứng độc lập trên MongoDB instance thật qua script `scripts/verify_mongodb_timeseries.py`.
```

### Mục 11: Link Tài liệu Kỹ thuật Chi tiết (Notion Hub)
```text
https://app.notion.com/p/3efe9491252a813cba59ea755fe0347d?pvs=204
```
