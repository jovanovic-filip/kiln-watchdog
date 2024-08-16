import sys
import time
from typing import Dict, Union, List, Any
import board
import adafruit_max31855
import adafruit_bitbangio as bitbangio
import digitalio
import statistics
from DataService import createDataService

# Force unbuffered output for logging
sys.stdout.reconfigure(line_buffering=True)

try:
    from config import (
        DEVICE_ID, API_URL, API_KEY, 
        SUPABASE_URL, SUPABASE_KEY, 
        SCLK_PIN, MISO_PIN, CS_PIN, MOSI_PIN, LED_PIN_OK, LED_PIN_ERROR
    )
except ImportError:
    print("Error: config.py file not found.")
    print("Please create config.py based on config.example.py with your API key, URL and Supabase credentials.")
    sys.exit(1)

dataService = createDataService(
    device_id = DEVICE_ID, 
    api_url = API_URL, 
    api_key = API_KEY,
    supabase_url = SUPABASE_URL, 
    supabase_key = SUPABASE_KEY
)

remote_config = dataService.get_config()
READ_INTERVAL_SECONDS = remote_config.get('read_interval', 3.0)
READINGS_BEFORE_UPLOAD = remote_config.get('readings_before_upload', 20)

def get_board_pin(pin_number: int):
    return getattr(board, f"D{pin_number}")

spi_sclk = get_board_pin(SCLK_PIN)
spi_miso = get_board_pin(MISO_PIN)
spi_cs = get_board_pin(CS_PIN)
spi_mosi = get_board_pin(MOSI_PIN)
led_pin_ok = digitalio.DigitalInOut(get_board_pin(LED_PIN_OK))
led_pin_error = digitalio.DigitalInOut(get_board_pin(LED_PIN_ERROR))

spi = bitbangio.SPI(spi_sclk, spi_mosi, spi_miso)
led_pin_ok.direction = digitalio.Direction.OUTPUT
led_pin_error.direction = digitalio.Direction.OUTPUT

cs = digitalio.DigitalInOut(spi_cs)

sensor = adafruit_max31855.MAX31855(spi, cs)

def notifySuccess(blinkCount: int = 1):
    notifyViaLed(blinkCount)

def notifyError(errorType: str = "general"):
    if errorType == "send":
        notifyViaLed(blinkCount = 5)
    elif errorType == "connection":
        notifyViaLed(blinkCount = 4)
    else:  # general error
        notifyViaLed(blinkCount = 3)

def notifyViaLed(blinkCount: int):
    duration = 0.1
    try:
        for _ in range(blinkCount):
            led_pin_ok.value = True
            time.sleep(duration)
            led_pin_ok.value = False
            time.sleep(duration)
    except Exception as e:
        print(f"LED notification error: {e}")
    finally:
        pass

def readTemperature() -> float:
    temperature = sensor.temperature_NIST
    return round(temperature, 2)

def uploadTemperature(temperature: float, timestamp: int, humanTime: str) -> None:
    try:
        result = dataService.sendTemperature(temperature, timestamp)
        
        if result["success"]:
            notifySuccess(blinkCount = 5)
            print(f"Successfully sent: {temperature}°C at {humanTime}")
        else:
            notifyError("connection")
            print(f"Failed to send data: {result.get('status_code')} {result.get('response')}")
    except Exception as e:
        notifyError()
        print(f"Error sending data: {e}")

if __name__ == "__main__":
    print("Starting temperature monitoring and uploading...")
    print(f"READ INTERVAL SECONDS: {READ_INTERVAL_SECONDS}")
    print(f"READINGS BEFORE UPLOAD: {READINGS_BEFORE_UPLOAD}")
    numberOfReads: int = 0
    temperatures: List[float] = []
    
    while True:
        try:
            temperature: float = readTemperature()
            notifySuccess()
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
            notifyError()
            print(f"Error: {e}")

        time.sleep(READ_INTERVAL_SECONDS)