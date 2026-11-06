"""
RailOps VN / CompressorGuard — Independent Telemetry Stream Producer (CLI)
==========================================================================

This is the *producer* half of the decoupled producer-consumer mechanism
documented in docs/ARCHITECTURE.md §"Luồng sinh dữ liệu" and
docs/superpowers/specs/2026-10-11-prod-ready-ux-and-mechanism-design.md §2.0.

    "The Dashboard Does Not Trigger Telemetry."

The web console never pulls a data point. Telemetry is advanced by this CLI
process, or by the server-side background worker inside src/api/app.py.

Two modes
---------
local   (default) Drive the real ReplayEngine -> Detectors -> Fusion -> Decision
                  -> Recovery pipeline in this process, persist every point to
                  MongoDB, and optionally publish each frame on an MQTT topic
                  exactly as an onboard edge gateway would.

remote  Send *simulation control plane* commands (play / pause / speed / jump /
                  scenario / reset) to an already-running API server. It steers
                  the pace of the producer; it never fetches telemetry for the UI.

Examples
--------
    # Stream Failure #3 for 4 simulated hours at 200x, persist to MongoDB
    python scripts/stream_telemetry.py --scenario failure_3 --speed 200 --hours 4

    # Emit like an edge gateway on a real broker
    set MQTT_BROKER=tcp://localhost:1883
    python scripts/stream_telemetry.py --scenario failure_3 --speed 300 --hours 6

    # Jump straight to the confirmed-onset milestone, then keep streaming
    python scripts/stream_telemetry.py --jump onset --speed 100

    # Operate a running server's stream without touching the browser
    python scripts/stream_telemetry.py --mode remote --base-url http://localhost:8000 --play --speed 300
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8")
        except Exception:
            pass

SENSOR_FIELDS = (
    "tp2_bar", "tp3_bar", "h1_bar", "dv_pressure_bar", "reservoirs_bar",
    "oil_temp_c", "motor_current_a", "comp_val", "dv_electric", "towers_val",
    "mpg_val", "lps_active", "pressure_switch", "oil_level_low", "caudal_impulses",
)


def _to_dt(value) -> datetime:
    """Coerce a scenario/event timestamp (str or datetime) to an aware UTC datetime."""
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class EdgePublisher:
    """MQTT publisher mirroring an onboard edge gateway.

    Degrades to a no-op when no broker is configured, so the producer still
    runs in a bare checkout. Store-and-forward is represented by a bounded
    local buffer: frames are retained while the link is down and flushed on
    reconnect, rather than being dropped.
    """

    def __init__(self, broker_url: str | None, fleet: str, asset: str, buffer_size: int = 512):
        self.topic = f"railops/{fleet}/{asset}/telemetry"
        self.buffer: list[dict] = []
        self.buffer_size = buffer_size
        self.published = 0
        self.client = None
        self._warned = False

        if not broker_url:
            return
        try:
            import paho.mqtt.client as mqtt  # type: ignore
        except ImportError:
            print(f"[EDGE] MQTT_BROKER set but paho-mqtt is not installed; "
                  f"buffering {buffer_size} frames locally instead.")
            return

        host, _, port = broker_url.replace("tcp://", "").partition(":")
        try:
            client = mqtt.Client()
            client.connect(host, int(port or 1883), keepalive=30)
            client.loop_start()
            self.client = client
            print(f"[EDGE] Connected to MQTT broker {host}:{port or 1883} -> {self.topic}")
        except Exception as exc:  # broker down: keep buffering
            print(f"[EDGE] Broker unavailable ({exc}); using store-and-forward buffer.")

    def publish(self, frame: dict) -> None:
        self.buffer.append(frame)
        if len(self.buffer) > self.buffer_size:
            del self.buffer[: len(self.buffer) - self.buffer_size]
        if self.client is None:
            return
        try:
            for pending in self.buffer:
                self.client.publish(self.topic, json.dumps(pending), qos=1)
                self.published += 1
            self.buffer.clear()
        except Exception as exc:
            if not self._warned:
                print(f"[EDGE] Publish failed ({exc}); retaining frames for resend.")
                self._warned = True

    def close(self) -> None:
        if self.client is not None:
            try:
                self.client.loop_stop()
                self.client.disconnect()
            except Exception:
                pass


def _frame_from(point) -> dict:
    """Serialise a TelemetryPoint with BOTH clocks preserved."""
    event_time = point.timestamp
    if event_time.tzinfo is None:
        event_time = event_time.replace(tzinfo=timezone.utc)
    frame = {
        "asset_id": point.asset_id,
        "event_time": event_time.isoformat(),          # physical clock, never rewritten
        "simulation_time": _utcnow().isoformat(),      # wall clock of this producer
        "regime": point.regime.value if getattr(point, "regime", None) is not None else None,
    }
    for name in SENSOR_FIELDS:
        value = getattr(point, name, None)
        if value is not None:
            frame[name] = value
    return frame


def _sleep_for(manager, fallback: float = 0.02) -> float:
    runner = getattr(manager, "runner", None)
    if runner is None:
        return fallback
    for name in ("get_sleep_interval_seconds", "calculate_sleep_interval"):
        fn = getattr(runner, name, None)
        if callable(fn):
            try:
                return max(0.0, float(fn()))
            except TypeError:
                pass
    return fallback


def run_local(args: argparse.Namespace) -> int:
    from src.engine.lifecycle import IncidentLifecycleManager
    from src.storage.repository import CompressorGuardRepository

    print("=" * 78)
    print("  RAILOPS VN — TELEMETRY PRODUCER (local mode)")
    print("  Dashboard does not trigger telemetry. This process does.")
    print("=" * 78)

    repo = CompressorGuardRepository()
    manager = IncidentLifecycleManager(repository=repo)
    manager.initialize()

    if args.scenario:
        manager.switch_scenario(args.scenario)
    if args.jump:
        manager.jump_to_milestone(args.jump)
        print(f"[PRODUCER] Seeded to milestone '{args.jump}'.")

    manager.set_simulation_speed(args.speed)
    manager.play()

    publisher = EdgePublisher(os.environ.get("MQTT_BROKER"), "metro-line-1", "APU-COMP-01")

    batch: list[dict] = []
    started = time.monotonic()
    frames = 0
    last_report = started
    transitions = 0

    print(f"[PRODUCER] speed={args.speed}x  budget={args.hours} simulated hours  "
          f"scenario={args.scenario or 'active'}")
    print(f"[PRODUCER] persistence={'MongoDB' if os.environ.get('MONGODB_URI') else 'in-memory repository'}")

    budget_end = _to_dt(manager.scenario.stream_start) + timedelta(
        hours=args.hours if args.hours is not None else 0
    )

    try:
        while True:
            previous_state = manager.lifecycle_state
            point = manager.tick()
            if point is None:
                print("[PRODUCER] Stream exhausted (end of scenario window).")
                break

            frames += 1
            frame = _frame_from(point)
            if args.hours is not None and _to_dt(frame["event_time"]) >= budget_end:
                print("[PRODUCER] Simulated budget exhausted; stopping.")
                break
            batch.append(frame)
            publisher.publish(frame)

            if manager.lifecycle_state != previous_state:
                transitions += 1
                print(f"[CASE] {previous_state.value} -> {manager.lifecycle_state.value} @ {frame['event_time']}")

            if len(batch) >= args.batch:
                repo.insert_measurements_batch(batch)
                batch = []

            if time.monotonic() - last_report >= args.report_every:
                status = manager.get_simulation_status()
                inc = manager.get_incident_payload()
                print(f"[STREAM] event={frame['event_time']}  regime={frame.get('regime')}  "
                      f"dv={frame.get('dv_pressure_bar')}  oil={frame.get('oil_temp_c')}  "
                      f"state={manager.lifecycle_state.value}  ack={inc.get('acknowledged')}  "
                      f"points={status.get('total_points_emitted', frames)}")
                last_report = time.monotonic()

            time.sleep(_sleep_for(manager))

    except KeyboardInterrupt:
        print("\n[PRODUCER] Interrupted by operator.")
    finally:
        if batch:
            repo.insert_measurements_batch(batch)
        publisher.close()

    elapsed = time.monotonic() - started
    print("-" * 78)
    print(f"[DONE] frames_produced={frames}  state_transitions={transitions}  "
          f"wall_seconds={elapsed:.1f}  mqtt_published={publisher.published}  "
          f"mqtt_buffered={len(publisher.buffer)}")
    print("[DONE] Sensor values above come from MetroPT-3 historical rows. "
          "No value is synthesised by this program.")
    return 0


def run_remote(args: argparse.Namespace) -> int:
    import urllib.error
    import urllib.request

    base = args.base_url.rstrip("/")
    calls: list[tuple[str, str, dict | None]] = []

    if args.reset:
        calls.append(("POST", "/demo/reset", {"milestone": args.jump} if args.jump else {}))
    if args.scenario:
        calls.append(("POST", "/api/operations/scenario", {"scenario_id": args.scenario}))
    if args.jump and not args.reset:
        calls.append(("POST", "/demo/jump", {"milestone": args.jump}))
    if args.speed is not None:
        calls.append(("POST", "/demo/speed", {"speed_multiplier": args.speed}))
    if args.pause:
        calls.append(("POST", "/demo/pause", None))
    if args.play:
        calls.append(("POST", "/demo/play", None))

    print("=" * 78)
    print(f"  RAILOPS VN — SIMULATION CONTROL HARNESS (remote mode) -> {base}")
    print("  Steers the producer's pace. Does not fetch telemetry for the UI.")
    print("=" * 78)

    rc = 0
    for method, path, body in calls:
        url = base + path
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(
            url, data=data,
            headers={"Content-Type": "application/json"},
            method=method,
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = resp.read().decode("utf-8", "replace")
                print(f"[OK]   {method} {path} -> {resp.status} {payload[:160]}")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:200]
            print(f"[FAIL] {method} {path} -> HTTP {exc.code} {detail}")
            rc = 1
        except Exception as exc:
            print(f"[FAIL] {method} {path} -> {exc}")
            rc = 1

    try:
        with urllib.request.urlopen(f"{base}/demo/status", timeout=60) as resp:
            print(f"[STATUS] {resp.read().decode('utf-8', 'replace')}")
    except Exception as exc:
        print(f"[STATUS] unavailable: {exc}")
        rc = 1
    return rc


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Independent dual-clock telemetry producer for RailOps VN / CompressorGuard.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--mode", choices=["local", "remote"], default="local")
    parser.add_argument("--scenario", help="failure_3 | failure_1 | failure_4 | healthy_baseline")
    parser.add_argument("--speed", type=float, default=100.0, help="simulation speed multiplier (1x..300x)")
    parser.add_argument("--hours", type=float, default=2.0, help="simulated hours to stream (local mode)")
    parser.add_argument("--jump", help="seed to a named milestone (e.g. onset, confirmed, post_maintenance)")
    parser.add_argument("--batch", type=int, default=500, help="measurement flush batch size")
    parser.add_argument("--report-every", type=float, default=5.0, dest="report_every",
                        help="seconds of wall time between progress lines")

    parser.add_argument("--base-url", default="http://localhost:8000", dest="base_url")
    parser.add_argument("--play", action="store_true")
    parser.add_argument("--pause", action="store_true")
    parser.add_argument("--reset", action="store_true")

    args = parser.parse_args()

    if args.mode == "remote":
        if not (args.play or args.pause or args.reset or args.jump or args.scenario
                or args.speed != 100.0):
            parser.error("remote mode needs at least one of --play/--pause/--reset/--jump/--scenario/--speed")
        return run_remote(args)
    return run_local(args)


if __name__ == "__main__":
    raise SystemExit(main())
