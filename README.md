# Kiln Watchdog

A simple kiln watchdog service to read temperature from MAX31855 and K-type probe on RPI.

### Features

- Sends median temperature in desired timeframe
-  LED status notifications (success, error, etc.)
- Remote configuration - read intervals and upload thresholds (Supabase integration)
- Automatic startup on Raspberry Pi boot
- Modular design with pluggable data service for easy backend replacement

### Architecture

The project is designed with modularity in mind:

- `KilnWatchdog.py`: Main script for reading temperature and controlling hardware
- `DataService.py`: Service layer that abstracts all data operations
- `config.py`: Configuration settings (not tracked in git)

The data service provides a clean interface for:
1. Fetching remote configuration
2. Uploading temperature data periodically

I use Supabase database for convinience.

## Configuration

The project uses two levels of configuration:

1. **Local configuration** (`config.py`): Contains sensitive information like API keys and pin configuration.
2. **Remote configuration** (Supabase): Contains operational parameters like read intervals

### Local Configuration

Create a copy of `config.example.py` named `config.py` with your actual values for `SUPABASE_URL` and `SUPABASE_KEY`. Update pin configuration according to your preference.

### Remote Configuration (Supabase)

You should have the following tables in your Supabase project:

#### Table `rpi_config`:
- `device_id` (text): Set to the value that corresponds to your device
- `read_interval` (float): Time in seconds between temperature readings
- `readings_before_upload` (int): Number of readings before calculating median and uploading

#### Table `temperature_readings`:
- `device_id` (text): ID of the device that sent the data
- `temperature` (float): Measured temperature
- `timestamp` (bigint): UNIX timestamp when the temperature was measured

## Steps to install on RPi
```
sudo apt-get update
sudo apt-get dist-upgrade
git clone https://github.com/jovanovic-filip/kiln-watchdog
cd kiln-watchdog
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp config.example.py config.py
nano config.py  # Enter your API credentials, device ID and update PIN layout
python3 KilnWatchdog.py
```

## Running the script on Raspberry Pi startup

To set up the script to run automatically at Raspberry Pi startup, simply run:

```bash
# Make the setup script executable
chmod +x setup_autostart.sh
chmod +x run_kiln_watchdog.sh

# Run the setup script
./setup_autostart.sh
```

## LED Notifications

The script uses two LEDs for status notifications, one for error and other one for success.

## Logging

Logs are written to standard output. You can view them in real-time using systemd journal:

```bash
sudo journalctl -u kiln-watchdog.service -f
```

## Checking Service Status

To check if the service is running correctly:

```bash
sudo systemctl status kiln-watchdog.service
```

To view service logs:

```bash
sudo journalctl -u kiln-watchdog.service
```

## TODOs:
- Error to readings ratio to be uploaded (confidence ratio)
- Calibration parameters for probe
- Alarm output in case of limit temperature is reached
