# 06. Diễn tập Tình huống Sự cố Rò rỉ Khí số 3

> **Dự án:** CompressorGuard — Hệ thống Giám sát & Quản lý Vận hành Máy nén khí Đoàn tàu (MUGVN Hackathon 2026: MongoDB + Datadog)  
> **Tình huống:** Hỏng gioăng cụm van xả nước ngưng của máy nén khí (Tháng 06/2020)  
> **Nguyên tắc phân định:** Dán nhãn thông tin rõ ràng: `[Dữ liệu Thực tế]`, `[Thuật toán Tính toán]`, `[Kịch bản Giả định]`.

---

## 1. Bối cảnh & Tiến trình Diễn biến Sự cố

Sự cố số 3 (rò rỉ khí nén) là sự việc có thật được ghi lại trong bộ dữ liệu MetroPT-3 khi van xả nước ngưng tự động bị hở gioăng, khiến khí nén liên tục bị thất thoát ra ngoài môi trường mỗi khi máy nén hoạt động:

```mermaid
timeline
    title Tiến trình Diễn biến Sự cố và Can thiệp Vận hành
    2020-06-05 10:00 : [Dữ liệu Thực tế] Sụt áp van xả DV_pressure tăng vọt trên 2.0 bar
                     : [Thuật toán Tính toán] CompressorGuard kích hoạt cảnh báo sớm mức P1
    2020-06-05 10:15 : [Kịch bản Giả định] Điều độ viên tiếp nhận ca và lập lệnh sửa chữa
                     : [Thuật toán Tính toán] Tự động kiểm tra đạt 5/5 điều kiện an toàn
                     : [Kịch bản Giả định] Điều độ viên phê duyệt đưa tàu về chế độ an toàn
    2020-06-06 21:52 : [Dữ liệu Thực tế] Rơ-le cơ học LPS bị sụt áp và nhảy ngắt trên tuyến
                     : [Thuật toán Tính toán] Xác nhận thời gian cảnh báo trước đạt 33 giờ 52 phút
    2020-06-08 14:00 : [Dữ liệu Thực tế] Dữ liệu đo đạc sau khi máy nén được bảo trì tại xưởng
                     : [Thuật toán Tính toán] Nghiệm thu 5 chu kỳ nạp liên tiếp đạt chuẩn
                     : [Kịch bản Giả định] Điều độ viên ký duyệt đóng ca sự cố
```

---

## 2. Diễn biến Chi tiết Qua 4 Giai đoạn

### Giai đoạn 1: Phát hiện Bất thường Sớm (Ngày 05/06/2020 — 10:00)
- `[Dữ liệu Thực tế]` Cảm biến độ sụt áp van xả `DV_pressure` bắt đầu xuất hiện các đỉnh áp suất bất thường vượt ngưỡng $2,0$ bar (khi van đóng kín bình thường thì giá trị $< 0,1$ bar) trong các chu kỳ nạp tải liên tiếp của máy nén.
- `[Thuật toán Tính toán]` 
  - Mô hình học máy Isolation Forest phát hiện biến động bất thường đa chiều, đẩy điểm số bất thường từ $0,12$ lên $0,78$ (vượt ngưỡng cảnh báo $0,65$).
  - Thuật toán kiểm tra vật lý xác nhận áp suất van xả duy trì mức cao bất thường liên tục qua 3 chu kỳ nạp.
  - Điểm số hợp nhất chứng cứ đạt mức cao ($0,85$).
- `[Kịch bản Giả định]`
  - Hệ thống tự động tạo ca sự cố mức ưu tiên P1 trên màn hình điều độ của đoàn tàu `TRAIN-302`.
  - Chuông cảnh báo và đèn tín hiệu nhấp nháy trên màn hình trực của điều độ viên.

### Giai đoạn 2: Tiếp nhận & Phê duyệt Đưa tàu về Chế độ An toàn (Ngày 05/06/2020 — 10:15)
- `[Kịch bản Giả định]`
  - Điều độ viên bấm nút **Tiếp nhận Ca**, gán mức ưu tiên cao nhất P1 và nhập ghi chú nhận định ban đầu.
  - Điều độ viên lập Lệnh công tác sửa chữa, chỉ định đưa đoàn tàu về kiểm tra cụm van tại Depot Long Bình vào khung giờ bảo dưỡng đêm.
- `[Thuật toán Tính toán]`
  - Trước khi cho phép chuyển trạng thái vận hành, hệ thống tự động kiểm tra 5 điều kiện kỹ thuật an toàn:
    1. Ca sự cố đang mở và đã được điều độ viên tiếp nhận $\rightarrow$ `ĐẠT`.
    2. Động cơ ra quyết định khuyến nghị cần can thiệp xử lý $\rightarrow$ `ĐẠT`.
    3. Không có ca sự cố nào khác đang xung đột trên cùng máy nén $\rightarrow$ `ĐẠT`.
    4. Áp lực mạch xả khí vẫn đủ an toàn để tàu tự chạy về xưởng (`TP3 = 8,85 bar >= 7,0 bar` và rơ-le an toàn chưa ngắt) $\rightarrow$ `ĐẠT`.
    5. Đã có sẵn đoạn dữ liệu sau bảo trì để đối chứng $\rightarrow$ `ĐẠT`.
- `[Kịch bản Giả định]`
  - Với kết quả **5/5 điều kiện đều ĐẠT**, nút **Kích hoạt Chế độ An toàn** sáng lên để điều độ viên bấm duyệt.
  - Thao tác phê duyệt được ghi nhận vào sổ cái kiểm toán và hệ thống chuyển luồng dữ liệu sang mốc thời gian sau bảo trì.

### Giai đoạn 3: Mốc Đối chứng Hỏng hóc Thực tế ngoài Hiện trường (Ngày 06/06/2020 — 21:52)
- `[Dữ liệu Thực tế]`
  - Trong bộ dữ liệu gốc ngoài đời thực (khi đoàn tàu chưa được trang bị hệ thống cảnh báo sớm AI), máy nén khí tiếp tục phải chạy trong tình trạng rò rỉ khí nặng suốt hơn một ngày.
  - Khí nén trong hệ thống bị cạn kiệt, khiến **rơ-le áp suất thấp cơ học (LPS) bị ngắt lúc 21:52 ngày 06/06/2020**. Đây là thời điểm đoàn tàu thực tế ngoài đời bị mất phanh khẩn cấp và phải dừng tàu giữa tuyến.
- `[Thuật toán Tính toán]`
  - **Thời gian Cảnh báo Báo trước (Lead Time):**
    $$\text{Thời gian báo trước} = \text{Mốc rơ-le cơ học nhảy (21:52 ngày 06/06)} - \text{Mốc hệ thống cảnh báo (10:00 ngày 05/06)} = 33\text{ giờ } 52\text{ phút}$$
  - Khoảng thời gian gần 34 tiếng đồng hồ này là **cửa sổ can thiệp an toàn quý giá**, đủ để đưa đoàn tàu về xưởng sửa chữa mà hoàn toàn không làm gián đoạn lịch chạy tàu của hành khách.

### Giai đoạn 4: Nghiệm thu Phục hồi sau Sửa chữa (Ngày 08/06/2020)
- `[Dữ liệu Thực tế]`
  - Luồng dữ liệu chuyển sang mốc ngày 08/06/2020 — thời điểm máy nén khí trong bộ dữ liệu gốc đã được kỹ sư thay thế phụ tùng và chạy thử lại tại xưởng.
- `[Thuật toán Tính toán]`
  - Hệ thống tự động theo dõi liên tiếp 5 chu kỳ nạp tải của máy nén:
    - Chu kỳ 1: Áp suất van $0,02$ bar, nhiệt độ dầu $58,2$ °C $\rightarrow$ `ĐẠT`
    - Chu kỳ 2: Áp suất van $0,01$ bar, nhiệt độ dầu $61,5$ °C $\rightarrow$ `ĐẠT`
    - Chu kỳ 3: Áp suất van $0,02$ bar, nhiệt độ dầu $63,8$ °C $\rightarrow$ `ĐẠT`
    - Chu kỳ 4: Áp suất van $0,01$ bar, nhiệt độ dầu $65,1$ °C $\rightarrow$ `ĐẠT`
    - Chu kỳ 5: Áp suất van $0,02$ bar, nhiệt độ dầu $66,4$ °C $\rightarrow$ `ĐẠT`
  - Đạt tiêu chuẩn **5/5 chu kỳ nạp ổn định**.
- `[Kịch bản Giả định]`
  - Nút **Đóng Ca Sự cố** sáng lên.
  - Điều độ viên thực hiện ký duyệt đóng ca, hoàn tất trọn vẹn quy trình xử lý sự cố.
