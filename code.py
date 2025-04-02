"""
MLB Scoreboard for ESP32-S3 RGB Matrix Portal
======================================================
Displays MLB baseball scores and game information on an RGB LED matrix
using the Adafruit Matrix Portal S3 running CircuitPython.

Author: Created with Claude AI
License: MIT
"""

import gc
import time
import board
import busio
import supervisor
import microcontroller
import displayio
import terminalio
import json
import traceback
import neopixel

# First check WiFi connection before importing other modules
import network_check

# Import our packages
from packages.utils.logger import Logger

# Try to load the new ESP WiFi manager first
try:
    from packages.utils.esp_wifi import ESPWiFiManager as WiFiManager
    using_esp_wifi = True
except ImportError:
    from packages.utils.network import WiFiManager
    using_esp_wifi = False

from packages.utils.time_utils import TimeUtil
from packages.ui.display import Display
from packages.ui.screens import (
    SplashScreen,
    GameScreen,
    StandingsScreen,
    ScheduleScreen,
    ErrorScreen,
)
from packages.mlb_api.statsapi import StatsAPIClient

# Try to load settings
try:
    import settings
except ImportError:
    # Default settings if no settings.toml file exists
    class Settings:
        # Network settings
        WIFI_SSID = None  # Will prompt via web config if not set
        WIFI_PASSWORD = None
        TIMEZONE = "America/New_York"
        
        # Display settings
        DISPLAY_WIDTH = 64  # Default for Matrix Portal S3
        DISPLAY_HEIGHT = 32
        DISPLAY_BIT_DEPTH = 6  # 6 bit color (64 levels per channel)
        DISPLAY_ROTATION = 0  # 0 = 0°, 1 = 90°, 2 = 180°, 3 = 270°
        DISPLAY_CHAIN_LENGTH = 1
        DISPLAY_PARALLEL = 1
        
        # MLB settings
        FAVORITE_TEAM = "NYY"  # Team abbreviation
        ROTATION_SPEED = 15.0  # Seconds per screen
        DATA_REFRESH_INTERVAL = 60  # Seconds between API refreshes
        
        # Debug settings
        DEBUG = False  # Enable debug logging
        
    settings = Settings()

# Set up logger
log = Logger("MLB", debug=getattr(settings, "DEBUG", False))
log.info("MLB Scoreboard starting up...")
log.info(f"Using ESP32-SPI WiFi: {using_esp_wifi}")

# Free up memory
gc.collect()
log.debug(f"Free memory: {gc.mem_free()} bytes")

class MLBScoreboard:
    """Main application class for the MLB Scoreboard."""
    
    def __init__(self):
        """Initialize the MLB Scoreboard application."""
        # Initialize logger
        self.log = Logger("MLB", debug=getattr(settings, "DEBUG", False))
        
        # Store config
        self.config = settings
        
        self.last_data_refresh = 0
        self.last_screen_change = 0
        self.current_screen = 0
        self.display = None
        self.network = None
        self.mlb_client = None
        self.screens = []
        self.error_screen = None
        self.time_util = None
        self.debug = getattr(settings, "DEBUG", False)
        
        # Application state
        self.is_initialized = False
        self.has_data = False
        
        # Game data
        self.games = []
        self.favorite_game = None
        self.standings = None
        self.schedule = None
        
        # Status indicator
        # self.status_pixel = neopixel.NeoPixel(
        #     board.NEOPIXEL, 1, brightness=0.2, auto_write=True
        # )
        self.status_pixel[0] = (0, 0, 128)  # Blue during startup
    
    def initialize(self):
        """Initialize all needed components and subsystems."""
        try:
            # Log initialization
            self.log.info("Initializing hardware...")
            
            # Initialize display
            self.display = Display(
                width=getattr(self.config, "DISPLAY_WIDTH", 64),
                height=getattr(self.config, "DISPLAY_HEIGHT", 32),
                chain_length=getattr(self.config, "DISPLAY_CHAIN_LENGTH", 1),
                parallel=getattr(self.config, "DISPLAY_PARALLEL", 1)
            )
            
            # First ensure WiFi connection using network_check
            self.log.info("Ensuring WiFi connection...")
            if not network_check.ensure_wifi_connection():
                self.log.error("Failed to connect to WiFi")
                return False
            
            # Initialize network if WiFi credentials are provided
            from secrets import secrets
            ssid = secrets.get('ssid')
            password = secrets.get('password')
            
            if ssid and password:
                self.log.info("Initializing network...")
                self.network = WiFiManager(
                    status_neopixel=self.status_pixel,
                    debug=self.debug
                )
                
                # Connect with the credentials from secrets
                connected = self.network.connect(ssid, password)
                if connected:
                    self.log.info("Network connected")
                    # Initialize time utilities
                    self.time_util = TimeUtil(
                        network=self.network,
                        timezone=secrets.get("timezone", "America/New_York"),
                        debug=self.debug
                    )
                    
                    # Initialize MLB API client with network parameter
                    self.mlb_client = StatsAPIClient(
                        network=self.network,
                        debug=self.debug
                    )
                else:
                    self.log.error("Failed to connect to network")
                    return False
            
            # Initialize screens
            self._init_screens()
            
            # Create error screen
            self.error_screen = ErrorScreen(
                self.display,
                debug=self.debug
            )
            
            # Show the first screen (splash)
            if self.screens:
                self.display.show(self.screens[0])
            
            # Set status pixel to green
            self.status_pixel[0] = (0, 128, 0)  # Green when ready
            
            self.is_initialized = True
            self.log.info("Initialization complete")
            return True
            
        except Exception as e:
            # Log failure
            self.log.error(f"Failed to initialize: {str(e)}")
            self.log.error(traceback.format_exc())
            self.status_pixel[0] = (128, 0, 0)  # Red on error
            return False
    
    def _init_screens(self):
        """Initialize display screens."""
        try:
            # We need to create a dummy implementation for screens if they don't exist yet
            
            # Create a simple Screen class if it doesn't exist
            if 'SplashScreen' not in globals():
                class BaseScreen:
                    def __init__(self, display, debug=False):
                        self.display = display
                        self.debug = debug
                        self.group = displayio.Group()
                    
                    def update(self, *args, **kwargs):
                        pass
                    
                    def update_animations(self):
                        pass
                
                # Create placeholder screen classes
                global SplashScreen, GameScreen, StandingsScreen, ScheduleScreen, ErrorScreen
                SplashScreen = GameScreen = StandingsScreen = ScheduleScreen = ErrorScreen = BaseScreen
            
            # Add splash screen as the first screen
            self.screens.append(
                SplashScreen(
                    self.display,
                    debug=self.debug
                )
            )
            
            # Game screen will be populated once we have data
            game_screen = GameScreen(
                self.display,
                debug=self.debug
            )
            self.screens.append(game_screen)
            
            # Standings screen
            standings_screen = StandingsScreen(
                self.display,
                debug=self.debug
            )
            self.screens.append(standings_screen)
            
            # Schedule screen
            schedule_screen = ScheduleScreen(
                self.display,
                favorite_team=getattr(settings, "FAVORITE_TEAM", "NYY"),
                debug=self.debug
            )
            self.screens.append(schedule_screen)
            
            # Create error screen
            self.error_screen = ErrorScreen(
                self.display,
                debug=self.debug
            )
            
        except Exception as e:
            self.log.error(f"Failed to initialize screens: {e}")
            raise
    
    def refresh_data(self):
        """Refresh data from the MLB API."""
        try:
            log.info("Refreshing MLB data...")
            
            # Check if network is connected first
            if not self.network:
                self.log.error("Network not initialized")
                # Try to reconnect using network_check
                if network_check.ensure_wifi_connection():
                    # Reinitialize network
                    from secrets import secrets
                    ssid = secrets.get('ssid')
                    password = secrets.get('password')
                    self.network = WiFiManager(
                        status_neopixel=self.status_pixel,
                        debug=self.debug
                    )
                    self.network.connect(ssid, password)
                else:
                    return False
            
            # Check if MLB client exists
            if self.mlb_client is None:
                self.log.error("MLB client not initialized")
                # Try to initialize it if we have network
                if self.network:
                    self.log.info("Attempting to initialize MLB client")
                    self.mlb_client = StatsAPIClient(
                        network=self.network,
                        debug=self.debug
                    )
                else:
                    return False
                
            # Check if time_util exists
            if not hasattr(self, 'time_util') or self.time_util is None:
                self.log.warning("TimeUtil not initialized, creating now")
                if self.network:
                    from secrets import secrets
                    self.time_util = TimeUtil(
                        network=self.network,
                        timezone=secrets.get("timezone", "America/New_York"),
                        debug=self.debug
                    )
                    self.time_util.sync_time()
                current_date = None
            else:
                # Get current date from network time
                current_date = self.time_util.get_current_date()
            
            # Set status pixel to cyan during data fetch
            self.status_pixel[0] = (0, 128, 128)  # Cyan during data refresh
            
            # If we have no date, use the mlb_client's fallback method
            if current_date is None and self.mlb_client and hasattr(self.mlb_client, 'get_current_date_string'):
                current_date = self.mlb_client.get_current_date_string()
            
            # If we still don't have a date, create one manually as last resort
            if current_date is None:
                year, month, day = time.localtime()[:3]
                current_date = f"{year}-{month:02d}-{day:02d}"
                self.log.warning(f"Using fallback date: {current_date}")
            
            log.debug(f"Using date for API calls: {current_date}")
            
            # Get scoreboard data
            self.games = self.mlb_client.get_games(current_date)
            log.info(f"Found {len(self.games)} games for {current_date}")
            
            # Find favorite team's game
            favorite_team = getattr(settings, "FAVORITE_TEAM", "NYY")
            self.favorite_game = self.mlb_client.get_team_game(favorite_team, current_date)
            
            if self.favorite_game:
                log.info(f"Found game for {favorite_team}: {self.favorite_game['away_team']} @ {self.favorite_game['home_team']}")
            else:
                log.info(f"No game found for {favorite_team} today")
            
            # Get standings data
            self.standings = self.mlb_client.get_standings()
            
            # Get schedule data for favorite team
            self.schedule = self.mlb_client.get_team_schedule(favorite_team, limit=5)
            
            # Update screens with new data
            self._update_screens()
            
            # Set status pixel back to green after successful refresh
            self.status_pixel[0] = (0, 128, 0)  # Green when ready
            
            self.has_data = True
            self.last_data_refresh = time.monotonic()
            
            # Free up memory after data refresh
            gc.collect()
            log.debug(f"Free memory after refresh: {gc.mem_free()} bytes")
            
            return True
            
        except Exception as e:
            log.error(f"Failed to refresh data: {e}")
            self.status_pixel[0] = (128, 64, 0)  # Orange on data error
            
            # Show error on the display
            if self.error_screen:
                self.error_screen.update(
                    title="Data Error",
                    message=f"Failed to refresh data:\n{type(e).__name__}: {str(e)}"
                )
                self.display.show(self.error_screen)
                
            return False
    
    def _update_screens(self):
        """Update all screens with the latest data."""
        for screen in self.screens:
            if isinstance(screen, GameScreen) and self.games:
                screen.update(self.games, self.favorite_game)
            elif isinstance(screen, StandingsScreen) and self.standings:
                screen.update(self.standings)
            elif isinstance(screen, ScheduleScreen) and self.schedule:
                screen.update(self.schedule)
    
    def rotate_screen(self):
        """Rotate to the next screen."""
        # Skip if only one screen or not yet initialized
        if len(self.screens) <= 1 or not self.is_initialized:
            return
            
        # Increment screen index
        self.current_screen = (self.current_screen + 1) % len(self.screens)
        
        # Show the new screen
        self.display.show(self.screens[self.current_screen])
        self.last_screen_change = time.monotonic()
    
    def run(self):
        """Main application loop."""
        # Try to initialize the system
        if not self.initialize():
            # If initialization failed, show the error screen
            if hasattr(self, "display") and self.display and self.error_screen:
                self.error_screen.update(
                    title="Init Error",
                    message="Failed to initialize system.\nCheck WiFi connection."
                )
                self.display.show(self.error_screen)
            
            # Try simple recovery - reconnect WiFi
            self.log.info("Attempting recovery...")
            if network_check.ensure_wifi_connection(max_attempts=5):
                self.log.info("WiFi reconnected, restarting...")
                supervisor.reload()
            else:
                # If reconnect failed, enter fail-safe mode
                while True:
                    # Blink status LED to indicate error
                    self.status_pixel[0] = (128, 0, 0)  # Red
                    time.sleep(0.5)
                    self.status_pixel[0] = (0, 0, 0)  # Off
                    time.sleep(0.5)
                    
                    # Check for reset command
                    if supervisor.runtime.serial_bytes_available:
                        supervisor.reload()
        
        # Main loop
        while True:
            try:
                now = time.monotonic()
                
                # Check if we need to refresh data
                refresh_interval = getattr(settings, "DATA_REFRESH_INTERVAL", 60)
                if not self.has_data or (now - self.last_data_refresh) >= refresh_interval:
                    self.refresh_data()
                
                # Check if we need to rotate screens
                rotation_speed = getattr(settings, "ROTATION_SPEED", 15.0)
                if self.has_data and (now - self.last_screen_change) >= rotation_speed:
                    self.rotate_screen()
                
                # Update the current screen
                current_screen = self.screens[self.current_screen]
                current_screen.update_animations()
                
                # Keep the display refreshed
                self.display.refresh()
                
                # Small delay to prevent overloading the CPU
                time.sleep(0.1)
                
                # Memory management
                if now % 60 < 0.1:  # Roughly every minute
                    log.debug(f"Free memory: {gc.mem_free()} bytes")
                    gc.collect()
                
                # Check for serial input (to enable REPL)
                if supervisor.runtime.serial_bytes_available:
                    input_byte = input().strip().lower()
                    if input_byte == 'r':  # Press 'r' to refresh data
                        self.refresh_data()
                    elif input_byte == 's':  # Press 's' to switch screens
                        self.rotate_screen()
                    elif input_byte == 'd':  # Press 'd' to show debug info
                        log.info(f"Free memory: {gc.mem_free()} bytes")
                    elif input_byte == 'q':  # Press 'q' to restart
                        supervisor.reload()
                
            except Exception as e:
                log.error(f"Error in main loop: {e}")
                self.status_pixel[0] = (128, 0, 0)  # Red on error
                
                # Show error on the display
                if self.error_screen:
                    self.error_screen.update(
                        title="Runtime Error",
                        message=f"Error in main loop:\n{type(e).__name__}: {str(e)}"
                    )
                    self.display.show(self.error_screen)
                
                # Wait a bit before continuing
                time.sleep(5)
                
                # Try to recover - check WiFi connection
                if not network_check.ensure_wifi_connection():
                    self.log.warning("WiFi connection lost, restarting...")
                    time.sleep(1)
                    supervisor.reload()
                
                # Continue with normal operation
                self.status_pixel[0] = (0, 128, 0)  # Back to green


# Initialize and run the application
if __name__ == "__main__":
    # Run the network test first to ensure WiFi is working
    if not network_check.ensure_wifi_connection():
        log.error("Failed to establish WiFi connection - cannot proceed")
        
        # Set up status pixel for visual feedback
        status_pixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2)
        
        # Flash red error indicator
        while True:
            status_pixel[0] = (50, 0, 0)  # Red
            time.sleep(0.5)
            status_pixel[0] = (0, 0, 0)  # Off
            time.sleep(0.5)
            
            # Check if user wants to retry
            if supervisor.runtime.serial_bytes_available:
                supervisor.reload()
    else:
        # WiFi is connected, proceed with application
        app = MLBScoreboard()
        app.run()
