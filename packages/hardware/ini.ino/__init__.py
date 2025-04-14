"""
Network package for MLB Scoreboard
Provides networking utilities and connection management
"""

# Import ESP32-SPI based WiFi if available
try:
    from .esp_wifi import ESPWiFiManager
    print("ESP32-SPI WiFi manager successfully imported")
except ImportError as e:
    print(f"Failed to import ESP32-SPI WiFi manager: {e}")
    ESPWiFiManager = None
    
    # Try to import the adapter
    try:
        from .wifi_adapter import WiFiManagerAdapter as ESPWiFiManager
        print("Using WiFiManager adapter instead")
    except ImportError:
        print("WiFiManager adapter not available")
