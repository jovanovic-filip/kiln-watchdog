# Example configuration file
# Create a copy of this file named 'config.py' and fill in your actual values

# Unique device ID
DEVICE_ID: str = "your_device_uuid_here"

# API configuration
API_URL: str = "https://your-api-endpoint.com/api/save-temperature"
API_KEY: str = "your-api-key-here"

# Supabase configuration
SUPABASE_URL: str = "https://your-supabase-project-url.supabase.co"
SUPABASE_KEY: str = "your-supabase-anon-key" 

# Pin configuration (GPIO)
SCLK_PIN: int = 22
MISO_PIN: int = 17
CS_PIN: int = 27
MOSI_PIN: int = 10
LED_PIN_OK: int = 8    
LED_PIN_ERROR: int = 7