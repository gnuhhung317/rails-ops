# CompressorGuard — Detection Decision Matrix Specification

> **Specification Authority:** This document defines the exact pure deterministic evaluation logic for `DecisionEngine.evaluate(evidence_state: EvidenceState) -> Decision`.

---

## 1. Matrix Table (1:1 Code Specification)

| Inputs (Signals & Operational Confidence) | Target Asset Health | Incident Action | Target Operational Confidence | UI Action / Representation |
| :--- | :--- | :--- | :--- | :--- |
| All signals `NORMAL` / `NONE` | `HEALTHY` | `NONE` | `NONE` | Fleet normal |
| 1 Signal `TRIGGERED` (Persistence = `UNCONFIRMED`) | `DEGRADING` | `NONE` | `LOW` | Yellow badge: "Early Warning Excursion" |
| 2+ Signals `TRIGGERED` (Persistence = `CONFIRMED`) | `DEGRADING` | `NONE` | `MEDIUM` | Yellow status: "Tracking Degradation" |
| Pressure + Thermal `TRIGGERED` (Persistence = `CONFIRMED`) | `CRITICAL` | `CREATE` | `MEDIUM` | Red alert: **Incident Created** (`APU-INC-20200605-01`) |
| Pressure + Thermal `TRIGGERED` + ML `CORROBORATED` | `CRITICAL` | `UPDATE_INVESTIGATING` | **`HIGH`** | Red alert: **Strong Evidence Pack Assembled**; Safe Mode Recommended |
| `LPS_ALERT` Signal `TRIGGERED` (Line Pressure < 7 bar) | `CRITICAL` | `UPDATE_INVESTIGATING` | **`CRITICAL_REACTIVE`** | Flashing alert: "Reactive Baseline Alert Active" |
| Operator executes Safe Mode | `RECOVERING` | `EXECUTE_MITIGATION` | `PENDING_VERIFICATION` | Amber status: "Executing Safe Mode Switch" |
| Scenario Recovery Criteria Met (5 cycles) | `HEALTHY` | `RESOLVE` | **`HIGH_VERIFIED`** | Green checkmark: **Incident Resolved & Verified** |

---

## 2. Invariants & Rules

1. **Decoupled Input:** `DecisionEngine` evaluates `EvidenceState` ONLY. It never accesses raw telemetry arrays or database instances.
2. **Determinism:** `evaluate(evidence_state)` must produce identical outputs for identical `EvidenceState` inputs.
3. **Operational Confidence Progression:**
   - `NONE` $\rightarrow$ `LOW` (Single unconfirmed excursion)
   - `LOW` $\rightarrow$ `MEDIUM` (Multiple signals / confirmed persistence)
   - `MEDIUM` $\rightarrow$ `HIGH` (Physical signals + ML corroboration)
   - `HIGH` $\rightarrow$ `CRITICAL_REACTIVE` (LPS reactive threshold hit)
   - `MITIGATING` $\rightarrow$ `HIGH_VERIFIED` (Telemetry recovery verified)
