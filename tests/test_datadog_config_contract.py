"""Contract test: the Datadog dashboard/monitors must only reference signals the code emits.

A dashboard JSON that imports cleanly but plots empty series is the exact "toy demo" failure
mode this project forbids. Nothing else in the suite checked that the two artifacts agree,
because the app runs correctly with no Datadog agent at all.

Custom metric names are read statically out of src/observability/metrics.py (the same source
the client prefixes at runtime), so this test does not need an agent, a network, or the CSV.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILES = [ROOT / "datadog" / "dashboard.json", ROOT / "datadog" / "monitors.json"]

from src.observability.metrics import DatadogMetricsClient  # noqa: E402
from src.observability.tracer import DEFAULT_ENV  # noqa: E402


def _emitted_custom_metrics() -> set[str]:
    """Every `prefix.<name>` the client can emit, read from the emit_* call sites."""
    source = (ROOT / "src" / "observability" / "metrics.py").read_text(encoding="utf-8")
    suffixes = set(re.findall(r'self\.(?:gauge|increment)\(\s*"([^"]+)"', source))
    prefix = DatadogMetricsClient(prefix="compressorguard").prefix
    return {f"{prefix}.{s}" for s in suffixes}


def _emitted_span_names() -> set[str]:
    """Every operation name actually traced by the engine."""
    names: set[str] = set()
    for path in (ROOT / "src").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        names.update(re.findall(r'trace_operation\(\s*"([^"]+)"', text))
    return names


def _config_text() -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in CONFIG_FILES)


def _referenced_custom_metrics(text: str) -> set[str]:
    return set(re.findall(r'(?<!trace\.)\b(compressorguard\.[a-z0-9_]+(?:\.[a-z0-9_]+)+)', text))


def _trace_queries(text: str) -> list[tuple[str, str]]:
    """(app_name, span_name) pairs from `trace.<app>.<span>.<statistic>` queries."""
    out = []
    for raw in re.findall(r'trace\.([A-Za-z0-9_.]+?)\.(?:duration|hit|error|DURATION|HIT|ERROR)\b', text):
        app, _, span = raw.partition(".")
        out.append((app, span))
    return out


def test_config_files_are_valid_json_with_expected_shape():
    dashboard = json.loads((ROOT / "datadog" / "dashboard.json").read_text(encoding="utf-8"))
    assert dashboard["layout_type"] == "ordered"
    assert len(dashboard["widgets"]) >= 6
    monitors = json.loads((ROOT / "datadog" / "monitors.json").read_text(encoding="utf-8"))["monitors"]
    assert monitors
    for m in monitors:
        assert m["type"] and m["query"] and m["message"], m.get("name")


def test_every_referenced_custom_metric_is_actually_emitted():
    emitted = _emitted_custom_metrics()
    referenced = _referenced_custom_metrics(_config_text())
    assert referenced, "no compressorguard.* metrics found in the Datadog config"
    missing = sorted(referenced - emitted)
    assert not missing, (
        f"Datadog config references metrics the code never emits: {missing}. "
        f"Emitted set: {sorted(emitted)}"
    )


def test_apm_trace_queries_match_real_engine_spans():
    spans = _emitted_span_names()
    queries = _trace_queries(_config_text())
    assert queries, "dashboard has no APM trace query, so tracing is not visualised"
    for app, span in queries:
        assert app == "compressorguard", f"trace app_name {app!r} is not the traced service"
        assert span in spans, (
            f"trace query references span {span!r}, which no trace_operation() call emits. "
            f"Datadog builds the metric as trace.<service>.<operation>.duration, so the "
            f"operation name must not repeat the service prefix. Known spans: {sorted(spans)}"
        )


def test_env_filter_used_by_the_dashboard_is_the_one_the_tracer_tags():
    text = _config_text()
    envs = set(re.findall(r'env[:"]([a-z0-9-]+)', text))
    assert envs, "no env tag anywhere in the Datadog config"
    assert envs == {DEFAULT_ENV}, f"config filters {sorted(envs)} but tracer tags {DEFAULT_ENV!r}"


def test_tracer_tags_spans_with_env_so_the_filter_is_satisfiable():
    from src.observability.tracer import trace_operation

    with trace_operation("detector.evaluate", resource="ContractTest") as span:
        env = span.get_tag("env") if hasattr(span, "get_tag") else span.tags.get("env")
        assert env == DEFAULT_ENV
