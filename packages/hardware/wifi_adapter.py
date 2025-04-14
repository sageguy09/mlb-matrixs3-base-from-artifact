"""
WiFiManager adapter to provide a consistent API between
different WiFi implementations.
"""

from packages.utils.network import WiFiManager as BaseWiFiManager
from packages.utils.logger import Logger

class WiFiManagerAdapter:
    """
    Adapter class to make the traditional WiFiManager use the
    same API as the ESP32-SPI based manager.
    """
    
    def __init__(self, status_pixel=None, ssid=None, password=None, debug=False):
        """
        Initialize adapter with same parameters as ESPWiFiManager.
        
        Args:
            status_pixel: NeoPixel for status indication (saved but not used)
            ssid: WiFi network name (passed to base manager)
            password: WiFi password (passed to base manager)
            debug: Enable debug logging
        """
        self.log = Logger("WiFiAdapter", debug=debug)
        self.debug = debug
        self.status_pixel = status_pixel
        
        # Initialize the base WiFiManager
        self.wifi_manager = BaseWiFiManager(ssid=ssid, password=password, debug=debug)
        
    def _set_status_pixel(self, color):
        """Set status pixel color if available."""
        if self.status_pixel:
            try:
                self.status_pixel[0] = color
            except Exception as e:
                self.log.error(f"Error setting status pixel: {e}")
    
    def connect(self, ssid=None, password=None, max_attempts=3):
        """Connect to WiFi network using the base manager.
        
        Args:
            ssid: WiFi network name (override if provided)
            password: WiFi password (override if provided)
            max_attempts: Maximum number of connection attempts
            
        Returns:
            True if connection successful, False otherwise
        """
        # Set yellow status during connection
        self._set_status_pixel((255, 255, 0))
        
        # If new credentials provided, update the base manager
        if ssid and password:
            self.wifi_manager.ssid = ssid
            self.wifi_manager.password = password
            
        # Attempt connection
        result = self.wifi_manager.connect(max_attempts)
        
        # Update status pixel based on result
        if result:
            self._set_status_pixel((0, 255, 0))  # Green for success
        else:
            self._set_status_pixel((255, 0, 0))  # Red for failure
            
        return result
        
    def disconnect(self):
        """Disconnect from WiFi network."""
        return self.wifi_manager.disconnect()
    
    def is_connected(self):
        """Check if WiFi is currently connected."""
        return self.wifi_manager.is_connected()
    
    def get_signal_strength(self):
        """Get WiFi signal strength (RSSI) - not supported in base manager."""
        try:
            return -50  # Dummy value as base manager doesn't support this
        except Exception:
            return None
    
    def get_ip_address(self):
        """Get device IP address."""
        try:
            return str(self.wifi_manager.wifi.ipv4_address)
        except Exception:
            return None
    
    def get_mac_address(self):
        """Get device MAC address - not well supported in base manager."""
        try:
            mac_bytes = self.wifi_manager.wifi.mac_address
            return ':'.join(['{:02x}'.format(b) for b in mac_bytes])
        except Exception:
            return None
    
    def fetch(self, url, headers=None, timeout=30):
        """
        Fetch data from URL - delegate to Network class.
        This is not directly implemented in the adapter.
        """
        self.log.error("fetch() not implemented in WiFiManagerAdapter")
        return (False, None)
