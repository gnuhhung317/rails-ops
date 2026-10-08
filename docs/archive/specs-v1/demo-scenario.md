# CompressorGuard — Demo Scenario Walkthrough (Failure #3 Golden Path)

## 1. Golden Path Storyline

```text
67h09m before reactive alert
        │
        ● Early pressure excursion (DV_pressure > 0.5 bar)
        │
33h52m  ● Confirmed severe step degradation (DV_pressure = 2.18 bar, +23.75σ)
        │
        ● Thermal stress drift (Oil_temperature = 74.97°C, +5.71σ)
        │
        ● Multivariate ML corroboration (Isolation Forest Score = 0.38)
        │
        ▼
        🔴 REACTIVE BASELINE ALERT (LPS = 1, Line Pressure < 7.0 bar)
        │
        │
        ● Operator executed Safe Mode (Dataset-driven stream branch switch)
        │
        ● Recovery evidence verified (DV_pressure = -0.016 bar, Oil_temp = 64.1°C)
        ▼
        ✅ INCIDENT RESOLVED & VERIFIED
```

---

## 2. Key Timeline Milestones

| Timeline Offset | Raw Timestamp | System Action / Event | Telemetry State | Asset Health | Operational Confidence |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **T-67h 09m** | `2020-06-04 00:33:07` | Early transient excursion detected | `DV_pressure = 0.52` bar | `DEGRADING` | `LOW` |
| **T-33h 52m** | `2020-06-05 09:50:00` | Step change & confirmed degradation | `DV_pressure = 2.18` bar | `CRITICAL` | `MEDIUM` |
| **T-33h 27m** | `2020-06-05 10:15:00` | ML corroborates multivariate pattern | `IF_score = 0.38` | `CRITICAL` | `HIGH` |
| **T-0h 00m** | `2020-06-06 19:42:19` | Reactive baseline alert fires | `LPS = 1`, `TP3 < 7` bar | `CRITICAL` | `CRITICAL_REACTIVE` |
| **Intervention** | User Click | Operator triggers Safe Mode | Branch switch executed | `RECOVERING` | `PENDING_VERIFICATION` |
| **Recovery** | `2020-06-08 16:05:00` | 5 cycles pass recovery criteria | `DV_pressure = -0.016` bar | `HEALTHY` | `HIGH_VERIFIED` |
