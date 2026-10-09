from typing import Optional
from fastapi import APIRouter, Depends

from src.api.dependencies import get_manager
from src.api.schemas import (
    ResetRequest,
    ResetResponse,
    TickResponse,
    JumpRequest,
    JumpResponse,
    ErrorResponse,
    SimulationSpeedRequest,
    SimulationPlaybackResponse,
    SimulationStatusResponse,
)
from src.engine.lifecycle import IncidentLifecycleManager

router = APIRouter(prefix="/demo", tags=["Demo & Simulation Controls"])


@router.post(
    "/reset",
    response_model=ResetResponse,
    responses={400: {"model": ErrorResponse, "description": "Invalid milestone"}},
)
def reset_demo(
    body: Optional[ResetRequest] = None,
    manager: IncidentLifecycleManager = Depends(get_manager),
) -> ResetResponse:
    """
    Resets the simulation to initial state.
    Optionally fast-forwards to a designated milestone if specified.
    """
    manager.reset()
    milestone = body.milestone if body else None
    if milestone:
        manager.jump_to_milestone(milestone)

    return ResetResponse(status="RESET_OK", milestone=milestone)


@router.post("/tick", response_model=TickResponse)
def tick_demo(manager: IncidentLifecycleManager = Depends(get_manager)) -> TickResponse:
    """
    Advances the deterministic replay cursor by one sample (10 seconds).
    Idempotent no-op once RESOLVED is reached.
    """
    manager.tick()
    state_val = (
        manager.lifecycle_state.value
        if hasattr(manager.lifecycle_state, "value")
        else str(manager.lifecycle_state)
    )
    return TickResponse(status="TICK_OK", lifecycle_state=state_val)


@router.post(
    "/jump",
    response_model=JumpResponse,
    responses={400: {"model": ErrorResponse, "description": "Invalid milestone"}},
)
def jump_demo(
    body: JumpRequest,
    manager: IncidentLifecycleManager = Depends(get_manager),
) -> JumpResponse:
    """
    Jumps the replay stream directly to a verified historical milestone.
    Raises ValueError (HTTP 400) if milestone name is unknown.
    """
    manager.jump_to_milestone(body.milestone)
    state_val = (
        manager.lifecycle_state.value
        if hasattr(manager.lifecycle_state, "value")
        else str(manager.lifecycle_state)
    )
    return JumpResponse(status="JUMP_OK", milestone=body.milestone, lifecycle_state=state_val)


@router.post("/play", response_model=SimulationPlaybackResponse)
def play_demo(manager: IncidentLifecycleManager = Depends(get_manager)) -> SimulationPlaybackResponse:
    """Resumes or starts simulation playback."""
    manager.play()
    return SimulationPlaybackResponse(
        status="PLAY_OK",
        is_paused=False,
        speed_multiplier=manager.runner.config.speed_multiplier if manager.runner else 60.0,
    )


@router.post("/pause", response_model=SimulationPlaybackResponse)
def pause_demo(manager: IncidentLifecycleManager = Depends(get_manager)) -> SimulationPlaybackResponse:
    """Pauses simulation playback."""
    manager.pause()
    return SimulationPlaybackResponse(
        status="PAUSE_OK",
        is_paused=True,
        speed_multiplier=manager.runner.config.speed_multiplier if manager.runner else 60.0,
    )


@router.post("/speed", response_model=SimulationPlaybackResponse)
def speed_demo(
    body: SimulationSpeedRequest,
    manager: IncidentLifecycleManager = Depends(get_manager),
) -> SimulationPlaybackResponse:
    """Sets the simulation speed pacing multiplier (e.g. 1.0, 10.0, 60.0, 300.0)."""
    manager.set_simulation_speed(body.speed_multiplier)
    is_paused = manager.runner.is_paused if manager.runner else True
    return SimulationPlaybackResponse(
        status="SPEED_OK",
        is_paused=is_paused,
        speed_multiplier=body.speed_multiplier,
    )


@router.get("/status", response_model=SimulationStatusResponse)
def status_demo(manager: IncidentLifecycleManager = Depends(get_manager)) -> SimulationStatusResponse:
    """Returns the current simulation runner status, event_time clock, and emitted point counts."""
    st = manager.get_simulation_status()
    return SimulationStatusResponse(**st)

