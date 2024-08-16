#!/bin/bash

# Script for setting up automatic startup of KilnWatchdog
# when Raspberry Pi boots

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WRAPPER_SCRIPT="$SCRIPT_DIR/run_kiln_watchdog.sh"
LOG_PATH="$SCRIPT_DIR/kiln_watchdog.log"

# Check if config file exists
if [ ! -f "$SCRIPT_DIR/config.py" ]; then
    echo "ERROR: config.py file not found!"
    echo "Please create config.py based on config.example.py with your API key and URL first."
    exit 1
fi

# Ensure wrapper script is executable
chmod +x "$WRAPPER_SCRIPT"

# Set up systemd service
echo "Setting up automatic startup using systemd..."
SERVICE_FILE="/etc/systemd/system/KilnWatchdog.service"

# Create systemd service file
cat > /tmp/KilnWatchdog.service << EOL
[Unit]
Description=Kiln Watchdog
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR
ExecStart=$WRAPPER_SCRIPT
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

# Create empty log file if it doesn't exist and set permissions
touch "$LOG_PATH"
chmod 644 "$LOG_PATH"
chown "$USER:$(id -gn $USER)" "$LOG_PATH"

# Copy file to system location
sudo mv /tmp/KilnWatchdog.service $SERVICE_FILE

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable KilnWatchdog.service
sudo systemctl restart KilnWatchdog.service

echo "Successfully set up automatic startup using systemd!"
echo "Service status:"
sudo systemctl status KilnWatchdog.service --no-pager

echo
echo "Setup complete! Your script will run automatically at system startup."
echo "Logs will be written to: $LOG_PATH"
echo "You can view live logs using: tail -f $LOG_PATH"
echo "NOTE: You need to reboot your Raspberry Pi for changes to take effect." 