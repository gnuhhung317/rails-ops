import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from src.observability.tracer import get_tracer


class DatadogJSONFormatter(logging.Formatter):
    """
    Structured JSON log formatter compliant with Datadog Log Management.
    Automatically injects `dd.trace_id` and `dd.span_id` for APM log-to-trace correlation.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_payload: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }

        # Extract domain extras if present
        for attr in ("incident_id", "asset_id", "train_id", "fleet_id", "case_id", "actor", "source"):
            if hasattr(record, attr):
                log_payload[attr] = getattr(record, attr)

        # Inject Datadog APM trace correlation
        tracer = get_tracer()
        span = None
        try:
            span = tracer.current_span()
        except Exception:
            span = None

        if span is not None:
            trace_id = getattr(span, "trace_id", None)
            span_id = getattr(span, "span_id", None)
            log_payload["dd.trace_id"] = str(trace_id) if trace_id is not None else "0"
            log_payload["dd.span_id"] = str(span_id) if span_id is not None else "0"
        else:
            log_payload["dd.trace_id"] = "0"
            log_payload["dd.span_id"] = "0"

        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_payload, ensure_ascii=False)


def setup_datadog_logging(
    logger_name: str = "compressorguard",
    level: int = logging.INFO
) -> logging.Logger:
    """Configures structured Datadog JSON logging for the application."""
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # Avoid duplicate handlers
    if not any(isinstance(h.formatter, DatadogJSONFormatter) for h in logger.handlers):
        handler = logging.StreamHandler()
        handler.setFormatter(DatadogJSONFormatter())
        logger.addHandler(handler)

    return logger
