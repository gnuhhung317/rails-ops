import pytest
from src.domain.registry import (
    AssetRegistry,
    FleetEntity,
    TrainEntity,
    SubsystemEntity,
    CompressorAssetEntity,
    ValidationReference,
)

def test_asset_hierarchy_resolution():
    registry = AssetRegistry.get_default()
    
    # 1. Verify 4-level hierarchy structure
    fleet = registry.get_fleet("FLEET-METRO-01")
    assert fleet is not None
    assert "RailOps VN" in fleet.name
    
    train = registry.get_train("TRAIN-302")
    assert train is not None
    assert train.fleet_id == "FLEET-METRO-01"
    assert train.model == "Nippon Sharyo Type 001 EMU"
    
    subsystem = registry.get_subsystem("SUB-APU-01")
    assert subsystem is not None
    assert subsystem.train_id == "TRAIN-302"
    assert subsystem.name == "Air Production Unit"
    
    asset = registry.get_asset("APU-COMP-01")
    assert asset is not None
    assert asset.subsystem_id == "SUB-APU-01"
    assert asset.criticality == "CRITICAL"
    assert asset.service_role == "Main Air Supply"

def test_validation_reference_ground_truth_separation():
    registry = AssetRegistry.get_default()
    ref = registry.get_validation_reference("SCENARIO-FAIL-03")
    
    assert ref is not None
    assert ref.scenario_id == "SCENARIO-FAIL-03"
    assert ref.scenario_name == "Failure #3 — Air Leak / High Stress"
    assert ref.dataset_source == "MetroPT-3 Historical Telemetry"
    assert ref.reported_failure_mode == "Air leak in Air Production Unit"
    assert ref.reported_failure_start == "2020-06-05T10:00:00Z"
    assert ref.conventional_lps_breach == "2020-06-06T19:42:19Z"
    # Ground truth is distinct from online detection
    assert ref.online_detector_confirmation == "2020-06-05T09:50:39Z"
