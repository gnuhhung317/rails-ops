# CompressorGuard: Vertical Slice Backend & Domain API Implementation Plan (v2.1)

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hiện thực hóa **Vertical Slice Backend v2.1** cho CompressorGuard kết nối trực tiếp với engine hiện tại (`ReplayEngine`, `DecisionEngine`, `EvidenceFusionEngine`, `detectors`). Toàn bộ luồng nghiệp vụ 90 giây (**Phát hiện sớm 33h 52m $\rightarrow$ Bằng chứng nhiệt động lực $\rightarrow$ Kích hoạt Safe Mode $\rightarrow$ Rẽ nhánh luồng dữ liệu sau bảo trì $\rightarrow$ Kiểm chứng phục hồi 5 cửa sổ đánh giá liên tiếp $\rightarrow$ Đóng sự cố**) được điều phối bằng dữ liệu thực 100%, không bịa telemetry, và expose qua API chuẩn mực tách biệt giữa Product API và Demo Controls. **Không viết mã UI/HTML/CSS.**

**Architecture:**
- **Domain Policy Layer:** `RecoveryCriteria` đóng gói tiêu chuẩn nghiệm thu phục hồi thành chính sách miền nghiệp vụ có nguồn gốc (provenance) rõ ràng.
- **Recovery Verification Layer:** `RecoveryVerifier` kiểm tra từng cửa sổ dữ liệu thực tế trong chế độ `LOADED`. Bất kỳ mẫu vi phạm nào cũng lập tức reset số cửa sổ liên tiếp về 0.
- **Orchestration Layer:** `IncidentLifecycleManager` điều phối luồng phát dữ liệu (`degradation` vs `post-maintenance recovery`), quản lý máy trạng thái tường minh (`DETECTED` $\rightarrow$ `INVESTIGATING` $\rightarrow$ `MITIGATING` $\rightarrow$ `VERIFYING_RECOVERY` $\rightarrow$ `RESOLVED`). Không hardcode bất kỳ con số nào thuộc về engine.
- **Interface Layer (FastAPI):** Tách bạch rõ 4 Product Domain Endpoints (`/api/incident`, `/api/evidence`, `/api/action/safe-mode`, `/api/recovery`) và các Simulation Controls (`/demo/reset`, `/demo/tick`, `/demo/jump`), có xử lý lỗi HTTP 409 Conflict cho chuyển đổi trạng thái phi pháp và HTTP 400 cho milestone không hợp lệ.

**Tech Stack:** Python 3.12, FastAPI, Uvicorn, Pandas, Scikit-learn, pytest.

---

## File Structure & Responsibilities

```text
d:/Code/Projects/self-projects/iot-hackathon/
├── docs/
│   ├── PRODUCT_UX_SPEC.md              # [UPDATED v2.1] Product thesis, cognitive hierarchy & API contract
│   └── superpowers/plans/
│       └── 2026-10-06-compressorguard-vertical-slice.md # [THIS FILE v2.1]
├── src/
│   ├── domain/
│   │   ├── enums.py                    # [EXISTING] IncidentLifecycleState, AssetHealthState...
│   │   └── models.py                   # [EXISTING] TelemetryPoint, EvidenceState, Decision...
│   ├── engine/
│   │   ├── recovery.py                 # [NEW] RecoveryCriteria (Policy) + RecoveryVerifier
│   │   ├── lifecycle.py                # [NEW] IncidentLifecycleManager (Orchestration & Stream branching)
│   │   └── ...                         # [EXISTING] detectors, fusion, decision, replay
│   └── api/
│       ├── __init__.py                 # [NEW]
│       ├── schemas.py                  # [NEW] Pydantic DTOs for Product API & Demo responses
│       ├── routes_product.py           # [NEW] 4 Product Endpoints (/api/incident, /evidence, /action, /recovery)
│       ├── routes_demo.py              # [NEW] Demo Controls (/demo/reset, /demo/tick, /demo/jump)
│       └── app.py                      # [NEW] FastAPI factory mounting routes
└── tests/
    ├── test_recovery_verifier.py       # [NEW] Unit test for RecoveryVerifier (with near-success reset test)
    ├── test_lifecycle_orchestrator.py  # [NEW] Orchestration test with exact state transitions & branching
    ├── test_deterministic_replay.py   # [NEW] Two-run deterministic replay comparison test
    └── test_api_vertical_slice.py      # [NEW] End-to-end API test covering happy path and HTTP 409/400 errors
```
