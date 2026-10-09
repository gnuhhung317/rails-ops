from typing import Dict, Optional
from pydantic import BaseModel, Field


class ScenarioDefinition(BaseModel):
    """
    Decoupled declarative specification of a physical historical scenario.
    Enables replaying arbitrary historical episodes (Failure #3, Failure #1,
    Failure #4, or Healthy baseline) without hardcoding scenario logic
    into the IncidentLifecycleManager domain orchestrator.
    """
    scenario_id: str
    name: str
    asset_id: str = "APU-COMP-01"
    stream_start: str
    stream_end: str
    recovery_start: Optional[str] = None
    recovery_end: Optional[str] = None
    lps_milestone: Optional[str] = None
    milestones: Dict[str, str] = Field(default_factory=dict)


FAILURE_3_SCENARIO = ScenarioDefinition(
    scenario_id="failure_3",
    name="Failure #3 Air Leak & Thermal Drift (Golden Path)",
    asset_id="APU-COMP-01",
    stream_start="2020-06-05 09:40:00",
    stream_end="2020-06-06 20:00:00",
    recovery_start="2020-06-08 16:05:00",
    recovery_end="2020-06-08 17:00:00",
    lps_milestone="2020-06-06 19:42:19",
    milestones={
        "early_excursion_0033": "2020-06-04 00:33:07",
        "onset_0950": "2020-06-05 09:50:00",
        "ml_corroborated_1015": "2020-06-05 10:15:00",
        "lps_reactive_1942": "2020-06-06 19:42:19",
        "post_maintenance_1605": "2020-06-08 16:05:00",
    },
)

FAILURE_1_SCENARIO = ScenarioDefinition(
    scenario_id="failure_1",
    name="Failure #1 Air Leak & High Duty Cycle",
    asset_id="APU-COMP-01",
    stream_start="2020-04-10 00:00:00",
    stream_end="2020-04-12 23:59:59",
    milestones={
        "onset": "2020-04-11 11:00:00",
    },
)

FAILURE_4_SCENARIO = ScenarioDefinition(
    scenario_id="failure_4",
    name="Failure #4 Oil Contamination & Thermal Stress",
    asset_id="APU-COMP-01",
    stream_start="2020-07-08 00:00:00",
    stream_end="2020-07-10 23:59:59",
    milestones={
        "onset": "2020-07-09 14:00:00",
    },
)

HEALTHY_SCENARIO = ScenarioDefinition(
    scenario_id="healthy_baseline",
    name="Healthy Baseline (February 2020)",
    asset_id="APU-COMP-01",
    stream_start="2020-02-10 08:00:00",
    stream_end="2020-02-10 12:00:00",
    milestones={},
)
