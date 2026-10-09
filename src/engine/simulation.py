from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Generator, Dict, Any
from pydantic import BaseModel, Field

from src.domain.models import TelemetryPoint
from src.engine.replay import ReplayEngine, DEFAULT_CSV_PATH


class SimulationPacingConfig(BaseModel):
    speed_multiplier: float = 60.0  # 1.0, 10.0, 60.0, 300.0
    max_step_delay_seconds: float = 2.0  # Bound extreme gaps for smooth UI


class ScenarioStream(ABC):
    @abstractmethod
    def next(self) -> Optional[TelemetryPoint]:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass

    @abstractmethod
    def seek(self, event_time: datetime) -> None:
        pass


class HistoricalScenarioStream(ScenarioStream):
    def __init__(
        self,
        start_ts: str = "2020-06-05 09:40:00",
        end_ts: str = "2020-06-06 20:00:00",
        csv_path: str = str(DEFAULT_CSV_PATH),
    ) -> None:
        self.start_ts = start_ts
        self.end_ts = end_ts
        self.replay = ReplayEngine(csv_path)
        self.generator: Optional[Generator[TelemetryPoint, None, None]] = None
        self.reset()

    def reset(self) -> None:
        self.generator = self.replay.stream_telemetry(self.start_ts, self.end_ts)

    def next(self) -> Optional[TelemetryPoint]:
        if self.generator is None:
            self.reset()
        try:
            return next(self.generator)
        except StopIteration:
            return None

    def seek(self, event_time: datetime) -> None:
        self.reset()
        while True:
            pt = self.next()
            if pt is None or pt.timestamp >= event_time:
                break


class SimulationRunner:
    """
    SimulationRunner drives pacing and stream advancement.
    INVARIANTS:
    1. Strictly preserves original TelemetryPoint.timestamp as event_time.
    2. Calculates step pacing based on delta event_time / speed_multiplier.
    3. Exposes play, pause, step, reset, and speed configuration.
    """
    def __init__(
        self,
        stream: ScenarioStream,
        config: Optional[SimulationPacingConfig] = None,
        scenario_name: str = "Failure #3 — Air Leak",
    ) -> None:
        self.stream = stream
        self.config = config or SimulationPacingConfig()
        self.scenario_name = scenario_name
        self.is_paused: bool = True
        self.current_point: Optional[TelemetryPoint] = None
        self.last_event_time: Optional[datetime] = None
        self.current_event_time: Optional[datetime] = None
        self.total_points_emitted: int = 0

    def set_speed(self, multiplier: float) -> None:
        if multiplier <= 0:
            raise ValueError(f"Speed multiplier must be positive, got {multiplier}")
        self.config.speed_multiplier = multiplier

    def calculate_step_delay(self, prev_time: datetime, next_time: datetime) -> float:
        delta_sec = max(0.0, (next_time - prev_time).total_seconds())
        scaled = delta_sec / self.config.speed_multiplier
        return min(scaled, self.config.max_step_delay_seconds)

    def step(self) -> Optional[TelemetryPoint]:
        pt = self.stream.next()
        if pt is None:
            return None
        self.last_event_time = self.current_event_time
        self.current_event_time = pt.timestamp
        self.current_point = pt
        self.total_points_emitted += 1
        return pt

    def play(self) -> None:
        self.is_paused = False

    def pause(self) -> None:
        self.is_paused = True

    def seek(self, event_time: datetime) -> Optional[TelemetryPoint]:
        self.stream.seek(event_time)
        return self.step()

    def reset(self) -> None:
        self.stream.reset()
        self.current_point = None
        self.last_event_time = None
        self.current_event_time = None
        self.total_points_emitted = 0
        self.is_paused = True

    def get_status(self) -> Dict[str, Any]:
        return {
            "scenario_name": self.scenario_name,
            "is_paused": self.is_paused,
            "speed_multiplier": self.config.speed_multiplier,
            "current_event_time": (
                self.current_event_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                if self.current_event_time
                else None
            ),
            "total_points_emitted": self.total_points_emitted,
            "mode": "LIVE_SIMULATION",
            "provenance": "MetroPT-3 Historical Telemetry",
        }
