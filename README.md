# 10-Minute Observability Kit (Docker + OpenTelemetry + Grafana)

A plug-and-play observability stack that gives you logs, metrics, and traces in under 10 minutes.

Built for developers who want production-style monitoring without setting up full DevOps infrastructure.

---

## What this is

This project gives you a complete working observability system:

- Metrics (Prometheus-compatible)
- Logs (OpenTelemetry → Loki-ready pipeline)
- Traces (OpenTelemetry distributed tracing)
- Grafana dashboards (prebuilt and auto-loaded)
- Example instrumented Python service

---

## What you get

- Preconfigured OpenTelemetry Collector
- Grafana with auto-provisioned dashboards
- Example Python service generating real telemetry
- Ready-to-use dashboards:
  - API Performance
  - Error Tracking
  - System Overview
  - Service Health
- Working alert-ready metric structure
- Docker-based one-command startup

---

## Architecture

Example App (Python)
→ OpenTelemetry SDK
→ OTLP HTTP Export (4318)
→ OpenTelemetry Collector
→ Prometheus / Loki / Tempo
→ Grafana Dashboards
→ Optional auto-injection
---

## Quick Start

1. Clone project

cd observability-kit

---

2. Configure environment

cp .env.example .env

Edit:

OTEL_ENDPOINT=http://localhost:4318
STATION_ID=station-001
LOCATION=chicago-demo

---

3. Start stack

docker compose up -d

---

4. Run example service

python charger_simulator.py

---

5. Open Grafana

http://localhost:3000

Login:
admin
admin

---

## Dashboards included

API Performance
- Request rate
- Latency (avg + p95)
- Throughput trends

Error Tracking
- Error rate
- Failure spikes
- Errors by endpoint

System Overview
- CPU usage
- Memory usage
- Network traffic

Service Health
- Uptime signal
- Request volume

---

## Project structure

observability-kit/
- docker-compose.yml
- .env.example
- charger_simulator.py
- grafana/
  - dashboards/
  - provisioning/
- otel/
  - otel-collector-config.yaml
- docs/
- scripts/

---

## How to use with your own app

1. Install OpenTelemetry SDK
2. Set:

OTEL_ENDPOINT=http://localhost:4318

3. Export:
- traces
- metrics
- logs

---

## Why this exists

Most observability setups fail because:
- too many tools
- too much configuration
- unclear starting point

This removes all setup complexity.

You get a working system immediately.

---

## Common issues

No data in Grafana:
- check collector is running
- verify OTLP endpoint http://localhost:4318

Dashboards missing:
- verify Grafana provisioning mounts

---

## License

MIT