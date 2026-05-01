# Troubleshooting

## No data in Grafana

Check:
- docker compose ps
- OTEL Collector running
- endpoint: http://localhost:4318

---

## Dashboards not loading

Check:
- Grafana volume mounts
- provisioning folder exists
- JSON files in /var/lib/grafana/dashboards

---

## Collector errors

Common issue:
- wrong exporter type (HTTP vs gRPC mismatch)

Fix:
- ensure OTLP HTTP exporter is used