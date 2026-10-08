from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from src.domain.enums import OperatingRegime
from src.domain.models import TelemetryPoint


class RecoveryCriteria(BaseModel):
    """
    Domain acceptance policy defining the physical threshold criteria required
    to verify asset recovery post-maintenance on MetroPT-3 compressor APU-COMP-01.

    Criteria Rationale:
    - Target: 5 consecutive observations (50 seconds) in LOADED regime.
    - DV Pressure < 0.05 bar: confirms seated discharge valve without reverse leakage.
    - Oil Temperature < 67.0°C: confirms normal steady-state loaded thermal equilibrium.
    """
    target_healthy_observations: int = Field(default=5, ge=1)
    dv_pressure_max: float = Field(default=0.05, gt=0.0)
    oil_temp_max: float = Field(default=67.0, gt=0.0)
    required_regime: OperatingRegime = OperatingRegime.LOADED
    max_observation_gap_seconds: float = Field(default=30.0, gt=0.0)

    # Internal-only legacy alias
    @property
    def target_healthy_windows(self) -> int:
        return self.target_healthy_observations


class RecoveryEvaluationResult(BaseModel):
    """
    Result of evaluating a single telemetry observation against the recovery criteria.
    """
    is_applicable_regime: bool
    is_observation_healthy: bool
    consecutive_healthy_observations: int
    target_healthy_observations: int
    is_verified: bool
    reason: str

    # Internal-only legacy aliases
    @property
    def is_window_healthy(self) -> bool:
        return self.is_observation_healthy

    @property
    def consecutive_healthy_windows(self) -> int:
        return self.consecutive_healthy_observations

    @property
    def target_healthy_windows(self) -> int:
        return self.target_healthy_observations


class RecoveryVerifier:
    """
    Evaluator that tracks consecutive healthy telemetry observations in the target
    operating regime (LOADED) against physical recovery acceptance criteria.

    Invariant:
    - Only observations in `criteria.required_regime` (default LOADED) increment or reset the observation counter.
    - Observations outside the required regime suspend evaluation (neither incrementing nor resetting).
    - ANY observation in the required regime that violates thresholds immediately resets the counter to 0.
    - Once `target_healthy_observations` consecutive healthy observations are reached, recovery is verified.
    """

    def __init__(self, criteria: Optional[RecoveryCriteria] = None) -> None:
        self.criteria: RecoveryCriteria = criteria or RecoveryCriteria()
        self.consecutive_healthy_observations: int = 0
        self.is_verified: bool = False
        self.last_healthy_timestamp: Optional[datetime] = None

    # Internal-only legacy alias
    @property
    def consecutive_healthy_windows(self) -> int:
        return self.consecutive_healthy_observations

    @consecutive_healthy_windows.setter
    def consecutive_healthy_windows(self, val: int) -> None:
        self.consecutive_healthy_observations = val

    def reset(self) -> None:
        """Resets the consecutive healthy observation counter and verification status."""
        self.consecutive_healthy_observations = 0
        self.is_verified = False
        self.last_healthy_timestamp = None

    def evaluate(self, point: TelemetryPoint) -> RecoveryEvaluationResult:
        """
        Evaluates an incoming telemetry observation point against recovery criteria.
        """
        # Regime guard: evaluation only occurs in the required regime
        if point.regime != self.criteria.required_regime:
            return RecoveryEvaluationResult(
                is_applicable_regime=False,
                is_observation_healthy=False,
                consecutive_healthy_observations=self.consecutive_healthy_observations,
                target_healthy_observations=self.criteria.target_healthy_observations,
                is_verified=self.is_verified,
                reason=(
                    f"Regime '{point.regime}' does not match required regime "
                    f"'{self.criteria.required_regime}'; evaluation suspended."
                ),
            )

        # Check physical recovery thresholds
        pressure_ok = point.dv_pressure_bar < self.criteria.dv_pressure_max
        temp_ok = point.oil_temp_c < self.criteria.oil_temp_max
        is_healthy = pressure_ok and temp_ok

        if is_healthy:
            if self.last_healthy_timestamp is not None:
                gap = (point.timestamp - self.last_healthy_timestamp).total_seconds()
                if gap > self.criteria.max_observation_gap_seconds:
                    self.consecutive_healthy_observations = 1
                else:
                    self.consecutive_healthy_observations += 1
            else:
                self.consecutive_healthy_observations = 1

            self.last_healthy_timestamp = point.timestamp

            if self.consecutive_healthy_observations >= self.criteria.target_healthy_observations:
                self.is_verified = True
                reason = (
                    f"Recovery verified: {self.consecutive_healthy_observations}/"
                    f"{self.criteria.target_healthy_observations} consecutive healthy observations achieved."
                )
            else:
                reason = (
                    f"Healthy observation {self.consecutive_healthy_observations}/"
                    f"{self.criteria.target_healthy_observations} in regime {self.criteria.required_regime}."
                )
        else:
            # Immediate reset on any breach in required regime
            self.consecutive_healthy_observations = 0
            self.is_verified = False
            self.last_healthy_timestamp = None
            violations = []
            if not pressure_ok:
                violations.append(
                    f"dv_pressure={point.dv_pressure_bar:.4f} >= max {self.criteria.dv_pressure_max}"
                )
            if not temp_ok:
                violations.append(
                    f"oil_temp={point.oil_temp_c:.1f} >= max {self.criteria.oil_temp_max}"
                )
            reason = (
                f"Recovery criteria breached ({', '.join(violations)}). "
                f"Consecutive healthy observations reset to 0."
            )

        return RecoveryEvaluationResult(
            is_applicable_regime=True,
            is_observation_healthy=is_healthy,
            consecutive_healthy_observations=self.consecutive_healthy_observations,
            target_healthy_observations=self.criteria.target_healthy_observations,
            is_verified=self.is_verified,
            reason=reason,
        )
