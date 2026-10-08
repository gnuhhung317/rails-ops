from datetime import datetime
import pytest
from src.domain.enums import IncidentLifecycleState
from src.engine.lifecycle import IncidentLifecycleManager

def test_case_event_timeline_ledger_recording():
    manager = IncidentLifecycleManager()
    manager.reset()
    
    # 1. Pre-onset has empty or baseline ledger
    events = manager.get_case_events()
    assert isinstance(events, list)
    
    # 2. Seek to confirmed degradation
    manager.jump_to_milestone("onset_0950")
    events = manager.get_case_events()
    detection_evt = next((e for e in events if e["event_type"] == "DETECTION"), None)
    assert detection_evt is not None
    assert "Confirmed degradation detected" in detection_evt["title"]
    assert detection_evt["phase"] == "DETECTED"

    # 3. Seek to ML corroboration
    manager.jump_to_milestone("ml_corroborated_1015")
    events = manager.get_case_events()
    corr_evt = next((e for e in events if e["event_type"] == "CORROBORATION"), None)
    assert corr_evt is not None
    assert "Isolation Forest" in corr_evt["title"]
    assert corr_evt["phase"] == "INVESTIGATING"

    # 4. Trigger Safe Mode action
    manager.trigger_safe_mode()
    events = manager.get_case_events()
    act_evt = next((e for e in events if e["event_type"] == "ACTION"), None)
    assert act_evt is not None
    assert "Safe Mode" in act_evt["title"]

def test_case_closure_requires_verified_recovery():
    manager = IncidentLifecycleManager()
    manager.reset()
    manager.jump_to_milestone("onset_0950")
    
    # Cannot close case before recovery verified
    with pytest.raises(ValueError, match="Recovery not verified"):
        manager.close_case(operator_id="DISPATCHER-0941")

    # Fast forward to post-maintenance recovery verified
    manager.jump_to_milestone("post_maintenance_1605")
    # Tick until recovery verified (up to 50 ticks)
    ticks = 0
    while ticks < 50 and not manager.recovery_verifier.is_verified:
        manager.tick()
        ticks += 1
        
    assert manager.recovery_verifier.is_verified is True
    # Now close case succeeds
    result = manager.close_case(operator_id="DISPATCHER-0941", notes="Depot maintenance complete.")
    assert result["status"] == "CASE_CLOSED"
    assert manager.lifecycle_state == IncidentLifecycleState.RESOLVED
