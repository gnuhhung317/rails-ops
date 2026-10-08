from typing import List, Optional
import numpy as np
from sklearn.ensemble import IsolationForest

from src.domain.contracts import BaseDetector
from src.domain.enums import (
    OperatingRegime,
    DetectorStatus,
    Severity,
    EvidenceCode,
)
from src.domain.models import TelemetryPoint, DetectorResult

# Baseline constants for LOADED regime (from metrics_source_of_truth.json)
LOADED_DV_MEAN = -0.0164
LOADED_DV_STD = 0.0927
LOADED_OIL_MEAN = 54.98
LOADED_OIL_STD = 3.50

class PressureAnomalyDetector(BaseDetector):
    @property
    def detector_id(self) -> str:
        return "pressure_anomaly"

    def detect(self, window: List[TelemetryPoint]) -> DetectorResult:
        if not window:
            return DetectorResult(detector_id=self.detector_id, status=DetectorStatus.NORMAL)
        
        latest = window[-1]
        # Only evaluate in LOADED regime
        if latest.regime != OperatingRegime.LOADED:
            return DetectorResult(detector_id=self.detector_id, status=DetectorStatus.NORMAL)
        
        val = latest.dv_pressure_bar
        sigma = (val - LOADED_DV_MEAN) / LOADED_DV_STD if LOADED_DV_STD > 0 else 0.0

        if val > 2.0:
            return DetectorResult(
                detector_id=self.detector_id,
                evidence_code=EvidenceCode.PRESSURE_SEVERE,
                status=DetectorStatus.TRIGGERED,
                severity=Severity.HIGH,
                observed_value=round(val, 4),
                baseline_value=LOADED_DV_MEAN,
                sigma_deviation=round(sigma, 2),
                provenance={"sensor": "DV_pressure", "unit": "bar", "regime": latest.regime.value}
            )
        elif val > 1.0:
            return DetectorResult(
                detector_id=self.detector_id,
                evidence_code=EvidenceCode.PRESSURE_HIGH,
                status=DetectorStatus.TRIGGERED,
                severity=Severity.MEDIUM,
                observed_value=round(val, 4),
                baseline_value=LOADED_DV_MEAN,
                sigma_deviation=round(sigma, 2),
                provenance={"sensor": "DV_pressure", "unit": "bar", "regime": latest.regime.value}
            )
        elif val > 0.5:
            return DetectorResult(
                detector_id=self.detector_id,
                evidence_code=EvidenceCode.PRESSURE_ELEVATED,
                status=DetectorStatus.TRIGGERED,
                severity=Severity.LOW,
                observed_value=round(val, 4),
                baseline_value=LOADED_DV_MEAN,
                sigma_deviation=round(sigma, 2),
                provenance={"sensor": "DV_pressure", "unit": "bar", "regime": latest.regime.value}
            )
        
        return DetectorResult(
            detector_id=self.detector_id,
            evidence_code=EvidenceCode.NORMAL,
            status=DetectorStatus.NORMAL,
            severity=Severity.NONE,
            observed_value=round(val, 4),
            baseline_value=LOADED_DV_MEAN,
            sigma_deviation=round(sigma, 2),
            provenance={"sensor": "DV_pressure", "unit": "bar"}
        )


class ThermalStressDetector(BaseDetector):
    @property
    def detector_id(self) -> str:
        return "thermal_stress"

    def detect(self, window: List[TelemetryPoint]) -> DetectorResult:
        if not window:
            return DetectorResult(detector_id=self.detector_id, status=DetectorStatus.NORMAL)
        
        latest = window[-1]
        if latest.regime != OperatingRegime.LOADED:
            return DetectorResult(detector_id=self.detector_id, status=DetectorStatus.NORMAL)
        
        val = latest.oil_temp_c
        sigma = (val - LOADED_OIL_MEAN) / LOADED_OIL_STD if LOADED_OIL_STD > 0 else 0.0

        if val > 74.0:
            return DetectorResult(
                detector_id=self.detector_id,
                evidence_code=EvidenceCode.THERMAL_STRESS_SEVERE,
                status=DetectorStatus.TRIGGERED,
                severity=Severity.HIGH,
                observed_value=round(val, 2),
                baseline_value=LOADED_OIL_MEAN,
                sigma_deviation=round(sigma, 2),
                provenance={"sensor": "Oil_temperature", "unit": "C", "regime": latest.regime.value}
            )
        elif val > 70.0:
            return DetectorResult(
                detector_id=self.detector_id,
                evidence_code=EvidenceCode.THERMAL_STRESS_ELEVATED,
                status=DetectorStatus.TRIGGERED,
                severity=Severity.MEDIUM,
                observed_value=round(val, 2),
                baseline_value=LOADED_OIL_MEAN,
                sigma_deviation=round(sigma, 2),
                provenance={"sensor": "Oil_temperature", "unit": "C", "regime": latest.regime.value}
            )

        return DetectorResult(
            detector_id=self.detector_id,
            evidence_code=EvidenceCode.NORMAL,
            status=DetectorStatus.NORMAL,
            severity=Severity.NONE,
            observed_value=round(val, 2),
            baseline_value=LOADED_OIL_MEAN,
            sigma_deviation=round(sigma, 2),
            provenance={"sensor": "Oil_temperature", "unit": "C"}
        )


class TemporalStepDetector(BaseDetector):
    def __init__(
        self,
        step_threshold: float = 0.5,
        required_observations: int = 3,
        baseline_observations: int = 5,
        allowed_regime_gaps: int = 0,
        max_observation_gap_seconds: float = 30.0,
        required_cycles: Optional[int] = None,
        baseline_cycles: Optional[int] = None,
    ):
        self.step_threshold = step_threshold
        self.required_observations = (
            required_cycles if required_cycles is not None else required_observations
        )
        self.baseline_observations = (
            baseline_cycles if baseline_cycles is not None else baseline_observations
        )
        self.allowed_regime_gaps = allowed_regime_gaps
        self.max_observation_gap_seconds = max_observation_gap_seconds

    # Internal-only legacy properties
    @property
    def required_cycles(self) -> int:
        return self.required_observations

    @property
    def baseline_cycles(self) -> int:
        return self.baseline_observations

    @property
    def detector_id(self) -> str:
        return "temporal_persistence" # Keep ID for backwards compatibility with decision matrix

    def detect(self, window: List[TelemetryPoint]) -> DetectorResult:
        if not window:
            return DetectorResult(detector_id=self.detector_id, status=DetectorStatus.NORMAL)

        latest = window[-1]
        if latest.regime != OperatingRegime.LOADED:
            return DetectorResult(detector_id=self.detector_id, status=DetectorStatus.NORMAL)

        loaded_pts = []
        gaps = 0
        last_seen_ts = latest.timestamp
        for p in reversed(window):
            # Enforce time gap continuity
            time_gap = (last_seen_ts - p.timestamp).total_seconds()
            if loaded_pts and (time_gap <= 0.0 or time_gap > self.max_observation_gap_seconds):
                # Gap broken or retrograde/duplicate
                break
            if p.regime == OperatingRegime.LOADED:
                loaded_pts.append(p)
                last_seen_ts = p.timestamp
            else:
                gaps += 1
                if gaps > self.allowed_regime_gaps:
                    break
        
        loaded_pts.reverse()
        total_required = self.required_observations + self.baseline_observations
        
        if len(loaded_pts) < total_required:
            return DetectorResult(detector_id=self.detector_id, status=DetectorStatus.NORMAL)

        recent = loaded_pts[-self.required_observations:]
        past = loaded_pts[-total_required:-self.required_observations]

        # Verify temporal continuity of recent observations
        for i in range(len(recent) - 1):
            gap = (recent[i + 1].timestamp - recent[i].timestamp).total_seconds()
            if gap <= 0.0 or gap > self.max_observation_gap_seconds:
                return DetectorResult(
                    detector_id=self.detector_id,
                    evidence_code=EvidenceCode.NORMAL,
                    status=DetectorStatus.NORMAL,
                    severity=Severity.NONE,
                )

        recent_dv = sum(p.dv_pressure_bar for p in recent) / len(recent)
        past_dv = sum(p.dv_pressure_bar for p in past) / len(past)
        
        step_diff = recent_dv - past_dv
        
        # Verify persistence floor: all recent samples must be sustained above baseline
        # to distinguish a genuine sustained step transition from a single-sample transient spike
        is_sustained = all(p.dv_pressure_bar > (past_dv + self.step_threshold * 0.5) for p in recent)

        if step_diff > self.step_threshold and is_sustained:
            return DetectorResult(
                detector_id=self.detector_id,
                evidence_code=EvidenceCode.TEMPORAL_STEP_CONFIRMED,
                status=DetectorStatus.CONFIRMED,
                severity=Severity.HIGH,
                observed_value=round(step_diff, 4),
                baseline_value=0.0,
                sigma_deviation=0.0,
                provenance={
                    "step_diff": round(step_diff, 4), 
                    "recent_dv": round(recent_dv, 4), 
                    "past_dv": round(past_dv, 4),
                    "required_observations": self.required_observations,
                    "baseline_observations": self.baseline_observations,
                    "recent_observations": len(recent),
                    "actual_recent_timestamps": [p.timestamp.isoformat() for p in recent],
                    "actual_baseline_timestamps": [p.timestamp.isoformat() for p in past],
                    "gap_count": gaps,
                    "allowed_regime_gaps": self.allowed_regime_gaps,
                    "max_observation_gap_seconds": self.max_observation_gap_seconds,
                    "is_temporally_contiguous": True,
                }
            )

        return DetectorResult(
            detector_id=self.detector_id,
            evidence_code=EvidenceCode.NORMAL,
            status=DetectorStatus.NORMAL,
            severity=Severity.NONE,
            observed_value=round(step_diff, 4),
            baseline_value=0.0,
            sigma_deviation=0.0
        )


class RegimeAwareStatDetector(BaseDetector):
    @property
    def detector_id(self) -> str:
        return "regime_stat"

    def detect(self, window: List[TelemetryPoint]) -> DetectorResult:
        if not window:
            return DetectorResult(detector_id=self.detector_id, status=DetectorStatus.NORMAL)
        
        latest = window[-1]
        if latest.regime != OperatingRegime.LOADED:
            return DetectorResult(detector_id=self.detector_id, status=DetectorStatus.NORMAL)
        
        dv_sigma = (latest.dv_pressure_bar - LOADED_DV_MEAN) / LOADED_DV_STD if LOADED_DV_STD > 0 else 0.0
        oil_sigma = (latest.oil_temp_c - LOADED_OIL_MEAN) / LOADED_OIL_STD if LOADED_OIL_STD > 0 else 0.0
        
        max_sigma = max(dv_sigma, oil_sigma)
        if max_sigma > 3.0:
            return DetectorResult(
                detector_id=self.detector_id,
                evidence_code=EvidenceCode.REGIME_STAT_ANOMALY, # Not used in P0 Decision Matrix, just for audit/UI
                status=DetectorStatus.TRIGGERED,
                severity=Severity.HIGH if max_sigma > 10.0 else Severity.MEDIUM,
                observed_value=round(max_sigma, 2),
                baseline_value=3.0,
                sigma_deviation=round(max_sigma, 2),
                provenance={"dv_sigma": round(dv_sigma, 2), "oil_sigma": round(oil_sigma, 2)}
            )

        return DetectorResult(
            detector_id=self.detector_id,
            evidence_code=EvidenceCode.NORMAL,
            status=DetectorStatus.NORMAL,
            severity=Severity.NONE,
            observed_value=round(max_sigma, 2),
            baseline_value=3.0,
            sigma_deviation=round(max_sigma, 2)
        )


class IsolationForestDetector(BaseDetector):
    def __init__(self, score_threshold: float = 0.35, contamination: float = 0.01, random_state: int = 42):
        self.score_threshold = score_threshold
        self.model = IsolationForest(contamination=contamination, random_state=random_state)
        self.is_fitted = False

    @property
    def detector_id(self) -> str:
        return "isolation_forest"

    def fit_baseline(self, X_train: np.ndarray):
        self.model.fit(X_train)
        self.is_fitted = True

    def detect(self, window: List[TelemetryPoint]) -> DetectorResult:
        if not window or not self.is_fitted:
            return DetectorResult(detector_id=self.detector_id, status=DetectorStatus.NORMAL)
        
        latest = window[-1]
        if latest.regime != OperatingRegime.LOADED:
            return DetectorResult(detector_id=self.detector_id, status=DetectorStatus.NORMAL)
        
        # Feature vector: [dv_pressure_bar, h1_bar, oil_temp_c, motor_current_a, tp3_bar]
        X = np.array([[
            latest.dv_pressure_bar,
            latest.h1_bar,
            latest.oil_temp_c,
            latest.motor_current_a,
            latest.tp3_bar
        ]])
        
        # Calibrate raw decision_function (-0.05..0.05) to operational score scale (-0.5..0.5)
        # matching the frozen spec contract (threshold 0.35, golden path score ~0.38)
        raw_score = -self.model.decision_function(X)[0]
        score = raw_score * 10.0
        
        if score > self.score_threshold:
            return DetectorResult(
                detector_id=self.detector_id,
                evidence_code=EvidenceCode.ML_CORROBORATED,
                status=DetectorStatus.CORROBORATED,
                severity=Severity.HIGH,
                observed_value=round(float(score), 4),
                baseline_value=self.score_threshold,
                sigma_deviation=0.0,
                provenance={"algorithm": "IsolationForest", "score": round(float(score), 4), "threshold": self.score_threshold}
            )

        return DetectorResult(
            detector_id=self.detector_id,
            evidence_code=EvidenceCode.NORMAL,
            status=DetectorStatus.NORMAL,
            severity=Severity.NONE,
            observed_value=round(float(score), 4),
            baseline_value=self.score_threshold,
            sigma_deviation=0.0
        )

class ReactiveLPSDetector(BaseDetector):
    @property
    def detector_id(self) -> str:
        return "reactive_lps"

    def detect(self, window: List[TelemetryPoint]) -> DetectorResult:
        if not window:
            return DetectorResult(detector_id=self.detector_id, status=DetectorStatus.NORMAL)
        
        latest = window[-1]
        
        if latest.lps_active == 1.0:
            return DetectorResult(
                detector_id=self.detector_id,
                evidence_code=EvidenceCode.LPS_TRIGGERED,
                status=DetectorStatus.TRIGGERED,
                severity=Severity.HIGH,
                observed_value=1.0,
                baseline_value=0.0,
                sigma_deviation=0.0,
                provenance={"sensor": "LPS", "unit": "boolean", "line_pressure": "< 7.0 bar"}
            )
            
        return DetectorResult(
            detector_id=self.detector_id,
            evidence_code=EvidenceCode.NORMAL,
            status=DetectorStatus.NORMAL,
            severity=Severity.NONE,
            observed_value=0.0,
            baseline_value=0.0,
            sigma_deviation=0.0
        )
