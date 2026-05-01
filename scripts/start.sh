#!/bin/bash

set -e

echo "Starting Observability Stack..."

docker compose up -d

echo "Waiting for services to stabilize..."
sleep 10

echo "Stack running:"
echo "- Grafana: http://localhost:3000"
echo "- OTEL Collector: http://localhost:4318"

echo "Run your app:"
echo "python charger_simulator.py"