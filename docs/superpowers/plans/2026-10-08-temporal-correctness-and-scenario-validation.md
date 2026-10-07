# Temporal Correctness, Policy Boundary & Cross-Scenario Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve the 6 critical backend semantic and architectural gaps identified in the review (P0 temporal continuity in `TemporalStepDetector` and `RecoveryVerifier`, P1 Safe Mode policy boundary enforcement, P1 ML score calibration defense, P1 early excursion 67h09 inclusion, P0 ScenarioDefinition decoupling, and `DecisionEngine` active lifecycle state check) before proceeding to MongoDB, Datadog, or UI.

**Architecture:** Enforce strict temporal contiguity validation across all time-series detectors and recovery verifiers using an explicit policy (`max_observation_gap_seconds=30.0`). Decouple historical scenario knowledge from `IncidentLifecycleManager` by introducing an injectable `ScenarioDefinition` supporting Failure #3, Failure #1, Failure #4, and Healthy scenarios. Close the Safe Mode policy boundary so `DecisionEngine` emits `recommended_action = EXECUTE_MITIGATION` and API/Lifecycle strictly authorizes execution only when recommended. Formally document and verify Isolation Forest score calibration against real dataset telemetry.

**Tech Stack:** Python 3.12, FastAPI, Pydantic v2, Scikit-learn, Pandas, pytest.

---

## File Structure & Responsibilities

- **Create:** `pytest.ini`
  - Restricts pytest collection to `tests/` directory to prevent collection collision with scratch or debug scripts.
- **Modify:** `src/engine/recovery.py`
  - Add `max_observation_gap_seconds: float = 30.0` to `RecoveryCriteria`.
  - Track `last_healthy_timestamp: Optional[datetime]` in `RecoveryVerifier`.
  - Break continuity (reset counter to 1) if $\Delta t > \text{max\_observation\_gap\_seconds}$.
- **Modify:** `src/engine/detectors.py`
  - Add `max_observation_gap_seconds: float = 30.0` to `TemporalStepDetector`.
  - Verify that adjacent observations in `recent` satisfy $(t_{i+1} - t_i) \le \text{max\_observation\_gap\_seconds}$.
  - Return `NORMAL` if temporal continuity is broken.
- **Modify:** `src/domain/enums.py`
  - Ensure `IncidentAction.EXECUTE_MITIGATION` is cleanly integrated.
- **Modify:** `src/domain/models.py`
  - Add `recommended_action: IncidentAction = IncidentAction.NONE` to `Decision`.
  - Add `ScenarioDefinition` model containing stream bounds, recovery bounds, LPS milestone, and milestones dictionary.
- **Modify:** `src/engine/decision.py`
  - Define `ACTIVE_INCIDENT_STATES = { DETECTED, INVESTIGATING, MITIGATING, VERIFYING_RECOVERY }`.
  - Set `recommended_action = IncidentAction.EXECUTE_MITIGATION` on ML Corroboration and LPS triggers.
- **Modify:** `src/engine/lifecycle.py`
  - Accept injectable `scenario: Optional[ScenarioDefinition] = None`.
  - In `trigger_safe_mode()`: validate `current_decision.recommended_action == IncidentAction.EXECUTE_MITIGATION`.
  - Support `early_excursion_0033` milestone seeking.
- **Create:** `src/domain/scenarios.py`
  - Define `ScenarioDefinition` presets: `FAILURE_3_SCENARIO`, `FAILURE_1_SCENARIO`, `FAILURE_4_SCENARIO`, `HEALTHY_SCENARIO`.
- **Create:** `scripts/verify_golden_path_evidence.py`
  - Streams real MetroPT-3 CSV dataset and outputs a frozen verification artifact at each milestone with raw and calibrated ML scores.
- **Create:** `docs/ml-score-calibration.md`
  - Mathematical documentation explaining Isolation Forest `decision_function` scaling and defensibility for judges.
- **Create:** `tests/test_temporal_continuity.py`
  - Unit tests specifically validating temporal continuity in `TemporalStepDetector` and `RecoveryVerifier` across gaps, regime changes, and normal intervals.
- **Create:** `tests/test_scenarios.py`
  - Multi-scenario validation tests for Failure #3, Failure #1, Failure #4, and Healthy negative control.
- **Modify:** `tests/test_recovery_verifier.py`
  - Update timestamps in test helpers to adhere to realistic 10-second increments.
- **Modify:** `tests/test_lifecycle_orchestrator.py` & `tests/test_api_vertical_slice.py`
  - Assert policy boundary enforcement: Safe Mode rejected before recommendation, authorized after recommendation.

---

### Task 1: Add pytest.ini Configuration

**Files:**
- Create: `pytest.ini`

- [ ] **Step 1: Write `pytest.ini`**

```ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -v
```

- [ ] **Step 2: Run pytest to verify test collection is isolated to `tests/`**

Run: `pytest --collect-only`
Expected: 24 tests collected from `tests/` directory with 0 errors.

- [ ] **Step 3: Commit**

```bash
git add pytest.ini
git commit -m "chore: add pytest.ini to isolate test collection"
```

---

### Task 2: Implement Temporal Continuity in RecoveryVerifier (P0)

**Files:**
- Modify: `src/engine/recovery.py`
- Modify: `tests/test_recovery_verifier.py`
- Test: `tests/test_temporal_continuity.py`

- [ ] **Step 1: Write failing tests for RecoveryVerifier temporal continuity**

Create `tests/test_temporal_continuity.py` with failing assertions:

```python
from datetime import datetime, timedelta
import pytest
from src.domain.enums import OperatingRegime
from src.domain.models import TelemetryPoint
from src.engine.recovery import RecoveryCriteria, RecoveryVerifier

def _make_pt(ts: datetime, dv: float = 0.02, temp: float = 60.0, regime: OperatingRegime = OperatingRegime.LOADED) -> TelemetryPoint:
    return TelemetryPoint(
        asset_id="APU-COMP-01",
        timestamp=ts,
        tp2_bar=0.0,
        tp3_bar=9.5,
        h1_bar=9.5,
        dv_pressure_bar=dv,
        reservoirs_bar=9.5,
        oil_temp_c=temp,
        motor_current_a=3.8,
        comp_val=1.0,
        dv_electric=0.0,
        towers_val=1.0,
        mpg_val=1.0,
        lps_active=0.0,
        pressure_switch=0.0,
        oil_level_low=0.0,
        caudal_impulses=1.0,
        regime=regime,
    )

def test_recovery_continuity_3_observations_at_10s_succeeds():
    verifier = RecoveryVerifier(RecoveryCriteria(target_healthy_observations=3, max_observation_gap_seconds=30.0))
    t0 = datetime(2020, 6, 8, 16, 5, 0)
    res1 = verifier.evaluate(_make_pt(t0))
    res2 = verifier.evaluate(_make_pt(t0 + timedelta(seconds=10)))
    res3 = verifier.evaluate(_make_pt(t0 + timedelta(seconds=20)))
    assert res1.consecutive_healthy_observations == 1
    assert res2.consecutive_healthy_observations == 2
    assert res3.consecutive_healthy_observations == 3
    assert res3.is_verified is True

def test_recovery_continuity_broken_by_60s_gap():
    verifier = RecoveryVerifier(RecoveryCriteria(target_healthy_observations=3, max_observation_gap_seconds=30.0))
    t0 = datetime(2020, 6, 8, 16, 5, 0)
    verifier.evaluate(_make_pt(t0))
    verifier.evaluate(_make_pt(t0 + timedelta(seconds=10)))
    # 60 second gap before observation 3
    res3 = verifier.evaluate(_make_pt(t0 + timedelta(seconds=70)))
    # Streak must be reset to 1 (current point is healthy, but continuity from past was broken)
    assert res3.consecutive_healthy_observations == 1
    assert res3.is_verified is False

def test_recovery_regime_gap_over_max_gap_breaks_continuity():
    verifier = RecoveryVerifier(RecoveryCriteria(target_healthy_observations=3, max_observation_gap_seconds=30.0))
    t0 = datetime(2020, 6, 8, 16, 5, 0)
    verifier.evaluate(_make_pt(t0))
    verifier.evaluate(_make_pt(t0 + timedelta(seconds=10)))
    # 60s spent in OFF regime
    verifier.evaluate(_make_pt(t0 + timedelta(seconds=40), regime=OperatingRegime.OFF))
    # Return to LOADED after gap
    res4 = verifier.evaluate(_make_pt(t0 + timedelta(seconds=80), regime=OperatingRegime.LOADED))
    assert res4.consecutive_healthy_observations == 1
    assert res4.is_verified is False
```

- [ ] **Step 2: Run test to verify failure**

Run: `pytest tests/test_temporal_continuity.py -v`
Expected: FAIL (`AttributeError: 'RecoveryCriteria' object has no attribute 'max_observation_gap_seconds'` or streak not reset).

- [ ] **Step 3: Update `src/engine/recovery.py` with temporal continuity validation**

```python
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from src.domain.enums import OperatingRegime
from src.domain.models import TelemetryPoint

class RecoveryCriteria(BaseModel):
    target_healthy_observations: int = Field(default=5, ge=1)
    dv_pressure_max: float = Field(default=0.05, gt=0.0)
    oil_temp_max: float = Field(default=67.0, gt=0.0)
    required_regime: OperatingRegime = OperatingRegime.LOADED
    max_observation_gap_seconds: float = Field(default=30.0, gt=0.0)

    @property
    def target_healthy_windows(self) -> int:
        return self.target_healthy_observations
```

In `RecoveryVerifier`:
```python
class RecoveryVerifier:
    def __init__(self, criteria: Optional[RecoveryCriteria] = None) -> None:
        self.criteria: RecoveryCriteria = criteria or RecoveryCriteria()
        self.consecutive_healthy_observations: int = 0
        self.is_verified: bool = False
        self.last_healthy_timestamp: Optional[datetime] = None

    def reset(self) -> None:
        self.consecutive_healthy_observations = 0
        self.is_verified = False
        self.last_healthy_timestamp = None

    def evaluate(self, point: TelemetryPoint) -> RecoveryEvaluationResult:
        if point.regime != self.criteria.required_regime:
            return RecoveryEvaluationResult(
                is_applicable_regime=False,
                is_observation_healthy=False,
                consecutive_healthy_observations=self.consecutive_healthy_observations,
                target_healthy_observations=self.criteria.target_healthy_observations,
                is_verified=self.is_verified,
                reason=(
                    f"Regime '{point.regime}' does not match required regime "
                    f"'{self.criteria.required_regime}'; evaluation suspended."
                ),
            )

        pressure_ok = point.dv_pressure_bar < self.criteria.dv_pressure_max
        temp_ok = point.oil_temp_c < self.criteria.oil_temp_max
        is_healthy = pressure_ok and temp_ok

        if is_healthy:
            if self.last_healthy_timestamp is not None:
                gap = (point.timestamp - self.last_healthy_timestamp).total_seconds()
                if gap > self.criteria.max_observation_gap_seconds:
                    # Time gap broken: reset streak to 1
                    self.consecutive_healthy_observations = 1
                else:
                    self.consecutive_healthy_observations += 1
            else:
                self.consecutive_healthy_observations = 1

            self.last_healthy_timestamp = point.timestamp

            if self.consecutive_healthy_observations >= self.criteria.target_healthy_observations:
                self.is_verified = True
                reason = (
                    f"Recovery verified: {self.consecutive_healthy_observations}/"
                    f"{self.criteria.target_healthy_observations} consecutive healthy observations achieved."
                )
            else:
                reason = (
                    f"Healthy observation {self.consecutive_healthy_observations}/"
                    f"{self.criteria.target_healthy_observations} in regime {self.criteria.required_regime}."
                )
        else:
            self.consecutive_healthy_observations = 0
            self.is_verified = False
            self.last_healthy_timestamp = None
            violations = []
            if not pressure_ok:
                violations.append(f"dv_pressure={point.dv_pressure_bar:.4f} >= max {self.criteria.dv_pressure_max}")
            if not temp_ok:
                violations.append(f"oil_temp={point.oil_temp_c:.1f} >= max {self.criteria.oil_temp_max}")
            reason = (
                f"Recovery criteria breached ({', '.join(violations)}). "
                f"Consecutive healthy observations reset to 0."
            )

        return RecoveryEvaluationResult(
            is_applicable_regime=True,
            is_observation_healthy=is_healthy,
            consecutive_healthy_observations=self.consecutive_healthy_observations,
            target_healthy_observations=self.criteria.target_healthy_observations,
            is_verified=self.is_verified,
            reason=reason,
        )
```

- [ ] **Step 4: Update `tests/test_recovery_verifier.py` to give unique 10s timestamps in `_make_point`**

Ensure `_make_point(dv_pressure, oil_temp, regime, ts=None)` uses incrementing timestamps (e.g. `t0 + timedelta(seconds=10*i)`) so that continuity tests in `test_recovery_verifier.py` pass.

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_temporal_continuity.py tests/test_recovery_verifier.py -v`
Expected: ALL PASS.

- [ ] **Step 6: Commit**

```bash
git add src/engine/recovery.py tests/test_temporal_continuity.py tests/test_recovery_verifier.py
git commit -m "fix(engine): enforce timestamp continuity validation in RecoveryVerifier"
```

---

### Task 3: Implement Temporal Continuity in TemporalStepDetector (P0)

**Files:**
- Modify: `src/engine/detectors.py`
- Modify: `tests/test_temporal_continuity.py`

- [ ] **Step 1: Write failing tests for TemporalStepDetector temporal continuity**

Add to `tests/test_temporal_continuity.py`:

```python
from src.engine.detectors import TemporalStepDetector
from src.domain.enums import DetectorStatus, EvidenceCode

def test_temporal_step_continuity_valid_10s_intervals():
    detector = TemporalStepDetector(
        step_threshold=0.5,
        required_observations=3,
        baseline_observations=5,
        allowed_regime_gaps=0,
        max_observation_gap_seconds=30.0,
    )
    t0 = datetime(2020, 6, 5, 9, 45, 0)
    # 5 baseline points with dv=0.0
    window = [_make_pt(t0 + timedelta(seconds=10*i), dv=0.0) for i in range(5)]
    # 3 step points with dv=1.5
    for i in range(5, 8):
        window.append(_make_pt(t0 + timedelta(seconds=10*i), dv=1.5))

    res = detector.detect(window)
    assert res.status == DetectorStatus.CONFIRMED
    assert res.evidence_code == EvidenceCode.TEMPORAL_STEP_CONFIRMED

def test_temporal_step_broken_by_60s_gap_in_recent():
    detector = TemporalStepDetector(
        step_threshold=0.5,
        required_observations=3,
        baseline_observations=5,
        allowed_regime_gaps=0,
        max_observation_gap_seconds=30.0,
    )
    t0 = datetime(2020, 6, 5, 9, 45, 0)
    window = [_make_pt(t0 + timedelta(seconds=10*i), dv=0.0) for i in range(5)]
    # Point 6 at +50s, Point 7 at +60s, Point 8 at +180s (120s gap!)
    window.append(_make_pt(t0 + timedelta(seconds=50), dv=1.5))
    window.append(_make_pt(t0 + timedelta(seconds=60), dv=1.5))
    window.append(_make_pt(t0 + timedelta(seconds=180), dv=1.5))

    res = detector.detect(window)
    assert res.status == DetectorStatus.NORMAL
    assert res.evidence_code == EvidenceCode.NORMAL

def test_temporal_step_gap_plus_regime_change_does_not_pick_old_points():
    detector = TemporalStepDetector(
        step_threshold=0.5,
        required_observations=3,
        baseline_observations=5,
        allowed_regime_gaps=0,
        max_observation_gap_seconds=30.0,
    )
    t0 = datetime(2020, 6, 5, 9, 45, 0)
    # Old points before large gap
    window = [_make_pt(t0 + timedelta(seconds=10*i), dv=0.0) for i in range(5)]
    window.append(_make_pt(t0 + timedelta(seconds=50), dv=1.5))
    # OFF regime for 5 minutes
    window.append(_make_pt(t0 + timedelta(seconds=350), dv=1.5, regime=OperatingRegime.OFF))
    # Two new LOADED points
    window.append(_make_pt(t0 + timedelta(seconds=360), dv=1.5))
    window.append(_make_pt(t0 + timedelta(seconds=370), dv=1.5))

    res = detector.detect(window)
    assert res.status == DetectorStatus.NORMAL
```

- [ ] **Step 2: Run test to verify failure**

Run: `pytest tests/test_temporal_continuity.py -k temporal_step -v`
Expected: FAIL (`AttributeError: 'TemporalStepDetector' object has no attribute 'max_observation_gap_seconds'` or gap not enforced).

- [ ] **Step 3: Update `TemporalStepDetector` in `src/engine/detectors.py`**

In `src/engine/detectors.py`:
```python
class TemporalStepDetector(BaseDetector):
    def __init__(
        self,
        step_threshold: float = 0.5,
        required_observations: int = 3,
        baseline_observations: int = 5,
        allowed_regime_gaps: int = 0,
        max_observation_gap_seconds: float = 30.0,
        required_cycles: Optional[int] = None,
        baseline_cycles: Optional[int] = None,
    ):
        self.step_threshold = step_threshold
        self.required_observations = (
            required_cycles if required_cycles is not None else required_observations
        )
        self.baseline_observations = (
            baseline_cycles if baseline_cycles is not None else baseline_observations
        )
        self.allowed_regime_gaps = allowed_regime_gaps
        self.max_observation_gap_seconds = max_observation_gap_seconds

    def detect(self, window: List[TelemetryPoint]) -> DetectorResult:
        if not window:
            return DetectorResult(detector_id=self.detector_id, status=DetectorStatus.NORMAL)

        latest = window[-1]
        if latest.regime != OperatingRegime.LOADED:
            return DetectorResult(detector_id=self.detector_id, status=DetectorStatus.NORMAL)

        loaded_pts = []
        gaps = 0
        last_seen_ts = latest.timestamp

        for p in reversed(window):
            # Enforce temporal continuity across consecutive points
            time_gap = (last_seen_ts - p.timestamp).total_seconds()
            if time_gap > self.max_observation_gap_seconds and loaded_pts:
                # Timestamp gap exceeded between observations: break streak
                break

            if p.regime == OperatingRegime.LOADED:
                loaded_pts.append(p)
                last_seen_ts = p.timestamp
            else:
                gaps += 1
                if gaps > self.allowed_regime_gaps:
                    break

        loaded_pts.reverse()
        total_required = self.required_observations + self.baseline_observations

        if len(loaded_pts) < total_required:
            return DetectorResult(detector_id=self.detector_id, status=DetectorStatus.NORMAL)

        recent = loaded_pts[-self.required_observations:]
        past = loaded_pts[-total_required:-self.required_observations]

        # Verify recent observations are strictly temporally contiguous
        for i in range(len(recent) - 1):
            dt = (recent[i + 1].timestamp - recent[i].timestamp).total_seconds()
            if dt > self.max_observation_gap_seconds:
                return DetectorResult(detector_id=self.detector_id, status=DetectorStatus.NORMAL)

        recent_dv = sum(p.dv_pressure_bar for p in recent) / len(recent)
        past_dv = sum(p.dv_pressure_bar for p in past) / len(past)

        step_diff = recent_dv - past_dv
        is_sustained = all(p.dv_pressure_bar > (past_dv + self.step_threshold * 0.5) for p in recent)

        if step_diff > self.step_threshold and is_sustained:
            return DetectorResult(
                detector_id=self.detector_id,
                evidence_code=EvidenceCode.TEMPORAL_STEP_CONFIRMED,
                status=DetectorStatus.CONFIRMED,
                severity=Severity.HIGH,
                observed_value=round(step_diff, 4),
                baseline_value=0.0,
                sigma_deviation=0.0,
                provenance={
                    "step_diff": round(step_diff, 4),
                    "recent_dv": round(recent_dv, 4),
                    "past_dv": round(past_dv, 4),
                    "required_observations": self.required_observations,
                    "baseline_observations": self.baseline_observations,
                    "recent_observations": len(recent),
                    "actual_recent_timestamps": [p.timestamp.isoformat() for p in recent],
                    "actual_baseline_timestamps": [p.timestamp.isoformat() for p in past],
                    "gap_count": gaps,
                    "allowed_regime_gaps": self.allowed_regime_gaps,
                    "max_observation_gap_seconds": self.max_observation_gap_seconds,
                    "is_temporally_contiguous": True,
                }
            )

        return DetectorResult(
            detector_id=self.detector_id,
            evidence_code=EvidenceCode.NORMAL,
            status=DetectorStatus.NORMAL,
            severity=Severity.NONE,
            observed_value=round(step_diff, 4),
            baseline_value=0.0,
            sigma_deviation=0.0,
        )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_temporal_continuity.py -v`
Expected: ALL PASS.

- [ ] **Step 5: Commit**

```bash
git add src/engine/detectors.py tests/test_temporal_continuity.py
git commit -m "fix(engine): enforce timestamp continuity in TemporalStepDetector"
```

---

### Task 4: Fix Active Incident Lifecycle States in DecisionEngine

**Files:**
- Modify: `src/engine/decision.py`
- Modify: `tests/test_decision.py`

- [ ] **Step 1: Write failing test in `tests/test_decision.py`**

Add to `tests/test_decision.py`:

```python
def test_decision_resolved_and_failed_not_treated_as_active_incident():
    engine = DecisionEngine()
    state = EvidenceState(
        asset_id="APU-COMP-01",
        timestamp=datetime.now(),
        regime=OperatingRegime.LOADED,
        signals=[
            DetectorResult(
                detector_id="pressure_anomaly",
                evidence_code=EvidenceCode.PRESSURE_SEVERE,
                status=DetectorStatus.TRIGGERED,
                severity=Severity.HIGH,
                observed_value=2.5,
            ),
            DetectorResult(
                detector_id="thermal_stress",
                evidence_code=EvidenceCode.THERMAL_STRESS_ELEVATED,
                status=DetectorStatus.TRIGGERED,
                severity=Severity.MEDIUM,
            ),
            DetectorResult(
                detector_id="temporal_persistence",
                evidence_code=EvidenceCode.TEMPORAL_STEP_CONFIRMED,
                status=DetectorStatus.CONFIRMED,
                severity=Severity.HIGH,
            ),
        ]
    )
    # Context with RESOLVED lifecycle state must NOT be treated as active incident
    ctx_resolved = IncidentContext(
        active_incident_id="APU-INC-20200605-01",
        lifecycle_state=IncidentLifecycleState.RESOLVED
    )
    dec = engine.evaluate(state, incident_context=ctx_resolved)
    # Since previous incident is RESOLVED, a new confirmed degradation should trigger CREATE
    assert dec.incident_action == IncidentAction.CREATE
```

- [ ] **Step 2: Run test to verify failure**

Run: `pytest tests/test_decision.py -k resolved -v`
Expected: FAIL (`assert <IncidentAction.NONE: 'NONE'> == <IncidentAction.CREATE: 'CREATE'>`).

- [ ] **Step 3: Update `ACTIVE_INCIDENT_STATES` in `src/engine/decision.py`**

In `src/engine/decision.py`:
```python
ACTIVE_INCIDENT_STATES = {
    IncidentLifecycleState.DETECTED,
    IncidentLifecycleState.INVESTIGATING,
    IncidentLifecycleState.MITIGATING,
    IncidentLifecycleState.VERIFYING_RECOVERY,
}
```
And update `has_active_incident`:
```python
        has_active_incident = (
            incident_context is not None
            and incident_context.active_incident_id is not None
            and incident_context.lifecycle_state in ACTIVE_INCIDENT_STATES
        )
```

- [ ] **Step 4: Run test to verify pass**

Run: `pytest tests/test_decision.py -v`
Expected: ALL PASS.

- [ ] **Step 5: Commit**

```bash
git add src/engine/decision.py tests/test_decision.py
git commit -m "fix(decision): restrict active incident check to ACTIVE_INCIDENT_STATES"
```

---

### Task 5: Enforce Safe Mode Policy Boundary (Engine Recommends, Operator Authorizes) (P1)

**Files:**
- Modify: `src/domain/models.py`
- Modify: `src/engine/decision.py`
- Modify: `src/engine/lifecycle.py`
- Modify: `tests/test_decision.py`
- Modify: `tests/test_lifecycle_orchestrator.py`
- Modify: `tests/test_api_vertical_slice.py`

- [ ] **Step 1: Write failing tests for Safe Mode policy boundary**

Add to `tests/test_lifecycle_orchestrator.py`:

```python
def test_safe_mode_rejected_when_not_recommended_by_decision_engine():
    manager = IncidentLifecycleManager()
    manager.reset()
    # Seek to onset (DETECTED state)
    manager.jump_to_milestone("onset_0950")
    assert manager.lifecycle_state == IncidentLifecycleState.DETECTED
    # Decision at onset does not recommend mitigation yet (only accumulating evidence)
    assert manager.current_decision.recommended_action != IncidentAction.EXECUTE_MITIGATION
    # Operator attempting Safe Mode now must be rejected with InvalidStateTransitionError
    with pytest.raises(InvalidStateTransitionError, match="not recommended mitigation"):
        manager.trigger_safe_mode()
```

- [ ] **Step 2: Run test to verify failure**

Run: `pytest tests/test_lifecycle_orchestrator.py -k test_safe_mode_rejected_when_not_recommended -v`
Expected: FAIL (Safe Mode triggers without checking recommendation).

- [ ] **Step 3: Update `Decision` model and `DecisionEngine`**

In `src/domain/models.py`:
```python
class Decision(BaseModel):
    asset_health: AssetHealthState
    incident_action: IncidentAction
    operational_confidence: OperationalConfidence
    ui_action: str
    reason: str
    evidence_state: EvidenceState
    recommended_action: IncidentAction = IncidentAction.NONE
```

In `src/engine/decision.py`:
Set `recommended_action = IncidentAction.EXECUTE_MITIGATION` for ML Corroboration:
```python
        # 2. Multivariate ML Corroboration (High Confidence Evidence Pack: Pressure > 2.0 + Oil > 74C + ML > 0.35)
        if has_severe_pressure and has_severe_thermal and has_ml:
            action = IncidentAction.UPDATE_INVESTIGATING if has_active_incident else IncidentAction.CREATE
            return Decision(
                asset_health=AssetHealthState.CRITICAL,
                incident_action=action,
                operational_confidence=OperationalConfidence.HIGH,
                ui_action="Strong Evidence Pack Assembled",
                reason="Multi-detector physical signals confirmed and corroborated by multivariate Isolation Forest. Safe Mode recommended.",
                evidence_state=evidence_state,
                recommended_action=IncidentAction.EXECUTE_MITIGATION,
            )
```
And for LPS alert:
```python
        # 1. Reactive Baseline Alert (LPS=1 breached)
        if has_lps:
            action = IncidentAction.UPDATE_INVESTIGATING if has_active_incident else IncidentAction.CREATE
            return Decision(
                asset_health=AssetHealthState.CRITICAL,
                incident_action=action,
                operational_confidence=OperationalConfidence.CRITICAL_REACTIVE,
                ui_action="Reactive Baseline Alert Active",
                reason="Low Pressure Switch (LPS=1) reactive threshold breached. Line pressure < 7.0 bar.",
                evidence_state=evidence_state,
                recommended_action=IncidentAction.EXECUTE_MITIGATION,
            )
```

In `src/engine/lifecycle.py`:
Update `trigger_safe_mode()`:
```python
        if self.lifecycle_state not in (
            IncidentLifecycleState.DETECTED,
            IncidentLifecycleState.INVESTIGATING,
        ):
            raise InvalidStateTransitionError(
                f"Action safe-mode is not permitted when incident is in state {self.lifecycle_state.value}."
            )

        if (
            self.current_decision is None
            or self.current_decision.recommended_action != IncidentAction.EXECUTE_MITIGATION
        ):
            raise InvalidStateTransitionError(
                "Action safe-mode rejected: DecisionEngine has not recommended mitigation for current evidence."
            )
```

- [ ] **Step 4: Update API negative test in `tests/test_api_vertical_slice.py`**

Add check at step 2.5 of `test_api_vertical_slice_golden_path`:
Before jumping to `ml_corroborated_1015`, call `POST /api/action/safe-mode` -> assert returns 409 Conflict because mitigation was not yet recommended!
Then after jumping to `ml_corroborated_1015`, call `POST /api/action/safe-mode` -> assert 200 OK!

- [ ] **Step 5: Run tests to verify pass**

Run: `pytest tests/test_lifecycle_orchestrator.py tests/test_api_vertical_slice.py tests/test_decision.py -v`
Expected: ALL PASS.

- [ ] **Step 6: Commit**

```bash
git add src/domain/models.py src/engine/decision.py src/engine/lifecycle.py tests/test_lifecycle_orchestrator.py tests/test_api_vertical_slice.py tests/test_decision.py
git commit -m "feat(policy): enforce DecisionEngine mitigation recommendation boundary on Safe Mode authorization"
```

---

### Task 6: Real Golden Path Verification & ML Score Calibration Defense (P1)

**Files:**
- Create: `scripts/verify_golden_path_evidence.py`
- Create: `docs/ml-score-calibration.md`
- Create: `tests/test_golden_path_checkpoints_artifact.py`

- [ ] **Step 1: Write script `scripts/verify_golden_path_evidence.py` to freeze verification artifact**

```python
"""
Real dataset verification script that replays MetroPT-3 and dumps a frozen artifact of key milestones.
"""
import json
from pathlib import Path
import pandas as pd
from src.engine.factory import setup_golden_path
from src.domain.enums import IncidentLifecycleState, OperatingRegime

def generate_golden_path_artifact():
    replay, detectors, fusion, decision_engine = setup_golden_path()
    if_detector = next(d for d in detectors if d.detector_id == "isolation_forest")

    # Training baseline metrics
    feb = replay.df[(replay.df["timestamp"] >= "2020-02-01") & (replay.df["timestamp"] < "2020-03-01")]
    feb_loaded = feb[feb["COMP"] == 0.0] # Loaded samples
    training_info = {
        "dataset": "MetroPT3(AirCompressor).csv",
        "baseline_period": "2020-02-01 to 2020-02-29",
        "training_samples_loaded": len(feb_loaded),
        "features": ["DV_pressure", "H1", "Oil_temperature", "Motor_current", "TP3"],
        "random_state": 42,
        "contamination": 0.01,
        "operational_scale_factor": 10.0,
        "operational_threshold": 0.35,
    }

    # Extract milestone states
    milestones_data = {}
    checkpoints = [
        ("early_excursion", "2020-06-04 00:33:07"),
        ("confirmed_degradation", "2020-06-05 09:50:39"),
        ("ml_corroborated", "2020-06-05 10:15:00"),
        ("lps_reactive", "2020-06-06 19:42:19"),
    ]

    for name, ts_str in checkpoints:
        row = replay.df[replay.df["timestamp"] == ts_str].iloc[0]
        # Calculate raw sklearn decision_function
        X = row[["DV_pressure", "H1", "Oil_temperature", "Motor_current", "TP3"]].values.reshape(1, -1)
        raw_df = float(if_detector.model.decision_function(X)[0])
        raw_score = -raw_df
        op_score = round(raw_score * 10.0, 4)

        milestones_data[name] = {
            "timestamp": ts_str,
            "dv_pressure_bar": float(row["DV_pressure"]),
            "oil_temp_c": float(row["Oil_temperature"]),
            "tp3_bar": float(row["TP3"]),
            "raw_decision_function": round(raw_df, 6),
            "raw_score_neg_df": round(raw_score, 6),
            "operational_ml_score": op_score,
            "threshold": 0.35,
            "is_anomalous": op_score > 0.35,
        }

    artifact = {
        "training_baseline": training_info,
        "milestones": milestones_data,
    }

    out_path = Path("docs/golden_path_evidence_artifact.json")
    out_path.write_text(json.dumps(artifact, indent=2))
    print(f"Artifact frozen to {out_path}")
    return artifact

if __name__ == "__main__":
    generate_golden_path_artifact()
```

- [ ] **Step 2: Run script to generate `docs/golden_path_evidence_artifact.json`**

Run: `python scripts/verify_golden_path_evidence.py`
Expected: File `docs/golden_path_evidence_artifact.json` generated.

- [ ] **Step 3: Create `docs/ml-score-calibration.md` documenting calibration rationale**

Document:
- sklearn `decision_function` mathematical definition: $s(x) = 2^{-\frac{E(h(x))}{c(n)}} - \text{offset}$.
- Anomaly scores for extreme excursions in MetroPT-3 lie in $[-0.05, -0.01]$.
- Negation $-\text{decision\_function}(x)$ maps higher = more anomalous.
- Domain scale multiplier $\times 10.0$ normalizes the score to $[0.1, 0.5]$ range with operational threshold $0.35$.
- Defend against hack critique: Show that at baseline $score \approx 0.0$, at early excursion $score = 0.22 < 0.35$ (no false alarm), at corroborated degradation $score = 0.381 > 0.35$.

- [ ] **Step 4: Create automated checkpoint verification test `tests/test_golden_path_checkpoints_artifact.py`**

Verify that `docs/golden_path_evidence_artifact.json` exists and that values at 10:15:00 match $0.38 \pm 0.02$.

- [ ] **Step 5: Run test**

Run: `pytest tests/test_golden_path_checkpoints_artifact.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add scripts/verify_golden_path_evidence.py docs/golden_path_evidence_artifact.json docs/ml-score-calibration.md tests/test_golden_path_checkpoints_artifact.py
git commit -m "docs(ml): freeze golden path evidence artifact and document ML score operational calibration"
```

---

### Task 7: Scenario Definition Abstraction & Early Excursion Narrative (P0 & P1)

**Files:**
- Create: `src/domain/scenarios.py`
- Modify: `src/domain/models.py`
- Modify: `src/engine/lifecycle.py`
- Create: `tests/test_scenarios.py`

- [ ] **Step 1: Write failing test in `tests/test_scenarios.py`**

```python
import pytest
from src.domain.scenarios import FAILURE_3_SCENARIO, HEALTHY_SCENARIO
from src.domain.enums import IncidentLifecycleState, AssetHealthState
from src.engine.lifecycle import IncidentLifecycleManager

def test_failure_3_early_excursion_milestone():
    manager = IncidentLifecycleManager(scenario=FAILURE_3_SCENARIO)
    manager.reset()
    manager.jump_to_milestone("early_excursion_0033")
    # Early excursion: transient excursion detected, but NO incident created
    assert manager.active_incident is None
    assert manager.lifecycle_state == IncidentLifecycleState.NONE
    assert manager.asset_health == AssetHealthState.DEGRADING
    assert manager.operational_confidence.value == "LOW"

def test_healthy_scenario_no_incidents_created():
    manager = IncidentLifecycleManager(scenario=HEALTHY_SCENARIO)
    manager.reset()
    # Tick 30 points in healthy stream
    for _ in range(30):
        manager.tick()
    assert manager.active_incident is None
    assert manager.lifecycle_state == IncidentLifecycleState.NONE
    assert manager.asset_health == AssetHealthState.HEALTHY
```

- [ ] **Step 2: Run test to verify failure**

Run: `pytest tests/test_scenarios.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'src.domain.scenarios'`).

- [ ] **Step 3: Create `src/domain/scenarios.py`**

```python
from typing import Dict, Optional
from pydantic import BaseModel, Field

class ScenarioDefinition(BaseModel):
    scenario_id: str
    name: str
    asset_id: str = "APU-COMP-01"
    stream_start: str
    stream_end: str
    recovery_start: Optional[str] = None
    recovery_end: Optional[str] = None
    lps_milestone: Optional[str] = None
    milestones: Dict[str, str] = Field(default_factory=dict)

FAILURE_3_SCENARIO = ScenarioDefinition(
    scenario_id="failure_3",
    name="Failure #3 Air Leak & Thermal Drift (Golden Path)",
    asset_id="APU-COMP-01",
    stream_start="2020-06-05 09:40:00",
    stream_end="2020-06-06 20:00:00",
    recovery_start="2020-06-08 16:05:00",
    recovery_end="2020-06-08 17:00:00",
    lps_milestone="2020-06-06 19:42:19",
    milestones={
        "early_excursion_0033": "2020-06-04 00:33:07",
        "onset_0950": "2020-06-05 09:50:00",
        "ml_corroborated_1015": "2020-06-05 10:15:00",
        "lps_reactive_1942": "2020-06-06 19:42:19",
        "post_maintenance_1605": "2020-06-08 16:05:00",
    },
)

FAILURE_1_SCENARIO = ScenarioDefinition(
    scenario_id="failure_1",
    name="Failure #1 Air Leak & High Duty Cycle",
    asset_id="APU-COMP-01",
    stream_start="2020-04-10 00:00:00",
    stream_end="2020-04-12 23:59:59",
    milestones={
        "onset": "2020-04-11 11:00:00",
    },
)

FAILURE_4_SCENARIO = ScenarioDefinition(
    scenario_id="failure_4",
    name="Failure #4 Oil Contamination & Thermal Stress",
    asset_id="APU-COMP-01",
    stream_start="2020-07-08 00:00:00",
    stream_end="2020-07-10 23:59:59",
    milestones={
        "onset": "2020-07-09 14:00:00",
    },
)

HEALTHY_SCENARIO = ScenarioDefinition(
    scenario_id="healthy_baseline",
    name="Healthy Baseline (February 2020)",
    asset_id="APU-COMP-01",
    stream_start="2020-02-10 08:00:00",
    stream_end="2020-02-10 12:00:00",
    milestones={},
)
```

- [ ] **Step 4: Update `IncidentLifecycleManager` to accept `scenario: Optional[ScenarioDefinition] = None`**

In `src/engine/lifecycle.py`:
- Use `self.scenario = scenario or FAILURE_3_SCENARIO`.
- `self.milestones = self.scenario.milestones.copy()`.
- In `reset()`: stream from `self.scenario.stream_start` to `self.scenario.stream_end`.
- In `trigger_safe_mode()`: stream from `self.scenario.recovery_start` to `self.scenario.recovery_end`.
- In `jump_to_milestone("early_excursion_0033")`:
  If target dt is before stream start, seek stream starting from `"2020-06-04 00:30:00"`.
- In `get_incident_payload()`: read `self.scenario.lps_milestone`.

- [ ] **Step 5: Run tests to verify pass**

Run: `pytest tests/test_scenarios.py -v`
Expected: ALL PASS.

- [ ] **Step 6: Commit**

```bash
git add src/domain/scenarios.py src/engine/lifecycle.py tests/test_scenarios.py
git commit -m "feat(scenario): decouple ScenarioDefinition and support early excursion milestone narrative"
```

---

### Task 8: Full Test Suite Regression & Verification

**Files:**
- All tests

- [ ] **Step 1: Run the full test suite**

Run: `pytest tests/ -v`
Expected: ALL tests pass across unit, integration, and scenario suites.

- [ ] **Step 2: Commit any remaining test updates**

```bash
git add .
git commit -m "test: full verification of temporal continuity, policy boundary, and scenario validation"
```
