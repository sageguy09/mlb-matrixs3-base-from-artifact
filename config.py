# config.py - Configuration settings for Matrix Portal S3 application

# WiFi Settings
WIFI = {
    "ssid": "your_wifi_ssid",
    "password": "your_wifi_password",
    "attempts": 3
}

# Matrix Display Settings
MATRIX = {
    "width": 64,
    "height": 32,
    "bit_depth": 6,
    "brightness": 0.8,  # 0.0-1.0 range
    "tile_rows": 1
}

# Application Settings
APP = {
    "debug": True,
    "enable_usb_drive": True,
    "scroll_speed": 0.03  # seconds between scroll steps
}

# Data Settings
DATA = {
    "currency": "USD",
    "source_url": "https://api.coindesk.com/v1/bpi/currentprice.json",
    "json_path": ["bpi", "USD", "rate_float"],
    "refresh_interval": 180,  # seconds between data refreshes
    "timeout": 10  # seconds before request timeout
}

# Load secrets from a separate file (if exists)
try:
    from secrets import secrets
    
    # Override config values with secrets if available
    if "wifi_ssid" in secrets and "wifi_password" in secrets:
        WIFI["ssid"] = secrets["wifi_ssid"]
        WIFI["password"] = secrets["wifi_password"]
    
except ImportError:
    # No secrets file found, using default values
    pass

# Safety checks
if WIFI["ssid"] == "your_wifi_ssid" or WIFI["password"] == "your_wifi_password":
    print("WARNING: Default WiFi credentials detected.")
    print("Update secrets.py or config.py with your actual WiFi credentials.")