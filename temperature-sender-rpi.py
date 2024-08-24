import sys
import time
import requests
from typing import Dict, Union, List
import board
import adafruit_max31855
import adafruit_bitbangio as bitbangio
import digitalio
import statistics

# Force unbuffered output for logging
sys.stdout.reconfigure(line_buffering=True)

try:
    from config import API_URL, API_KEY
except ImportError:
    print("Error: config.py file not found.")
    print("Please create config.py based on config.example.py with your API key and URL first.")
    sys.exit(1)

READ_INTERVAL_SECONDS: float = 3.0 
READINGS_BEFORE_UPLOAD: int = 20

spi_sclk = board.D22
spi_miso = board.D17
spi_cs = board.D27
spi_mosi = board.D10
spi = bitbangio.SPI(spi_sclk, spi_mosi, spi_miso)

led_pin = board.D8
led_pin.direction = digitalio.Direction.OUTPUT

cs = digitalio.DigitalInOut(spi_cs)

sensor = adafruit_max31855.MAX31855(spi, cs)

def notifyViaLed(blinkCount: int,  isShort: bool):
    on_time = 0.1 if isShort else 0.5
    off_time = 0.1 if isShort else 0.5
    try:
        for _ in range(blinkCount):
            led_pin.value = True
            time.sleep(on_time)
            led_pin.value = False
            time.sleep(off_time)
    except Exception as e:
        print(f"LED notification error: {e}")
    finally:
        pass

def readTemperature() -> float:
    temperature = sensor.temperature_NIST
    return round(temperature, 2)

def uploadTemperature(temperature: float, timestamp: int, humanTime: str) -> None:
    try:
        payload: Dict[str, Union[float, int]] = {
            "temperature": temperature,
            "timestamp": timestamp
        }
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "x-api-key": API_KEY
        }
        response = requests.post(API_URL, json=payload, headers=headers)

        if response.status_code == 200:
            notifyViaLed(blinkCount = 1, isShort = False)
            print(f"Successfully sent: {temperature}°C at {humanTime}")
        else:
            notifyViaLed(blinkCount = 4, isShort = True) 
            print(f"Failed to send data: {response.status_code} {response}")
    except Exception as e:
        notifyViaLed(blinkCount = 5, isShort = True) 
        print(f"Error sending data: {e}")

if __name__ == "__main__":
    print("Starting temperature monitoring and uploading...")
    numberOfReads: int = 0
    temperatures: List[float] = []
    
    while True:
        try:
            temperature: float = readTemperature()
            timestamp: int = int(time.time())
            humanTime: str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
            print(f" Temperature: {temperature} °C at: {humanTime}")
            
            temperatures.append(temperature)
            
            if numberOfReads >= READINGS_BEFORE_UPLOAD:
                medianTemperature: float = statistics.median(temperatures)
                uploadTemperature(medianTemperature, timestamp, humanTime)
                numberOfReads = 0
                temperatures = []
            numberOfReads += 1
        except Exception as e:
            notifyViaLed(blinkCount = 3, isShort = True)
            print(f"Error: {e}")

        time.sleep(READ_INTERVAL_SECONDS)