# MLB Scoreboard for CircuitPython

A CircuitPython project for displaying MLB baseball scoreboard data on RGB LED matrices using the ESP32-S3 RGB Matrix Portal or other Adafruit portal devices.

![MLB Scoreboard Preview](docs/images/preview.jpg)

## Overview

This project displays live MLB baseball scores and game information on an RGB LED matrix display. It shows:

- Live game scores with team colors
- Current game status and inning information
- Base runners and count (balls/strikes/outs)
- Division standings
- Upcoming schedule for your favorite team

The project is designed specifically for the ESP32-S3 Matrix Portal from Adafruit, but with minimal modifications can work on other CircuitPython-compatible devices with displays.

## Features

- **Live Game Data**: Shows real-time MLB game scores and stats
- **Multiple Screens**: Rotates between different information screens
- **Team-Specific Colors**: Displays team information using official MLB team colors
- **Low Memory Usage**: Optimized for the ESP32-S3's limited memory
- **Network Status Indicator**: NeoPixel shows connection and data status
- **Configurable Settings**: Easy configuration via settings.toml file

## Hardware Requirements

- [Adafruit Matrix Portal S3 - ESP32-S3 Powered](https://www.adafruit.com/product/5778)
- RGB LED Matrix (32x64 pixels recommended, other sizes supported)
- USB-C cable for power and programming
- Optional: Separate 5V power supply for matrix brightness

## Software Requirements

- CircuitPython 8.2.0 or newer
- Required libraries (included in lib directory)

## Installation

1. Update your Matrix Portal S3 to CircuitPython 8.2.0 or newer
2. Download this repository
3. Copy the following to your CIRCUITPY drive:
   - `code.py`
   - `settings.toml` (edit with your WiFi credentials)
   - `packages` directory
   - `lib` directory (if not already present with required libraries)

## Configuration

Edit the `settings.toml` file to configure your MLB Scoreboard:

```toml
# WiFi Settings
WIFI_SSID = "Your_WiFi_Name"
WIFI_PASSWORD = "Your_WiFi_Password"
TIMEZONE = "America/New_York"  # Your timezone

# Display Settings
DISPLAY_WIDTH = 64      # Matrix width in pixels
DISPLAY_HEIGHT = 32     # Matrix height in pixels
BRIGHTNESS = 0.5        # Display brightness (0.0-1.0)

# MLB Settings
FAVORITE_TEAM = "NYY"   # Your favorite team abbreviation
ROTATION_SPEED = 15.0   # Seconds per screen
```

## Usage

1. Power on your Matrix Portal S3
2. The device will connect to WiFi (blue → yellow → green LEDs during connection)
3. Once connected, the display will show MLB game information
4. The display will automatically rotate between screens
5. The RGB LED indicates status:
   - Green: Normal operation
   - Blue: Startup
   - Yellow: Connecting to WiFi
   - Cyan: Refreshing data
   - Red: Error state

## Screens

The MLB Scoreboard displays several screens that automatically rotate:

1. **Splash Screen**: Shown during startup
2. **Game Screen**: Shows current game scores and status
3. **Standings Screen**: Shows division standings
4. **Schedule Screen**: Shows upcoming games for favorite team

## Team Abbreviations

Use these abbreviations when setting your favorite team:

### American League
- **AL East**: BAL, BOS, NYY, TB, TOR
- **AL Central**: CWS, CLE, DET, KC, MIN
- **AL West**: HOU, LAA, OAK, SEA, TEX

### National League
- **NL East**: ATL, MIA, NYM, PHI, WSH
- **NL Central**: CHC, CIN, MIL, PIT, STL
- **NL West**: ARI, COL, LAD, SD, SF

## Customization

### Adding Custom Screens

You can create custom screens by extending the `Screen` class:

```python
from packages.display.screens import Screen

class MyCustomScreen(Screen):
    def __init__(self, display_manager, debug=False):
        super().__init__(display_manager, title="Custom", debug=debug)
        # Create your UI elements
        
    def update(self, data=None):
        # Update your UI with new data
```

### Modifying Team Colors

Team colors are defined in `packages.display.colors`. You can modify them to your preferences.

## Troubleshooting

### Screen is Black/Not Displaying

- Check that your Matrix Portal is powered adequately
- Ensure settings.toml has correct display dimensions
- Check the onboard NeoPixel for status information

### WiFi Connection Issues

- Verify your WiFi credentials in settings.toml
- Check that your WiFi network is operational
- Try placing the device closer to your router

### Data Not Updating

- Check your internet connection
- Verify the status NeoPixel turns cyan during data refresh
- Check for error messages in the CircuitPython REPL

## Development

### Project Structure

```
mlb_scoreboard/
├── code.py                     # Main entry point
├── settings.toml               # Configuration settings
├── packages/
│   ├── display/                # Display handling modules
│   ├── mlb_api/                # MLB API modules
│   └── utils/                  # Utility modules
└── lib/                        # CircuitPython libraries
```

### Building from Source

The project uses standard CircuitPython so no compilation is needed. Simply copy the files to your device.

## Credits

- Inspired by the [MLB-LED-Scoreboard](https://github.com/MLB-LED-Scoreboard/mlb-led-scoreboard) project for Raspberry Pi
- Uses the MLB Stats API for baseball data
- Built with CircuitPython and Adafruit libraries

## License

This project is licensed under the MIT License - see the LICENSE file for details.
