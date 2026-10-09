# MongoDB Integration & Operational Case Screens Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Triển khai tích hợp MongoDB Atlas / Local (`localhost:27017`) cho Time Series telemetry và Operational Cases, đồng thời tài liệu hóa toàn bộ kiến trúc giao diện sản phẩm qua bộ đặc tả `screen/*.md`.

**Architecture:** Tạo storage layer `src/storage/` gồm `mongo_client.py` và `repository.py` kết nối tới MongoDB `compressorguard`. Hỗ trợ Time Series collection `measurements` với Aggregation Pipeline `$setWindowFields` tính rolling stats và document collections (`operational_cases`, `evidence_records`). Tạo thư mục `screen/` chứa 7 tệp đặc tả màn hình phản ánh cấu trúc Operations Console (Asset Overview, Active Cases, Case Workspace 4 câu hỏi vàng).

**Tech Stack:** Python 3.12, PyMongo 4.17, FastAPI, Pytest, Markdown.

---

### Task 1: MongoDB Client & Collection Initializer

**Files:**
- Create: `src/storage/__init__.py`
- Create: `src/storage/mongo_client.py`
- Test: `tests/test_mongodb_storage.py`

- [ ] **Step 1: Write the failing test for MongoDB connection & schema setup**

```python
# tests/test_mongodb_storage.py
import pytest
from src.storage.mongo_client import get_mongo_db, init_mongodb_schema

def test_mongodb_connection_and_initialization():
    db = get_mongo_db()
    assert db.name == "compressorguard"
    collections = init_mongodb_schema(db)
    assert "measurements" in collections
    assert "operational_cases" in collections
    assert "evidence_records" in collections
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_mongodb_storage.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'src.storage'`

- [ ] **Step 3: Implement `src/storage/__init__.py` and `src/storage/mongo_client.py`**

```python
# src/storage/mongo_client.py
import os
import pymongo
from pymongo.database import Database

DEFAULT_MONGO_URI = os.getenv(
    "MONGODB_URI",
    "mongodb://admin:password123@localhost:27017/?authSource=admin"
)
DATABASE_NAME = os.getenv("MONGODB_DB_NAME", "compressorguard")

_CLIENT = None

def get_mongo_client() -> pymongo.MongoClient:
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = pymongo.MongoClient(DEFAULT_MONGO_URI, serverSelectionTimeoutMS=4000)
    return _CLIENT

def get_mongo_db() -> Database:
    client = get_mongo_client()
    return client[DATABASE_NAME]

def init_mongodb_schema(db: Database) -> list:
    existing = db.list_collection_names()
    
    # 1. Time Series Collection for high-frequency measurements
    if "measurements" not in existing:
        db.create_collection(
            "measurements",
            timeseries={
                "timeField": "timestamp",
                "metaField": "metadata",
                "granularity": "seconds"
            }
        )
    
    # 2. Collections for cases and evidence
    if "operational_cases" not in existing:
        db.create_collection("operational_cases")
        db["operational_cases"].create_index([("case_id", pymongo.ASCENDING)], unique=True)
        db["operational_cases"].create_index([("asset_id", pymongo.ASCENDING)])

    if "evidence_records" not in existing:
        db.create_collection("evidence_records")
        db["evidence_records"].create_index([("case_id", pymongo.ASCENDING)])
        db["evidence_records"].create_index([("timestamp", pymongo.ASCENDING)])

    return db.list_collection_names()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_mongodb_storage.py -v`  
Expected: PASS

---

### Task 2: Repository Layer & Rolling Stats Aggregation Pipeline

**Files:**
- Create: `src/storage/repository.py`
- Test: `tests/test_mongodb_storage.py`

- [ ] **Step 1: Write failing test for repository ingest, case persistence, and $setWindowFields pipeline**

```python
# append to tests/test_mongodb_storage.py
from datetime import datetime, timezone
from src.storage.repository import CompressorGuardRepository

def test_repository_telemetry_and_case_lifecycle():
    repo = CompressorGuardRepository()
    
    # Ingest telemetry points
    t1 = datetime(2020, 6, 5, 9, 50, 0, tzinfo=timezone.utc)
    point = {
        "timestamp": t1,
        "metadata": {"asset_id": "APU-COMP-01", "train_id": "TRAIN-302"},
        "dv_pressure_bar": 2.18,
        "oil_temp_c": 74.97,
        "motor_current_a": 6.8,
        "regime": "LOADED"
    }
    repo.insert_measurement(point)
    
    # Save operational case
    case_doc = {
        "case_id": "CASE-20200605-01",
        "asset_id": "APU-COMP-01",
        "phase": "CONFIRMED",
        "severity": "CRITICAL",
        "started_at": t1.isoformat(),
        "summary": "Severe discharge valve leakage confirmed",
        "lead_time_minutes": 2032
    }
    repo.save_case(case_doc)
    
    retrieved = repo.get_case("CASE-20200605-01")
    assert retrieved is not None
    assert retrieved["case_id"] == "CASE-20200605-01"
    assert retrieved["phase"] == "CONFIRMED"

def test_set_window_fields_pipeline():
    repo = CompressorGuardRepository()
    stats = repo.get_rolling_stats("APU-COMP-01", window_seconds=600)
    assert isinstance(stats, list)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_mongodb_storage.py::test_repository_telemetry_and_case_lifecycle -v`  
Expected: FAIL with `ImportError: cannot import name 'CompressorGuardRepository'`

- [ ] **Step 3: Implement `src/storage/repository.py`**

```python
# src/storage/repository.py
from typing import Optional, Dict, Any, List
from src.storage.mongo_client import get_mongo_db

class CompressorGuardRepository:
    def __init__(self, db=None):
        self.db = db if db is not None else get_mongo_db()

    def insert_measurement(self, point_dict: Dict[str, Any]) -> str:
        res = self.db["measurements"].insert_one(point_dict)
        return str(res.inserted_id)

    def insert_measurements_batch(self, points: List[Dict[str, Any]]) -> int:
        if not points:
            return 0
        res = self.db["measurements"].insert_many(points)
        return len(res.inserted_ids)

    def save_case(self, case_dict: Dict[str, Any]) -> str:
        res = self.db["operational_cases"].update_one(
            {"case_id": case_dict["case_id"]},
            {"$set": case_dict},
            upsert=True
        )
        return case_dict["case_id"]

    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        return self.db["operational_cases"].find_one({"case_id": case_id}, {"_id": 0})

    def get_active_case_for_asset(self, asset_id: str) -> Optional[Dict[str, Any]]:
        return self.db["operational_cases"].find_one(
            {"asset_id": asset_id, "phase": {"$ne": "CLOSED"}},
            {"_id": 0}
        )

    def save_evidence_pack(self, case_id: str, evidence_doc: Dict[str, Any]) -> str:
        evidence_doc["case_id"] = case_id
        res = self.db["evidence_records"].insert_one(evidence_doc)
        return str(res.inserted_id)

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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_mongodb_storage.py -v`  
Expected: PASS

---

### Task 3: Ingest Historical Golden Path Telemetry into MongoDB

**Files:**
- Create: `scripts/ingest_golden_path_to_mongo.py`
- Test: `tests/test_mongodb_storage.py`

- [ ] **Step 1: Write ingestion script from ReplayEngine to MongoDB**

Script loads Onset (`09:50`), Corroborated (`10:15`), LPS milestone (`19:42`), and Recovery (`16:05+`) slices and bulk writes into `measurements` and `operational_cases`.

- [ ] **Step 2: Run ingestion script and verify document count**

Run: `python scripts/ingest_golden_path_to_mongo.py`  
Expected: Success with documents populated in `measurements` and `operational_cases`.

---

### Task 4: Generate Screen Specifications (`screen/*.md`)

**Files:**
- Create: `screen/README.md`
- Create: `screen/01_OPERATIONS_NAV_AND_FLEET_VIEW.md`
- Create: `screen/02_ACTIVE_CASES_LIST.md`
- Create: `screen/03_CASE_WORKSPACE_WHAT_CHANGED.md`
- Create: `screen/04_CASE_WORKSPACE_WHY_EVIDENCE.md`
- Create: `screen/05_CASE_WORKSPACE_WHAT_DID_WE_DO.md`
- Create: `screen/06_CASE_WORKSPACE_DID_IT_WORK.md`
- Create: `screen/07_CONFIGURABLE_VALUE_MODEL_DRAWER.md`

- [ ] **Step 1: Tạo thư mục `screen/`**
- [ ] **Step 2: Viết đặc tả từng màn hình chi tiết, trực quan ASCII Wireframes, data binding contracts, và operator cognitive progressions.**

---

### Task 5: Full Regression Testing & Attestation

**Files:**
- Test: `tests/test_api_vertical_slice.py`
- Test: `tests/test_deterministic_replay.py`
- Test: `tests/test_mongodb_storage.py`

- [ ] **Step 1: Run complete test suite**

Run: `python -m pytest tests/ -v`  
Expected: All tests pass.
