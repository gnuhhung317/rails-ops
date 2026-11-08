import os
import time
import json
import urllib.request
import threading
from typing import List, Optional, Dict, Any
from datetime import datetime

try:
    from datadog.dogstatsd import DogStatsd
except ImportError:
    DogStatsd = None
from src.domain.enums import IncidentLifecycleState, OperatingRegime
from src.domain.models import TelemetryPoint

DEFAULT_TAGS = [
    "service:compressorguard",
    "env:hackathon-2026",
    "asset_id:APU-COMP-01",
    "train_id:TRAIN-302",
    "fleet_id:FLEET-METRO-01",
]


class DatadogMetricsClient:
    """
    DogStatsD custom metrics client for CompressorGuard Industrial Operations.
    Emits telemetry gauges, ML corroboration scores, lead time, and recovery counters.
    Maintains an in-memory buffer (`buffered_metrics`) for zero-dependency offline testability.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        prefix: str = "compressorguard",
        constant_tags: Optional[List[str]] = None,
        buffer_only: bool = False,
    ) -> None:
        self.host = host or os.getenv("DD_AGENT_HOST", "localhost")
        self.port = port or int(os.getenv("DD_DOGSTATSD_PORT", "8125"))
        self.prefix = prefix
        self.constant_tags = constant_tags or list(DEFAULT_TAGS)
        self.buffer_only = buffer_only
        self.buffered_metrics: List[Dict[str, Any]] = []
        self.api_key: Optional[str] = os.getenv("DD_API_KEY")
        self.dd_site: str = os.getenv("DD_SITE", "ap2.datadoghq.com")
        self._http_queue: List[Dict[str, Any]] = []
        self._last_http_flush: float = time.time()
        self._lock = threading.Lock()

        self.statsd: Optional[Any] = None
        if not self.buffer_only and DogStatsd is not None:
            try:
                self.statsd = DogStatsd(
                    host=self.host,
                    port=self.port,
                    namespace=self.prefix,
                    constant_tags=self.constant_tags,
                )
            except Exception:
                self.statsd = None

    def _flush_http(self) -> None:
        if self.buffer_only or not self.api_key:
            return
        with self._lock:
            if not self._http_queue:
                return
            batch = list(self._http_queue)
            self._http_queue.clear()
            self._last_http_flush = time.time()

        def _worker(items: List[Dict[str, Any]], key: str, site: str):
            try:
                url = f"https://api.{site}/api/v1/series"
                headers = {
                    "Content-Type": "application/json",
                    "DD-API-KEY": key,
                }
                body = json.dumps({"series": items}).encode("utf-8")
                req = urllib.request.Request(url, data=body, headers=headers)
                urllib.request.urlopen(req, timeout=4)
            except Exception:
                pass

        threading.Thread(target=_worker, args=(batch, self.api_key, self.dd_site), daemon=True).start()

    def gauge(self, metric: str, value: float, tags: Optional[List[str]] = None) -> None:
        full_tags = list(self.constant_tags) + (tags or [])
        metric_name = f"{self.prefix}.{metric}" if not metric.startswith(self.prefix) else metric
        self.buffered_metrics.append({
            "type": "gauge",
            "name": metric_name,
            "value": value,
            "tags": full_tags,
            "timestamp": datetime.now().isoformat(),
        })
        if not self.buffer_only and self.api_key:
            now_epoch = int(time.time())
            with self._lock:
                self._http_queue.append({
                    "metric": metric_name,
                    "points": [[now_epoch, float(value)]],
                    "type": "gauge",
                    "tags": full_tags,
                })
            if len(self._http_queue) >= 12 or (time.time() - self._last_http_flush) >= 2.0:
                self._flush_http()
        if self.statsd:
            try:
                self.statsd.gauge(metric, value, tags=tags)
            except Exception:
                pass

    def increment(self, metric: str, value: int = 1, tags: Optional[List[str]] = None) -> None:
        full_tags = list(self.constant_tags) + (tags or [])
        metric_name = f"{self.prefix}.{metric}" if not metric.startswith(self.prefix) else metric
        self.buffered_metrics.append({
            "type": "count",
            "name": metric_name,
            "value": value,
            "tags": full_tags,
            "timestamp": datetime.now().isoformat(),
        })
        if not self.buffer_only and self.api_key:
            now_epoch = int(time.time())
            with self._lock:
                self._http_queue.append({
                    "metric": metric_name,
                    "points": [[now_epoch, float(value)]],
                    "type": "count",
                    "tags": full_tags,
                })
            if len(self._http_queue) >= 12 or (time.time() - self._last_http_flush) >= 2.0:
                self._flush_http()
        if self.statsd:
            try:
                self.statsd.increment(metric, value, tags=tags)
            except Exception:
                pass

    def emit_telemetry(self, point: TelemetryPoint) -> None:
        """Emits physical sensor telemetry metrics."""
        regime_str = point.regime.value if isinstance(point.regime, OperatingRegime) else str(point.regime)
        tags = [
            f"asset_id:{point.asset_id}",
            f"regime:{regime_str}",
        ]
        self.gauge("telemetry.dv_pressure_bar", point.dv_pressure_bar, tags=tags)
        self.gauge("telemetry.oil_temp_c", point.oil_temp_c, tags=tags)
        self.gauge("telemetry.motor_current_a", point.motor_current_a, tags=tags)
        self.gauge("telemetry.h1_bar", point.h1_bar, tags=tags)
        self.gauge("telemetry.tp3_bar", point.tp3_bar, tags=tags)
        self.gauge("telemetry.lps_active", point.lps_active, tags=tags)

    def emit_ml_score(self, score: float, asset_id: str = "APU-COMP-01") -> None:
        """Emits Isolation Forest multivariate anomaly corroboration score."""
        tags = [f"asset_id:{asset_id}"]
        self.gauge("ml.anomaly_score", score, tags=tags)

    def emit_ml_observability(
        self,
        score: float,
        inference_latency_ms: float = 0.0,
        physics_agreed: bool = True,
        asset_id: str = "APU-COMP-01",
    ) -> None:
        """Emits AI/ML observability signals: anomaly score, inference latency, and physics consensus."""
        tags = [f"asset_id:{asset_id}", "model:isolation_forest_5f"]
        self.gauge("ml.anomaly_score", score, tags=tags)
        self.gauge("ml.inference_latency_ms", round(float(inference_latency_ms), 3), tags=tags)
        self.gauge("ml.physics_agreement", 1.0 if physics_agreed else 0.0, tags=tags)

    def emit_signal_suppression(
        self,
        asset_id: str = "APU-COMP-01",
        detector_id: str = "pressure_anomaly",
    ) -> None:
        """Increments counter when a transient spike is suppressed before case creation."""
        tags = [f"asset_id:{asset_id}", f"detector:{detector_id}"]
        self.increment("signals.suppressed_total", 1, tags=tags)

    def emit_runtime_warning_elapsed(self, elapsed_seconds: int, asset_id: str = "APU-COMP-01") -> None:
        """Emits real-time elapsed warning duration since confirmed onset while LPS remains silent."""
        tags = [f"asset_id:{asset_id}"]
        self.gauge("incident.elapsed_warning_seconds", float(max(0, elapsed_seconds)), tags=tags)

    def emit_lead_time(self, seconds: int, asset_id: str = "APU-COMP-01") -> None:
        """Emits confirmed counterfactual intervention lead time buffer in seconds (e.g. 121,920s = 33h 52m)."""
        tags = [f"asset_id:{asset_id}"]
        self.gauge("incident.lead_time_seconds", float(seconds), tags=tags)

    def emit_recovery_progress(self, consecutive_obs: int, asset_id: str = "APU-COMP-01") -> None:
        """Emits physical recovery progress counter (0 to 5 consecutive healthy observations)."""
        tags = [f"asset_id:{asset_id}"]
        self.gauge("recovery.consecutive_observations", float(consecutive_obs), tags=tags)

    def emit_case_transition(self, state: IncidentLifecycleState, asset_id: str = "APU-COMP-01") -> None:
        """Emits operational case lifecycle state change."""
        state_str = state.value if isinstance(state, IncidentLifecycleState) else str(state)
        tags = [f"asset_id:{asset_id}", f"state:{state_str}"]
        self.gauge("case.lifecycle_state", 1.0, tags=tags)
        self.increment("case.transitions_total", 1, tags=tags)


_GLOBAL_METRICS_CLIENT: Optional[DatadogMetricsClient] = None


def get_metrics_client(buffer_only: bool = False) -> DatadogMetricsClient:
    global _GLOBAL_METRICS_CLIENT
    if _GLOBAL_METRICS_CLIENT is None:
        _GLOBAL_METRICS_CLIENT = DatadogMetricsClient(buffer_only=buffer_only)
    return _GLOBAL_METRICS_CLIENT

