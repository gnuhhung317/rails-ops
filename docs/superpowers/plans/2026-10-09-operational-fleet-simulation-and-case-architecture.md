# Operational Fleet, Deterministic Live Simulation & Case Architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Triển khai toàn diện kiến trúc sản phẩm mới cho CompressorGuard: thiết lập Asset Hierarchy 4 cấp (Fleet -> Train -> APU -> Compressor), tách biệt 3 lớp dữ liệu (Business Context, Observed State, Validation Ground Truth), xây dựng Deterministic Live Simulation Runner trên nền `event_time` gốc của MetroPT-3 với điều khiển tốc độ (1x/10x/60x), tinh chỉnh DecisionEngine để ML đóng vai trò Corroboration thuần túy (không tự tạo Case), bổ sung ActionGuard 5 tiêu chí cho Safe Mode simulation, triển khai CaseEvent Timeline Ledger chuẩn Datadog, và expose bộ API `GET /api/operations`, `GET /api/case`, `GET /api/case/events`, `POST /api/case/close`.

**Architecture:** Mở rộng domain với `src/domain/registry.py` (Asset Registry & Validation Reference) và `OperationalCase` / `CaseEvent` trong `src/domain/models.py`. Xây dựng streaming layer `src/engine/simulation.py` tách biệt tuyệt đối giữa `event_time` (thời gian dữ liệu lịch sử) và `simulation_time` (thời gian demo trải nghiệm). Cập nhật `src/engine/decision.py` đảm bảo chỉ bộ ba Physical Pressure + Thermal + Temporal mới kích hoạt tạo Case, trong khi ML Isolation Forest (5 đặc trưng LOADED) đóng vai trò độc lập nâng Confidence lên HIGH và đề xuất mitigation. Bổ sung `src/engine/action_guard.py` kiểm soát rẽ nhánh mô phỏng Safe Mode, và tích hợp ledger vào `src/engine/lifecycle.py`. Đồng bộ hóa các hợp đồng REST API và cập nhật toàn bộ 7 file đặc tả `screen/*.md`.

**Tech Stack:** Python 3.12, FastAPI, Pydantic, Pandas, Scikit-learn (Isolation Forest), Pytest.

---

### Task 1: Asset Hierarchy & 3-Layer Data Architecture (Registry & Ground Truth)

**Files:**
- Create: `src/domain/registry.py`
- Modify: `src/domain/models.py`
- Test: `tests/test_asset_registry.py`

- [ ] **Step 1: Write the failing test for Asset Registry and Ground Truth Validation Reference**

```python
# tests/test_asset_registry.py
import pytest
from src.domain.registry import (
    AssetRegistry,
    FleetEntity,
    TrainEntity,
    SubsystemEntity,
    CompressorAssetEntity,
    ValidationReference,
)

def test_asset_hierarchy_resolution():
    registry = AssetRegistry.get_default()
    
    # 1. Verify 4-level hierarchy structure
    fleet = registry.get_fleet("FLEET-METRO-01")
    assert fleet is not None
    assert fleet.name == "Metro Fleet (Linha Azul)"
    
    train = registry.get_train("TRAIN-302")
    assert train is not None
    assert train.fleet_id == "FLEET-METRO-01"
    assert train.model == "Series 300 EMU"
    
    subsystem = registry.get_subsystem("SUB-APU-01")
    assert subsystem is not None
    assert subsystem.train_id == "TRAIN-302"
    assert subsystem.name == "Air Production Unit"
    
    asset = registry.get_asset("APU-COMP-01")
    assert asset is not None
    assert asset.subsystem_id == "SUB-APU-01"
    assert asset.criticality == "CRITICAL"
    assert asset.service_role == "Main Air Supply"

def test_validation_reference_ground_truth_separation():
    registry = AssetRegistry.get_default()
    ref = registry.get_validation_reference("SCENARIO-FAIL-03")
    
    assert ref is not None
    assert ref.scenario_id == "SCENARIO-FAIL-03"
    assert ref.scenario_name == "Failure #3 — Air Leak / High Stress"
    assert ref.dataset_source == "MetroPT-3 Historical Telemetry"
    assert ref.reported_failure_mode == "Air leak in Air Production Unit"
    assert ref.reported_failure_start == "2020-06-05T10:00:00Z"
    assert ref.conventional_lps_breach == "2020-06-06T19:42:19Z"
    # Ground truth is distinct from online detection
    assert ref.online_detector_confirmation == "2020-06-05T09:50:39Z"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_asset_registry.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'src.domain.registry'`

- [ ] **Step 3: Implement `src/domain/registry.py`**

```python
# src/domain/registry.py
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class FleetEntity(BaseModel):
    fleet_id: str = "FLEET-METRO-01"
    name: str = "Metro Fleet (Linha Azul)"
    operator_name: str = "Metro do Porto / CP"
    depot_location: str = "Depot Oriente"
    train_ids: List[str] = Field(default_factory=lambda: ["TRAIN-302"])

class TrainEntity(BaseModel):
    train_id: str = "TRAIN-302"
    fleet_id: str = "FLEET-METRO-01"
    model: str = "Series 300 EMU"
    car_number: str = "Car 1 (Leading Cab)"
    service_status: str = "REVENUE_SERVICE"
    subsystem_ids: List[str] = Field(default_factory=lambda: ["SUB-APU-01"])

class SubsystemEntity(BaseModel):
    subsystem_id: str = "SUB-APU-01"
    train_id: str = "TRAIN-302"
    name: str = "Air Production Unit"
    subsystem_code: str = "APU"
    asset_ids: List[str] = Field(default_factory=lambda: ["APU-COMP-01"])

class CompressorAssetEntity(BaseModel):
    asset_id: str = "APU-COMP-01"
    subsystem_id: str = "SUB-APU-01"
    name: str = "Air Compressor Unit #01"
    criticality: str = "CRITICAL"
    service_role: str = "Main Air Supply"
    rated_pressure_bar: float = 10.0
    discharge_valve_model: str = "Knorr-Bremse LP49"

class ValidationReference(BaseModel):
    scenario_id: str = "SCENARIO-FAIL-03"
    scenario_name: str = "Failure #3 — Air Leak / High Stress"
    dataset_source: str = "MetroPT-3 Historical Telemetry"
    historical_period: str = "February 2020 — August 2020"
    reported_failure_mode: str = "Air leak in Air Production Unit"
    reported_failure_start: str = "2020-06-05T10:00:00Z"
    conventional_lps_breach: str = "2020-06-06T19:42:19Z"
    online_detector_confirmation: str = "2020-06-05T09:50:39Z"
    confirmed_intervention_window_minutes: int = 2032
    confirmed_intervention_window_formatted: str = "33h 52m"
    maintenance_summary: str = (
        "UCI dataset ground truth record: MetroPT-3 compressor failure report #3 "
        "indicates discharge valve leak and high thermal stress. CompressorGuard provides "
        "a 33h 52m actionable intervention window prior to reactive Low Pressure Switch breach."
    )

class AssetRegistry:
    def __init__(self) -> None:
        self.fleets: Dict[str, FleetEntity] = {
            "FLEET-METRO-01": FleetEntity(),
        }
        self.trains: Dict[str, TrainEntity] = {
            "TRAIN-302": TrainEntity(),
        }
        self.subsystems: Dict[str, SubsystemEntity] = {
            "SUB-APU-01": SubsystemEntity(),
        }
        self.assets: Dict[str, CompressorAssetEntity] = {
            "APU-COMP-01": CompressorAssetEntity(),
        }
        self.validation_references: Dict[str, ValidationReference] = {
            "SCENARIO-FAIL-03": ValidationReference(),
        }

    @classmethod
    def get_default(cls) -> "AssetRegistry":
        return cls()

    def get_fleet(self, fleet_id: str) -> Optional[FleetEntity]:
        return self.fleets.get(fleet_id)

    def get_train(self, train_id: str) -> Optional[TrainEntity]:
        return self.trains.get(train_id)

    def get_subsystem(self, subsystem_id: str) -> Optional[SubsystemEntity]:
        return self.subsystems.get(subsystem_id)

    def get_asset(self, asset_id: str) -> Optional[CompressorAssetEntity]:
        return self.assets.get(asset_id)

    def get_validation_reference(self, scenario_id: str) -> Optional[ValidationReference]:
        return self.validation_references.get(scenario_id)

    def get_asset_hierarchy_tree(self) -> Dict[str, Any]:
        return {
            "fleet": self.fleets["FLEET-METRO-01"].model_dump(),
            "train": self.trains["TRAIN-302"].model_dump(),
            "subsystem": self.subsystems["SUB-APU-01"].model_dump(),
            "asset": self.assets["APU-COMP-01"].model_dump(),
        }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_asset_registry.py -v`  
Expected: PASS

- [ ] **Step 5: Commit changes**

```bash
git add src/domain/registry.py tests/test_asset_registry.py
git commit -m "feat(domain): add asset hierarchy registry and ground truth validation reference"
```

---

### Task 2: Live Simulation & Deterministic ScenarioStream Engine

**Files:**
- Create: `src/engine/simulation.py`
- Test: `tests/test_simulation_runner.py`

- [ ] **Step 1: Write the failing test for ScenarioStream and SimulationRunner**

```python
# tests/test_simulation_runner.py
from datetime import datetime, timedelta
import pytest
from src.domain.models import TelemetryPoint
from src.engine.simulation import (
    ScenarioStream,
    HistoricalScenarioStream,
    SimulationRunner,
    SimulationPacingConfig,
)

class DummyScenarioStream(ScenarioStream):
    def __init__(self, timestamps):
        self.timestamps = timestamps
        self.idx = 0

    def next(self):
        if self.idx >= len(self.timestamps):
            return None
        ts = self.timestamps[self.idx]
        self.idx += 1
        return TelemetryPoint(
            asset_id="APU-COMP-01",
            timestamp=ts,
            tp2_bar=0.0, tp3_bar=0.0, h1_bar=0.0, dv_pressure_bar=0.0,
            reservoirs_bar=8.0, oil_temp_c=60.0, motor_current_a=6.5,
            comp_val=0.0, dv_electric=1.0, towers_val=0.0, mpg_val=0.0,
            lps_active=0.0, pressure_switch=0.0, oil_level_low=0.0,
            caudal_impulses=0.0
        )

    def reset(self):
        self.idx = 0

    def seek(self, event_time):
        self.idx = 0
        while self.idx < len(self.timestamps) and self.timestamps[self.idx] < event_time:
            self.idx += 1

def test_simulation_runner_time_separation_and_speed_pacing():
    # Sequence with a normal 10s gap and an 80s telemetry gap
    t0 = datetime(2020, 6, 5, 9, 50, 0)
    t1 = datetime(2020, 6, 5, 9, 50, 10) # 10s delta
    t2 = datetime(2020, 6, 5, 9, 51, 30) # 80s delta
    stream = DummyScenarioStream([t0, t1, t2])
    
    runner = SimulationRunner(stream=stream, config=SimulationPacingConfig(speed_multiplier=60.0))
    
    # 1. Event times are preserved exactly as original timestamps (never now())
    p0 = runner.step()
    assert p0.timestamp == t0
    assert runner.current_event_time == t0
    
    # 2. Pacing respects real event delta
    p1 = runner.step()
    assert p1.timestamp == t1
    # delta is 10s historical -> 10 / 60 = 0.1667 simulation seconds
    assert runner.calculate_step_delay(t0, t1) == pytest.approx(10.0 / 60.0)
    
    # 3. Irregular gap respects delta
    p2 = runner.step()
    assert p2.timestamp == t2
    # delta is 80s historical -> 80 / 60 = 1.333 simulation seconds
    assert runner.calculate_step_delay(t1, t2) == pytest.approx(80.0 / 60.0)

def test_simulation_speed_controls():
    stream = DummyScenarioStream([datetime(2020, 6, 5, 9, 50, 0)])
    runner = SimulationRunner(stream=stream)
    
    runner.set_speed(10.0)
    assert runner.config.speed_multiplier == 10.0
    runner.set_speed(300.0)
    assert runner.config.speed_multiplier == 300.0
    
    with pytest.raises(ValueError):
        runner.set_speed(-1.0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_simulation_runner.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'src.engine.simulation'`

- [ ] **Step 3: Implement `src/engine/simulation.py`**

```python
# src/engine/simulation.py
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Generator, Dict, Any
from pydantic import BaseModel, Field

from src.domain.models import TelemetryPoint
from src.engine.replay import ReplayEngine, DEFAULT_CSV_PATH

class SimulationPacingConfig(BaseModel):
    speed_multiplier: float = 60.0  # 1.0, 10.0, 60.0, 300.0
    max_step_delay_seconds: float = 2.0  # Bound extreme gaps for smooth UI

class ScenarioStream(ABC):
    @abstractmethod
    def next(self) -> Optional[TelemetryPoint]:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass

    @abstractmethod
    def seek(self, event_time: datetime) -> None:
        pass

class HistoricalScenarioStream(ScenarioStream):
    def __init__(
        self,
        start_ts: str = "2020-06-05 09:40:00",
        end_ts: str = "2020-06-06 20:00:00",
        csv_path: str = str(DEFAULT_CSV_PATH),
    ) -> None:
        self.start_ts = start_ts
        self.end_ts = end_ts
        self.replay = ReplayEngine(csv_path)
        self.generator: Optional[Generator[TelemetryPoint, None, None]] = None
        self.reset()

    def reset(self) -> None:
        self.generator = self.replay.stream_telemetry(self.start_ts, self.end_ts)

    def next(self) -> Optional[TelemetryPoint]:
        if self.generator is None:
            self.reset()
        try:
            return next(self.generator)
        except StopIteration:
            return None

    def seek(self, event_time: datetime) -> None:
        self.reset()
        while True:
            pt = self.next()
            if pt is None or pt.timestamp >= event_time:
                break

class SimulationRunner:
    """
    SimulationRunner drives pacing and stream advancement.
    INVARIANTS:
    1. Strictly preserves original TelemetryPoint.timestamp as event_time.
    2. Calculates step pacing based on delta event_time / speed_multiplier.
    3. Exposes play, pause, step, reset, and speed configuration.
    """
    def __init__(
        self,
        stream: ScenarioStream,
        config: Optional[SimulationPacingConfig] = None,
        scenario_name: str = "Failure #3 — Air Leak",
    ) -> None:
        self.stream = stream
        self.config = config or SimulationPacingConfig()
        self.scenario_name = scenario_name
        self.is_paused: bool = True
        self.current_point: Optional[TelemetryPoint] = None
        self.last_event_time: Optional[datetime] = None
        self.current_event_time: Optional[datetime] = None
        self.total_points_emitted: int = 0

    def set_speed(self, multiplier: float) -> None:
        if multiplier <= 0:
            raise ValueError(f"Speed multiplier must be positive, got {multiplier}")
        self.config.speed_multiplier = multiplier

    def calculate_step_delay(self, prev_time: datetime, next_time: datetime) -> float:
        delta_sec = max(0.0, (next_time - prev_time).total_seconds())
        scaled = delta_sec / self.config.speed_multiplier
        return min(scaled, self.config.max_step_delay_seconds)

    def step(self) -> Optional[TelemetryPoint]:
        pt = self.stream.next()
        if pt is None:
            return None
        self.last_event_time = self.current_event_time
        self.current_event_time = pt.timestamp
        self.current_point = pt
        self.total_points_emitted += 1
        return pt

    def reset(self) -> None:
        self.stream.reset()
        self.current_point = None
        self.last_event_time = None
        self.current_event_time = None
        self.total_points_emitted = 0
        self.is_paused = True

    def get_status(self) -> Dict[str, Any]:
        return {
            "scenario_name": self.scenario_name,
            "is_paused": self.is_paused,
            "speed_multiplier": self.config.speed_multiplier,
            "current_event_time": (
                self.current_event_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                if self.current_event_time
                else None
            ),
            "total_points_emitted": self.total_points_emitted,
            "mode": "LIVE_SIMULATION",
            "provenance": "MetroPT-3 Historical Telemetry",
        }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_simulation_runner.py -v`  
Expected: PASS

- [ ] **Step 5: Commit changes**

```bash
git add src/engine/simulation.py tests/test_simulation_runner.py
git commit -m "feat(simulation): add ScenarioStream and SimulationRunner with delta-time pacing"
```

---

### Task 3: DecisionEngine Alignment — ML as Independent Corroboration Only & Provenance

**Files:**
- Modify: `src/engine/decision.py`
- Modify: `src/engine/detectors.py`
- Test: `tests/test_decision_ml_corroboration.py`
- Test: `tests/test_evidence_provenance.py`

- [ ] **Step 1: Write the failing tests for ML Corroboration Invariant and Provenance Expose**

```python
# tests/test_decision_ml_corroboration.py
from datetime import datetime
import pytest
from src.domain.enums import (
    OperatingRegime,
    AssetHealthState,
    IncidentAction,
    OperationalConfidence,
    DetectorStatus,
    Severity,
    EvidenceCode,
)
from src.domain.models import EvidenceState, DetectorResult, IncidentContext
from src.engine.decision import DecisionEngine

def test_ml_cannot_create_case_on_its_own():
    engine = DecisionEngine()
    
    # EvidenceState containing ML trigger only (no physical severe pressure or temporal step)
    ml_only_state = EvidenceState(
        asset_id="APU-COMP-01",
        timestamp=datetime(2020, 6, 5, 9, 30, 0),
        regime=OperatingRegime.LOADED,
        signals=[
            DetectorResult(
                detector_id="isolation_forest",
                evidence_code=EvidenceCode.ML_CORROBORATED,
                status=DetectorStatus.CORROBORATED,
                severity=Severity.HIGH,
                observed_value=0.38,
                baseline_value=0.35,
            )
        ]
    )
    
    decision = engine.evaluate(ml_only_state, incident_context=None)
    # INVARIANT: ML CANNOT CREATE A CASE!
    assert decision.incident_action == IncidentAction.NONE
    assert decision.asset_health != AssetHealthState.CRITICAL

def test_ml_escalates_confidence_and_recommends_mitigation_when_case_active():
    engine = DecisionEngine()
    
    # Confirmed case already active, now ML corroborates
    ml_corroborated_state = EvidenceState(
        asset_id="APU-COMP-01",
        timestamp=datetime(2020, 6, 5, 10, 15, 0),
        regime=OperatingRegime.LOADED,
        signals=[
            DetectorResult(
                detector_id="pressure_anomaly",
                evidence_code=EvidenceCode.PRESSURE_SEVERE,
                status=DetectorStatus.CONFIRMED,
                severity=Severity.CRITICAL,
                observed_value=2.18,
                baseline_value=0.0,
                sigma_deviation=23.75,
            ),
            DetectorResult(
                detector_id="thermal_stress",
                evidence_code=EvidenceCode.THERMAL_STRESS_SEVERE,
                status=DetectorStatus.CONFIRMED,
                severity=Severity.HIGH,
                observed_value=74.97,
                baseline_value=60.0,
                sigma_deviation=5.71,
            ),
            DetectorResult(
                detector_id="isolation_forest",
                evidence_code=EvidenceCode.ML_CORROBORATED,
                status=DetectorStatus.CORROBORATED,
                severity=Severity.HIGH,
                observed_value=0.382,
                baseline_value=0.350,
            ),
        ]
    )
    
    inc_ctx = IncidentContext(
        active_incident_id="CASE-20200605-01",
        lifecycle_state="DETECTED",
    )
    
    decision = engine.evaluate(ml_corroborated_state, incident_context=inc_ctx)
    assert decision.incident_action == IncidentAction.UPDATE_INVESTIGATING
    assert decision.operational_confidence == OperationalConfidence.HIGH
    assert decision.recommended_action == IncidentAction.EXECUTE_MITIGATION
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_decision_ml_corroboration.py -v`  
Expected: FAIL if current code creates incident on ML or behaves inconsistently

- [ ] **Step 3: Modify `src/engine/decision.py` to enforce ML corroboration-only invariant**

Update `src/engine/decision.py`:
```python
# In src/engine/decision.py evaluate():
# Rule 2: Multivariate ML Corroboration
# INVARIANT: ML CANNOT CREATE A CASE. ML only corroborates an existing active case or confirmed degradation.
if has_severe_pressure and has_severe_thermal and has_ml:
    if has_active_incident:
        return Decision(
            asset_health=AssetHealthState.CRITICAL,
            incident_action=IncidentAction.UPDATE_INVESTIGATING,
            operational_confidence=OperationalConfidence.HIGH,
            recommended_action=IncidentAction.EXECUTE_MITIGATION,
            ui_action="Multivariate Corroboration Confirmed",
            reason="Physical step degradation corroborated by multivariate Isolation Forest (5 LOADED features). Safe Mode recommended.",
            evidence_state=evidence_state,
        )
    elif confirmed_degradation:
        # Confirmed physical degradation + ML simultaneous -> create and recommend mitigation
        return Decision(
            asset_health=AssetHealthState.CRITICAL,
            incident_action=IncidentAction.CREATE,
            operational_confidence=OperationalConfidence.HIGH,
            recommended_action=IncidentAction.EXECUTE_MITIGATION,
            ui_action="Confirmed Degradation with ML Corroboration",
            reason="Confirmed severe step degradation corroborated by Isolation Forest.",
            evidence_state=evidence_state,
        )

# If ML triggers without confirmed physical degradation and no active incident:
if has_ml and not has_active_incident and not confirmed_degradation:
    return Decision(
        asset_health=AssetHealthState.DEGRADING,
        incident_action=IncidentAction.NONE,
        operational_confidence=OperationalConfidence.MEDIUM,
        ui_action="Multivariate Corroboration Observed (No Case)",
        reason="Isolation Forest anomaly detected, but physical evidence insufficient to open an operational case.",
        evidence_state=evidence_state,
    )
```

Also ensure in `src/engine/detectors.py` that `IsolationForestDetector` annotates `provenance`:
```python
"provenance": {
    "detector_class": "IsolationForestDetector",
    "method": "Isolation Forest (5 features, LOADED baseline)",
    "feature_names": ["DV_pressure", "H1", "Oil_temperature", "Motor_current", "TP3"],
    "feature_count": 5,
    "threshold": 0.35,
    "role": "Independent Corroboration",
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_decision_ml_corroboration.py tests/test_decision.py -v`  
Expected: PASS

- [ ] **Step 5: Commit changes**

```bash
git add src/engine/decision.py src/engine/detectors.py tests/test_decision_ml_corroboration.py
git commit -m "fix(decision): restrict ML Isolation Forest to independent corroboration only"
```

---

### Task 4: ActionGuard & Controlled Safe Mode Simulation Branch

**Files:**
- Create: `src/engine/action_guard.py`
- Modify: `src/engine/lifecycle.py`
- Test: `tests/test_action_guard.py`

- [ ] **Step 1: Write the failing test for ActionGuard**

```python
# tests/test_action_guard.py
import pytest
from src.domain.enums import IncidentLifecycleState, IncidentAction
from src.engine.action_guard import ActionGuard, ActionGuardCheckResult

def test_action_guard_five_criteria_validation():
    guard = ActionGuard()
    
    # 1. Rejects if case is not in valid phase
    res_invalid_phase = guard.validate(
        lifecycle_state=IncidentLifecycleState.NONE,
        has_active_case=False,
        recommended_action=IncidentAction.EXECUTE_MITIGATION,
        replay_branch_available=True,
    )
    assert res_invalid_phase.is_permitted is False
    assert "Active case required" in res_invalid_phase.denial_reason

    # 2. Rejects if mitigation not recommended by DecisionEngine
    res_no_rec = guard.validate(
        lifecycle_state=IncidentLifecycleState.DETECTED,
        has_active_case=True,
        recommended_action=IncidentAction.NONE,
        replay_branch_available=True,
    )
    assert res_no_rec.is_permitted is False
    assert "Mitigation not recommended" in res_no_rec.denial_reason

    # 3. Permits when all 5 criteria satisfied
    res_valid = guard.validate(
        lifecycle_state=IncidentLifecycleState.INVESTIGATING,
        has_active_case=True,
        recommended_action=IncidentAction.EXECUTE_MITIGATION,
        replay_branch_available=True,
    )
    assert res_valid.is_permitted is True
    assert len(res_valid.checklist) == 5
    assert all(item["passed"] for item in res_valid.checklist)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_action_guard.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'src.engine.action_guard'`

- [ ] **Step 3: Implement `src/engine/action_guard.py`**

```python
# src/engine/action_guard.py
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from src.domain.enums import IncidentLifecycleState, IncidentAction

class ActionGuardCheckResult(BaseModel):
    is_permitted: bool
    denial_reason: str = ""
    checklist: List[Dict[str, Any]] = Field(default_factory=list)

class ActionGuard:
    """
    ActionGuard replaces fake physical safety systems (fake SIL-2, fake actuators)
    with a transparent, policy-controlled simulation boundary:
    1. Case is active and confirmed
    2. DecisionEngine recommends mitigation
    3. Single active case invariant holds
    4. Simulation mode only (transparent operational boundary)
    5. Historical replay branch available
    """
    def validate(
        self,
        lifecycle_state: IncidentLifecycleState,
        has_active_case: bool,
        recommended_action: IncidentAction,
        replay_branch_available: bool = True,
        conflicting_cases_count: int = 0,
    ) -> ActionGuardCheckResult:
        checklist = [
            {
                "id": "CASE_CONFIRMED",
                "label": "Case is active and confirmed",
                "passed": has_active_case and lifecycle_state in (
                    IncidentLifecycleState.DETECTED,
                    IncidentLifecycleState.INVESTIGATING,
                ),
            },
            {
                "id": "MITIGATION_RECOMMENDED",
                "label": "DecisionEngine recommends mitigation",
                "passed": recommended_action == IncidentAction.EXECUTE_MITIGATION,
            },
            {
                "id": "SINGLE_ACTIVE_CASE",
                "label": "No conflicting active cases on asset",
                "passed": conflicting_cases_count == 0,
            },
            {
                "id": "SIMULATION_MODE",
                "label": "Simulation intervention boundary verified",
                "passed": True,
            },
            {
                "id": "REPLAY_BRANCH_AVAILABLE",
                "label": "Post-maintenance historical stream segment available",
                "passed": replay_branch_available,
            },
        ]

        all_passed = all(item["passed"] for item in checklist)
        denial_reason = ""
        if not checklist[0]["passed"]:
            denial_reason = "Active case required in DETECTED or INVESTIGATING state."
        elif not checklist[1]["passed"]:
            denial_reason = "Mitigation not recommended by DecisionEngine."
        elif not checklist[2]["passed"]:
            denial_reason = "Conflicting active cases detected on asset."
        elif not checklist[4]["passed"]:
            denial_reason = "Post-maintenance historical stream segment unavailable."

        return ActionGuardCheckResult(
            is_permitted=all_passed,
            denial_reason=denial_reason,
            checklist=checklist,
        )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_action_guard.py -v`  
Expected: PASS

- [ ] **Step 5: Commit changes**

```bash
git add src/engine/action_guard.py tests/test_action_guard.py
git commit -m "feat(engine): add ActionGuard for transparent safe mode policy control"
```

---

### Task 5: Dynamic Lead Time & Append-Only CaseEvent Timeline Ledger

**Files:**
- Modify: `src/domain/models.py`
- Modify: `src/engine/lifecycle.py`
- Test: `tests/test_case_events_ledger.py`

- [ ] **Step 1: Write the failing test for CaseEvent timeline ledger and case closure**

```python
# tests/test_case_events_ledger.py
from datetime import datetime
import pytest
from src.domain.enums import IncidentLifecycleState
from src.engine.lifecycle import IncidentLifecycleManager

def test_case_event_timeline_ledger_recording():
    manager = IncidentLifecycleManager()
    manager.reset()
    
    # 1. Pre-onset has empty or baseline ledger
    events = manager.get_case_events()
    assert isinstance(events, list)
    
    # 2. Seek to confirmed degradation
    manager.jump_to_milestone("onset_0950")
    events = manager.get_case_events()
    detection_evt = next((e for e in events if e["event_type"] == "DETECTION"), None)
    assert detection_evt is not None
    assert "Confirmed degradation detected" in detection_evt["title"]
    assert detection_evt["phase"] == "DETECTED"

    # 3. Seek to ML corroboration
    manager.jump_to_milestone("ml_corroborated_1015")
    events = manager.get_case_events()
    corr_evt = next((e for e in events if e["event_type"] == "CORROBORATION"), None)
    assert corr_evt is not None
    assert "Isolation Forest" in corr_evt["title"]
    assert corr_evt["phase"] == "INVESTIGATING"

    # 4. Trigger Safe Mode action
    manager.trigger_safe_mode()
    events = manager.get_case_events()
    act_evt = next((e for e in events if e["event_type"] == "ACTION"), None)
    assert act_evt is not None
    assert "Safe Mode" in act_evt["title"]

def test_case_closure_requires_verified_recovery():
    manager = IncidentLifecycleManager()
    manager.reset()
    manager.jump_to_milestone("onset_0950")
    
    # Cannot close case before recovery verified
    with pytest.raises(ValueError, match="Recovery not verified"):
        manager.close_case(operator_id="DISPATCHER-0941")

    # Fast forward to post-maintenance recovery verified
    manager.jump_to_milestone("post_maintenance_1605")
    # Tick 5 healthy cycles
    for _ in range(6):
        manager.tick()
        
    assert manager.recovery_verifier.is_verified is True
    # Now close case succeeds
    result = manager.close_case(operator_id="DISPATCHER-0941", notes="Depot maintenance complete.")
    assert result["status"] == "CASE_CLOSED"
    assert manager.lifecycle_state == IncidentLifecycleState.RESOLVED
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_case_events_ledger.py -v`  
Expected: FAIL with `AttributeError: 'IncidentLifecycleManager' object has no attribute 'get_case_events'`

- [ ] **Step 3: Update `src/domain/models.py` and `src/engine/lifecycle.py`**

In `src/domain/models.py`:
```python
class CaseEventType(str, Enum):
    OBSERVATION = "OBSERVATION"
    DETECTION = "DETECTION"
    CORROBORATION = "CORROBORATION"
    ACTION = "ACTION"
    BENCHMARK = "BENCHMARK"
    RECOVERY = "RECOVERY"
    CASE_CLOSED = "CASE_CLOSED"

class CaseEvent(BaseModel):
    event_id: str
    event_time: datetime
    event_type: CaseEventType
    phase: str
    title: str
    detail: str
    actor: str = "system"
    source: str = "CompressorGuard Engine"
    provenance: Dict[str, Any] = Field(default_factory=dict)
```

In `src/engine/lifecycle.py`:
- Initialize `self.case_events: List[CaseEvent] = []`
- Implement `record_case_event(event_type, phase, title, detail, actor, source, provenance)`
- Record events during:
  - `00:33:07` early excursion suppression -> `OBSERVATION`
  - `09:50:39` onset transition -> `DETECTION`
  - `10:15:00` ML corroboration -> `CORROBORATION`
  - `trigger_safe_mode()` -> `ACTION`
  - LPS reached -> `BENCHMARK`
  - Recovery verified -> `RECOVERY`
  - `close_case()` -> `CASE_CLOSED`
- Implement `close_case(operator_id, notes)` verifying `self.recovery_verifier.is_verified`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_case_events_ledger.py -v`  
Expected: PASS

- [ ] **Step 5: Commit changes**

```bash
git add src/domain/models.py src/engine/lifecycle.py tests/test_case_events_ledger.py
git commit -m "feat(lifecycle): add CaseEvent timeline ledger and verified case closure"
```

---

### Task 6: Operations & Case API Surface Expansion

**Files:**
- Modify: `src/api/schemas.py`
- Modify: `src/api/routes_product.py`
- Modify: `src/api/routes_demo.py`
- Test: `tests/test_operations_api.py`

- [ ] **Step 1: Write the failing test for `/api/operations`, `/api/case`, and `/api/case/events`**

```python
# tests/test_operations_api.py
from fastapi.testclient import TestClient
from src.api.app import create_app

def test_operations_endpoint_structure():
    app = create_app()
    client = TestClient(app)
    
    resp = client.get("/api/operations")
    assert resp.status_code == 200
    data = resp.json()
    
    # 1. Business context hierarchy
    assert "fleet" in data
    assert data["fleet"]["fleet_id"] == "FLEET-METRO-01"
    assert "train" in data
    assert data["train"]["train_id"] == "TRAIN-302"
    assert "asset" in data
    assert data["asset"]["asset_id"] == "APU-COMP-01"
    
    # 2. Operations metrics (truthful, no hardcoded 98%)
    assert "operations_summary" in data
    ops = data["operations_summary"]
    assert ops["monitored_assets_count"] == 1
    assert ops["active_cases_count"] in (0, 1)
    assert ops["scenario_name"] == "Failure #3 — Air Leak"
    assert ops["simulation_mode"] == "LIVE_SIMULATION"

def test_case_timeline_and_closure_flow():
    app = create_app()
    client = TestClient(app)
    
    client.post("/demo/reset", json={"milestone": "onset_0950"})
    
    # GET /api/case (alias for /api/incident)
    case_resp = client.get("/api/case")
    assert case_resp.status_code == 200
    assert case_resp.json()["lifecycle_state"] == "DETECTED"
    
    # GET /api/case/events
    timeline_resp = client.get("/api/case/events")
    assert timeline_resp.status_code == 200
    events = timeline_resp.json()
    assert len(events) >= 1
    assert any(e["event_type"] == "DETECTION" for e in events)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_operations_api.py -v`  
Expected: FAIL with 404 Not Found on `/api/operations`

- [ ] **Step 3: Implement API Schemas and Routes in `src/api/`**

In `src/api/schemas.py`:
- Add `OperationsSummaryInfo`, `OperationsResponse`, `CaseEventItem`, `CaseCloseRequest`, `CaseCloseResponse`, `ValidationReferenceResponse`.

In `src/api/routes_product.py`:
- Add `@router.get("/operations", response_model=OperationsResponse)`
- Add `@router.get("/case", response_model=IncidentResponse)` (and keep `@router.get("/incident")`)
- Add `@router.get("/case/events", response_model=List[CaseEventItem])` (and `@router.get("/timeline")`)
- Add `@router.post("/case/close", response_model=CaseCloseResponse)`
- Add `@router.get("/validation-reference", response_model=ValidationReferenceResponse)`

In `src/api/routes_demo.py`:
- Add simulation controls `GET /demo/simulation` and `POST /demo/simulation/control`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_operations_api.py -v`  
Expected: PASS

- [ ] **Step 5: Commit changes**

```bash
git add src/api/schemas.py src/api/routes_product.py src/api/routes_demo.py tests/test_operations_api.py
git commit -m "feat(api): expose /api/operations, /api/case/events, and /api/case/close endpoints"
```

---

### Task 7: Screen Specifications Synchronization (Truthful Operations Console)

**Files:**
- Modify: `screen/01_OPERATIONS_NAV_AND_ASSET_OVERVIEW.md`
- Modify: `screen/03_CASE_WORKSPACE_WHAT_CHANGED.md`
- Modify: `screen/04_CASE_WORKSPACE_WHY_EVIDENCE.md`
- Modify: `screen/05_CASE_WORKSPACE_WHAT_DID_WE_DO.md`
- Modify: `screen/06_CASE_WORKSPACE_DID_IT_WORK.md`
- Modify: `screen/07_CASE_TIMELINE_HISTORY.md`
- Test: `tests/test_screen_spec_consistency.py`

- [ ] **Step 1: Write test verifying screen spec alignment with backend contracts**

```python
# tests/test_screen_spec_consistency.py
from pathlib import Path

def test_screen_specs_truthfulness_and_no_fake_live():
    screen_dir = Path("screen")
    s1 = (screen_dir / "01_OPERATIONS_NAV_AND_ASSET_OVERVIEW.md").read_text(encoding="utf-8")
    s3 = (screen_dir / "03_CASE_WORKSPACE_WHAT_CHANGED.md").read_text(encoding="utf-8")
    s4 = (screen_dir / "04_CASE_WORKSPACE_WHY_EVIDENCE.md").read_text(encoding="utf-8")
    s5 = (screen_dir / "05_CASE_WORKSPACE_WHAT_DID_WE_DO.md").read_text(encoding="utf-8")
    s7 = (screen_dir / "07_CASE_TIMELINE_HISTORY.md").read_text(encoding="utf-8")
    
    # 1. No fake [🔴 LIVE] in header, replaced by LIVE SIMULATION
    assert "[🔴 LIVE]" not in s1
    assert "LIVE SIMULATION" in s1 or "HISTORICAL REPLAY" in s1
    
    # 2. No fake 98% fleet health claim
    assert "FLEET HEALTH: 98%" not in s1
    
    # 3. Screen 04 specifies 5 features for IF, not 15 sensors
    assert "5 features" in s4 or "5 telemetry features" in s4
    
    # 4. Screen 05 documents ActionGuard
    assert "ActionGuard" in s5 or "ACTION GUARD" in s5
    
    # 5. Screen 07 documents Datadog ledger
    assert "CaseEvent" in s7 or "AUDIT LEDGER" in s7
```

- [ ] **Step 2: Run test to verify it fails initially**

Run: `pytest tests/test_screen_spec_consistency.py -v`  
Expected: FAIL due to existing `[🔴 LIVE]` or `FLEET HEALTH: 98%` in specs

- [ ] **Step 3: Update `screen/*.md` to reflect truthful product semantics**

- Update `screen/01_OPERATIONS_NAV_AND_ASSET_OVERVIEW.md`:
  - Header: `[● LIVE SIMULATION · HISTORICAL DATA] | Scenario: Failure #3 | Event Time: 2020-06-05 09:50:39 UTC`
  - Operational KPIs: `1 MONITORED ASSET`, `0/1 ACTIVE CASES`, `1 ASSET OBSERVING`, `33h 52m INTERVENTION WINDOW`.
  - Asset Hierarchy: Operations -> Metro Fleet -> Train-302 -> APU -> APU-COMP-01.
- Update `screen/03_CASE_WORKSPACE_WHAT_CHANGED.md`:
  - 4 layers: Observed, Operational Condition, Business Context, Validation Reference.
  - Terminology: "Confirmed degradation detected" instead of "Onset".
- Update `screen/04_CASE_WORKSPACE_WHY_EVIDENCE.md`:
  - Evidence cards include PROVENANCE (Source class, method, regime, timestamp).
  - Clarify Isolation Forest uses 5 LOADED features, not 15.
- Update `screen/05_CASE_WORKSPACE_WHAT_DID_WE_DO.md`:
  - Replace fake safety with `ActionGuard` 5 criteria.
  - Explain simulation branch to post-maintenance segment.
- Update `screen/06_CASE_WORKSPACE_DID_IT_WORK.md`:
  - "RECOVERY CRITERIA VERIFIED (5/5 healthy LOADED observations)".
- Update `screen/07_CASE_TIMELINE_HISTORY.md`:
  - Aligned with backend `CaseEvent` ledger.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_screen_spec_consistency.py -v`  
Expected: PASS

- [ ] **Step 5: Commit changes**

```bash
git add screen/ tests/test_screen_spec_consistency.py
git commit -m "docs(screen): update screen specs to reflect truthful operations architecture"
```

---

### Task 8: Full Regression & Deterministic Golden Path Verification

**Files:**
- Test: `tests/test_api_vertical_slice.py`
- Test: `tests/test_golden_path.py`
- Test: `tests/test_lifecycle_orchestrator.py`

- [ ] **Step 1: Run complete test suite**

Run: `pytest tests/ -v`  
Expected: All tests PASS with zero regressions across deterministic replay, vertical slice, and value model.

- [ ] **Step 2: Verify git status is clean**

Run: `git status`  
Expected: working tree clean.
