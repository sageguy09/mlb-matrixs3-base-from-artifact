import board
import displayio
import framebufferio
import rgbmatrix
from adafruit_display_text import label
import terminalio
import time
import os
import ssl
import socketpool
import wifi
import gc

# Release any existing displays
displayio.release_displays()

# --- Matrix Setup ---
BIT_DEPTH = 4  # Adjust for color depth (1-6)
WIDTH = 64
HEIGHT = 32

# Initialize the RGB matrix with standard hub75 pinout for MatrixPortal S3
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

# Create a loading message to display while we wait
loading_group = displayio.Group()
status_line = label.Label(terminalio.FONT, text="Initializing...", color=0xFFFFFF, x=2, y=16)
loading_group.append(status_line)

# Show loading screen immediately
display.root_group = loading_group

# Function to update status message
def update_status(message):
    print(message)
    status_line.text = message
    # Allow a brief moment for display to update
    time.sleep(0.1)

# Check that our logo file exists
try:
    if not os.path.exists("/ATL.bmp"):
        update_status("Logo file missing!")
        time.sleep(3)
    else:
        update_status("Logo file found")
except Exception as e:
    update_status(f"File check error: {str(e)}")

# Initialize WiFi connection
update_status("Connecting WiFi...")

wifi_connected = False
try:
    # Get WiFi details from settings.toml
    ssid = os.getenv("CIRCUITPY_WIFI_SSID")
    password = os.getenv("CIRCUITPY_WIFI_PASSWORD")
    
    if not ssid or ssid == "Your_WiFi_Name" or ssid == "YourSSID":
        update_status("Set WiFi in settings.toml")
        time.sleep(3)
    else:
        update_status(f"Connecting to {ssid}")
        try:
            # Set a timeout for connection attempts
            wifi.radio.connect(ssid, password, timeout=10)
            
            # Create socket pool for network requests
            pool = socketpool.SocketPool(wifi.radio)
            
            update_status(f"WiFi connected! IP: {wifi.radio.ipv4_address}")
            wifi_connected = True
            time.sleep(1)  # Show success briefly
        except (ValueError, RuntimeError) as e:
            update_status(f"WiFi connection error: {str(e)}")
            time.sleep(2)
except Exception as e:
    update_status(f"WiFi Failed: {str(e)}")
    time.sleep(2)  # Show error longer

# Create the main display group
main_group = displayio.Group()

# Define teams for current game
home_team = "ATL"  # Atlanta Braves
opponent_team = "NYM"  # New York Mets (just for display)

# Load the Braves logo directly from root directory
update_status("Loading team logo...")
try:
    # Load the bitmap directly from the file in root directory
    bitmap = displayio.OnDiskBitmap("/ATL.bmp")
    tile_grid = displayio.TileGrid(bitmap, pixel_shader=bitmap.pixel_shader)
    
    # Position logo in top left
    tile_grid.x = 2
    tile_grid.y = 2
    main_group.append(tile_grid)
    
    # Try to load the custom font, fall back to built-in if it fails
    try:
        from adafruit_bitmap_font import bitmap_font
        font = bitmap_font.load_font("/fonts/font.bdf")
        print("Custom font loaded successfully")
    except Exception as e:
        print(f"Error loading font: {e}")
        font = terminalio.FONT  # Use built-in font as fallback
    
    # Create scoreboard labels
    score_label = label.Label(
        font, 
        text=f"{home_team} 5 - {opponent_team} 3", 
        color=0x00FF00, 
        x=2, 
        y=20
    )
    next_game_label = label.Label(
        font, 
        text=f"Next: 7/15 @ {opponent_team}", 
        color=0xFF0000, 
        x=2, 
        y=28
    )
    
    # Add labels to the group
    main_group.append(score_label)
    main_group.append(next_game_label)
    
    # Show the main display group once everything is ready
    display.root_group = main_group
    
except Exception as e:
    update_status(f"Logo Error: {str(e)}")
    # If we can't load the logo, at least display something
    message_group = displayio.Group()
    title = label.Label(terminalio.FONT, text="Atlanta Braves", color=0xFFFFFF, x=2, y=12)
    status = label.Label(terminalio.FONT, text="Logo unavailable", color=0xFF0000, x=2, y=24)
    message_group.append(title)
    message_group.append(status)
    display.root_group = message_group
    time.sleep(2)

# Keep the display on and periodically refresh data
while True:
    # Just keep the display active
    time.sleep(1)
    
    # Optional: implement a memory check and garbage collection
    # to prevent memory issues on long runs
    gc.collect()
