# boot.py - Initial setup code for Matrix Portal S3
# This file runs before main.py on startup

import board
import digitalio
import storage
import supervisor
import time
import microcontroller

# Constants
DEBUG_MODE = True  # Set to False for production
ENABLE_USB_DRIVE = True  # Set to False to disable USB drive access

# Setup status LED to indicate boot process
status_led = digitalio.DigitalInOut(board.NEOPIXEL)
status_led.direction = digitalio.Direction.OUTPUT

def blink_led(count, on_time=0.1, off_time=0.1):
    """Blink the onboard NeoPixel to indicate status"""
    for _ in range(count):
        status_led.value = True
        time.sleep(on_time)
        status_led.value = False
        time.sleep(off_time)

# Indicate boot start
blink_led(2)

# Check for safe mode
if supervisor.runtime.safe_mode:
    # Rapid blink to indicate safe mode
    blink_led(10, 0.05, 0.05)
    
    # Skip the rest of boot process in safe mode
    print("Boot in safe mode - skipping further initialization")
else:
    # Configure USB drive access
    if ENABLE_USB_DRIVE:
        # USB drive is enabled by default
        print("USB drive access enabled")
    else:
        # Disable USB drive write access to protect against corruption
        # when board loses power without clean shutdown
        storage.remount("/", readonly=True)
        print("USB drive access disabled for stability")
    
    # Set CPU frequency - higher for performance, lower for power savings
    # Options: 125000000 (125MHz), 62500000 (62.5MHz), 31250000 (31.25MHz)
    if DEBUG_MODE:
        # Full speed for debugging
        pass  # Default is already full speed
    else:
        # Lower speed for power savings in production
        pass  # Uncomment the next line to reduce CPU speed
        # microcontroller.cpu.frequency = 62500000

    # Configure other hardware as needed before main.py runs
    # ...

    # Indicate boot complete
    blink_led(1, 0.5, 0)
    print("Boot complete, transferring control to main.py")