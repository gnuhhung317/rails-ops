import pytest
from src.domain.registry import AssetRegistry


def test_fleet_hierarchy_is_explicitly_labeled_as_illustrative_context():
    registry = AssetRegistry.get_default()
    fleet = registry.get_fleet("FLEET-METRO-01")
    assert fleet is not None
    # Must explicitly state illustrative context
    assert getattr(fleet, "is_illustrative_context", False) is True

    train = registry.get_train("TRAIN-302")
    assert train is not None
    assert getattr(train, "is_illustrative_context", False) is True


def test_validation_reference_separates_dataset_ground_truth_from_computed_metrics():
    registry = AssetRegistry.get_default()
    ref = registry.get_validation_reference("SCENARIO-FAIL-03")
    assert ref is not None
    # Ground truth failure report vs computed lead time
    assert ref.reported_failure_mode == "Air leak in Air Production Unit"
    assert "computed_by_compressorguard" in ref.model_fields or hasattr(ref, "confirmed_intervention_window_minutes")
