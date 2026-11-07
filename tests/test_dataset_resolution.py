"""
The clean-clone guarantee: a repo checkout must contain telemetry real enough to run.

A clean clone used to contain no CSV at all (the 208 MB original is gitignored), so
`git clone && pip install && python run_demo.py` could not demo anything. These tests
fail if that regresses. They never read the 208 MB file — only the committed slice and
path-resolution logic.
"""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.engine import replay


def test_committed_slice_exists_and_is_substantial():
    assert replay.SLICE_CSV_PATH.exists(), (
        "dataset/MetroPT3-demo-slice.csv is what makes a clean clone runnable — "
        "regenerate with python scripts/build_demo_slice.py --stride 1"
    )
    assert replay.SLICE_CSV_PATH.stat().st_size > 10 * 1024 * 1024
    header = replay.SLICE_CSV_PATH.read_text(encoding="utf-8", errors="replace").splitlines()[0]
    for column in ("timestamp", "DV_pressure", "Oil_temperature", "Motor_current", "TP3", "H1"):
        assert column in header, f"slice lost column {column}"


def test_prefers_full_dataset_then_slice(monkeypatch, tmp_path):
    full, slice_path = tmp_path / "full.csv", tmp_path / "slice.csv"
    full.write_text("timestamp\n")
    slice_path.write_text("timestamp\n")
    monkeypatch.setattr(replay, "FULL_CSV_PATH", full)
    monkeypatch.setattr(replay, "SLICE_CSV_PATH", slice_path)
    monkeypatch.delenv("TELEMETRY_CSV", raising=False)
    assert replay.resolve_csv_path() == full

    full.unlink()
    assert replay.resolve_csv_path() == slice_path


def test_explicit_override_wins_and_missing_data_fails_loudly(monkeypatch, tmp_path):
    other = tmp_path / "other.csv"
    other.write_text("timestamp\n")
    monkeypatch.setenv("TELEMETRY_CSV", str(other))
    assert replay.resolve_csv_path() == other

    monkeypatch.setenv("TELEMETRY_CSV", str(tmp_path / "absent.csv"))
    with pytest.raises(FileNotFoundError) as exc:
        replay.resolve_csv_path()
    assert "TELEMETRY_CSV" in str(exc.value)

    monkeypatch.delenv("TELEMETRY_CSV")
    monkeypatch.setattr(replay, "FULL_CSV_PATH", tmp_path / "no-full.csv")
    monkeypatch.setattr(replay, "SLICE_CSV_PATH", tmp_path / "no-slice.csv")
    with pytest.raises(FileNotFoundError) as exc:
        replay.resolve_csv_path()
    message = str(exc.value)
    assert "10.5281/zenodo.7157937" in message
    assert "synthesises" in message  # no fake-data fallback, ever


def test_missing_data_fails_at_load_time_not_at_import(monkeypatch, tmp_path):
    """`import src.engine.replay` must stay safe — run_demo.py prints its own error."""
    monkeypatch.delenv("TELEMETRY_CSV", raising=False)
    engine = replay.ReplayEngine(str(tmp_path / "nope.csv"))
    with pytest.raises(FileNotFoundError):
        engine.load_data()
