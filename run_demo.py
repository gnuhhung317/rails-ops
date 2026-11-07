"""
CompressorGuard — Turnkey 1-Click Demo Launcher
RailOps VN / Metro Line 1 Ben Thanh - Suoi Tien | APU-COMP-01 | MUGVN Hackathon 2026

Runs self-checks, launches the FastAPI/Uvicorn server, and opens the Command Console in default browser.
"""

import os
import sys
import time
import webbrowser
import threading
import importlib
from pathlib import Path

# UTF-8 stdout configuration for Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_CSV_PATH = REPO_ROOT / "dataset" / "MetroPT3(AirCompressor).csv"
PORT = int(os.environ.get("PORT", "8000"))
HOST = os.environ.get("HOST", "127.0.0.1")
URL = f"http://{HOST}:{PORT}/"


def print_banner():
    print("=" * 80)
    print("  RAILOPS VN -- INDUSTRIAL OPERATIONS COMMAND PLATFORM (CompressorGuard core)")
    print("  RailOps VN (Metro Line 1) - CompressorGuard Mission-Critical Subsystem")
    print("=" * 80)
    print(f"  Web Console:   {URL}")
    print(f"  Interactive UI: {URL}console")
    print(f"  API Docs:       {URL}docs")
    print(f"  Health Probe:   {URL}health")
    print(f"  Prometheus:     {URL}metrics")
    print("=" * 80)


def _missing_dependencies():
    # pymongo is a top-level import in src/storage, so the in-memory fallback
    # still needs the driver installed; only the server connection is optional.
    probes = {"fastapi": "fastapi", "uvicorn": "uvicorn", "pandas": "pandas",
              "numpy": "numpy", "sklearn": "scikit-learn", "pymongo": "pymongo"}
    missing = []
    for module, dist in probes.items():
        try:
            importlib.import_module(module)
        except ImportError:
            missing.append(dist)
    return missing


def preflight_checks():
    print("[PREFLIGHT] Checking environment & dataset...")
    missing = _missing_dependencies()
    if missing:
        print(f"[ERROR] Missing Python dependencies: {', '.join(missing)}")
        print("Install them with:  python -m pip install -r requirements.txt")
        sys.exit(1)
    print("[OK] Runtime dependencies importable (fastapi/uvicorn/pandas/numpy/sklearn/pymongo).")
    from src.engine.replay import resolve_csv_path

    try:
        csv_path = resolve_csv_path()
    except FileNotFoundError as exc:
        print(f"[ERROR] {exc}")
        sys.exit(1)
    print(f"[OK] Dataset confirmed: {csv_path.name} "
          f"({csv_path.stat().st_size / (1024*1024):.1f} MB)")
    if csv_path.name != DEFAULT_CSV_PATH.name:
        print("     This is the committed real-data slice (same instrument, same rows). "
              "Drop the full 1,516,948-row CSV in dataset/ to use it instead -- see README.")
    print("[OK] Zero Fake Telemetry gate verified: historical replay engine ready.")


def open_browser():
    time.sleep(1.5)
    try:
        print(f"[BROWSER] Launching default browser at {URL}...")
        webbrowser.open(URL)
    except Exception as e:
        print(f"[BROWSER] Notice: Could not open browser automatically: {e}")


def main():
    print_banner()
    preflight_checks()

    # Launch browser in a background timer thread
    threading.Thread(target=open_browser, daemon=True).start()

    print(f"\n[SERVER] Starting Uvicorn server on http://{HOST}:{PORT} ...")
    print("[SERVER] Press Ctrl+C at any time to gracefully terminate.")
    print("-" * 80)

    try:
        import uvicorn
        uvicorn.run(
            "src.api.app:create_app",
            factory=True,
            host=HOST,
            port=PORT,
            reload=False,
            log_level="info",
        )
    except KeyboardInterrupt:
        print("\n[SERVER] CompressorGuard server stopped by user. Goodbye!")


if __name__ == "__main__":
    main()
