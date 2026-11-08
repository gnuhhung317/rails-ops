# 07. Bằng chứng Đo kiểm & Kết quả Xác minh (Verification Evidence & Benchmarks)

> **Dự án:** CompressorGuard — Industrial Operations Command Platform (MUGVN Hackathon 2026: MongoDB + Datadog)  
> **Cam kết:** 100% bằng chứng kỹ thuật có thể tái lập độc lập bằng các đoạn mã kiểm thử chuẩn trong repository.

---

## 1. Báo cáo 5 Cổng Kiểm định Tự động (Evaluation Gates 5/5 PASS)

Hệ thống cung cấp kịch bản kiểm định độc lập `scripts/verify_evaluation_gates.py` quét qua toàn bộ **1.516.948 bản ghi cảm biến** của bộ dữ liệu gốc `MetroPT-3` để xác minh 5 tiêu chí chất lượng kỹ thuật:

```powershell
cd d:\Code\Projects\self-projects\iot-hackathon
python scripts/verify_evaluation_gates.py
```

### Bảng Kết quả Kiểm định Thực tế:

| Cổng Kiểm định | Nội dung Xác minh Kỹ thuật | Tiêu chuẩn Chấp thuận | Kết quả Thực tế | Đánh giá |
| :---: | :--- | :---: | :---: | :---: |
| **G1** | **Chống Báo Động Giả (Noise Suppression)** | Tỷ lệ báo giả trong dải dữ liệu lành mạnh tháng 03/2020 = $0\%$ | 0 cảnh báo giả trên 100,000 mẫu chuẩn | **PASS** |
| **G2** | **Cảnh báo Sớm Sự cố (Early Detection)** | Phát hiện rò rỉ khí van xả ngày 05/06/2020; Lead Time $\ge 24$ giờ | Phát hiện lúc 10:00 (05/06); Lead Time = **33h 52m** | **PASS** |
| **G3** | **Khóa An toàn (ActionGuard Pre-Flight)** | Kiểm tra đủ 5 điều kiện an toàn trước khi chuyển Safe Mode | 5/5 điều kiện đạt chuẩn (`TP3 = 8.85 bar >= 7.0 bar`) | **PASS** |
| **G4** | **Nghiệm thu Phục hồi (Loaded Recovery)** | Xác nhận 5 chu kỳ nạp liên tiếp sau bảo trì đạt chuẩn nhiệt áp | 5/5 chu kỳ nạp đạt $DV \le 0.1$ bar và $Oil \le 75$ °C | **PASS** |
| **G5** | **Hiệu năng Xử lý (Latency Benchmark)** | Độ trễ xử lý toàn trình mỗi mẫu cảm biến $< 50$ ms | Độ trễ trung bình đo được = **11.2 ms** ($< 15$ ms) | **PASS** |

---

## 2. Kiểm chứng Độc lập trên MongoDB Server Thật (`verify_mongodb_timeseries.py`)

Để đảm bảo các tính năng Time Series và Aggregation Pipeline hoạt động chuẩn xác trên môi trường cơ sở dữ liệu thực (không dựa vào giả lập in-memory), script `scripts/verify_mongodb_timeseries.py` được thiết kế để kết nối trực tiếp với MongoDB instance:

```powershell
# Chạy MongoDB tạm bằng Docker:
docker run -d -p 27017:27017 --name mongo-verify mongo:7.0

# Chạy kiểm thử xác minh:
$env:MONGODB_URI="mongodb://localhost:27017"
$env:MONGODB_DB_NAME="compressorguard_verify"
python scripts/verify_mongodb_timeseries.py
```

### 4 Khẳng định Kỹ thuật được Chứng minh:
1. **Cấu trúc Time Series Thật:** Collection `measurements` được khởi tạo thành công với cấu trúc Time Series của MongoDB Engine, tự động nén và gom nhóm các bản ghi theo bucket nhị phân.
2. **Bảo toàn Dữ liệu Lịch sử & TTL Hợp lý:**
   - Trường `timestamp` (tháng 06/2020) không có TTL index $\rightarrow$ dữ liệu lịch sử được bảo toàn vĩnh viễn.
   - Trường `ingested_at` có chỉ mục TTL 7 ngày $\rightarrow$ tự động dọn dẹp các bản ghi phát lại cũ mà không cần can thiệp thủ công.
3. **Độ chính xác của Pipeline `$setWindowFields`:** Giá trị trung bình trượt và độ lệch chuẩn 60 giây do MongoDB Engine tính toán khớp hoàn toàn với kết quả tính toán độc lập của thư viện `pandas` với sai số tuyệt đối $< 10^{-6}$.
4. **Độ chính xác của Pipeline `$facet` + `$group`:** Phân tích tỷ lệ chu kỳ nạp tải (Duty Cycle) và phân bố nhiệt động học của MongoDB khớp hoàn toàn với kết quả đối chứng của `pandas`.

---

## 3. Mốc Tham chiếu Hiệu năng APM & DogStatsD (Observability Benchmark)

- **Môi trường Đo kiểm:** Máy trạm thử nghiệm Windows 11, CPU AMD Ryzen 7, RAM 16GB, Python 3.12, FastAPI backend, Datadog Agent 7.x (DogStatsD UDP port 8125).
- **Kết quả Đo lường Phân phối Độ trễ (Span Durations):**
  - Đọc mẫu & phân loại chế độ nạp tải: $1.2$ ms
  - Đánh giá 4 Detector song song: $4.8$ ms
  - Suy luận mô hình Isolation Forest: $2.4$ ms
  - Xác thực chốt chặn an toàn ActionGuard: $1.1$ ms
  - Ghi bản ghi vào repository & phát metric: $1.7$ ms
  - **Tổng thời gian xử lý toàn trình (End-to-End Latency):** $\approx 11.2$ ms (thỏa mãn yêu cầu khắt khe của hệ thống thời gian thực 1Hz).
