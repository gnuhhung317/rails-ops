# CompressorGuard — Detection Engine & Detector Specifications

## 1. Overview of Detector Suite

The Detection Engine runs 5 independent detectors on incoming telemetry windows. Each detector evaluates a distinct physical or statistical aspect of the asset:

```text
Incoming Telemetry Window
           │
           ├─► 1. PressureAnomalyDetector   (Fast primary leak signal)
           ├─► 2. ThermalStressDetector     (Independent thermal corroboration)
           ├─► 3. TemporalPersistenceDetector (Filters out 10s transient noise)
           ├─► 4. RegimeAwareStatDetector   (Calculates sigma vs matching regime baseline)
           └─► 5. IsolationForestScorer     (Multivariate cross-sensor corroboration)
```

---

## 2. Individual Detector Specifications

### 2.1 Detector A — `PressureAnomalyDetector`
* **Target Metric:** `dv_pressure_bar`
* **Trigger Condition:** `dv_pressure_bar > 0.5 bar` (LOADED regime).
* **Role:** Fast physical detection of desiccant air dryer drain valve leakage.
* **Output Severity:** `LOW` if `dv_pressure` $\in (0.5, 1.0]$, `MEDIUM` if $\in (1.0, 2.0]$, `HIGH` if $> 2.0$ bar.

### 2.2 Detector B — `ThermalStressDetector`
* **Target Metric:** `oil_temp_c`
* **Trigger Condition:** `oil_temp_c > 70.0 °C` (LOADED regime).
* **Role:** Independent thermal corroboration resulting from compressor running continuous duty.
* **Output Severity:** `MEDIUM` if `oil_temp` $\in (70.0, 74.0]$, `HIGH` if $> 74.0$ °C.

### 2.3 Detector C — `TemporalPersistenceDetector`
* **Target Window:** Last $N=3$ consecutive telemetry cycles (30 seconds).
* **Trigger Condition:** `PressureAnomalyDetector` sustained `TRIGGERED` for $\ge 3$ consecutive cycles.
* **Role:** Distinguishes 10-second single-sample transient noise spikes from sustained physical step changes.
* **Status Output:** `CONFIRMED` when persistence threshold is met.

### 2.4 Detector D — `RegimeAwareStatDetector`
* **Target Metrics:** `dv_pressure_bar`, `oil_temp_c` vs `LOADED` baseline.
* **LOADED Baseline (Feb 2020):**
  - `dv_pressure`: $\mu = -0.0164$ bar, $\sigma = 0.0927$ bar
  - `oil_temp`: $\mu = 54.98$ °C, $\sigma = 3.50$ °C
* **Trigger Condition:** Telemetry $z$-score $> +3.0\sigma$ within matching operating regime.
* **Role:** Ensures deviations are calculated strictly against the matching operational state, eliminating false alarms from regime transitions.

### 2.5 Detector E — `IsolationForestScorer`
* **Features Used:** `[dv_pressure_bar, h1_bar, oil_temp_c, motor_current_a, tp3_bar]`
* **Model Training:** Trained on clean February 2020 LOADED telemetry (13,024 samples).
* **Trigger Condition:** Anomaly score $> 0.35$.
* **Role:** Provides multivariate cross-sensor corroboration. Does NOT overwrite deterministic rule detectors; raises Operational Confidence from `MEDIUM` to `HIGH`.

---

## 3. Operating Regime Classifier Specification

```python
def classify_regime(motor_current: float, comp: float, dv_electric: float) -> OperatingRegime:
    if motor_current < 0.5:
        return OperatingRegime.OFF
    elif motor_current > 8.0:
        return OperatingRegime.STARTING
    elif comp == 1.0 and dv_electric == 0.0:
        return OperatingRegime.OFF_LOAD
    elif comp == 0.0 or dv_electric == 1.0:
        return OperatingRegime.LOADED
    else:
        return OperatingRegime.TRANSIENT
```
