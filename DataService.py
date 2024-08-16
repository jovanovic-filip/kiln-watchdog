from typing import Dict, Any
import sys
import requests
from supabase import create_client

class DataService:
    
    def __init__(self, device_id: str, api_url: str, api_key: str, 
                 supabase_url: str, supabase_key: str):
      
        self.device_id = device_id
        self.api_url = api_url
        self.api_key = api_key
        
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
    
    def sendTemperature(self, temperature: float, timestamp: int) -> Dict[str, Any]:
        try:
            payload = {
                "device_id": self.device_id,
                "temperature": temperature,
                "timestamp": timestamp
            }
            
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers)
            
            return {
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response": response.text
            }
        except Exception as e:
            print(f"Error sending data: {e}")
            return {
                "success": False,
                "error": str(e)
            }

def createDataService(**config) -> DataService:
    return DataService(
        device_id=config.get("device_id", ""),
        api_url=config.get("api_url", ""),
        api_key=config.get("api_key", ""),
        supabase_url=config.get("supabase_url", ""),
        supabase_key=config.get("supabase_key", "")
    ) 