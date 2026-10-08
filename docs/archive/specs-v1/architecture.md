# CompressorGuard — System Architecture & Layer Contracts

## 1. System Overview

CompressorGuard is structured into 4 decoupled execution layers to enforce the principle:  
**"Many signals. One decision. One incident story. Closed-loop recovery."**

```text
                 METROPT-3 TELEMETRY / REPLAY ENGINE
                                  │
                                  ▼
                         Telemetry Data Object
                                  │
                                  ▼
                     Operating Regime Classifier
                                  │
                                  ▼
                      Feature Extraction Engine
                                  │
      ┌───────────────────────────┼───────────────────────────┐
      ▼                           ▼                           ▼
Pressure Detector          Thermal Stress Detector    Persistence Detector
(DetectorResult A)          (DetectorResult B)         (DetectorResult C)
      │                           │                           │
      └───────────────────────────┼───────────────────────────┘
                                  ▼
                         Regime Stat Detector
                          (DetectorResult D)
                                  │
                                  ▼
                         Isolation Forest Scorer
                          (DetectorResult E)
                                  │
                                  ▼
                       EVIDENCE FUSION ENGINE
                                  │
                                  ▼
                            EvidenceState
                (Signals + Operational Confidence)
                                  │
                                  ▼
                           DECISION ENGINE
                     (Pure Deterministic Function)
                                  │
               ┌──────────────────┴──────────────────┐
               ▼                                     ▼
       Asset Health State                    Incident Action
     (HEALTHY/DEGRADING/                  (NONE/CREATE/INVESTIGATE/
     CRITICAL/RECOVERING)                  MITIGATE/VERIFY/RESOLVE)
```

---

## 2. Decoupled Layer Contracts

### 2.1 Detector Contract (`Detector` Interface)
Every detector must implement the standard contract:
```python
class BaseDetector(ABC):
    @abstractmethod
    def detect(self, window: TelemetryWindow) -> DetectorResult:
        pass
```
* **Input:** `TelemetryWindow` (sliding window of raw & derived telemetry points).
* **Output:** `DetectorResult` containing:
  - `detector_id`: string (e.g. `"pressure_anomaly"`, `"thermal_stress"`)
  - `status`: `DetectorStatus` (`NORMAL`, `TRIGGERED`, `CONFIRMED`, `CORROBORATED`)
  - `severity`: `Severity` (`NONE`, `LOW`, `MEDIUM`, `HIGH`)
  - `observed_value`: float
  - `baseline_value`: float
  - `sigma_deviation`: float
  - `provenance`: metadata dictionary (sensor name, window size, timestamps)

### 2.2 Evidence Fusion Contract (`EvidenceFusionEngine`)
* **Input:** List of `DetectorResult`s from all active detectors.
* **Output:** `EvidenceState` object containing:
  - `asset_id`: string
  - `timestamp`: string (ISO-8601)
  - `regime`: `OperatingRegime` (`OFF`, `STARTING`, `OFF_LOAD`, `LOADED`, `TRANSIENT`)
  - `signals`: list of active `DetectorResult`s
  - `confidence`: `OperationalConfidence` (`NONE`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL_REACTIVE`)
* **Constraint:** Fusion engine does NOT mutate asset state or create incidents. It evaluates evidence ONLY.

### 2.3 Decision Engine Contract (`DecisionEngine`)
* **Input:** `EvidenceState`
* **Output:** `Decision` containing:
  - `asset_health`: `AssetHealthState` (`HEALTHY`, `DEGRADING`, `CRITICAL`, `RECOVERING`)
  - `incident_action`: `IncidentAction` (`NONE`, `CREATE`, `UPDATE_INVESTIGATING`, `EXECUTE_MITIGATION`, `VERIFY_RECOVERY`, `RESOLVE`)
  - `operational_confidence`: `OperationalConfidence`
  - `ui_action`: string
  - `reason`: string
* **Constraint:** Pure deterministic function. No external IO, database calls, or side effects. `evaluate(evidence_state)` must produce identical decisions for identical inputs.
