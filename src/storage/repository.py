from datetime import datetime, timezone
import math
from typing import Optional, Dict, Any, List
from src.storage.mongo_client import get_mongo_db, init_mongodb_schema


class CompressorGuardRepository:
    def __init__(self, db=None):
        self.db = db if db is not None else get_mongo_db()
        init_mongodb_schema(self.db)

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

    def get_rolling_stats(
        self,
        asset_id: str,
        window_seconds: int = 600,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        MongoDB Aggregation Pipeline #1: Window Functions ($setWindowFields)
        Computes rolling mean and standard deviation over a sliding time window on the
        Time Series `measurements` collection.
        """
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

