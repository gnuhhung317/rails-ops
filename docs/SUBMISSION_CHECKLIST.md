# SUBMISSION CHECKLIST — MUGVN Hackathon 2026
### RailOps VN / CompressorGuard · deadline **2026-11-08 23:59**

> Dùng để bảo đảm **không thiếu artifact nào khi nộp** và để biết chính xác còn việc gì.
> Cột "Bằng chứng" là thứ phải mở được ra trong vòng 60 giây, không phải mô tả.

## 1. Artifact bắt buộc theo thể lệ

> **Cách nộp:** điền link repo + video + upload file tại **https://forms.gle/7JHbcihzVA3uGTPw6** trước **2026-11-08 23:59**.
> **Số thành viên:** 1–3 (kiểm tra danh sách thành viên khai trên form khớp với repo).

| # | Artifact (theo BTC) | Trạng thái | Bằng chứng / đường dẫn | Còn phải làm |
|:-:|:---|:---:|:---|:---|
| 1 | **Repository mã nguồn** | 🔴 | 49 commit local trên branch `feature/temporal-correctness-and-scenario-validation` (đếm bằng `git rev-list --count HEAD`; số này tăng mỗi lần commit) | **CHƯA CÓ REMOTE NÀO** (`git remote -v` rỗng) — repo mới tồn tại trên máy này. Phải tạo repo + push, rồi mở thử bằng trình duyệt ẩn danh để chắc người chấm vào được. |
| 2 | **Video demo** | 🟡 | `docs/DEMO_VIDEO_SCRIPT.md` (10 shot, 5:00 + bản cắt 2:30) | **QUAY THẬT** sau khi console chạy ổn. Đây là mục dễ trượt nhất. |
| 3 | **Slide thuyết trình chung kết** | ✅ | `docs/railops-vn-final-deck.pptx` — 12 slide, sinh lại bằng `python scripts/build_pitch_deck.py`; bản nộp không font-dependency: `docs/railops-vn-final-deck.pdf` | **Đã render thật từng slide qua PowerPoint 16 và xem bằng mắt 12/12 trang** (không suy luận bằng hình học): không tràn lề, không lỗi font tiếng Việt, không ký tự lạ. Phát hiện và sửa 1 lỗi sinh file: nhánh `("t", …)` trong `bullets()` tạo textbox rồi `pass`, **nuốt silently 4 dòng nội dung** — gồm dòng ánh xạ rubric 30/30/30/10 ở slide 12, dòng tech stack ở slide 5, dòng Phase 2–4 và dòng retrofit Layer C ở slide 8. Speaker notes vẫn nhúng đủ 12/12. Mở Presenter View, bấm giờ 1 lần cho đúng 3 phút. |
| 4 | **README** | ✅ | `README.md` — bài toán, kiến trúc, quickstart 2 lệnh, bảng 5 evaluation gates, mục "Operator journey against a live server" | Đối chiếu lại một lần cuối sau khi đổi branding RailOps VN |

## 2. Yêu cầu kỹ thuật bắt buộc của đề bài

| Yêu cầu | Trạng thái | Bằng chứng mở được ngay |
|:---|:---:|:---|
| **MongoDB làm nền tảng dữ liệu** | ✅ | `src/storage/repository.py`, `src/storage/mongo_client.py` — Time Series `measurements`, `$setWindowFields`, TTL. Cần `MONGODB_URI` để thấy Compass. |
| **Datadog: quan sát – phát hiện – xử lý** | ✅ | `datadog/dashboard.json` (6 widget), `datadog/monitors.json`, `src/observability/metrics.py` (DogStatsD + APM traces). Cần agent `:8125/:8126`. |
| **Cài được từ clone sạch** | ✅ | `requirements.txt` — pin đúng bộ đã chạy trên Python 3.12.4; `python -m pip install --dry-run -r requirements.txt` resolve sạch. `run_demo.py` giờ **dừng ngay** và in lệnh cài nếu thiếu package (đã test cả 2 nhánh). |
| **Mô đun IoT** | ✅ | `scripts/stream_telemetry.py` — producer CLI tách rời, MQTT edge topic `railops/metro-line-1/APU-COMP-01/telemetry`, QoS 1, store-and-forward buffer. Đã kiểm chứng bằng `pytest tests/test_edge_publisher.py` (5 passed): buffer có trần, đúng topic, drain khi có client, và **không crash khi broker chết** (paho-mqtt 1.6.1 thật, port đóng). Giới hạn nói thật: **chưa có round-trip với broker thật** vì máy này không có mosquitto — ai muốn thấy thì `pip install paho-mqtt`, chạy một broker bất kỳ rồi set `MQTT_BROKER=tcp://host:1883`. |
| **Realtime** | ✅ | Background Stream Worker trong `src/api/app.py` + CLI producer; dashboard là consumer thuần túy, không `setInterval` kéo `/demo/tick`. |
| **Dữ liệu thật, zero fake** | ✅ | `1,516,948` rows MetroPT-3; in ra bởi Gate 1 khi chạy `scripts/verify_evaluation_gates.py`. |

## 3. Chuỗi vận hành phải trọn vẹn (luận điểm cốt lõi)

| Bước | Bằng chứng | Lệnh / thao tác mở chứng minh |
|:---|:---|:---|
| **Phát hiện sớm 33h 52m** | `lead_time.lead_time_formatted` | `curl -s localhost:8000/api/incident` |
| **Bằng chứng số `$setWindowFields`** | `evidence_pack[].provenance`, rolling stats | `curl -s localhost:8000/api/evidence` |
| **Can thiệp an toàn ActionGuard 5/5** | `checklist[5]`, `is_permitted`, `denial_reason` | `curl -s "localhost:8000/api/action/guard-status?operator_id=DISPATCHER-0941"` — và bấm Safe Mode **muộn** để thấy HTTP 409 |
| **Kiểm chứng phục hồi** | `consecutive_healthy_observations`/`target` | `curl -s localhost:8000/api/recovery` |
| **Sổ cái kiểm toán** | `case_events` có actor + source + provenance | `curl -s localhost:8000/api/case/events` |

## 4. Cửa nghiệm thu tự động (chạy trước khi bấm nộp)

```bash
# 5 evaluation gates — KHÔNG phải pytest trần, theo quy tắc AGENTS.md
python scripts/verify_evaluation_gates.py       # kỳ vọng: ALL 5 GATES PASSED

# Bằng chứng golden path xuất file
python scripts/verify_golden_path_evidence.py

# Producer độc lập chạy thật
python scripts/stream_telemetry.py --scenario failure_3 --speed 300 --hours 1

# Console bật được
python run_demo.py                               # http://localhost:8000/console

# Toàn bộ hành trình Operator đi qua API thật, 23 khẳng định tự động
# (server phải đang chạy; endpoint 409 Safe Mode sớm là một phần của test)
CONSOLE_BASE_URL=http://localhost:8000 python scripts/verify_console_journey.py
```

Kết quả gate gần nhất: **G1–G5 PASSED**, `ReplayEngine loaded 1,516,948 rows`
(thời điểm chạy: 2026-11-06 17:19 UTC). Datadog agent không chạy trên máy dev nên
trace bị drop kèm warning — đó là hành vi chấp nhận được, nhưng **khi quay video
phải có agent** hoặc nói rõ là đang tắt.

Kết quả journey gần nhất (`verify_console_journey.py`): **23/23 PASSED**
(2026-11-06 17:37 UTC, chạy lại 17:54 UTC sau khi sửa docs/launcher/tests — vẫn 23/23) — trong đó `lead_time = 33h 52m`, `4 evidence cards`,
ActionGuard `5/5`, recovery `5/5 healthy LOADED`, `state=RESOLVED / health=HEALTHY`,
ledger `10 events`, và Safe Mode sớm bị từ chối bằng **HTTP 409**.
Console v3.0 chạy thật trên trình duyệt: 6 Chart.js canvases, 42 node bind,
**0 binding trống**, **0 lỗi console**, bookmark/Play/Pause hoạt động bằng chuột.

## 5. Việc còn lại, xếp theo độ rủi ro khi hết giờ

| Ưu tiên | Việc | Vì sao rủi ro |
|:-:|:---|:---|
| **P0** | Tạo repo hosted + push, rồi mở bằng trình duyệt ẩn danh | `git remote -v` đang **rỗng** — toàn bộ 49 commit chỉ tồn tại trên máy này. Repo nộp không mở được = mất điểm Kỹ thuật. Lệnh sẵn ở §5.1. |
| **P0** | Quay + dựng video demo (5:00) | Artifact bắt buộc, tốn thời gian nhất, dễ trễ nhất; console đã xanh (23/23) nên chỉ còn thiếu file ghi hình. Kịch bản 10 shot ở `docs/DEMO_VIDEO_SCRIPT.md`. |
| ~~P0~~ | ~~Chạy thật console v3.0, bấm trọn 4 bước Human-in-the-Loop~~ **XONG 2026-11-06 17:37 UTC · chạy lại 17:54 UTC vẫn 23/23 sau toàn bộ sửa đổi docs/launcher/tests** | `verify_console_journey.py` 23/23 + trình duyệt thật 0 lỗi console |
| ~~P1~~ | ~~Chốt deck 12 slide~~ **XONG — 12/12 slide đã render thật qua PowerPoint và xem bằng mắt, PDF nộp đã commit** | Còn lại duy nhất: **tập nói 3 phút** trong Presenter View (speaker notes đã nhúng sẵn từng slide, mốc 0:00→3:00). |
| **P1** | Điền form `forms.gle/7JHbcihzVA3uGTPw6` trước **2026-11-08 23:59** | Hết hạn là mất quyền nộp, không có gia hạn. |
| **P2** | Bật MongoDB Atlas + Datadog agent thật khi quay | "Doanh nghiệp" hay "bài tập lớn" phân nhau ở chỗ này |
| **P2** | Đọc lại `docs/DEMO_VIDEO_SCRIPT.md` §4 — 5 lỗi biến sản phẩm thành đồ chơi | Mất 10% Trình bày rất dễ, lấy lại rất khó |

### 5.1 Lệnh push — chỉ cần máy có tài khoản GitHub (việc của chủ repo)

```bash
# 1) Tạo repo PUBLIC trên GitHub bằng tay (không dùng gh CLI vì máy này không cài gh):
#    github.com/new -> tên "railops-vn" hoặc "iot-hackathon" -> Public -> Create
#    KHÔNG tick "add a README" (sẽ xung đột lịch sử 49 commit đang có).

# 2) Gắn remote và push đúng branch đang nộp:
git remote add origin git@github.com:<user>/railops-vn.git
git push -u origin feature/temporal-correctness-and-scenario-validation

# 3) Kiểm tra bằng chứng BGK vào được: mở đường dẫn ở trình duyệt ẩn danh.
#    Trang repo phải hiện README, dataset/ phải trống (CSV 145MB đã gitignore),
#    và file docs/railops-vn-final-deck.pdf phải tải được không cần đăng nhập.
```

**Không** push `dataset/MetroPT3(AirCompressor).csv` hay `metropt+3+dataset.zip` — cả hai nằm
trong `.gitignore`; README đã ghi rõ DOI và đường dẫn tải thủ công.

## 6. Câu chốt khi BGK hỏi "ý tưởng triển khai là gì?"

> Metro Line 1 và Cát Linh – Hà Đông đã có sẵn áp suất bình chính, nhiệt độ dầu và
> dòng động cơ trên bus điều khiển của tàu. Phase 1 chỉ là một bản sao **read-only**
> từ TCMS — không gắn cảm biến, không đụng mạch điều khiển, không cần phê duyệt an
> toàn chạy tàu. Engine không đổi một dòng khi thay dữ liệu Lisbon bằng dữ liệu Việt
> Nam. Đó là lý do chúng tôi xin **sáu tháng và hai đầu tàu**, chứ không xin một
> project pilot mười tám tháng.
