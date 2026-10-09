import pytest
from src.engine.lifecycle import IncidentLifecycleManager
from src.domain.scenarios import FAILURE_3_SCENARIO


def test_evidence_payload_exposes_detector_provenance():
    manager = IncidentLifecycleManager(scenario=FAILURE_3_SCENARIO)
    manager.reset()
    manager.jump_to_milestone("onset_0950")

    payload = manager.get_evidence_payload()
    evidence_pack = payload["evidence_pack"]
    assert len(evidence_pack) > 0

    primary = next((e for e in evidence_pack if e["is_primary"]), None)
    assert primary is not None
    assert "provenance" in primary
    prov = primary["provenance"]
    assert "detector_class" in prov or "sensor" in prov or "source" in prov
    assert "regime" in prov
    assert prov["regime"] == "LOADED"


def test_independent_observation_timestamps_preserved():
    manager = IncidentLifecycleManager(scenario=FAILURE_3_SCENARIO)
    manager.reset()
    manager.jump_to_milestone("ml_corroborated_1015")

    payload = manager.get_evidence_payload()
    evidence_pack = payload["evidence_pack"]
    ml_sig = next((e for e in evidence_pack if "Isolation Forest" in e["signal_name"]), None)
    assert ml_sig is not None
    assert "provenance" in ml_sig
    assert ml_sig["provenance"].get("event_time") is not None
    assert "10:15" in ml_sig["provenance"]["event_time"]
