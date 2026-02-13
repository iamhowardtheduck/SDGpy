#!/bin/bash

# Command to run
CMD="python3 -m venv venv && source venv/bin/activate && pip install -r /root/SDGpy/requirements.txt && python /root/SDGpy/sdg.py /root/SDGpy/Tracks/netflow.yml"

# Infinite loop
while true; do
    echo "[INFO] Starting process..."
    $CMD &
    PID=$!

    # Let it run for 5 seconds
    sleep 5

    echo "[INFO] Killing process (PID: $PID)..."
    kill -9 $PID 2>/dev/null

    # Wait 30 seconds before restarting
    echo "[INFO] Waiting 30 seconds before restart..."
    sleep 30
done
