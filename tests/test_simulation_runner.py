from datetime import datetime
import pytest
from src.domain.models import TelemetryPoint
from src.engine.simulation import (
    ScenarioStream,
    SimulationRunner,
    SimulationPacingConfig,
)

class DummyScenarioStream(ScenarioStream):
    def __init__(self, timestamps):
        self.timestamps = timestamps
        self.idx = 0

    def next(self):
        if self.idx >= len(self.timestamps):
            return None
        ts = self.timestamps[self.idx]
        self.idx += 1
        return TelemetryPoint(
            asset_id="APU-COMP-01",
            timestamp=ts,
            tp2_bar=0.0, tp3_bar=0.0, h1_bar=0.0, dv_pressure_bar=0.0,
            reservoirs_bar=8.0, oil_temp_c=60.0, motor_current_a=6.5,
            comp_val=0.0, dv_electric=1.0, towers_val=0.0, mpg_val=0.0,
            lps_active=0.0, pressure_switch=0.0, oil_level_low=0.0,
            caudal_impulses=0.0
        )

    def reset(self):
        self.idx = 0

    def seek(self, event_time):
        self.idx = 0
        while self.idx < len(self.timestamps) and self.timestamps[self.idx] < event_time:
            self.idx += 1

def test_simulation_runner_time_separation_and_speed_pacing():
    # Sequence with a normal 10s gap and an 80s telemetry gap
    t0 = datetime(2020, 6, 5, 9, 50, 0)
    t1 = datetime(2020, 6, 5, 9, 50, 10) # 10s delta
    t2 = datetime(2020, 6, 5, 9, 51, 30) # 80s delta
    stream = DummyScenarioStream([t0, t1, t2])
    
    runner = SimulationRunner(stream=stream, config=SimulationPacingConfig(speed_multiplier=60.0))
    
    # 1. Event times are preserved exactly as original timestamps (never now())
    p0 = runner.step()
    assert p0.timestamp == t0
    assert runner.current_event_time == t0
    
    # 2. Pacing respects real event delta
    p1 = runner.step()
    assert p1.timestamp == t1
    # delta is 10s historical -> 10 / 60 = 0.1667 simulation seconds
    assert runner.calculate_step_delay(t0, t1) == pytest.approx(10.0 / 60.0)
    
    # 3. Irregular gap respects delta
    p2 = runner.step()
    assert p2.timestamp == t2
    # delta is 80s historical -> 80 / 60 = 1.333 simulation seconds
    assert runner.calculate_step_delay(t1, t2) == pytest.approx(80.0 / 60.0)

def test_simulation_speed_controls():
    stream = DummyScenarioStream([datetime(2020, 6, 5, 9, 50, 0)])
    runner = SimulationRunner(stream=stream)
    
    runner.set_speed(10.0)
    assert runner.config.speed_multiplier == 10.0
    runner.set_speed(300.0)
    assert runner.config.speed_multiplier == 300.0
    
    with pytest.raises(ValueError):
        runner.set_speed(-1.0)
