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

    def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        results = list(self.documents)
        for stage in pipeline:
            if "$match" in stage:
                match_spec = stage["$match"]
                results = [doc for doc in results if self._doc_matches_query(doc, match_spec)]

            elif "$setWindowFields" in stage:
                dv_vals = [r.get("dv_pressure_bar", 0.0) for r in results]
                oil_vals = [r.get("oil_temp_c", 0.0) for r in results]
                avg_dv = sum(dv_vals) / len(dv_vals) if dv_vals else 0.0
                avg_oil = sum(oil_vals) / len(oil_vals) if oil_vals else 0.0
                for r in results:
                    r["rolling_avg_dv"] = round(avg_dv, 4)
                    r["rolling_avg_oil_temp"] = round(avg_oil, 2)

            elif "$sort" in stage:
                sort_spec = stage["$sort"]
                def _safe_sort_key(doc, key):
                    val = doc.get(key, 0)
                    if val is None:
                        return 0
                    if hasattr(val, "tzinfo") and val.tzinfo is not None:
                        return val.astimezone(timezone.utc).replace(tzinfo=None)
                    return val
                for k, direction in sort_spec.items():
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



def init_mongodb_schema(db: Any) -> List[str]:
    existing = db.list_collection_names()

    # 1. Time Series Collection for high-frequency measurements
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
        db["measurements"].create_index([("timestamp", pymongo.ASCENDING)], expireAfterSeconds=30 * 86400)
    except Exception:
        pass

    # 2. Collections for cases and events
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

    return db.list_collection_names()
