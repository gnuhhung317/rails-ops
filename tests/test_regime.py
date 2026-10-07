import pytest
from src.domain.enums import OperatingRegime
from src.engine.replay import classify_regime

def test_classify_regime_off():
    # Motor current < 0.5 A -> OFF regardless of comp/dv_electric
    assert classify_regime(motor_current=0.0, comp=0.0, dv_electric=0.0) == OperatingRegime.OFF
    assert classify_regime(motor_current=0.49, comp=1.0, dv_electric=1.0) == OperatingRegime.OFF

def test_classify_regime_starting():
    # Motor current > 8.0 A -> STARTING
    assert classify_regime(motor_current=8.1, comp=0.0, dv_electric=1.0) == OperatingRegime.STARTING
    assert classify_regime(motor_current=9.5, comp=1.0, dv_electric=0.0) == OperatingRegime.STARTING

def test_classify_regime_off_load():
    # Running (0.5 <= motor_current <= 8.0), COMP == 1.0 and DV_electric == 0.0 -> OFF_LOAD
    assert classify_regime(motor_current=5.5, comp=1.0, dv_electric=0.0) == OperatingRegime.OFF_LOAD
    assert classify_regime(motor_current=2.0, comp=1.0, dv_electric=0.0) == OperatingRegime.OFF_LOAD

def test_classify_regime_loaded():
    # Running (0.5 <= motor_current <= 8.0), COMP == 0.0 or DV_electric == 1.0 -> LOADED
    assert classify_regime(motor_current=5.8, comp=0.0, dv_electric=1.0) == OperatingRegime.LOADED
    assert classify_regime(motor_current=6.0, comp=0.0, dv_electric=0.0) == OperatingRegime.LOADED
    assert classify_regime(motor_current=6.2, comp=1.0, dv_electric=1.0) == OperatingRegime.LOADED

def test_classify_regime_transient():
    # Any other combination when running -> TRANSIENT
    # (e.g. edge states not matching standard patterns)
    pass
