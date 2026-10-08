from datetime import datetime
import numpy as np
import pytest
from src.domain.enums import OperatingRegime
from src.domain.models import TelemetryPoint
from src.engine.detectors import (
    PressureAnomalyDetector,
    ThermalStressDetector,
    TemporalPersistenceTracker,
    IsolationForestDetector,
)

def test_detector_provenance_information():
    # 1. Pressure Anomaly Detector Provenance
    p_det = PressureAnomalyDetector()
    pt_loaded = TelemetryPoint(
        asset_id="APU-COMP-01",
        timestamp=datetime(2020, 6, 5, 9, 50, 0),
        tp2_bar=0.0, tp3_bar=0.0, h1_bar=0.0, dv_pressure_bar=2.18,
        reservoirs_bar=8.0, oil_temp_c=60.0, motor_current_a=6.5,
        comp_val=0.0, dv_electric=1.0, towers_val=0.0, mpg_val=0.0,
        lps_active=0.0, pressure_switch=0.0, oil_level_low=0.0,
        caudal_impulses=0.0, regime=OperatingRegime.LOADED
    )
    res_p = p_det.detect([pt_loaded])
    assert "detector_class" in res_p.provenance
    assert res_p.provenance["detector_class"] == "PressureAnomalyDetector"
    assert "method" in res_p.provenance

    # 2. Thermal Stress Detector Provenance
    t_det = ThermalStressDetector()
    pt_thermal = pt_loaded.model_copy(update={"oil_temp_c": 75.0})
    res_t = t_det.detect([pt_thermal])
    assert "detector_class" in res_t.provenance
    assert res_t.provenance["detector_class"] == "ThermalStressDetector"

    # 3. Isolation Forest Provenance with 5 features
    if_det = IsolationForestDetector()
    # Dummy fit on 5 features
    X_train = np.zeros((10, 5))
    if_det.fit_baseline(X_train)
    res_if = if_det.detect([pt_loaded])
    if res_if.status.value != "NORMAL":
        assert res_if.provenance["feature_count"] == 5
        assert res_if.provenance["feature_names"] == ["DV_pressure", "H1", "Oil_temperature", "Motor_current", "TP3"]
        assert res_if.provenance["role"] == "Independent Corroboration"
