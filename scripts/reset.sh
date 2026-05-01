#!/bin/bash

echo "Resetting Observability Stack..."

docker compose down -v
docker compose up -d

echo "Reset complete. All data cleared."