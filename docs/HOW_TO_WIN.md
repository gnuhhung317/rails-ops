Điểm đáng chú ý là: tôi không nghĩ điểm yếu lớn nhất của bạn là công nghệ. Nó nằm ở cách bạn biến công nghệ thành một bài thi có khả năng thắng.

1. Bạn đang có nguy cơ tối ưu “đúng đề” hơn là tối ưu “điểm”

CompressorGuard hiện cover rất nhiều thứ:

MongoDB Time Series
$setWindowFields
TTL
ML
Datadog
Metrics / Logs / Traces
Incident lifecycle
AI
Vector Search
Recovery verification

Nghe rất mạnh.

Nhưng nhiều checkbox ≠ giải nhất.

Ban giám khảo có thể nhớ:

“Một hệ thống predictive maintenance dùng MongoDB + Datadog.”

Trong khi đội thắng thường khiến họ nhớ:

“À, cái đội mà khi compressor bắt đầu hỏng, hệ thống phát hiện → chỉ ra bằng chứng → quyết định xử lý → và chứng minh nó đã hồi phục.”

Điểm mù: bạn có thể đang xây technology showcase, trong khi giải nhất cần operational story.

2. Bạn chưa có “10 giây khiến giám khảo hiểu tại sao phải tồn tại”

Đây là thứ tôi sẽ cực kỳ nghiêm khắc.

Nếu mở demo bằng:

“We use MetroPT-3 dataset, MongoDB Time Series, Isolation Forest…”

thì gần như đã thua về storytelling.

Họ phải hiểu trước:

Compressor hỏng → tàu có thể bị đưa khỏi vận hành → phát hiện càng sớm càng tốt → nhưng operator phải biết có chuyện gì và đã xử lý xong chưa.

Sau đó mới:

“Đó là vấn đề CompressorGuard giải quyết.”

Nếu một judge không hiểu domain trong 15–20 giây, phần MongoDB/ML phía sau sẽ giảm giá trị rất mạnh.

3. “AI” có thể trở thành điểm trừ nếu bạn nhét nó vào chỉ vì hackathon

Đây là điểm tôi đặc biệt cảnh giác.

Bạn hiện có khá nhiều ý tưởng AI:

Isolation Forest
Vector Search
LLM Investigator
evidence synthesis
forecasting
similar incidents

Nếu làm hết, rất dễ thành:

“AI wrapper + dashboard + database.”

Trong khi AI tốt nhất ở đây phải trả lời một câu rất cụ thể:

“Tại sao hệ thống nghĩ compressor đang có vấn đề?”

Ví dụ:

INCIDENT #1042

Anomaly score: 0.91
Health: 62 → 41

Evidence:
• pressure variance: +4.1σ
• pressure instability: +3.6σ
• motor current slope: +2.8σ
• pattern persisted for 37 sec

Similar historical incidents:
2 previous cases
→ same degradation pattern
→ maintenance required

Đây mới là AI có giá trị.

AI không nên là nhân vật chính. Evidence mới là nhân vật chính.

4. Điểm mù nguy hiểm nhất: bạn có thể chưa chứng minh được “earlier”

Tên pitch của bạn là:

Detect earlier. Prove why. Act safely. Verify recovery.

Nhưng “earlier” là claim quan trọng nhất.

Bạn phải trả lời bằng số liệu:

Rule-based system phát hiện lúc T+X.
ML phát hiện lúc T+Y.
Failure/maintenance ground truth xảy ra lúc T+Z.
→ ML cho lead time = Z−Y.

Nếu không có experiment này, “predictive maintenance” rất dễ biến thành marketing.

Tôi thậm chí sẽ coi:

Rule vs ML experiment > Vector Search > LLM

về giá trị cạnh tranh.

5. Bạn có nguy cơ overfit vào một failure window

Đây là vấn đề ML khá nghiêm trọng.

Nếu bạn chọn một đoạn MetroPT-3 đẹp → train model → demo đúng đoạn đó → model bắt được rất đẹp.

Judge hỏi:

“How do you know this generalizes?”

Bạn phải có câu trả lời.

Ít nhất nên có:

train / validation / test split theo time
healthy periods
nhiều failure/degradation windows nếu dataset cho phép
false positive analysis
rule-only baseline
ML-only / rule+ML comparison

Và đặc biệt:

Không random split time-series một cách ngây thơ.

Nếu leakage xảy ra, accuracy đẹp nhưng bài thi yếu.

6. “Root cause” là một cái bẫy ngôn ngữ

Bạn rất dễ nói:

“AI identifies the root cause.”

Trong khi model thực tế chỉ nói:

“Multivariate behavior is anomalous.”

Hai cái đó khác nhau rất xa.

Nên dùng hierarchy:

Detection
→ “Something abnormal is happening.”

Evidence
→ “These signals changed.”

Hypothesis
→ “The pattern is consistent with X.”

Root cause
→ chỉ nói khi ground truth/evidence đủ mạnh.

Điều này paradoxically làm project trông trưởng thành hơn, không yếu hơn.

7. Recovery verification có thể trở thành “wow moment” của bạn — nhưng hiện chưa đủ nổi

Nhiều đội sẽ làm:

anomaly → alert.

Bạn làm:

anomaly → investigation → action → prove recovery.

Đây là một differentiator rất tốt.

Ví dụ demo:

10:32:41  INCIDENT DETECTED
10:32:43  INVESTIGATION STARTED
10:32:51  ABNORMAL PRESSURE PATTERN CONFIRMED
10:33:02  REMEDIATION EXECUTED
10:33:17  PRESSURE STABILIZING
10:33:26  RECOVERY VERIFIED

Incident duration: 45s
Health: 38 → 91
Status: RESOLVED

Judge nhìn thấy một lifecycle hoàn chỉnh, thay vì dashboard.

Tôi sẽ đẩy phần này rất mạnh.

8. Bạn có thể đang đánh giá thấp “demo engineering”

Hackathon thắng không chỉ bằng architecture.

Một project cực kỳ thông minh nhưng:

demo fail
latency
Datadog dashboard load chậm
ML inference lỗi
network lỗi
data replay không deterministic
UI không biết backend đang state nào

→ có thể thua một project đơn giản hơn nhưng demo như đồng hồ.

Vì vậy tôi sẽ coi Demo Reliability là một engineering requirement, không phải polish.

Đặc biệt phải có:

1 command → reset → run → incident → recovery

Không phụ thuộc vào thao tác thủ công.

9. Bạn đang có một câu hỏi mà phải trả lời cực chắc:

“Why MongoDB?”

Không được trả lời:

“Because MongoDB is mandatory.”

Câu trả lời phải là:

Telemetry là time-series data, nhưng incident investigation không chỉ cần đọc từng datapoint. Chúng tôi cần kết hợp temporal telemetry, device state, incident history và operational evidence để reason về một incident.

Rồi MongoDB architecture phải thực sự thể hiện điều đó.

Nếu judge thấy MongoDB chỉ là:

CSV → MongoDB → dashboard

thì mất điểm.

Nếu thấy:

Telemetry
   ↓
Window analytics
   ↓
Device state
   ↓
Incident
   ↓
Evidence
   ↓
Historical incidents
   ↓
Investigation

thì khác hoàn toàn.

10. Và đây là điểm mù lớn nhất của bạn: bạn đang nghĩ như engineer trước khi nghĩ như judge

Tôi thấy pattern này khá rõ trong cách bạn phát triển đề tài.

Bạn rất nhanh nghĩ tới:

MongoDB → Datadog → ML → Vector Search → LLM → architecture...

Nhưng judge nghĩ theo thứ tự gần như ngược lại:

Có vấn đề thật không?
↓
Tôi có hiểu nó không?
↓
Hệ thống này giải quyết nó tốt hơn cách bình thường thế nào?
↓
Có bằng chứng không?
↓
MongoDB/Datadog có thực sự cần thiết không?
↓
Có đáng tin không?
↓
Wow.

Đây là thứ tôi nghĩ bạn nên sửa trong tư duy ngay từ bây giờ.

Nếu tôi muốn ép CompressorGuard thành ứng viên giải nhất

Tôi sẽ đặt 5 “gates”:

Gate	Câu hỏi
G1 — Business	Judge hiểu vấn đề trong 20s không?
G2 — Detection	Có chứng minh detect sớm hơn không?
G3 — Investigation	Có chứng minh why không?
G4 — Response	Có action + recovery thật không?
G5 — Technology	MongoDB + Datadog + AI có tạo ra năng lực mà cách đơn giản không có không?

Và tôi sẽ ưu tiên theo:

G1 → G2 → G3 → G4 → G5

chứ không phải:

MongoDB → ML → AI → UI → presentation.

Nếu chỉ được chọn 3 thứ để làm cực sâu

Tôi sẽ chọn:

🥇 1. Detection lead time + Rule vs ML

Đây là proof.

🥈 2. Incident investigation narrative

Đây là wow.

🥉 3. Deterministic end-to-end demo + recovery verification

Đây là trust.

Vector Search, LLM, fancy frontend... đều đứng sau ba thứ này.

Và có một điều tôi muốn bạn giữ trong đầu:

Đừng cố làm project “nhiều công nghệ nhất”.

Hãy làm project mà sau 5 phút judge có thể kể lại chính xác:
“Compressor bắt đầu có vấn đề → hệ thống thấy nó sớm → cho tôi biết tại sao → tôi xử lý → hệ thống xác nhận nó đã ổn.”

Nếu làm được mức đó và chứng minh bằng số liệu rằng ML thực sự đem lại lead time/giảm false positive, lúc ấy CompressorGuard mới bắt đầu có dáng của ứng viên giải nhất, chứ không chỉ là một project kỹ thuật tốt.