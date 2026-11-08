# 03. Lưu trữ và Xử lý Dữ liệu trên MongoDB

> **Mục tiêu tài liệu:** Giải thích rõ MongoDB được sử dụng để lưu trữ và phân tích dữ liệu như thế nào trong giải pháp CompressorGuard.  
> **Bố cục:** Phần 1 dành cho người vận hành hiểu bản chất ứng dụng; Phần 2 dành cho lập trình viên tra cứu kỹ thuật.

---

## PHẦN 1: DÀNH CHO NGƯỜI VẬN HÀNH

### 1. MongoDB Lưu Những Gì?
Trong hệ thống CompressorGuard, MongoDB đóng vai trò là kho dữ liệu trung tâm, lưu giữ 4 nhóm thông tin chính:
1. **Dữ liệu cảm biến từng giây:** Lưu toàn bộ số đo áp suất, nhiệt độ, dòng điện và trạng thái rơ-le từ 1,5 triệu điểm đo thực nghiệm của bộ dữ liệu MetroPT-3.
2. **Hồ sơ các ca sự cố:** Theo dõi vòng đời của từng sự cố (khi nào phát hiện, mức độ ưu tiên P1, điều độ viên nào đang tiếp nhận).
3. **Nhật ký thao tác của con người:** Sổ cái kiểm toán lưu vết từng hành động của điều độ viên (tiếp nhận ca, lập lệnh sửa chữa, ký duyệt nghiệm thu) để đảm bảo tính minh bạch và trách nhiệm giải trình.
4. **Bộ mẫu sự cố tham chiếu:** Các đặc trưng của các đợt hỏng hóc trong lịch sử để giúp hệ thống nhận diện loại hư hỏng và gợi ý cẩm nang xử lý phù hợp.

### 2. Hai Phép Tính Trực Tiếp trên Cơ Sở Dữ Liệu
Thay vì phải kéo hàng trăm ngàn dòng dữ liệu thô về máy chủ ứng dụng để tính toán (gây chậm và tốn bộ nhớ), hệ thống tận dụng sức mạnh xử lý của chính MongoDB qua hai phép phân tích:
- **Tính toán thống kê cửa sổ trượt 60 giây (`$setWindowFields`):** Tính trực tiếp giá trị trung bình và độ lệch chuẩn của cảm biến trong 1 phút gần nhất. Phép tính này giúp phát hiện ngay các dao động áp suất bất thường của van xả ngay tại tầng cơ sở dữ liệu.
- **Phân loại chu kỳ làm việc đa chiều (`$facet` kết hợp `$group`):** Thống kê tỷ lệ phần trăm thời gian máy nén chạy có tải hay không tải, cùng mức nhiệt độ trung bình ở từng chế độ để người vận hành nắm được hiệu suất hoạt động của máy nén.

---

## PHẦN 2: CHI TIẾT KỸ THUẬT DÀNH CHO LẬP TRÌNH VIÊN

### 1. Cấu trúc 5 Bảng Dữ liệu (Collections)

Mã nguồn tại `src/storage/mongo_client.py` và `repository.py` khởi tạo 5 bảng dữ liệu với các đặc tả kỹ thuật chuẩn xác sau:

| Tên Bảng | Kiểu Dữ liệu | Mục đích Sử dụng | Cấu hình Chỉ mục & Vòng đời Dữ liệu |
| :--- | :---: | :--- | :--- |
| `measurements` | **Time Series** | Lưu các điểm đo cảm biến 1Hz | `timeField: "timestamp"`, `metaField: "metadata"`, `granularity: "seconds"`. Chỉ mục trên `metadata.asset_id` và `timestamp`. **Không gắn TTL** để bảo toàn dữ liệu đo lịch sử năm 2020. |
| `anomaly_signals` | Document | Lưu các tín hiệu bất thường thô và số lượng nhiễu đã lọc | Có chỉ mục tự hủy (TTL) **7 ngày** trên trường thời gian nhận thực tế: `expireAfterSeconds: 604800` gắn trên trường `ingested_at`. |
| `operational_cases` | Document | Quản lý trạng thái và hồ sơ ca sự cố | Chỉ mục duy nhất trên mã ca `case_id` và chỉ mục tìm kiếm theo thiết bị `asset_id`. |
| `case_events` | Document | Sổ cái kiểm toán bất biến các sự kiện vận hành | Lưu vết theo dạng chỉ thêm mới (append-only) cho mọi thao tác của điều độ viên. |
| `failure_fingerprints` | Document | Lưu các vector mẫu sự cố chuẩn hóa từ lịch sử | Lưu trữ các bộ đặc trưng chuẩn (seed data) để tham chiếu cẩm nang xử lý. |

### 2. Quy tắc Quan trọng về Bảo toàn Dữ liệu Lịch sử (TTL Rule)
Trong các dự án mô phỏng dữ liệu lịch sử (năm 2020), nếu cài đặt TTL trực tiếp lên trường thời gian đo gốc `timestamp`, cơ chế tự dọn dẹp của MongoDB sẽ xóa sạch toàn bộ dữ liệu ngay khi vừa nạp vào.

Do đó, hệ thống phân định rõ:
- Trường `timestamp` (tháng 06/2020) được bảo tồn nguyên vẹn.
- Chỉ mục tự hủy 7 ngày chỉ được đặt trên trường `ingested_at` của bảng `anomaly_signals` để dọn dẹp các tín hiệu phát sinh trong quá trình chạy thử nghiệm.

### 3. Cách So khớp Mẫu Sự cố Tham chiếu
Khi phát hiện sự cố, hàm `match_failure_fingerprint()` trong `src/storage/repository.py` truy vấn các mẫu đặc trưng từ bảng `failure_fingerprints`, sau đó **sử dụng hàm toán học Python** (`math.sqrt` và tích vô hướng vector) để tính toán độ tương đồng Cosine giữa vector đo đạc thực tế và vector mẫu tham chiếu. Đây là cách làm thực dụng, ổn định và không phụ thuộc vào hạ tầng Vector Search phức tạp bên ngoài.
