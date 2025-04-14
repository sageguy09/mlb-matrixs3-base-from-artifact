# network/wifi_manager.py - WiFi and network management for Matrix Portal S3

import time
import wifi
import socketpool
import adafruit_requests
import ssl
import gc

class WiFiManager:
    """
    Manages WiFi connectivity and network requests for Matrix Portal S3
    """
    
    def __init__(self, status_led=None, debug=False):
        """
        Initialize the WiFi manager.
        
        Args:
            status_led: Optional DigitalInOut object for status indication
            debug: Enable debug output
        """
        self.status_led = status_led
        self.debug = debug
        self.connected = False
        self.requests_session = None
        self.pool = None
    
    def log(self, message):
        """Print debug messages if debug mode enabled"""
        if self.debug:
            print(f"[WiFiManager] {message}")
    
    def connect(self, ssid, password, max_attempts=3):
        """
        Connect to WiFi network.
        
        Args:
            ssid: WiFi network name
            password: WiFi password
            max_attempts: Maximum connection attempts
        
        Returns:
            bool: Connection success
        """
        # If already connected, don't try again
        if self.connected:
            self.log("Already connected")
            return True
        
        self.log(f"Connecting to {ssid}...")
        
        # Attempt to connect multiple times if needed
        for attempt in range(max_attempts):
            try:
                # Flash status LED if available
                if self.status_led:
                    self.status_led.value = True
                
                # Attempt connection
                wifi.radio.connect(ssid, password)
                
                # Create socket pool for requests
                self.pool = socketpool.SocketPool(wifi.radio)
                self.requests_session = adafruit_requests.Session(self.pool)
                
                # Connection successful
                self.connected = True
                self.log(f"Connected! IP: {wifi.radio.ipv4_address}")
                
                # Turn off status LED
                if self.status_led:
                    self.status_led.value = False
                
                return True
            
            except (ConnectionError, ValueError, RuntimeError) as e:
                self.log(f"Connection attempt {attempt+1}/{max_attempts} failed: {e}")
                
                # Flash status LED to indicate failure
                if self.status_led:
                    for _ in range(3):
                        self.status_led.value = not self.status_led.value
                        time.sleep(0.1)
                    self.status_led.value = False
                
                # Wait before retry
                time.sleep(1)
        
        # All attempts failed
        self.log(f"Failed to connect to {ssid} after {max_attempts} attempts")
        return False
    
    def fetch_json(self, url, json_path=None, timeout=10):
        """
        Fetch JSON data from a URL.
        
        Args:
            url: URL to fetch
            json_path: Optional list of keys to navigate JSON structure
            timeout: Request timeout in seconds
        
        Returns:
            Data at the specified path or full JSON response
        """
        if not self.connected or not self.requests_session:
            self.log("Not connected - cannot fetch data")
            return None
        
        # Indicate activity with status LED
        if self.status_led:
            self.status_led.value = True
        
        try:
            # Perform the HTTP request
            self.log(f"Fetching data from {url}")
            response = self.requests_session.get(url, timeout=timeout)
            
            # Parse the JSON response
            json_data = response.json()
            response.close()
            
            # Run garbage collection to free memory
            gc.collect()
            
            # Navigate to the specified path in the JSON if provided
            if json_path:
                for key in json_path:
                    json_data = json_data[key]
            
            self.log("Data fetched successfully")
            return json_data
        
        except (RuntimeError, ValueError, KeyError) as e:
            self.log(f"Error fetching data: {e}")
            return None
        
        finally:
            # Always turn off the status LED when done
            if self.status_led:
                self.status_led.value = False
    
    def is_connected(self):
        """Check if currently connected to WiFi"""
        if not self.connected:
            return False
        
        try:
            # Test connection by checking IP
            return wifi.radio.ipv4_address is not None
        except (RuntimeError, OSError):
            self.connected = False
            return False