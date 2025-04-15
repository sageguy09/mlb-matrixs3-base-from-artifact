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

def load_layout_config():
    """Load the layout configuration file for the display"""
    try:
        with open("/layouts/w64h32.json", "r") as f:
            config = json.load(f)
            print("Layout configuration loaded successfully")
            return config
    except Exception as e:
        print("Error loading layout configuration:", e)
        # Default configuration if file is missing
        return {
            "logo": {"x": 2, "y": 2, "scale": 1, "max_width": 24, "max_height": 24},
            "team_matchup": {
                "home_team": {"x": 28, "y": 4, "color": "0xFFFFFF"},
                "vs_text": {"x": 38, "y": 4, "color": "0xFFFFFF"},
                "away_team": {"x": 47, "y": 4, "color": "0xFFFFFF"}
            },
            "inning": {"x": 30, "y": 14, "color": "0x00FFFF"},
            "score": {"x": 28, "y": 26, "color": "0x00FF00"},
            "bases": {
                "x": 35, "y": 8,
                "first": {"x": 44, "y": 13, "color_on": "0xFFFFFF", "color_off": "0x222222"},
                "second": {"x": 39, "y": 8, "color_on": "0xFFFFFF", "color_off": "0x222222"},
                "third": {"x": 34, "y": 13, "color_on": "0xFFFFFF", "color_off": "0x222222"},
                "home": {"x": 39, "y": 18, "color": "0x444444"}
            },
            "count": {"x": 50, "y": 18, "color": "0xFFFFFF"}
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

# --- Show MLB Startup Logo ---
def show_mlb_startup_logo():
    """Display the MLB logo centered on the screen during startup"""
    startup_group = displayio.Group()
    
    try:
        # Try to load the MLB logo bitmap
        mlb_bitmap = displayio.OnDiskBitmap("/images/MLB.bmp")
        mlb_grid = displayio.TileGrid(mlb_bitmap, pixel_shader=mlb_bitmap.pixel_shader)
        
        # Center the logo
        mlb_grid.x = (WIDTH - mlb_bitmap.width) // 2
        mlb_grid.y = (HEIGHT - mlb_bitmap.height) // 2
        
        startup_group.append(mlb_grid)
    except Exception as e:
        print(f"Error loading MLB logo: {e}")
        # Create text as fallback
        mlb_text = label.Label(terminalio.FONT, text="MLB", color=0x0000FF, scale=2)
        mlb_text.x = (WIDTH - mlb_text.bounding_box[2]) // 2
        mlb_text.y = HEIGHT // 2
        startup_group.append(mlb_text)
    
    # Startup message
    version_label = label.Label(
        terminalio.FONT, 
        text="MLB Scoreboard v1.0", 
        color=0xFFFFFF, 
        x=2, 
        y=HEIGHT - 4
    )
    startup_group.append(version_label)
    
    # Show the startup screen
    display.root_group = startup_group
    time.sleep(3)  # Show for 3 seconds
    
    # Cleanup
    gc.collect()

# --- Create Pixel-Based Diamond for Base Visualization ---
def create_base_diamond(main_group, first=False, second=False, third=False, layout=None):
    """Create a diamond-shaped base indicator using pixels"""
    if not layout or "bases" not in layout:
        print("Layout configuration missing bases information")
        return
    
    bases_config = layout["bases"]
    base_group = displayio.Group(x=bases_config["x"], y=bases_config["y"])
    
    # Create bitmap for the bases
    bitmap = displayio.Bitmap(15, 15, 4)  # 15x15 pixel bitmap with 4 colors
    palette = displayio.Palette(4)
    
    # Color definitions (using configured colors)
    base1_color = hex_to_int(bases_config["first"]["color_on" if first else "color_off"])
    base2_color = hex_to_int(bases_config["second"]["color_on" if second else "color_off"])
    base3_color = hex_to_int(bases_config["third"]["color_on" if third else "color_off"])
    home_color = hex_to_int(bases_config["home"]["color"])
    
    palette[0] = 0x000000  # Transparent/background
    palette[1] = base1_color  # First base
    palette[2] = base2_color  # Second base
    palette[3] = base3_color  # Third base
    
    # Set transparent color
    palette.make_transparent(0)
    
    # Calculate relative positions
    first_x = bases_config["first"]["x"] - bases_config["x"]
    first_y = bases_config["first"]["y"] - bases_config["y"]
    second_x = bases_config["second"]["x"] - bases_config["x"]
    second_y = bases_config["second"]["y"] - bases_config["y"]
    third_x = bases_config["third"]["x"] - bases_config["x"]
    third_y = bases_config["third"]["y"] - bases_config["y"]
    home_x = bases_config["home"]["x"] - bases_config["x"]
    home_y = bases_config["home"]["y"] - bases_config["y"]
    
    # Draw bases as solid pixels
    bitmap[first_x, first_y] = 1  # First base
    bitmap[second_x, second_y] = 2  # Second base
    bitmap[third_x, third_y] = 3  # Third base
    
    # Draw home plate (always gray)
    if 0 <= home_x < 15 and 0 <= home_y < 15:
        bitmap[home_x, home_y] = 0
    
    # Draw lines connecting bases
    # Line from home to first
    for i in range(1, 6):
        x = home_x + int(i * (first_x - home_x) / 6)
        y = home_y + int(i * (first_y - home_y) / 6)
        if 0 <= x < 15 and 0 <= y < 15:
            bitmap[x, y] = 1 if first else 0
    
    # Line from first to second
    for i in range(1, 6):
        x = first_x + int(i * (second_x - first_x) / 6)
        y = first_y + int(i * (second_y - first_y) / 6)
        if 0 <= x < 15 and 0 <= y < 15:
            bitmap[x, y] = 2 if second else 0
    
    # Line from second to third
    for i in range(1, 6):
        x = second_x + int(i * (third_x - second_x) / 6)
        y = second_y + int(i * (third_y - second_y) / 6)
        if 0 <= x < 15 and 0 <= y < 15:
            bitmap[x, y] = 3 if third else 0
    
    # Line from third to home
    for i in range(1, 6):
        x = third_x + int(i * (home_x - third_x) / 6)
        y = third_y + int(i * (home_y - third_y) / 6)
        if 0 <= x < 15 and 0 <= y < 15:
            bitmap[x, y] = 0
    
    # Create a TileGrid using the bitmap and palette
    base_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
    base_group.append(base_grid)
    
    main_group.append(base_group)
    return base_group

def setup_game_day_display(game_data, layout_config):
    """Set up the display for game day using the layout configuration"""
    main_group = displayio.Group()
    
    # --- Load Braves Logo ---
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
    
    # --- Team Matchup Text ---
    try:
        matchup_config = layout_config["team_matchup"]
        
        # Home team
        home_team_label = label.Label(
            font, 
            text=game_data["home_team"], 
            color=hex_to_int(matchup_config["home_team"]["color"]), 
            x=matchup_config["home_team"]["x"], 
            y=matchup_config["home_team"]["y"]
        )
        main_group.append(home_team_label)
        
        # VS text
        vs_label = label.Label(
            font, 
            text="v", 
            color=hex_to_int(matchup_config["vs_text"]["color"]), 
            x=matchup_config["vs_text"]["x"], 
            y=matchup_config["vs_text"]["y"]
        )
        main_group.append(vs_label)
        
        # Away team
        away_team_label = label.Label(
            font, 
            text=game_data["away_team"], 
            color=hex_to_int(matchup_config["away_team"]["color"]), 
            x=matchup_config["away_team"]["x"], 
            y=matchup_config["away_team"]["y"]
        )
        main_group.append(away_team_label)
        
    except Exception as e:
        print("Error creating matchup:", e)
    
    # --- Inning ---
    try:
        inning_config = layout_config["inning"]
        inning_label = label.Label(
            font, 
            text=game_data["inning"], 
            color=hex_to_int(inning_config["color"]), 
            x=inning_config["x"], 
            y=inning_config["y"]
        )
        main_group.append(inning_label)
    except Exception as e:
        print("Error creating inning:", e)
    
    # --- Base Diamond ---
    try:
        create_base_diamond(
            main_group,
            first=game_data["bases"]["first"],
            second=game_data["bases"]["second"],
            third=game_data["bases"]["third"],
            layout=layout_config
        )
    except Exception as e:
        print("Error creating bases:", e)
    
    # --- Count: Balls, Strikes, Outs ---
    try:
        count_config = layout_config["count"]
        count_text = f"B:{game_data['balls']} S:{game_data['strikes']} O:{game_data['outs']}"
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
        score_text = f"{game_data['home_team']} {game_data['score_home']} - {game_data['away_team']} {game_data['score_away']}"
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
    
    return main_group

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

# Load layout configuration
layout_config = load_layout_config()

# Show MLB startup logo first
show_mlb_startup_logo()

# Setup and display the game day screen
main_group = setup_game_day_display(game_state, layout_config)

# Show the game display
display.root_group = main_group

# Debug: Memory usage
gc.collect()
print(f"Free memory: {gc.mem_free()} bytes")

# Print layout information for debugging
def print_layout_grid():
    """Print a text representation of the current layout for debugging"""
    grid = [[" " for _ in range(64)] for _ in range(32)]
    
    # Mark key layout positions from configuration
    for element, config in layout_config.items():
        if isinstance(config, dict) and "x" in config and "y" in config:
            x, y = config["x"], config["y"]
            if 0 <= x < 64 and 0 <= y < 32:
                grid[y][x] = "X"
        elif isinstance(config, dict):
            for key, subconfig in config.items():
                if isinstance(subconfig, dict) and "x" in subconfig and "y" in subconfig:
                    x, y = subconfig["x"], subconfig["y"]
                    if 0 <= x < 64 and 0 <= y < 32:
                        grid[y][x] = "X"
    
    # Print the grid
    print("Display Layout (64x32):")
    for row in grid:
        print("".join(row))

# Uncomment to print layout grid for debugging
# print_layout_grid()

# Idle loop - in a real implementation, this would update from the ESPN API
while True:
    time.sleep(1)
