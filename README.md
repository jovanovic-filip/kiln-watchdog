A simple project to read temperature from max31855 and K-type probe on RPI.
There is a config file to add API_KEY and endpoint url to upload readout via POST method.

Endpoint shall accept `API_KEY` via `x-api-key` header and have the following data in body:
```
{
    "temperature": float,
    "timestamp": long
}
```

## Features

- Temperature monitoring using MAX31855 and K-type thermocouple
- LED status notifications (success, error, etc.)
- Remote configuration with Supabase integration (Configurable read intervals and upload thresholds)
- Temperature data median calculation for more reliable readings
- Automatic startup on Raspberry Pi boot

## TODOs:
- Error to readings ratio to be uploaded (confidence ratio)
- Calibration parameters for probe
- Device ID in remote config

## Configuration

The project uses two levels of configuration:

1. **Local configuration** (`config.py`): Contains sensitive information like API keys
2. **Remote configuration** (Supabase): Contains operational parameters like read intervals

### Local Configuration

Create a copy of `config.example.py` named `config.py` with your actual values:

```python
# API configuration
API_URL: str = "https://your-api-endpoint.com/api/save-temperature"
API_KEY: str = "your-api-key-here"

# Supabase configuration
SUPABASE_URL: str = "https://your-supabase-project-url.supabase.co"
SUPABASE_KEY: str = "your-supabase-anon-key" 

# Pin configuration - GPIO pin numbers
SCLK_PIN: int = 22
MISO_PIN: int = 17
CS_PIN: int = 27
MOSI_PIN: int = 10
LED_PIN: int = 8
```

### Remote Configuration (Supabase)

You need to create a table named `rpi_config` in your Supabase project with the following fields:
- `read_interval` (float): Time in seconds between temperature readings
- `readings_before_upload` (int): Number of readings before calculating median and uploading

## Steps to install on RPi
```
$ sudo apt-get update
$ sudo apt-get dist-upgrade
$ git clone https://github.com/jovanovic-filip/temperature-reader-rpi
$ cd temperature-reader-rpi
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

## Running the script on Raspberry Pi startup

To set up the script to run automatically at Raspberry Pi startup, simply run:

```bash
# Make the setup script executable
chmod +x setup_autostart.sh

# Run the setup script
./setup_autostart.sh
```

The script will automatically set up a systemd service to run the temperature monitoring script at startup. This is the most reliable method for ensuring your script runs properly when the Raspberry Pi boots.

After setup, you'll need to reboot your Raspberry Pi for the changes to take effect.

## LED Notifications

The script uses an LED for status notifications:

- 1 long blink: Successful temperature upload
- 4 short blinks: Failed to send data
- 5 short blinks: Error sending data
- 3 short blinks: Other errors

## Logging

Logs are written to `temperature.log` in the project directory. You can view them in real-time using:

```bash
tail -f temperature.log
```

## Checking Service Status

To check if the service is running correctly:

```bash
sudo systemctl status temperature-sender.service
```

To view service logs:

```bash
sudo journalctl -u temperature-sender.service
```
