"""
Logger utility for MLB Scoreboard
================================
Simple logging utility with levels and timestamps.
"""

import time

class Logger:
    """Simple logging utility."""
    
    # Log levels
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    
    def __init__(self, name, level=INFO, debug=False):
        """Initialize logger.
        
        Args:
            name: Logger name
            level: Minimum log level to display
            debug: Enable debug logging
        """
        self.name = name
        self.level = self.DEBUG if debug else level
    
    def _log(self, level, message, *args):
        """Log a message if level meets threshold.
        
        Args:
            level: Message log level
            message: Message to log
            *args: Format arguments for message
        """
        if level >= self.level:
            # Format message with args if any
            if args:
                message = message.format(*args)
            
            # Get timestamp
            timestamp = time.localtime()
            time_str = "{:02d}:{:02d}:{:02d}".format(
                timestamp.tm_hour,
                timestamp.tm_min,
                timestamp.tm_sec
            )
            
            # Format level
            if level == self.DEBUG:
                level_str = "DEBUG"
            elif level == self.INFO:
                level_str = "INFO"
            elif level == self.WARNING:
                level_str = "WARNING"
            elif level == self.ERROR:
                level_str = "ERROR"
            else:
                level_str = "LOG"
            
            # Print log message
            print(f"[{time_str}] {self.name} {level_str}: {message}")
    
    def debug(self, message, *args):
        """Log a debug message.
        
        Args:
            message: Message to log
            *args: Format arguments for message
        """
        self._log(self.DEBUG, message, *args)
    
    def info(self, message, *args):
        """Log an info message.
        
        Args:
            message: Message to log
            *args: Format arguments for message
        """
        self._log(self.INFO, message, *args)
    
    def warning(self, message, *args):
        """Log a warning message.
        
        Args:
            message: Message to log
            *args: Format arguments for message
        """
        self._log(self.WARNING, message, *args)
    
    def error(self, message, *args):
        """Log an error message.
        
        Args:
            message: Message to log
            *args: Format arguments for message
        """
        self._log(self.ERROR, message, *args)
