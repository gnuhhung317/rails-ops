import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Generator, Tuple

from src.domain.enums import OperatingRegime
from src.domain.models import TelemetryPoint

DEFAULT_CSV_PATH = Path(__file__).resolve().parents[2] / "dataset" / "MetroPT3(AirCompressor).csv"
CSV_PATH = str(DEFAULT_CSV_PATH)

def classify_regime(motor_current: float, comp: float, dv_electric: float) -> OperatingRegime:
    if motor_current < 0.5:
        return OperatingRegime.OFF
    elif motor_current > 8.0:
        return OperatingRegime.STARTING
    elif comp == 1.0 and dv_electric == 0.0:
        return OperatingRegime.OFF_LOAD
    elif comp == 0.0 or dv_electric == 1.0:
        return OperatingRegime.LOADED
    else:
        return OperatingRegime.TRANSIENT

def row_to_telemetry_point(row: pd.Series) -> TelemetryPoint:
    mc = float(row['Motor_current'])
    comp = float(row['COMP'])
    dv_el = float(row['DV_eletric'])
    regime = classify_regime(mc, comp, dv_el)

    ts = row['timestamp']
    if isinstance(ts, str):
        ts = pd.to_datetime(ts)

    return TelemetryPoint(
        asset_id="APU-COMP-01",
        timestamp=ts,
        tp2_bar=float(row['TP2']),
        tp3_bar=float(row['TP3']),
        h1_bar=float(row['H1']),
        dv_pressure_bar=float(row['DV_pressure']),
        reservoirs_bar=float(row['Reservoirs']),
        oil_temp_c=float(row['Oil_temperature']),
        motor_current_a=mc,
        comp_val=comp,
        dv_electric=dv_el,
        towers_val=float(row['Towers']),
        mpg_val=float(row['MPG']),
        lps_active=float(row['LPS']),
        pressure_switch=float(row['Pressure_switch']),
        oil_level_low=float(row['Oil_level']),
        caudal_impulses=float(row['Caudal_impulses']),
        regime=regime
    )

class ReplayEngine:
    def __init__(self, csv_path: str = CSV_PATH):
        self.csv_path = csv_path
        self.df: pd.DataFrame = None

    def load_data(self):
        print(f"ReplayEngine loading dataset from {self.csv_path}...")
        self.df = pd.read_csv(self.csv_path)
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        if not self.df['timestamp'].is_monotonic_increasing:
            self.df = self.df.sort_values("timestamp").reset_index(drop=True)
        print(f"ReplayEngine loaded {len(self.df):,} rows.")

    def stream_telemetry(self, start_ts: str, end_ts: str) -> Generator[TelemetryPoint, None, None]:
        if self.df is None:
            self.load_data()
        
        sub = self.df[(self.df['timestamp'] >= start_ts) & (self.df['timestamp'] <= end_ts)]
        for _, row in sub.iterrows():
            yield row_to_telemetry_point(row)
