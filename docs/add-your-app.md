# Add Your Own Application

To instrument your app:

## 1. Install OpenTelemetry SDK

pip install opentelemetry-sdk opentelemetry-exporter-otlp

---

## 2. Set environment variable

OTEL_ENDPOINT=http://localhost:4318

---

## 3. Configure exporter

Use OTLP HTTP exporter:

- Traces → /v1/traces
- Metrics → /v1/metrics
- Logs → /v1/logs

---

## 4. Recommended setup

- service.name = your app name
- environment = dev/staging/prod