from typing import List

from src.domain.contracts import BaseEvidenceFusion
from src.domain.models import TelemetryPoint, DetectorResult, EvidenceState

class EvidenceFusionEngine(BaseEvidenceFusion):
    def fuse(self, results: List[DetectorResult], latest_telemetry: TelemetryPoint) -> EvidenceState:
        return EvidenceState(
            asset_id=latest_telemetry.asset_id,
            timestamp=latest_telemetry.timestamp,
            regime=latest_telemetry.regime,
            signals=results
        )
