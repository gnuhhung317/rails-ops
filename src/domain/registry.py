from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class FleetEntity(BaseModel):
    fleet_id: str = "FLEET-METRO-01"
    name: str = "Metro Fleet (Linha Azul)"
    operator_name: str = "Metro do Porto / CP"
    depot_location: str = "Depot Oriente"
    train_ids: List[str] = Field(default_factory=lambda: ["TRAIN-302"])
    is_illustrative_context: bool = True
    context_note: str = "Illustrative operational hierarchy mapping for MetroPT-3 compressor telemetry."


class TrainEntity(BaseModel):
    train_id: str = "TRAIN-302"
    fleet_id: str = "FLEET-METRO-01"
    model: str = "Series 300 EMU"
    car_number: str = "Car 1 (Leading Cab)"
    service_status: str = "REVENUE_SERVICE"
    subsystem_ids: List[str] = Field(default_factory=lambda: ["SUB-APU-01"])
    is_illustrative_context: bool = True
    context_note: str = "Illustrative operational hierarchy mapping for MetroPT-3 compressor telemetry."


class SubsystemEntity(BaseModel):
    subsystem_id: str = "SUB-APU-01"
    train_id: str = "TRAIN-302"
    name: str = "Air Production Unit"
    subsystem_code: str = "APU"
    asset_ids: List[str] = Field(default_factory=lambda: ["APU-COMP-01"])
    is_illustrative_context: bool = True
    context_note: str = "Illustrative operational hierarchy mapping for MetroPT-3 compressor telemetry."


class CompressorAssetEntity(BaseModel):
    asset_id: str = "APU-COMP-01"
    subsystem_id: str = "SUB-APU-01"
    name: str = "Air Compressor Unit #01"
    criticality: str = "CRITICAL"
    service_role: str = "Main Air Supply"
    rated_pressure_bar: float = 10.0
    discharge_valve_model: str = "Knorr-Bremse LP49"


class ValidationReference(BaseModel):
    scenario_id: str = "SCENARIO-FAIL-03"
    scenario_name: str = "Failure #3 — Air Leak / High Stress"
    dataset_source: str = "MetroPT-3 Historical Telemetry"
    historical_period: str = "February 2020 — August 2020"
    reported_failure_mode: str = "Air leak in Air Production Unit"
    reported_failure_start: str = "2020-06-05T10:00:00Z"
    conventional_lps_breach: str = "2020-06-06T19:42:19Z"
    online_detector_confirmation: str = "2020-06-05T09:50:39Z"
    confirmed_intervention_window_minutes: int = 2032
    confirmed_intervention_window_formatted: str = "33h 52m"
    computed_by_compressorguard: Dict[str, Any] = Field(
        default_factory=lambda: {
            "online_detector_confirmation": "2020-06-05T09:50:39Z",
            "confirmed_intervention_window_minutes": 2032,
            "confirmed_intervention_window_formatted": "33h 52m",
        }
    )
    maintenance_summary: str = (
        "UCI dataset ground truth record: MetroPT-3 compressor failure report #3 "
        "indicates discharge valve leak and high thermal stress. CompressorGuard provides "
        "a 33h 52m actionable intervention window prior to reactive Low Pressure Switch breach."
    )


class AssetRegistry:
    def __init__(self) -> None:
        self.fleets: Dict[str, FleetEntity] = {
            "FLEET-METRO-01": FleetEntity(),
        }
        self.trains: Dict[str, TrainEntity] = {
            "TRAIN-302": TrainEntity(),
        }
        self.subsystems: Dict[str, SubsystemEntity] = {
            "SUB-APU-01": SubsystemEntity(),
        }
        self.assets: Dict[str, CompressorAssetEntity] = {
            "APU-COMP-01": CompressorAssetEntity(),
        }
        self.validation_references: Dict[str, ValidationReference] = {
            "SCENARIO-FAIL-03": ValidationReference(),
        }

    @classmethod
    def get_default(cls) -> "AssetRegistry":
        return cls()

    def get_fleet(self, fleet_id: str) -> Optional[FleetEntity]:
        return self.fleets.get(fleet_id)

    def get_train(self, train_id: str) -> Optional[TrainEntity]:
        return self.trains.get(train_id)

    def get_subsystem(self, subsystem_id: str) -> Optional[SubsystemEntity]:
        return self.subsystems.get(subsystem_id)

    def get_asset(self, asset_id: str) -> Optional[CompressorAssetEntity]:
        return self.assets.get(asset_id)

    def get_validation_reference(self, scenario_id: str) -> Optional[ValidationReference]:
        return self.validation_references.get(scenario_id)

    def get_asset_hierarchy_tree(self) -> Dict[str, Any]:
        return {
            "fleet": self.fleets["FLEET-METRO-01"].model_dump(),
            "train": self.trains["TRAIN-302"].model_dump(),
            "subsystem": self.subsystems["SUB-APU-01"].model_dump(),
            "asset": self.assets["APU-COMP-01"].model_dump(),
        }
