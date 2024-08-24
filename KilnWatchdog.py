import sys
import time
from typing import Dict, Union, List, Any
import board
import adafruit_max31855
import adafruit_bitbangio as bitbangio
import digitalio
import statistics
from DataService import dataService

# Force unbuffered output for logging
sys.stdout.reconfigure(line_buffering=True)

try:
    from config import (
        SCLK_PIN, MISO_PIN, CS_PIN, MOSI_PIN, LED_PIN_OK, LED_PIN_ERROR, ALARM_PIN
    )
except ImportError:
    print("Error: config.py file not found.")
    print("Please create config.py based on config.example.py with your PIN setup.")
    sys.exit(1)

remote_config = dataService.get_config()
READ_INTERVAL_SECONDS: float = remote_config.get('read_interval', 3.0)
READINGS_BEFORE_UPLOAD: int = remote_config.get('readings_before_upload', 20)
MAX_ALLOWED_TEMPERATURE: int = remote_config.get('max_temperature', None)

def get_board_pin(pin_number: int):
    return getattr(board, f"D{pin_number}")

spi_sclk = get_board_pin(SCLK_PIN)
spi_miso = get_board_pin(MISO_PIN)
spi_cs = get_board_pin(CS_PIN)
spi_mosi = get_board_pin(MOSI_PIN)
led_ok = digitalio.DigitalInOut(get_board_pin(LED_PIN_OK))
led_error = digitalio.DigitalInOut(get_board_pin(LED_PIN_ERROR))
alarm_out = digitalio.DigitalInOut(get_board_pin(ALARM_PIN))

spi = bitbangio.SPI(spi_sclk, spi_mosi, spi_miso)
led_ok.direction = digitalio.Direction.OUTPUT
led_error.direction = digitalio.Direction.OUTPUT
alarm_out.direction = digitalio.Direction.OUTPUT

cs = digitalio.DigitalInOut(spi_cs)

sensor = adafruit_max31855.MAX31855(spi, cs)

def notifySuccess(blinkCount: int = 1):
    blink(led_ok, blinkCount)

def notifyError(errorType: str = "general"):
    if errorType == "send":
        blink(led_error, blinkCount = 5)
    elif errorType == "connection":
        blink(led_error, blinkCount = 4)
    else:  # general error
        blink(led_error, blinkCount = 3)

def blink(output, blinkCount: int):
    duration = 0.1
    try:
        for _ in range(blinkCount):
            output.value = True
            time.sleep(duration)
            output.value = False
            time.sleep(duration)
    except Exception as e:
        print(f"Output GPIO error: {e}")
    finally:
        pass

def readTemperature() -> float:
    temperature = sensor.temperature_NIST
    return round(temperature, 2)

def uploadTemperature(
    temperature: float, 
    timestamp: int, 
    isAlarm: bool = False
) -> None:
    try:
        result = dataService.sendTemperature(temperature, timestamp, isAlarm)
        if result["success"]:
            notifySuccess(blinkCount = 5)
            print(f"Successfully sent: {temperature}°C at {timestamp}")
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
    print(f"MAX ALLOWED TEMPERATURE: {MAX_ALLOWED_TEMPERATURE}")

    # Test indicators
    blink(led_error, 3)
    blink(led_ok, 3)
    blink(alarm_out, 3)
   
    numberOfReads: int = 0
    temperatures: List[float] = []
    
    while True:
        try:
            timestamp: int = int(time.time())
            temperature: float = readTemperature()
            print(f" Temperature: {temperature} °C at: {timestamp}")

            while MAX_ALLOWED_TEMPERATURE != None and temperature > MAX_ALLOWED_TEMPERATURE:
                print("Temperature is over the limit, rising alarm!")
                alarm_out.value = True
                uploadTemperature(temperature, int(time.time()), isAlarm = True)
                time.sleep(READ_INTERVAL_SECONDS)
                temperature = readTemperature()
            alarm_out.value = False

            notifySuccess()
            
            temperatures.append(temperature)
            
            if numberOfReads >= READINGS_BEFORE_UPLOAD:
                medianTemperature: float = statistics.median(temperatures)
                uploadTemperature(medianTemperature, timestamp)
                numberOfReads = 0
                temperatures = []
            numberOfReads += 1
        except Exception as e:
            notifyError()
            print(f"Error: {e}")

        time.sleep(READ_INTERVAL_SECONDS)