import functools
import os
from contextlib import contextmanager
from typing import Optional, Callable, Any

try:
    from ddtrace import tracer as dd_tracer
except ImportError:
    dd_tracer = None

DEFAULT_ENV = "hackathon-2026"


class FallbackSpan:
    def __init__(self, name: str, resource: Optional[str] = None) -> None:
        self.name = name
        self.resource = resource or name
        self.tags = {}

    def set_tag(self, key: str, value: Any) -> None:
        self.tags[key] = str(value)

    def set_tags(self, tags: dict) -> None:
        for k, v in tags.items():
            self.set_tag(k, v)

    def finish(self) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish()


class FallbackTracer:
    def __init__(self) -> None:
        self._current_span: Optional[FallbackSpan] = None

    def trace(self, name: str, resource: Optional[str] = None, service: str = "compressorguard") -> FallbackSpan:
        span = FallbackSpan(name, resource)
        span.set_tag("service", service)
        return span

    def current_span(self) -> Optional[FallbackSpan]:
        return self._current_span


def get_tracer():
    """Returns the ddtrace tracer singleton or a resilient fallback."""
    if dd_tracer is not None:
        return dd_tracer
    return FallbackTracer()


@contextmanager
def trace_operation(name: str, resource: Optional[str] = None, service: str = "compressorguard"):
    """
    Context manager for measuring domain operations with Datadog APM spans.
    Usage:
        with trace_operation("detector.evaluate", resource="PressureAnomalyDetector") as span:
            span.set_tag("asset_id", "APU-COMP-01")
            ...
    """
    tracer = get_tracer()
    with tracer.trace(name, resource=resource, service=service) as span:
        # The dashboard filters APM series by {env:hackathon-2026}; tagging here makes
        # that filter satisfiable regardless of how the agent's DD_ENV is configured.
        span.set_tag("env", os.environ.get("DD_ENV", DEFAULT_ENV))
        yield span
