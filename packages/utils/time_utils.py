# Time manipulation
"""
Time utilities for MLB Scoreboard
================================
Handles time synchronization, timezone conversion, and formatting.
"""

import time
import rtc
import adafruit_ntp
from packages.utils.logger import Logger

class TimeUtil:
    """Time utility for handling time-related operations."""
    
    def __init__(self, network, timezone="America/New_York", debug=False):
        """Initialize time utility.
        
        Args:
            network: Network instance for NTP sync
            timezone: Timezone name
            debug: Enable debug logging
        """
        self.network = network
        self.timezone = timezone
        self.log = Logger("Time", debug=debug)
        self.debug = debug
        self.ntp = None
        self.rtc = rtc.RTC()
        self.time_offset = self._get_timezone_offset(timezone)
        self.is_synced = False
    
    def _get_timezone_offset(self, timezone):
        """Get timezone offset in seconds.
        
        Args:
            timezone: Timezone name
            
        Returns:
            Offset in seconds
        """
        # Simple timezone offsets
        offsets = {
            "America/New_York": -5 * 3600,     # EST (-5)
            "America/Chicago": -6 * 3600,      # CST (-6)
            "America/Denver": -7 * 3600,       # MST (-7)
            "America/Los_Angeles": -8 * 3600,  # PST (-8)
            "America/Anchorage": -9 * 3600,    # AKST (-9)
            "Pacific/Honolulu": -10 * 3600,    # HST (-10)
            "Europe/London": 0,                # GMT (+0)
            "Europe/Paris": 1 * 3600,          # CET (+1)
            "Europe/Helsinki": 2 * 3600,       # EET (+2)
            "Asia/Tokyo": 9 * 3600,            # JST (+9)
        }
        
        # Apply DST adjustment if applicable
        # This is a simplified approach - for production, use a proper timezone library
        t = time.localtime()
        is_dst = 0  # Default: no DST
        
        # Very simple DST check for US timezones:
        # DST from second Sunday in March to first Sunday in November
        if timezone.startswith("America/"):
            month = t[1]
            day = t[2]
            weekday = t[6]  # 0 is Monday, 6 is Sunday
            
            # March to November
            if 3 <= month <= 11:
                # March: DST starts on the second Sunday
                if month == 3 and day >= 8 and day <= 14 and weekday == 6:
                    # Second Sunday in March
                    is_dst = 1
                elif month == 3 and day > 14:
                    # After second Sunday in March
                    is_dst = 1
                # November: DST ends on the first Sunday
                elif month == 11 and day <= 7 and weekday == 6:
                    # First Sunday in November
                    is_dst = 0
                elif month == 11 and day < 7:
                    # Before first Sunday in November
                    is_dst = 1
                # April through October
                elif 4 <= month <= 10:
                    is_dst = 1
        
        # Apply DST adjustment (add 1 hour) if needed
        offset = offsets.get(timezone, 0)
        if is_dst:
            offset += 3600
            
        return offset
    
    def sync_time(self, max_attempts=3):
        """Synchronize time with NTP server.
        
        Args:
            max_attempts: Maximum number of sync attempts
            
        Returns:
            True if sync successful, False otherwise
        """
        if self.is_synced:
            return True
            
        self.log.info(f"Syncing time with NTP server...")
        
        for attempt in range(max_attempts):
            try:
                # Create NTP client
                self.ntp = adafruit_ntp.NTP(self.network.pool, tz_offset=0)
                
                # Get the time from NTP
                ntp_time = self.ntp.datetime
                
                # Apply timezone offset manually (since ESP32-S3 doesn't support tzinfo)
                epoch_time = time.mktime(ntp_time) + self.time_offset
                local_time = time.localtime(epoch_time)
                
                # Set the RTC
                self.rtc.datetime = local_time
                
                self.log.info(f"Time synchronized: {self.format_datetime()}")
                self.is_synced = True
                return True
                
            except Exception as e:
                self.log.error(f"Time sync attempt {attempt+1} failed: {e}")
                time.sleep(1)
        
        self.log.error(f"Failed to sync time after {max_attempts} attempts")
        return False
    
    def format_datetime(self, t=None):
        """Format datetime as a readable string.
        
        Args:
            t: Time tuple (defaults to current time)
            
        Returns:
            Formatted datetime string
        """
        if t is None:
            t = time.localtime()
            
        return f"{t[0]:04d}-{t[1]:02d}-{t[2]:02d} {t[3]:02d}:{t[4]:02d}:{t[5]:02d}"
    
    def format_time(self, t=None):
        """Format time as a readable string.
        
        Args:
            t: Time tuple (defaults to current time)
            
        Returns:
            Formatted time string (HH:MM)
        """
        if t is None:
            t = time.localtime()
            
        return f"{t[3]:02d}:{t[4]:02d}"
    
    def format_date(self, t=None):
        """Format date as a readable string.
        
        Args:
            t: Time tuple (defaults to current time)
            
        Returns:
            Formatted date string (YYYY-MM-DD)
        """
        if t is None:
            t = time.localtime()
            
        return f"{t[0]:04d}-{t[1]:02d}-{t[2]:02d}"
    
    def get_current_date(self):
        """Get current date in format YYYY-MM-DD.
        
        Returns:
            Current date string
        """
        t = time.localtime()
        return self.format_date(t)
    
    def parse_isotime(self, iso_time):
        """Parse ISO 8601 time string (very simplified).
        
        Args:
            iso_time: ISO time string (YYYY-MM-DDTHH:MM:SSZ)
            
        Returns:
            Time tuple
        """
        try:
            # Split the date and time parts
            date_part, time_part = iso_time.split("T")
            
            # Parse date
            year, month, day = [int(p) for p in date_part.split("-")]
            
            # Parse time (ignoring sub-seconds)
            time_part = time_part.split(".")[0].replace("Z", "")
            hour, minute, second = [int(p) for p in time_part.split(":")]
            
            # Create time tuple (year, month, day, hour, minute, second, weekday, yearday, isdst)
            # We don't calculate weekday and yearday here
            return (year, month, day, hour, minute, second, 0, 0, 0)
            
        except Exception as e:
            self.log.error(f"Error parsing ISO time '{iso_time}': {e}")
            return None
    
    def convert_game_time(self, game_time):
        """Convert game time to local time string.
        
        Args:
            game_time: Game time in ISO format
            
        Returns:
            Formatted local time string (HH:MM)
        """
        try:
            # Parse the ISO time
            parsed_time = self.parse_isotime(game_time)
            if not parsed_time:
                return "TBD"
                
            # Convert to epoch time
            epoch_time = time.mktime(parsed_time)
            
            # Apply timezone offset
            local_epoch = epoch_time + self.time_offset
            
            # Convert back to time tuple
            local_time = time.localtime(local_epoch)
            
            # Format as HH:MM
            return self.format_time(local_time)
            
        except Exception as e:
            self.log.error(f"Error converting game time '{game_time}': {e}")
            return "TBD"
