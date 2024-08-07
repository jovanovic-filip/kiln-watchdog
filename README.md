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
