# Kịch bản Video Demo — RailOps VN / CompressorGuard
### Hướng dẫn quay từng shot, đúng nhịp, cho bài nộp MUGVN Hackathon 2026

> **Artifact type:** Video demo (bắt buộc theo thể lệ — cùng với Repository và Slide chung kết)
> **Date:** 2026-11-07 · **Target runtime:** 5:00 (dự phòng bản 2:30 ở §6)
> **Người nói:** 1 giọng, vai *CTO/Trưởng nhóm kỹ thuật*, nói tiếng Việt, thuật ngữ kỹ thuật giữ tiếng Anh
> **Quy tắc bất biến khi quay:** không cắt ghép để tạo cảm giác hệ thống tự chạy. Mọi thứ trong video phải được bấm và chờ thật.

---

## 0. Chuẩn bị trước khi bấm ghi (15 phút)

```bash
# 1. Đặt dataset đúng chỗ (bắt buộc, file không commit trong git)
ls dataset/MetroPT3(AirCompressor).csv     # ~145 MB, 1.516.948 dòng

# 2. Bật MongoDB (Atlas SRV hoặc local) và Datadog Agent nếu muốn thấy trace thật
set MONGODB_URI=mongodb+srv://...          # để thấy Time Series + $setWindowFields thật
set DD_API_KEY=...                         # agent DogStatsD:8125 / APM:8126

# 3. Khởi động toàn bộ stack bằng MỘT lệnh
python run_demo.py                          # mở console tại http://localhost:8000/
```

**Checklist tiền quay — phải đạt hết, nếu không thì quay lại sau:**

| # | Kiểm tra | Cách kiểm tra nhanh |
|:-:|:---|:---|
| 1 | Console tải, **không** có con số hardcode | F12 → Network: mọi ô số đều đến từ `GET /api/...`. Thử tắt mạng API → UI phải hiện trạng thái lỗi, không hiển thị số ma |
| 2 | Không có nút demo trên Header chính | Nhìn header: chỉ có breadcrumb, KPI, timeframe, operator, 2 nút drawer |
| 3 | Streams đang chạy phía server | `curl http://localhost:8000/demo/status` → `total_points_emitted` tăng dần, `is_paused:false` |
| 4 | Datadog live | `curl -s localhost:8000/metrics` có `compressorguard.*` |
| 5 | Kịch bản `failure_3` đang active | `curl -s localhost:8000/api/scenarios` → `active_scenario_id` |
| 6 | Chuỗi vận hành không gãy trước khi bấm record | `CONSOLE_BASE_URL=http://localhost:8000 python scripts/verify_console_journey.py` → `23/23 assertions passed` (chạy ở terminal riêng, server vẫn bật). Script này tự bấm lại đúng 4 bước bạn sẽ nói trong video, kể cả bước Safe Mode sớm bị **409**. |

**Bố cục màn hình khi quay:** trình duyệt fullscreen (F11), zoom 90%, tắt bookmark bar, đổi tên tab thành `RailOps VN — Operations Console`. Overlay góc: `LIVE SIMULATION · HISTORICAL DATA`. Dùng OBS, 1080p60, mic gần, nền lặng.

---

## 1. Cấu trúc kể chuyện (vì sao dựng theo thứ tự này)

Video đi theo đúng một đường ray cảm xúc của người mua công nghệ, không đi theo cấu trúc module code:

```
Rủi ro thật  →  Chúng ta đang mù  →  Bật đèn sớm  →  Bằng chứng, không tin mù  →
Con người quyết định, máy chặn quyết định liều  →  Xác nhận đã lành thật  →  Quy mô
```

Mỗi đoạn đều trả lời đúng một tiêu chí chấm: **Tác động → Sáng tạo → Kỹ thuật → Trình bày.**

---

## 2. Kịch bản chi tiết theo shot

### [0:00 – 0:25] SHOT 1 — BLACK SCREEN, CHỈ MỘT CON SỐ
**Hình:** nền tối, chữ lớn dần: `33h 52m`. Không nhạc dồn, chỉ một tiếng tick.
**Thoại:**
> "33 giờ 52 phút. Đó là khoảng thời gian giữa lúc chúng tôi biết chắc máy nén khí trên một đoàn tàu đang rò khí — và lúc hệ thống cảnh báo hiện nay của đường sắt phát hiện ra nó.
> Trong 33 giờ đó, nếu bạn biết trước, bạn kéo tàu về depot và thay một cái gioăng. Nếu bạn không biết, bạn có một đoàn tàu chết giữa tuyến, hoặc một toa tàu mất áp suất phanh."

**Mục đích:** bán bằng chứng trước khi bán tính năng. BGK nhớ con số này, không nhớ tên module.

---

### [0:25 – 0:55] SHOT 2 — VẤN ĐỀ CÓ THẬT Ở VIỆT NAM
**Hình:** ảnh tư liệu/bản đồ tuyến Metro 1 Bến Thành – Suối Tiên và Cát Linh – Hà Đông; chèn text nguồn.
**Thoại:**
> "Đây không phải bài toán tưởng tượng. Cát Linh – Hà Đông sau hơn ba năm đã xuống cấp nhiều hạng mục; ga Yên Nghĩa từng bị nước tràn vào và Hà Nội phải đề xuất sửa chữa khẩn cấp. Thành phố đang chuẩn bị đầu tư mười tuyến metro. Và dự án đường sắt tốc độ cao Bắc – Nam 1.541 km vừa được phê duyệt, khởi công trước cuối năm nay.
> Chúng ta đang mua rất nhiều tàu, nhưng chúng ta vẫn bảo trì chúng bằng nhật ký và trực giác."

**Text on screen (nhỏ, dưới):** nguồn VnEconomy 30/05/2025 · The Investor 20/03/2026 — *trích trong `docs/RAILOPS_VN_PLATFORM_BLUEPRINT.md` §7*.

---

### [0:55 – 1:25] SHOT 3 — ĐIỂM MÙ KỸ THUẬT: VÌ SAO NGƯỠNG TĨNH BÁC HỎI ĐƯỢC
**Hình:** chuyển vào **Screen 01 — Fleet Overview**. Breadcrumb đọc được: `RailOps VN — Metro Line 1 → TRAIN-302 → SUB-APU-01 → APU-COMP-01`.
**Thoại:**
> "Máy nén khí cấp khí cho ba thứ sống còn: phanh, treo khí, và cửa hành khách. Nó chạy ngắt theo tải — một phút đầy tải, phút sau nghỉ.
> Hệ thống ngưỡng tĩnh không phân biệt được hai trạng thái đó. Áp suất thấp lúc máy đang nghỉ là bình thường. Nên hoặc nó báo khi quá muộn, hoặc nó báo rầm lên cả trăm lần một tuần và người ta tắt nó đi.
> Chúng tôi bắt đầu bằng cách phân loại chế độ vận hành trước khi tính bất kỳ ngưỡng nào."

**Bấm:** mở một asset `HEALTHY` trong lưới để chứng minh lưới tới từ API, không phải ảnh chụp.

---

### [1:25 – 2:10] SHOT 4 — BẰNG CHỨNG SỐ, KHÔNG PHẢI ĐIỂM ANOMALY
**Hình:** case tới trạng thái `DETECTED/INVESTIGATING`. Mở **Workbench** (Screen 03–04). Chuột di chậm qua 4 thẻ bằng chứng, dừng ở khối provenance.
**Thoại:**
> "Bốn tín hiệu, mỗi tín hiệu mang theo xuất xứ của chính nó: áp suất van xả lệch bao nhiêu sigma so với đường cơ sở *trong cùng chế độ mang tải*, nhiệt độ dầu trôi theo hướng nào, bước nhảy có lặp lại trên tối thiểu ba chu kỳ mang tải liên tiếp hay không, và một Isolation Forest đa biến chạy song song để đối chiếu.
> Đây là chỗ chúng tôi cố tình khác phần còn lại: hệ thống không trả về một điểm anomaly rồi mong bạn tin nó. Nó trả về một bộ hồ sơ mà một kỹ sư có thể đọc, phản biện, và ký tên vào."

**Chèn chữ phụ góc phải:** *Mọi sigma tính trên dữ liệu MetroPT-3 thật — 1.516.948 điểm. Không một giá trị nào do phần mềm sinh ra.*

---

### [2:10 – 2:35] SHOT 5 — TÍNH CHỐNG BÁO ĐỘNG ẢO (đoạn này ghi điểm Sáng tạo)
**Hình:** kéo về mốc nhiễu loạn bằng **Replay Studio Drawer** (`Shift + S`).
**Thoại:**
> "Lúc 00:33:07 có một cú vọt áp suất sáu mươi lăm sigma. Ngưỡng tĩnh sẽ gọi đây là sự cố. Chúng tôi không.
> Vì nó không bền trên ba chu kỳ mang tải. Nó bị suppression, và — quan trọng hơn — nó được **ghi vào sổ cái**. Nếu sau này xảy ra chuyện, chúng tôi chứng minh được rằng hệ thống đã nhìn thấy nó và đã có lý do để không cắt tàu."

**Bấm:** `Shift + S` → bookmark mốc nhiễu → chỉ số `active_cases_count` vẫn bằng 0.

---

### [2:35 – 3:30] SHOT 6 — CON NGƯỜI QUYẾT ĐỊNH, MÁY CHẶN QUYẾT ĐỊNH LIỀU (trọng tâm)
**Hình:** **Right pane** của Workbench, Human-in-the-Loop rail. Quay chuột thật, không tua nhanh.
**Thoại + thao tác:**
> "Bốn bước. Con người làm, engine chỉ dẫn."
> 1. **Acknowledge & Triage** — bấm, chọn `P1-CRITICAL`, ghi danh tính điều độ viên.
> 2. **Forensic note** — gõ một câu thật, ví dụ: *"Pattern phù hợp rò gioăng van xả, không phải lỗi cảm biến."*
> 3. **Depot Work Order** — chọn playbook, depot nhận tàu (`DEPOT-LONGBINH-01`), cửa sổ bảo trì `NEXT_TERMINAL_STOP`.
> 4. **ActionGuard trước khi Safe Mode.**

**ĐÂY LÀ CÚ ĐÁNH CỦA CẢ VIDEO.** Trước khi đủ điều kiện, hãy bấm nút Safe Mode **một lần có chủ đích** để hàng rào từ chối:
> "Và đây là thứ chúng tôi muốn bạn chú ý nhất. Tôi vừa bấm nút xin kích hoạt Safe Mode, và hệ thống **từ chối** — năm cổng kiểm định, mới qua có mấy cổng, nó nói cho tôi biết cổng nào còn thiếu.
> Trong một ngành mà sai một lần là mất người, chúng tôi không cho tự động hóa quyền quyết định. Nhưng chúng tôi cũng **không cho phép con người hành động khi bằng chứng chưa đủ**. ActionGuard chặn cả hai chiều."

**Đừng:** để hệ thống tự chạy từ đầu đến cuối. Nếu UI tự nhảy trạng thái mà không có cú bấm nào, video mất giá trị.

---

### [3:30 – 4:05] SHOT 7 — ĐÓNG VÒNG: ĐÃ LÀNH THẬT CHƯA?
**Hình:** `MITIGATING → VERIFYING_RECOVERY → RESOLVED`, bảng đối chiếu 5 mẫu mang tải (Screen 06), rồi **Root-Cause Sign-Off** đóng case.
**Thoại:**
> "Sửa xong không phải là hết báo động. Hệ thống chỉ cho đóng hồ sơ khi năm lần quan sát **liên tiếp ở chế độ mang tải** đều đạt tiêu chí áp suất và nhiệt độ.
> Nếu bạn không chứng minh được thiết bị đã lành, bạn chưa được phép quên nó. Đây cũng chính là chỗ mà phần lớn công cụ dự báo dừng lại — chúng báo lỗi, rồi để bạn tự đoán xem đã sửa được chưa."

**Bấm:** Close case → `asset_health` trở về `HEALTHY`, tài sản được giải phóng.

---

### [4:05 – 4:30] SHOT 8 — NỀN TẢNG, KHÔNG PHẢI MỘT DASHBOARD
**Hình:** `GET /api/telemetry/window` trên Console + vẽ nhanh MongoDB Compass/Atlas Time Series + Datadog dashboard & trace.
**Thoại:**
> "Phía dưới là một kiến trúc doanh nghiệp. Điểm đo vào MongoDB Time Series, thống kê cửa trượt tính ngay trong database bằng `$setWindowFields` phân vùng theo chế độ mang tải. Hồ sơ sự kiện và sổ cái kiểm toán là document — thêm một phân hệ mới không phải sửa schema.
> Còn Datadog giám sát **chính hệ thống đang giám sát đoàn tàu**: mỗi khung dữ liệu là một chuỗi span, nên khi pipeline chậm, tôi thấy ngay span nào chậm. MongoDB để hiểu con tàu. Datadog để hiểu hệ thống đang hiểu con tàu."

**Bấm:** chuyển sang tab Datadog dashboard, hover một trace.

---

### [4:30 – 4:50] SHOT 9 — MODULE IoT: CÓ GẮN ĐƯỢC NGOÀI THỰC ĐỊA KHÔNG?
**Hình:** sơ đồ `CAN/MVB/TCMS → Edge Gateway → MQTT → Ingest → MongoDB`.
**Thoại:**
> "Và đây là câu hỏi quyết định với một nhà khai thác: bạn có phải dừng tàu để gắn cảm biến không? Không.
> Áp suất bình chính, nhiệt độ dầu, dòng động cơ — đầu tàu metro hiện đại **đã có sẵn**, đang chạy trên bus của hệ thống điều khiển tàu._phase 1_ chỉ là một bản sao read-only từ TCMS, không đụng vào mạch điều khiển, nên không cần phê duyệt an toàn chạy tàu.
> Trong hầm thì gateway store-and-forward, và vì mọi điểm đo mang theo `event_time` vật lý của riêng nó, phát lại là xác định — bạn replay đúng sự cố cho thanh tra xem."

---

### [4:50 – 5:00] SHOT 10 — ASK
**Hình:** quay lại Screen 01, KPI `Lead Window: 33h 52m`.
**Thoại:**
> "RailOps VN là nền tảng; CompressorGuard là phân hệ lõi sống còn mà chúng tôi đã chạy trọn đường hôm nay. Cho chúng tôi sáu tháng và hai đầu tàu, và đến khi đường sắt tốc độ cao Bắc – Nam chọn nhà thầu, giám sát trạng thái đã là mặc định thay vì đi retrofit."

**End card:** `RailOps VN — CompressorGuard · MongoDB × Datadog · MUGVN Hackathon 2026` + link repo.

---

## 3. Bảng ánh xạ đoạn video → tiêu chí chấm

| Shot | Thời lượng | Tiêu chí nó nuôi | Bằng chứng xuất hiện trên hình |
|:---|:---|:---|:---|
| 1–2 | 0:55 | **Tác động 30%** | 33h52m; ba dẫn chứng đường sắt VN có nguồn |
| 3 | 0:30 | **Sáng tạo 30%** | regime-aware, breadcrumb từ API |
| 4 | 0:45 | **Sáng tạo + Kỹ thuật** | 4 thẻ bằng chứng + provenance |
| 5 | 0:25 | **Sáng tạo 30%** | 65σ suppressed, vẫn có sổ cái |
| 6 | 0:55 | **Sáng tạo + Trình bày** | 4 bước HITL + ActionGuard **từ chối thật (HTTP 409)** |
| 7 | 0:35 | **Kỹ thuật 30%** | 5/5 mẫu mang tải đạt chuẩn, sign-off |
| 8 | 0:25 | **Kỹ thuật 30%** | `$setWindowFields`, Time Series, APM trace |
| 9 | 0:20 | **Tác động 30%** | tap TCMS, không gắn sensor, deterministic replay |
| 10 | 0:10 | **Trình bày 10%** | recap + ask |

---

## 4. Năm lỗi sẽ khiến video bị nhìn là "demo đồ chơi" — tuyệt đối tránh

1. **Tua nhanh hoặc cắt bỏ đoạn chờ.** Nỗi tự hào của sản phẩm là *khoảng thời gian chờ có kiểm soát*. Nếu cần tiết kiệm thời lượng, tua phần dữ liệu chạy nền, **không** tua các cú bấm của operator.
2. **Nút Safe Mode xanh và tự bấm thành công ngay lần đầu.** Phải cho BGK thấy lần bị từ chối. Đó là bằng chứng hệ thống có chính sách, không có kịch bản.
3. **Số liệu trên header đổi mà không có request mạng nào.** Nghĩa là hardcode. Trước khi quay, mở Network tab và bảo đảm mọi chỉ số có nguồn.
4. **Không có mặt người vận hành trong luồng.** Hệ thống phải trông như một công cụ của một ca trực có tên, có danh tính (`DISPATCHER-0941`), không như một đoạn animation.
5. **Giọng thuyết trình "chúng em đã xây dựng".** Nói như một CTO đang báo cáo quyết toán rủi ro: vấn đề, cơ chế, bằng chứng, chi phí nếu không làm.

---

## 5. Lời thoại cấm dùng & cách nói thay

| ❌ Đừng nói | ✅ Nói thay |
|:---|:---|
| "AI dự đoán lỗi chính xác 99%" | "Chúng tôi không bán độ chính xác, chúng tôi bán thời gian để quyết định." |
| "Hệ thống tự động dừng tàu" | "Engine đề xuất, con người ký, và hàng rào chặn cả người khi bằng chứng chưa đủ." |
| "Dữ liệu mô phỏng của chúng tôi rất thực" | "Đây là 1.516.948 điểm đo thật từ dataset công bố MetroPT-3. Đây là dataset Lisbon — và đó chính xác là lý do bước pilot là thay nó bằng TCMS Việt Nam, engine giữ nguyên." |
| "Có thể mở rộng dễ dàng" | "Cấu hình lại `signal_pack` và playbook là ra phân hệ mới, không sửa engine." |

---

## 6. Bản cắt 2:30 (nếu BTC giới hạn thời lượng)

| Thời gian | Nội dung | Shot gốc |
|:---|:---|:---|
| 0:00–0:15 | 33h52m + một câu rủi ro phanh | 1 |
| 0:15–0:30 | 1 dẫn chứng VN (Yên Nghĩa / ĐSCT Bắc–Nam) | 2 |
| 0:30–0:50 | 4 thẻ bằng chứng + provenance | 4 |
| 0:50–1:30 | HITL 4 bước **và cú ActionGuard từ chối** | 6 |
| 1:30–1:55 | Recovery 5/5 + đóng case | 7 |
| 1:55–2:15 | MongoDB `$setWindowFields` + Datadog trace | 8 |
| 2:15–2:30 | Tap TCMS không gắn sensor + ask | 9, 10 |

---

## 7. Hậu kỳ & nộp bài

- **Phụ đề:** burn-in tiếng Việt, font hệ giao diện, không tự động của YouTube.
- **Nhãn minh bạch phải hiện suốt video** ở góc: `LIVE SIMULATION · HISTORICAL DATA (MetroPT-3)`.
- **Kiểm tra lần cuối trước khi upload:** chạy `python scripts/verify_evaluation_gates.py` và bảo đảm cả 5 gate PASS; số liệu bạn vừa nói trong video phải khớp với số gate in ra. Nếu lệch, sửa lời thoại chứ không sửa con số.
- **Bộ artifact nộp:** (1) repository, (2) file video này + link, (3) `docs/railops-vn-final-deck.pptx`, (4) tài liệu: `docs/RAILOPS_VN_PLATFORM_BLUEPRINT.md`, `docs/PITCH_DECK_AND_DEMO_RUNBOOK.md`.
