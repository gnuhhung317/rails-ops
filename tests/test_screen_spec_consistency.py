from pathlib import Path

def test_screen_specs_truthfulness_and_no_fake_live():
    screen_dir = Path("screen")
    s1 = (screen_dir / "01_OPERATIONS_NAV_AND_ASSET_OVERVIEW.md").read_text(encoding="utf-8")
    s3 = (screen_dir / "03_CASE_WORKSPACE_WHAT_CHANGED.md").read_text(encoding="utf-8")
    s4 = (screen_dir / "04_CASE_WORKSPACE_WHY_EVIDENCE.md").read_text(encoding="utf-8")
    s5 = (screen_dir / "05_CASE_WORKSPACE_WHAT_DID_WE_DO.md").read_text(encoding="utf-8")
    s7 = (screen_dir / "07_CASE_TIMELINE_HISTORY.md").read_text(encoding="utf-8")
    
    # 1. No fake [🔴 LIVE] in header, replaced by LIVE SIMULATION
    assert "[🔴 LIVE]" not in s1
    assert "LIVE SIMULATION" in s1 or "HISTORICAL REPLAY" in s1
    
    # 2. No fake 98% fleet health claim
    assert "FLEET HEALTH: 98%" not in s1
    
    # 3. Screen 04 specifies 5 features for IF, not 15 sensors
    assert (
        "5 features" in s4.lower()
        or "5 telemetry" in s4.lower()
        or "5 đặc trưng" in s4
        or "5-feature" in s4.lower()
    )
    
    # 4. Screen 05 documents ActionGuard
    assert "ActionGuard" in s5 or "ACTION GUARD" in s5 or "Action Guard" in s5
    
    # 5. Screen 07 documents Datadog ledger
    assert "CaseEvent" in s7 or "AUDIT LEDGER" in s7 or "Case Event" in s7 or "LEDGER" in s7
