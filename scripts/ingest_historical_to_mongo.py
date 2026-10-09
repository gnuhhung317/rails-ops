#!/usr/bin/env python3
"""
Ingest MetroPT-3 Failure #3 historical telemetry slice into MongoDB Time Series collection.
"""
import argparse
import sys
from pathlib import Path
from datetime import timezone

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.engine.replay import ReplayEngine, DEFAULT_CSV_PATH
from src.storage.repository import CompressorGuardRepository


def ingest(limit: int = 500, csv_path: str = str(DEFAULT_CSV_PATH)) -> int:
    print(f"Connecting to MongoDB and initializing collections...")
    repo = CompressorGuardRepository()
    
    print(f"Reading telemetry stream from {csv_path}...")
    replay = ReplayEngine(csv_path)
    stream = replay.stream_telemetry("2020-06-05 09:40:00", "2020-06-05 10:30:00")
    
    batch = []
    count = 0
    for pt in stream:
        ts = pt.timestamp
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        batch.append({
            "timestamp": ts,
            "metadata": {
                "asset_id": pt.asset_id,
                "train_id": "TRAIN-302",
                "fleet_id": "FLEET-METRO-01",
            },
            "dv_pressure_bar": round(pt.dv_pressure_bar, 4),
            "oil_temp_c": round(pt.oil_temp_c, 2),
            "motor_current_a": round(pt.motor_current_a, 2),
            "tp3_bar": round(pt.tp3_bar, 4),
            "regime": pt.regime.value if pt.regime else "UNKNOWN",
        })
        count += 1
        if len(batch) >= 100:
            repo.insert_measurements_batch(batch)
            print(f"Ingested {count} points...")
            batch = []
        if limit > 0 and count >= limit:
            break

    if batch:
        repo.insert_measurements_batch(batch)
        print(f"Ingested {count} points total.")

    print(f"Successfully ingested {count} telemetry documents into MongoDB measurements collection.")
    return count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest MetroPT-3 telemetry to MongoDB")
    parser.add_argument("--limit", type=int, default=500, help="Max records to ingest (0 for all)")
    args = parser.parse_args()
    ingest(limit=args.limit)
