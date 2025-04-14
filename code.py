# main.py - Bitcoin price display example for Matrix Portal S3
# Adapted from the Adafruit MatrixPortal example

import time
import board
import terminalio
import displayio
import gc

# Import modules from our project
from packages.hardware.matrix import Matrix
from packages.utils.network import WiFiManager
from packages.ui.text_display import TextDisplay

# Configuration
WIFI_SSID = "your_wifi_ssid"
WIFI_PASSWORD = "your_wifi_password"
CURRENCY = "USD"
DATA_SOURCE = "https://api.coindesk.com/v1/bpi/currentprice.json"
DATA_LOCATION = ["bpi", CURRENCY, "rate_float"]
REFRESH_INTERVAL = 180  # Refresh data every 180 seconds (3 minutes)
SCROLL_DELAY = 0.03  # 30ms between scroll steps

# Initialize Matrix hardware
matrix = Matrix(width=64, height=32, bit_depth=6)
display_group = matrix.get_display_group()

# Create text display manager
text = TextDisplay(display_group, width=64, height=32)

# Initialize network connection
network = WiFiManager(status_led=matrix.status_led, debug=True)

def format_price(price):
    """Format the price value based on currency"""
    if CURRENCY == "USD":
        return f"${int(price)}"
    if CURRENCY == "EUR":
        return f"€{int(price)}"
    if CURRENCY == "GBP":
        return f"£{int(price)}"
    return f"{int(price)}"

def main():
    """Main application function"""
    print("Starting Bitcoin Price Display")
    
    # Connect to WiFi
    if not network.connect(WIFI_SSID, WIFI_PASSWORD):
        print("Failed to connect to WiFi. Check credentials.")
        return
    
    # Add scrolling text display
    bitcoin_text = text.add_text(
        text="Connecting...",
        name="bitcoin_price",
        color=0xFFFFFF,
        x=matrix.width,  # Start off-screen to the right
        y=16,  # Vertical center of 32px display
        scrolling=True,
        scroll_delay=SCROLL_DELAY
    )
    
    # Preload font characters for faster rendering
    special_chars = b"$0123456789"
    if CURRENCY == "EUR":
        special_chars += bytes([0x20AC])  # Euro symbol
    elif CURRENCY == "GBP":
        special_chars += bytes([0x00A3])  # Pound symbol
    
    text.preload_font("bitcoin_price", special_chars)
    
    # Main loop
    last_check = None
    
    while True:
        # Check if it's time to fetch new price data
        if last_check is None or time.monotonic() > last_check + REFRESH_INTERVAL:
            try:
                # Fetch current Bitcoin price
                current_price = network.fetch_json(DATA_SOURCE, json_path=DATA_LOCATION)
                
                if current_price is not None:
                    # Format and update the display text
                    price_text = format_price(current_price)
                    bitcoin_message = f"Bitcoin price: {price_text} - powered by CoinDesk"
                    text.update_text("bitcoin_price", bitcoin_message)
                    print(f"Updated price: {price_text}")
                    
                    # Update last check time
                    last_check = time.monotonic()
            except Exception as e:
                print(f"Error updating price: {e}")
                # Keep going with previous data
        
        # Update scrolling text
        text.scroll_all()
        
        # Short delay between updates
        time.sleep(0.01)
        
        # Run garbage collection occasionally to prevent memory issues
        if time.monotonic() % 10 < 0.1:  # Roughly every 10 seconds
            gc.collect()

if __name__ == "__main__":
    try:
        # Run the main application
        main()
    except Exception as e:
        # Log any unhandled exceptions
        print(f"Unhandled exception: {e}")
        matrix.status_flash(count=5)  # Flash status LED to indicate error
        
        # In production code, you might want to reset the device
        # import microcontroller
        # microcontroller.reset()