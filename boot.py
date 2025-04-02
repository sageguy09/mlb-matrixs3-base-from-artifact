# Initial boot configuration
"""
Boot configuration to ensure REPL accessibility
with enhanced debugging for startup errors
"""
import sys
import time
import gc

# List to capture boot logs
boot_logs = []

def log(message, error=False):
    """Log a message to both console and boot log list"""
    timestamp = time.monotonic()
    formatted = f"[BOOT {timestamp:.3f}] {'ERROR: ' if error else ''}{message}"
    print(formatted)
    boot_logs.append(formatted)

def save_boot_log():
    """Save boot logs to a file"""
    try:
        with open("/boot_log.txt", "w") as f:
            f.write("\n".join(boot_logs))
    except Exception as e:
        print(f"Failed to write boot log: {e}")

def blink_error(count=3, fast=False):
    """Blink the onboard LED to indicate an error"""
    try:
        import board
        import digitalio
        led = digitalio.DigitalInOut(board.LED)
        led.direction = digitalio.Direction.OUTPUT
        
        # Blink LED to indicate error
        delay = 0.1 if fast else 0.2
        for _ in range(count):
            led.value = True
            time.sleep(delay)
            led.value = False
            time.sleep(delay)
    except Exception:
        # Can't signal via LED, just continue
        pass

# Begin main boot sequence with error handling
try:
    log("Boot sequence starting")
    gc.collect()  # Start with clean memory
    
    # Import necessary modules within try block to catch import errors
    try:
        import supervisor
        import board
        import storage
        log("Core modules imported")
    except Exception as e:
        log(f"Failed to import core modules: {str(e)}", error=True)
        blink_error(5, fast=True)
        raise  # Re-raise to see the full traceback
    
    # Configure supervisor for better debugging
    try:
        supervisor.runtime.autoreload = False
        supervisor.disable_autoreload()
        log("Autoreload disabled")
    except Exception as e:
        log(f"Failed to configure supervisor: {str(e)}", error=True)
    
    # Give the USB connection time to establish
    time.sleep(1)
    
    # Print CircuitPython version
    version = sys.implementation.version
    version_str = f"{version[0]}.{version[1]}.{version[2]}"
    log(f"CircuitPython version: {version_str}")
    
    # Log memory stats
    gc.collect()
    free = gc.mem_free()
    alloc = gc.mem_alloc()
    log(f"Memory: {free} bytes free, {alloc} bytes used")
    
    # Try to mount storage as read-write to enable logging
    try:
        storage.remount("/", readonly=False)
        log("Storage remounted as read-write for logging")
    except Exception as e:
        log(f"Storage remount error: {str(e)}", error=True)
    
    # Print device information
    log(f"Board: {board.board_id}")
    log("REPL is enabled - Type help() for more info")

    # Final boot message
    log("Boot sequence completed successfully")
    
except Exception as e:
    # Catch-all for any unhandled exceptions during boot
    error_msg = f"BOOT ERROR: {str(e)}"
    print("\n" + "!" * 40)
    print(error_msg)
    print("!" * 40 + "\n")
    
    # Add to boot logs
    boot_logs.append(error_msg)
    
    # Try to get traceback info
    import traceback
    tb_text = traceback.format_exception(None, e, e.__traceback__)
    boot_logs.extend(tb_text)
    print("".join(tb_text))
    
    # Signal error with LED
    blink_error(10, fast=True)
    
finally:
    # Always try to save boot logs
    try:
        save_boot_log()
    except Exception:
        pass
    
    # Ensure we end with clean memory
    gc.collect()
