# CompressorGuard: Product Thesis & 90-Second Golden Experience Spec

> **Version:** 1.0 (Post-Spike Vertical Slice Design)  
> **Target:** MUGVN Hackathon 2026 (MongoDB + Datadog)  
> **Core Promise:** **Detect earlier → Prove why → Act safely → Verify recovery.**

---

## 1. Product Thesis (1-Pager — The North Star)

| Dimension | Definition |
| :--- | :--- |
| **Sản phẩm là gì?** | **Incident Command Console cho Thiết bị Vật lý Trọng yếu (Physical Assets)** — Không phải IoT Dashboard, không phải công cụ thống kê anomaly. |
| **User Persona & Role** | **Kỹ sư Giám sát Vận hành Tàu Metro (Fleet Operations Specialist)**. Họ không quan tâm thuật toán; họ cần bảo vệ đoàn tàu khỏi cảnh chết máy giữa đường hầm. |
| **Core Promise** | **Detect earlier → Prove why → Act safely → Verify recovery.** |
| **3 Killer Claims (Bắt buộc phải nhớ)** | 1. **33 giờ 52 phút:** Cảnh báo trước khi còi cơ học tụt áp (`LPS=1`) kịp kêu.<br>2. **Evidence > Anomaly Score:** Bằng chứng nhiệt động lực học có cấu trúc ($\Delta \text{DV} = +23.75\sigma$, $\text{Oil} = +5.71\sigma$, Chu kỳ xác nhận).<br>3. **Closed-Loop Physical Recovery:** Hành động Safe Mode không phải animation; nó rẽ nhánh dữ liệu sang phân đoạn thực tế sau bảo trì để chứng minh máy nén đã nguội và áp suất đã hồi phục. |
| **Nguyên tắc "Không Làm" (Strict Anti-Scope)** | ❌ KHÔNG LLM Chatbot.<br>❌ KHÔNG giả lập hạm đội 50 tàu.<br>❌ KHÔNG thêm thuật toán ML phức tạp.<br>❌ KHÔNG bày bừa biểu đồ đo lường thô khiến màn hình bị loãng. |
| **The 90s Judge Takeaway** | *"Đội này bắt được chiếc máy nén khí chết dần trước 34 tiếng, chỉ rõ lý do vật lý, cho operator ấn chuyển chế độ an toàn, và dùng dữ liệu thật để chứng minh tàu đã an toàn."* |

---

## 2. 90-Second Golden Experience Storyboard (Second-by-Second)

```
00:00                00:20                     00:45                  00:70                00:90s
  │                    │                         │                      │                    │
  ▼                    ▼                         ▼                      ▼                    ▼
[THE STAKES]    [THE INCIDENT CARD]      [WHY WE BELIEVE IT]       [SAFE MODE]         [VERIFIED RECOVERY]
Role: Metro OP   33h 52m Early            +23.75σ Pressure          Rebranching to      5/5 Stable Cycles
Asset at risk    Health: CRITICAL         +5.71σ Temperature        post-maint data     Incident: RESOLVED
```

* **[00:00 - 00:15] Bước vào vai (The Role & Stakes):**
  Màn hình tối giản, nhãn hiệu rõ ràng: `APU-COMP-01 | Metro Lisbon - Linha Azul`.
  Giám khảo lập tức nhận thức: Đây là một trung tâm chỉ huy an toàn chạy tàu.
* **[00:15 - 00:35] Cú đấm trực diện (The Lead Time Hook):**
  Badge cảnh báo màu hổ phách đậm bật sáng:
  `⚠ COMPRESSOR DEGRADATION CONFIRMED — 33H 52M BEFORE CONVENTIONAL ALARM`
  So sánh đối chiếu trực tiếp: Hệ thống cũ (LPS = 1) chỉ biết lúc 19:42 ngày 06/06. CompressorGuard biết từ 09:50 ngày 05/06!
* **[00:35 - 00:55] Dọn bằng chứng ra đĩa (Progressive Disclosure):**
  Không giấu sau các menu phức tạp. 3 thẻ bằng chứng xuất hiện thẳng dưới thông báo:
  1. `Pressure Step: +23.75σ (2.18 bar vs baseline -0.016 bar)`
  2. `Thermal Drift: +5.71σ (74.97°C vs baseline 54.98°C)`
  3. `Regime Corroboration: LOADED (Isolation Forest Score = 0.38)`
* **[00:55 - 00:75] Hành động làm thay đổi thế giới (The Action):**
  Operator nhấn nút lớn màu xanh lục: `[ ACTIVATE REVERSIBLE SAFE MODE ]`.
  State chuyển đổi rõ ràng: `CRITICAL` $\rightarrow$ `MITIGATING (ISOLATING LEAK)`.
* **[00:75 - 00:90] Bằng chứng hồi phục (Physical Recovery Proof):**
  Đồng hồ đo áp suất quay về `-0.016 bar`, nhiệt độ dầu hạ xuống `64°C`.
  Hộp kiểm đếm chu kỳ: `Stabilization: [✓] [✓] [✓] [✓] [✓] (5/5 cycles passed)`.
  Trạng thái đóng sự cố: `STATUS: INCIDENT RESOLVED & VERIFIED`.

---

## 3. Information Architecture (Incident Console Layout)

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  COMPRESSORGUARD // INCIDENT COMMAND CONSOLE                [Asset: APU-COMP-01]  LOADED │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│  🔴 CRITICAL DEGRADATION DETECTED                      ⏱️ 33H 52M EARLY LEAD TIME      │
│     Onset: 2020-06-05 09:50:00                         Conventional LPS: 2020-06-06    │
│                                                                                        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  WHY WE BELIEVE IT (OPERATIONAL EVIDENCE PACK)                                         │
│                                                                                        │
│  ┌───────────────────────┐  ┌───────────────────────┐  ┌────────────────────────────┐  │
│  │ DISCHARGE PRESSURE    │  │ OIL TEMPERATURE       │  │ TEMPORAL & ML CORROBORATION│  │
│  │ 2.18 bar (+23.75σ)    │  │ 74.97 °C (+5.71σ)     │  │ Regime: LOADED             │  │
│  │ [███████████████████] │  │ [████████████░░░░░]   │  │ IF Anomaly Score: 0.38     │  │
│  │ Normal: -0.016 bar    │  │ Normal: 54.98 °C      │  │ Persistence: 3/3 Cycles    │  │
│  └───────────────────────┘  └───────────────────────┘  └────────────────────────────┘  │
│                                                                                        │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  OPERATIONAL RESPONSE & VERIFICATION                                                   │
│                                                                                        │
│  Suggested Mitigation: Isolate Air Dryer Tower 2, switch to safe single-line mode.     │
│                                                                                        │
│  [⚡ ACTIVATE SAFE MODE]                  Current State: MITIGATING                     │
│                                           Telemetry Recovery: 4/5 Cycles               │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```
