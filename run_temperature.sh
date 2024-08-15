#!/bin/bash

# Wrapper script that runs the temperature monitoring script and redirects output to log file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/temperature.log"

echo "Starting temperature monitoring at $(date)" >> "$LOG_FILE"

# Force unbuffered output by setting environment variable and using -u flag
export PYTHONUNBUFFERED=1 
"$SCRIPT_DIR/venv/bin/python" -u "$SCRIPT_DIR/temperature-sender-rpi.py" >> "$LOG_FILE" 2>&1 