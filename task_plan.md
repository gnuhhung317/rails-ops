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
2. **Deterministic Simulation:** Kiểm thử hồi quy đảm bảo tính tất định không đổi qua các lần chạy (59/59 tests passing).
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
| **Phase 3** | **MongoDB Atlas Multi-Modal Integration** | `READY` | Time Series collection `measurements`, pipeline `$setWindowFields`, `operational_cases`, `case_events`. |
| **Phase 4** | **Datadog Unified Observability Integration** | `PENDING` | DogStatsD metrics, `dd-trace` APM, structured JSON logs với `dd.trace_id`. |
| **Phase 5** | **Operations Command Console Frontend (Web UI)** | `PENDING` | 4 Tiers of Progressive Disclosure, Fleet Hierarchy Landing, Case Workspace 4 Questions, Validation Reference Drawer. |
| **Phase 6** | **Demo Hardening, 1-Click Simulation & Pitch Deck** | `PENDING` | Dual-clock pacing controls (1x, 10x, 60x), 5 evaluation gates (G1-G5). |

---

## 4. Current Milestone & Next Action
- **Current Milestone:** Phase 2 hoàn tất xuất sắc với 59/59 test vượt qua (100% pass rate). Toàn bộ Asset Registry, ScenarioStream, ActionGuard, CaseEvent Ledger, và các REST endpoint vận hành (`/api/operations`, `/api/case`, `/api/case/events`, `/api/case/close`) đã sẵn sàng.
- **Recommended Next Action:** Triển khai **Phase 3: MongoDB Atlas Multi-Modal Integration** (lưu trữ Time Series collection `measurements`, document collection `operational_cases`, và `case_events` ledger).
