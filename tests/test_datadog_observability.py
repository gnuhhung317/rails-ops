import json
import logging
from datetime import datetime, timezone
import pytest

from src.domain.enums import IncidentLifecycleState, OperatingRegime
from src.domain.models import TelemetryPoint
from src.observability.metrics import DatadogMetricsClient, get_metrics_client
from src.observability.tracer import get_tracer, trace_operation
from src.observability.logger import DatadogJSONFormatter, setup_datadog_logging


def test_dogstatsd_metrics_emission():
    client = DatadogMetricsClient(buffer_only=True)
    
    # 1. Emit telemetry point
    point = TelemetryPoint(
        asset_id="APU-COMP-01",
        timestamp=datetime(2020, 6, 5, 9, 50, 0, tzinfo=timezone.utc),
        tp2_bar=0.0,
        tp3_bar=8.2,
        h1_bar=9.5,
        dv_pressure_bar=2.1856,
        reservoirs_bar=9.5,
        oil_temp_c=74.97,
        motor_current_a=6.8,
        comp_val=1.0,
        dv_electric=0.0,
        towers_val=1.0,
        mpg_val=1.0,
        lps_active=0.0,
        pressure_switch=0.0,
        oil_level_low=0.0,
        caudal_impulses=1.0,
        regime=OperatingRegime.LOADED,
    )
    client.emit_telemetry(point)
    
    # 2. Emit ML anomaly score
    client.emit_ml_score(0.382)
    
    # 3. Emit early intervention lead time (33h 52m = 121,920s)
    client.emit_lead_time(121920)
    
    # 4. Emit recovery progress
    client.emit_recovery_progress(5)
    
    # 5. Emit case transition
    client.emit_case_transition(IncidentLifecycleState.DETECTED)

    metrics = client.buffered_metrics
    assert len(metrics) >= 8
    
    # Verify metric names
    metric_names = [m["name"] for m in metrics]
    assert "compressorguard.telemetry.dv_pressure_bar" in metric_names
    assert "compressorguard.telemetry.oil_temp_c" in metric_names
    assert "compressorguard.telemetry.motor_current_a" in metric_names
    assert "compressorguard.ml.anomaly_score" in metric_names
    assert "compressorguard.incident.lead_time_seconds" in metric_names
    assert "compressorguard.recovery.consecutive_observations" in metric_names
    assert "compressorguard.case.lifecycle_state" in metric_names
    
    # Verify tagging
    dv_metric = next(m for m in metrics if m["name"] == "compressorguard.telemetry.dv_pressure_bar")
    assert dv_metric["value"] == 2.1856
    assert any("asset_id:APU-COMP-01" in tag for tag in dv_metric["tags"])
    assert any("regime:LOADED" in tag for tag in dv_metric["tags"])
    assert any("service:compressorguard" in tag for tag in dv_metric["tags"])


def test_apm_distributed_tracing_spans():
    tracer = get_tracer()
    
    with tracer.trace("compressorguard.test_span", resource="test_resource") as span:
        span.set_tag("asset_id", "APU-COMP-01")
        span.set_tag("custom.test", "true")
        assert span is not None
        
        # Test trace_operation decorator / context manager
        with trace_operation("compressorguard.detector.evaluate", resource="PressureAnomalyDetector") as op_span:
            op_span.set_tag("detector_id", "pressure_anomaly")
            assert op_span is not None


def test_structured_json_logging_trace_correlation():
    formatter = DatadogJSONFormatter()
    
    logger = logging.getLogger("test_compressorguard_logger")
    logger.setLevel(logging.INFO)
    
    # Create record inside an active trace span
    tracer = get_tracer()
    with tracer.trace("test_operation", resource="audit_log"):
        record = logger.makeRecord(
            name="test_compressorguard_logger",
            level=logging.INFO,
            fn="test_file.py",
            lno=42,
            msg="Safe mode activated. Branching replay stream to post-maintenance telemetry.",
            args=(),
            exc_info=None,
            extra={"incident_id": "APU-INC-20200605-01", "asset_id": "APU-COMP-01"}
        )
        json_output = formatter.format(record)
        
    data = json.loads(json_output)
    assert data["level"] == "INFO"
    assert "Safe mode activated" in data["message"]
    assert data["incident_id"] == "APU-INC-20200605-01"
    assert data["asset_id"] == "APU-COMP-01"
    assert "timestamp" in data
    assert "dd.trace_id" in data
    assert "dd.span_id" in data


def test_lifecycle_orchestrator_datadog_integration():
    from src.engine.lifecycle import IncidentLifecycleManager

    metrics_client = DatadogMetricsClient(buffer_only=True)
    manager = IncidentLifecycleManager(metrics_client=metrics_client)
    manager.reset()
    
    # Jump to onset
    manager.jump_to_milestone("onset_0950")
    
    # Invariant: Metrics emitted during progression
    buffered = metrics_client.buffered_metrics
    assert len(buffered) > 0
    
    # Verify lead time metric was emitted (33h 52m = 121,920 seconds)
    lead_time_metrics = [m for m in buffered if m["name"] == "compressorguard.incident.lead_time_seconds"]
    assert len(lead_time_metrics) >= 1
    assert lead_time_metrics[-1]["value"] == 121920


def test_datadog_monitors_and_dashboard_schema():
    from pathlib import Path
    
    monitors_path = Path("datadog/monitors.json")
    dashboard_path = Path("datadog/dashboard.json")
    
    assert monitors_path.exists(), "datadog/monitors.json must exist"
    assert dashboard_path.exists(), "datadog/dashboard.json must exist"
    
    monitors = json.loads(monitors_path.read_text(encoding="utf-8"))
    assert "monitors" in monitors
    assert len(monitors["monitors"]) >= 2
    
    monitor_names = [m["name"] for m in monitors["monitors"]]
    assert any("Pressure Breach" in name or "Early Warning" in name for name in monitor_names)
    assert any("Recovery" in name for name in monitor_names)
    
    dashboard = json.loads(dashboard_path.read_text(encoding="utf-8"))
    assert "title" in dashboard
    assert "widgets" in dashboard
    assert len(dashboard["widgets"]) >= 4
