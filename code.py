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
        # Default configuration if file is missing - updated for 15x15 logo
        return {
            "logo_area": {"x": 0, "y": 0, "width": 17, "height": 17, "border_color": "0xFFFFFF"},
            "logo": {"x": 1, "y": 1, "max_width": 15, "max_height": 15},
            "team_display": {
                "home_team": {"x": 19, "y": 7, "color": "0x00FFFF"},
                "vs_text": {"x": 31, "y": 7, "color": "0xFFFFFF"},
                "away_team": {"x": 37, "y": 7, "color": "0x00FFFF"}
            },
            "inning": {"x": 19, "y": 15, "color": "0x00FFFF"},
            "score": {"x": 19, "y": 23, "color": "0x00FF00"},
            "bases": {
                "x": 50, "y": 10,
                "first": {"x": 56, "y": 15, "color_on": "0xFFFFFF", "color_off": "0x222222"},
                "second": {"x": 50, "y": 10, "color_on": "0xFFFFFF", "color_off": "0x222222"},
                "third": {"x": 44, "y": 15, "color_on": "0xFFFFFF", "color_off": "0x222222"},
                "home": {"x": 50, "y": 20, "color": "0x444444"}
            },
            "count": {"x": 38, "y": 30, "color": "0xFFFFFF"}
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
        text="MLB Scoreboard v1.1", 
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

# --- Draw Logo Border ---
def draw_logo_border(main_group, layout):
    """Draw a border around the logo area"""
    if "logo_area" not in layout:
        return
    
    # Create a rectangle bitmap for the border
    border_width = layout["logo_area"]["width"]
    border_height = layout["logo_area"]["height"]
    border_bitmap = displayio.Bitmap(border_width, border_height, 2)
    border_palette = displayio.Palette(2)
    border_palette[0] = 0x000000  # Transparent/black
    border_palette[1] = hex_to_int(layout["logo_area"]["border_color"])  # Border color
    
    # Draw the border (just the outline)
    # Top and bottom edges
    for x in range(border_width):
        border_bitmap[x, 0] = 1  # Top edge
        border_bitmap[x, border_height-1] = 1  # Bottom edge
    
    # Left and right edges
    for y in range(border_height):
        border_bitmap[0, y] = 1  # Left edge
        border_bitmap[border_width-1, y] = 1  # Right edge
    
    # Create a TileGrid for the border
    border_grid = displayio.TileGrid(
        border_bitmap, 
        pixel_shader=border_palette,
        x=layout["logo_area"]["x"],
        y=layout["logo_area"]["y"]
    )
    
    # Add the border to the main group
    main_group.append(border_grid)

# --- Create Pixel-Based Diamond for Base Visualization ---
def create_base_diamond(main_group, first=False, second=False, third=False, layout=None):
    """Create a diamond-shaped base visualization using the layout configuration"""
    if not layout or "bases" not in layout:
        print("Layout configuration missing bases information")
        return
    
    bases_config = layout["bases"]
    
    # Create a group for the bases
    base_group = displayio.Group()
    base_group.x = bases_config.get("x", 0)
    base_group.y = bases_config.get("y", 0)
    
    # Base size (diameter) - smaller for 15x15 layout
    base_size = 2
    
    # Create bitmaps for each base
    for base_name, occupied in [
        ("first", first),
        ("second", second), 
        ("third", third),
        ("home", False)  # Home plate is always shown but never "occupied"
    ]:
        # Get base configuration
        base_config = bases_config.get(base_name, {})
        base_x = base_config.get("x", 0) - base_group.x
        base_y = base_config.get("y", 0) - base_group.y
        
        # Determine color
        if base_name == "home":
            color = hex_to_int(base_config.get("color", "0x444444"))
        else:
            color_key = "color_on" if occupied else "color_off"
            color = hex_to_int(base_config.get(color_key, "0xFFFFFF" if occupied else "0x222222"))
        
        # Create bitmap for this base
        base_bitmap = displayio.Bitmap(base_size, base_size, 2)
        base_palette = displayio.Palette(2)
        base_palette[0] = 0x000000  # Transparent
        base_palette[1] = color  # Base color
        
        # Draw a filled circle (well, a square in this case due to limited resolution)
        for bx in range(base_size):
            for by in range(base_size):
                base_bitmap[bx, by] = 1
        
        # Create TileGrid for this base
        base_grid = displayio.TileGrid(
            base_bitmap,
            pixel_shader=base_palette,
            x=base_x - base_size // 2,  # Center the base at the specified coordinates
            y=base_y - base_size // 2
        )
        
        # Add to the base group
        base_group.append(base_grid)
    
    # Draw lines connecting the bases - simplified for smaller diamond
    # This requires more complex bitmap manipulation - simplified for now
    
    # Add the base group to the main group
    main_group.append(base_group)
    return base_group

def setup_game_day_display(game_data, layout_config):
    """Set up the display for game day using the layout configuration"""
    main_group = displayio.Group()
    
    # Draw the logo border
    draw_logo_border(main_group, layout_config)
    
    # --- Load Team Logo ---
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
        team_display_config = layout_config["team_display"]
        
        # Home team - reduced scale for 7-pixel height
        home_team_label = label.Label(
            terminalio.FONT, 
            text=game_data["home_team"], 
            color=hex_to_int(team_display_config["home_team"]["color"]), 
            x=team_display_config["home_team"]["x"], 
            y=team_display_config["home_team"]["y"],
            scale=1
        )
        main_group.append(home_team_label)
        
        # VS text
        vs_label = label.Label(
            terminalio.FONT, 
            text="v", 
            color=hex_to_int(team_display_config["vs_text"]["color"]), 
            x=team_display_config["vs_text"]["x"], 
            y=team_display_config["vs_text"]["y"],
            scale=1
        )
        main_group.append(vs_label)
        
        # Away team
        away_team_label = label.Label(
            terminalio.FONT, 
            text=game_data["away_team"], 
            color=hex_to_int(team_display_config["away_team"]["color"]), 
            x=team_display_config["away_team"]["x"], 
            y=team_display_config["away_team"]["y"],
            scale=1
        )
        main_group.append(away_team_label)
        
    except Exception as e:
        print("Error creating team display:", e)
    
    # --- Inning ---
    try:
        inning_config = layout_config["inning"]
        inning_label = label.Label(
            terminalio.FONT, 
            text=game_data["inning"], 
            color=hex_to_int(inning_config["color"]), 
            x=inning_config["x"], 
            y=inning_config["y"],
            scale=1
        )
        main_group.append(inning_label)
    except Exception as e:
        print("Error creating inning:", e)
    
    # --- Score ---
    try:
        score_config = layout_config["score"]
        score_text = f"{game_data['home_team']} {game_data['score_home']}-{game_data['score_away']} {game_data['away_team']}"
        score_label = label.Label(
            terminalio.FONT, 
            text=score_text, 
            color=hex_to_int(score_config["color"]), 
            x=score_config["x"], 
            y=score_config["y"],
            scale=1
        )
        main_group.append(score_label)
    except Exception as e:
        print("Error creating score:", e)
    
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
            terminalio.FONT, 
            text=count_text, 
            color=hex_to_int(count_config["color"]), 
            x=count_config["x"], 
            y=count_config["y"],
            scale=1
        )
        main_group.append(count_label)
    except Exception as e:
        print("Error creating count:", e)
    
    return main_group

def setup_off_day_display(team_data, layout_config):
    """Set up the display for off days using the layout configuration"""
    main_group = displayio.Group()
    
    # Draw the logo border
    draw_logo_border(main_group, layout_config)
    
    # Load the logo
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
    
    # Team name and record - adjusted for 7-pixel height
    try:
        team_record = f"{team_data['team']}: {team_data['wins']}-{team_data['losses']}"
        record_label = label.Label(
            terminalio.FONT,
            text=team_record,
            color=0x00FFFF,
            x=19,
            y=8,
            scale=1
        )
        main_group.append(record_label)
    except Exception as e:
        print("Error creating team record:", e)
    
    # Next game information
    try:
        next_game_text = f"NEXT: {team_data['next_date']}"
        next_game_label = label.Label(
            terminalio.FONT,
            text=next_game_text,
            color=0xFFFFFF,
            x=19,
            y=16,
            scale=1
        )
        main_group.append(next_game_label)
        
        # Opponent
        opponent_text = f"vs {team_data['next_opponent']}"
        opponent_label = label.Label(
            terminalio.FONT,
            text=opponent_text,
            color=0x00FFFF,
            x=19,
            y=24,
            scale=1
        )
        main_group.append(opponent_label)
    except Exception as e:
        print("Error creating next game info:", e)
    
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

# Static team data for off-day display
team_data = {
    "team": "ATL",
    "wins": 48,
    "losses": 30,
    "next_date": "Apr 16",
    "next_opponent": "NYM"
}

# Load layout configuration
layout_config = load_layout_config()

# Show MLB startup logo first
show_mlb_startup_logo()

# Determine display mode (game day or off day)
# For now, use static setting - eventually will be based on ESPN API data
display_mode = "GAME_DAY"  # or "OFF_DAY"

# Setup and display the appropriate screen
if display_mode == "GAME_DAY":
    main_group = setup_game_day_display(game_state, layout_config)
else:
    main_group = setup_off_day_display(team_data, layout_config)

# Show the display
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
