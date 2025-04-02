"""
ESP32-SPI based WiFi manager for MLB Scoreboard
Handles WiFi connectivity using the ESP32 co-processor
"""

import time
import gc
import board
import busio
import digitalio
import traceback
from adafruit_esp32spi import adafruit_esp32spi
import adafruit_requests
from packages.utils.logger import Logger

class ESPWiFiManager:
    """WiFi connection manager using ESP32-SPI."""
    
    def __init__(self, status_pixel=None, debug=False):
        """Initialize WiFi manager.
        
        Args:
            status_pixel: NeoPixel for status indication
            debug: Enable debug logging
        """
        self.log = Logger("ESP-WiFi", debug=debug)
        self.debug = debug
        self.status_pixel = status_pixel
        self.esp = None
        self.requests = None
        self.is_connected = False
        
        # Initialize ESP32 SPI
        try:
            # Configure ESP32 control pins
            esp32_cs = digitalio.DigitalInOut(board.ESP_CS)
            esp32_ready = digitalio.DigitalInOut(board.ESP_BUSY)
            esp32_reset = digitalio.DigitalInOut(board.ESP_RESET)
            
            # Initialize SPI bus
            spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
            
            # Create ESP control interface
            self.esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
            
            if self.debug:
                self.log.info(f"ESP32 firmware version: {self.esp.firmware_version}")
        
        except Exception as e:
            self.log.error(f"Failed to initialize ESP32: {e}")
            if self.debug:
                self.log.error(traceback.format_exc())
            
            # Try to recover with generic initialization
            self.esp = None
    
    def _set_status_pixel(self, color):
        """Set status pixel color if available."""
        if self.status_pixel:
            try:
                self.status_pixel[0] = color
            except Exception as e:
                self.log.error(f"Error setting status pixel: {e}")
    
    def connect(self, ssid=None, password=None, max_attempts=3):
        """Connect to WiFi network.
        
        Args:
            ssid: WiFi network name
            password: WiFi password
            max_attempts: Maximum number of connection attempts
            
        Returns:
            True if connection successful, False otherwise
        """
        if not self.esp:
            self.log.error("ESP32 not initialized")
            return False
            
        if self.is_connected:
            return True
            
        if not ssid or not password:
            self.log.error("WiFi credentials not provided")
            return False
        
        self.log.info(f"Connecting to {ssid}...")
        self._set_status_pixel((255, 255, 0))  # Yellow during connection
        
        # Make multiple attempts
        for attempt in range(max_attempts):
            try:
                self.log.info(f"Connection attempt {attempt+1}/{max_attempts}")
                
                # Connect to WiFi access point
                self.esp.connect_AP(ssid, password)
                
                # Check if connected
                if self.esp.is_connected:
                    self.is_connected = True
                    ip = self.esp.ip_address
                    self.log.info(f"Connected to {ssid} | IP: {self.esp.pretty_ip(ip)}")
                    
                    # Set up requests library
                    self._initialize_requests()
                    
                    # Green for success
                    self._set_status_pixel((0, 255, 0))
                    return True
                
            except Exception as e:
                self.log.error(f"Connection attempt {attempt+1} failed: {e}")
                if self.debug:
                    self.log.error(traceback.format_exc())
                self._set_status_pixel((255, 0, 0))  # Red for error
                time.sleep(2)  # Wait before retry
        
        self.log.error(f"Failed to connect to {ssid} after {max_attempts} attempts")
        return False
    
    def _initialize_requests(self):
        """Initialize requests library for HTTP access."""
        try:
            # First try the modern connection manager approach
            try:
                import adafruit_connection_manager
                pool = adafruit_connection_manager.get_radio_socketpool(self.esp)
                ssl_context = adafruit_connection_manager.get_radio_ssl_context(self.esp)
                self.requests = adafruit_requests.Session(pool, ssl_context)
                self.log.info("Using modern connection manager")
            except ImportError:
                # Fall back to legacy socket approach
                import adafruit_esp32spi.adafruit_esp32spi_socket as socket
                socket.set_interface(self.esp)
                self.requests = adafruit_requests.Session(socket, self.esp)
                self.log.info("Using legacy socket approach")
            
            return True
        except Exception as e:
            self.log.error(f"Failed to initialize requests: {e}")
            if self.debug:
                self.log.error(traceback.format_exc())
            return False
    
    def disconnect(self):
        """Disconnect from WiFi network."""
        if self.is_connected:
            try:
                # Note: ESP32-SPI doesn't have a direct disconnect method
                # Reset ESP to disconnect
                self.esp.reset()
                self.is_connected = False
                self.log.info("Disconnected from WiFi")
            except Exception as e:
                self.log.error(f"Error disconnecting: {e}")
    
    def is_connected(self):
        """Check if WiFi is currently connected.
        
        Returns:
            bool: True if connected, False otherwise
        """
        try:
            if not self.esp:
                return False
            return self.esp.is_connected
        except Exception as e:
            self.log.error(f"Error checking connection: {e}")
            return False
    
    def get_signal_strength(self):
        """Get WiFi signal strength (RSSI).
        
        Returns:
            int: Signal strength in dBm or None if not connected
        """
        try:
            if self.esp and self.esp.is_connected:
                return self.esp.rssi
            return None
        except Exception as e:
            self.log.error(f"Error getting signal strength: {e}")
            return None
    
    def get_ip_address(self):
        """Get device IP address.
        
        Returns:
            str: IP address or None if not connected
        """
        try:
            if self.esp and self.esp.is_connected:
                ip = self.esp.ip_address
                return self.esp.pretty_ip(ip)
            return None
        except Exception as e:
            self.log.error(f"Error getting IP address: {e}")
            return None
    
    def get_mac_address(self):
        """Get device MAC address.
        
        Returns:
            str: MAC address or None if not available
        """
        try:
            if self.esp:
                mac = self.esp.MAC_address
                # Format as XX:XX:XX:XX:XX:XX
                return ":".join(["{:02X}".format(b) for b in mac])
            return None
        except Exception as e:
            self.log.error(f"Error getting MAC address: {e}")
            return None
    
    def fetch(self, url, headers=None, timeout=30):
        """Fetch data from URL using HTTP GET.
        
        Args:
            url: URL to fetch
            headers: Optional HTTP headers
            timeout: Request timeout in seconds
            
        Returns:
            tuple: (success, data) where data is parsed JSON if successful
        """
        if not self.requests:
            self.log.error("Requests library not initialized")
            return (False, None)
            
        if not self.is_connected:
            self.log.error("WiFi not connected")
            return (False, None)
        
        try:
            self._set_status_pixel((0, 0, 255))  # Blue during fetch
            
            if headers is None:
                headers = {}
                
            # Add default headers
            if "User-Agent" not in headers:
                headers["User-Agent"] = "MLB-Scoreboard/1.0 CircuitPython"
            
            response = self.requests.get(url, headers=headers, timeout=timeout)
            
            self.log.debug(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                # Return parsed JSON
                data = response.json()
                response.close()
                
                # Reset status pixel
                self._set_status_pixel((0, 255, 0))  # Green for success
                return (True, data)
            else:
                self.log.error(f"HTTP error: {response.status_code}")
                response.close()
                
                # Reset status pixel
                self._set_status_pixel((255, 0, 0))  # Red for error
                return (False, None)
                
        except Exception as e:
            self.log.error(f"Error fetching data: {e}")
            if self.debug:
                self.log.error(traceback.format_exc())
                
            # Reset status pixel
            self._set_status_pixel((255, 0, 0))  # Red for error
            return (False, None)
