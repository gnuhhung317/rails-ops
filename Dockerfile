# RailOps VN — CompressorGuard console image.
#
#   docker compose up --build console     # http://localhost:8000
#   docker compose run --rm verify        # MongoDB Time Series proof, see below
#
# The image is built from files that are IN git, so `git clone` + this build works
# on a clean machine. It ships dataset/MetroPT3-demo-slice.csv — 286,855 real
# MetroPT-3 rows covering the Isolation-Forest baseline month and every scenario
# window (scripts/build_demo_slice.py). Verified: the frozen golden-path artifact
# regenerated from this slice is byte-identical to the one from the full
# 1,516,948-row CSV. To run on the full file, download it (README → Data source)
# and either set TELEMETRY_CSV or mount it over /app/dataset.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MONGODB_URI=mongodb://mongo:27017 \
    MONGODB_DB_NAME=compressorguard \
    MQTT_BROKER=tcp://mosquitto:1883

WORKDIR /app

COPY requirements.txt ./
# datadog/ddtrace are pinned for observability; the app degrades to dropped metrics
# with a warning when no agent is reachable, so the build needs no network beyond pip.
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY scripts ./scripts
COPY datadog ./datadog
COPY dataset/MetroPT3-demo-slice.csv ./dataset/
COPY README.md run_demo.py ./

EXPOSE 8000
CMD ["uvicorn", "src.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
