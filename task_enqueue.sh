#!/usr/bin/env bash

# Usage: ./task_enqueue.sh [seconds]
# Example: ./task_enqueue.sh 10

SECONDS="${1:-5}"

curl -X POST "http://localhost:8000/api/jobs" \
  -H "Content-Type: application/json" \
  -d "{
    \"type\": \"sleep\",
    \"payload\": {
      \"seconds\": ${SECONDS}
    }
  }"
echo ""