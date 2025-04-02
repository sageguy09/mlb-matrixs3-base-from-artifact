"""
Network utilities for MLB Scoreboard
===================================
Handles WiFi connectivity and HTTP requests.
"""

import gc
import time
import ssl
import json
import traceback
import socketpool
import wifi
import adafruit_requests
from packages.utils.logger import Logger

class WiFiManager:
    """WiFi connection manager."""
    
    def __init__(self, ssid=None, password=None, debug=False):
        """Initialize WiFi manager.
        
        Args:
            ssid: WiFi network name
            password: WiFi password
            debug: Enable debug logging
        """
        self.ssid = ssid
        self.password = password
        self.log = Logger("WiFi", debug=debug)
        self.debug = debug
        self.is_connected = False
        self.wifi = wifi.radio
    
    def connect(self, max_attempts=3):
        """Connect to WiFi network.
        
        Args:
            max_attempts: Maximum number of connection attempts
            
        Returns:
            True if connection successful, False otherwise
        """
        if self.is_connected:
            return True
            
        if not self.ssid or not self.password:
            self.log.error("WiFi credentials not provided")
            return False
        
        self.log.info(f"Connecting to {self.ssid}...")
        
        # Make multiple attempts
        for attempt in range(max_attempts):
            try:
                self.wifi.connect(self.ssid, self.password)
                # Check if connected
                if self.wifi.connected:
                    self.is_connected = True
                    ip = self.wifi.ipv4_address
                    self.log.info(f"Connected to {self.ssid} | IP: {ip}")
                    return True
            except Exception as e:
                self.log.error(f"Connection attempt {attempt+1} failed: {e}")
                if self.debug:
                    self.log.error(traceback.format_exc())
                time.sleep(1)
        
        self.log.error(f"Failed to connect to {self.ssid} after {max_attempts} attempts")
        return False
    
    def disconnect(self):
        """Disconnect from WiFi network."""
        if self.is_connected:
            self.wifi.enabled = False
            self.is_connected = False
            self.log.info(f"Disconnected from {self.ssid}")
    
    def is_connected(self):
        """Check if WiFi is currently connected.
        
        Returns:
            bool: True if connected, False otherwise
        """
        try:
            if not hasattr(self, 'wifi') or self.wifi is None:
                return False
            # Test connection by checking IP
            return self.wifi.is_connected
        except Exception as e:
            self.log.error(f"Error checking connection: {e}")
            return False


class Network:
    """Network manager for HTTP requests."""
    
    def __init__(self, status_neopixel=None, debug=False):
        """Initialize network manager.
        
        Args:
            status_neopixel: NeoPixel for status indication
            debug: Enable debug logging
        """
        self.log = Logger("Network", debug=debug)
        self.debug = debug
        self.status_pixel = status_neopixel
        self.requests_session = None
        self.pool = None
    
    def _initialize_session(self):
        """Initialize requests session."""
        try:
            self.pool = socketpool.SocketPool(wifi.radio)
            self.requests_session = adafruit_requests.Session(self.pool, ssl.create_default_context())
            return True
        except Exception as e:
            self.log.error(f"Failed to initialize session: {e}")
            if self.debug:
                self.log.error(traceback.format_exc())
            return False
    
    def fetch(self, url, headers=None, timeout=30):
        """Fetch data from a URL.
        
        Args:
            url: URL to fetch
            headers: HTTP headers
            timeout: Request timeout in seconds
            
        Returns:
            Response text or None on error
        """
        # Initialize session if not already done
        if not self.requests_session:
            if not self._initialize_session():
                return None
        
        # Set default headers
        if headers is None:
            headers = {
                "User-Agent": "ESP32-MLB-Scoreboard/1.0",
                "Accept": "application/json"
            }
        
        # Set status pixel to cyan during request if available
        if self.status_pixel:
            self.status_pixel[0] = (0, 128, 128)
        
        try:
            self.log.debug(f"GET {url}")
            response = self.requests_session.get(url, headers=headers, timeout=timeout)
            
            if response.status_code == 200:
                # Set status pixel back to green on success if available
                if self.status_pixel:
                    self.status_pixel[0] = (0, 128, 0)
                    
                # Return the response text
                return response.text
            else:
                self.log.error(f"Request failed with status code {response.status_code}")
                
                # Set status pixel to orange on error if available
                if self.status_pixel:
                    self.status_pixel[0] = (128, 64, 0)
                    
                return None
                
        except Exception as e:
            self.log.error(f"Request failed: {e}")
            if self.debug:
                self.log.error(traceback.format_exc())
                
            # Set status pixel to red on exception if available
            if self.status_pixel:
                self.status_pixel[0] = (128, 0, 0)
                
            return None
        finally:
            # Clean up memory
            gc.collect()
