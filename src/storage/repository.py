from datetime import datetime, timezone
import math
from typing import Optional, Dict, Any, List
import pymongo
from src.storage.mongo_client import get_mongo_db, init_mongodb_schema


DEFAULT_COMPONENT_CONFIGS = [
    {
        "component_id": "APU-COMP-01",
        "train_id": "TRAIN-302",
        "leak_pressure_threshold_bar": 0.05,
        "oil_temp_threshold_c": 67.0,
        "maintenance_depot": "Depot Long Bình",
        "transient_filter": True,
        "supervision_priority": "P1 - Khẩn cấp",
        "maintenance_notes": "Theo dõi nhiệt độ dầu và dòng điện động cơ kéo máy nén chính",
        "last_updated_by": "Hùng Bùi (NV-0941)",
        "last_updated_at": "2020-06-05T09:50:39Z",
    },
    {
        "component_id": "APU-DRY-LP49",
        "train_id": "TRAIN-302",
        "leak_pressure_threshold_bar": 0.05,
        "oil_temp_threshold_c": 67.0,
        "maintenance_depot": "Depot Long Bình",
        "transient_filter": True,
        "supervision_priority": "P1 - Khẩn cấp",
        "maintenance_notes": "Kiểm tra định kỳ van xả pilot cụm tháp sấy LP49",
        "last_updated_by": "Hùng Bùi (NV-0941)",
        "last_updated_at": "2020-06-05T09:50:39Z",
    },
    {
        "component_id": "APU-RES-TP3",
        "train_id": "TRAIN-302",
        "leak_pressure_threshold_bar": 0.05,
        "oil_temp_threshold_c": 67.0,
        "maintenance_depot": "Depot Long Bình",
        "transient_filter": True,
        "supervision_priority": "P2 - Tiêu chuẩn",
        "maintenance_notes": "Bình chứa khí nén phanh chính 300L, duy trì áp lực an toàn > 9.0 bar",
        "last_updated_by": "Hùng Bùi (NV-0941)",
        "last_updated_at": "2020-06-05T09:50:39Z",
    },
    {
        "component_id": "APU-SW-LPS",
        "train_id": "TRAIN-302",
        "leak_pressure_threshold_bar": 0.05,
        "oil_temp_threshold_c": 67.0,
        "maintenance_depot": "Depot Long Bình",
        "transient_filter": True,
        "supervision_priority": "P1 - Khẩn cấp",
        "maintenance_notes": "Rơ-le áp suất thấp LPS, tác động cắt phanh khẩn cấp khi dưới 7.0 bar",
        "last_updated_by": "Hùng Bùi (NV-0941)",
        "last_updated_at": "2020-06-05T09:50:39Z",
    },
]

DEFAULT_SOP_PLAYBOOKS = [
    {
        "sop_id": "SOP-APU-ISO-04",
        "title": "Xử lý rò rỉ van xả cụm tháp sấy khí (LP49)",
        "category": "Hệ thống khí nén APU",
        "version": "v2.1",
        "effective_date": "2024-01-15",
        "applicable_component_id": "APU-DRY-LP49",
        "target_component": "APU-DRY-LP49",
        "priority": "P1",
        "target_depot": "Depot Long Bình",
        "estimated_duration_minutes": 45,
        "maintenance_window": "NEXT_TERMINAL_STOP",
        "safety_warning": "Xả áp toàn phần bình chứa khí chính TP3 trước khi tháo giắc điện van pilot DV.",
        "steps": [
            {
                "step_number": 1,
                "action": "Cô lập van pilot xả ngưng điện từ DV trên cụm tháp sấy LP49",
                "role": "Kỹ thuật viên Depot",
                "safety_check": "Xác nhận áp kế chỉ về 0 bar",
                "expected_result": "Không còn áp lực dư trong buồng sấy",
            },
            {
                "step_number": 2,
                "action": "Kiểm tra độ kín buồng van màng, vệ sinh muội dầu và hạt hút ẩm nghẹt",
                "role": "Kỹ thuật viên Depot",
                "safety_check": "Đeo kính bảo hộ và găng tay chịu nhiệt",
                "expected_result": "Phát hiện vết rách hoặc cặn bám",
            },
            {
                "step_number": 3,
                "action": "Thay mới gioăng đệm O-ring chịu nhiệt và lò xo hồi vị",
                "role": "Kỹ thuật viên Depot",
                "safety_check": "Kiểm tra kích thước chuẩn Viton",
                "expected_result": "Gioăng mới lắp khít hoàn toàn",
            },
            {
                "step_number": 4,
                "action": "Kích hoạt chu trình nạp khí thử nghiệm 5 chu kỳ nén có tải liên tục",
                "role": "Kỹ thuật viên Depot",
                "safety_check": "Theo dõi đồng hồ áp suất cabin",
                "expected_result": "Áp suất tăng đều không tụt áp",
            },
            {
                "step_number": 5,
                "action": "Đo kiểm áp suất dư buồng xả DV (< 0.05 bar) và nhiệt độ dầu (< 67°C) nghiệm thu",
                "role": "Trực ban OCC",
                "safety_check": "Dung sai đo kiểm ± 0.01 bar",
                "expected_result": "Đạt 5/5 mẫu tải phục hồi chuẩn",
            },
        ],
        "safety_precautions": [
            "Tuyệt đối ngắt nguồn điều khiển điện từ trước khi tháo lắp cuộn coil.",
            "Đảm bảo áp suất bình tích khí phụ được xả hoàn toàn trước khi mở nắp van.",
        ],
        "last_updated_by": "Hùng Bùi (NV-0941)",
        "last_updated_at": "2020-06-05T09:50:39Z",
    },
    {
        "sop_id": "SOP-APU-ISO-01",
        "title": "Kiểm tra rơ-le áp suất thấp LPS và van an toàn SV",
        "category": "Hệ thống an toàn áp suất",
        "version": "v1.8",
        "effective_date": "2023-11-20",
        "applicable_component_id": "APU-SW-LPS",
        "target_component": "APU-SW-LPS",
        "priority": "P2",
        "target_depot": "Depot Long Bình",
        "estimated_duration_minutes": 30,
        "maintenance_window": "OVERNIGHT_STABLING",
        "safety_warning": "Ngắt nguồn điều khiển 110VDC trước khi đo điện trở tiếp điểm LPS.",
        "steps": [
            {
                "step_number": 1,
                "action": "Đo kiểm ngưỡng tác động đóng ngắt rơ-le LPS ở mốc 7.0 bar",
                "role": "Kỹ thuật viên Depot",
                "safety_check": "Đồng hồ chuẩn kiểm định còn hạn",
                "expected_result": "Rơ-le nhảy ngắt chính xác ở 7.0 bar",
            },
            {
                "step_number": 2,
                "action": "Kiểm tra tín hiệu điện áp phản hồi về rơ-le an toàn TCMS",
                "role": "Kỹ thuật viên Depot",
                "safety_check": "Điện áp danh định 110VDC",
                "expected_result": "Tín hiệu đóng ngắt truyền về buồng lái",
            },
            {
                "step_number": 3,
                "action": "Kiểm tra cơ cấu xả khẩn van an toàn SV tại ngưỡng 10.5 bar",
                "role": "Kỹ thuật viên Depot",
                "safety_check": "Đứng cách xa hướng xả của van",
                "expected_result": "Van bung xả đúng áp định mức",
            },
        ],
        "safety_precautions": [
            "Không đứng trước hướng thoát khí của van an toàn.",
        ],
        "last_updated_by": "Hùng Bùi (NV-0941)",
        "last_updated_at": "2020-06-05T08:00:00Z",
    },
    {
        "sop_id": "SOP-APU-ISO-08",
        "title": "Đại tu tháp hút ẩm và thay hạt hút ẩm silicagel",
        "category": "Bảo dưỡng định kỳ APU",
        "version": "v1.5",
        "effective_date": "2024-02-10",
        "applicable_component_id": "APU-DRY-LP49",
        "target_component": "APU-DRY-LP49",
        "priority": "P3",
        "target_depot": "Depot Long Bình",
        "estimated_duration_minutes": 90,
        "maintenance_window": "SCHEDULED_OVERHAUL",
        "safety_warning": "Đeo kính bảo hộ và khẩu trang chống bụi khi xử lý hạt hút ẩm đã qua sử dụng.",
        "steps": [
            {
                "step_number": 1,
                "action": "Tháo nắp tháp sấy đôi và loại bỏ hạt hút ẩm bão hòa",
                "role": "Kỹ thuật viên Depot",
                "safety_check": "Đeo khẩu trang chống bụi hạt",
                "expected_result": "Thu hồi toàn bộ hạt ẩm biến chất",
            },
            {
                "step_number": 2,
                "action": "Vệ sinh lưới lọc tinh và sấy khô lòng tháp",
                "role": "Kỹ thuật viên Depot",
                "safety_check": "Dùng khí nén sạch khô",
                "expected_result": "Lòng tháp sạch hoàn toàn cặn bẩn",
            },
            {
                "step_number": 3,
                "action": "Nạp hạt hút ẩm phân tử mới và siết lực nắp theo tiêu chuẩn Knorr-Bremse",
                "role": "Kỹ thuật viên Depot",
                "safety_check": "Lực siết cân lực 45 Nm",
                "expected_result": "Kín khí hoàn toàn khi nén thử tải",
            },
        ],
        "safety_precautions": [
            "Bảo quản hạt hút ẩm mới trong bao bì kín, tránh hút ẩm trước khi nạp.",
        ],
        "last_updated_by": "Hùng Bùi (NV-0941)",
        "last_updated_at": "2020-06-05T08:00:00Z",
    },
]

DEFAULT_SHIFT_HANDOVERS = [
    {
        "handover_id": "HO-20200605-01",
        "shift_name": "Ca 1 (06:00 – 14:00)",
        "outgoing_operator": "Lê Văn Hùng (NV-0820)",
        "incoming_operator": "Hùng Bùi (NV-0941)",
        "timestamp": "2020-06-05T06:00:00Z",
        "depot_location": "Depot Long Bình",
        "operational_depot": "Trung tâm Điều hành OCC Tuyến Metro Số 1 (HURC1)",
        "fleet_status_summary": "3/3 đoàn tàu đang chạy trên tuyến; thông số phanh và áp suất bình chính ổn định.",
        "open_cases_count": 0,
        "handover_notes": "Bắt đầu ca trực sáng. Kiểm tra tình trạng sẵn sàng hệ thống nén khí APU toàn hạm đội.",
        "acknowledged_active_cases": [],
        "checklist_verified": True,
    }
]


class CompressorGuardRepository:
    def __init__(self, db=None):
        self.db = db if db is not None else get_mongo_db()
        init_mongodb_schema(self.db)
        self._init_enterprise_collections()

    def _init_enterprise_collections(self) -> None:
        """Seed enterprise collections if they are empty."""
        try:
            # 1. component_configs
            configs = list(self.db["component_configs"].find({}))
            if not configs:
                self.db["component_configs"].insert_many(DEFAULT_COMPONENT_CONFIGS)
                try:
                    self.db["component_configs"].create_index([("component_id", pymongo.ASCENDING)], unique=True)
                except Exception:
                    pass

            # 2. sop_playbooks
            sops = list(self.db["sop_playbooks"].find({}))
            if not sops:
                self.db["sop_playbooks"].insert_many(DEFAULT_SOP_PLAYBOOKS)
                try:
                    self.db["sop_playbooks"].create_index([("sop_id", pymongo.ASCENDING)], unique=True)
                except Exception:
                    pass

            # 3. shift_handovers
            handovers = list(self.db["shift_handovers"].find({}))
            if not handovers:
                self.db["shift_handovers"].insert_many(DEFAULT_SHIFT_HANDOVERS)
                try:
                    self.db["shift_handovers"].create_index([("handover_id", pymongo.ASCENDING)], unique=True)
                    self.db["shift_handovers"].create_index([("timestamp", pymongo.DESCENDING)])
                except Exception:
                    pass
        except Exception:
            pass

    def insert_measurement(self, point_dict: Dict[str, Any]) -> str:
        doc = dict(point_dict)
        if "ingested_at" not in doc:
            doc["ingested_at"] = datetime.now(timezone.utc)
        res = self.db["measurements"].insert_one(doc)
        return str(res.inserted_id)

    def insert_measurements_batch(self, points: List[Dict[str, Any]]) -> int:
        if not points:
            return 0
        now_utc = datetime.now(timezone.utc)
        docs = []
        for p in points:
            d = dict(p)
            if "ingested_at" not in d:
                d["ingested_at"] = now_utc
            docs.append(d)
        res = self.db["measurements"].insert_many(docs)
        return len(res.inserted_ids)

    def save_anomaly_signal(self, signal_dict: Dict[str, Any]) -> str:
        doc = dict(signal_dict)
        if "ingested_at" not in doc:
            doc["ingested_at"] = datetime.now(timezone.utc)
        res = self.db["anomaly_signals"].insert_one(doc)
        return str(res.inserted_id)

    def get_recent_anomaly_signals(self, asset_id: str = "APU-COMP-01", limit: int = 30) -> List[Dict[str, Any]]:
        pipeline = [
            {"$match": {"asset_id": asset_id}},
            {"$sort": {"timestamp": -1}},
            {"$limit": limit},
        ]
        raw = list(self.db["anomaly_signals"].aggregate(pipeline))
        cleaned = []
        for item in raw:
            d = dict(item)
            d.pop("_id", None)
            if hasattr(d.get("timestamp"), "isoformat"):
                d["timestamp"] = d["timestamp"].isoformat()
            if hasattr(d.get("ingested_at"), "isoformat"):
                d["ingested_at"] = d["ingested_at"].isoformat()
            cleaned.append(d)
        return cleaned

    def save_case(self, case_dict: Dict[str, Any]) -> str:
        case_id = case_dict.get("case_id") or case_dict.get("incident_id") or "CASE-UNKNOWN"
        doc = dict(case_dict)
        doc["case_id"] = case_id
        self.db["operational_cases"].update_one(
            {"case_id": case_id},
            {"$set": doc},
            upsert=True
        )
        return case_id

    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        return self.db["operational_cases"].find_one({"case_id": case_id}, {"_id": 0})

    def get_active_case_for_asset(self, asset_id: str) -> Optional[Dict[str, Any]]:
        return self.db["operational_cases"].find_one(
            {"asset_id": asset_id, "phase": {"$nin": ["RESOLVED", "CLOSED"]}},
            {"_id": 0}
        )

    def save_case_event(self, event_dict: Dict[str, Any]) -> str:
        res = self.db["case_events"].insert_one(event_dict)
        return str(res.inserted_id)

    def get_case_events(self, case_id: str) -> List[Dict[str, Any]]:
        return self.db["case_events"].find({"case_id": case_id}, {"_id": 0})

    # -------------------------------------------------------------------------
    # Component Configurations Persistence (Màn hình 2)
    # -------------------------------------------------------------------------
    def save_component_config(self, component_id: str, config: Dict[str, Any]) -> str:
        """
        Lưu hoặc cập nhật cấu hình thiết bị con vào collection component_configs.
        Tương thích hoàn hảo với real MongoDB và InMemoryDatabase.
        """
        doc = dict(config)
        doc["component_id"] = component_id
        if "last_updated_at" not in doc or not doc["last_updated_at"]:
            doc["last_updated_at"] = datetime.now(timezone.utc).isoformat()
        self.db["component_configs"].update_one(
            {"component_id": component_id},
            {"$set": doc},
            upsert=True
        )
        return component_id

    def get_component_config(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Lấy cấu hình chi tiết của một thiết bị con theo component_id."""
        return self.db["component_configs"].find_one({"component_id": component_id}, {"_id": 0})

    def get_all_component_configs(self) -> List[Dict[str, Any]]:
        """Lấy toàn bộ danh sách cấu hình thiết bị con."""
        return list(self.db["component_configs"].find({}, {"_id": 0}))

    # -------------------------------------------------------------------------
    # SOP Playbooks Persistence (Màn hình 4)
    # -------------------------------------------------------------------------
    def save_sop(self, sop_id: str, sop_dict: Dict[str, Any]) -> str:
        """
        Lưu hoặc cập nhật quy trình chuẩn SOP vào collection sop_playbooks.
        """
        doc = dict(sop_dict)
        doc["sop_id"] = sop_id
        if "last_updated_at" not in doc or not doc["last_updated_at"]:
            doc["last_updated_at"] = datetime.now(timezone.utc).isoformat()
        self.db["sop_playbooks"].update_one(
            {"sop_id": sop_id},
            {"$set": doc},
            upsert=True
        )
        return sop_id

    def get_sop(self, sop_id: str) -> Optional[Dict[str, Any]]:
        """Lấy quy trình SOP theo mã sop_id."""
        return self.db["sop_playbooks"].find_one({"sop_id": sop_id}, {"_id": 0})

    def get_all_sops(self) -> List[Dict[str, Any]]:
        """Lấy danh mục tất cả quy trình chuẩn SOP."""
        return list(self.db["sop_playbooks"].find({}, {"_id": 0}))

    # -------------------------------------------------------------------------
    # Shift Handovers Persistence (Màn hình 4)
    # -------------------------------------------------------------------------
    def save_shift_handover(self, handover_dict: Dict[str, Any]) -> str:
        """
        Lưu biên bản bàn giao ca trực vào collection shift_handovers.
        Tự động tạo handover_id nếu chưa có.
        """
        doc = dict(handover_dict)
        handover_id = doc.get("handover_id")
        if not handover_id:
            ts_str = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
            handover_id = f"HO-{ts_str}"
            doc["handover_id"] = handover_id
        if "timestamp" not in doc or not doc["timestamp"]:
            doc["timestamp"] = datetime.now(timezone.utc).isoformat()
        self.db["shift_handovers"].update_one(
            {"handover_id": handover_id},
            {"$set": doc},
            upsert=True
        )
        return handover_id

    def get_recent_shift_handovers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Lấy danh sách các biên bản bàn giao ca gần nhất, sắp xếp thời gian giảm dần.
        Sử dụng aggregation pipeline để tương thích cả MongoDB và InMemoryCollection.
        """
        pipeline = [
            {"$sort": {"timestamp": -1}},
            {"$limit": limit},
        ]
        raw = list(self.db["shift_handovers"].aggregate(pipeline))
        cleaned = []
        for item in raw:
            d = dict(item)
            d.pop("_id", None)
            if hasattr(d.get("timestamp"), "isoformat"):
                d["timestamp"] = d["timestamp"].isoformat()
            cleaned.append(d)
        return cleaned

    def get_rolling_stats(
        self,
        asset_id: str,
        window_seconds: int = 600,
        limit: int = 50,
        max_timestamp: Optional[Any] = None,
    ) -> List[Dict[str, Any]]:
        """
        MongoDB Aggregation Pipeline #1: Window Functions ($setWindowFields)
        Computes rolling mean and standard deviation over a sliding time window on the
        Time Series `measurements` collection.
        """
        match_criteria: Dict[str, Any] = {"metadata.asset_id": asset_id}
        if max_timestamp is not None:
            match_criteria["timestamp"] = {"$lte": max_timestamp}
        pipeline = [
            {"$match": match_criteria},
            {
                "$setWindowFields": {
                    "partitionBy": "$metadata.asset_id",
                    "sortBy": {"timestamp": 1},
                    "output": {
                        "rolling_avg_dv": {
                            "$avg": "$dv_pressure_bar",
                            "window": {"range": [-window_seconds, 0], "unit": "second"}
                        },
                        "rolling_std_dv": {
                            "$stdDevSamp": "$dv_pressure_bar",
                            "window": {"range": [-window_seconds, 0], "unit": "second"}
                        },
                        "rolling_avg_oil_temp": {
                            "$avg": "$oil_temp_c",
                            "window": {"range": [-window_seconds, 0], "unit": "second"}
                        }
                    }
                }
            },
            {"$sort": {"timestamp": -1}},
            {"$limit": limit}
        ]
        return list(self.db["measurements"].aggregate(pipeline))

    def get_regime_duty_cycle_analytics(
        self,
        asset_id: str = "APU-COMP-01",
    ) -> Dict[str, Any]:
        """
        MongoDB Aggregation Pipeline #2: Multi-Facet Regime & Duty Cycle Profiler ($facet + $group)
        Analyzes operating regime distribution (LOADED duty cycle %), peak physical stress,
        and alert hygiene (suppressed transient spikes vs. opened cases).
        """
        pipeline = [
            {"$match": {"metadata.asset_id": asset_id}},
            {
                "$facet": {
                    "by_regime": [
                        {
                            "$group": {
                                "_id": "$regime",
                                "sample_count": {"$sum": 1},
                                "avg_dv_pressure_bar": {"$avg": "$dv_pressure_bar"},
                                "max_dv_pressure_bar": {"$max": "$dv_pressure_bar"},
                                "avg_oil_temp_c": {"$avg": "$oil_temp_c"},
                                "max_oil_temp_c": {"$max": "$oil_temp_c"},
                            }
                        }
                    ],
                    "overall_extremes": [
                        {
                            "$group": {
                                "_id": None,
                                "total_samples": {"$sum": 1},
                                "peak_dv_pressure_bar": {"$max": "$dv_pressure_bar"},
                                "peak_oil_temp_c": {"$max": "$oil_temp_c"},
                                "min_tp3_bar": {"$min": "$tp3_bar"},
                            }
                        }
                    ],
                }
            },
        ]
        agg_res = list(self.db["measurements"].aggregate(pipeline))
        facet_data = agg_res[0] if agg_res else {"by_regime": [], "overall_extremes": []}

        by_regime = facet_data.get("by_regime", [])
        extremes_list = facet_data.get("overall_extremes", [])
        extremes = extremes_list[0] if extremes_list else {
            "total_samples": 0,
            "peak_dv_pressure_bar": 0.0,
            "peak_oil_temp_c": 0.0,
            "min_tp3_bar": 0.0,
        }

        total_samples = int(extremes.get("total_samples", 0))
        loaded_samples = sum(
            int(r.get("sample_count", 0))
            for r in by_regime
            if r.get("_id") == "LOADED"
        )
        loaded_duty_pct = round((loaded_samples / total_samples) * 100.0, 2) if total_samples > 0 else 0.0

        suppressed_signals = self.db["anomaly_signals"].find(
            {"asset_id": asset_id, "disposition": "SUPPRESSED_TRANSIENT"}
        )
        suppressed_count = len(list(suppressed_signals))

        return {
            "asset_id": asset_id,
            "total_samples_analyzed": total_samples,
            "loaded_samples_count": loaded_samples,
            "loaded_duty_cycle_pct": loaded_duty_pct,
            "peak_dv_pressure_bar": round(float(extremes.get("peak_dv_pressure_bar") or 0.0), 4),
            "peak_oil_temp_c": round(float(extremes.get("peak_oil_temp_c") or 0.0), 2),
            "min_tp3_bar": round(float(extremes.get("min_tp3_bar") or 0.0), 2),
            "suppressed_transient_spikes_count": suppressed_count,
            "regime_breakdown": [
                {
                    "regime": str(r.get("_id") or "UNKNOWN"),
                    "sample_count": int(r.get("sample_count", 0)),
                    "avg_dv_pressure_bar": round(float(r.get("avg_dv_pressure_bar") or 0.0), 4),
                    "max_dv_pressure_bar": round(float(r.get("max_dv_pressure_bar") or 0.0), 4),
                    "avg_oil_temp_c": round(float(r.get("avg_oil_temp_c") or 0.0), 2),
                    "max_oil_temp_c": round(float(r.get("max_oil_temp_c") or 0.0), 2),
                }
                for r in by_regime
            ],
        }

    def match_failure_fingerprint(
        self,
        dv_sigma: float,
        oil_sigma: float,
        if_score: float,
        loaded_duty_pct: float = 70.0,
    ) -> List[Dict[str, Any]]:
        """
        MongoDB Operational Query #3: Historical Failure Fingerprint Similarity Matching.
        Compares the observed thermodynamic & ML vector against canonical historical
        MetroPT-3 failure episodes stored in `failure_fingerprints` to recommend the right SOP.
        """
        fps = list(self.db["failure_fingerprints"].find({}, {"_id": 0}))
        obs_vec = [
            max(0.0, float(dv_sigma)) / 25.0,
            max(0.0, float(oil_sigma)) / 10.0,
            max(0.0, float(if_score)),
            max(0.0, float(loaded_duty_pct)) / 100.0,
        ]
        obs_norm = math.sqrt(sum(v * v for v in obs_vec)) or 1e-6

        ranked = []
        for fp in fps:
            sig = fp.get("signature_vector", {})
            ref_vec = [
                float(sig.get("dv_sigma_ref", 0.0)) / 25.0,
                float(sig.get("oil_sigma_ref", 0.0)) / 10.0,
                float(sig.get("if_score_ref", 0.0)),
                float(sig.get("loaded_duty_pct_ref", 50.0)) / 100.0,
            ]
            ref_norm = math.sqrt(sum(v * v for v in ref_vec)) or 1e-6
            cosine_sim = sum(a * b for a, b in zip(obs_vec, ref_vec)) / (obs_norm * ref_norm)
            ranked.append({
                "fingerprint_id": fp.get("fingerprint_id"),
                "episode_id": fp.get("episode_id"),
                "title": fp.get("title"),
                "similarity_score": round(max(0.0, min(1.0, cosine_sim)), 4),
                "recommended_playbook": fp.get("recommended_playbook"),
                "recommended_action": fp.get("recommended_action"),
                "root_cause_component": fp.get("root_cause_component"),
            })

        ranked.sort(key=lambda x: x["similarity_score"], reverse=True)
        return ranked
