# Rail Economics & Configurable Value Model API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cung cấp endpoint REST API `/api/incident/business-impact` và schema DTO kinh tế vận hành đường sắt (Rail Economics), cho phép tính toán kịch bản kinh tế minh bạch (Conservative, Base, Severe) gắn liền với lead time thực tế của sự cố mà không can thiệp vào máy trạng thái lõi đã đóng băng.

**Architecture:** Mở rộng domain layer với `BusinessImpactDTO` và `ValueScenarioConfig` trong `src/domain/models.py`. Tạo module tính toán thuần túy `src/engine/economics.py` tuân thủ nguyên tắc "Observed ≠ Modeled ≠ Verified", và expose endpoint mới trong `src/api/routes.py` kế thừa từ `IncidentLifecycleManager`.

**Tech Stack:** Python 3.12, Pydantic, FastAPI, Pytest.

---

### Task 1: Domain Schemas & DTO Definition for Rail Economics

**Files:**
- Modify: `src/domain/models.py`
- Test: `tests/test_value_model.py`

- [ ] **Step 1: Write the failing test for Value Model schemas**

```python
# tests/test_value_model.py
from src.domain.models import ValueScenarioConfig, BusinessImpactDTO

def test_value_scenario_calculation():
    config = ValueScenarioConfig(
        scenario_name="BASE_METRO_DISRUPTION",
        downtime_cost_per_hour=2500.0,
        estimated_avoided_downtime_hours=12.0,
        emergency_overtime_premium=2000.0,
        engineering_minutes_saved=17.0,
        engineer_loaded_rate=75.0,
    )
    impact = config.calculate_impact()
    assert impact["avoided_downtime_value"] == 30000.0
    assert impact["labor_investigation_saved"] == 21.25
    assert impact["total_gross_avoided_impact"] == 32021.25
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_value_model.py -v`  
Expected: FAIL with `ImportError: cannot import name 'ValueScenarioConfig'`

- [ ] **Step 3: Implement ValueScenarioConfig & BusinessImpactDTO in `src/domain/models.py`**

```python
class ValueScenarioConfig(BaseModel):
    scenario_name: str = "BASE_METRO_DISRUPTION"
    downtime_cost_per_hour: float = 2500.0
    estimated_avoided_downtime_hours: float = 12.0
    emergency_overtime_premium: float = 2000.0
    engineering_minutes_saved: float = 17.0
    engineer_loaded_rate: float = 75.0

    def calculate_impact(self) -> Dict[str, float]:
        avoided_downtime = self.downtime_cost_per_hour * self.estimated_avoided_downtime_hours
        labor_saved = (self.engineering_minutes_saved / 60.0) * self.engineer_loaded_rate
        total = avoided_downtime + self.emergency_overtime_premium + labor_saved
        return {
            "avoided_downtime_value": avoided_downtime,
            "avoided_emergency_premium": self.emergency_overtime_premium,
            "labor_investigation_saved": labor_saved,
            "total_gross_avoided_impact": total,
        }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_value_model.py -v`  
Expected: PASS

---

### Task 2: Implement Economics Engine Module

**Files:**
- Create: `src/engine/economics.py`
- Test: `tests/test_value_model.py`

- [ ] **Step 1: Write failing test for RailEconomicsEngine**

```python
# append to tests/test_value_model.py
from src.engine.economics import RailEconomicsEngine

def test_rail_economics_engine_predefined_scenarios():
    engine = RailEconomicsEngine()
    conservative = engine.get_scenario("CONSERVATIVE")
    base = engine.get_scenario("BASE")
    severe = engine.get_scenario("SEVERE")
    
    assert conservative.downtime_cost_per_hour == 1200.0
    assert base.downtime_cost_per_hour == 2500.0
    assert severe.downtime_cost_per_hour == 5000.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_value_model.py::test_rail_economics_engine_predefined_scenarios -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'src.engine.economics'`

- [ ] **Step 3: Implement `src/engine/economics.py`**

```python
# src/engine/economics.py
from typing import Dict
from src.domain.models import ValueScenarioConfig

PREDEFINED_SCENARIOS: Dict[str, ValueScenarioConfig] = {
    "CONSERVATIVE": ValueScenarioConfig(
        scenario_name="CONSERVATIVE",
        downtime_cost_per_hour=1200.0,
        estimated_avoided_downtime_hours=4.0,
        emergency_overtime_premium=500.0,
        engineering_minutes_saved=17.0,
        engineer_loaded_rate=75.0,
    ),
    "BASE": ValueScenarioConfig(
        scenario_name="BASE_METRO_DISRUPTION",
        downtime_cost_per_hour=2500.0,
        estimated_avoided_downtime_hours=12.0,
        emergency_overtime_premium=2000.0,
        engineering_minutes_saved=17.0,
        engineer_loaded_rate=75.0,
    ),
    "SEVERE": ValueScenarioConfig(
        scenario_name="SEVERE_LINE_COLLAPSE",
        downtime_cost_per_hour=5000.0,
        estimated_avoided_downtime_hours=24.0,
        emergency_overtime_premium=8500.0,
        engineering_minutes_saved=30.0,
        engineer_loaded_rate=75.0,
    ),
}

class RailEconomicsEngine:
    def get_scenario(self, name: str) -> ValueScenarioConfig:
        return PREDEFINED_SCENARIOS.get(name.upper(), PREDEFINED_SCENARIOS["BASE"])
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_value_model.py::test_rail_economics_engine_predefined_scenarios -v`  
Expected: PASS

---

### Task 3: Expose Business Impact REST API Endpoint

**Files:**
- Modify: `src/api/routes.py`
- Test: `tests/test_api_vertical_slice.py`

- [ ] **Step 1: Write failing test for `GET /api/incident/business-impact`**

```python
# append to tests/test_api_vertical_slice.py
def test_api_business_impact_endpoint(client):
    response = client.get("/api/incident/business-impact?scenario=BASE")
    assert response.status_code == 200
    data = response.json()
    assert "economic_model" in data
    assert data["economic_model"]["scenario_name"] == "BASE_METRO_DISRUPTION"
    assert data["economic_model"]["calculated_impact"]["total_gross_avoided_impact_eur"] == 32021.25
    assert "disclaimer" in data["economic_model"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_api_vertical_slice.py::test_api_business_impact_endpoint -v`  
Expected: FAIL with `404 Not Found`

- [ ] **Step 3: Implement endpoint in `src/api/routes.py`**

```python
@router.get("/incident/business-impact")
def get_business_impact(scenario: str = "BASE"):
    manager = get_lifecycle_manager()
    incident_resp = manager.get_incident_response()
    econ_engine = RailEconomicsEngine()
    scenario_cfg = econ_engine.get_scenario(scenario)
    impact = scenario_cfg.calculate_impact()
    return {
        "case_id": incident_resp.get("incident_id"),
        "asset_context": {
            "fleet_id": "METRO-LISBON-BLUE",
            "train_id": "TRAIN-302",
            "subsystem": "AIR_PRODUCTION_UNIT",
            "component_id": incident_resp.get("asset_id"),
        },
        "operational_window": incident_resp.get("lead_time"),
        "economic_model": {
            "scenario_name": scenario_cfg.scenario_name,
            "parameters": scenario_cfg.model_dump(),
            "calculated_impact": impact,
            "disclaimer": "Scenario model projection based on European rail operator benchmarks. Not historical realized cash.",
        },
        "recovery_verification": {
            "status": "VERIFIED" if manager.lifecycle_state == IncidentLifecycleState.RESOLVED else "PENDING",
            "consecutive_loaded_observations": manager.recovery_verifier.consecutive_healthy_observations,
        }
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_api_vertical_slice.py::test_api_business_impact_endpoint -v`  
Expected: PASS

---

### Task 4: Full Regression Test & Verification

**Files:**
- Test: `tests/test_api_vertical_slice.py`
- Test: `tests/test_deterministic_replay.py`
- Test: `tests/test_value_model.py`

- [ ] **Step 1: Run complete test suite**

Run: `python -m pytest tests/ -v`  
Expected: All tests PASS.
