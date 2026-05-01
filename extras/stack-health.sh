#!/bin/bash

echo "Checking stack health..."

docker compose ps

echo ""
echo "Testing endpoints..."

curl -s http://localhost:4318/v1/traces && echo "OTEL traces OK"
curl -s http://localhost:4318/v1/metrics && echo "OTEL metrics OK"

echo "Done."