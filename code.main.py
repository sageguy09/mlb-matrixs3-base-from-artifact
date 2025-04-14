# main.py - Main application file for Matrix Portal S3 Base Project

import time
import board
import busio
import terminalio
import digitalio
import displayio
import gc
import wifi
import socketpool
import adafruit_requests
from adafruit_matrixportal.matrix import Matrix
from adafruit_matrixportal.network import Network

# Configuration Constants
MATRIX_WIDTH = 64  # Matrix width in pixels
MATRIX_HEIGHT = 32  # Matrix height in pixels
BITDEPTH = 6  # Bit depth for color precision (6 is typical for RGB panels)
UPDATE_RATE = 0.03  # Scroll speed (30ms delay between updates)

# Network Configuration
# Replace with your WiFi credentials
WIFI_SSID = "Sage1"
WIFI_PASSWORD = "J@sper123"

# Data Source Configuration
DATA_SOURCE = "https://api.coindesk.com/v1/bpi/currentprice.json"
DATA_LOCATION = ["bpi", "USD", "rate_float"]  # Path to data in JSON
REFRESH_INTERVAL = 180  # Refresh data every 180 seconds (3 minutes)

# Initialize hardware
def initialize_hardware():
    """Initialize and configure the Matrix Portal hardware"""
    print("Initializing Matrix Portal S3...")
    
    # Initialize the Matrix object with dimensions and pin configuration for S3
    matrix = Matrix(
        width=MATRIX_WIDTH,
        height=MATRIX_HEIGHT,
        bit_depth=BITDEPTH,
        tile_rows=1,
    )
    
    # Create a display using the Matrix configuration
    display = matrix.display
    
    # Initialize status LED
    status_led = digitalio.DigitalInOut(board.NEOPIXEL)
    status_led.direction = digitalio.Direction.OUTPUT
    
    # Set up the display group for rendering content
    splash = displayio.Group()
    display.root_group = splash
    
    return matrix, display, splash, status_led

# Network functionality
def initialize_network():
    """Connect to WiFi and initialize the network services"""
    print(f"Connecting to {WIFI_SSID}...")
    
    try:
        # Connect to WiFi
        wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
        
        # Create socket pool for HTTP requests
        pool = socketpool.SocketPool(wifi.radio)
        requests = adafruit_requests.Session(pool)
        
        print(f"Connected to {WIFI_SSID}!")
        print(f"IP address: {wifi.radio.ipv4_address}")
        
        return Network(requests)
    except Exception as e:
        print(f"Failed to connect to WiFi: {e}")
        return None

# Data transformation function
def text_transform(val):
    """Format the value for display with the appropriate currency symbol"""
    return f"${int(val)}"  # Format as USD

# Main application
def run():
    """Main application function"""
    # Initialize hardware components
    matrix, display, splash, status_led = initialize_hardware()
    
    # Connect to WiFi and initialize network
    network = initialize_network()
    if not network:
        print("Network initialization failed. Check your credentials.")
        return
    
    # Set up scrolling text area
    scroll_text = network.add_text(
        text_font=terminalio.FONT,
        text_position=(16, 16),
        text_color=0xFFFFFF,
        scrolling=True,
        text_transform=text_transform,
    )
    
    # Preload font characters to speed up rendering
    scroll_text.preload_font(b"$0123456789")
    
    # Main loop
    last_check = None
    
    while True:
        # Fetch new data if it's time to refresh
        if last_check is None or time.monotonic() > last_check + REFRESH_INTERVAL:
            try:
                # Turn on status LED to indicate data fetch
                status_led.value = True
                
                # Fetch data from the API
                value = network.fetch(DATA_SOURCE, json_path=DATA_LOCATION)
                print(f"Bitcoin price: ${value}")
                
                # Update the last check time
                last_check = time.monotonic()
                
                # Turn off status LED
                status_led.value = False
            except Exception as e:
                print(f"Error fetching data: {e}")
                # Blink LED to indicate error
                for _ in range(3):
                    status_led.value = True
                    time.sleep(0.1)
                    status_led.value = False
                    time.sleep(0.1)
        
        # Scroll the text
        scroll_text.scroll()
        
        # Short delay between scroll steps
        time.sleep(UPDATE_RATE)
        
        # Perform garbage collection to prevent memory issues
        gc.collect()

# Run the application if this is the main file
if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print(f"Application error: {e}")
        # Reset in case of fatal error
        import microcontroller
        microcontroller.reset()