import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import pymongo
from pymongo.database import Database

DEFAULT_MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("MONGODB_DB_NAME", "compressorguard")

_CLIENT = None
_MONGO_AVAILABLE: Optional[bool] = None


class InMemoryCollection:
    def __init__(self, name: str):
        self.name = name
        self.documents: List[Dict[str, Any]] = []
        self._indexes: Dict[str, Any] = {}

    def clear(self):
        self.documents = []

    @staticmethod
    def _doc_matches_query(d: Dict[str, Any], query: Dict[str, Any]) -> bool:
        for k, v in query.items():
            val = d
            if "." in k:
                for part in k.split("."):
                    val = val.get(part) if isinstance(val, dict) else None
            else:
                val = d.get(k)

            if isinstance(v, dict):
                if "$ne" in v and val == v["$ne"]:
                    return False
                if "$nin" in v and val in v["$nin"]:
                    return False
                if "$in" in v and val not in v["$in"]:
                    return False
                if "$gt" in v and (val is None or val <= v["$gt"]):
                    return False
                if "$gte" in v and (val is None or val < v["$gte"]):
                    return False
                if "$lt" in v and (val is None or val >= v["$lt"]):
                    return False
                if "$lte" in v and (val is None or val > v["$lte"]):
                    return False
            elif val != v:
                return False
        return True

    def insert_one(self, doc: Dict[str, Any]):
        class InsertResult:
            def __init__(self, doc_id):
                self.inserted_id = doc_id
        d = dict(doc)
        if "_id" not in d:
            d["_id"] = f"{self.name}_{len(self.documents) + 1}"
        self.documents.append(d)
        return InsertResult(d["_id"])

    def insert_many(self, docs: List[Dict[str, Any]]):
        class InsertManyResult:
            def __init__(self, doc_ids):
                self.inserted_ids = doc_ids
        ids = []
        for doc in docs:
            res = self.insert_one(doc)
            ids.append(res.inserted_id)
        return InsertManyResult(ids)

    def find_one(self, query: Dict[str, Any], projection: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        for d in reversed(self.documents):
            if self._doc_matches_query(d, query):
                res = dict(d)
                if projection and projection.get("_id") == 0 and "_id" in res:
                    del res["_id"]
                return res
        return None

    def find(self, query: Dict[str, Any], projection: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        results = []
        for d in self.documents:
            if self._doc_matches_query(d, query):
                res = dict(d)
                if projection and projection.get("_id") == 0 and "_id" in res:
                    del res["_id"]
                results.append(res)
        return results

    def update_one(self, query: Dict[str, Any], update: Dict[str, Any], upsert: bool = False):
        set_vals = update.get("$set", {})
        for idx, d in enumerate(self.documents):
            if self._doc_matches_query(d, query):
                self.documents[idx].update(set_vals)
                return
        if upsert:
            new_doc = dict(query)
            new_doc.update(set_vals)
            self.insert_one(new_doc)

    def delete_many(self, query: Dict[str, Any]):
        class DeleteResult:
            def __init__(self, count):
                self.deleted_count = count
        if not query:
            count = len(self.documents)
            self.documents = []
            return DeleteResult(count)
        kept = []
        del_count = 0
        for d in self.documents:
            if self._doc_matches_query(d, query):
                del_count += 1
            else:
                kept.append(d)
        self.documents = kept
        return DeleteResult(del_count)

    def clear(self):
        self.documents = []
        self._indexes = {}

    def create_index(self, keys: Any, **kwargs):
        name = kwargs.get("name", str(keys))
        self._indexes[name] = {"key": keys, **kwargs}
        return name

    def index_information(self) -> Dict[str, Any]:
        return dict(self._indexes)

    @staticmethod
    def _extract_field(doc: Dict[str, Any], field_expr: Any) -> Any:
        if not isinstance(field_expr, str) or not field_expr.startswith("$"):
            return field_expr
        path = field_expr[1:]
        val = doc
        for part in path.split("."):
            val = val.get(part) if isinstance(val, dict) else None
        return val

    def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        import math

        results = [dict(d) for d in self.documents]
        for stage in pipeline:
            if "$match" in stage:
                match_spec = stage["$match"]
                results = [doc for doc in results if self._doc_matches_query(doc, match_spec)]

            elif "$setWindowFields" in stage:
                # Sliding window statistics (up to 60 preceding samples ~ 600s)
                for idx, r in enumerate(results):
                    win_slice = results[max(0, idx - 59): idx + 1]
                    dv_vals = [float(x.get("dv_pressure_bar", 0.0)) for x in win_slice]
                    oil_vals = [float(x.get("oil_temp_c", 0.0)) for x in win_slice]
                    avg_dv = sum(dv_vals) / len(dv_vals) if dv_vals else 0.0
                    avg_oil = sum(oil_vals) / len(oil_vals) if oil_vals else 0.0
                    if len(dv_vals) > 1:
                        var_dv = sum((v - avg_dv) ** 2 for v in dv_vals) / (len(dv_vals) - 1)
                        std_dv = math.sqrt(max(0.0, var_dv))
                    else:
                        std_dv = 0.0927
                    r["rolling_avg_dv"] = round(avg_dv, 4)
                    r["rolling_std_dv"] = round(std_dv, 4)
                    r["rolling_avg_oil_temp"] = round(avg_oil, 2)

            elif "$group" in stage:
                group_spec = stage["$group"]
                id_expr = group_spec.get("_id")
                buckets: Dict[Any, List[Dict[str, Any]]] = {}
                for doc in results:
                    key = self._extract_field(doc, id_expr) if id_expr is not None else None
                    buckets.setdefault(key, []).append(doc)

                grouped_results = []
                for key, docs_in_bucket in buckets.items():
                    out_doc: Dict[str, Any] = {"_id": key}
                    for field_out, acc_spec in group_spec.items():
                        if field_out == "_id" or not isinstance(acc_spec, dict):
                            continue
                        if "$sum" in acc_spec:
                            sum_target = acc_spec["$sum"]
                            if isinstance(sum_target, (int, float)):
                                out_doc[field_out] = len(docs_in_bucket) * sum_target
                            else:
                                vals = [float(self._extract_field(d, sum_target) or 0.0) for d in docs_in_bucket]
                                out_doc[field_out] = sum(vals)
                        elif "$avg" in acc_spec:
                            vals = [
                                float(self._extract_field(d, acc_spec["$avg"]))
                                for d in docs_in_bucket
                                if self._extract_field(d, acc_spec["$avg"]) is not None
                            ]
                            out_doc[field_out] = round(sum(vals) / len(vals), 4) if vals else 0.0
                        elif "$max" in acc_spec:
                            vals = [
                                float(self._extract_field(d, acc_spec["$max"]))
                                for d in docs_in_bucket
                                if self._extract_field(d, acc_spec["$max"]) is not None
                            ]
                            out_doc[field_out] = round(max(vals), 4) if vals else 0.0
                        elif "$min" in acc_spec:
                            vals = [
                                float(self._extract_field(d, acc_spec["$min"]))
                                for d in docs_in_bucket
                                if self._extract_field(d, acc_spec["$min"]) is not None
                            ]
                            out_doc[field_out] = round(min(vals), 4) if vals else 0.0
                    grouped_results.append(out_doc)
                results = grouped_results

            elif "$facet" in stage:
                facet_spec = stage["$facet"]
                facet_out: Dict[str, Any] = {}
                for facet_name, sub_pipeline in facet_spec.items():
                    temp_col = InMemoryCollection(f"{self.name}_{facet_name}")
                    temp_col.documents = [dict(d) for d in results]
                    facet_out[facet_name] = temp_col.aggregate(sub_pipeline)
                results = [facet_out]

            elif "$sort" in stage:
                sort_spec = stage["$sort"]
                def _safe_sort_key(doc, key):
                    val = doc.get(key, 0)
                    if val is None:
                        return 0
                    if hasattr(val, "tzinfo") and val.tzinfo is not None:
                        return val.astimezone(timezone.utc).replace(tzinfo=None)
                    return val
                for k, direction in reversed(list(sort_spec.items())):
                    results.sort(key=lambda x: _safe_sort_key(x, k), reverse=(direction == -1))

            elif "$limit" in stage:
                limit = stage["$limit"]
                results = results[:limit]

        return results


class InMemoryDatabase:
    def __init__(self, name: str = DATABASE_NAME):
        self.name = name
        self.collections: Dict[str, InMemoryCollection] = {}

    def clear(self):
        for col in self.collections.values():
            col.clear()
        self.collections = {}

    def __getitem__(self, name: str) -> InMemoryCollection:
        if name not in self.collections:
            self.collections[name] = InMemoryCollection(name)
        return self.collections[name]

    def list_collection_names(self) -> List[str]:
        return list(self.collections.keys())

    def create_collection(self, name: str, **kwargs) -> InMemoryCollection:
        if name not in self.collections:
            self.collections[name] = InMemoryCollection(name)
        return self.collections[name]


def is_mongo_available() -> bool:
    global _MONGO_AVAILABLE
    if _MONGO_AVAILABLE is not None:
        return _MONGO_AVAILABLE
    try:
        client = pymongo.MongoClient(DEFAULT_MONGO_URI, serverSelectionTimeoutMS=1000)
        client.admin.command("ping")
        _MONGO_AVAILABLE = True
    except Exception:
        _MONGO_AVAILABLE = False
    return _MONGO_AVAILABLE


_IN_MEMORY_DB = None


def get_mongo_client() -> Optional[pymongo.MongoClient]:
    global _CLIENT
    if not is_mongo_available():
        return None
    if _CLIENT is None:
        _CLIENT = pymongo.MongoClient(DEFAULT_MONGO_URI, serverSelectionTimeoutMS=2000)
    return _CLIENT


def get_mongo_db() -> Any:
    global _IN_MEMORY_DB
    if is_mongo_available():
        client = get_mongo_client()
        return client[DATABASE_NAME]
    if _IN_MEMORY_DB is None:
        _IN_MEMORY_DB = InMemoryDatabase(DATABASE_NAME)
    return _IN_MEMORY_DB


def reset_in_memory_db() -> None:
    global _IN_MEMORY_DB
    if _IN_MEMORY_DB is not None:
        _IN_MEMORY_DB.clear()
        _IN_MEMORY_DB = None


DEFAULT_FAILURE_FINGERPRINTS = [
    {
        "fingerprint_id": "FP-METROPT3-FAIL-03",
        "episode_id": "failure_3",
        "title": "Failure #3 — Dryer Discharge Pilot Valve Leakage & Thermal Drift",
        "historical_period": "2020-06-05 to 2020-06-06",
        "recommended_playbook": "SOP-APU-ISO-04",
        "recommended_action": "Isolate Dryer Tower #2 drain valve, apply APU derated load-sharing, and schedule Depot Oriente valve replacement.",
        "root_cause_component": "Desiccant Dryer Discharge Pilot Valve (Knorr-Bremse LP49)",
        "signature_vector": {
            "dv_sigma_ref": 23.75,
            "oil_sigma_ref": 5.71,
            "if_score_ref": 0.382,
            "loaded_duty_pct_ref": 75.0,
        },
    },
    {
        "fingerprint_id": "FP-METROPT3-FAIL-01",
        "episode_id": "failure_1",
        "title": "Failure #1 — High-Duty Pneumatic Air Leak",
        "historical_period": "2020-04-12 to 2020-04-18",
        "recommended_playbook": "SOP-APU-LEAK-01",
        "recommended_action": "Inspect secondary pneumatic manifold and governor cut-in/cut-out pressure thresholds at terminal depot.",
        "root_cause_component": "Pneumatic Distribution Manifold & Governor Seal",
        "signature_vector": {
            "dv_sigma_ref": 14.20,
            "oil_sigma_ref": 3.80,
            "if_score_ref": 0.365,
            "loaded_duty_pct_ref": 85.0,
        },
    },
    {
        "fingerprint_id": "FP-METROPT3-FAIL-04",
        "episode_id": "failure_4",
        "title": "Failure #4 — Compressor Oil Contamination & Severe Thermal Stress",
        "historical_period": "2020-07-08 to 2020-07-15",
        "recommended_playbook": "SOP-APU-THERM-02",
        "recommended_action": "Flush compressor oil circuit, inspect oil level sensor, and replace thermal bypass cartridge.",
        "root_cause_component": "Lubrication Cooling Circuit & Oil Separator",
        "signature_vector": {
            "dv_sigma_ref": 4.50,
            "oil_sigma_ref": 6.80,
            "if_score_ref": 0.395,
            "loaded_duty_pct_ref": 65.0,
        },
    },
]


def init_mongodb_schema(db: Any) -> List[str]:
    existing = db.list_collection_names()

    # 1. Time Series Collection for high-frequency measurements
    # CRITICAL INVARIANT: Never set expireAfterSeconds on historical `timestamp` (year 2020),
    # or MongoDB's TTL monitor will immediately purge all 2020 records!
    if "measurements" not in existing:
        try:
            db.create_collection(
                "measurements",
                timeseries={
                    "timeField": "timestamp",
                    "metaField": "metadata",
                    "granularity": "seconds",
                },
            )
        except Exception:
            db.create_collection("measurements")

    try:
        db["measurements"].create_index([("timestamp", pymongo.ASCENDING)], name="idx_measurements_timestamp")
        db["measurements"].create_index([("metadata.asset_id", pymongo.ASCENDING)], name="idx_measurements_asset")
    except Exception:
        pass

    # 2. Anomaly Signals Collection (Raw detector triggers & suppressed transient spikes)
    # Uses wall-clock `ingested_at` for 7-day TTL lifecycle retention
    if "anomaly_signals" not in existing:
        db.create_collection("anomaly_signals")
    try:
        db["anomaly_signals"].create_index(
            [("ingested_at", pymongo.ASCENDING)],
            expireAfterSeconds=7 * 86400,
            name="idx_ttl_ingested_at_7d",
        )
        db["anomaly_signals"].create_index([("asset_id", pymongo.ASCENDING)], name="idx_signals_asset")
    except Exception:
        pass

    # 3. Collections for cases and events
    if "operational_cases" not in existing:
        db.create_collection("operational_cases")
        try:
            db["operational_cases"].create_index([("case_id", pymongo.ASCENDING)], unique=True)
            db["operational_cases"].create_index([("asset_id", pymongo.ASCENDING)])
        except Exception:
            pass

    if "case_events" not in existing:
        db.create_collection("case_events")
        try:
            db["case_events"].create_index([("case_id", pymongo.ASCENDING)])
            db["case_events"].create_index([("event_time", pymongo.ASCENDING)])
        except Exception:
            pass

    # 4. Historical Failure Fingerprints Collection for Similarity Matching
    if "failure_fingerprints" not in existing:
        db.create_collection("failure_fingerprints")
    try:
        existing_fps = db["failure_fingerprints"].find({})
        if not list(existing_fps):
            db["failure_fingerprints"].insert_many(DEFAULT_FAILURE_FINGERPRINTS)
    except Exception:
        pass

    return db.list_collection_names()

