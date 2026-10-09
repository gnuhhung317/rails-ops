# CompressorGuard — Master Task Plan

> **Planning Framework:** `planning-with-files` v2.43.0  
> **Target:** MUGVN Hackathon 2026 (MongoDB + Datadog) & Industrial Commercialization  
> **Core Promise:** Detect earlier → Prove why → Act safely → Verify recovery → Quantify value.  
> **Status:** Active

---

## 1. Goal Statement
Chuyển hóa CompressorGuard từ một Vertical Slice Backend thành một **Hệ thống Điều hành Sự cố Vật lý Cấp Công nghiệp (Industrial Operations Command Platform)** hoàn chỉnh: tích hợp mô hình phân cấp hạm đội (Fleet Spine), tách biệt 3 tầng dữ liệu, mô phỏng hai đồng hồ (Dual-Clock Live Simulation), sổ cái sự kiện CaseEvent, nền tảng dữ liệu MongoDB Atlas (Time Series & Document Collections), bảng quan sát Datadog APM/Traces, và giao diện chỉ huy Operations Console 4 tầng nhận thức.

---

## 2. Invariants & Rules of Engagement
1. **Zero Fake Telemetry:** Dữ liệu cảm biến 100% bắt nguồn từ `MetroPT3(AirCompressor).csv`.
2. **Deterministic Simulation:** Kiểm thử hồi quy đảm bảo tính tất định không đổi qua các lần chạy (63/63 tests passing).
3. **Phân Định 3 Tầng Dữ Liệu:** Business Context (Asset Registry) $\neq$ Observed Telemetry $\neq$ Validation Reference (Ground Truth).
4. **Dual-Clock Architecture:** Giữ nguyên `event_time` gốc lịch sử cho mọi suy luận và kiểm chứng; điều tiết phát dòng bằng `simulation_time`.
5. **ActionGuard & Single Active Case:** Tuân thủ chuẩn công nghiệp Siemens Senseye (tối đa 1 case/asset; 5 kiểm định an toàn trước khi rẽ nhánh).

---

## 3. Implementation Phases & Status

| Phase | Description | Status | Reference / Deliverables |
| :---: | :--- | :---: | :--- |
| **Phase 1** | **Core Domain Backend Vertical Slice v2.1** | `COMPLETE` | 12/12 pytest passed; Replay, Detectors, Fusion, Decision, RecoveryVerifier frozen. |
| **Phase 1.5** | **Rail Economics & Value Model Specification** | `COMPLETE` | `docs/RAIL_ECONOMICS_AND_VALUE_MODEL.md`, `master_context.md` (Phần 8). |
| **Phase 1.8** | **Fleet-Centric Case Architecture & Docs Alignment** | `COMPLETE` | 3 Data Layers, Dual-Clock Live Simulation, Screen 01-07 Specs, ActionGuard, CaseEvent Ledger, Expanded API Contracts. |
| **Phase 2** | **Backend Domain & API Contract Expansion (P0/P1)** | `COMPLETE` | 59/59 pytest passed; AssetRegistry, ScenarioStream dual-clock, ActionGuard, CaseEvent ledger, `/api/operations`, `/api/case`, `/api/case/events`, `/api/case/close`. |
| **Phase 3** | **MongoDB Atlas Multi-Modal Integration** | `COMPLETE` | 63/63 pytest passed; Time Series collection `measurements`, pipeline `$setWindowFields`, `operational_cases`, `case_events`, ingest script. |
| **Phase 4** | **Datadog Unified Observability Integration** | `COMPLETE` | 76/76 pytest passed; DogStatsD metrics, APM distributed tracing, structured JSON logging với `dd.trace_id`, Monitors & Dashboard JSON. |
| **Phase 5** | **Operations Command Console Frontend (Web UI)** | `COMPLETE` | 91/91 pytest passed; Modern SPA in FastAPI, Screens 01-07, 4 Tiers, Dual-clock playback, ActionGuard & Recovery UI. |
| **Phase 6** | **Demo Hardening, 1-Click Simulation & Pitch Deck** | `READY` | 1-Click launcher, evaluation gates (G1-G5), pitch deck, and judging runbook. |

---

## 4. Current Milestone & Next Action
- **Current Milestone:** Phase 5 hoàn tất xuất sắc với 91/91 test vượt qua (100% pass rate). Giao diện chỉ huy vận hành Operations Command Console (Web UI) hiện thực hóa đầy đủ 7 màn hình theo chuẩn Siemens Senseye & Datadog Incident Timelines, chạy trơn tru trực tiếp từ FastAPI mà không phát sinh thêm tiến trình hay bước build nào.
- **Recommended Next Action:** Khởi động **Phase 6: Demo Hardening, 1-Click Simulation & Pitch Deck** (Tạo script chạy 1-click `run_demo.py` / `demo.bat`, kiểm chứng 5 Evaluation Gates G1-G5, chuẩn bị Pitch Deck và kịch bản demo 3 phút).
