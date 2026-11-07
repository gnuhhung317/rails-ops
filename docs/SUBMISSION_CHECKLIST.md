# SUBMISSION CHECKLIST — MUGVN Hackathon 2026
### RailOps VN / CompressorGuard · deadline **2026-11-08 23:59**

> Dùng để bảo đảm **không thiếu artifact nào khi nộp** và để biết chính xác còn việc gì.
> Cột "Bằng chứng" là thứ phải mở được ra trong vòng 60 giây, không phải mô tả.

## 1. Artifact bắt buộc theo thể lệ

> **Cách nộp:** điền link repo + video + upload file tại **https://forms.gle/7JHbcihzVA3uGTPw6** trước **2026-11-08 23:59**.
> **Số thành viên:** 1–3 (kiểm tra danh sách thành viên khai trên form khớp với repo).

| # | Artifact (theo BTC) | Trạng thái | Bằng chứng / đường dẫn | Còn phải làm |
|:-:|:---|:---:|:---|:---|
| 1 | **Repository mã nguồn** | 🟡 *(mới — trước đây 🔴 "chưa có remote")* | `git@github.com:gnuhhung317/rails-ops.git`, HEAD `94e7585`. `master` được fast-forward bằng `git update-ref refs/heads/master HEAD` (kiểm tra `git merge-base --is-ancestor master HEAD` trước — không merge commit, không rewrite). Đã push cả `master` và `feature/temporal-correctness-and-scenario-validation`. **Quét secret trên TOÀN BỘ history** (`git log --all -p \| grep -c`): 0 lần xuất hiện mật khẩu Atlas, 0 lần API key Datadog, `.env` chưa từng bị track. Blob lớn nhất từng commit: slice 39 MB (không phải file 208 MB). **Còn mở:** repo đang **PRIVATE** — `curl https://github.com/gnuhhhung317/rails-ops` trả **404** và `git ls-remote` vô danh báo "Repository not found" y như repo không tồn tại. Người chấm không vào được cho tới khi chuyển Public (Settings → General → Danger Zone) hoặc thêm người chấm làm collaborator. Đây là cổ chai duy nhất còn lại và nằm phía người dùng. |
| 2 | **Video demo** | 🟡 | `docs/DEMO_VIDEO_SCRIPT.md` (10 shot, 5:00 + bản cắt 2:30) | **QUAY THẬT** sau khi console chạy ổn. Đây là mục dễ trượt nhất. |
| 3 | **Slide thuyết trình chung kết** | ✅ | `docs/railops-vn-final-deck.pptx` — 12 slide, sinh lại bằng `python scripts/build_pitch_deck.py`; bản nộp không font-dependency: `docs/railops-vn-final-deck.pdf` | **Đã render thật từng slide qua PowerPoint 16 và xem bằng mắt 12/12 trang** (không suy luận bằng hình học): không tràn lề, không lỗi font tiếng Việt, không ký tự lạ. Phát hiện và sửa 1 lỗi sinh file: nhánh `("t", …)` trong `bullets()` tạo textbox rồi `pass`, **nuốt silently 4 dòng nội dung** — gồm dòng ánh xạ rubric 30/30/30/10 ở slide 12, dòng tech stack ở slide 5, dòng Phase 2–4 và dòng retrofit Layer C ở slide 8. Speaker notes vẫn nhúng đủ 12/12. Mở Presenter View, bấm giờ 1 lần cho đúng 3 phút. |
| 4 | **README** | ✅ | `README.md` — bài toán, kiến trúc, quickstart 2 lệnh, bảng 5 evaluation gates, mục "Operator journey against a live server" | Đối chiếu lại một lần cuối sau khi đổi branding RailOps VN |

## 2. Yêu cầu kỹ thuật bắt buộc của đề bài

| Yêu cầu | Trạng thái | Bằng chứng mở được ngay |
|:---|:---:|:---|
| **MongoDB làm nền tảng dữ liệu** | ✅ | `src/storage/repository.py`, `src/storage/mongo_client.py` — Time Series `measurements`, `$setWindowFields`, TTL. **Đã chạy chống lại `mongod` THẬT: 16/16 check PASS trên MongoDB Atlas (mongod 8.0.37), dữ liệu nạp từ file CSV đầy đủ 1.516.948 dòng**, lệnh: `MONGODB_URI=<atlas+srv> MONGODB_DB_NAME=compressorguard_verify python scripts/verify_mongodb_timeseries.py`. Số liệu thật từ run: 726 document → **2 bucket vật lý** (363 docs/bucket, 24 KiB), `timeField=timestamp metaField=metadata granularity=seconds`, rolling avg/std khớp phép tính pandas độc lập với sai số **8.9e-16 / 5.3e-16**, cửa sổ server thấy = 61 sample (median 10 s), duty cycle `92.98% = 92.98%`, peak `2.754 = 2.754`, 0 dòng không khớp timestamp, 0 TTL trên `timestamp` (dữ liệu 2020 sống), 1 TTL `expireAfterSeconds=604800` trên `anomaly_signals.ingested_at`, explain plan là stage thật chứ không phải emulator. **Ba lỗi trong chính script verify bị lộ ở run đầu tiên và đã sửa:** (1) `collstats` trên Time Series *view* không trả `bucketCount`/`count` trên mongod 8.0/Atlas (về `None`, script cũ biến `None` thành `0` → FAIL giả), giờ đếm document trong `system.buckets.measurements`; (2) thiếu `.mean()` sau `.rolling()` nên lấy object `Rolling` trừ `Series` → crash; (3) gọi `client.server_info()` sau khi `client.close()` → crash dòng tổng kết. Run đầu tiên là 12 PASS / 1 FAIL / 1 crash — không phải sản phẩm sai, mà là bằng chứng chưa từng được chạy thật. Time Series chạy được trên shared tier của Atlas, nên không cần Docker/máy remote cho chân này. **Không chỉ verifier — chính APP ghi xuống Atlas:** console journey 23/23 chạy chống lại server thật trên Atlas, và số liệu kiểm tra trực tiếp trong DB sau run xác nhận ledger append-only hoạt động (`case_events` **10 → 20**, `measurements` 247, `operational_cases` 1 đúng `APU-INC-20200605-01`). Bằng chứng mạnh hơn vừa có: journey **23/23** chạy từ **bản clone GitHub** ghi xuống database Atlas **riêng** `compressorguard_clonecheck` (`measurements` 247, `operational_cases` 1, `case_events` 10 với `EVT-010 / CASE_CLOSED` mới nhất, `anomaly_signals` 2) — emulator in-memory **không thể tạo database trên cluster từ xa**, nên sự tồn tại của database mới là bằng chứng, không phải exit code. Kèm bài học kiểm chứng: query đầu tiên đọc **nhầm database** vì `. .env` re-export `MONGODB_DB_NAME=compressorguard` và trả `case_events 20` — số liệu của phiên trước; phải đặt cả hai DB cạnh nhau (clonecheck 10, default 20) và so ObjectId (`6aeeb61f…` mới hơn `6aee9c15…`) mới kết luận được. `run_demo.py` giờ tự công bố backend ngay ở preflight (`[OK] Storage backend: REAL MongoDB Atlas v8.0.37, database=compressorguard.` / `[WARN] Storage backend: IN-MEMORY EMULATION … do not present this run as MongoDB evidence.`), vì trước đây hai chế độ nhìn y hệt nhau — chính sự im lặng đó đã suýt làm tôi nhận vơ một run 23/23 chạy trên emulator. **Run compose còn cho thêm một server thật thứ hai:** `docker compose up -d --build console` + journey **23/23** chống lại **mongod 7.0.45** tự chứa (không cần cloud), kiểm tra thẳng trong container: `getCollectionInfos` trả `type: 'timeseries'`, `timeField: timestamp metaField: metadata granularity: seconds bucketMaxSpanSeconds: 3600`, `measurements` 247 / `case_events` 10 / `operational_cases` 1. |
| **Datadog: quan sát – phát hiện – xử lý** | ✅ | `datadog/dashboard.json` (8 widget), `datadog/monitors.json` (3 metric alert), `src/observability/metrics.py` (15 DogStatsD gauges/counters + APM traces). **Hợp đồng config↔code đã được test** bằng `pytest tests/test_datadog_config_contract.py` (5 passed): mọi metric tên trong dashboard/monitors phải có thật trong code, query APM phải khớp span thật, và bộ lọc `env:` phải khớp tag tracer gán. **Đã chạy agent THẬT (agent 7.85.2, `registry.datadoghq.com/agent:7`) trên VM và nhận số liệu sống**, không còn là claim trên giấy: `agent status` báo **3.246 DogStatsD metric packets / 0 parse errors**, `Series Flushed` tăng theo từng flush, toàn bộ endpoint `https://*.ap2.datadoghq.com` (kể cả `api/v1/validate`) trả `success`, và `agent dogstatsd-stats` **liệt kê đúng tên metric của project** với tag khớp bộ lọc dashboard: `compressorguard.telemetry.dv_pressure_bar \| asset_id:APU-COMP-01 regime:LOADED service:compressorguard env:hackathon-2026 fleet_id:FLEET-METRO-01 train_id:TRAIN-302`, tương tự `ml.anomaly_score`, `ml.inference_latency_ms`, `ml.physics_agreement`, `incident.lead_time_seconds`, `recovery.consecutive_observations`. **APM cũng nhận span thật:** `datadog.trace_agent.receiver.serve_traces_ms … service:compressorguard success:true` (tracer 4.15.6, CPython 3.12.16). Cách tái hiện: `docker compose up -d --build agent mosquitto console` rồi `docker compose exec -T console python scripts/verify_console_journey.py`. **Còn thiếu (phía người dùng, không phải code):** screenshot/quote dashboard thật từ UI để nhét vào video — cần đăng nhập `app.ap2.datadoghq.com`; CLI không query được `/api/v1/series` vì endpoint đó cần Application Key, mà phiên này chỉ có API Key. |
| **Cài được từ clone sạch** | ✅ *(mới sửa — trước đây SAI)* | `requirements.txt` pin đúng bộ đã chạy trên Python 3.12.4; `pip install --dry-run -r requirements.txt` resolve sạch; `run_demo.py` dừng ngay và in lệnh cài nếu thiếu package. **Lỗi nghiêm trọng vừa tìm ra và sửa:** file CSV 208 MB bị gitignore, nên `git clone` thuần **không còn dữ liệu nào** — người chấm không chạy được gì. Từ phiên này repo commit `dataset/MetroPT3-demo-slice.csv` (286,855 dòng MetroPT-3 THẬT, 39.5 MB, sinh bởi `scripts/build_demo_slice.py`): đủ tháng nền Isolation-Forest (2/2020) + mọi cửa sổ scenario ở đúng nhịp 10 s. Bằng chứng đã nghiệm thu trên máy này: (1) artifact `docs/golden_path_evidence_artifact.json` sinh từ slice **giống từng byte** so với sinh từ file 1,5 triệu dòng; (2) console boots trên slice và journey **23/23 assertions PASS**; (3) `pytest tests/test_dataset_resolution.py` (4 passed) chốt lại không tái phạm.Đã thử stride=3 trước khi commit: nó **đổi verdict ML** (`is_anomalous: true → false`) nên bị loại — baseline để nguyên độ phân giải. **Nâng bằng chứng lên đúng thứ người chấm sẽ làm:** SSH-clone từ GitHub về `/tmp/gh-clone` (lần đầu dùng HTTPS bị "Repository not found" vì repo private — đó là dấu hiệu quyền truy cập, không phải lỗi push), kiểm tra `dataset/` trong clone chỉ có `Data Description_Metro.pdf` + `MetroPT3-demo-slice.csv` (41.468.972 byte), **không** có file 208 MB, **không** có `.env`; rồi chạy **trong chính bản clone đó với mọi biến môi trường bị unset**: `Data source: MetroPT3-demo-slice.csv`, `ReplayEngine loaded 286,855 rows`, Gates 1–5 `[PASS]`, `ALL 5 EVALUATION GATES PASSED WITH ZERO REGRESSION`, và console journey **23/23** chống lại server Atlas khởi động từ clone. |
| **Mô đun IoT** | ✅ | `scripts/stream_telemetry.py` — producer CLI tách rời, MQTT edge topic `railops/metro-line-1/APU-COMP-01/telemetry`, QoS 1, store-and-forward buffer. Đã kiểm chứng bằng `pytest tests/test_edge_publisher.py` (**8 passed**, trước là 5): buffer có trần, đúng topic, drain khi có client, **không crash khi broker chết** (paho-mqtt 1.6.1 thật, port đóng). **Round-trip với broker THẬT đã có** (eclipse-mosquitto:2 trong compose): producer `[EDGE] Connected to MQTT broker mosquitto:1883`, `mqtt_published=4`, và `mosquitto_sub -t "railops/#" -v` nhận đúng 4 frame JSON MetroPT-3 thật. **Nghiêm trọng: chính run đầu tiên này lộ ra rằng producer chưa từng ghi được xuống MongoDB.** Nó insert nguyên payload của bus vào `measurements` — mà `measurements` là Time Series collection có `timeField: timestamp` — nên mongod từ chối bằng `BulkWriteError code 2: "'timestamp' must be present and contain a valid BSON UTC datetime value"` và producer chết giữa dòng. Emulator in-memory **không hề phản đối**, nên bug này sống sót qua toàn bộ test suite và chỉ hiện ra khi có server thật; tài liệu còn thiếu luôn cả `metadata` (metaField) nên document dù ghi được vẫn vô hình với `$setWindowFields`. Đã sửa: tách `_frame_from()` (payload JSON, bắt buộc serialisable) khỏi `_doc_from()` (document lưu trữ, `timestamp` là datetime + `metadata`), nghiệm thu bằng cách query thẳng Atlas: 4 doc `metadata.source: "edge-producer"`, `timestamp` type `datetime` = `2020-06-05 09:40:05`, và aggregate `$setWindowFields partitionBy:$metadata.asset_id` tính ra `avg_dv` trên đúng các doc đó. |
| **Realtime** | ✅ | Background Stream Worker trong `src/api/app.py` + CLI producer; dashboard là consumer thuần túy, không `setInterval` kéo `/demo/tick`. |
| **Dữ liệu thật, zero fake** | ✅ | File gốc: `1,516,948` rows MetroPT-3 (in ra bởi Gate 1 khi đủ file). Slice commit trong repo: `286,855` rows **cùng instrument, cùng cột, không dòng nào tự sinh** — Gate 1 in số dòng của file đang nạp, không cố định con số. |

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
(thời điểm chạy: 2026-11-06 17:19 UTC). Từ 2026-11-07, **Datadog agent đã chạy thật** (trên VM,
qua `docker compose up -d --build agent mosquitto console`) nên đường trace/metric không còn bị drop
khi nghiệm thu; trên máy dev không agent thì hành vi vẫn là drop kèm warning — khi quay video cứ bật
agent hoặc nói rõ là đang tắt.

Kết quả journey gần nhất (`verify_console_journey.py`): **23/23 PASSED**
(2026-11-06 17:37 UTC, chạy lại 17:54 UTC sau khi sửa docs/launcher/tests — vẫn 23/23) — trong đó `lead_time = 33h 52m`, `4 evidence cards`,
ActionGuard `5/5`, recovery `5/5 healthy LOADED`, `state=RESOLVED / health=HEALTHY`,
ledger `10 events`, và Safe Mode sớm bị từ chối bằng **HTTP 409**.
Console v3.0 chạy thật trên trình duyệt: 6 Chart.js canvases, 42 node bind,
**0 binding trống**, **0 lỗi console**, bookmark/Play/Pause hoạt động bằng chuột.

**Chạy lại gần nhất — và là lần có ý nghĩa nhất (2026-11-07 05:23 UTC):** toàn bộ chuỗi trên được chạy
**trong một bản SSH-clone từ GitHub về `/tmp/gh-clone`, với mọi biến môi trường bị unset**.
`Data source: MetroPT3-demo-slice.csv`, `ReplayEngine loaded 286,855 rows`, G1–G5 PASSED, journey
**23/23**, ledger **10 events**, và app ghi xuống database Atlas riêng `compressorguard_clonecheck`.
Đây là chính xác những gì máy người chấm sẽ làm — khác với các lần chạy trước, vốn diễn ra trên working
tree của tôi (nơi có file CSV 208 MB và `.env` mà bản clone không có).

Hai chân từng được khai là "chưa chứng minh" **đã được chứng minh trong phiên này** (xem chi tiết ở §2):
(i) **Datadog agent sống** — agent 7.85.2 chạy thật, `dogstatsd-stats` liệt kê đúng tên metric
`compressorguard.*` với tag `env:hackathon-2026`, APM receiver báo `success:true`; (ii) **MQTT round-trip
với broker thật** — eclipse-mosquitto:2 nhận 4 frame từ producer độc lập. Cái giá phải trả cho việc chạy
thật là **một bug thật**: `scripts/stream_telemetry.py` ghi nhầm payload MQTT xuống Time Series collection
nên bị mongod từ chối từ đầu (chỉ có server thật mới lộ ra). Bài học ghi thẳng vào §2 để không tái phạm:
emulator không phải là bằng chứng.
Còn lại duy nhất phía công cụ: `docker context remote-vm` vẫn hỏng vì IP đổi — lệnh đúng là
`gcloud compute config-ssh --quiet` (lệnh này thêm Host entry vào `~/.ssh/config`; ở máy này có sẵn
một khối `Host test-2g2c...` cũ trỏ IP cũ **đứng trước** nên SSH vẫn resolve sai — đã né bằng
`gcloud compute ssh`/`scp`, chưa động vào config của người dùng).

## 5. Việc còn lại, xếp theo độ rủi ro khi hết giờ

| Ưu tiên | Việc | Vì sao rủi ro |
|:-:|:---|:---|
| ~~P0~~ | ~~Tạo repo hosted + push~~ **XONG một nửa: đã push `git@github.com:gnuhhung317/rails-ops.git` @ `94e7585` (master + branch), secret scan 0 hit, clone-GitHub đã chạy thật 5 gates + journey 23/23 + ghi Atlas.** | **Còn đúng một thao tác phía chủ repo: chuyển repo từ Private → Public.** Bằng chứng nó đang chặn người chấm: `curl https://github.com/gnuhhhung317/rails-ops` → **404**, `git ls-remote` vô danh → "Repository not found". Với BGK, repo private không khác gì repo không tồn tại. |
| **P0** | Quay + dựng video demo (5:00) | Artifact bắt buộc, tốn thời gian nhất, dễ trễ nhất; console đã xanh (23/23) nên chỉ còn thiếu file ghi hình. Kịch bản 10 shot ở `docs/DEMO_VIDEO_SCRIPT.md`. |
| ~~P0~~ | ~~Chạy thật console v3.0, bấm trọn 4 bước Human-in-the-Loop~~ **XONG 2026-11-06 17:37 UTC · chạy lại 17:54 UTC vẫn 23/23 sau toàn bộ sửa đổi docs/launcher/tests** | `verify_console_journey.py` 23/23 + trình duyệt thật 0 lỗi console |
| ~~P1~~ | ~~Chốt deck 12 slide~~ **XONG — 12/12 slide đã render thật qua PowerPoint và xem bằng mắt, PDF nộp đã commit** | Còn lại duy nhất: **tập nói 3 phút** trong Presenter View (speaker notes đã nhúng sẵn từng slide, mốc 0:00→3:00). |
| **P1** | Điền form `forms.gle/7JHbcihzVA3uGTPw6` trước **2026-11-08 23:59** | Hết hạn là mất quyền nộp, không có gia hạn. |
| **P2** | Chụp/quote dashboard Datadog thật vào video (đăng nhập `app.ap2.datadoghq.com`, env `hackathon-2026`) | Số liệu đã chảy thật qua agent (3.246 metric packets, `Series Flushed` tăng), nhưng **CLI không query được series** vì `/api/v1/series` cần Application Key — chỉ người dùng đăng nhập mới thấy được UI. |
| **P2** | Đọc lại `docs/DEMO_VIDEO_SCRIPT.md` §4 — 5 lỗi biến sản phẩm thành đồ chơi | Mất 10% Trình bày rất dễ, lấy lại rất khó |

### 5.1 Tình trạng push và 3 việc còn lại của chủ repo

Đã làm xong (không cần lặp):

```bash
git remote add origin git@github.com:gnuhhung317/rails-ops.git
git merge-base --is-ancestor master HEAD        # xác nhận fast-forward AN TOÀN trước khi động vào master
git update-ref refs/heads/master HEAD           # không merge commit, không rewrite history
git push origin master
git push origin feature/temporal-correctness-and-scenario-validation
```

Còn lại — chỉ tài khoản GitHub của chủ repo làm được:

1. **Chuyển repo sang Public**: `github.com/gnuhhhung317/rails-ops/settings` → Danger Zone →
   *Change visibility* → Public. Kiểm chứng lại bằng `curl -I https://github.com/gnuhhhung317/rails-ops`
   phải trả **200** (hiện tại **404**). Public là yêu cầu của thể lệ, không phải lựa chọn.
2. **Rotate 2 secret đã lộ có chủ đích trong phiên này**: mật khẩu Atlas `duchung02nd_db_user`
   (Atlas → Security → Database Access → Connect) và Datadog API key (Datadog → Organization Settings →
   API Keys). Cả hai chỉ sống trong `.env` (đã gitignore, chưa từng bị track — đã kiểm tra trên toàn bộ
   history), nhưng key đã nằm trên bàn phím/serial log thì coi như lộ.
3. **Kiểm tra IP whitelist của các API key trading** trên GCP: VM `test-2g2c` vừa resize nên NAT IP
   đã đổi (`35.247.151.158` → `34.143.162.225`). Sandbox bot vẫn healthy nhưng bất kỳ sàn nào
   whitelist theo IP đều cần cập nhật.

**Không** push `dataset/MetroPT3(AirCompressor).csv` hay `metropt+3+dataset.zip` — cả hai nằm
trong `.gitignore`; repo nộp chủ ý chỉ mang slice 39 MB thật (`MetroPT3-demo-slice.csv`), README ghi
rõ DOI `10.5281/zenodo.7157937` và đường dẫn tải file đầy đủ.

## 6. Câu chốt khi BGK hỏi "ý tưởng triển khai là gì?"

> Metro Line 1 và Cát Linh – Hà Đông đã có sẵn áp suất bình chính, nhiệt độ dầu và
> dòng động cơ trên bus điều khiển của tàu. Phase 1 chỉ là một bản sao **read-only**
> từ TCMS — không gắn cảm biến, không đụng mạch điều khiển, không cần phê duyệt an
> toàn chạy tàu. Engine không đổi một dòng khi thay dữ liệu Lisbon bằng dữ liệu Việt
> Nam. Đó là lý do chúng tôi xin **sáu tháng và hai đầu tàu**, chứ không xin một
> project pilot mười tám tháng.
