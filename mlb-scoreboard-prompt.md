# Atlanta Braves MLB Scoreboard Development Prompt

## Project Overview

You're helping develop a CircuitPython project for a 64x32 RGB LED matrix that displays Atlanta Braves MLB game information using an Adafruit MatrixPortal S3. The immediate goal is to implement a configuration-based layout system and Game Day screen with proper layout and base runner visualization, followed by ESPN API integration. We'll be adopting the MLB-LED-Scoreboard project's approach of using configuration files to define element positions.

## Core Requirements

1. The Braves logo must be persistently visible on all screens
2. The Game Day screen should display:
   - Team matchup (ATL vs Opponent)
   - Current inning status (Top/Bottom and inning number)
   - Base runners (using a pixel-based diamond visualization)
   - Ball-Strike-Out counts
   - Current score
3. The display must be optimized for a 64x32 pixel RGB matrix
4. All code must be memory-efficient for the ESP32-S3 microcontroller

## Reference Resources

- MLB-LED-Scoreboard GitHub: https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard
  - Look especially at `data/scoreboard/w64h32.json` for layout configuration
  - Review `renderers/games.py` for the game display logic
  - Study `renderers/bases.py` for base runner visualization implementation
  - Understand how `data/config.json.example` handles different configurations

- Adafruit Sports Scoreboard Guide: 
  - https://learn.adafruit.com/led-matrix-sports-scoreboard/code-the-scoreboard
  - https://learn.adafruit.com/led-matrix-sports-scoreboard/use-and-customization

- CircuitPython Documentation:
  - RGBMatrix module: https://docs.circuitpython.org/en/latest/shared-bindings/rgbmatrix/
  - JSON module: https://docs.circuitpython.org/en/latest/shared-bindings/json/
  - DisplayIO module: https://docs.circuitpython.org/en/latest/shared-bindings/displayio/

## Current Files

1. `code.py` - Main application file (needs to be updated)
2. `/images/ATL.bmp` - Braves logo bitmap (already exists)
3. `/fonts/font.bdf` - Optional bitmap font (may need to be created)
4. `settings.toml` - WiFi and configuration settings (needs cleanup)
5. `/layouts/w64h32.json` - NEW: Layout configuration file (needs to be created)

## Immediate Tasks

### 1. Create Layout Configuration File

Create a new `/layouts/w64h32.json` file defining all display element positions:
```json
{
  "logo": {
    "x": 0,
    "y": 0,
    "scale": 1
  },
  "team_matchup": {
    "x": 18,
    "y": 4,
    "font": "font.bdf",
    "color": "0xFFFFFF"
  },
  "inning": {
    "x": 18,
    "y": 14,
    "font": "terminalio",
    "color": "0xFFFFFF"
  },
  "score": {
    "x": 18,
    "y": 26,
    "font": "terminalio",
    "color": "0xFFFFFF"
  },
  "bases": {
    "x": 32,
    "y": 10,
    "first": {
      "x": 38,
      "y": 16,
      "color_on": "0xFFFFFF",
      "color_off": "0x222222"
    },
    "second": {
      "x": 32,
      "y": 10,
      "color_on": "0xFFFFFF",
      "color_off": "0x222222"
    },
    "third": {
      "x": 26,
      "y": 16,
      "color_on": "0xFFFFFF",
      "color_off": "0x222222"
    },
    "home": {
      "x": 32,
      "y": 22,
      "color": "0x444444"
    }
  },
  "count": {
    "x": 45,
    "y": 16,
    "font": "terminalio",
    "color": "0xFFFFFF"
  }
}
```

### 2. Clean up `settings.toml`

Create a streamlined `settings.toml` file with:
- WiFi credentials (SSID/password)
- Display mode setting (GAME_DAY or OFF_DAY for now, before API integration)
- Braves team_id (15)
- Update interval settings

### 3. Implement Layout Configuration Loading

Add code to:
- Load the layout configuration file
- Parse JSON into a usable format
- Apply coordinates from configuration to display elements

### 4. Implement Game Day Screen

Develop the Game Day screen with:
- Proper initialization and release of the display
- Logo positioned according to layout config
- Team matchup and inning at positions from config
- Score at position from config
- Interactive base runner diamond visualization
- Ball-Strike-Out counters

### 5. Base Runner Diamond Visualization

Create a pixel-based diamond visualization that:
- Shows all bases in a diamond pattern
- Highlights occupied bases with a different color
- Is clearly visible on the LED matrix
- Updates based on game state
- Uses positions from the layout configuration

## Implementation Guidelines

### Display Initialization

```python
import board
import displayio
import rgbmatrix
import framebufferio

# Release any resources currently in use for the displays
displayio.release_displays()

# Configure matrix
matrix = rgbmatrix.RGBMatrix(
    width=64, height=32, bit_depth=4,
    rgb_pins=[board.MTX_R1, board.MTX_G1, board.MTX_B1, board.MTX_R2, board.MTX_G2, board.MTX_B2],
    addr_pins=[board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC, board.MTX_ADDRD],
    clock_pin=board.MTX_CLK, latch_pin=board.MTX_LAT, output_enable_pin=board.MTX_OE
)

# Create the display
display = framebufferio.FramebufferDisplay(matrix)
```

### Memory Optimization

- Use `gc.collect()` after major display updates
- Minimize string operations in tight loops
- Reuse display groups when possible
- Limit the total number of display elements

### Base Diamond Visualization

Consider implementing the base diamond using bitmap or simple shapes rather than text/characters:

```python
def create_base_diamond(base_group, first=False, second=False, third=False):
    """Create a diamond-shaped base indicator using pixels"""
    # Implementation will draw a diamond shape with different colors for occupied bases
    # ...
```

### Color Recommendations

- Team Logo: Team colors (Braves red)
- Base Occupied: Bright white or yellow
- Base Empty: Dark gray
- Text: White or light colors
- Background: Black/dark blue

## Expected Output

The final Game Day screen should look approximately like:

```
+----------------------------------------------------------------+
|                                                                |
| [ATL LOGO]  ATL v OPP                                          |
|             TOP 5                                              |
|                        ○                                       |
|                       / \                                      |
|             SCORE: 3-2 ○─●                                     |
|                       \ /                                      |
|                        ○       B:2 S:1 O:1                     |
|                                                                |
+----------------------------------------------------------------+
```

Note that exact positions of all elements should be defined in the layout configuration file rather than hardcoded in the implementation. This allows for easy adjustment and fine-tuning without code modifications.

## Next Steps After Game Day Screen

1. Create off-day layout configuration
   ```json
   {
     "logo": {
       "x": 24,
       "y": 2,
       "scale": 1
     },
     "record": {
       "x": 16,
       "y": 18,
       "font": "font.bdf",
       "color": "0xFFFFFF"
     },
     "next_game": {
       "x": 8,
       "y": 24,
       "font": "terminalio",
       "color": "0xFFFFFF"
     }
   }
   ```

2. Implement settings.toml parsing 
3. Add ESPN API integration for live data
4. Create Off Day screen layout using configuration
5. Implement automatic mode switching based on game schedule
6. Add support for different matrix sizes (make layouts swappable)

## Debugging Approach

Include simple diagnostic information in your implementation:
- Print pixel coordinates during setup
- Add memory usage reporting
- Include version/mode information

Add a debug mode in settings.toml to enable:
```toml
[debug]
enabled = true
show_coordinates = true
report_memory = true
```

Consider adding a simple layout editor/preview tool:
```python
def print_layout_grid():
    """Print a text representation of the current layout for debugging"""
    grid = [[" " for _ in range(64)] for _ in range(32)]
    
    # Mark key layout positions from configuration
    for element, config in layout.items():
        if isinstance(config, dict) and "x" in config and "y" in config:
            x, y = config["x"], config["y"]
            if 0 <= x < 64 and 0 <= y < 32:
                grid[y][x] = "X"
    
    # Print the grid
    print("Display Layout (64x32):")
    for row in grid:
        print("".join(row))
```

Use the camera to capture the actual display output for iterative improvements.

## Required Resources

Review the full project analysis document for comprehensive details on the implementation strategy and design considerations.

Let me know if you need any specific code snippets, additional reference links, or have questions about the implementation approach!