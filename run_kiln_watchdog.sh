#!/bin/bash

# Wrapper script that runs the Kiln Watchdog and redirects output to log file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/kiln_watchdog.log"

echo "Starting Kiln Watchdog at $(date)" >> "$LOG_FILE"

# Force unbuffered output by setting environment variable and using -u flag
export PYTHONUNBUFFERED=1 
"$SCRIPT_DIR/venv/bin/python" -u "$SCRIPT_DIR/KilnWatchdog.py" >> "$LOG_FILE" 2>&1 