#!/bin/bash

echo "Generating sample traffic..."

for i in {1..20}
do
  curl -s http://localhost:8000/test >/dev/null
  echo "Request $i sent"
  sleep 1
done

echo "Done."