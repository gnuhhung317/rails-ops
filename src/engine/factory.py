"""
Factory module for instantiating and wiring CompressorGuard engine components.
Enforces clean dependency inversion by decoupling domain/engine layers
from test suites.
"""
from typing import Tuple, List

from src.domain.contracts import BaseDetector
from src.domain.enums import OperatingRegime
from src.engine.detectors import (
    PressureAnomalyDetector,
    ThermalStressDetector,
    TemporalStepDetector,
    RegimeAwareStatDetector,
    IsolationForestDetector,
    ReactiveLPSDetector,
)
from src.engine.fusion import EvidenceFusionEngine
from src.engine.decision import DecisionEngine
from src.engine.replay import ReplayEngine, CSV_PATH, classify_regime


def setup_golden_path() -> Tuple[ReplayEngine, List[BaseDetector], EvidenceFusionEngine, DecisionEngine]:
    """Sets up and wires the golden path components for replay and detection."""
    replay = ReplayEngine(CSV_PATH)
    replay.load_data()

    # Fit Isolation Forest on Feb LOADED regime
    feb = replay.df[
        (replay.df["timestamp"] >= "2020-02-01") & (replay.df["timestamp"] < "2020-03-01")
    ].copy()
    feb["regime"] = feb.apply(
        lambda r: classify_regime(r["Motor_current"], r["COMP"], r["DV_eletric"]),
        axis=1,
    )
    feb_loaded = feb[feb["regime"] == OperatingRegime.LOADED]

    X_train = feb_loaded[
        ["DV_pressure", "H1", "Oil_temperature", "Motor_current", "TP3"]
    ].values

    if_detector = IsolationForestDetector(score_threshold=0.35)
    if_detector.fit_baseline(X_train)

    detectors: List[BaseDetector] = [
        PressureAnomalyDetector(),
        ThermalStressDetector(),
        TemporalStepDetector(
            step_threshold=0.5,
            required_cycles=3,
            baseline_cycles=5,
            allowed_regime_gaps=0,
        ),
        RegimeAwareStatDetector(),
        if_detector,
        ReactiveLPSDetector(),
    ]

    fusion = EvidenceFusionEngine()
    decision_engine = DecisionEngine()

    return replay, detectors, fusion, decision_engine
