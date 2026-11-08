"""
Domain Asset Registry & Hierarchy for CompressorGuard Enterprise Platform.

Provides multi-level industrial operational hierarchy:
Fleet (Metro Line 1) -> Trains (TRAIN-301, TRAIN-302, TRAIN-303) -> Subsystems (APU)
-> Components (APU-COMP-01, APU-DRY-LP49, APU-RES-TP3, APU-SW-LPS).

Implements True Singleton pattern with in-memory persistence and dynamic threshold propagation.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class FleetEntity(BaseModel):
    fleet_id: str = "FLEET-METRO-01"
    name: str = "RailOps VN — Đội tàu Metro số 1 (Bến Thành – Suối Tiên)"
    operator_name: str = "HURC1 — Đường sắt đô thị TP.HCM"
    depot_location: str = "Depot Long Bình"
    train_ids: List[str] = Field(
        default_factory=lambda: ["TRAIN-301", "TRAIN-302", "TRAIN-303"]
    )
    total_trains: int = 3
    active_trains: int = 3
    normal_trains: int = 2
    alerted_trains: int = 1
    is_illustrative_context: bool = True
    context_note: str = (
        "Bối cảnh phân cấp vận hành Metro đô thị VN mô phỏng trên tập dữ liệu "
        "khí nén MetroPT-3 (Metro do Porto, Bồ Đào Nha)."
    )


class TrainEntity(BaseModel):
    train_id: str = "TRAIN-302"
    fleet_id: str = "FLEET-METRO-01"
    name: str = "Đoàn tàu 302"
    model: str = "Nippon Sharyo Type 001 EMU"
    car_number: str = "Toa 1 (Cabin lái điều khiển)"
    service_status: str = "REVENUE_SERVICE"
    route: str = "Bến Thành – Suối Tiên"
    health_status: str = "WARNING_P1"
    health_label: str = "Cảnh báo P1"
    status: str = "WARNING_P1"
    badge: str = "WARNING"
    speed_kmh: float = 54.0
    brake_pressure_bar: float = 9.19
    brake_safety_margin: str = "+2.19 bar"
    safety_buffer: Optional[str] = "33h 52m"
    safety_buffer_minutes: Optional[int] = 2032
    has_active_warning: bool = True
    subsystem_ids: List[str] = Field(default_factory=lambda: ["SUB-APU-01"])
    depot_location: str = "Depot Long Bình"
    is_illustrative_context: bool = True
    context_note: str = (
        "Bối cảnh phân cấp vận hành Metro đô thị VN mô phỏng trên tập dữ liệu "
        "khí nén MetroPT-3 (Metro do Porto, Bồ Đào Nha)."
    )


class SubsystemEntity(BaseModel):
    subsystem_id: str = "SUB-APU-01"
    train_id: str = "TRAIN-302"
    name: str = "Air Production Unit"
    display_name: str = "Phân hệ cấp khí nén APU"
    subsystem_code: str = "APU"
    asset_ids: List[str] = Field(
        default_factory=lambda: [
            "APU-COMP-01",
            "APU-DRY-LP49",
            "APU-RES-TP3",
            "APU-SW-LPS",
        ]
    )
    component_ids: List[str] = Field(
        default_factory=lambda: [
            "APU-COMP-01",
            "APU-DRY-LP49",
            "APU-RES-TP3",
            "APU-SW-LPS",
        ]
    )
    is_illustrative_context: bool = True
    context_note: str = (
        "Bối cảnh phân cấp vận hành Metro đô thị VN mô phỏng trên tập dữ liệu "
        "khí nén MetroPT-3 (Metro do Porto, Bồ Đào Nha)."
    )


class ComponentEntity(BaseModel):
    component_id: str
    asset_id: Optional[str] = None
    subsystem_id: str = "SUB-APU-01"
    train_id: str = "TRAIN-302"
    fleet_id: str = "FLEET-METRO-01"
    name: str
    component_type: str
    manufacturer: str = "Knorr-Bremse"
    model_number: str
    installation_date: str = "15/01/2020"
    operating_hours: int = 14280
    rated_pressure_bar: float = 10.0
    criticality: str = "CRITICAL"
    service_role: str = "Main Air Supply"
    service_role_vi: str = "Cấp khí nén hệ thống phanh & treo"
    discharge_valve_model: Optional[str] = None
    status: str = "NORMAL"
    status_label: str = "Bình thường"
    badge: str = "NORMAL"
    leak_pressure_threshold_bar: float = 0.05
    oil_temp_threshold_c: float = 67.0
    maintenance_depot: str = "Depot Long Bình"
    transient_filter: bool = True
    supervision_priority: str = "P1 - Khẩn cấp"
    maintenance_notes: str = ""
    last_updated_by: Optional[str] = "Hùng Bùi (NV-0941)"
    last_updated_at: Optional[str] = "2020-06-05T09:50:39Z"
    latest_reading: Dict[str, Any] = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        if self.asset_id is None:
            self.asset_id = self.component_id


class CompressorAssetEntity(BaseModel):
    asset_id: str = "APU-COMP-01"
    subsystem_id: str = "SUB-APU-01"
    name: str = "Cụm máy nén khí chính APU-01"
    criticality: str = "CRITICAL"
    service_role: str = "Main Air Supply"
    service_role_vi: str = "Cấp khí nén hệ thống phanh & treo"
    rated_pressure_bar: float = 10.0
    discharge_valve_model: str = "Van xả điện từ DV (Pneumatic Pilot Valve)"


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


_REGISTRY_INSTANCE: Optional["AssetRegistry"] = None


class AssetRegistry:
    def __init__(self) -> None:
        self.fleets: Dict[str, FleetEntity] = {
            "FLEET-METRO-01": FleetEntity(),
        }

        # Initialize 3 trains on Metro Line 1
        self.trains: Dict[str, TrainEntity] = {
            "TRAIN-301": TrainEntity(
                train_id="TRAIN-301",
                fleet_id="FLEET-METRO-01",
                name="Đoàn tàu 301",
                model="Nippon Sharyo Type 001 EMU",
                health_status="NORMAL",
                health_label="Bình thường",
                status="NORMAL",
                badge="NORMAL",
                speed_kmh=58.0,
                brake_pressure_bar=9.20,
                brake_safety_margin="+2.20 bar",
                safety_buffer="—",
                safety_buffer_minutes=None,
                has_active_warning=False,
                subsystem_ids=["SUB-APU-301"],
                depot_location="Depot Long Bình",
            ),
            "TRAIN-302": TrainEntity(
                train_id="TRAIN-302",
                fleet_id="FLEET-METRO-01",
                name="Đoàn tàu 302",
                model="Nippon Sharyo Type 001 EMU",
                health_status="WARNING_P1",
                health_label="Cảnh báo P1",
                status="WARNING_P1",
                badge="WARNING",
                speed_kmh=54.0,
                brake_pressure_bar=9.19,
                brake_safety_margin="+2.19 bar",
                safety_buffer="33h 52m",
                safety_buffer_minutes=2032,
                has_active_warning=True,
                subsystem_ids=["SUB-APU-01"],
                depot_location="Depot Long Bình",
            ),
            "TRAIN-303": TrainEntity(
                train_id="TRAIN-303",
                fleet_id="FLEET-METRO-01",
                name="Đoàn tàu 303",
                model="Nippon Sharyo Type 001 EMU",
                health_status="NORMAL",
                health_label="Bình thường",
                status="NORMAL",
                badge="NORMAL",
                speed_kmh=60.0,
                brake_pressure_bar=9.18,
                brake_safety_margin="+2.18 bar",
                safety_buffer="—",
                safety_buffer_minutes=None,
                has_active_warning=False,
                subsystem_ids=["SUB-APU-303"],
                depot_location="Depot Long Bình",
            ),
        }

        # Initialize APU Subsystems
        self.subsystems: Dict[str, SubsystemEntity] = {
            "SUB-APU-01": SubsystemEntity(
                subsystem_id="SUB-APU-01",
                train_id="TRAIN-302",
                name="Air Production Unit",
                display_name="Phân hệ cấp khí nén APU",
                subsystem_code="APU",
                asset_ids=["APU-COMP-01", "APU-DRY-LP49", "APU-RES-TP3", "APU-SW-LPS"],
                component_ids=["APU-COMP-01", "APU-DRY-LP49", "APU-RES-TP3", "APU-SW-LPS"],
            ),
            "SUB-APU-301": SubsystemEntity(
                subsystem_id="SUB-APU-301",
                train_id="TRAIN-301",
                name="Air Production Unit",
                display_name="Phân hệ cấp khí nén APU",
                subsystem_code="APU",
                asset_ids=["APU-COMP-301", "APU-DRY-301", "APU-RES-301", "APU-SW-301"],
                component_ids=["APU-COMP-301", "APU-DRY-301", "APU-RES-301", "APU-SW-301"],
            ),
            "SUB-APU-303": SubsystemEntity(
                subsystem_id="SUB-APU-303",
                train_id="TRAIN-303",
                name="Air Production Unit",
                display_name="Phân hệ cấp khí nén APU",
                subsystem_code="APU",
                asset_ids=["APU-COMP-303", "APU-DRY-303", "APU-RES-303", "APU-SW-303"],
                component_ids=["APU-COMP-303", "APU-DRY-303", "APU-RES-303", "APU-SW-303"],
            ),
        }

        # Initialize Components
        self.components: Dict[str, ComponentEntity] = {
            # --- TRAIN-302 Components (Focal point of Failure #3) ---
            "APU-COMP-01": ComponentEntity(
                component_id="APU-COMP-01",
                asset_id="APU-COMP-01",
                subsystem_id="SUB-APU-01",
                train_id="TRAIN-302",
                fleet_id="FLEET-METRO-01",
                name="Máy nén khí chính (APU-COMP-01)",
                component_type="COMPRESSOR",
                manufacturer="Knorr-Bremse",
                model_number="VV120-T",
                installation_date="15/01/2020",
                operating_hours=14280,
                rated_pressure_bar=10.0,
                criticality="CRITICAL",
                service_role="Main Air Supply",
                service_role_vi="Cấp nguồn khí nén áp lực cao cho hệ thống phanh và bóng đệm khí",
                discharge_valve_model="Van xả điện từ DV (Pneumatic Pilot Valve)",
                status="WARNING",
                status_label="Cảnh báo quá nhiệt",
                badge="WARNING",
                leak_pressure_threshold_bar=0.05,
                oil_temp_threshold_c=67.0,
                maintenance_depot="Depot Long Bình",
                transient_filter=True,
                supervision_priority="P1 - Khẩn cấp",
                maintenance_notes="Giám sát nhiệt độ dầu máy nén trong chu kỳ nén có tải",
                last_updated_by="Hùng Bùi (NV-0941)",
                last_updated_at="2020-06-05T09:50:39Z",
                latest_reading={
                    "dv_pressure_bar": 9.19,
                    "oil_temp_c": 58.2,
                    "motor_current_a": 3.8,
                    "tp3_bar": 9.19,
                },
            ),
            "APU-DRY-LP49": ComponentEntity(
                component_id="APU-DRY-LP49",
                asset_id="APU-DRY-LP49",
                subsystem_id="SUB-APU-01",
                train_id="TRAIN-302",
                fleet_id="FLEET-METRO-01",
                name="Tháp sấy khí & Cụm van xả (Dryer & Drain Valve LP49)",
                component_type="DRYER_DRAIN_VALVE",
                manufacturer="Knorr-Bremse",
                model_number="LP49",
                installation_date="15/01/2020",
                operating_hours=14280,
                rated_pressure_bar=10.0,
                criticality="HIGH",
                service_role="Air Drying & Water Drain",
                service_role_vi="Hút ẩm khí nén và tự động xả nước ngưng qua van xả áp điện từ DV",
                status="LEAKING",
                status_label="Đang rò rỉ khí",
                badge="LEAKING",
                leak_pressure_threshold_bar=0.05,
                oil_temp_threshold_c=67.0,
                maintenance_depot="Depot Long Bình",
                transient_filter=True,
                supervision_priority="P1 - Khẩn cấp",
                maintenance_notes="Cần đại tu van xả DV do xuất hiện rò rỉ khí liên tục trong pha ngắt tải",
                last_updated_by="Hùng Bùi (NV-0941)",
                last_updated_at="2020-06-05T09:50:39Z",
                latest_reading={
                    "dv_pressure_bar": 1.12,
                    "valve_status": "CHẬM ĐÓNG",
                    "leak_severity": "P1",
                },
            ),
            "APU-RES-TP3": ComponentEntity(
                component_id="APU-RES-TP3",
                asset_id="APU-RES-TP3",
                subsystem_id="SUB-APU-01",
                train_id="TRAIN-302",
                fleet_id="FLEET-METRO-01",
                name="Bình chứa khí phanh chính (Main Reservoir TP3)",
                component_type="RESERVOIR",
                manufacturer="Knorr-Bremse",
                model_number="Steel 300L Air Reservoir",
                installation_date="15/01/2020",
                operating_hours=14280,
                rated_pressure_bar=10.0,
                criticality="CRITICAL",
                service_role="Main Air Reservoir",
                service_role_vi="Tích trữ dự phòng áp suất phanh và duy trì cơ cấu an toàn dừng tàu",
                status="SAFE",
                status_label="An toàn",
                badge="SAFE",
                leak_pressure_threshold_bar=0.05,
                oil_temp_threshold_c=67.0,
                maintenance_depot="Depot Long Bình",
                transient_filter=True,
                supervision_priority="P2 - Tiêu chuẩn",
                maintenance_notes="Áp suất bình chứa duy trì an toàn 9.19 bar (ngưỡng ngắt khẩn LPS 7.0 bar)",
                last_updated_by="Hùng Bùi (NV-0941)",
                last_updated_at="2020-06-05T09:50:39Z",
                latest_reading={
                    "tp3_bar": 9.19,
                    "safety_margin_bar": 2.19,
                    "capacity_liters": 300,
                },
            ),
            "APU-SW-LPS": ComponentEntity(
                component_id="APU-SW-LPS",
                asset_id="APU-SW-LPS",
                subsystem_id="SUB-APU-01",
                train_id="TRAIN-302",
                fleet_id="FLEET-METRO-01",
                name="Rơ-le áp suất thấp (Low Pressure Switch LPS)",
                component_type="PRESSURE_SWITCH",
                manufacturer="Knorr-Bremse",
                model_number="LPS-02",
                installation_date="15/01/2020",
                operating_hours=14280,
                rated_pressure_bar=10.0,
                criticality="CRITICAL",
                service_role="Emergency Low Pressure Trip",
                service_role_vi="Cảm biến bảo vệ an toàn ngắt khẩn khi áp suất phanh tụt dưới 7.0 bar",
                status="NORMAL",
                status_label="Bình thường",
                badge="NORMAL",
                leak_pressure_threshold_bar=0.05,
                oil_temp_threshold_c=67.0,
                maintenance_depot="Depot Long Bình",
                transient_filter=True,
                supervision_priority="P1 - Khẩn cấp",
                maintenance_notes="Chưa kích hoạt ngắt an toàn. Biên áp suất dự phòng +2.19 bar",
                last_updated_by="Hùng Bùi (NV-0941)",
                last_updated_at="2020-06-05T09:50:39Z",
                latest_reading={
                    "lps_active": 0.0,
                    "trip_threshold_bar": 7.0,
                    "margin_bar": 2.19,
                },
            ),

            # --- TRAIN-301 Components (Normal operation) ---
            "APU-COMP-301": ComponentEntity(
                component_id="APU-COMP-301",
                asset_id="APU-COMP-301",
                subsystem_id="SUB-APU-301",
                train_id="TRAIN-301",
                fleet_id="FLEET-METRO-01",
                name="Máy nén khí chính (APU-COMP-301)",
                component_type="COMPRESSOR",
                model_number="VV120-T",
                service_role="Main Air Supply",
                service_role_vi="Cấp nguồn khí nén hệ thống phanh",
                status="NORMAL",
                status_label="Bình thường",
                badge="NORMAL",
                maintenance_notes="Hoạt động ổn định, thông số danh định đạt yêu cầu",
                latest_reading={"dv_pressure_bar": 0.01, "oil_temp_c": 54.0, "tp3_bar": 9.20},
            ),
            "APU-DRY-301": ComponentEntity(
                component_id="APU-DRY-301",
                asset_id="APU-DRY-301",
                subsystem_id="SUB-APU-301",
                train_id="TRAIN-301",
                fleet_id="FLEET-METRO-01",
                name="Tháp sấy khí & Cụm van xả (Dryer LP49)",
                component_type="DRYER_DRAIN_VALVE",
                model_number="LP49",
                service_role="Air Drying & Water Drain",
                service_role_vi="Hút ẩm và xả nước ngưng",
                status="NORMAL",
                status_label="Bình thường",
                badge="NORMAL",
                latest_reading={"dv_pressure_bar": 0.01, "valve_status": "BÌNH THƯỜNG"},
            ),
            "APU-RES-301": ComponentEntity(
                component_id="APU-RES-301",
                asset_id="APU-RES-301",
                subsystem_id="SUB-APU-301",
                train_id="TRAIN-301",
                fleet_id="FLEET-METRO-01",
                name="Bình chứa khí phanh chính (Main Reservoir TP3)",
                component_type="RESERVOIR",
                model_number="Steel 300L Air Reservoir",
                service_role="Main Air Reservoir",
                status="SAFE",
                status_label="An toàn",
                badge="SAFE",
                latest_reading={"tp3_bar": 9.20, "safety_margin_bar": 2.20},
            ),
            "APU-SW-301": ComponentEntity(
                component_id="APU-SW-301",
                asset_id="APU-SW-301",
                subsystem_id="SUB-APU-301",
                train_id="TRAIN-301",
                fleet_id="FLEET-METRO-01",
                name="Rơ-le áp suất thấp (Low Pressure Switch LPS)",
                component_type="PRESSURE_SWITCH",
                model_number="LPS-02",
                service_role="Emergency Low Pressure Trip",
                status="NORMAL",
                status_label="Bình thường",
                badge="NORMAL",
                latest_reading={"lps_active": 0.0, "trip_threshold_bar": 7.0},
            ),

            # --- TRAIN-303 Components (Normal operation) ---
            "APU-COMP-303": ComponentEntity(
                component_id="APU-COMP-303",
                asset_id="APU-COMP-303",
                subsystem_id="SUB-APU-303",
                train_id="TRAIN-303",
                fleet_id="FLEET-METRO-01",
                name="Máy nén khí chính (APU-COMP-303)",
                component_type="COMPRESSOR",
                model_number="VV120-T",
                service_role="Main Air Supply",
                service_role_vi="Cấp nguồn khí nén hệ thống phanh",
                status="NORMAL",
                status_label="Bình thường",
                badge="NORMAL",
                maintenance_notes="Hoạt động ổn định, chu kỳ bảo dưỡng định kỳ tiếp theo sau 800 giờ",
                latest_reading={"dv_pressure_bar": 0.02, "oil_temp_c": 53.5, "tp3_bar": 9.18},
            ),
            "APU-DRY-303": ComponentEntity(
                component_id="APU-DRY-303",
                asset_id="APU-DRY-303",
                subsystem_id="SUB-APU-303",
                train_id="TRAIN-303",
                fleet_id="FLEET-METRO-01",
                name="Tháp sấy khí & Cụm van xả (Dryer LP49)",
                component_type="DRYER_DRAIN_VALVE",
                model_number="LP49",
                service_role="Air Drying & Water Drain",
                service_role_vi="Hút ẩm và xả nước ngưng",
                status="NORMAL",
                status_label="Bình thường",
                badge="NORMAL",
                latest_reading={"dv_pressure_bar": 0.02, "valve_status": "BÌNH THƯỜNG"},
            ),
            "APU-RES-303": ComponentEntity(
                component_id="APU-RES-303",
                asset_id="APU-RES-303",
                subsystem_id="SUB-APU-303",
                train_id="TRAIN-303",
                fleet_id="FLEET-METRO-01",
                name="Bình chứa khí phanh chính (Main Reservoir TP3)",
                component_type="RESERVOIR",
                model_number="Steel 300L Air Reservoir",
                service_role="Main Air Reservoir",
                status="SAFE",
                status_label="An toàn",
                badge="SAFE",
                latest_reading={"tp3_bar": 9.18, "safety_margin_bar": 2.18},
            ),
            "APU-SW-303": ComponentEntity(
                component_id="APU-SW-303",
                asset_id="APU-SW-303",
                subsystem_id="SUB-APU-303",
                train_id="TRAIN-303",
                fleet_id="FLEET-METRO-01",
                name="Rơ-le áp suất thấp (Low Pressure Switch LPS)",
                component_type="PRESSURE_SWITCH",
                model_number="LPS-02",
                service_role="Emergency Low Pressure Trip",
                status="NORMAL",
                status_label="Bình thường",
                badge="NORMAL",
                latest_reading={"lps_active": 0.0, "trip_threshold_bar": 7.0},
            ),
        }

        # Backward compatibility dictionary
        self.assets: Dict[str, CompressorAssetEntity] = {
            "APU-COMP-01": CompressorAssetEntity(),
        }

        self.validation_references: Dict[str, ValidationReference] = {
            "SCENARIO-FAIL-03": ValidationReference(),
        }

    @classmethod
    def get_default(cls) -> "AssetRegistry":
        """Returns process-wide singleton instance of AssetRegistry."""
        global _REGISTRY_INSTANCE
        if _REGISTRY_INSTANCE is None:
            _REGISTRY_INSTANCE = cls()
        return _REGISTRY_INSTANCE

    @classmethod
    def reset_default(cls) -> "AssetRegistry":
        """Resets process-wide singleton instance (for testing)."""
        global _REGISTRY_INSTANCE
        _REGISTRY_INSTANCE = cls()
        return _REGISTRY_INSTANCE

    def get_fleet(self, fleet_id: str) -> Optional[FleetEntity]:
        return self.fleets.get(fleet_id)

    def get_train(self, train_id: str) -> Optional[TrainEntity]:
        return self.trains.get(train_id)

    def get_trains(self) -> List[Dict[str, Any]]:
        """Returns list of trains in canonical order for Fleet Overview."""
        order = ["TRAIN-301", "TRAIN-302", "TRAIN-303"]
        result = []
        for tid in order:
            if tid in self.trains:
                result.append(self.trains[tid].model_dump())
        return result

    def get_subsystem(self, subsystem_id: str) -> Optional[SubsystemEntity]:
        return self.subsystems.get(subsystem_id)

    def get_subsystems_by_train(self, train_id: str) -> List[SubsystemEntity]:
        return [s for s in self.subsystems.values() if s.train_id == train_id]

    def get_component(self, component_id: str) -> Optional[ComponentEntity]:
        return self.components.get(component_id)

    def get_components_by_train(self, train_id: str) -> List[ComponentEntity]:
        return [c for c in self.components.values() if c.train_id == train_id]

    def get_components_by_subsystem(self, subsystem_id: str) -> List[ComponentEntity]:
        return [c for c in self.components.values() if c.subsystem_id == subsystem_id]

    def get_all_components(self) -> List[ComponentEntity]:
        return list(self.components.values())

    def get_asset(self, asset_id: str) -> Optional[Any]:
        if asset_id in self.assets:
            return self.assets[asset_id]
        return self.components.get(asset_id)

    def get_validation_reference(self, scenario_id: str) -> Optional[ValidationReference]:
        return self.validation_references.get(scenario_id)

    def update_component(
        self,
        component_id: str,
        updates: Dict[str, Any],
        operator: Optional[str] = None,
    ) -> Optional[ComponentEntity]:
        """
        Updates component fields in-memory with automatic audit trail attribution.
        """
        comp = self.components.get(component_id)
        if comp is None:
            return None

        actor = (
            operator
            or updates.get("last_updated_by")
            or updates.get("operator_name")
            or updates.get("operator_id")
            or "Hùng Bùi (NV-0941)"
        )
        now_iso = datetime.now(timezone.utc).isoformat()

        allowed_fields = {
            "leak_pressure_threshold_bar",
            "oil_temp_threshold_c",
            "maintenance_depot",
            "transient_filter",
            "supervision_priority",
            "maintenance_notes",
            "status",
            "status_label",
            "badge",
            "latest_reading",
        }

        comp_dict = comp.model_dump()
        for field, val in updates.items():
            if field in allowed_fields and val is not None:
                comp_dict[field] = val

        comp_dict["last_updated_by"] = actor
        comp_dict["last_updated_at"] = now_iso

        updated_comp = ComponentEntity(**comp_dict)
        self.components[component_id] = updated_comp

        if component_id == "APU-COMP-01" and "APU-COMP-01" in self.assets:
            self.assets["APU-COMP-01"].rated_pressure_bar = updated_comp.rated_pressure_bar

        return updated_comp

    def update_component_config(
        self,
        component_id: str,
        updates: Dict[str, Any],
        operator: Optional[str] = None,
    ) -> Optional[ComponentEntity]:
        """Alias for update_component."""
        return self.update_component(component_id, updates, operator=operator)

    def get_asset_hierarchy_tree(self) -> Dict[str, Any]:
        """
        Returns full hierarchy tree (Fleet -> Trains -> Subsystems -> Components)
        along with backward-compatible single asset keys.
        """
        fleet_dump = self.fleets["FLEET-METRO-01"].model_dump()
        trains_tree = []
        for train_id in ["TRAIN-301", "TRAIN-302", "TRAIN-303"]:
            t = self.trains.get(train_id)
            if not t:
                continue
            t_dict = t.model_dump()
            subs_list = []
            for s_id in t.subsystem_ids:
                sub = self.subsystems.get(s_id)
                if not sub:
                    continue
                sub_dict = sub.model_dump()
                sub_dict["components"] = [
                    c.model_dump()
                    for c in self.components.values()
                    if c.subsystem_id == s_id
                ]
                subs_list.append(sub_dict)
            t_dict["subsystems"] = subs_list
            trains_tree.append(t_dict)

        return {
            "fleet": fleet_dump,
            "trains": trains_tree,
            "train": self.trains["TRAIN-302"].model_dump(),
            "subsystem": self.subsystems["SUB-APU-01"].model_dump(),
            "asset": (
                self.components["APU-COMP-01"].model_dump()
                if "APU-COMP-01" in self.components
                else self.assets["APU-COMP-01"].model_dump()
            ),
            "components": [
                c.model_dump()
                for c in self.components.values()
                if c.train_id == "TRAIN-302"
            ],
        }

    def get_operations_kpis(self) -> Dict[str, Any]:
        total = len(self.trains)
        normal = sum(1 for t in self.trains.values() if t.health_status == "NORMAL")
        alert = sum(1 for t in self.trains.values() if t.health_status != "NORMAL")
        return {
            "total_trains": f"{total}/{total}",
            "normal_trains": normal,
            "alerted_trains": alert,
            "standby_depot": "Depot Long Bình",
        }

    def get_hero_banner(self) -> Dict[str, Any]:
        t302 = self.trains.get("TRAIN-302")
        is_active = t302 is not None and t302.health_status == "WARNING_P1"
        return {
            "is_active": is_active,
            "active": is_active,
            "train_id": "TRAIN-302",
            "train_name": "Đoàn tàu 302",
            "safety_buffer": "33h 52m",
            "safety_buffer_minutes": 2032,
            "brake_margin": "+2.19 bar",
            "severity": "P1",
            "priority_label": "P1 - CẢNH BÁO RÒ RỈ KHÍ",
            "title": "CẢNH BÁO P1 — RÒ RỈ KHÍ PHÂN HỆ APU",
            "action_label": "Vào Phòng Điều Tra Sự Cố ➔",
            "action_target": "view-workbench",
            "description": (
                "Phát hiện rò van xả cụm sấy khí LP49 trên đoàn tàu TRAIN-302. "
                "Áp suất phanh hiện tại 9.19 bar (vùng an toàn +2.19 bar)."
            ),
        }
