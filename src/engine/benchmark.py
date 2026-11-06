from datetime import datetime
from typing import Optional, Dict, Any
import pandas as pd


class BaselineBenchmarkTracker:
    """
    Decouples the historical unmitigated baseline benchmark from simulated intervention.
    Calculates lead time strictly from observed historical onset and observed baseline LPS breach.
    """
    def __init__(self, expected_lps_timestamp: Optional[str] = "2020-06-06 19:42:19") -> None:
        self.onset_timestamp: Optional[datetime] = None
        self.lps_timestamp: Optional[datetime] = (
            pd.to_datetime(expected_lps_timestamp) if expected_lps_timestamp else None
        )
        self.is_lps_observed: bool = False

    def record_onset(self, onset_dt: datetime) -> None:
        self.onset_timestamp = pd.to_datetime(onset_dt)

    def record_lps_benchmark(self, lps_dt: datetime) -> None:
        self.lps_timestamp = pd.to_datetime(lps_dt)
        self.is_lps_observed = True

    @property
    def is_ready(self) -> bool:
        return self.onset_timestamp is not None and self.lps_timestamp is not None

    @property
    def lead_time_minutes(self) -> Optional[int]:
        if not self.is_ready or self.onset_timestamp is None or self.lps_timestamp is None:
            return None
        delta = self.lps_timestamp - self.onset_timestamp
        mins = int(round(delta.total_seconds() / 60.0))
        return max(0, mins)

    @property
    def formatted_lead_time(self) -> Optional[str]:
        mins = self.lead_time_minutes
        if mins is None:
            return None
        hours = mins // 60
        rem_mins = mins % 60
        return f"{hours}h {rem_mins:02d}m"

    def get_runtime_warning_status(
        self,
        current_time: Optional[datetime] = None,
        tp3_bar: Optional[float] = None,
        lps_active: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Computes strictly causal runtime early-warning metrics at current_time (t <= cursor),
        without looking ahead to future timestamps.
        """
        if self.onset_timestamp is None:
            return {
                "is_warning_active": False,
                "elapsed_warning_minutes": 0,
                "elapsed_warning_formatted": "0h 00m",
                "legacy_lps_still_silent": bool(lps_active == 0.0),
                "brake_reservoir_tp3_bar": round(float(tp3_bar), 2) if tp3_bar is not None else None,
                "projected_rul_window": None,
            }

        elapsed_mins = 0
        if current_time is not None:
            cur_dt = pd.to_datetime(current_time)
            onset_dt = pd.to_datetime(self.onset_timestamp)
            if cur_dt.tzinfo is not None and onset_dt.tzinfo is None:
                cur_dt = cur_dt.tz_localize(None)
            elif cur_dt.tzinfo is None and onset_dt.tzinfo is not None:
                onset_dt = onset_dt.tz_localize(None)
            delta_sec = max(0.0, (cur_dt - onset_dt).total_seconds())
            elapsed_mins = int(round(delta_sec / 60.0))

        e_hours = elapsed_mins // 60
        e_rem = elapsed_mins % 60
        elapsed_fmt = f"+{e_hours}h {e_rem:02d}m"

        is_safe_pressure = (tp3_bar is None or tp3_bar >= 7.5) and (lps_active == 0.0)
        rul_window = (
            "24h - 36h (Safe for Scheduled Night Depot Swap)"
            if is_safe_pressure
            else "IMMEDIATE WITHDRAWAL REQUIRED (Reservoir < 7.5 bar)"
        )

        return {
            "is_warning_active": True,
            "elapsed_warning_minutes": elapsed_mins,
            "elapsed_warning_formatted": elapsed_fmt,
            "legacy_lps_still_silent": bool(lps_active == 0.0),
            "brake_reservoir_tp3_bar": round(float(tp3_bar), 2) if tp3_bar is not None else None,
            "projected_rul_window": rul_window,
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_ready": self.is_ready,
            "lead_time_minutes": self.lead_time_minutes,
            "lead_time_formatted": self.formatted_lead_time,
            "onset_timestamp": self.onset_timestamp.isoformat() if self.onset_timestamp else None,
            "lps_benchmark_timestamp": self.lps_timestamp.isoformat() if self.lps_timestamp else None,
        }

