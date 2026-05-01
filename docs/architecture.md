# Architecture

Data flow:

Application (Python)
→ OpenTelemetry SDK
→ OTLP HTTP (4318)
→ OpenTelemetry Collector
→ Prometheus / Loki / Tempo
→ Grafana

---

## Key idea

- SDK emits telemetry
- Collector routes data
- Grafana visualizes

---

## Why this design works

- decouples apps from backend
- standard OTLP format
- portable across stacks