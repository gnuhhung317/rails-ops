# CompressorGuard — Product Definition

> **Category:** Closed-loop Incident Intelligence System for Physical Assets  
> **Core Promise:** **Detect earlier → Prove why → Act safely → Verify recovery.**

---

## 1. Vision & Core Positioning
CompressorGuard continuous monitors telemetry from critical industrial compressors (APU). Rather than acting as a static dashboard or producing standalone anomaly scores, CompressorGuard identifies evolving degradation patterns early, fuses multi-sensor evidence into actionable operational confidence, assists operators with dataset-driven reversible mitigation (Safe Mode), and verifies natural physical recovery from real telemetry.

---

## 2. Official Product Claims & Metrics

### 2.1 The Official Product Claim
> **“CompressorGuard identifies an evolving degradation pattern in MetroPT-3 earlier than a conventional reactive alert, explains the evidence behind the decision, and verifies recovery after an intervention.”**

### 2.2 Empirical Lead Time Metrics (MetroPT-3 Source of Truth)
* **Confirmed Degradation Lead Time:** **33 hours 52 minutes earlier** than conventional reactive alert (`LPS = 1`).
  - *Confirmed Degradation Timestamp:* `2020-06-05 09:50:00`
  - *Reactive LPS Alert Timestamp:* `2020-06-06 19:42:19`
* **First Abnormal Excursion:** **~67 hours 09 minutes earlier** than `LPS = 1`.
  - *Early Anomaly Excursion Timestamp:* `2020-06-04 00:33:07`
* **Primary Leak Signature:** `dv_pressure_bar` observed at **2.1856 bar** (LOADED regime baseline $-0.0164 \pm 0.0927$ bar) $\rightarrow$ **$+23.75\sigma$ deviation**.
* **Thermal Stress Corroboration:** `oil_temp_c` observed at **74.97 °C** (LOADED regime baseline $54.98 \pm 3.50$ °C) $\rightarrow$ **$+5.71\sigma$ thermal drift**.

---

## 3. User Persona & Operational Job-to-be-Done

* **User Persona:** Fleet & Maintenance Operations Specialist monitoring compressor/APU systems on metro trains.
* **Problem Statement:** Compressor failures progress silently through subtle cross-sensor changes. Reactive alarms fire too late (when system pressure has already collapsed), requiring emergency removal of trains from service.
* **Job-to-be-Done:** Detect degradation early $\rightarrow$ Review temporal evidence $\rightarrow$ Execute safe mitigation $\rightarrow$ Verify telemetry stabilization.

---

## 4. Scope Boundaries & Non-Goals

### 4.1 In Scope (P0)
- Local MetroPT-3 real-time stream replay.
- Operating-condition-aware baseline calculations (LOADED regime).
- Multi-detector engine & Evidence Fusion.
- Pure deterministic Decision Engine.
- Dataset-driven intervention simulation (Safe Mode stream offset branch).
- Telemetry-based recovery verification.
- Datadog APM, Metrics, & Logging integration.

### 4.2 Non-Goals (Out of Scope)
- Autonomous direct physical control of train hardware.
- Certified Remaining Useful Life (RUL) estimation.
- Microservice distributed architecture (Single backend deployable for hackathon reliability).
- Pretending to monitor synthetic fake multi-asset fleets.
