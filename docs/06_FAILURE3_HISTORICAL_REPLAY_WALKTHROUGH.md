# 06. Diễn tập Sự cố số 3 từ Dữ liệu Lịch sử

> **Tình huống mô phỏng:** Hỏng gioăng cụm van xả nước ngưng của máy nén khí (Tháng 06/2020)  
> **Nguyên tắc phân định:** Dán nhãn thông tin rõ ràng: `[Dữ liệu Thực tế]`, `[Thuật toán Tính toán]`, `[Kịch bản Giả định]`.

---

## 1. Trình tự Diễn biến Sự cố Tổng thể

Sự cố số 3 (rò rỉ khí nén) là một sự việc có thật được ghi lại trong bộ dữ liệu MetroPT-3 khi van xả nước ngưng tự động bị hở gioăng, khiến khí nén liên tục bị thất thoát ra ngoài môi trường mỗi khi máy nén nạp tải:

```mermaid
timeline
    title Tiến trình Diễn biến Sự cố và Can thiệp Vận hành
    2020-06-05 09:50:39 : [Thuật toán Tính toán] CompressorGuard phát hiện sụt áp van xả và kích hoạt cảnh báo sớm
    2020-06-05 10:15:00 : [Kịch bản Giả định] Điều độ viên tiếp nhận ca, kiểm tra an toàn và lập lệnh sửa chữa
    2020-06-06 19:42:19 : [Dữ liệu Thực tế] Rơ-le áp suất thấp cơ học LPS trong dữ liệu gốc bị sụt áp và ngắt
                         : [Thuật toán Tính toán] Xác nhận thời gian báo trước đạt 33 giờ 52 phút
    2020-06-08 16:05:00 : [Dữ liệu Thực tế] Phát lại dòng dữ liệu sau khi máy nén được bảo trì tại xưởng
                         : [Thuật toán Tính toán] Tự động nghiệm thu 5 chu kỳ nạp liên tiếp đạt chuẩn
                         : [Kịch bản Giả định] Điều độ viên ký duyệt đóng ca sự cố
```

---

## 2. Diễn biến Chi tiết Qua 4 Giai đoạn

### Giai đoạn 1: Máy nén bình thường và xuất hiện bất thường (Ngày 05/06/2020 — 09:50:39)
- `[Dữ liệu Thực tế]` Cảm biến độ sụt áp van xả `DV_pressure` bắt đầu xuất hiện các đỉnh áp suất bất thường vượt ngưỡng $2,0$ bar (khi van đóng kín bình thường thì giá trị $< 0,1$ bar) trong các chu kỳ nạp tải liên tiếp của máy nén.
- `[Thuật toán Tính toán]` 
  - Mô hình học máy Isolation Forest phát hiện biến động bất thường đa chiều, đẩy điểm số bất thường từ $0,12$ lên $0,78$ (vượt ngưỡng cảnh báo $0,35$).
  - Thuật toán kiểm tra vật lý xác nhận áp suất van xả duy trì mức cao bất thường liên tục qua 3 chu kỳ nạp tải.
  - Lúc **09:50:39**, hệ thống chính thức kích hoạt ca sự cố mức ưu tiên P1.
- `[Kịch bản Giả định]`
  - Hệ thống hiển thị ca sự cố trên màn hình điều độ của đoàn tàu `TRAIN-302`.
  - Chuông cảnh báo và đèn tín hiệu nhấp nháy trên màn hình trực của điều độ viên.

### Giai đoạn 2: Tiếp nhận và thử nghiệm quy trình xử lý (Ngày 05/06/2020 — 10:15)
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
  - Với kết quả **5/5 điều kiện đều ĐẠT**, điều độ viên bấm duyệt đưa tàu về chế độ an toàn. Thao tác này được ghi vào nhật ký kiểm toán và hệ thống chuyển dữ liệu sang mốc thời gian sau bảo trì.

### Giai đoạn 3: Mốc đối chứng hỏng hóc trong dữ liệu lịch sử (Ngày 06/06/2020 — 19:42:19)
- `[Dữ liệu Thực tế]`
  - Trong bộ dữ liệu gốc ngoài đời thực (khi đoàn tàu thực tế chưa có hệ thống cảnh báo sớm), máy nén khí tiếp tục phải chạy trong tình trạng rò rỉ khí nặng suốt hơn một ngày.
  - Áp suất trong hệ thống sụt giảm liên tục, khiến **rơ-le áp suất thấp cơ học (LPS) bị ngắt lúc 19:42:19 ngày 06/06/2020**.
- `[Thuật toán Tính toán]`
  - **Thời gian Cảnh báo Báo trước (Lead Time):**
    $$\text{Thời gian báo trước} = 19:42:19\text{ (ngày 06/06)} - 09:50:39\text{ (ngày 05/06)} = 33\text{ giờ } 51\text{ phút } 40\text{ giây} \approx 33\text{ giờ } 52\text{ phút}$$
  - Khoảng thời gian gần 34 tiếng đồng hồ này là cửa sổ can thiệp an toàn quý giá, đủ để điều độ viên xếp lịch đưa đoàn tàu về xưởng sửa chữa trong đêm mà không làm ảnh hưởng đến hành khách.

> **Đối chiếu với thông tin tổng quát trong bài báo công bố UCI:**  
> Bài báo khoa học của MetroPT-3 ghi nhận chung khoảng thời gian xảy ra sự cố kéo dài từ 10:00 ngày 05/06 đến 14:30 ngày 07/06, và mốc thời gian bảo trì ghi nhận tại xưởng là 16:00 ngày 08/06. Mốc phát hiện 09:50:39 và mốc ngắt rơ-le 19:42:19 là các mốc đo đạc chính xác đến từng giây được trích xuất từ dữ liệu cảm biến thực tế để tính toán khoảng thời gian báo trước.

### Giai đoạn 4: Kiểm tra dữ liệu sau bảo trì (Ngày 08/06/2020 — 16:05:00)
- `[Dữ liệu Thực tế]`
  - Luồng dữ liệu chuyển sang mốc ngày 08/06/2020 lúc 16:05 — thời điểm máy nén khí trong bộ dữ liệu gốc đã được kỹ sư thay thế phụ tùng và vận hành thử lại tại xưởng.
- `[Thuật toán Tính toán]`
  - Hệ thống tự động theo dõi liên tiếp 5 chu kỳ nạp tải của máy nén:
    - Chu kỳ 1: Áp suất van $0,02$ bar, nhiệt độ dầu $58,2$ °C $\rightarrow$ `ĐẠT`
    - Chu kỳ 2: Áp suất van $0,01$ bar, nhiệt độ dầu $61,5$ °C $\rightarrow$ `ĐẠT`
    - Chu kỳ 3: Áp suất van $0,02$ bar, nhiệt độ dầu $63,8$ °C $\rightarrow$ `ĐẠT`
    - Chu kỳ 4: Áp suất van $0,01$ bar, nhiệt độ dầu $65,1$ °C $\rightarrow$ `ĐẠT`
    - Chu kỳ 5: Áp suất van $0,02$ bar, nhiệt độ dầu $66,4$ °C $\rightarrow$ `ĐẠT`
  - Đạt tiêu chuẩn **5/5 chu kỳ nạp ổn định**.
- `[Kịch bản Giả định]`
  - Nút **Đóng Ca Sự cố** sáng lên để điều độ viên ký duyệt hoàn tất ca xử lý.

---

## 3. Hai Lưu ý Quan trọng về Thuật ngữ và Nghiệp vụ

1. **Phân biệt đúng cảm biến `TP3` và `Reservoirs`:**  
   `TP3` là cảm biến đo áp suất tại bảng khí nén ở đầu ra của khối sấy khí, phản ánh sự thông thoát của dòng khí nén. Cảm biến đo áp suất thực tế bên trong các bình chứa khí chính là cột `Reservoirs`. Cần phân biệt rõ hai vị trí này, không dùng lẫn lộn.
2. **Tính chất của kịch bản vận hành:**  
   Dữ liệu cảm biến và mốc ngắt rơ-le LPS là số liệu thực tế từ bộ dữ liệu Metro do Porto (Bồ Đào Nha). Tình huống đoàn tàu dừng giữa tuyến, mất phanh hoặc lịch trình chạy tàu tuyến Metro số 1 Bến Thành – Suối Tiên là **giả định nghiệp vụ minh họa** được xây dựng để kiểm thử quy trình vận hành của phần mềm.
