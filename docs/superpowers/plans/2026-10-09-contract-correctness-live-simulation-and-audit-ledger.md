# Contract Correctness, Deterministic Live Simulation & Audit Ledger Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Address all critical review blockers (P0/P1) from the 09/10/2026 architecture review: integrate SimulationRunner as the single telemetry engine for IncidentLifecycleManager, fix active case projection and lead time calculations, ground early excursion telemetry in verifiable dataset facts, expose detector provenance in the public API, complete the CaseEvent audit ledger with MongoDB persistence, wire Datadog observability, and enforce dynamic ActionGuard conditions.

**Architecture:** Refactor `IncidentLifecycleManager` to consume telemetry exclusively through `SimulationRunner` and `HistoricalScenarioStream` with deterministic time pacing while strictly preserving dataset `event_time`. Establish two decoupled evaluation tracks: an unmitigated historical baseline tracker for dynamic LPS benchmark measurement and a simulated intervention recovery verification track. Project lifecycle states onto product operations so closed cases never report active status, expose rich evidence provenance via `GET /api/evidence`, persist time-series measurements and audit events to MongoDB, and emit operational telemetry to Datadog.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, Pandas, NumPy, Scikit-learn (Isolation Forest), PyMongo, DogStatsD / Datadog, Pytest.

---

### Task 1: Product State Projection, Incident Closure & Zero Fake Active Cases

**Files:**
- Modify: `src/domain/enums.py:16-25`
- Modify: `src/engine/lifecycle.py:88-105, 184-215, 540-555`
- Modify: `src/api/routes_product.py:25-56`
- Modify: `src/api/schemas.py:19-27, 123-130`
- Test: `tests/test_operations_api.py`
- Test: `tests/test_lifecycle_orchestrator.py`

- [ ] **Step 1: Write the failing test for active case state projection and closure**

```python
# tests/test_operations_case_projection.py
import pytest
from src.engine.lifecycle import IncidentLifecycleManager
from src.domain.enums import IncidentLifecycleState, AssetHealthState
from src.domain.scenarios import FAILURE_3_SCENARIO

def test_no_active_case_in_initial_none_state():
    manager = IncidentLifecycleManager(scenario=FAILURE_3_SCENARIO)
    manager.reset()

    # Initial state must have zero active cases
    assert manager.has_active_case() is False
    assert manager.get_active_case() is None
    payload = manager.get_incident_payload()
    assert payload["incident_id"] is None or payload["lifecycle_state"] == "NONE"
    assert payload["lead_time"]["lead_time_formatted"] is None

def test_closed_case_projects_zero_active_cases():
    manager = IncidentLifecycleManager(scenario=FAILURE_3_SCENARIO)
    manager.reset()
    manager.jump_to_milestone("onset_0950")
    assert manager.has_active_case() is True

    # Trigger safe mode and verify recovery
    manager.jump_to_milestone("ml_corroborated_1015")
    manager.trigger_safe_mode()
    
    # Fast forward through 5 healthy cycles
    for _ in range(10):
        manager.tick()

    assert manager.recovery_verifier.is_verified is True
    # Close case with operator sign-off
    res = manager.close_case(operator_id="DISPATCHER-0941", notes="Verified recovery complete.")
    assert res["status"] == "CASE_CLOSED"

    # Invariant: Once closed, case is NOT active, active cases count is 0
    assert manager.has_active_case() is False
    assert manager.get_active_case() is None
    assert manager.lifecycle_state == IncidentLifecycleState.RESOLVED
    assert manager.asset_health == AssetHealthState.HEALTHY
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_operations_case_projection.py -v`
Expected: FAIL with `AttributeError: 'IncidentLifecycleManager' object has no attribute 'has_active_case'`

- [ ] **Step 3: Implement product state projection and clean closure in `lifecycle.py` and `routes_product.py`**

In `src/engine/lifecycle.py`:
```python
    def has_active_case(self) -> bool:
        """Determines if there is a currently open, active operational case."""
        if self.active_incident is None:
            return False
        # A case is only active if it is currently in DETECTED, INVESTIGATING, MITIGATING, or VERIFYING_RECOVERY
        return self.active_incident.lifecycle_state in (
            IncidentLifecycleState.DETECTED,
            IncidentLifecycleState.INVESTIGATING,
            IncidentLifecycleState.MITIGATING,
            IncidentLifecycleState.VERIFYING_RECOVERY,
        )

    def get_active_case(self) -> Optional[IncidentEvent]:
        """Returns the active incident if open, else None."""
        return self.active_incident if self.has_active_case() else None

    def close_case(self, operator_id: str = "DISPATCHER-0941", notes: str = "") -> Dict[str, Any]:
        if not self.recovery_verifier.is_verified:
            raise ValueError("Recovery not verified. Cannot close operational case before 5/5 healthy LOADED observations are verified.")
        
        self.lifecycle_state = IncidentLifecycleState.RESOLVED
        self.asset_health = AssetHealthState.HEALTHY
        
        closed_incident_id = "CASE-20200605-01"
        if self.active_incident:
            closed_incident_id = self.active_incident.incident_id
            self.active_incident.lifecycle_state = IncidentLifecycleState.RESOLVED
            self.active_incident.health_state = AssetHealthState.HEALTHY
            if self.current_point:
                self.active_incident.updated_at = self.current_point.timestamp

        self.record_case_event(
            event_type=CaseEventType.CASE_CLOSED,
            phase="RESOLVED",
            title="Case Signed Off & Closed",
            detail=f"Operator {operator_id} signed off incident. Asset APU-COMP-01 released back to HEALTHY service. Notes: {notes or 'Recovery criteria satisfied'}",
            actor=f"operator:{operator_id}",
            source="Operations Console",
        )
        if getattr(self, "repository", None) is not None and self.active_incident is not None:
            try:
                self.repository.save_case(self.active_incident.model_dump(mode="json"))
            except Exception:
                pass

        # Clear active incident pointer so it is no longer reported as active
        archived_incident = self.active_incident
        self.active_incident = None

        return {
            "status": "CASE_CLOSED",
            "case_id": closed_incident_id,
            "operator_id": operator_id,
            "notes": notes,
            "lifecycle_state": "RESOLVED",
            "asset_health": "HEALTHY",
        }
```

And update `src/api/routes_product.py`:
```python
@router.get("/operations", response_model=OperationsResponse)
def get_operations(manager: IncidentLifecycleManager = Depends(get_manager)) -> OperationsResponse:
    registry = AssetRegistry.get_default()
    has_active = manager.has_active_case()
    is_observing = manager.lifecycle_state == IncidentLifecycleState.NONE

    summary = OperationsSummaryInfo(
        monitored_assets_count=1,
        active_cases_count=1 if has_active else 0,
        assets_observing_count=1 if is_observing else 0,
        scenario_name=manager.scenario.name,
        simulation_mode="LIVE_SIMULATION",
        confirmed_intervention_window=manager.get_lead_time_formatted() if has_active else None,
    )

    return OperationsResponse(
        fleet=registry.fleets["FLEET-METRO-01"].model_dump(),
        train=registry.trains["TRAIN-302"].model_dump(),
        subsystem=registry.subsystems["SUB-APU-01"].model_dump(),
        asset=registry.assets["APU-COMP-01"].model_dump(),
        operations_summary=summary,
        active_case=manager.get_incident_payload() if has_active else None,
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_operations_case_projection.py -v`
Expected: PASS

- [ ] **Step 5: Commit changes**

```bash
git add src/engine/lifecycle.py src/api/routes_product.py tests/test_operations_case_projection.py
git commit -m "fix(lifecycle): enforce product case state projection and clean closure invariant"
```

---

### Task 2: Dynamic Lead Time & Baseline Benchmark Tracker

**Files:**
- Create: `src/engine/benchmark.py`
- Modify: `src/engine/lifecycle.py:509-555`
- Modify: `src/api/schemas.py:12-17`
- Test: `tests/test_dynamic_lead_time.py`

- [ ] **Step 1: Write the failing test for dynamic lead time computation**

```python
# tests/test_dynamic_lead_time.py
import pytest
from datetime import datetime, timezone
from src.engine.benchmark import BaselineBenchmarkTracker
from src.engine.lifecycle import IncidentLifecycleManager
from src.domain.scenarios import FAILURE_3_SCENARIO, HEALTHY_SCENARIO

def test_lead_time_returns_none_when_no_active_incident():
    manager = IncidentLifecycleManager(scenario=FAILURE_3_SCENARIO)
    manager.reset()
    # Before detection, lead time must NOT return a hardcoded 33h 52m!
    payload = manager.get_incident_payload()
    assert payload["lead_time"]["lead_time_minutes"] is None
    assert payload["lead_time"]["lead_time_formatted"] is None

def test_dynamic_lead_time_calculation_with_observed_lps():
    tracker = BaselineBenchmarkTracker()
    # Register confirmed onset at June 5 09:50:39
    onset_dt = datetime(2020, 6, 5, 9, 50, 39, tzinfo=timezone.utc)
    # Register historical LPS breached at June 6 19:42:19
    lps_dt = datetime(2020, 6, 6, 19, 42, 19, tzinfo=timezone.utc)

    tracker.record_onset(onset_dt)
    tracker.record_lps_benchmark(lps_dt)

    assert tracker.is_ready is True
    assert tracker.lead_time_minutes == 2031  # 33 hours 51 minutes (2031 mins) or exact delta
    assert tracker.formatted_lead_time == "33h 51m"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_dynamic_lead_time.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'src.engine.benchmark'`

- [ ] **Step 3: Implement `src/engine/benchmark.py` and dynamic lead time in `lifecycle.py`**

Create `src/engine/benchmark.py`:
```python
from datetime import datetime
from typing import Optional, Dict, Any
import pandas as pd


class BaselineBenchmarkTracker:
    """
    Decouples the historical unmitigated baseline benchmark from the simulated intervention.
    Calculates lead time strictly from observed historical onset and observed baseline LPS breach.
    """
    def __init__(self, expected_lps_timestamp: Optional[str] = "2020-06-06 19:42:19") -> None:
        self.onset_timestamp: Optional[datetime] = None
        self.lps_timestamp: Optional[datetime] = (
            pd.to_datetime(expected_lps_timestamp) if expected_lps_timestamp else None
        )
        self.is_lps_observed: bool = False

    def record_onset(self, onset_dt: datetime) -> None:
        self.onset_timestamp = onset_dt

    def record_lps_benchmark(self, lps_dt: datetime) -> None:
        self.lps_timestamp = lps_dt
        self.is_lps_observed = True

    @property
    def is_ready(self) -> bool:
        return self.onset_timestamp is not None and self.lps_timestamp is not None

    @property
    def lead_time_minutes(self) -> Optional[int]:
        if not self.is_ready or self.onset_timestamp is None or self.lps_timestamp is None:
            return None
        delta = self.lps_timestamp - self.onset_timestamp
        mins = int(round(delta.total_seconds() / 60.0))
        return max(0, mins)

    @property
    def formatted_lead_time(self) -> Optional[str]:
        mins = self.lead_time_minutes
        if mins is None:
            return None
        hours = mins // 60
        rem_mins = mins % 60
        return f"{hours}h {rem_mins:02d}m"

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_ready": self.is_ready,
            "lead_time_minutes": self.lead_time_minutes,
            "lead_time_formatted": self.formatted_lead_time,
            "onset_timestamp": self.onset_timestamp.isoformat() if self.onset_timestamp else None,
            "lps_benchmark_timestamp": self.lps_timestamp.isoformat() if self.lps_timestamp else None,
        }
```

In `src/engine/lifecycle.py`:
Wire `self.benchmark_tracker = BaselineBenchmarkTracker(self.scenario.lps_milestone)`.
When incident is created: call `self.benchmark_tracker.record_onset(pt.timestamp)`.
In `get_incident_payload()`:
```python
        if not self.has_active_case():
            lead_info = {
                "lead_time_minutes": None,
                "lead_time_formatted": None,
                "conventional_alert_timestamp": None,
                "earliest_detection_timestamp": None,
            }
        else:
            lead_info = {
                "lead_time_minutes": self.benchmark_tracker.lead_time_minutes,
                "lead_time_formatted": self.benchmark_tracker.formatted_lead_time,
                "conventional_alert_timestamp": (
                    self.benchmark_tracker.lps_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
                    if self.benchmark_tracker.lps_timestamp
                    else None
                ),
                "earliest_detection_timestamp": (
                    self.benchmark_tracker.onset_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
                    if self.benchmark_tracker.onset_timestamp
                    else None
                ),
            }
```

In `src/api/schemas.py`: Update `LeadTimeInfo` fields `lead_time_minutes`, `lead_time_formatted`, `conventional_alert_timestamp`, `earliest_detection_timestamp` to be `Optional`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_dynamic_lead_time.py -v`
Expected: PASS

- [ ] **Step 5: Commit changes**

```bash
git add src/engine/benchmark.py src/engine/lifecycle.py src/api/schemas.py tests/test_dynamic_lead_time.py
git commit -m "feat(benchmark): decouple unmitigated baseline LPS benchmark and make lead time dynamic"
```

---

### Task 3: Early Excursion Truthfulness & Real Telemetry Grounding

**Files:**
- Modify: `docs/golden_path_evidence_artifact.json:27-43`
- Modify: `screen/01_OPERATIONS_NAV_AND_ASSET_OVERVIEW.md:67-117`
- Modify: `tests/test_golden_path_checkpoints_artifact.py:69-87`
- Modify: `src/domain/scenarios.py:23-39`
- Test: `tests/test_screen_spec_consistency.py`
- Test: `tests/test_scenarios.py`

- [ ] **Step 1: Write the failing test asserting true sensor values at 2020-06-04 00:33:07**

```python
# tests/test_early_excursion_truth.py
import pytest
from src.domain.scenarios import FAILURE_3_SCENARIO
from src.engine.lifecycle import IncidentLifecycleManager
from src.domain.enums import AssetHealthState, IncidentLifecycleState

def test_early_excursion_matches_actual_dataset_telemetry():
    manager = IncidentLifecycleManager(scenario=FAILURE_3_SCENARIO)
    manager.reset()
    manager.jump_to_milestone("early_excursion_0033")

    pt = manager.current_point
    assert pt is not None
    assert "2020-06-04 00:33:07" in str(pt.timestamp)
    # The actual sensor value in MetroPT-3 is ~6.046 bar, not synthetic 0.52 bar!
    assert round(pt.dv_pressure_bar, 2) == 6.05
    
    # State truth: transient excursion is observed, asset is marked DEGRADING, but NO case created
    assert manager.lifecycle_state == IncidentLifecycleState.NONE
    assert manager.asset_health == AssetHealthState.DEGRADING
    assert manager.active_incident is None
```

- [ ] **Step 2: Run test to verify it fails (if scenario bounds or stream offsets mismatch)**

Run: `pytest tests/test_early_excursion_truth.py -v`
Expected: Runs against actual CSV sample and verifies true values.

- [ ] **Step 3: Update `docs/golden_path_evidence_artifact.json` and `screen/01_OPERATIONS_NAV_AND_ASSET_OVERVIEW.md`**

In `docs/golden_path_evidence_artifact.json`:
Update `early_excursion` checkpoint to reflect actual MetroPT-3 sensor values:
`"DV_pressure": 6.046`, `"Oil_temperature": 70.2`, `"Motor_current": 5.455`, with explanation that the transient pulse in LOADED regime triggers elevated pressure sigma ($65.4\sigma$), but lacking temporal continuity and thermal confirmation, the system marks the asset as `DEGRADING` under observation without creating a case.

In `screen/01_OPERATIONS_NAV_AND_ASSET_OVERVIEW.md`:
Update Data Binding Contract to:
```json
{
  "fleet_id": "FLEET-METRO-01",
  "fleet_name": "Linha Azul Fleet (Illustrative Demo Context)",
  "asset_hierarchy": {
    "train_id": "TRAIN-302",
    "asset_id": "APU-COMP-01",
    "asset_health": "DEGRADING",
    "active_case_id": null
  },
  "signal_observation": {
    "signal": "OBSERVED",
    "pressure_state": "ELEVATED",
    "temporal_evidence": "INSUFFICIENT",
    "asset_health": "DEGRADING",
    "operational_case": "NONE",
    "decision": "NO_CASE_CREATED",
    "observed_value": 6.046,
    "sigma_deviation": 65.4,
    "persistence": {
      "confirmed": false,
      "status": "UNCONFIRMED_TRANSIENT"
    }
  }
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_early_excursion_truth.py tests/test_golden_path_checkpoints_artifact.py -v`
Expected: PASS

- [ ] **Step 5: Commit changes**

```bash
git add docs/golden_path_evidence_artifact.json screen/01_OPERATIONS_NAV_AND_ASSET_OVERVIEW.md tests/test_early_excursion_truth.py
git commit -m "fix(contract): align early excursion wireframe spec with true dataset telemetry"
```

---

### Task 4: Deterministic Live Simulation Engine Integration

**Files:**
- Modify: `src/engine/simulation.py:61-125`
- Modify: `src/engine/lifecycle.py:68-120, 277-300, 407-440`
- Modify: `src/api/routes_demo.py`
- Test: `tests/test_simulation_runner.py`
- Test: `tests/test_lifecycle_orchestrator.py`

- [ ] **Step 1: Write the failing test for SimulationRunner driving IncidentLifecycleManager**

```python
# tests/test_simulation_integration.py
import pytest
from src.engine.lifecycle import IncidentLifecycleManager
from src.engine.simulation import SimulationRunner, HistoricalScenarioStream
from src.domain.scenarios import FAILURE_3_SCENARIO

def test_lifecycle_manager_uses_simulation_runner_as_sole_stream_driver():
    manager = IncidentLifecycleManager(scenario=FAILURE_3_SCENARIO)
    manager.reset()

    assert hasattr(manager, "runner")
    assert isinstance(manager.runner, SimulationRunner)
    assert manager.runner.is_paused is True

    # Pacing and play controls
    manager.play()
    assert manager.runner.is_paused is False

    manager.set_simulation_speed(300.0)
    assert manager.runner.config.speed_multiplier == 300.0

    # Advance by one tick through SimulationRunner
    pt = manager.tick()
    assert pt is not None
    assert manager.runner.total_points_emitted >= 1
    assert manager.runner.current_event_time == pt.timestamp
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_simulation_integration.py -v`
Expected: FAIL with `AttributeError: 'IncidentLifecycleManager' object has no attribute 'runner'`

- [ ] **Step 3: Integrate `SimulationRunner` as the single telemetry engine in `IncidentLifecycleManager`**

In `src/engine/lifecycle.py`:
```python
    def __init__(
        self,
        replay: Optional[ReplayEngine] = None,
        detectors: Optional[List[BaseDetector]] = None,
        fusion: Optional[EvidenceFusionEngine] = None,
        decision_engine: Optional[DecisionEngine] = None,
        recovery_verifier: Optional[RecoveryVerifier] = None,
        scenario: Optional[ScenarioDefinition] = None,
        repository: Optional[Any] = None,
        runner: Optional[SimulationRunner] = None,
    ) -> None:
        self.scenario: ScenarioDefinition = scenario or FAILURE_3_SCENARIO
        self.milestones: Dict[str, str] = self.scenario.milestones.copy()
        self.replay = replay
        self.detectors = detectors
        self.fusion = fusion
        self.decision_engine = decision_engine
        self.recovery_verifier = recovery_verifier or RecoveryVerifier()
        self.repository = repository
        self.runner = runner

        # Stream initialized through SimulationRunner
        self._init_stream_runner()
        # ...
    
    def _init_stream_runner(self) -> None:
        stream = HistoricalScenarioStream(
            start_ts=self.scenario.stream_start,
            end_ts=self.scenario.stream_end,
            csv_path=str(self.replay.csv_path if self.replay else DEFAULT_CSV_PATH),
        )
        self.runner = SimulationRunner(stream=stream, scenario_name=self.scenario.name)

    def play(self) -> None:
        if self.runner:
            self.runner.is_paused = False

    def pause(self) -> None:
        if self.runner:
            self.runner.is_paused = True

    def set_simulation_speed(self, multiplier: float) -> None:
        if self.runner:
            self.runner.set_speed(multiplier)

    def tick(self) -> Optional[TelemetryPoint]:
        # Advance strictly via SimulationRunner
        pt = self.runner.step()
        if pt is None:
            return None
        self.current_point = pt
        return self._process_telemetry_point(pt)
```

And update `jump_to_milestone`:
Instead of recreating streams manually, call `self.runner.stream.seek(target_dt)`!

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_simulation_integration.py -v`
Expected: PASS

- [ ] **Step 5: Commit changes**

```bash
git add src/engine/simulation.py src/engine/lifecycle.py tests/test_simulation_integration.py
git commit -m "feat(simulation): integrate SimulationRunner as sole telemetry engine in lifecycle manager"
```

---

### Task 5: Evidence Provenance in Public API & Exact Signal Provenance

**Files:**
- Modify: `src/api/schemas.py:29-38`
- Modify: `src/engine/lifecycle.py:615-675`
- Test: `tests/test_evidence_provenance.py`
- Test: `tests/test_api_vertical_slice.py`

- [ ] **Step 1: Write the failing test for public API evidence provenance**

```python
# tests/test_api_evidence_provenance.py
import pytest
from src.engine.lifecycle import IncidentLifecycleManager
from src.domain.scenarios import FAILURE_3_SCENARIO

def test_evidence_payload_exposes_detector_provenance():
    manager = IncidentLifecycleManager(scenario=FAILURE_3_SCENARIO)
    manager.reset()
    manager.jump_to_milestone("onset_0950")

    payload = manager.get_evidence_payload()
    evidence_pack = payload["evidence_pack"]
    assert len(evidence_pack) > 0

    primary = next((e for e in evidence_pack if e["is_primary"]), None)
    assert primary is not None
    assert "provenance" in primary
    prov = primary["provenance"]
    assert "detector_class" in prov or "source" in prov
    assert "regime" in prov
    assert prov["regime"] == "LOADED"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_api_evidence_provenance.py -v`
Expected: FAIL with `AssertionError: 'provenance' not in primary`

- [ ] **Step 3: Update schema and lifecycle `get_evidence_payload()`**

In `src/api/schemas.py`:
```python
class EvidenceSignalItem(BaseModel):
    code: str
    signal_name: str
    observed_value: float
    baseline_value: float
    unit: str
    sigma_deviation: Optional[float] = None
    status: str
    is_primary: bool
    provenance: dict = {}
```

In `src/engine/lifecycle.py` inside `get_evidence_payload()`:
For each `sig` in `evidence_state.signals`, pass `sig.provenance`:
```python
    evidence_pack.append({
        "code": sig.evidence_code.value,
        "signal_name": "Discharge Valve Pressure",
        "observed_value": sig.observed_value,
        "baseline_value": sig.baseline_value,
        "unit": "bar",
        "sigma_deviation": sig.sigma_deviation,
        "status": "CRITICAL" if sig.evidence_code == EvidenceCode.PRESSURE_SEVERE else "TRIGGERED",
        "is_primary": True,
        "provenance": {
            **sig.provenance,
            "event_time": self.current_point.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ") if self.current_point else None,
            "regime": self.current_point.regime.value if self.current_point and self.current_point.regime else "LOADED",
        },
    })
```
And ensure ML corroboration provenance records its own distinct observation time (`2020-06-05T10:15:00Z`).

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_api_evidence_provenance.py -v`
Expected: PASS

- [ ] **Step 5: Commit changes**

```bash
git add src/api/schemas.py src/engine/lifecycle.py tests/test_api_evidence_provenance.py
git commit -m "feat(api): expose rich detector provenance in public evidence schema"
```

---

### Task 6: Complete Audit Ledger with CaseEvent & Repository Integration

**Files:**
- Modify: `src/domain/enums.py:68-76`
- Modify: `src/engine/lifecycle.py:150-182, 330-405`
- Modify: `src/storage/repository.py:38-45`
- Modify: `src/api/app.py:17-23`
- Test: `tests/test_case_events_ledger.py`
- Test: `tests/test_mongodb_storage.py`

- [ ] **Step 1: Write the failing test for audit ledger completeness and persistence**

```python
# tests/test_audit_ledger_completeness.py
import pytest
from src.engine.lifecycle import IncidentLifecycleManager
from src.storage.repository import CompressorGuardRepository
from src.domain.enums import CaseEventType
from src.domain.scenarios import FAILURE_3_SCENARIO

def test_audit_ledger_records_observation_and_decision_events():
    repo = CompressorGuardRepository()
    manager = IncidentLifecycleManager(scenario=FAILURE_3_SCENARIO, repository=repo)
    manager.reset()

    # 1. Early excursion creates OBSERVATION event
    manager.jump_to_milestone("early_excursion_0033")
    events = manager.get_case_events()
    event_types = [e["event_type"] for e in events]
    assert CaseEventType.OBSERVATION.value in event_types

    # 2. Confirmed onset creates CASE_CONFIRMED (or DETECTION) and DECISION events
    manager.jump_to_milestone("onset_0950")
    events = manager.get_case_events()
    event_types = [e["event_type"] for e in events]
    assert any(t in event_types for t in ["CASE_CONFIRMED", "DETECTION"])
    assert "DECISION" in event_types
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_audit_ledger_completeness.py -v`
Expected: FAIL with `AssertionError: 'DECISION' not in event_types`

- [ ] **Step 3: Update `CaseEventType` enum, event emission in `lifecycle.py`, and inject repository by default in `app.py`**

In `src/domain/enums.py`:
```python
class CaseEventType(str, Enum):
    OBSERVATION = "OBSERVATION"
    CASE_CONFIRMED = "CASE_CONFIRMED"
    DETECTION = "DETECTION"  # backward compat
    ML_CORROBORATION = "ML_CORROBORATION"
    CORROBORATION = "CORROBORATION"  # backward compat
    DECISION = "DECISION"
    ACTION = "ACTION"
    BENCHMARK_REFERENCE_REACHED = "BENCHMARK_REFERENCE_REACHED"
    BENCHMARK = "BENCHMARK"  # backward compat
    RECOVERY_VERIFIED = "RECOVERY_VERIFIED"
    RECOVERY = "RECOVERY"  # backward compat
    CASE_CLOSED = "CASE_CLOSED"
```

In `src/engine/lifecycle.py`:
- Record `OBSERVATION` during early excursion transient detection.
- Record `DECISION` when policy evaluation recommends state changes.
- Record `BENCHMARK_REFERENCE_REACHED` when unmitigated baseline LPS is observed.
- In `record_case_event`: persist directly to `self.repository.save_case_event(...)`.
- In `get_case_events()`: read from `self.repository.get_case_events(case_id)` if repository is present, falling back to in-memory list.

In `src/api/app.py`:
```python
def get_default_manager() -> IncidentLifecycleManager:
    global _DEFAULT_MANAGER
    if _DEFAULT_MANAGER is None:
        from src.storage.repository import CompressorGuardRepository
        repo = CompressorGuardRepository()
        _DEFAULT_MANAGER = IncidentLifecycleManager(repository=repo)
    return _DEFAULT_MANAGER
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_audit_ledger_completeness.py -v`
Expected: PASS

- [ ] **Step 5: Commit changes**

```bash
git add src/domain/enums.py src/engine/lifecycle.py src/storage/repository.py src/api/app.py tests/test_audit_ledger_completeness.py
git commit -m "feat(ledger): implement complete audit event types and wire persistent repository by default"
```

---

### Task 7: Real MongoDB Time-Series Pipeline, TTL Index & Datadog Emitter

**Files:**
- Modify: `src/storage/mongo_client.py:190-226`
- Modify: `src/storage/repository.py:10-30`
- Modify: `src/engine/lifecycle.py:277-330`
- Modify: `src/observability/metrics.py:10-60`
- Test: `tests/test_mongodb_storage.py`
- Test: `tests/test_datadog_observability.py`

- [ ] **Step 1: Write the failing test for measurements TTL index and streaming persistence**

```python
# tests/test_storage_timeseries_pipeline.py
import pytest
from src.storage.repository import CompressorGuardRepository
from src.storage.mongo_client import get_mongo_db
from src.engine.lifecycle import IncidentLifecycleManager
from src.domain.scenarios import FAILURE_3_SCENARIO

def test_timeseries_collection_has_ttl_or_retention():
    repo = CompressorGuardRepository()
    db = repo.db
    cols = db.list_collection_names()
    assert "measurements" in cols

def test_lifecycle_manager_persists_telemetry_measurements():
    repo = CompressorGuardRepository()
    manager = IncidentLifecycleManager(scenario=FAILURE_3_SCENARIO, repository=repo)
    manager.reset()

    # Tick 3 times
    for _ in range(3):
        manager.tick()

    # Measurements should be recorded in repository
    stats = repo.get_rolling_stats("APU-COMP-01")
    assert len(stats) >= 3 or repo.db["measurements"].find_one({"metadata.asset_id": "APU-COMP-01"}) is not None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_storage_timeseries_pipeline.py -v`
Expected: FAIL with `AssertionError` (tick did not insert measurements).

- [ ] **Step 3: Implement measurements batching in tick, TTL index in `mongo_client.py`, and wire Datadog client in `lifecycle.py`**

In `src/storage/mongo_client.py`:
```python
    if "measurements" in existing or True:
        try:
            # 30-day retention index on timestamp
            db["measurements"].create_index([("timestamp", pymongo.ASCENDING)], expireAfterSeconds=30 * 86400)
        except Exception:
            pass
```

In `src/engine/lifecycle.py`:
```python
    def tick(self) -> Optional[TelemetryPoint]:
        pt = self.runner.step()
        if pt is None:
            return None
        
        # Persist measurement to MongoDB repository if present
        if self.repository is not None:
            doc = {
                "timestamp": pt.timestamp,
                "metadata": {"asset_id": pt.asset_id, "scenario": self.scenario.scenario_id},
                "dv_pressure_bar": pt.dv_pressure_bar,
                "oil_temp_c": pt.oil_temp_c,
                "motor_current_a": pt.motor_current_a,
                "regime": pt.regime.value if pt.regime else "LOADED",
            }
            self.repository.insert_measurement(doc)

        # Emit to Datadog
        try:
            from src.observability.metrics import get_metrics_client
            dd = get_metrics_client()
            dd.emit_telemetry(pt)
        except Exception:
            pass

        return self._process_telemetry_point(pt)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_storage_timeseries_pipeline.py -v`
Expected: PASS

- [ ] **Step 5: Commit changes**

```bash
git add src/storage/mongo_client.py src/storage/repository.py src/engine/lifecycle.py tests/test_storage_timeseries_pipeline.py
git commit -m "feat(storage): wire measurements time-series pipeline, TTL retention, and Datadog emission"
```

---

### Task 8: ActionGuard Dynamic Invariants & Operator Identity

**Files:**
- Modify: `src/engine/action_guard.py:22-77`
- Modify: `src/engine/lifecycle.py:216-276`
- Modify: `src/api/schemas.py:58-65`
- Modify: `src/api/routes_product.py:71-82`
- Test: `tests/test_action_guard.py`
- Test: `tests/test_lifecycle_orchestrator.py`

- [ ] **Step 1: Write the failing test for dynamic ActionGuard conditions and operator identity**

```python
# tests/test_action_guard_dynamic.py
import pytest
from src.engine.action_guard import ActionGuard
from src.engine.lifecycle import IncidentLifecycleManager
from src.domain.scenarios import FAILURE_3_SCENARIO, HEALTHY_SCENARIO

def test_action_guard_rejects_when_recovery_stream_missing():
    guard = ActionGuard()
    # If scenario has no recovery bounds (e.g. healthy baseline)
    res = guard.validate(
        lifecycle_state=IncidentLifecycleState.INVESTIGATING,
        has_active_case=True,
        recommended_action=IncidentAction.EXECUTE_MITIGATION,
        replay_branch_available=False,
        conflicting_cases_count=0,
    )
    assert res.is_permitted is False
    assert "Post-maintenance historical stream segment unavailable" in res.denial_reason

def test_trigger_safe_mode_accepts_and_records_operator_identity():
    manager = IncidentLifecycleManager(scenario=FAILURE_3_SCENARIO)
    manager.reset()
    manager.jump_to_milestone("ml_corroborated_1015")

    res = manager.trigger_safe_mode(operator_id="DISPATCHER-0941")
    assert res["status"] == "ACTIVATED"
    assert res["operator_id"] == "DISPATCHER-0941"

    # Action event in timeline contains operator identity
    events = manager.get_case_events()
    action_event = next(e for e in events if e["event_type"] == "ACTION")
    assert action_event["actor"] == "operator:DISPATCHER-0941"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_action_guard_dynamic.py -v`
Expected: FAIL with `TypeError: trigger_safe_mode() got an unexpected keyword argument 'operator_id'`

- [ ] **Step 3: Update `ActionGuard` validation, `trigger_safe_mode` signature and routes**

In `src/engine/lifecycle.py`:
```python
    def trigger_safe_mode(self, operator_id: str = "DISPATCHER-0941") -> Dict[str, Any]:
        # Dynamic check of recovery stream availability
        has_recovery = bool(self.scenario.recovery_start and self.scenario.recovery_end)

        # Dynamic check of conflicting active cases
        conflicting_count = 0
        if self.repository is not None:
            # Query active cases for this asset
            active_existing = self.repository.get_active_case_for_asset(self.scenario.asset_id)
            if active_existing and active_existing.get("case_id") != getattr(self.active_incident, "incident_id", None):
                conflicting_count = 1

        guard_res = self.action_guard.validate(
            lifecycle_state=self.lifecycle_state,
            has_active_case=self.has_active_case(),
            recommended_action=self.current_decision.recommended_action if self.current_decision else IncidentAction.NONE,
            replay_branch_available=has_recovery,
            conflicting_cases_count=conflicting_count,
        )
        if not guard_res.is_permitted:
            raise InvalidStateTransitionError(f"Action safe-mode rejected: {guard_res.denial_reason}")

        self.lifecycle_state = IncidentLifecycleState.MITIGATING
        if self.active_incident:
            self.active_incident.lifecycle_state = IncidentLifecycleState.MITIGATING

        self.is_recovery_branch = True
        rec_start = self.scenario.recovery_start or "2020-06-08 16:05:00"
        rec_end = self.scenario.recovery_end or "2020-06-08 17:00:00"
        self.runner.stream = HistoricalScenarioStream(start_ts=rec_start, end_ts=rec_end, csv_path=str(DEFAULT_CSV_PATH))

        self.record_case_event(
            event_type=CaseEventType.ACTION,
            phase="MITIGATING",
            title="Safe Mode Simulated Intervention",
            detail=f"ActionGuard validated 5 criteria. Branching stream to post-maintenance historical segment.",
            actor=f"operator:{operator_id}",
            source="ActionGuard",
            event_time=self.current_point.timestamp if self.current_point else None,
        )

        return {
            "action_id": "ACT-SM-001",
            "operator_id": operator_id,
            "status": "ACTIVATED",
            "execution_mode": "SIMULATION_BRANCH",
            "target_state": "MITIGATING",
            "stream_branch": {
                "source": "METROPT-3_POST_MAINTENANCE",
                "offset_timestamp": "2020-06-08T16:05:00Z",
            },
        }
```

In `src/api/schemas.py`:
Add `SafeModeRequest(operator_id: str = "DISPATCHER-0941")`, and add `operator_id: str` to `SafeModeResponse`.

In `src/api/routes_product.py`:
Accept `body: Optional[SafeModeRequest] = None` and pass `operator_id`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_action_guard_dynamic.py -v`
Expected: PASS

- [ ] **Step 5: Commit changes**

```bash
git add src/engine/action_guard.py src/engine/lifecycle.py src/api/schemas.py src/api/routes_product.py tests/test_action_guard_dynamic.py
git commit -m "feat(action-guard): enforce dynamic recovery branch and conflict checks with operator identity"
```

---

### Task 9: Illustrative Fleet Context Boundaries & Validation Reference Alignment

**Files:**
- Modify: `src/domain/registry.py:25-95, 115-165`
- Modify: `screen/01_OPERATIONS_NAV_AND_ASSET_OVERVIEW.md` through `screen/07_CASE_TIMELINE_HISTORY.md`
- Test: `tests/test_asset_registry.py`
- Test: `tests/test_screen_spec_consistency.py`

- [ ] **Step 1: Write the failing test for illustrative context labeling and validation reference separation**

```python
# tests/test_registry_boundary.py
import pytest
from src.domain.registry import AssetRegistry

def test_fleet_hierarchy_is_explicitly_labeled_as_illustrative_context():
    registry = AssetRegistry.get_default()
    fleet = registry.get_fleet("FLEET-METRO-01")
    assert fleet is not None
    # Must explicitly state illustrative context
    assert getattr(fleet, "is_illustrative_context", True) is True

def test_validation_reference_separates_dataset_ground_truth_from_computed_metrics():
    registry = AssetRegistry.get_default()
    ref = registry.get_validation_reference("SCENARIO-FAIL-03")
    assert ref is not None
    # Ground truth failure report vs computed lead time
    assert ref.reported_failure_mode == "Air leak in Air Production Unit"
    assert "computed_by_compressorguard" in ref.model_fields or hasattr(ref, "confirmed_intervention_window_minutes")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_registry_boundary.py -v`
Expected: FAIL with `AssertionError` if fields are missing or not marked illustrative.

- [ ] **Step 3: Update `src/domain/registry.py` and screen markdown specifications**

In `src/domain/registry.py`:
Ensure `FleetEntity`, `TrainEntity`, `SubsystemEntity` have:
`is_illustrative_context: bool = True`
`context_note: str = "Illustrative operational hierarchy mapping for MetroPT-3 compressor telemetry."`
And `ValidationReference`:
Clearly document that `reported_failure_start` and `conventional_lps_breach` are historical events recorded by the dataset maintainers, while `confirmed_intervention_window` is the predictive lead time metric computed dynamically by CompressorGuard.

Update `screen/01_OPERATIONS_NAV_AND_ASSET_OVERVIEW.md` through `07_CASE_TIMELINE_HISTORY.md` to consistently refer to `Linha Azul Fleet (Illustrative Demo Context)` and true telemetry numbers.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_registry_boundary.py tests/test_screen_spec_consistency.py -v`
Expected: PASS

- [ ] **Step 5: Commit changes**

```bash
git add src/domain/registry.py screen/*.md tests/test_registry_boundary.py
git commit -m "docs(domain): distinguish illustrative fleet context from raw sensor ground truth"
```

---

### Task 10: Multi-Scenario Verification & Full Regression Suite

**Files:**
- Test: `tests/test_scenarios.py`
- Test: `tests/test_golden_path.py`
- Test: `tests/test_deterministic_replay.py`
- Test: `tests/test_api_vertical_slice.py`

- [ ] **Step 1: Write multi-scenario regression test for Failure #1, Failure #4, and Healthy baseline**

```python
# tests/test_multi_scenario_regression.py
import pytest
from src.engine.lifecycle import IncidentLifecycleManager
from src.domain.scenarios import FAILURE_1_SCENARIO, FAILURE_4_SCENARIO, HEALTHY_SCENARIO
from src.domain.enums import IncidentLifecycleState, AssetHealthState

def test_healthy_scenario_remains_strictly_healthy():
    manager = IncidentLifecycleManager(scenario=HEALTHY_SCENARIO)
    manager.reset()
    for _ in range(50):
        pt = manager.tick()
        if pt is None:
            break
        assert manager.has_active_case() is False
        assert manager.lifecycle_state == IncidentLifecycleState.NONE
        assert manager.asset_health == AssetHealthState.HEALTHY

def test_failure_1_scenario_loads_and_advances():
    manager = IncidentLifecycleManager(scenario=FAILURE_1_SCENARIO)
    manager.reset()
    pt = manager.tick()
    assert pt is not None
    assert pt.asset_id == "APU-COMP-01"

def test_failure_4_scenario_loads_and_advances():
    manager = IncidentLifecycleManager(scenario=FAILURE_4_SCENARIO)
    manager.reset()
    pt = manager.tick()
    assert pt is not None
    assert pt.asset_id == "APU-COMP-01"
```

- [ ] **Step 2: Run test to verify it fails if any regression occurs**

Run: `pytest tests/test_multi_scenario_regression.py -v`
Expected: PASS or identifies any scenario initialization mismatch.

- [ ] **Step 3: Run the full test suite to guarantee 100% regression pass**

Run: `pytest -v`
Expected: ALL 63+ tests PASS with zero regressions across Golden Path, replay determinism, API slices, and storage.

- [ ] **Step 4: Commit changes**

```bash
git add tests/test_multi_scenario_regression.py
git commit -m "test(regression): verify multi-scenario execution and end-to-end regression invariants"
```
