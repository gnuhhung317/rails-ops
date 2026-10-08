# CompressorGuard

> **Incident Command Console cho Thiết Bị Vật Lý Trọng Yếu (Metro Lisbon APU)**  
> *MUGVN Hackathon 2026 (MongoDB Atlas + Datadog Observability)*  
> **Core Promise:** Detect earlier → Prove why → Act safely → Verify recovery.

---

## 🧭 Điều Hướng Tài Liệu (Documentation Guide)

Dự án tuân thủ cấu trúc tài liệu phân tầng nghiêm ngặt nhằm tối ưu hóa độ chuẩn xác của AI Agent và Kỹ sư phát triển:

* **Tài liệu chuẩn mực duy nhất (SSOT):**  
  👉 [`master_context.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/master_context.md) — Chứa trọn vẹn 100% ngữ cảnh: Persona, Killer Claims, Ground Truth MetroPT-3 (Failure #3), Kiến trúc Vertical Slice v2.1, MongoDB Time Series / Datadog Blueprint, và Lộ trình phát triển 5 giai đoạn.
* **Đặc tả giao diện Frontend (Phase 4):**  
  👉 [`docs/PRODUCT_UX_SPEC.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/docs/PRODUCT_UX_SPEC.md) — Đặc tả wireframe 4 tầng nhận thức và kịch bản trình diễn 90 giây.
* **Kế hoạch thực thi (Superpowers Plans):**  
  👉 [`docs/superpowers/plans/`](file:///d:/Code/Projects/self-projects/iot-hackathon/docs/superpowers/plans/) — Nhật ký và kế hoạch thực thi chi tiết của từng giai đoạn.
* **Kho lưu trữ lịch sử nghiên cứu & logs cũ:**  
  👉 [`docs/archive/`](file:///d:/Code/Projects/self-projects/iot-hackathon/docs/archive/) — Toàn bộ bản nháp, spike reports, specs v1 và session logs trước khi tổng hợp SSOT.

---

## ⚡ Quickstart: Chạy Kiểm Thử Backend Vertical Slice v2.1

```bash
# Cài đặt phụ thuộc
pip install -r requirements.txt

# Chạy toàn bộ integration test suite của Vertical Slice (100% deterministic)
python -m pytest tests/test_api_vertical_slice.py tests/test_deterministic_replay.py tests/test_decision.py -v
```

---

## 🏗️ Kiến Trúc Hệ Thống (Frozen Backend Vertical Slice v2.1)

```text
MetroPT-3 Replay Stream (Failure #3: June 5-8, 2020)
       ↓
Regime Classifier (STANDBY / LOADED / UNLOADED)
       ↓
Multivariate Detectors (Pressure + Thermal Drift + Temporal Step Persistence + Isolation Forest)
       ↓
Evidence Fusion Engine (Deterministic Evidence State)
       ↓
Decision Engine (Incident Creation & Operational Confidence)
       ↓
Closed-Loop Lifecycle Manager (Active Incident → Safe Mode Branching → 5 Consecutive Recovery Checks)
```

Chi tiết kiến trúc, API contract schemas và roadmap tiếp theo xem tại [`master_context.md`](file:///d:/Code/Projects/self-projects/iot-hackathon/master_context.md).
