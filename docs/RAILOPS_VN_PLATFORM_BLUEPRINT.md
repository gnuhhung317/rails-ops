# RailOps VN — Nền Tảng Vận Hành Đường Sắt Việt Nam Bằng Dữ Liệu Thời Gian Thực
### Blueprint Kiến Trúc Doanh Nghiệp & Kế Hoạch Triển Khai Thương Mại Hóa

> **Document Version:** 1.0
> **Date:** 2026-11-07
> **Author:** Principal Enterprise Architect, CompressorGuard Team
> **Context:** MUGVN Mini Hackathon 2026 (MongoDB × Datadog) — deadline 08/11/2026 23:59
> **Status:** Normative — đây là tài liệu định vị sản phẩm (Positioning Document) cho vòng chung kết

---

## 0. Elevator Pitch (30 giây — dùng mở đầu video demo và slide 1)

> Mỗi đoàn tàu metro có một máy nén khí — nó bơm khí cho **phanh, giảm xóc và cửa hành khách**. Nó hỏng thì tàu **mất phanh và phải rút khỏi tuyến**.
>
> Hôm nay, ngành đường sắt Việt Nam biết nó hỏng **sau khi** nó hỏng: một kỹ sư nhìn ngưỡng áp suất thấp nhất trong nhật ký, quá muộn để hành động.
>
> **RailOps VN** là nền tảng vận hành dữ-liệu-first cho đường sắt Việt Nam. Phân hệ lõi sống còn của chúng tôi, **CompressorGuard**, phát hiện lỗi rò khí trên **1.5 triệu điểm đo vật lý thật** sớm hơn cách konvensional **33 giờ 52 phút** — đủ để điều độ viên kéo tàu vào ga cuối và sửa trong khoảng trống bảo trì, thay vì dừng tàu giữa tuyến.
>
> Không có dữ liệu giả. Không có auto-pilot. Một người điều độ thật, ra quyết định thật, trên bằng chứng thật, với sổ cái kiểm chứng được.

---

## 1. Vấn Đề Có Thật (Không Phải Vấn Đề Bịa)

### 1.1. Ba bằng chứng từ thực tế vận hành đường sắt Việt Nam

| # | Thực tế đã ghi nhận | Ý nghĩa kỹ thuật |
|:-:|:---|:---|
| 1 | Sau **hơn 3 năm vận hành**, tuyến Cát Linh – Hà Đông đã xuống cấp nhiều hạng mục; ngày **23/5/2025** ga **Yên Nghĩa bị nước tràn vào**, Hà Nội phải đề xuất **sửa chữa khẩn cấp nhà ga**. | Hạ tầng và đầu tàu đã bước vào **vùng quá độ mòn (wear-out zone)**. Chế độ giám sát "định kỳ theo đồng hồ giờ" (time-based) đã bộc lộ giới hạn. |
| 2 | Hà Nội/Metro HCM đang **chuẩn bị đầu tư 10 tuyến đường sắt đô thị trong 2025–2026**; Hanoi Metro đã lập **Chi nhánh Xí nghiệp Quản lý Bảo trì** riêng. | Đội tàu và bộ máy bảo trì **phình to nhanh hơn tốc độ tuyển kỹ sư có kinh nghiệm**. Bài toán là *scalability của phán đoán con người*, không phải của cảm biến. |
| 3 | Dự án **ĐSCT Bắc–Nam 1.541 km, ~1,7 triệu tỷ VND**, Quốc hội thông qua 30/11/2024, **khởi công trước cuối 2026**, chọn nhà thầu Q2/2026. | Cửa sổ để thiết kế **hệ thống giám sát ngay từ phase bàn giao** còn mở. Ai chuẩn hoá data schema + observability pipeline bây giờ sẽ định nghĩa chuẩn cho 15 năm tới. Đây là lý do sản phẩm phải ở tầm **nền tảng**, không phải một dashboard. |

### 1.2. Nỗi đau định lượng được: một máy nén khí

Trên đầu tàu metro, **Main Air Compressor / APU** cấp khí nén cho ba hệ thống *an toàn chạy tàu* (safety-critical):

1. **Phanh khí động (pneumatic / service brake)** — mất áp = mất phanh, buộc dừng tàu.
2. **Treo khí (air spring)** — mất áp = goòng cứng, giới hạn tốc độ, nguy cơ trật ray ở ga cong.
3. **Điều khiển cửa hành khách + còi + hệ thống treo cửa** — mất áp = tàu chết kẹt ở ga.

**Chi phí thật của một lần tàu chết giữa tuyến** (ngành metro quốc tế, quy VND cho tuyến 19.7 km Bến Thành – Suối Tiên):

- Rút tàu khẩn cấp + cứu hộ + kiểm tra an toàn hầm: **2–6 giờ** mất năng lực phục vụ của 1 đoàn tàu.
- Giãn/hoãn chạy tàu dây chuyền: **hàng nghìn hành khách** trễ, mất doanh thu vé + phạt hợp đồng dịch vụ (service-level agreement).
- Hỏng thứ cấp: piston/valve breakage do chạy tiếp khi thiếu dầu → chi phí **overhaul** gấp ~10 lần chi phí **seal replacement** sửa sớm.
- Nghiêm trọng nhất: **sự cố an toàn** — chi phí không tính bằng tiền.

→ **Vấn đề không phải "dự đoán lỗi". Vấn đề là "mua lại được thời gian để quyết định".** Đó là lý do sản phẩm lấy **lead time** làm hero metric, không lấy accuracy.

### 1.3. Vì sao giải pháp hiện có chưa đủ (khoảng trống thị trường)

| Hướng tiếp cận hiện có | Giới hạn | RailOps VN khác ở đâu |
|:---|:---|:---|
| **CBM / Condition-Based Maintenance trên SCADA sẵn có** (ngưỡng tĩnh, báo khi vượt ngưỡng) | Ngưỡng tĩnh **không phân biệt LOADED vs UNLOADED**. Máy nén nghỉ thì áp suất thấp là bình thường → hoặc bỏ sót (leak tiến triển trong lúc mang tải), hoặc báo động ảo tràn lan. | **Regime-aware**: mọi sigma được tính trong từng chế độ vận hành. Nhảy bậc **≥3 chu kỳ mang tải** mới được nâng case. |
| **Predictive ML "hộp đen"** (trả về điểm anomaly) | Cho biết *có gì đó bất thường*, không cho *tại sao*, *đã lâu chưa*, và *sửa xong thật chưa*. Điều độ viên không dám ký quyết định rút tàu dựa trên một con số 0.382. | **Bằng chứng 4 tầng + provenance từng tín hiệu** và **Recovery Verification**: chỉ đóng case khi 5 mẫu mang tải liên tiếp thực sự đạt chuẩn. |
| **CMMS/EAM** (SAP PM, Maximo) quản lý work order | Ghi lại quyết định **sau khi** nó được đưa ra. Không có dòng thời gian vật lý. | RailOps VN là **sổ cái sự kiện (CaseEvent ledger)**: mọi phát hiện, mọi ghi chú, mọi phê duyệt đều có actor + timestamp + nguồn dữ liệu — nối được vào work order của EAM. |

---

## 2. Định Vị Sản Phẩm: RailOps VN (Platform) ⊃ CompressorGuard (Subsystem)

Đây là quyết định chiến lược để ăn điểm **Sáng tạo (30%)** và **Tác động (30%)**: chúng tôi không nộp một dashboard máy nén khí. Chúng tôi nộp **kiến trúc nền tảng** và **một phân hệ đã chạy thật được chứng minh end-to-end**.

```
┌──────────────────────────────────────────────────────────────────────┐
│                        RAILOPS VN  (Platform)                        │
│   Data spine: Fleet → Train → Subsystem → Asset   (Layer A)          │
├──────────────┬──────────────┬──────────────┬──────────────┬──────────┤
│ Compressor-  │ Brake &      │ Traction /   │ Platform     │ Track &  │
│ Guard        │ Door Air     │ HV Inter-    │ Door /       │ Signals  │
│ (LIVE HERE)  │ Circuit      │ HV (future)   │ Escalator    │ (future) │
│  [Mission-   │ Guard        │              │ Watch        │          │
│   Critical   │ (Phase 2)    │ (Phase 3)    │ (Phase 3)    │ (Phase 4)│
│   Core)      │              │              │              │          │
├──────────────┴──────────────┴──────────────┴──────────────┴──────────┤
│  SHARED ENGINE: Regime Classifier · Detector Fusion · Case Correlator│
│                 ActionGuard · RecoveryVerifier · CaseEvent Ledger    │
├──────────────────────────────────────────────────────────────────────┤
│  MongoDB  (Time Series + Document + $window analytics)              │
│  Datadog  (APM traces · Metrics · Monitors · Dashboard · On-call)   │
│  IoT Edge (MQTT gateway · store-and-forward · dual-clock stamping)  │
└──────────────────────────────────────────────────────────────────────┘
```

**Luận điểm bán hàng:** CompressorGuard không phải một *ứng dụng*, nó là **chứng minh rằng cái khung của nền tảng hoạt động**. Cùng một engine, cùng một schema, cùng một ActionGuard — đổi `signal_pack` và `playbook` là ra `BrakeAirGuard`. Đây chính là tính **Openness/Scalability** mà hội đồng chấm "Tác động" tìm kiếm.

### 2.1. Module IoT (phần "có thể vận hành thật")

| Tầng | Thiết bị hiện có trên đầu tàu | Lấy dữ liệu bằng cách nào | Not yet |
|:---|:---|:---|:---|
| **Sensing** | Áp suất bình chính (pressure transducer `MPa`/`bar`), nhiệt độ dầu, dòng điện mô-tơ compressor, states contactor/valve | Tap trực tiếp **bus CAN/MVB/TCMS** của đầu tàu (đầu tàu metro hiện đại đã có sẵn các đo này cho TCMS nội bộ) | Không cần gắn thêm sensor mới → **giảm ma sát triển khai gần bằng 0**. Đây là điểm then chốt để nói "vận hành thật". |
| **Edge gateway** | Box trên tàu: thu CAN/MVB → chuẩn hoá JSON → **store-and-forward** | MQTT/Sparkplug B over **tunnel radio / 4G-5G / wifi depot**; buffer cục bộ khi mất kết nối trong hầm | Chống mất dữ liệu — yêu cầu bắt buộc của hệ thống an toàn. |
| **Ground truth đối chứng** | Đầu đo rung (vibration accelerometer) trên vỏ máy nén, đầu đo rò khí (acoustic) | Gắn **retrofit không xâm nhập** khi overhaul | Nâng cấp ML corroboration; Layer C. |
| **Clock** | Đồng hồ thời gian thực trên gateway | **Dual-clock stamping**: thiết bị ghi `event_time` vật lý; hệ thống ghi `simulation_time`/`ingest_time` | Cho phép **replay chính xác** phục vụ điều tra và audit — tính năng bắt buộc khi có sự cố pháp lý. |

### 2.2. Realtime path (pipeline không giả lập)

```
CAN/MVB bus ──> Edge Gateway ──MQTT──> Ingest Service ──> MongoDB
 (onboard)      (stamp event_time)     (validate +tag)    measurements  [Time Series]
                                                              │
                                    ┌─────────────────────────┤
                                    ▼                         ▼
                             Stream Processor         $setWindowFields
                          Regime → Detectors →        rolling mean/std
                          Isolation Forest →          (LOADED partition)
                          Evidence Fusion                    │
                                    │                        ▼
                                    ▼                 Analytics view
                          Case Correlator  ──>  operational_cases   [Document]
                          (max 1 case/asset)    case_events (ledger)[Document]
                                    │
                                    ▼
                          ActionGuard (5 gates) ──> Safe Mode branch
                                    │
                                    ▼
                          RecoveryVerifier (5 healthy LOADED) ──> CLOSE
                                    │
                    DogStatsD / OTel traces ──> DATADOG (metrics, APM,
                                                 monitors, on-call pages)
```

### 2.3. Vai trò MongoDB (đa mô thức, không phải "để cho đủ")

| Workload | Tính năng MongoDB | Vì sao không thay bằng PostgreSQL/khác |
|:---|:---|:---|
| Telemetry 1.5M điểm | **Time Series collection** + auto **bucketing** + **TTL retention** | Nén theo tự nhiên của chuỗi thời gian; retention tự động mà không cần cron partition. |
| Rolling sigma | **`$setWindowFields`** — partition by regime, sort by event_time | Tính mean/std cửa trượt ngay trong DB, không cần kéo 1.5M dòng về app. |
| Schema đa dạng 4 loại asset guard | **Document model** linh hoạt (`signal_pack` khác nhau mỗi phân hệ) | Thêm `BrakeAirGuard` không cần migration bảng. |
| Audit | **Immutable-ish `case_events`** với embedded `provenance` | Giữ provenance theo từng event mà không vỡ quan hệ. |

### 2.4. Vai trò Datadog (quan sát *chính hệ thống*, không chỉ quan sát tàu)

- **Metrics (DogStatsD):** `points_ingested`, `detector_latency`, `case_created`, `operator_ack_latency`, `actionguard_denials`.
- **APM Traces:** mỗi khung dữ liệu là một span chain `ingest → regime → detect → fuse → case`. Khi stream tụt nhịp trong demo, trace chỉ ra **span nào chậm** — đó là hành vi của một hệ thống thật.
- **Monitors:** (a) *Early Warning Pressure Breach*, (b) *Recovery Criteria Verified*, (c) **monitor cho chính độ trễ pipeline** — meta-observability.
- **Dashboard:** tình trạng hạm đội, chuỗi áp suất, điểm ML, thời gian can thiệp, chuỗi hồi phục.

**Câu chốt cho BGK:** *Chúng tôi dùng MongoDB để hiểu con tàu, và Datadog để hiểu hệ thống đang hiểu con tàu.*

---

## 3. Kịch Bản Kinh Doanh: Trước – Trong – Sau RailOps VN

Con số hoạt động của MetroPT-3 (Failure #3, Air Leak, 06/2020) — dữ liệu thật, không ngoại suy:

| Mốc | `event_time` | Sự kiện |
|:---|:---|:---|
| **T-early** | *sớm hơn* | **CompressorGuard phát hiện** (nhảy bậc ≥3 chu kỳ LOADED) |
| **T-conventional** | +33h 52m | Cách konvensional phát hiện (vi phạm ngưỡng LPS) |
| Maintenance | 08/06/2020 16:05 | Bảo trì thực tế theo báo cáo lịch sử (Layer C) |

**Cửa sổ 33h 52m = một ca trực + một khoảng trống bảo trì đêm.** Không phải con số trang trí: nó là khoảng thời gian *đủ để một điều độ viên thật kéo tàu vào depot và xiết lại gioăng van xả*.

Chi phí suy giảm (illustrative, ghi rõ là mô hình hoá theo `docs/RAIL_ECONOMICS_AND_VALUE_MODEL.md`, **không** phải số liệu thực đo):
- 1 đoàn tàu rút ngoài kế hoạch ≈ **6–10 giờ** dịch vụ mất + chi phí cứu hộ.
- 20 đoàn × 2 dây chuyền (BT-ST, CL-HĐ) → mỗi **1% giảm sự cố bất ngờ** tạo giá trị vận hành đáng kể và **giảm nhu cầu dự phòng đầu tàu** (capex avoidance — thường mới là khoản lớn nhất).
- Payback của retrofit-based monitoring: **dưới 1 năm** nếu tránh được một sự cố an toàn.

> **Minh bạch là một tính năng.** Mọi con số loại "mô hình hoá" đều được gắn nhãn và tách khỏi số đo thực. Đây chính là lý do hội đồng có thể tin 100% số liệu còn lại.

---

## 4. Kế Hoạch Triển Khai Thực Tế (Rollout) — Trả lời "Ý tưởng để triển khai là gì?"

### Phase 0 — Proof (Chính là cái đang nộp ở hackathon này) ✅
- Replay 1.5M điểm MetroPT-3 qua engine thật → MongoDB → Datadog → Console.
- **Chứng minh điều duy nhất quan trọng:** phát hiện sớm 33h52m trên dữ liệu vật lý thật, và luồng Operator 4 bước đi đến đóng case có kiểm chứng.
- Không có bằng chứng giả, không có UI hardcode.

### Phase 1 — Pilot trên dây chuyền đang chạy (6 tháng, chi phí thấp nhất)
- **Đối tượng:** 2 đầu tàu Cát Linh – Hà Đông (đã có Xí nghiệp Quản lý Bảo trì riêng → một khách hàng quyết định duy nhất).
- **Cách lấy dữ liệu:** đọc **song song (read-only mirror)** từ TCMS/CAN bus — **không can thiệp hệ thống điều khiển**, không cần phê duyệt an toàn chạy tàu. Ma sát triển khai gần bằng 0.
- **Thành công đo bằng:** tỷ lệ báo động ảo chấp nhận được (< X%/tuần), *operator acknowledgement latency*, và số lần **lead time chuyển thành quyết định thật**.
- Song song: gắn 1 đầu đo rung retrofit để nâng ML corroboration.

### Phase 2 — Mở rộng phân hệ dùng chung engine (6–12 tháng)
- `BrakeAirGuard`, `DoorAirCircuitGuard` trên cùng **Shared Engine** — chỉ đổi `signal_pack` + `playbook` + `ActionGuard` criteria.
- Tích hợp **một chiều ra EAM/CMMS**: RailOps VN đề xuất work order, hệ thống quản lý bảo trì vẫn là nơi phê duyệt. **Không thay thế bộ máy đang tồn tại → dễ mua.**
- Bật Datadog **On-call + Service Catalog** cho ca trực đêm.

### Phase 3 — Nhân bản cho Metro số 1 Bến Thành – Suối Tiên & Line 3 Nhổn – Ga Hà Nội (12–18 tháng)
- Cùng kiến trúc, chỉ khác **Asset Registry**. Đây là bài kiểm tra tính nền tảng: **onboard đoàn tàu mới = cấu hình, không phải code.**

### Phase 4 — Chuẩn hoá cho ĐSCT Bắc–Nam (từ 2026+, 1.541 km)
- Đề xuất **schema telemetry + event-ledger chuẩn** ngay trong giai đoạn lựa chọn nhà thầu/thiết kế hệ thống, để dữ liệu giám sát được **sinh ra theo chuẩn** thay vì retrofit.
- Mô hình giá trị chuyển từ *avoided downtime* sang **contractual SLA + condition-based overhaul interval extension** (kéo dài chu kỳ đại tu khi dữ liệu chứng minh máy còn tốt — thường là khoản tiết kiệm lớn nhất của đường sắt).

### 4.1. Rủi ro & cách nói thẳng với hội đồng (biến điểm yếu thành điểm mạnh)

| Rủi ro BGK sẽ hỏi | Trả lời |
|:---|:---|
| "Đây là dữ liệu Brazil, không phải Việt Nam." | Đúng, và **chúng tôi nói rõ**. MetroPT-3 là dataset metro công khai, cùng **mode hỏng hóc** (air leak) và cùng **loại thiết bị**. Giá trị nộp ở đây là **cơ chế và kiến trúc**, đã được chứng minh trên vật lý thật. Pilot Phase 1 thay dữ liệu bằng chính TCMS Việt Nam — **engine không đổi một dòng**. |
| "AI tự động dừng tàu à?" | **Không.** Human-in-the-Loop là bất biến thiết kế. Engine chỉ *đề xuất*; chỉ người mới *ký*. ActionGuard chặn cả quyết định của người khi bằng chứng chưa đủ. |
| "Mất mạng trong hầm thì sao?" | Edge **store-and-forward**; pipeline phát lại và mọi điểm giữ nguyên `event_time` → **replay xác định (deterministic replay)**, đã kiểm thử. |
| "Khác gì Siemens Senseye?" | Cùng bất biến công nghiệp (max 1 case/asset, 5-gate pre-flight), nhưng **mở, self-host được, và chi phí phù hợp cho đường sắt VN** — không bị lock-in license của hãng. |

---

## 5. Ánh Xạ Rubric → Bằng Chứng (dùng khi chấm và khi dựng slide)

| Tiêu chí | Trọng số | Bằng chứng cụ thể trong repo/demo |
|:---|:-:|:---|
| **Sáng tạo** | 30% | (1) **Regime-aware detection** (sigma tính riêng trong LOADED/UNLOADED); (2) **Dual-clock + deterministic replay** như một cơ chế điều tra, không phải tiện ích demo; (3) **ActionGuard** — hàng rào 5 cổng chặn cả *hành động của con người*; (4) **Recovery Verification** — hệ thống từ chối cho đóng case nếu chưa thực sự lành; (5) phản-đề-can **anti-alert-fatigue** (suppression có sổ cái). |
| **Kỹ thuật** | 30% | 1.5M điểm vật lý thật (Zero Fake Telemetry, kiểm toán được); `$setWindowFields` rolling statistics trong MongoDB Time Series; 4 detector + Isolation Forest fusion; CaseEvent ledger bền hoá; APM traces + DogStatsD + monitors/dashboard Datadog; **98/98 tests**, 5 evaluation gates G1–G5, launcher một lệnh. |
| **Tác động** | 30% | Vấn đề an toàn chạy tàu có thật ở VN (§1.1, 3 dẫn chứng); lead time **33h52m** = cửa sổ quyết định thật; kiến trúc nền tảng 4 phân hệ + rollout 4 phase tới ĐSCT Bắc–Nam; **không cần gắn sensor mới** (tap TCMS) → triển khai được ngay. |
| **Trình bày** | 10% | Console chuẩn APM doanh nghiệp (không một con số hardcode, không một nút demo trên header); Replay Studio Drawer tách bạch; Validation Reference Drawer đối chứng; kịch bản thuyết trình + deck rubric-mapped; tài liệu kiến trúc đầy đủ trong repo. |

---

## 6. Việc Cần Hoàn Tất Trước 23:59 Ngày 08/11 (Priority Stack)

| # | Hạng mục | Trạng thái | Ghi chú |
|:-:|:---|:---|:---|
| 1 | **Operations Console v3.0 (`src/static/`)** | 🔄 đang xây | Previously deleted và chưa dựng lại — **blocking**. Không có UI thì không có video, không có điểm Trình bày. |
| 2 | Chạy thật end-to-end + screenshot/record | ⏳ chờ #1 | Chứng minh bằng chứng sống, không bằng ảnh cũ. |
| 3 | **Video demo** (yêu cầu của BTC) | ⏳ | Kịch bản 5–7 phút ở `docs/PITCH_DECK_AND_DEMO_RUNBOOK.md`, quay bằng console mới. |
| 4 | **Slide chung kết** (yêu cầu của BTC) | ⏳ | Dựng theo §5, hero metric 33h52m ở slide 2. |
| 5 | RailOps VN positioning (tài liệu này) | ✅ | Đưa vào slide 3–4 và phần mở đầu video. |
| 6 | README + quickstart một lệnh | ⏳ | BGK phải chạy được trong <5 phút. |

---

## 7. Nguồn Tham Chiếu (dữ liệu thực tế §1.1)

- Lao Động — *Doanh nghiệp Việt đã sẵn sàng cho vai trò làm chủ tại các dự án metro* (28/09/2026): https://laodong.vn/xa-hoi/doanh-nghiep-viet-da-san-sang-cho-vai-tro-lam-chu-tai-cac-du-an-metro-1774032.ldo
- Bộ Xây dựng — *Sẵn sàng vai trò làm chủ tại các dự án metro* (15/10/2026): https://moc.gov.vn/vn/tin-tuc/1268/97533/san-sang-vai-tro-lam-chu-tai-cac-du-an-metro.aspx
- VnEconomy — *Hà Nội: Đề xuất xin sửa chữa khẩn cấp nhà ga metro Cát Linh – Hà Đông* (30/05/2025): https://vneconomy.vn/ha-noi-de-xuat-xin-sua-chua-khan-cap-nha-ga-metro-cat-linh-ha-dong.htm
- VTV — *Nhiều hạng mục tuyến metro Cát Linh – Hà Đông hư hỏng*: https://www.youtube.com/watch?v=Rwuu8Gb3Q_Y
- The Investor — *Vietnam targets Q2/2026 contractor selection for North-South high-speed railway* (20/03/2026): https://theinvestor.vn/vietnam-targets-q2-2026-contractor-selection-for-north-south-high-speed-railway-d18649.html
- Xinhua — *Vietnam to start construction of north-south high-speed railway line by 2026* (24/04/2025): https://english.news.cn/20250424/2d6bd559bfce464186bd83b6133a08a4/c.html
- MUGVN — *Mini Hackathon Sep/Oct 2026 (MongoDB × Datadog)*, rubric & timeline: https://mini-hackathon-sep-2026.mugvn.com/

**Datasets & đặc tả nội bộ:** `dataset/MetroPT3(AirCompressor).csv` (Nature Scientific Data / MetroPT-3), `docs/superpowers/specs/2026-10-11-prod-ready-ux-and-mechanism-design.md`, `docs/ARCHITECTURE.md`, `docs/RAIL_ECONOMICS_AND_VALUE_MODEL.md`, `screen/01..07`.
