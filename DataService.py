from typing import Dict, Any
import sys
from supabase import create_client

class DataService:
    
    def __init__(self, device_id: str, supabase_url: str, supabase_key: str):
      
        self.device_id = device_id
        
        try:
            self.supabase = create_client(supabase_url, supabase_key)
        except Exception as e:
            print(f"Error initializing Supabase client: {e}")
            sys.exit(1)
    
    def get_config(self) -> Dict[str, Any]:
        try:
            response = self.supabase.table('device_config').select('*').eq('device_id', self.device_id).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]
            else:
                print(f"No configuration found for device ID: {self.device_id}")
                sys.exit(1)
        except Exception as e:
            print(f"Error fetching configuration from Supabase: {e}")
            sys.exit(1)
    
    def sendTemperature(self, temperature: float, timestamp: int, isAlarm: bool = False) -> Dict[str, Any]:
        try:
            data = {
                "device_id": self.device_id,
                "temperature": temperature,
                "timestamp": timestamp,
                "isAlarm": isAlarm,
            }
            response = self.supabase.table('temperature_readings').insert(data).execute()
            return {
                "success": True,
                "response": "Data saved to Supabase"
            }
        except Exception as e:
            print(f"Error sending data to Supabase: {e}")
            return {
                "success": False,
                "error": str(e)
            }

def createDataService(**config) -> DataService:
    return DataService(
        device_id=config.get("device_id", ""),
        supabase_url=config.get("supabase_url", ""),
        supabase_key=config.get("supabase_key", "")
    ) 

try:
    from config import (
        DEVICE_ID, SUPABASE_URL, SUPABASE_KEY
    )
    dataService = createDataService(
        device_id = DEVICE_ID, 
        supabase_url = SUPABASE_URL, 
        supabase_key = SUPABASE_KEY
    )
except ImportError:
    print("Error: config.py file not found.")
    print("Please create config.py based on config.example.py with your Supabase credentials.")
    sys.exit(1) 