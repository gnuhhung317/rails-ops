# Backend Semantic Cleanup & Vertical Slice Freeze Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clean up the 3 remaining semantic mismatches in the backend vertical slice (unify observation terminology across domain models, evaluator, detector, schemas, and tests; derive 33h52m lead-time dynamically from detection and verified LPS milestone timestamps; include temporal persistence as 4th signal in evidence pack) and freeze the backend domain & API contract before proceeding to UX review.

**Architecture:** Enforce the strict domain rule: **No cycle, window, or sample in any public domain model or API contract**. All contracts standardize on **observations**. `RecoveryStatus` in `src/domain/models.py` is updated to `consecutive_healthy_observations` and `target_healthy_observations`. Lead-time is dynamically derived in `IncidentLifecycleManager` from the detection timestamp and verified LPS milestone timestamp. Legacy aliases are strictly internal-only and forbidden from API schemas, responses, provenance dictionaries, and UX specifications.

**Tech Stack:** Python 3.12, FastAPI, Pydantic v2, Pandas, Scikit-learn, pytest.

---

## File Structure & Responsibilities

- **Modify:** `src/domain/models.py`
  - In `RecoveryStatus`: rename `consecutive_healthy_cycles` -> `consecutive_healthy_observations`, `target_healthy_cycles` -> `target_healthy_observations`.
- **Modify:** `src/engine/recovery.py`
  - Rename `target_healthy_windows` -> `target_healthy_observations`, `consecutive_healthy_windows` -> `consecutive_healthy_observations`, `is_window_healthy` -> `is_observation_healthy`.
  - Refine policy documentation: state clearly that `RecoveryCriteria` is a deterministic domain acceptance policy for MetroPT-3 post-maintenance validation, without overclaiming external provenance metadata.
  - Internal-only properties (`consecutive_healthy_windows`, `target_healthy_windows`) remain strictly internal.
- **Modify:** `src/engine/detectors.py`
  - In `TemporalStepDetector`: constructor takes `required_observations: int = 3`, `baseline_observations: int = 5`.
  - Internal-only fallback: `required_cycles`, `baseline_cycles` mapped internally.
  - Provenance dictionary MUST strictly emit observation keys: `"required_observations"`, `"baseline_observations"`, `"recent_observations"` (no cycle/window keys).
- **Modify:** `src/api/schemas.py`
  - In `PersistenceInfo`: strictly `confirmed: bool`, `recent_observations: int`, `required_observations: int`.
  - In `RecoveryResponse`: strictly `consecutive_healthy_observations: int`, `target_healthy_observations: int`.
  - In `EvidenceSignalItem`: supports `TEMPORAL_STEP_CONFIRMED` mapping (`observed_value=step_diff`, `baseline_value=0.0`, `unit="bar_diff"`, `sigma_deviation=0.0`).
- **Modify:** `src/engine/lifecycle.py`
  - In `get_incident_payload()`: derive `lead_time_minutes`, `lead_time_formatted = f"{lead_hours}h {lead_mins:02d}m"`, and ISO timestamps dynamically from detection timestamp (`actual_detection_dt`) and verified LPS milestone timestamp (`pd.to_datetime(self.milestones["lps_reactive_1942"])`). Derive `summary` from `active_incident.summary` or `current_decision.reason`.
  - In `get_evidence_payload()`: include `TEMPORAL_STEP_CONFIRMED` as the 4th signal in `evidence_pack` (code `TEMPORAL_STEP_CONFIRMED`, signal name `"Temporal Persistence Tracking"`, observed_value `sig.observed_value`, baseline_value `0.0`, unit `"bar_diff"`, sigma_deviation `0.0`, status `"CONFIRMED"`, is_primary `False`), while also providing `persistence` with `{ confirmed, recent_observations, required_observations }`.
  - In `get_recovery_payload()`: output `consecutive_healthy_observations` and `target_healthy_observations`.
- **Modify:** `tests/test_golden_path.py`
  - Update `RecoveryStatus` attributes in `run_golden_path_simulation` to `consecutive_healthy_observations` and `target_healthy_observations`.
- **Modify:** `tests/test_recovery_verifier.py`
  - Update all assertions and attribute names to `consecutive_healthy_observations`, `target_healthy_observations`, `is_observation_healthy`.
- **Modify:** `tests/test_lifecycle_orchestrator.py`
  - Update recovery payload assertions and lead time dynamic verification.
- **Modify:** `tests/test_api_vertical_slice.py`
  - Update assertions for `recent_observations`, `consecutive_healthy_observations`, and presence of all 4 signals (including `TEMPORAL_STEP_CONFIRMED`) in `evidence_pack`.
- **Modify:** `tests/test_deterministic_replay.py`
  - Clarify docstring and assertion message to "Two-run deterministic replay".
- **Modify:** `docs/PRODUCT_UX_SPEC.md`
  - Update API JSON examples and terminology to match the frozen contract.

---

### Task 1: Unify Observation Terminology in Domain & Detector Models

**Files:**
- Modify: `src/domain/models.py`
- Modify: `src/engine/recovery.py`
- Modify: `src/engine/detectors.py`
- Modify: `src/api/schemas.py`
- Modify: `tests/test_golden_path.py`
- Test: `tests/test_recovery_verifier.py`

- [x] **Step 1: Update `src/domain/models.py`**

Refactor `RecoveryStatus` to use observation terminology:
```python
class RecoveryStatus(BaseModel):
    asset_id: str = "APU-COMP-01"
    is_recovering: bool = False
    consecutive_healthy_observations: int = 0
    target_healthy_observations: int = 5
    is_verified: bool = False
    verification_reason: str = ""
```
Also update `tests/test_golden_path.py` (lines 126, 128, 130) where `recovery_status.consecutive_healthy_cycles` and `recovery_status.target_healthy_cycles` are used to use `consecutive_healthy_observations` and `target_healthy_observations`.

- [x] **Step 2: Update `tests/test_recovery_verifier.py` with observation terminology**

```python
from datetime import datetime
import pytest

from src.domain.enums import OperatingRegime
from src.domain.models import TelemetryPoint
from src.engine.recovery import (
    RecoveryCriteria,
    RecoveryEvaluationResult,
    RecoveryVerifier,
)
...
```

- [x] **Step 3: Update `src/engine/recovery.py`**

Refactor `RecoveryCriteria`, `RecoveryEvaluationResult`, `RecoveryVerifier` to use `observations`. Remove overclaiming about provenance registries; clearly state it is a domain validation policy. Internal property aliases (`consecutive_healthy_windows`, `target_healthy_windows`) remain internal-only.

- [x] **Step 4: Update `src/engine/detectors.py`**

Update `TemporalStepDetector`:
```python
class TemporalStepDetector(BaseDetector):
    def __init__(
        self,
        step_threshold: float = 0.5,
        required_observations: int = 3,
        baseline_observations: int = 5,
        allowed_regime_gaps: int = 0,
        # Internal-only legacy parameter fallback
        required_cycles: Optional[int] = None,
        baseline_cycles: Optional[int] = None,
    ):
...
```
In provenance, record strictly observation keys:
`"required_observations": self.required_observations, "baseline_observations": self.baseline_observations, "recent_observations": len(recent)`

- [x] **Step 5: Update `src/api/schemas.py`**

Update `PersistenceInfo`:
```python
class PersistenceInfo(BaseModel):
    confirmed: bool
    recent_observations: int
    required_observations: int
```
Update `RecoveryResponse`:
```python
class RecoveryResponse(BaseModel):
    incident_id: str
    is_recovering: bool
    is_verified: bool
    consecutive_healthy_observations: int
    target_healthy_observations: int
    latest_telemetry: LatestTelemetry
    criteria: RecoveryCriteriaInfo
```

- [x] **Step 6: Run `pytest tests/test_recovery_verifier.py -v` to confirm it passes**

Expected: 5 passed. (Verified: 5 passed in 0.33s).

---

### Task 2: Dynamic Lead Time & Summary Derivation in Lifecycle Manager

**Files:**
- Modify: `src/engine/lifecycle.py`
- Test: `tests/test_lifecycle_orchestrator.py`

- [x] **Step 1: Write test in `tests/test_lifecycle_orchestrator.py` asserting dynamic calculation**

Verify that `get_incident_payload()` derives `lead_time_minutes` and `lead_time_formatted` from the actual detection timestamp and the verified LPS milestone timestamp.

- [x] **Step 2: Run test to verify failure / mismatch**

Run: `pytest tests/test_lifecycle_orchestrator.py -v`

- [x] **Step 3: Implement dynamic calculation in `src/engine/lifecycle.py`**

In `get_incident_payload(self)`:
```python
    actual_lps_dt = pd.to_datetime(self.milestones["lps_reactive_1942"])
    if self.active_incident and self.active_incident.created_at:
        actual_detection_dt = self.active_incident.created_at
    else:
        actual_detection_dt = pd.to_datetime(self.milestones["onset_0950"])

    delta = actual_lps_dt - actual_detection_dt
    lead_time_minutes = max(0, int(round(delta.total_seconds() / 60.0)))
    lead_hours = lead_time_minutes // 60
    lead_mins = lead_time_minutes % 60
    lead_time_formatted = f"{lead_hours}h {lead_mins:02d}m"
```

- [x] **Step 4: Run `pytest tests/test_lifecycle_orchestrator.py -v`**

Expected: PASS. (Verified: 3 passed in 7.41s).

---

### Task 3: Include Temporal Signal in `evidence_pack` & Align Recovery Payload

**Files:**
- Modify: `src/engine/lifecycle.py`
- Modify: `tests/test_lifecycle_orchestrator.py`
- Modify: `tests/test_api_vertical_slice.py`

- [x] **Step 1: Write test assertions in `tests/test_lifecycle_orchestrator.py` and `tests/test_api_vertical_slice.py`**

Assert that:
1. `ev_payload["evidence_pack"]` contains 4 signals: Discharge Valve Pressure, Compressor Oil Temperature, Temporal Persistence Tracking, Multivariate Isolation Forest.
2. `TEMPORAL_STEP_CONFIRMED` maps strictly to:
   - `observed_value`: `sig.observed_value` (the `step_diff`)
   - `baseline_value`: `0.0`
   - `unit`: `"bar_diff"`
   - `sigma_deviation`: `0.0`
   - `status`: `"CONFIRMED"`
   - `is_primary`: `False`
3. `ev_payload["persistence"]` has keys `confirmed`, `recent_observations`, `required_observations`.
4. `rec_payload` has `consecutive_healthy_observations` and `target_healthy_observations`.

- [x] **Step 2: Run test to verify failure**

Run: `pytest tests/test_lifecycle_orchestrator.py tests/test_api_vertical_slice.py -v`  
Expected: FAIL on missing temporal signal and observation field names.

- [x] **Step 3: Implement in `src/engine/lifecycle.py`**

In `get_evidence_payload()`:
Append `TEMPORAL_STEP_CONFIRMED` to `evidence_pack` and serialize observation fields in `persistence`.
In `get_recovery_payload()`:
Output `consecutive_healthy_observations` and `target_healthy_observations`.

- [x] **Step 4: Run test to verify passes**

Run: `pytest tests/test_lifecycle_orchestrator.py tests/test_api_vertical_slice.py -v`  
Expected: PASS. (Verified: 3 passed in 10.12s).

---

### Task 4: Replay Determinism Clarification & Full Test Suite Audit

**Files:**
- Modify: `tests/test_deterministic_replay.py`
- Run: Full test suite

- [x] **Step 1: Update docstrings & assertion in `tests/test_deterministic_replay.py`**

Change:
`"Two-run deterministic replay must produce identical simulation outputs across reset cycles"` (Verified: passed in 8.82s).

- [x] **Step 2: Run full test suite across entire repository**

Run: `pytest tests -v`  
Expected: All tests in `tests/` pass with 0 failures and 0 errors (24 tests expected in the current suite).  
Result: **24 passed in 118.99s (0 failures, 0 errors)**.

---

### Task 5: Freeze Contract & Update Specification Documentation

**Files:**
- Modify: `docs/PRODUCT_UX_SPEC.md`

- [x] **Step 1: Synchronize `docs/PRODUCT_UX_SPEC.md`**

1. Section 1 & Section 4: replace "windows" with "observations" (`consecutive_healthy_observations`, `target_healthy_observations`).
2. Section 5.1:
   - `GET /api/incident`: document dynamic lead time formula derived from detection timestamp and verified LPS milestone ($T_{\text{LPS}} - T_{\text{detection}} = 33\text{h } 52\text{m}$).
   - `GET /api/evidence`: show `evidence_pack` containing all 4 signals (`PRESSURE_SEVERE`, `THERMAL_STRESS_SEVERE`, `TEMPORAL_STEP_CONFIRMED`, `ML_CORROBORATED`), and `persistence` block with `recent_observations` and `required_observations`.
   - `GET /api/recovery`: show `consecutive_healthy_observations` and `target_healthy_observations`.
3. Mark status: **Backend Vertical Slice Contract: FROZEN (v2.2)**. Ready for UX Spec Stress-Test.

- [ ] **Step 2: Commit changes**

Run:
```bash
git add src/ tests/ docs/
git commit -m "fix(backend): harmonize observation semantics, derive dynamic lead-time, and freeze contract"
```

