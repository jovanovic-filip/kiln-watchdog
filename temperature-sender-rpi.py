import sys
import time
import requests
from typing import Dict, Union, List
import board
import adafruit_max31855
import adafruit_bitbangio as bitbangio
import digitalio
import statistics
from supabase import create_client, Client

# Force unbuffered output for logging
sys.stdout.reconfigure(line_buffering=True)

try:
    from config import (
        API_URL, API_KEY, 
        SUPABASE_URL, SUPABASE_KEY, 
        SCLK_PIN, MISO_PIN, CS_PIN, MOSI_PIN, LED_PIN
    )
except ImportError:
    print("Error: config.py file not found.")
    print("Please create config.py based on config.example.py with your API key, URL and Supabase credentials.")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def getRemoteSupabaseConfig():
    try:
        response = supabase.table('rpi_config').select('*').execute()
        if response.data and len(response.data) > 0:
            config = response.data[0]
            return config
        else:
            print("No configuration found in Supabase")
            sys.exit(1)
    except Exception as e:
        print(f"Error fetching configuration from Supabase: {e}")
        sys.exit(1)

remoteConfig = getRemoteSupabaseConfig()
READ_INTERVAL_SECONDS = remoteConfig.get('read_interval', 3.0)
READINGS_BEFORE_UPLOAD = remoteConfig.get('readings_before_upload', 20)


def get_board_pin(pin_number: int):
    return getattr(board, f"D{pin_number}")

spi_sclk = get_board_pin(SCLK_PIN)
spi_miso = get_board_pin(MISO_PIN)
spi_cs = get_board_pin(CS_PIN)
spi_mosi = get_board_pin(MOSI_PIN)
led_pin = digitalio.DigitalInOut(get_board_pin(LED_PIN))

spi = bitbangio.SPI(spi_sclk, spi_mosi, spi_miso)
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
    print(f"READ INTERVAL SECONDS: {READ_INTERVAL_SECONDS}")
    print(f"READINGS BEFORE UPLOAD: {READINGS_BEFORE_UPLOAD}")
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