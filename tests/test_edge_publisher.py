"""Edge gateway publish path in scripts/stream_telemetry.py.

These are the only assertions that make the "module IoT" claim honest: the
producer must never lose frames and must never crash when the broker is
absent, because that is the state this repository was developed in.
"""

import importlib.util
import json
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
