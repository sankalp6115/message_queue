#!/bin/bash
for i in {1..4}; do
    echo "Starting Worker #$i..."
    uv run worker.py & 
done

wait