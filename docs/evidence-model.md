# CompressorGuard — Evidence Model & Schema Specification

## 1. Overview
The Evidence Model defines how individual detector signals are encapsulated into immutable evidence objects and fused into an `EvidenceState`.

---

## 2. Pydantic Schemas & JSON Examples

### 2.1 `DetectorResult` Schema
```json
{
  "detector_id": "pressure_anomaly",
  "status": "TRIGGERED",
  "severity": "HIGH",
  "observed_value": 2.1856,
  "baseline_value": -0.0164,
  "sigma_deviation": 23.75,
  "provenance": {
    "sensor": "DV_pressure",
    "unit": "bar",
    "regime": "LOADED",
    "timestamp": "2020-06-05T09:50:00Z"
  }
}
```

### 2.2 `EvidenceState` Schema
```json
{
  "asset_id": "APU-COMP-01",
  "timestamp": "2020-06-05T10:15:00Z",
  "regime": "LOADED",
  "signals": [
    {
      "detector_id": "pressure_anomaly",
      "status": "TRIGGERED",
      "severity": "HIGH",
      "observed_value": 2.1856,
      "baseline_value": -0.0164,
      "sigma_deviation": 23.75,
      "provenance": {"sensor": "DV_pressure"}
    },
    {
      "detector_id": "thermal_stress",
      "status": "TRIGGERED",
      "severity": "MEDIUM",
      "observed_value": 74.97,
      "baseline_value": 54.98,
      "sigma_deviation": 5.71,
      "provenance": {"sensor": "Oil_temperature"}
    },
    {
      "detector_id": "temporal_persistence",
      "status": "CONFIRMED",
      "severity": "HIGH",
      "observed_value": 5.0,
      "baseline_value": 3.0,
      "sigma_deviation": 0.0,
      "provenance": {"window_size": 5}
    },
    {
      "detector_id": "multivariate_ml",
      "status": "CORROBORATED",
      "severity": "HIGH",
      "observed_value": 0.38,
      "baseline_value": 0.1,
      "sigma_deviation": 2.8,
      "provenance": {"model": "IsolationForest"}
    }
  ],
  "confidence": "HIGH"
}
```
