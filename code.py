import board
import displayio
import framebufferio
import rgbmatrix
from adafruit_display_text import label
import terminalio  # Use built-in font as fallback
import time
import os
import ssl
import socketpool
import wifi
from get_team_logos import get_logo_tilegrid, LOGO_READY

# Release any existing displays
displayio.release_displays()

# --- Matrix Setup ---
BIT_DEPTH = 4  # Adjust for color depth (1-6)
WIDTH = 64
HEIGHT = 32

# Initialize the RGB matrix
matrix = rgbmatrix.RGBMatrix(
    width=WIDTH,
    height=HEIGHT,
    bit_depth=BIT_DEPTH,
    rgb_pins=[
        board.MTX_R1,
        board.MTX_G1,
        board.MTX_B1,
        board.MTX_R2,
        board.MTX_G2,
        board.MTX_B2,
    ],
    addr_pins=[
        board.MTX_ADDRA,
        board.MTX_ADDRB,
        board.MTX_ADDRC,
        board.MTX_ADDRD,
    ],
    clock_pin=board.MTX_CLK,
    latch_pin=board.MTX_LAT,
    output_enable_pin=board.MTX_OE,
)

# Create a display context
display = framebufferio.FramebufferDisplay(matrix)

# Create a loading message to display while we wait for logo and WiFi
loading_group = displayio.Group()
loading_text = label.Label(terminalio.FONT, text="Loading...", color=0xFFFFFF, x=5, y=16)
loading_group.append(loading_text)

# Show loading screen first
display.root_group = loading_group

# Initialize WiFi connection
print("Connecting to WiFi...")
loading_text.text = "Connecting WiFi..."

try:
    # Get WiFi details from settings.toml
    ssid = os.getenv("CIRCUITPY_WIFI_SSID")
    password = os.getenv("CIRCUITPY_WIFI_PASSWORD")
    
    print(f"Connecting to {ssid}...")
    wifi.radio.connect(ssid, password)
    
    # Create socket pool for network requests
    pool = socketpool.SocketPool(wifi.radio)
    
    print("WiFi connected!")
    print(f"IP address: {wifi.radio.ipv4_address}")
    loading_text.text = "WiFi connected!"
    time.sleep(1)  # Show success message briefly
except Exception as e:
    print(f"Failed to connect to WiFi: {e}")
    loading_text.text = "WiFi error!"
    time.sleep(2)  # Show error longer

# Create the main display group
main_group = displayio.Group()

# Define teams for current game
home_team = "ATL"  # We only support ATL in this version
opponent_team = "NYM"  # Just for display, not loading a logo

# Load Braves logo
loading_text.text = "Loading logo..."
braves_logo = get_logo_tilegrid(home_team)

# Position logo
braves_logo.x = 2
braves_logo.y = 2
main_group.append(braves_logo)

# Try to load the custom font, fall back to built-in if it fails
try:
    from adafruit_bitmap_font import bitmap_font
    font = bitmap_font.load_font("/fonts/font.bdf")
    print("Custom font loaded successfully")
except Exception as e:
    print(f"Error loading font: {e}")
    font = terminalio.FONT  # Use built-in font as fallback

# Create labels
score_label = label.Label(font, text=f"{home_team} 5 - {opponent_team} 3", color=0x00FF00, x=2, y=20)
next_game_label = label.Label(font, text=f"Next: 7/15 @ {opponent_team}", color=0xFF0000, x=2, y=28)

# Add labels to the group
main_group.append(score_label)
main_group.append(next_game_label)

# Show the main display group once everything is ready
display.root_group = main_group

# Keep the display on
while True:
    time.sleep(1)
