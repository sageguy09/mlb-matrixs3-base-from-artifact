import board
import displayio
import framebufferio
import rgbmatrix
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
import terminalio
import time
import os
import json
import gc

# Release any displays
displayio.release_displays()

# --- Load Configuration ---
def hex_to_int(hex_str):
    """Convert a hex string (with or without 0x prefix) to an integer."""
    if isinstance(hex_str, int):
        return hex_str
    if hex_str.startswith("0x"):
        return int(hex_str, 16)
    return int(hex_str, 16)

# Load layout configuration
try:
    with open("/layouts/w64h32.json", "r") as f:
        layout_config = json.load(f)
    print("Layout configuration loaded successfully")
except Exception as e:
    print("Error loading layout configuration:", e)
    # Default configuration if file is missing
    layout_config = {
        "logo": {"x": 0, "y": 0, "scale": 1},
        "team_matchup": {"x": 18, "y": 4, "color": "0xFFFFFF"},
        "inning": {"x": 18, "y": 14, "color": "0xFFFF00"},
        "score": {"x": 18, "y": 26, "color": "0x00FF00"},
        "bases": {
            "x": 32, "y": 10,
            "first": {"x": 38, "y": 16, "color_on": "0xFFFFFF", "color_off": "0x222222"},
            "second": {"x": 32, "y": 10, "color_on": "0xFFFFFF", "color_off": "0x222222"},
            "third": {"x": 26, "y": 16, "color_on": "0xFFFFFF", "color_off": "0x222222"},
            "home": {"x": 32, "y": 22, "color": "0x444444"}
        },
        "count": {"x": 45, "y": 16, "color": "0x00FFFF"}
    }

# --- Matrix Setup ---
WIDTH = 64
HEIGHT = 32
BIT_DEPTH = 4

matrix = rgbmatrix.RGBMatrix(
    width=WIDTH,
    height=HEIGHT,
    bit_depth=BIT_DEPTH,
    rgb_pins=[
        board.MTX_R1, board.MTX_G1, board.MTX_B1,
        board.MTX_R2, board.MTX_G2, board.MTX_B2,
    ],
    addr_pins=[
        board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC, board.MTX_ADDRD
    ],
    clock_pin=board.MTX_CLK,
    latch_pin=board.MTX_LAT,
    output_enable_pin=board.MTX_OE,
)
display = framebufferio.FramebufferDisplay(matrix)

# Load font
try:
    font = bitmap_font.load_font("/fonts/font.bdf")
except Exception:
    font = terminalio.FONT

# === Static Game Data for Display ===
game_state = {
    "home_team": "ATL",
    "away_team": "NYM",
    "home_record": "48-30",
    "away_record": "37-41",
    "inning": "Top 4th",
    "balls": 1,
    "strikes": 2,
    "outs": 1,
    "score_home": 5,
    "score_away": 3,
    "bases": {"first": True, "second": False, "third": True}
}

# === Display Group ===
main_group = displayio.Group()

# --- Create Pixel-Based Diamond for Base Visualization ---
def create_base_diamond(first=False, second=False, third=False):
    """Create a diamond-shaped base indicator using pixels"""
    base_group = displayio.Group(x=layout_config["bases"]["x"], y=layout_config["bases"]["y"])
    
    # Create bitmap for the diamond shape
    bitmap = displayio.Bitmap(15, 15, 4)  # 15x15 pixel bitmap with 4 colors
    palette = displayio.Palette(4)
    
    # Color definitions (using configured colors)
    palette[0] = 0x000000  # Transparent/background
    palette[1] = hex_to_int(layout_config["bases"]["first"]["color_on" if first else "color_off"])  # First base
    palette[2] = hex_to_int(layout_config["bases"]["second"]["color_on" if second else "color_off"])  # Second base
    palette[3] = hex_to_int(layout_config["bases"]["third"]["color_on" if third else "color_off"])  # Third base
    
    # Set transparent color
    palette.make_transparent(0)
    
    # Home plate (always shown as gray)
    home_x = layout_config["bases"]["home"]["x"] - layout_config["bases"]["x"]
    home_y = layout_config["bases"]["home"]["y"] - layout_config["bases"]["y"]
    bitmap[home_x, home_y] = 0  # Draw home plate with gray pixel
    
    # First base
    first_x = layout_config["bases"]["first"]["x"] - layout_config["bases"]["x"]
    first_y = layout_config["bases"]["first"]["y"] - layout_config["bases"]["y"]
    bitmap[first_x, first_y] = 1  # First base (right)
    
    # Second base
    second_x = layout_config["bases"]["second"]["x"] - layout_config["bases"]["x"]
    second_y = layout_config["bases"]["second"]["y"] - layout_config["bases"]["y"]
    bitmap[second_x, second_y] = 2  # Second base (top)
    
    # Third base
    third_x = layout_config["bases"]["third"]["x"] - layout_config["bases"]["x"]
    third_y = layout_config["bases"]["third"]["y"] - layout_config["bases"]["y"]
    bitmap[third_x, third_y] = 3  # Third base (left)
    
    # Add lines connecting the bases
    for i in range(1, 7):
        # Line from home to first
        x = home_x + int(i * (first_x - home_x) / 7)
        y = home_y + int(i * (first_y - home_y) / 7)
        bitmap[x, y] = 1 if first else 0
        
        # Line from first to second
        x = first_x + int(i * (second_x - first_x) / 7)
        y = first_y + int(i * (second_y - first_y) / 7)
        bitmap[x, y] = 2 if second else 0
        
        # Line from second to third
        x = second_x + int(i * (third_x - second_x) / 7)
        y = second_y + int(i * (third_y - second_y) / 7)
        bitmap[x, y] = 3 if third else 0
        
        # Line from third to home
        x = third_x + int(i * (home_x - third_x) / 7)
        y = third_y + int(i * (home_y - third_y) / 7)
        bitmap[x, y] = 0
    
    # Create a TileGrid using the bitmap and palette
    base_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
    base_group.append(base_grid)
    
    return base_group

# --- Braves Logo ---
try:
    logo_config = layout_config["logo"]
    logo_bitmap = displayio.OnDiskBitmap("/images/ATL.bmp")
    logo_tilegrid = displayio.TileGrid(
        logo_bitmap, 
        pixel_shader=logo_bitmap.pixel_shader, 
        x=logo_config["x"], 
        y=logo_config["y"]
    )
    main_group.append(logo_tilegrid)
except Exception as e:
    print("Error loading logo:", e)

# --- Matchup Text ---
try:
    matchup_config = layout_config["team_matchup"]
    matchup_text = f"{game_state['home_team']} vs {game_state['away_team']}"
    matchup_label = label.Label(
        font, 
        text=matchup_text, 
        color=hex_to_int(matchup_config["color"]), 
        x=matchup_config["x"], 
        y=matchup_config["y"]
    )
    main_group.append(matchup_label)
except Exception as e:
    print("Error creating matchup:", e)

# --- Inning ---
try:
    inning_config = layout_config["inning"]
    inning_label = label.Label(
        font, 
        text=game_state['inning'], 
        color=hex_to_int(inning_config["color"]), 
        x=inning_config["x"], 
        y=inning_config["y"]
    )
    main_group.append(inning_label)
except Exception as e:
    print("Error creating inning:", e)

# --- Base Diamond ---
try:
    bases_group = create_base_diamond(**game_state["bases"])
    main_group.append(bases_group)
except Exception as e:
    print("Error creating bases:", e)

# --- Count: Balls, Strikes, Outs ---
try:
    count_config = layout_config["count"]
    count_text = f"B:{game_state['balls']} S:{game_state['strikes']} O:{game_state['outs']}"
    count_label = label.Label(
        font, 
        text=count_text, 
        color=hex_to_int(count_config["color"]), 
        x=count_config["x"], 
        y=count_config["y"]
    )
    main_group.append(count_label)
except Exception as e:
    print("Error creating count:", e)

# --- Score ---
try:
    score_config = layout_config["score"]
    score_text = f"{game_state['home_team']} {game_state['score_home']} - {game_state['away_team']} {game_state['score_away']}"
    score_label = label.Label(
        font, 
        text=score_text, 
        color=hex_to_int(score_config["color"]), 
        x=score_config["x"], 
        y=score_config["y"]
    )
    main_group.append(score_label)
except Exception as e:
    print("Error creating score:", e)

# Show it all
display.root_group = main_group

# Debug: Memory usage
gc.collect()
print(f"Free memory: {gc.mem_free()} bytes")

# Idle loop - in a real implementation, this would update from the ESPN API
while True:
    time.sleep(1)
