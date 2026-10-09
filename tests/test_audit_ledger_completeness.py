import pytest
from src.engine.lifecycle import IncidentLifecycleManager
from src.storage.repository import CompressorGuardRepository
from src.domain.enums import CaseEventType
from src.domain.scenarios import FAILURE_3_SCENARIO
from src.api.app import get_default_manager


def test_audit_ledger_records_observation_and_decision_events():
    repo = CompressorGuardRepository()
    manager = IncidentLifecycleManager(scenario=FAILURE_3_SCENARIO, repository=repo)
    manager.reset()

    # 1. Early excursion creates OBSERVATION event
    manager.jump_to_milestone("early_excursion_0033")
    events = manager.get_case_events()
    event_types = [e["event_type"] for e in events]
    assert CaseEventType.OBSERVATION.value in event_types

    # 2. Confirmed onset creates CASE_CONFIRMED (or DETECTION) and DECISION events
    manager.jump_to_milestone("onset_0950")
    events = manager.get_case_events()
    event_types = [e["event_type"] for e in events]
    assert any(t in event_types for t in ["CASE_CONFIRMED", "DETECTION"])
    assert "DECISION" in event_types


def test_default_manager_has_repository_injected():
    manager = get_default_manager()
    assert manager.repository is not None
    assert isinstance(manager.repository, CompressorGuardRepository)
