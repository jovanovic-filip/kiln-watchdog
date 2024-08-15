A script to read temperature from max31855 and K-type probe on RPI.
There is a config file to add API_KEY and endpoint url to upload readout via POST method.

Endpoint shall accept `API_KEY` via `x-api-key` header and have the following data in body:
```
{
    "temperature": float,
    "timestamp": long
}
```

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
