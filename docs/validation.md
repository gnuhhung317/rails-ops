# CompressorGuard — Empirical Dataset Validation Report

## 1. Dataset Source of Truth Statistics

Derived directly from `MetroPT3(AirCompressor).csv` (1,516,948 samples):

```json
{
  "dataset": {
    "total_rows": 1516948,
    "total_csv_columns": 17,
    "median_interval_sec": 10.0,
    "temporal_gaps_gt_30s": 331,
    "duplicate_timestamps": 0
  },
  "february_healthy_loaded_baseline": {
    "dv_pressure_mean_bar": -0.0164,
    "dv_pressure_std_bar": 0.0927,
    "oil_temperature_mean_c": 54.98,
    "oil_temperature_std_c": 3.5
  },
  "failure_3_golden_path_metrics": {
    "observed_dv_pressure_bar": 2.1627,
    "dv_pressure_sigma_deviation": 23.52,
    "observed_oil_temperature_c": 73.87,
    "oil_temperature_sigma_deviation": 5.39,
    "lead_times": {
      "confirmed_degradation_to_lps_str": "33h52m",
      "early_anomaly_to_lps_str": "67h09m"
    }
  }
}
```

---

## 2. Multi-Scenario Validation Matrix Results

| Failure Window | Primary Role | Pressure Detector | Thermal Detector | Persistence | ML Corroboration | Outcome |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Failure #3 (June 5–8)** | **Golden Path Demo** | ✓ | ✓ | ✓ | ✓ | **PASS (33h52m Lead Time)** |
| **Failure #1 (April 18)** | Platform Multi-Failure Test | ✓ | ✓ | ✓ | ✓ | **PASS (Acute Failure Detected)** |
| **Failure #4 (July 15)** | Thermal Overheat Test | ✓ | ✓ (89.05°C) | ✓ | ✓ | **PASS (Thermal Drift Detected)** |
| **February 2020** | Healthy False Positive Test | Normal | Normal | Normal | Normal | **PASS (0 False Incidents)** |
| **Failure #2 (May 29–30)** | Excluded | — | — | — | — | **Excluded (Report date mismatch)** |
