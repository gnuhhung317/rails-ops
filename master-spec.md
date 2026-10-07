## Business / Domain layer — added after self-critique

### Vì sao business clarity là một criterion riêng?

Một đề tài tốt không chỉ cần “giải thích được trong 30 giây”. Cần đồng thời có:

1. **Business consequence rõ:** failure xảy ra thì operator/business mất gì?
2. **Operational loop thật:** Detect → Investigate → Response → Recovery.
3. **Dataset đúng domain:** dữ liệu phải đủ để chứng minh câu chuyện, không dựng business logic chỉ từ suy đoán.
4. **Technical fit:** MongoDB + Datadog phải giải quyết vấn đề, không phải lớp công nghệ trang trí.

### So sánh lại các lựa chọn

**Cold-chain:** business story dễ hiểu nhất: nhiệt độ vượt range → hàng có nguy cơ hỏng → xử lý → recovery. Nhưng dữ liệu cold-chain đã tìm được không nhất thiết đại diện cho logistics/kho vận đầy đủ; nếu thiếu shipment/vehicle/warehouse/actuator/failure ground truth thì rất dễ biến thành threshold dashboard. Chỉ chọn nếu Spike xác nhận dataset đủ để xây incident thật.

**Smart HVAC:** business story rất dễ hiểu (“điều hòa chạy nhưng phòng vẫn nóng / tiêu thụ điện bất thường”), nhưng UCI Appliances Energy Prediction chủ yếu là dữ liệu một low-energy house với temperature/humidity/weather/appliance energy, không phải HVAC fault telemetry đầy đủ. Không nên claim HVAC degradation/failure nếu dataset không chứng minh được. Tạm thời loại khỏi shortlist chính.

**IoT Security:** detect → investigate → isolate → recovery rất trực quan và RT-IoT2022 có normal + nhiều attack patterns. Tuy nhiên risk lớn là project bị nhìn thành IDS/network security hơn là IoT Real-time Operations. Nếu chọn, phải xoay quanh incident response và operational control loop, không phải chỉ attack-classification accuracy.

### Vì sao CompressorGuard vẫn đứng đầu?

CompressorGuard khó hiểu hơn, nhưng MetroPT-3 có **physical equipment + operational context + event-level failure/maintenance ground truth + real sensor telemetry**. Paper mô tả APU failure có operational consequence và các failure scenarios như air leak/air dryer/pneumatic pilot valve/oil leak. Điều này cho phép xây operations story dựa trên dữ liệu thật thay vì tự tưởng tượng business logic.

### Business-first mental model

**Ai dùng?**  

Maintenance / operations engineer theo dõi tình trạng APU/compressor.

**Họ sợ điều gì?**  

Một compressor/APU degradation tiến triển thành failure, gây disruption và cần đưa train ra khỏi vận hành để sửa chữa.

**Họ đang phải làm gì?**  

Theo dõi nhiều sensor, nhận biết pattern bất thường, ghép telemetry với trạng thái thiết bị và lịch sử incident, rồi quyết định có cần can thiệp hay không.

**CompressorGuard thay đổi điều gì?**  

Thay vì chờ một sensor vượt hard threshold hoặc failure xảy ra, hệ thống phát hiện pattern bất thường sớm hơn, tập hợp evidence thành một incident và đưa operator qua một workflow có thể kiểm chứng.

**Success là gì?**

- phát hiện failure/degradation sớm hơn baseline;
- giảm false positives trong healthy windows;
- rút ngắn investigation;
- response được ghi nhận;
- recovery được xác minh từ telemetry.

### Business loop

```
Physical compressor / APU
        ↓
Operational telemetry
        ↓
Normal → degradation → failure risk
        ↓
DETECT
        ↓
INVESTIGATE
  “What changed?”
  “What evidence supports it?”
  “Have we seen this before?”
        ↓
RESPOND
  safe remediation / maintenance workflow
        ↓
VERIFY RECOVERY
  telemetry returns toward healthy baseline
        ↓
Incident = RECOVERED
```

### Business-first pitch

> **A compressor failure can take a train out of operation. CompressorGuard watches the compressor's operating behavior, detects degradation before it becomes an obvious failure, gives the operator evidence for investigation, supports a safe response, and verifies from telemetry that the system has recovered.**
> 

Sau đó mới nói technical stack:

> **MongoDB stores and reasons over the operational telemetry and incident history; Datadog provides the observability control plane; deterministic rules provide predictable detection; multivariate ML adds earlier detection of subtle cross-sensor behavior.**
> 

### Defense questions

**“Why not just Datadog?”**

> Datadog tells the operator that the observable system is unhealthy. MongoDB lets our application reason over the device's time-series behavior, current state, incident lifecycle, and historical operational context.
> 

**“Why AI?”**

> AI is not the product. The operations system still works with deterministic rules. ML is valuable only if experiments show that it catches subtle multivariate deviations or provides earlier detection than rules alone.
> 

**“Why is this business-relevant?”**

> **Failure → operational disruption / maintenance → earlier detection → earlier intervention → potentially less disruption.**
> 

Không lượng hóa financial impact nếu chưa có explicit cost assumptions.

---

> **Decision:** Chọn **CompressorGuard — Real-time Compressor Operations & Incident Response** làm đề tài chính cho MUGVN Hackathon 2026, sử dụng **MetroPT-3** làm dữ liệu nền, kết hợp MongoDB + Datadog + deterministic detection + multivariate anomaly detection + incident response + recovery verification.
> 

> 
> 

> **Core thesis:** Không xây “ML dashboard” hay “AI chatbot predictive maintenance”. Xây một **real-time operations system** trả lời trọn vẹn: **Detect earlier → Prove why → Act → Prove recovery.**
> 

## 1. Executive summary

| Hạng mục | Quyết định |
| --- | --- |
| Project | CompressorGuard |
| Domain | IoT / Industrial Operations / Predictive Maintenance |
| Dataset | UCI MetroPT-3 |
| Primary DB | MongoDB Time Series Collections |
| Observability | Datadog Metrics + Logs + APM/Tracing + Monitors |
| Detection | Deterministic rules + multivariate ML anomaly detection |
| AI retrieval | MongoDB Vector Search — P1 |
| LLM | Evidence synthesis / RCA — P2 |
| Demo | Deterministic live scenario ~90 giây |
| Differentiator | Operational Evidence Graph |

## 2. Đề bài và chiến lược chấm điểm

MUGVN Hackathon 2026 yêu cầu một hệ thống **IoT Real-time Operations** có thể trình diễn trọn vẹn một incident: **Detection → Investigation → Response → Recovery**.

### MongoDB bắt buộc

- MongoDB là operational data platform chính.
- Time Series Collections.
- Aggregation Pipeline + window functions.
- expireAfterSeconds / data lifecycle.
- Data model và access pattern hợp lý.
- MongoDB phải gắn chặt với operational problem.
- Optional: Change Streams, Vector Search, Search, geospatial, event processing.

### Datadog bắt buộc

- Dashboard cho operational signals/system health.
- Monitor/alert cho failure/degradation/risk có ý nghĩa.
- Ít nhất một capability bổ sung: Log Management, APM, Distributed Tracing, RUM, Anomaly Detection hoặc Agent Observability.
- Kết nối metrics + logs + traces + operational context cho detection/investigation/response.

### Cách đọc rubric

Không hỏi “đề tài nào thú vị nhất?”. Hỏi:

> **Trong 5–10 phút, giám khảo có nhìn thấy một failure xảy ra, hệ thống tự phát hiện, giải thích được bằng evidence, hành động và chứng minh recovery hay không?**
> 

Các trục cần tối ưu:

1. Problem / operational reality
2. MongoDB architecture
3. Datadog observability
4. Full incident flow
5. Reliability / maintainability
6. Creativity + appropriate AI
7. Business / operational impact
8. MVP / docs / video / presentation

## 3. Vì sao chọn CompressorGuard?

| Rank | Concept | Đánh giá |
| --- | --- | --- |
| 1 | Compressor Operations | ~9.3–9.4/10 |
| 2 | Industrial Motor/Bearing | ~8.6/10 |
| 3 | Smart HVAC | ~8.7/10 |
| 4 | Gas Turbine | ~7.9/10 |
| 5 | Fleet | ~7.9/10 |
| 6 | C-MAPSS aircraft engine | ~7.8/10 |

### CompressorGuard thắng vì

- Equipment và operational context thực tế.
- Multivariate telemetry.
- Failure/maintenance intervals để làm ground truth event-level.
- Rất hợp MongoDB Time Series + window analytics.
- Rất hợp Datadog metrics/logs/traces.
- Có thể xây incident story rõ.
- Có thể tạo deterministic demo từ failure pattern thật.

## 4. Dataset — MetroPT-3

Nguồn chính:

- UCI: https://archive.ics.uci.edu/dataset/791/metropt+3+
- Scientific Data paper: https://www.nature.com/articles/s41597-022-01877-3

MetroPT-3 là dữ liệu vận hành của **Air Production Unit (APU) trên metro train**, khoảng 1.5M observations, 15 features, khoảng 208 MB CSV.

Sensor acquisition khoảng **1 Hz**. Hệ thống gốc truyền dữ liệu lên remote server theo batch khoảng 5 phút qua GSM. Trong hackathon, replay engine sẽ mô phỏng sensor stream thành realtime feed.

README cần nói rõ:

> Dataset sensor acquisition is 1 Hz; the original system transmitted data remotely in batches. For the hackathon, our replay engine emulates the sensor stream as a real-time operational feed.
> 

### Failure ground truth

Không nói “MetroPT-3 không có failure labels”.

Cách chính xác:

> **MetroPT-3 không có point-level failure label cho từng sample, nhưng có event-level ground truth qua maintenance/failure reports dưới dạng time intervals.**
> 

Paper mô tả các failure scenarios liên quan tới:

- air leak on clients;
- air leak on air dryer associated with pneumatic pilot valve malfunction;
- oil leak on compressor.

Có inconsistency cần freeze trong Spike 0 giữa UCI listing và paper về số lượng failure reports/catastrophic failures. Đây là việc phải xác minh, không phải lý do pivot.

### Spike 0 phải xác định

- exact columns;
- timestamp/sampling;
- missingness;
- failure intervals;
- failure modes;
- healthy baseline windows;
- train/validation/test split;
- license/citation.

## 5. Problem statement

Industrial compressors/air-production systems có thể suy giảm trước catastrophic failure.

Nếu chỉ monitor từng sensor:

- threshold có thể chưa bị vượt;
- degradation có thể diễn ra từ từ;
- cross-sensor relationship có thể thay đổi trước khi một sensor trở nên obviously abnormal.

Operator phải tự ghép telemetry + logs + service health + history + previous incidents + remediation.

CompressorGuard tự động hóa công việc này.

### Product statement

> **CompressorGuard is a real-time IoT operations platform that detects subtle compressor degradation, correlates device and service evidence, guides incident investigation, executes a safe remediation workflow, and verifies recovery from telemetry.**
> 

## 6. Incident story

### Phase 0 — Healthy

APU-01 hoạt động bình thường:

- pressure stable;
- motor current stable;
- temperature stable;
- anomaly score low;
- Datadog green.

### Phase 1 — Degradation

Inject/replay degradation pattern:

- pressure variance tăng;
- pressure relationships thay đổi;
- motor current trend tăng;
- control/valve behavior thay đổi;
- ML anomaly score tăng.

### Phase 2 — Detection

Layer 1: threshold + rate-of-change + rolling statistics.

Layer 2: multivariate anomaly model.

Incident Engine tạo incident khi evidence đủ mạnh.

### Phase 3 — Investigation

Incident page cung cấp:

- device;
- telemetry window;
- anomaly score;
- dominant anomalous features;
- Datadog metrics;
- logs;
- traces;
- device state;
- similar cases nếu Vector Search có.

### Phase 4 — Response

Simulate safe operating mode/remediation.

Không giả vờ điều khiển thiết bị vật lý thật.

### Phase 5 — Recovery

Không chỉ đổi status thành RECOVERED.

Phải xác minh:

- pressure variance giảm;
- motor current trở lại baseline;
- anomaly score giảm;
- health score tăng;
- critical alert biến mất.

## 7. Architecture

MetroPT-3

↓

Scenario Compiler

↓

Replay / Demo Mode

↓

IoT Gateway

↓

FastAPI Ingestion

├──→ MongoDB Time Series

├──→ Rule Engine

├──→ Feature Window → Multivariate ML

└──→ Datadog Metrics / Logs / Traces

MongoDB Time Series

↓

$setWindowFields / historical analytics

↓

Evidence Engine

├──→ device_state

└──→ incidents

Incident

├──→ Datadog

├──→ Vector Search (P1)

└──→ LLM synthesis (P2)

Incident

↓

Remediation

↓

Recovery Verification

↓

Incident = RECOVERED

### Architectural principles

**MongoDB = operational telemetry brain**

- raw IoT telemetry;
- window analytics;
- device state;
- incident lifecycle;
- historical operational context.

**Datadog = observability control plane**

- service health;
- metrics;
- logs;
- traces;
- monitors;
- operational investigation.

**ML = intelligent detection**

**LLM = evidence synthesis**

## 8. MongoDB data model

### telemetry — Time Series Collection

Conceptual document:

{

timestamp,

deviceId,

pressure,

temperature,

motorCurrent,

valveState

}

Configuration:

- timeField = timestamp
- metaField = deviceId
- TTL via expireAfterSeconds.

Operational retention có thể khoảng 7 ngày cho demo/dev; historical archive giữ riêng nếu cần.

### device_state — current operational snapshot

Không phải second telemetry stream.

Ví dụ:

{

deviceId,

updatedAt,

healthScore,

anomalyScore,

operatingRegime,

dominantAnomalies,

activeIncidentId

}

Mục đích:

- dashboard reads nhanh;
- AI context nhanh;
- incident engine không scan raw history.

### incidents — incident lifecycle

Nên chứa:

- incidentId;
- deviceId;
- status;
- severity;
- detectedAt;
- rootCauseHypothesis;
- evidence;
- action;
- recoveredAt;
- source = real/synthetic.

### incident_signatures — optional

Chỉ tạo khi Vector Search thực sự được dùng.

Lưu:

- normalized feature vector;
- incident metadata;
- root cause;
- remediation;
- outcome;
- source real/synthetic.

## 9. MongoDB capabilities

### Time Series

Core requirement. Raw telemetry phải nằm ở Time Series Collection.

### $setWindowFields

Dùng cho:

- rolling mean;
- rolling std;
- slope/derivative;
- moving statistics;
- historical anomaly analysis.

### TTL

expireAfterSeconds cho operational telemetry.

Câu chuyện:

> “We intentionally separate hot operational telemetry from long-term incident knowledge.”
> 

### Access patterns

- telemetry: append-heavy time series;
- device_state: point lookup;
- incidents: lifecycle queries;
- indexes theo deviceId/status/time khi cần.

### Change Streams

**Không dùng trên Time Series Collection.**

MongoDB Time Series Collections không hỗ trợ Change Streams.

Nếu cần event-driven behavior, Change Stream chỉ nên đặt trên normal collections như device_state/incidents/incident_candidates.

Chỉ làm nếu business logic thật sự cần, không tick checkbox.

### Vector Search

P1.

Use case:

Current anomaly signature → nearest historical incidents → known root cause/playbook.

## 10. Detection

### Layer 1 — Deterministic

Inputs:

- thresholds;
- rolling statistics;
- rate-of-change;
- known operational constraints.

Ưu điểm:

- fast;
- interpretable;
- predictable;
- dễ demo.

Không claim “zero false negatives”.

Cách nói:

> Detects predefined operational violations.
> 

### Layer 2 — Multivariate ML

Mục tiêu:

> Detect combinations of sensor behavior that look abnormal even when no individual sensor has crossed a hard threshold.
> 

Pipeline:

1Hz telemetry

↓

rolling feature windows

↓

normalization

↓

operating regime

↓

Isolation Forest

↓

anomaly_score

Feature candidates:

- rolling mean;
- rolling std;
- slope;
- delta;
- pressure variance;
- motor current trend;
- valve switching rate;
- cross-sensor relationships.

Không feed raw 1Hz values blindly nếu chưa xử lý operating regime.

### Operating regime

Anomaly nên hiểu là:

> unusual relative to the current operating regime.
> 

Có thể phân biệt:

- startup;
- steady state;
- high load;
- shutdown.

Nếu thiếu thời gian, bắt đầu với một controlled healthy baseline.

## 11. ML evaluation

Không chỉ show anomaly_score.

Cần đo:

- precision/recall nếu phù hợp;
- false positives;
- detection lead time;
- rule-only vs rule+ML;
- known failure windows;
- healthy windows.

Quan trọng nhất: **lead-time comparison**.

Format:

Metric                     Rule       ML

---

Failure detected           yes        yes

Detection lead time        X          Y

False positives            X          Y

Known failures detected    X/X        Y/Y

Các số trên là format, không phải kết quả giả định.

Câu hỏi phòng thủ:

> “ML added what that deterministic rules could not?”
> 

Answer:

> Rules catch predefined operational violations. The multivariate model detects subtle cross-sensor deviations that may not produce any single-sensor threshold violation, and evaluation measures whether that produces earlier detection.
> 

## 12. Explainability

Isolation Forest cho anomaly score nhưng không tự động cho contributing_features.

Không claim API mặc định có feature attribution.

Có thể tạo explanation layer bằng:

- feature perturbation;
- attribution method;
- hoặc đơn giản hơn: feature-level deviation so với healthy baseline.

Ví dụ output:

anomaly_score = 0.91

dominant deviations:

pressure_variance     +4.1σ

pressure_delta        +3.6σ

motor_current_slope   +2.8σ

temperature            +0.4σ

Gọi đây là **dominant anomalous features**, không gọi sai thành Isolation Forest feature importance.

## 13. Datadog

### Metrics

- compressor.health_score
- compressor.anomaly_score
- compressor.pressure_variance
- compressor.motor_current_deviation
- compressor.time_to_threshold
- compressor.active_incidents

Tags:

- device_id;
- device_type;
- scenario;
- environment;
- incident_id.

### Logs

Ví dụ event types:

- INCIDENT_DETECTED
- REMEDIATION_EXECUTED
- RECOVERY_VERIFIED

### APM / Distributed Tracing

Dùng ddtrace hoặc OpenTelemetry.

Không tạo microservice zoo.

Architecture đủ dùng:

Ingestion API

↓

MongoDB

↓

Incident Worker

Custom spans:

- telemetry.ingest
- mongodb.insert
- feature.compute
- incident.evaluate
- root_cause.analyze
- remediation.execute
- recovery.verify

Mục tiêu demo:

> Incident → trace → worker → MongoDB operation → anomaly evaluation.
> 

### Monitors

Ví dụ:

- anomaly score > threshold;
- health score < threshold;
- sustained pressure instability;
- incident chưa recovery trong SLA.

Datadog monitor là observability mechanism, không phải sole control loop.

## 14. Datadog timing vs system timing

Tách hai clock:

**Detection clock**

- Incident Engine detects immediately.

**Observability clock**

- Datadog reflects metrics/logs/traces/alert.

Backend lưu:

- detected_at;
- datadog_alert_at;
- remediation_at;
- recovered_at.

Nguyên tắc:

> **Observability should observe the system, not be the system's sole control loop.**
> 

## 15. AI stack

### P0 — Multivariate Anomaly Detection

Isolation Forest / Autoencoder.

Vai trò:

- cross-sensor anomaly;
- subtle degradation;
- bổ sung deterministic rules.

### P0 — Evidence Engine

Không phải LLM.

Gom:

- MongoDB anomaly evidence;
- rule violations;
- device state;
- Datadog metrics;
- logs;
- traces;
- historical incidents.

### P1 — Vector Search

Current anomaly signature → similar incidents.

Ví dụ:

Similar case: INC-0037

Similarity: 0.91

Pattern: pressure instability + motor compensation

Known cause: pilot-valve degradation

Previous action: safe mode + inspection

Chỉ triển khai khi có đủ incident corpus.

### P1 — Risk trend

Không gọi là certified RUL.

Dùng:

> Estimated time to critical threshold.
> 

Nếu health score giảm tuyến tính thì chỉ là heuristic projection cho tới khi validation tốt.

### P2 — LLM Investigator

LLM nhận structured evidence:

MongoDB evidence

- Datadog context
- device history
- similar incidents

Output:

- likely cause;
- evidence;
- confidence High/Medium/Low;
- recommended action;
- risks.

Không bịa confidence như 87% nếu chưa calibration.

## 16. Operational Evidence Graph

Đây là differentiator lớn.

Một incident phải liên kết:

Incident

├── telemetry window

├── anomaly scores

├── violated rules

├── affected sensors

├── Datadog metrics

├── logs

├── traces

├── device state

├── previous similar cases

├── remediation

└── recovery evidence

Không cần Graph Database.

Conceptual incident view:

INC-0042

Severity       HIGH

Device         APU-01

Status         RECOVERED

WHY?

✓ Pressure instability +4.1σ

✓ Motor current trend +2.8σ

✓ Multivariate anomaly 0.91

✓ Ingestion service healthy

LIKELY CAUSE

Air-dryer / pneumatic pilot-valve degradation

ACTION

Safe operating mode

RESULT

Pressure variance ↓

Motor current ↓

Health score 41 → 86

## 17. Demo engineering

### Vì sao historical replay không đủ?

Failure có thể phát triển trong nhiều giờ/ngày.

60× vẫn có thể mất nhiều phút.

600× làm:

- graph quá nhanh;
- Datadog monitor khó evaluation;
- incident story khó theo dõi.

### Hai mode

**Historical Replay**

- development;
- validation;
- EDA;
- real dataset processing;
- 60×–300× tùy test.

**Demo Mode**

- presentation;
- ~90 giây;
- deterministic.

Demo scenario là **time-compressed transformation của real failure pattern**, không phải animation giả.

### Scenario Compiler

Input:

- real failure window.

Output:

scenario = pilot_valve_degradation

duration = 90 sec

baseline = 20 sec

degradation = 25 sec

critical = 10 sec

remediation = 10 sec

recovery = 25 sec

README:

> Demo mode uses a time-compressed scenario derived from real MetroPT-3 failure patterns.
> 

## 18. 90-second demo

### T+0–20 — Healthy

Dashboard:

- health green;
- anomaly low;
- Datadog healthy.

### T+20–40 — Degradation

Inject scenario.

Show:

- pressure variance;
- motor current trend;
- ML anomaly score.

### T+40–45 — Detection

Incident Engine creates HIGH incident.

Datadog reflects alert.

### T+45–65 — Investigation

Show:

1. telemetry;
2. anomaly evidence;
3. Datadog logs;
4. trace;
5. device state;
6. similar case if available.

### T+65–75 — Response

Trigger SAFE MODE.

### T+75–90 — Recovery

Show:

- anomaly ↓;
- pressure variance ↓;
- health ↑;
- incident RECOVERED.

Final line:

> “We didn't just detect the failure. We proved why it happened, acted on it, and verified recovery from telemetry.”
> 

## 19. Demo phải là real backend

### Không làm

INJECT → UI animation → ALERT → UI animation → RECOVERED

### Phải làm

INJECT INCIDENT

→ scenario generator

→ real telemetry

→ real MongoDB writes

→ real feature calculation

→ real ML score

→ real incident

→ real Datadog metrics/logs/traces

→ real remediation

→ real recovery verification

UI chỉ hiển thị backend state.

## 20. Business / operational impact

KPIs:

- detection lead time;
- time-to-diagnosis;
- incident duration;
- false positive rate;
- recovery time;
- estimated downtime avoided;
- manual investigation steps reduced;
- health recovery delta.

Không bịa financial impact nếu chưa có cost assumptions.

## 21. Risk register

### MetroPT failure ambiguity

Mitigation: Spike 0; natural failure + synthetic demo.

### ML false positives

Mitigation: healthy validation; regime-aware features; threshold calibration; ML không tự trigger destructive action.

### Datadog timing

Mitigation: Incident Engine độc lập; Datadog observability.

### AI hallucination

Mitigation: structured evidence; evidence references; High/Medium/Low confidence; deterministic fallback.

### Vector Search corpus quá nhỏ

Mitigation: P1; không block MVP; real/synthetic tagging.

### Overengineering

Không làm nếu chưa cần:

- microservice zoo;
- Kafka;
- Kubernetes;
- Change Streams chỉ để tick box;
- Vector Search chỉ để tick box;
- fancy frontend;
- autonomous LLM agent.

## 22. What MongoDB does that Datadog cannot replace

Nếu giám khảo hỏi:

> “Why MongoDB? Datadog already has telemetry, metrics and alerts.”
> 

Trả lời:

**Datadog**

- service observability;
- metrics;
- logs;
- traces;
- alerts;
- operational control room.

**MongoDB**

- raw IoT telemetry;
- time-series storage;
- custom window analytics;
- device state;
- incident lifecycle;
- historical operational context;
- case retrieval.

Pitch:

> **Datadog tells the operator that something is wrong with the observable system. MongoDB enables the application to reason over device behavior and operational history.**
> 

## 23. What AI adds that rules cannot

Rules detect predefined violations.

ML detects:

- subtle;
- multivariate;
- cross-sensor;
- previously unspecified patterns.

Phải chứng minh bằng experiment, không assertion.

Target comparison:

Rule-only vs Rule+ML:

- detection lead time;
- false positives;
- known failure detection;
- healthy-window behavior.

## 24. Nếu bỏ AI thì sao?

Hệ thống vẫn phải chạy:

Telemetry → Rules → Incident → Datadog → Investigation → Remediation → Recovery

Nếu bỏ AI mà system chết, architecture quá AI-dependent.

## 25. Evaluation protocol

### Split

Không random split time series ngây thơ.

Ưu tiên temporal split:

- early healthy → baseline/training;
- later healthy → validation;
- held-out failure periods → evaluation.

Tránh future leakage.

### Compare

A. Rule-only

B. Rule + ML

C. Rule + ML + Vector Search (optional)

Metrics:

- precision;
- recall;
- false positives;
- detection lead time;
- recovery verification;
- investigation completeness.

## 26. MVP

### P0

- MetroPT ingestion/replay;
- MongoDB Time Series;
- TTL;
- $setWindowFields;
- device_state;
- deterministic rules;
- incident lifecycle;
- Datadog metrics;
- Datadog logs;
- Datadog monitor;
- APM trace;
- remediation simulation;
- recovery verification;
- 90-second demo.

### P1

- Isolation Forest;
- better multivariate features;
- evidence ranking;
- Vector Search.

### P2

- LLM Investigator;
- advanced forecasting;
- polished AI UX.

## 27. Spike / Go-No-Go

### Gate 1 — Data

- [ ]  Download MetroPT-3
- [ ]  Load sample
- [ ]  Confirm columns
- [ ]  Confirm timestamps
- [ ]  Confirm failure windows
- [ ]  Confirm missingness
- [ ]  Select healthy baseline

### Gate 2 — MongoDB

- [ ]  Time Series works
- [ ]  TTL works
- [ ]  $setWindowFields works
- [ ]  Meaningful anomaly query works

### Gate 3 — Datadog

- [ ]  metric
- [ ]  log
- [ ]  trace
- [ ]  monitor

### Gate 4 — Incident

INJECT INCIDENT must produce:

degradation → detection → incident → response → recovery

### Gate 5 — Decision

Không pivot chỉ vì ML khó.

Pivot sang Smart HVAC chỉ nếu core system không thể reliably:

- ingest;
- analyze;
- detect;
- create incident;
- demonstrate recovery.

## 28. Build plan

### Phase 0 — Spike

Dataset + MongoDB + Datadog + one incident end-to-end.

### Phase 1 — Core

Ingestion + replay + MongoDB + rules + incident engine + Datadog.

### Phase 2 — Intelligence

Features + Isolation Forest + evaluation + Evidence Engine.

### Phase 3 — Investigation

Incident UI + logs + traces + history + optional Vector Search.

### Phase 4 — Demo

Scenario Compiler + 90-second scenario + recovery verification.

### Phase 5 — Polish

README + architecture + attribution + AI disclosure + screenshots + video + rehearsal.

## 29. Team split

### 3 người

**Member A — Backend / MongoDB**

- ingestion;
- Time Series;
- aggregation;
- device_state;
- incidents;
- lifecycle.

**Member B — Observability / Platform**

- Datadog;
- metrics;
- logs;
- traces;
- monitors;
- deployment.

**Member C — ML / Product / Demo**

- feature engineering;
- anomaly model;
- evaluation;
- Scenario Compiler;
- UI/demo.

### 2 người

A: backend + MongoDB + ingestion.

B: Datadog + ML + UI/demo.

## 30. Repo structure

compressorguard/

├── apps/

│   ├── ingestion/

│   ├── incident-worker/

│   └── dashboard/

├── ml/

│   ├── features/

│   ├── training/

│   ├── inference/

│   └── evaluation/

├── simulator/

│   ├── historical-replay/

│   ├── scenarios/

│   └── compiler/

├── mongodb/

│   ├── schemas/

│   ├── indexes/

│   └── pipelines/

├── observability/

│   ├── datadog/

│   ├── monitors/

│   └── dashboards/

└── docs/

## 31. README requirements

README phải trả lời:

1. What problem?
2. Why IoT?
3. Why MongoDB?
4. Why Datadog?
5. What dataset?
6. What is real vs synthetic?
7. How detection works?
8. How ML differs from rules?
9. How incident response works?
10. How recovery is verified?
11. How to run locally?
12. How to reproduce demo?
13. What AI tools/models were used?
14. What components/datasets are reused?
15. Known limitations?

## 32. Những điều tuyệt đối không claim

Không claim:

- zero false negatives;
- certified RUL nếu chỉ heuristic;
- AI discovered root cause nếu model chỉ cho anomaly score;
- production realtime nếu chỉ replay CSV mà không giải thích;
- valve timeout sensor nếu dataset không có;
- Datadog detected incident nếu Incident Engine mới là detector;
- Vector Search found historical case nếu corpus không đủ;
- LLM confidence 87% nếu chưa calibration.

## 33. Competitive moat

Dataset không phải moat.

Nếu đội khác cũng dùng MetroPT-3, differentiation nằm ở:

1. Incident narrative
2. Operational evidence
3. MongoDB architecture
4. Datadog investigation
5. Rule-vs-ML evaluation
6. Deterministic live demo
7. Recovery verification

Đối thủ có thể làm:

> “Predict compressor failure using LSTM.”
> 

CompressorGuard làm:

> **“Detect → explain → investigate → act → verify recovery.”**
> 

## 34. Final product definition

> **CompressorGuard is a real-time industrial IoT operations platform for compressor/APU systems. It stores raw telemetry in MongoDB Time Series, uses window analytics and multivariate anomaly detection to identify degradation, uses Datadog as the observability control plane, correlates telemetry with logs/traces and historical incidents, executes a safe remediation workflow, and verifies recovery from live operational data.**
> 

### One-line pitch

> **Detect earlier. Prove why. Act safely. Verify recovery.**
> 

### Technical pitch

> **Deterministic rules catch known violations; multivariate ML catches subtle cross-sensor anomalies; MongoDB provides the operational data and historical reasoning layer; Datadog provides the observability control plane; AI synthesizes structured evidence when useful.**
> 

## 35. Final decision question

> **“If I remove the ML model, LLM and fancy UI, do I still have a legitimate IoT operations system that detects, investigates, responds and proves recovery?”**
> 

Nếu câu trả lời là **yes**, AI đang thêm value.

Nếu **no**, architecture đang được xây quanh demo thay vì operational problem.

## 36. Source links

- UCI MetroPT-3: https://archive.ics.uci.edu/dataset/791/metropt+3+
- MetroPT-3 paper: https://www.nature.com/articles/s41597-022-01877-3
- MongoDB Time Series: https://www.mongodb.com/docs/manual/core/timeseries-collections/
- MongoDB $setWindowFields: https://www.mongodb.com/docs/manual/reference/operator/aggregation/setwindowfields/
- MongoDB TTL: https://www.mongodb.com/docs/manual/core/index-ttl/
- MongoDB Time Series limitations: https://www.mongodb.com/docs/manual/core/timeseries/timeseries-limitations/
- MongoDB Vector Search: https://www.mongodb.com/docs/atlas/atlas-vector-search/
- Datadog IoT Monitoring: https://www.datadoghq.com/solutions/iot-monitoring/
- Datadog Tracing: https://docs.datadoghq.com/tracing/
- Datadog Logs: https://docs.datadoghq.com/logs/

## 37. Final pre-commit checklist

- [ ]  Dataset verified
- [ ]  Failure windows verified
- [ ]  Healthy baseline selected
- [ ]  MongoDB Time Series running
- [ ]  TTL demonstrated
- [ ]  $setWindowFields demonstrated
- [ ]  device_state implemented
- [ ]  incidents implemented
- [ ]  Rule detection implemented
- [ ]  ML baseline trained
- [ ]  Rule vs ML evaluated
- [ ]  Datadog metrics working
- [ ]  Datadog logs working
- [ ]  APM traces working
- [ ]  Datadog monitor working
- [ ]  Incident Engine independent from Datadog timing
- [ ]  Scenario Compiler working
- [ ]  Demo mode ~90s
- [ ]  Real backend behind demo
- [ ]  Remediation simulated
- [ ]  Recovery verified from telemetry
- [ ]  Vector Search only if justified
- [ ]  LLM only if justified
- [ ]  README explains real vs synthetic
- [ ]  Dataset/AI disclosure complete
- [ ]  Video recorded
- [ ]  Final pitch rehearsed