#!/usr/bin/env python3
"""
Cut a committable, still-100%-real slice out of MetroPT3(AirCompressor).csv.

Why this exists: the original CSV is ~218 MB and is not in git (GitHub would reject
it), so a clean clone had no telemetry at all and nothing in the product could run.
This script keeps the rows the platform actually reasons over and drops the rest:

  * the Isolation Forest baseline month (Feb 2020) — optionally even-strided,
  * every scenario window in src/domain/scenarios.py, at full 10 s resolution.

No row is synthesised, interpolated or reordered. Striding only *drops* whole
original rows; the survivors are byte-identical to the source file.

    python scripts/build_demo_slice.py --stride 3
"""

import argparse
import sys
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

from src.domain.scenarios import (
    FAILURE_1_SCENARIO,
    FAILURE_3_SCENARIO,
    FAILURE_4_SCENARIO,
    HEALTHY_SCENARIO,
)
from src.engine.replay import FULL_CSV_PATH

OUT_PATH = REPO_ROOT / "dataset" / "MetroPT3-demo-slice.csv"
ALL_SCENARIOS = [FAILURE_3_SCENARIO, FAILURE_1_SCENARIO, FAILURE_4_SCENARIO, HEALTHY_SCENARIO]
BASELINE_START = "2020-02-01"
BASELINE_END = "2020-03-01"


def scenario_windows() -> list[tuple[str, str, str]]:
    """Every timestamp the product reads, including milestones and recovery tails."""
    windows = []
    for scenario in ALL_SCENARIOS:
        anchors = [scenario.stream_start, scenario.stream_end,
                   scenario.lps_milestone or scenario.stream_start]
        anchors += list(scenario.milestones.values())
        if getattr(scenario, "recovery_start", None):
            anchors += [scenario.recovery_start, scenario.recovery_end]
        lo, hi = min(anchors), max(anchors)
        windows.append((lo, hi, scenario.scenario_id))
    return windows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stride", type=int, default=3,
                        help="keep 1 of every N baseline-month rows (1 = keep all)")
    parser.add_argument("--out", type=Path, default=OUT_PATH)
    args = parser.parse_args()

    if not FULL_CSV_PATH.exists():
        print(f"Source CSV missing at {FULL_CSV_PATH}")
        return 2

    df = pd.read_csv(FULL_CSV_PATH)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp").reset_index(drop=True)
    print(f"Source: {len(df):,} rows, {df.timestamp.min()} → {df.timestamp.max()}")

    in_baseline = (df["timestamp"] >= BASELINE_START) & (df["timestamp"] < BASELINE_END)
    scenario_mask = pd.Series(False, index=df.index)
    for lo, hi, name in scenario_windows():
        hit = (df["timestamp"] >= lo) & (df["timestamp"] <= hi)
        print(f"  window {name}: {lo} → {hi} = {int(hit.sum()):,} rows")
        scenario_mask |= hit

    # The baseline month is only used to fit a density model, so thinning it is a
    # size decision, not a data-fabrication decision. Rows any scenario streams stay
    # at the original 10 s resolution, otherwise replay spacing would change.
    keep = scenario_mask | (in_baseline & ~scenario_mask & (df.index % args.stride == 0))
    slice_df = df[keep].copy()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    slice_df.to_csv(args.out, index=False)
    size_mb = args.out.stat().st_size / 1024 / 1024
    print(f"\nWrote {len(slice_df):,} rows ({size_mb:.1f} MB) to {args.out.name} "
          f"(baseline stride=1/{args.stride})")
    print(f"Coverage: {slice_df.timestamp.min()} → {slice_df.timestamp.max()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
