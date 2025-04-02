# Debugging utilities
"""
ESP32-S3 CircuitPython Debug Utilities
Provides advanced logging and debugging capabilities
"""
import time
import gc
import traceback
import supervisor
import microcontroller
import board
import os

# Debug levels
CRITICAL = 50
ERROR = 40
WARNING = 30
INFO = 20
DEBUG = 10
NOTSET = 0

# Debug level names for human-readable output
_LEVEL_NAMES = {
    CRITICAL: "CRITICAL",
    ERROR: "ERROR",
    WARNING: "WARNING",
    INFO: "INFO",
    DEBUG: "DEBUG",
    NOTSET: "NOTSET"
}

# Default configuration
_DEFAULT_CONFIG = {
    "level": INFO,
    "file_logging": False,
    "log_file": "/logs/debug.log",
    "max_file_size": 512 * 1024,  # 512 KB max log file size
    "include_timestamp": True,
    "include_memory": False,
    "color_output": True
}

# ANSI color codes
_COLORS = {
    CRITICAL: "\033[1;31m",  # Bold Red
    ERROR: "\033[31m",       # Red
    WARNING: "\033[33m",     # Yellow
    INFO: "\033[32m",        # Green
    DEBUG: "\033[36m",       # Cyan
    NOTSET: "\033[0m"        # Reset
}
_COLOR_RESET = "\033[0m"

# Try to load settings
try:
    import toml
    try:
        with open("/settings.toml", "r") as f:
            settings = toml.load(f)
            debug_settings = settings.get("debug", {})
            
            # Update default config with settings from TOML
            for key, value in debug_settings.items():
                if key in _DEFAULT_CONFIG:
                    _DEFAULT_CONFIG[key] = value
            
            # Convert text level to numeric
            if isinstance(_DEFAULT_CONFIG["level"], str):
                level_map = {name.lower(): level for level, name in _LEVEL_NAMES.items()}
                _DEFAULT_CONFIG["level"] = level_map.get(_DEFAULT_CONFIG["level"].lower(), INFO)
                
    except (OSError, ValueError):
        # Use defaults if settings file can't be loaded
        pass
except ImportError:
    # Use defaults if toml module is not available
    pass

class Logger:
    """
    Advanced logger for CircuitPython
    Supports console and file output with configurable levels
    """
    def __init__(self, name, **kwargs):
        self.name = name
        
        # Copy default config and update with any provided kwargs
        self.config = _DEFAULT_CONFIG.copy()
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value
        
        # Create log directory and file if file logging is enabled
        if self.config["file_logging"]:
            log_dir = os.path.dirname(self.config["log_file"])
            try:
                os.stat(log_dir)
            except OSError:
                try:
                    os.mkdir(log_dir)
                except OSError:
                    # Can't create directory, disable file logging
                    self.config["file_logging"] = False
    
    def _get_prefix(self, level):
        """Generate the prefix for log messages"""
        prefix = ""
        
        # Add timestamp if configured
        if self.config["include_timestamp"]:
            prefix += f"{time.monotonic():.3f} "
        
        # Add level and name
        prefix += f"[{_LEVEL_NAMES[level]}] {self.name}: "
        
        # Add memory info if configured
        if self.config["include_memory"]:
            gc.collect()
            prefix += f"(Mem: {gc.mem_free()} free) "
            
        return prefix
    
    def _write_to_file(self, message):
        """Write a message to the log file"""
        if not self.config["file_logging"]:
            return
            
        try:
            # Check file size
            try:
                size = os.stat(self.config["log_file"])[6]
                if size > self.config["max_file_size"]:
                    # Truncate file if it's too large
                    with open(self.config["log_file"], "w") as f:
                        f.write("Log truncated due to size limit\n")
            except OSError:
                # File doesn't exist yet
                pass
                
            # Append to log file
            with open(self.config["log_file"], "a") as f:
                f.write(message + "\n")
        except OSError as e:
            # Print error to console but don't raise
            print(f"Log file write error: {e}")
    
    def log(self, level, message, *args):
        """Log a message at the specified level"""
        if level < self.config["level"]:
            return
            
        # Format message with args if provided
        if args:
            try:
                message = message % args
            except Exception as e:
                message = f"{message} [Error formatting: {e}]"
        
        # Create full message with prefix
        full_message = self._get_prefix(level) + message
        
        # Console output with colors if enabled
        if self.config["color_output"] and level >= self.config["level"]:
            print(f"{_COLORS.get(level, '')}{full_message}{_COLOR_RESET}")
        else:
            print(full_message)
            
        # File output if enabled
        self._write_to_file(full_message)
    
    def debug(self, message, *args):
        """Log a DEBUG level message"""
        self.log(DEBUG, message, *args)
    
    def info(self, message, *args):
        """Log an INFO level message"""
        self.log(INFO, message, *args)
    
    def warning(self, message, *args):
        """Log a WARNING level message"""
        self.log(WARNING, message, *args)
    
    def error(self, message, *args):
        """Log an ERROR level message"""
        self.log(ERROR, message, *args)
    
    def critical(self, message, *args):
        """Log a CRITICAL level message"""
        self.log(CRITICAL, message, *args)
    
    def exception(self, message, *args):
        """Log an ERROR level message with exception info"""
        exc = traceback.format_exception(
            None, 
            supervisor.get_previous_traceback().exception,
            supervisor.get_previous_traceback().traceback
        )
        exc_text = "".join(exc)
        self.error(f"{message}\n{exc_text}", *args)

# System information functions
def get_system_info():
    """Get detailed system information"""
    info = {
        "board": getattr(board, "board_id", "unknown"),
        "cpu": {
            "frequency": microcontroller.cpu.frequency,
            "temperature": microcontroller.cpu.temperature,
            "voltage": microcontroller.cpu.voltage,
        },
        "circuitpython": {
            "version": supervisor.runtime.version,
            "board": supervisor.runtime.board,
        },
        "memory": {
            "free": gc.mem_free(),
            "allocated": gc.mem_alloc(),
            "total": gc.mem_free() + gc.mem_alloc()
        },
        "filesystem": {
            "root": os.statvfs("/")
        }
    }
    
    # Calculate filesystem usage
    root_fs = info["filesystem"]["root"]
    block_size = root_fs[0]
    total_blocks = root_fs[2]
    free_blocks = root_fs[3]
    info["filesystem"]["total"] = block_size * total_blocks
    info["filesystem"]["free"] = block_size * free_blocks
    info["filesystem"]["used"] = block_size * (total_blocks - free_blocks)
    
    return info

def print_system_info():
    """Print detailed system information to console"""
    info = get_system_info()
    
    print("\n=== System Information ===")
    print(f"Board: {info['board']}")
    print(f"CircuitPython: {info['circuitpython']['version']}")
    print(f"CPU Frequency: {info['cpu']['frequency']/1000000:.1f} MHz")
    print(f"CPU Temperature: {info['cpu']['temperature']:.1f}°C")
    print(f"CPU Voltage: {info['cpu']['voltage']:.2f}V")
    
    print("\n=== Memory Information ===")
    print(f"Free: {info['memory']['free']} bytes")
    print(f"Used: {info['memory']['allocated']} bytes")
    print(f"Total: {info['memory']['total']} bytes")
    
    print("\n=== Filesystem Information ===")
    print(f"Total: {info['filesystem']['total']/1024:.1f} KB")
    print(f"Used: {info['filesystem']['used']/1024:.1f} KB")
    print(f"Free: {info['filesystem']['free']/1024:.1f} KB")
    
    return info

# Create default logger
system_log = Logger("SYSTEM")