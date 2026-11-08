# 06. Diễn tập Tình huống Lịch sử Failure #3 (Historical Replay Walkthrough)

> **Dự án:** CompressorGuard — Industrial Operations Command Platform (MUGVN Hackathon 2026: MongoDB + Datadog)  
> **Tình huống:** Rò rỉ cụm van xả nước ngưng máy nén khí (Air Leak Event — Tháng 06/2020)  
> **Nguyên tắc:** Dán nhãn thông tin minh bạch 100% (`[Observed]`, `[Derived]`, `[Simulated / Assumed]`).

---

## 1. Bối cảnh & Dòng Thời gian Tổng thể

Sự cố **Failure #3 (Air Leak)** là sự cố thực tế được ghi nhận trong bộ dữ liệu MetroPT-3 khi van xả nước ngưng tự động (drain valve) bị hở gioăng, khiến khí nén liên tục thất thoát ra ngoài môi trường mỗi khi máy nén nạp tải:

```mermaid
timeline
    title Tiến trình Diễn biến Sự cố Failure #3 & Can thiệp Vận hành
    2020-06-05 10:00 : [Observed] DV_pressure vọt lên > 2.0 bar
                     : [Derived] CompressorGuard kích hoạt cảnh báo P1 sớm
    2020-06-05 10:15 : [Simulated] Điều độ viên xác nhận & tạo Work Order
                     : [Derived] ActionGuard kiểm tra 5/5 điều kiện an toàn
                     : [Simulated] Kích hoạt Safe Mode (chuyển luồng sau bảo trì)
    2020-06-06 21:52 : [Observed] Rơ-le cơ khí LPS nhảy trong dữ liệu gốc
                     : [Derived] Xác nhận thời gian báo trước: 33 giờ 52 phút
    2020-06-08 14:00 : [Observed] Dữ liệu lịch sử sau mốc bảo trì tại xưởng
                     : [Derived] Bảng nghiệm thu 5 chu kỳ nạp đạt 5/5 PASS
                     : [Simulated] Điều độ viên ký duyệt đóng ca sự cố
```

---

## 2. Diễn tiến Chi tiết Từng Giai đoạn

### Giai đoạn 1: Phát hiện Bất thường Sớm (05/06/2020 — 10:00)
- `[Observed]` Cảm biến `DV_pressure` bắt đầu xuất hiện các đỉnh sụt áp bất thường vượt ngưỡng $2.0$ bar (bình thường $< 0.1$ bar) trong các chu kỳ nạp tải liên tiếp của máy nén khí.
- `[Derived]` 
  - Mô hình học máy Unsupervised Isolation Forest ghi nhận sự bất ổn định trong không gian vector 6 chiều, đẩy điểm số bất thường từ $0.12$ vọt lên $0.78$ (vượt ngưỡng báo động $0.65$).
  - Thuật toán `PhysicalDrainValveDetector` xác nhận áp suất van xả duy trì bất thường qua 3 chu kỳ tải.
  - Điểm số hợp nhất bằng chứng (Fused Anomaly Score) đạt $0.85$.
- `[Simulated / Assumed]`
  - Hệ thống tự động khởi tạo ca sự cố mức độ ưu tiên P1 trên giao diện Web Console của đoàn tàu minh họa `TRAIN-302`.
  - Cảnh báo âm thanh và tín hiệu nhấp nháy xuất hiện trên màn hình của điều độ viên `DISPATCHER-0941`.

### Giai đoạn 2: Tiếp nhận & Phê duyệt Chế độ An toàn (05/06/2020 — 10:15)
- `[Simulated / Assumed]`
  - Điều độ viên nhấp nút **Tiếp nhận Ca** (`POST /api/case/acknowledge`), gán mức ưu tiên P1-CRITICAL và bổ sung ghi chú chẩn đoán kỹ thuật.
  - Điều độ viên lập Lệnh công tác bảo trì (Work Order) chỉ định đưa đoàn tàu về kiểm tra cụm van tại Depot Long Bình trong khung giờ bảo trì ban đêm.
- `[Derived]`
  - Trước khi cho phép chuyển trạng thái vận hành, hệ thống gọi `GET /api/action/guard-status` để kích hoạt `ActionGuard`.
  - ActionGuard tiến hành kiểm tra tự động 5 tiêu chí vật lý:
    1. Ca sự cố đang hoạt động và được xác nhận $\rightarrow$ `PASS`.
    2. DecisionEngine khuyến nghị can thiệp giảm thiểu $\rightarrow$ `PASS`.
    3. Không có ca sự cố xung đột khác trên cùng máy nén $\rightarrow$ `PASS`.
    4. Áp suất mạch xả an toàn cho hành trình về depot (`TP3 = 8.85 bar >= 7.0 bar` và `LPS == 1`) $\rightarrow$ `PASS`.
    5. Đoạn dữ liệu lịch sử sau bảo trì đã sẵn sàng $\rightarrow$ `PASS`.
- `[Simulated / Assumed]`
  - Với kết quả **5/5 PASS**, điều độ viên được cấp quyền bấm nút **Kích hoạt Safe Mode** (`POST /api/action/safe-mode`).
  - Hệ thống ghi lại chữ ký số của điều độ viên vào Sổ cái kiểm toán bất biến (Audit Ledger) và điều hướng luồng mô phỏng sang dữ liệu sau bảo trì.

### Giai đoạn 3: Mốc Đối chứng Hỏng hóc Cơ khí LPS (06/06/2020 — 21:52)
- `[Observed]`
  - Trong dữ liệu lịch sử gốc của MetroPT-3 (khi đoàn tàu thực tế chưa được trang bị hệ thống cảnh báo sớm AI), máy nén khí tiếp tục hoạt động trong tình trạng rò rỉ khí nghiêm trọng suốt hơn 1 ngày.
  - Áp suất toàn hệ thống tụt dốc thảm hại, khiến **Rơ-le áp suất thấp cơ học (LPS) bị ngắt (nhảy từ 1 về 0) lúc 21:52 ngày 06/06/2020**. Đây là thời điểm đoàn tàu thực tế ngoài đời bị dừng khẩn cấp trên tuyến.
- `[Derived]`
  - **Thời gian Cảnh báo Dẫn trước (Intervention Lead Time):**
    $$\text{Lead Time} = t_{\text{LPS Trip (06/06 21:52)}} - t_{\text{CompressorGuard Detection (05/06 10:00)}} = 33\text{ giờ } 52\text{ phút}$$
  - Khoảng thời gian $33\text{h } 52\text{m}$ này chính là **cửa sổ vàng can thiệp an toàn**, cho phép đơn vị vận hành chủ động đưa tàu về trạm sửa chữa mà hoàn toàn không làm gián đoạn lịch trình chạy tàu của mạng lưới.

### Giai đoạn 4: Nghiệm thu Phục hồi sau Sửa chữa (08/06/2020)
- `[Observed]`
  - Luồng dữ liệu chuyển sang mốc thời gian ngày $08/06/2020$ — thời điểm máy nén khí trong bộ dữ liệu gốc đã được kỹ sư bảo trì thay thế cụm linh kiện và đưa vào vận hành trở lại.
- `[Derived]`
  - Hệ thống kích hoạt thuật toán giám sát phục hồi (`GET /api/recovery`), liên tục theo dõi 5 chu kỳ nạp tải kế tiếp (`LOADED`):
    - Mẫu 1: $DV = 0.02$ bar, $Oil = 58.2$ °C $\rightarrow$ `PASS`
    - Mẫu 2: $DV = 0.01$ bar, $Oil = 61.5$ °C $\rightarrow$ `PASS`
    - Mẫu 3: $DV = 0.02$ bar, $Oil = 63.8$ °C $\rightarrow$ `PASS`
    - Mẫu 4: $DV = 0.01$ bar, $Oil = 65.1$ °C $\rightarrow$ `PASS`
    - Mẫu 5: $DV = 0.02$ bar, $Oil = 66.4$ °C $\rightarrow$ `PASS`
  - Đạt tiêu chuẩn **5/5 chu kỳ nạp ổn định**.
- `[Simulated / Assumed]`
  - Nút **Đóng Ca Sự cố** (`POST /api/case/close`) sáng lên.
  - Điều độ viên thực hiện ký duyệt đóng ca, hoàn tất chu trình quản trị sự cố khép kín.
