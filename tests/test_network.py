# Network functionality tests
"""
Test script for network connectivity
Tests WiFi connection and basic HTTP requests
"""
import time
import gc
import board
import microcontroller
import displayio
import digitalio
import supervisor

print("ESP32-S3 Network Test")
print("=====================")

# Import custom modules if they exist
try:
    from packages.network import wifi
    has_wifi = True
    print("WiFi module loaded successfully")
except ImportError:
    has_wifi = False
    print("WiFi module not found")
    
try:
    import debug
    logger = debug.Logger("test_network")
    has_logger = True
    print("Debug module loaded successfully")
except ImportError:
    logger = None
    has_logger = False
    print("Debug module not found")

def log(message, level="info"):
    """Log a message if logger is available"""
    print(message)
    if not logger:
        return
    
    log_method = getattr(logger, level, None)
    if log_method:
        log_method(message)

def test_wifi_connect():
    """Test WiFi connection"""
    if not has_wifi:
        log("WiFi module not available", "error")
        return False
    
    log("Testing WiFi connection...", "info")
    
    try:
        from secrets import secrets
        
        ssid = secrets.get("ssid", "")
        password = secrets.get("password", "")
        
        if not ssid or not password:
            log("WiFi credentials not found in secrets.py", "error")
            return False
        
        log(f"Connecting to '{ssid}'...", "info")
        result = wifi.connect(ssid, password)
        
        if result:
            log("WiFi connection successful!", "info")
            
            ip_address = wifi.get_ip_address()
            signal_strength = wifi.get_signal_strength()
            mac_address = wifi.get_mac_address()
            
            log(f"IP Address: {ip_address}", "info")
            log(f"Signal Strength: {signal_strength} dBm", "info")
            log(f"MAC Address: {mac_address}", "info")
            
            return True
        else:
            log("WiFi connection failed", "error")
            return False
    except Exception as e:
        log(f"Error testing WiFi connection: {e}", "error")
        return False

def test_http_request():
    """Test HTTP request"""
    if not has_wifi:
        log("WiFi module not available", "error")
        return False
    
    if not wifi.get_ip_address():
        log("WiFi not connected", "error")
        return False
    
    log("Testing HTTP request...", "info")
    
    try:
        import adafruit_requests as requests
        
        # Try to access test page
        url = "http://wifitest.adafruit.com/testwifi/index.html"
        log(f"Requesting {url}...", "info")
        
        response = requests.get(url)
        
        log(f"Status code: {response.status_code}", "info")
        log(f"Content length: {len(response.text)} bytes", "info")
        
        if response.status_code == 200:
            log("HTTP request successful!", "info")
            response.close()
            return True
        else:
            log(f"HTTP request failed with status {response.status_code}", "error")
            response.close()
            return False
    except Exception as e:
        log(f"Error testing HTTP request: {e}", "error")
        return False

def main():
    """Main test function"""
    log("Starting network tests...", "info")
    
    # Run tests
    wifi_success = test_wifi_connect()
    
    if wifi_success:
        # Only test HTTP if WiFi connected
        http_success = test_http_request()
    else:
        http_success = False
    
    # Print summary
    log("\nTest Results:", "info")
    log(f"WiFi Connection: {'SUCCESS' if wifi_success else 'FAILURE'}", 
        "info" if wifi_success else "error")
    
    if wifi_success:
        log(f"HTTP Request: {'SUCCESS' if http_success else 'FAILURE'}", 
            "info" if http_success else "error")
    
    # Clean up
    if wifi_success:
        log("Disconnecting WiFi...", "info")
        wifi.disconnect()
    
    log("Tests completed", "info")

if __name__ == "__main__":
    main()
