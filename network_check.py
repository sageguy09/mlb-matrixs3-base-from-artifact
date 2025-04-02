"""
WiFi Connection Check Utility
Ensures proper connection to WiFi before proceeding with main application
"""
import gc
import time
import board
import neopixel
import traceback
from secrets import secrets

# Import the new ESP WiFi manager
try:
    from packages.network.esp_wifi import ESPWiFiManager
    has_esp_wifi = True
    print("Using ESP32-SPI WiFi manager")
except ImportError:
    has_esp_wifi = False
    print("ESP32-SPI WiFi manager not found, using native wifi module")
    import wifi

def log_message(message):
    """Print a log message with timestamp"""
    print(f"[NETWORK] {message}")

def ensure_wifi_connection(max_attempts=3):
    """
    Ensure WiFi is connected before proceeding
    Returns True if connected, False if connection failed
    """
    log_message("Checking WiFi connection...")
    
    # Create status pixel for feedback
    try:
        status_pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)
        status_pixel[0] = (0, 0, 50)  # Blue - initializing
    except Exception as e:
        log_message(f"Could not initialize status LED: {e}")
        status_pixel = None
    
    ssid = secrets.get('ssid')
    password = secrets.get('password')
    
    if not ssid or not password:
        log_message("ERROR: WiFi credentials missing from secrets.py")
        if status_pixel:
            status_pixel[0] = (50, 0, 0)  # Red - error
        return False
    
    log_message(f"Connecting to {ssid}...")
    if status_pixel:
        status_pixel[0] = (50, 50, 0)  # Yellow - connecting
    
    # Use ESP32-SPI WiFi manager if available
    if has_esp_wifi:
        wifi_manager = ESPWiFiManager(status_pixel=status_pixel, debug=True)
        connected = wifi_manager.connect(ssid, password, max_attempts)
        
        if connected:
            ip_address = wifi_manager.get_ip_address()
            log_message(f"Successfully connected! IP: {ip_address}")
            if status_pixel:
                status_pixel[0] = (0, 50, 0)  # Green - success
            
            # Free up memory
            gc.collect()
            return True
        else:
            log_message("ESP32-SPI WiFi connection failed")
            if status_pixel:
                status_pixel[0] = (50, 0, 0)  # Red - error
            return False
            
    else:
        # Fall back to native WiFi if ESP32-SPI is not available
        try:
            # Try multiple connection attempts
            for attempt in range(max_attempts):
                try:
                    wifi.radio.connect(ssid, password)
                    
                    # Wait a moment and check if connected
                    time.sleep(2)
                    if wifi.radio.connected:
                        ip = wifi.radio.ipv4_address
                        log_message(f"Successfully connected! IP: {ip}")
                        if status_pixel:
                            status_pixel[0] = (0, 50, 0)  # Green - success
                        
                        # Free up memory
                        gc.collect()
                        return True
                    else:
                        log_message(f"Connection attempt {attempt+1} failed")
                except Exception as e:
                    log_message(f"Connection error: {e}")
                    try:
                        log_message(traceback.format_exc())
                    except:
                        pass
                    
                    # Wait before retry
                    time.sleep(2)
            
            log_message(f"Failed to connect after {max_attempts} attempts")
            if status_pixel:
                status_pixel[0] = (50, 0, 0)  # Red - error
            return False
        
        except Exception as e:
            log_message(f"WiFi error: {e}")
            if status_pixel:
                status_pixel[0] = (50, 0, 0)  # Red - error
            return False

# Allow running standalone for testing connection
if __name__ == "__main__":
    ensure_wifi_connection()
