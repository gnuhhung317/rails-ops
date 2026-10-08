from typing import Optional

from src.domain.contracts import BaseDecisionEngine
from src.domain.enums import (
    AssetHealthState,
    IncidentAction,
    IncidentLifecycleState,
    OperationalConfidence,
    EvidenceCode,
)
from src.domain.models import EvidenceState, Decision, IncidentContext

# Active states for autonomous engine decision evaluation.
# RESOLVED, FAILED, and ESCALATED are non-active states (handled by operators or terminal).
ACTIVE_INCIDENT_STATES: frozenset[IncidentLifecycleState] = frozenset({
    IncidentLifecycleState.DETECTED,
    IncidentLifecycleState.INVESTIGATING,
    IncidentLifecycleState.MITIGATING,
    IncidentLifecycleState.VERIFYING_RECOVERY,
})

class DecisionEngine(BaseDecisionEngine):
    def evaluate(
        self,
        evidence_state: EvidenceState,
        incident_context: Optional[IncidentContext] = None
    ) -> Decision:
        # Determine if an active incident exists in the current operational context
        has_active_incident = (
            incident_context is not None
            and incident_context.active_incident_id is not None
            and incident_context.lifecycle_state in ACTIVE_INCIDENT_STATES
        )

        # Extract semantic facts (evidence codes) from EvidenceState signals
        evidence_codes = {
            s.evidence_code.value if hasattr(s.evidence_code, "value") else str(s.evidence_code)
            for s in evidence_state.signals
        }

        # Check semantic facts according to the matrix
        has_lps = EvidenceCode.LPS_TRIGGERED.value in evidence_codes
        has_severe_pressure = EvidenceCode.PRESSURE_SEVERE.value in evidence_codes
        has_temporal_step = EvidenceCode.TEMPORAL_STEP_CONFIRMED.value in evidence_codes
        has_ml = EvidenceCode.ML_CORROBORATED.value in evidence_codes
        
        has_any_pressure = any(c.startswith("PRESSURE_") for c in evidence_codes)
        has_any_thermal = any(c.startswith("THERMAL_STRESS") for c in evidence_codes)
        has_severe_thermal = EvidenceCode.THERMAL_STRESS_SEVERE.value in evidence_codes
        active_signals_count = int(has_any_pressure) + int(has_any_thermal)

        confirmed_degradation = has_severe_pressure and has_any_thermal and has_temporal_step

        # Evaluate matrix from top severity and lifecycle priority down

        # 1. Reactive Baseline Alert (LPS=1 breached)
        if has_lps:
            action = IncidentAction.UPDATE_INVESTIGATING if has_active_incident else IncidentAction.CREATE
            return Decision(
                asset_health=AssetHealthState.CRITICAL,
                incident_action=action,
                operational_confidence=OperationalConfidence.CRITICAL_REACTIVE,
                ui_action="Reactive Baseline Alert Active",
                reason="Low Pressure Switch (LPS=1) reactive threshold breached. Line pressure < 7.0 bar.",
                evidence_state=evidence_state
            )

        # 2. Multivariate ML Corroboration (High Confidence Evidence Pack: Pressure > 2.0 + Oil > 74C + ML > 0.35)
        if has_severe_pressure and has_severe_thermal and has_ml:
            action = IncidentAction.UPDATE_INVESTIGATING if has_active_incident else IncidentAction.CREATE
            return Decision(
                asset_health=AssetHealthState.CRITICAL,
                incident_action=action,
                operational_confidence=OperationalConfidence.HIGH,
                ui_action="Strong Evidence Pack Assembled",
                reason="Multi-detector physical signals confirmed and corroborated by multivariate Isolation Forest. Safe Mode recommended.",
                evidence_state=evidence_state
            )

        # 3. Confirmed Degradation (Physical Step + Thermal Drift, or ongoing active severe state)
        if confirmed_degradation or (has_active_incident and has_severe_pressure and has_any_thermal):
            # If incident already created, maintain tracking without re-issuing CREATE
            action = IncidentAction.NONE if has_active_incident else IncidentAction.CREATE
            ui_label = "Tracking Degradation" if has_active_incident else "Incident Created"
            return Decision(
                asset_health=AssetHealthState.CRITICAL,
                incident_action=action,
                operational_confidence=OperationalConfidence.MEDIUM,
                ui_action=ui_label,
                reason="Confirmed severe step degradation in DV_pressure with thermal stress drift.",
                evidence_state=evidence_state
            )

        # 4. Multi-Anomaly Degradation with Temporal Step
        if active_signals_count >= 2 and has_temporal_step:
            return Decision(
                asset_health=AssetHealthState.DEGRADING,
                incident_action=IncidentAction.NONE,
                operational_confidence=OperationalConfidence.MEDIUM,
                ui_action="Tracking Degradation",
                reason="Multiple anomaly signals detected with ongoing persistence tracking.",
                evidence_state=evidence_state
            )

        # 5. Early Warning Excursion (Transient or Single Anomaly)
        if active_signals_count > 0 and not has_temporal_step:
            return Decision(
                asset_health=AssetHealthState.DEGRADING,
                incident_action=IncidentAction.NONE,
                operational_confidence=OperationalConfidence.LOW,
                ui_action="Early Warning Excursion",
                reason="Transient anomaly excursion(s) detected. Accumulating telemetry evidence.",
                evidence_state=evidence_state
            )

        # 6. Default Fallback (Healthy Fleet Baseline)
        return Decision(
            asset_health=AssetHealthState.HEALTHY,
            incident_action=IncidentAction.NONE,
            operational_confidence=OperationalConfidence.NONE,
            ui_action="Fleet Normal",
            reason="Baseline state.",
            evidence_state=evidence_state
        )
