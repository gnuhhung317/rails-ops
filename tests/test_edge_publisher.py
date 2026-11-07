"""Edge gateway publish path in scripts/stream_telemetry.py.

These are the only assertions that make the "module IoT" claim honest: the
producer must never lose frames and must never crash when the broker is
absent, because that is the state this repository was developed in.
"""

import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

_MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "stream_telemetry.py"


@pytest.fixture(scope="module")
def producer():
    spec = importlib.util.spec_from_file_location("stream_telemetry", _MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FRAMES = [{"sensor": "DV_pressure", "value": 6.4 + i, "timestamp": "2020-06-05T09:50:39"} for i in range(3)]


class RecordingClient:
    def __init__(self):
        self.calls = []

    def publish(self, topic, payload, qos=0):
        self.calls.append((topic, json.loads(payload), qos))

    def loop_start(self):
        pass

    def loop_stop(self):
        pass

    def disconnect(self):
        pass


def test_no_broker_configured_buffers_everything(producer):
    pub = producer.EdgePublisher(None, "metro-line-1", "APU-COMP-01")
    assert pub.client is None
    for frame in FRAMES:
        pub.publish(frame)
    assert pub.published == 0
    assert len(pub.buffer) == len(FRAMES)


def test_buffer_is_bounded_and_keeps_newest(producer):
    pub = producer.EdgePublisher(None, "metro-line-1", "APU-COMP-01", buffer_size=2)
    for frame in FRAMES:
        pub.publish(frame)
    assert len(pub.buffer) == 2
    assert pub.buffer[-1] is FRAMES[-1]


def test_topic_follows_edge_contract(producer):
    pub = producer.EdgePublisher(None, "metro-line-1", "APU-COMP-01")
    assert pub.topic == "railops/metro-line-1/APU-COMP-01/telemetry"


def test_live_client_drains_buffer_at_qos1(producer):
    pub = producer.EdgePublisher(None, "metro-line-1", "APU-COMP-01")
    for frame in FRAMES:
        pub.publish(frame)
    pub.client = RecordingClient()
    pub.publish(FRAMES[0])
    assert pub.published == 4
    assert pub.buffer == []
    topics, payloads, qoss = zip(*pub.client.calls)
    assert set(topics) == {pub.topic}
    assert set(qoss) == {1}
    assert payloads[0]["timestamp"] == "2020-06-05T09:50:39"


def test_unreachable_broker_degrades_instead_of_crashing(producer):
    """Real paho-mqtt client against a closed port: the store-and-forward path."""
    pytest.importorskip("paho.mqtt.client", reason="paho-mqtt not installed")
    pub = producer.EdgePublisher("tcp://127.0.0.1:18830", "metro-line-1", "APU-COMP-01")
    pub.publish(FRAMES[0])
    assert pub.published == 0
    assert len(pub.buffer) == 1
    pub.close()


class _RegimeEnum:
    value = "LOADED"


class _Point:
    """One MetroPT-3 row shaped like TelemetryPoint, without importing the engine."""

    asset_id = "APU-COMP-01"
    timestamp = datetime(2020, 6, 5, 9, 40, 5, tzinfo=timezone.utc)
    regime = _RegimeEnum()
    tp2_bar = -0.012
    tp3_bar = 9.278
    h1_bar = 9.264
    dv_pressure_bar = -0.02
    reservoirs_bar = 9.278
    oil_temp_c = 66.25
    motor_current_a = 0.0425
    comp_val = 1.0
    dv_electric = 0.0
    towers_val = 1.0
    mpg_val = 1.0
    lps_active = 0.0
    pressure_switch = 1.0
    oil_level_low = 1.0
    caudal_impulses = 1.0


def test_storage_document_is_mongod_shaped(producer):
    """Against a real Time Series collection the producer used to die here with
    code 2 ("'timestamp' must be present and contain a valid BSON UTC datetime").
    The emulator accepted the ISO string, so only a real server could reveal it."""
    doc = producer._doc_from(_Point(), scenario_id="failure_3")
    assert isinstance(doc["timestamp"], datetime), "timeField must be a datetime, not a string"
    assert doc["timestamp"].tzinfo is not None
    assert doc["metadata"]["asset_id"] == "APU-COMP-01"
    assert doc["metadata"]["scenario"] == "failure_3"
    assert doc["dv_pressure_bar"] == -0.02


def test_storage_document_keeps_both_clocks(producer):
    doc = producer._doc_from(_Point())
    assert doc["event_time"] == "2020-06-05T09:40:05+00:00"
    assert doc["simulation_time"] != doc["event_time"]


def test_edge_frame_stays_json_serialisable(producer):
    frame = producer._frame_from(_Point())
    assert json.dumps(frame), "the MQTT payload must never carry a raw datetime"
    assert frame["event_time"] == "2020-06-05T09:40:05+00:00"
    assert "timestamp" not in frame
