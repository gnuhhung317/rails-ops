from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.models import (
    TelemetryPoint,
    DetectorResult,
    EvidenceState,
    Decision,
    IncidentContext,
)

class BaseDetector(ABC):
    @property
    @abstractmethod
    def detector_id(self) -> str:
        pass

    @abstractmethod
    def detect(self, window: List[TelemetryPoint]) -> DetectorResult:
        pass

class BaseEvidenceFusion(ABC):
    @abstractmethod
    def fuse(self, results: List[DetectorResult], latest_telemetry: TelemetryPoint) -> EvidenceState:
        pass

class BaseDecisionEngine(ABC):
    @abstractmethod
    def evaluate(self, evidence_state: EvidenceState, incident_context: Optional[IncidentContext] = None) -> Decision:
        pass
