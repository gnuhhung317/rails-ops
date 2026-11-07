#!/usr/bin/env python3
"""
MongoDB leg — real-server proof for MUGVN Hackathon 2026.

Without `MONGODB_URI` the app runs on `InMemoryCollection`, which *emulates* the
aggregation stages. That emulation is not the product: it hardcodes a 60-document
window and ignores the `range`/`unit` options the real pipeline passes. This script
refuses to run unless it is talking to a genuine `mongod`, then checks the four
things the in-memory path cannot prove:

  1. Structure  — `measurements` is a real Time Series collection and it bucketed.
  2. Invariants — no TTL on historical `timestamp`; 7-day TTL on `ingested_at`.
  3. Pipeline 1 — `$setWindowFields` output equals an independent pandas recompute,
                  and the drift of the in-memory emulation is measured, not assumed.
  4. Pipeline 2 — `$facet` + `$group` duty-cycle analytics equal a pandas recompute.

Run it against a throwaway server:

    docker compose up -d mongo
    MONGODB_URI=mongodb://localhost:27017 MONGODB_DB_NAME=compressorguard_verify \\
        python scripts/verify_mongodb_timeseries.py

Exit 0 = every check passed on a real server. Exit 2 = no real server reachable
(so nothing below was proven). Exit 1 = a real server was reached and a check failed.
"""

import os
import statistics
import sys
from datetime import timedelta, timezone
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pandas as pd
import pymongo

from src.engine.replay import ReplayEngine, resolve_csv_path
from src.storage.mongo_client import DATABASE_NAME, get_mongo_db, init_mongodb_schema
from src.storage.mongo_client import is_mongo_available
from src.storage.repository import CompressorGuardRepository

# Failure #3 window: the dryer-discharge leak the demo runs on.
WINDOW_START = "2020-06-05 09:40:00"
WINDOW_END = "2020-06-05 11:40:00"
WINDOW_SECONDS = 600
ASSET_ID = "APU-COMP-01"

_failures: list[str] = []


def check(label: str, ok: bool, detail: str) -> None:
    print(f"  [{'PASS' if ok else 'FAIL'}] {label} — {detail}")
    if not ok:
        _failures.append(f"{label}: {detail}")


def require_real_server() -> pymongo.MongoClient:
    print("\n[MONGO 0] Refusing the in-memory path...")
    if not is_mongo_available():
        print(f"  No `mongod` reachable at {os.getenv('MONGODB_URI', 'mongodb://localhost:27017')}.")
        print("  Nothing below was proven. Start one with `docker compose up -d mongo`.")
        sys.exit(2)
    client = pymongo.MongoClient(
        os.getenv("MONGODB_URI", "mongodb://localhost:27017"), serverSelectionTimeoutMS=3000
    )
    info = client.server_info()
    db = client[DATABASE_NAME]
    print(f"  Real server: mongod {info['version']} on {db.name} "
          f"(host={info.get('host', '?')},setName={info.get('setName', 'standalone')}).")
    return client


def ingest_slice() -> pd.DataFrame:
    """Load the failure-window telemetry from the real CSV, through the repo's own writer."""
    csv_path = resolve_csv_path()
    print(f"  Data source: {csv_path.name}")
    replay = ReplayEngine(str(csv_path))
    docs = []
    for pt in replay.stream_telemetry(WINDOW_START, WINDOW_END):
        ts = pt.timestamp
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        docs.append({
            "timestamp": ts,
            "metadata": {"asset_id": pt.asset_id, "train_id": "TRAIN-302", "fleet_id": "FLEET-METRO-01"},
            "dv_pressure_bar": round(pt.dv_pressure_bar, 4),
            "oil_temp_c": round(pt.oil_temp_c, 2),
            "motor_current_a": round(pt.motor_current_a, 2),
            "tp3_bar": round(pt.tp3_bar, 4),
            "regime": pt.regime.value if pt.regime else "UNKNOWN",
        })
    df = pd.DataFrame([{k: v for k, v in d.items() if k != "metadata"} | {"asset_id": ASSET_ID} for d in docs])
    repo = CompressorGuardRepository()
    repo.db["measurements"].delete_many({})
    inserted = repo.insert_measurements_batch(docs)
    print(f"\n[MONGO 1] Ingested {inserted} real MetroPT-3 rows into {db_collection()}.measurements")
    return df


def db_collection() -> str:
    return f"{DATABASE_NAME}.measurements"


def check_structure(client: pymongo.MongoClient) -> None:
    print("\n[MONGO 2] Time Series structure")
    db = client[DATABASE_NAME]
    spec = next((c for c in db.list_collections(filter={"name": "measurements"})), None)
    opts = (spec or {}).get("options", {})
    ts = opts.get("timeseries", {})
    check("measurements is a Time Series collection", spec is not None and spec.get("type") == "timeseries",
          f"type={(spec or {}).get('type')}")
    check("timeField / metaField wired as designed",
          ts.get("timeField") == "timestamp" and ts.get("metaField") == "metadata",
          f"timeField={ts.get('timeField')} metaField={ts.get('metaField')} granularity={ts.get('granularity')}")

    stats = db.command("collstats", "measurements")
    buckets = int(stats.get("bucketCount") or 0)
    docs = int(stats.get("count") or 0)
    check("server actually bucketed the data", buckets > 0,
          f"{docs} docs → {buckets} buckets ({docs / max(buckets, 1):.1f} docs/bucket), "
          f"storage={stats.get('storageSize', 0) / 1024:.0f} KiB, "
          f"rawBson={stats.get('totalBytesForBuckets', 0) / 1024:.0f} KiB")

    validation = db.command("validate", "measurements")
    check("collection validates", bool(validation.get("valid")), f"valid={validation.get('valid')}")


def check_retention_invariant(client: pymongo.MongoClient) -> None:
    print("\n[MONGO 3] Dual-clock retention invariant")
    db = client[DATABASE_NAME]
    ts_indexes = [i for i in db["measurements"].index_information().values() if "expireAfterSeconds" in i]
    check("no TTL on historical `timestamp` (2020 rows survive)", ts_indexes == [],
          f"{len(ts_indexes)} TTL index(es) on measurements")
    oldest = db["measurements"].find_one(sort=[("timestamp", 1)])
    newest = db["measurements"].find_one(sort=[("timestamp", -1)])
    check("earliest stored event_time is the historical 2020 window",
          oldest is not None and oldest["timestamp"].year == 2020,
          f"{oldest['timestamp'] if oldest else 'n/a'} .. {newest['timestamp'] if newest else 'n/a'}")
    signals = db["anomaly_signals"].index_information()
    ttl = [i for i in signals.values() if i.get("expireAfterSeconds") == 7 * 86400]
    check("7-day wall-clock TTL lives on anomaly_signals.ingested_at", len(ttl) == 1,
          f"{len(ttl)} index(es) with expireAfterSeconds=604800")


def check_window_fields(repo: CompressorGuardRepository, df: pd.DataFrame) -> None:
    print(f"\n[MONGO 4] Pipeline #1 — $setWindowFields over a {WINDOW_SECONDS}s sliding range")
    rows = repo.get_rolling_stats(ASSET_ID, window_seconds=WINDOW_SECONDS, limit=200)
    check("pipeline returned rows from the server", len(rows) == 200, f"{len(rows)} rows")
    if not rows:
        return

    frame = df.sort_values("timestamp").reset_index(drop=True)
    expected = []
    for i, row in frame.iterrows():
        lo = row["timestamp"] - timedelta(seconds=WINDOW_SECONDS)
        win = frame[(frame["timestamp"] >= lo) & (frame["timestamp"] <= row["timestamp"])]
        expected.append({
            "timestamp": row["timestamp"],
            "avg": win["dv_pressure_bar"].mean(),
            "std": win["dv_pressure_bar"].std(ddof=1) if len(win) > 1 else float("nan"),
            "oil": win["oil_temp_c"].mean(),
            "n": len(win),
        })
    by_ts = {e["timestamp"]: e for e in expected}

    avg_err = std_err = 0.0
    sizes = []
    missing = 0
    for r in rows:
        ts = r["timestamp"]
        ts = ts.replace(tzinfo=timezone.utc) if ts.tzinfo is None else ts
        exp = by_ts.get(ts)
        if exp is None:
            missing += 1
            continue
        avg_err = max(avg_err, abs(float(r["rolling_avg_dv"]) - float(exp["avg"])))
        if not (pd.isna(exp["std"]) or r.get("rolling_std_dv") is None):
            std_err = max(std_err, abs(float(r["rolling_std_dv"]) - float(exp["std"])))
        sizes.append(exp["n"])

    check("rolling mean matches an independent pandas recompute", avg_err < 1e-4,
          f"max |Δavg| = {avg_err:.2e}")
    check("sample std-dev matches ($stdDevSamp, not population)", std_err < 1e-4,
          f"max |Δstd| = {std_err:.2e}")
    check("every server row is matched to a CSV timestamp", missing == 0, f"{missing} unmatched")

    # What the in-memory emulation would have reported instead.
    fallback = frame.tail(len(frame))["dv_pressure_bar"].rolling(window=60, min_periods=1)
    real = pd.Series([e["avg"] for e in expected])
    drift = float((fallback.reset_index(drop=True) - real).abs().max())
    gaps = frame["timestamp"].diff().dropna().dt.total_seconds()
    print(f"  [INFO] sample spacing: min {gaps.min():.0f}s / median {gaps.median():.0f}s / max {gaps.max():.0f}s")
    print(f"  [INFO] window size seen by the server: min {min(sizes)} / median "
          f"{int(statistics.median(sizes))} / max {max(sizes)} samples")
    print(f"  [INFO] in-memory emulation (fixed 60 docs) vs real range window: "
          f"max |Δ| = {drift:.4f} bar → the fallback is an approximation, the server is the product.")


def check_facet(repo: CompressorGuardRepository, df: pd.DataFrame) -> None:
    print("\n[MONGO 5] Pipeline #2 — $facet + $group regime / duty-cycle profiler")
    analytics = repo.get_regime_duty_cycle_analytics(ASSET_ID)
    total = len(df)
    loaded = int((df["regime"] == "LOADED").sum())
    expected_duty = round(loaded / total * 100.0, 2)

    check("server saw every ingested row",
          analytics["total_samples_analyzed"] == total,
          f"{analytics['total_samples_analyzed']} vs {total} CSV rows")
    check("LOADED duty cycle matches pandas", analytics["loaded_duty_cycle_pct"] == expected_duty,
          f"{analytics['loaded_duty_cycle_pct']}% vs {expected_duty}%")
    check("peak dv_pressure matches pandas",
          abs(analytics["peak_dv_pressure_bar"] - round(float(df["dv_pressure_bar"].max()), 4)) < 1e-4,
          f"{analytics['peak_dv_pressure_bar']} vs {round(float(df['dv_pressure_bar'].max()), 4)}")
    check("regime breakdown came back from the server", len(analytics["regime_breakdown"]) > 0,
          ", ".join(f"{r['regime']}={r['sample_count']}" for r in analytics["regime_breakdown"]))


def check_query_planner(client: pymongo.MongoClient) -> None:
    print("\n[MONGO 6] The server executes the pipeline (not the emulator)")
    db = client[DATABASE_NAME]
    plan = db.command(
        "explain",
        {
            "aggregate": "measurements",
            "pipeline": [
                {"$match": {"metadata.asset_id": ASSET_ID}},
                {"$setWindowFields": {
                    "partitionBy": "$metadata.asset_id",
                    "sortBy": {"timestamp": 1},
                    "output": {"rolling_avg_dv": {"$avg": "$dv_pressure_bar",
                                                  "window": {"range": [-WINDOW_SECONDS, 0], "unit": "second"}}},
                }},
            ],
            "cursor": {},
        },
        verbosity="executionStats",
    )
    stages = str(plan).lower()
    ok = "setwindowfields" in stages or "windowfunction" in stages or "timeseries" in stages
    check("explain plan contains a real window/Time Series stage", ok,
          f"server={plan.get('serverInfo', {}).get('version', '?')}")


def main() -> int:
    print("=" * 78)
    print("CompressorGuard — MongoDB Time Series verification against a REAL server")
    print("=" * 78)

    client = require_real_server()
    init_mongodb_schema(get_mongo_db())
    df = ingest_slice()
    repo = CompressorGuardRepository()

    check_structure(client)
    check_retention_invariant(client)
    check_window_fields(repo, df)
    check_facet(repo, df)
    check_query_planner(client)

    client.close()
    print("\n" + "=" * 78)
    if _failures:
        print(f"RESULT: FAIL — {len(_failures)} check(s) failed on a real server")
        for f in _failures:
            print(f"  - {f}")
        return 1
    print(f"RESULT: PASS — Time Series + $setWindowFields + $facet proven on a real mongod "
          f"{client.server_info()['version']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
