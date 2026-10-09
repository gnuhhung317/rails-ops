from typing import Optional, Dict, Any, List
from src.storage.mongo_client import get_mongo_db, init_mongodb_schema


class CompressorGuardRepository:
    def __init__(self, db=None):
        self.db = db if db is not None else get_mongo_db()
        init_mongodb_schema(self.db)

    def insert_measurement(self, point_dict: Dict[str, Any]) -> str:
        res = self.db["measurements"].insert_one(point_dict)
        return str(res.inserted_id)

    def insert_measurements_batch(self, points: List[Dict[str, Any]]) -> int:
        if not points:
            return 0
        res = self.db["measurements"].insert_many(points)
        return len(res.inserted_ids)

    def save_case(self, case_dict: Dict[str, Any]) -> str:
        case_id = case_dict.get("case_id", "CASE-UNKNOWN")
        self.db["operational_cases"].update_one(
            {"case_id": case_id},
            {"$set": case_dict},
            upsert=True
        )
        return case_id

    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        return self.db["operational_cases"].find_one({"case_id": case_id}, {"_id": 0})

    def get_active_case_for_asset(self, asset_id: str) -> Optional[Dict[str, Any]]:
        return self.db["operational_cases"].find_one(
            {"asset_id": asset_id, "phase": {"$ne": "RESOLVED"}},
            {"_id": 0}
        )

    def save_case_event(self, event_dict: Dict[str, Any]) -> str:
        res = self.db["case_events"].insert_one(event_dict)
        return str(res.inserted_id)

    def get_case_events(self, case_id: str) -> List[Dict[str, Any]]:
        return self.db["case_events"].find({"case_id": case_id}, {"_id": 0})

    def get_rolling_stats(self, asset_id: str, window_seconds: int = 600) -> List[Dict[str, Any]]:
        pipeline = [
            {"$match": {"metadata.asset_id": asset_id}},
            {
                "$setWindowFields": {
                    "partitionBy": "$metadata.asset_id",
                    "sortBy": {"timestamp": 1},
                    "output": {
                        "rolling_avg_dv": {
                            "$avg": "$dv_pressure_bar",
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
            {"$limit": 50}
        ]
        return list(self.db["measurements"].aggregate(pipeline))
