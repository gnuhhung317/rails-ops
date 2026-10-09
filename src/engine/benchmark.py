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

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_ready": self.is_ready,
            "lead_time_minutes": self.lead_time_minutes,
            "lead_time_formatted": self.formatted_lead_time,
            "onset_timestamp": self.onset_timestamp.isoformat() if self.onset_timestamp else None,
            "lps_benchmark_timestamp": self.lps_timestamp.isoformat() if self.lps_timestamp else None,
        }
