# boot.py - Initial setup code for Matrix Portal S3

import board
import digitalio
import storage
import supervisor
import os
import time

# === CONFIGURATION ===
DEBUG_MODE = True
ENABLE_USB_DRIVE = True

# Disable auto-reload to prevent reloading during file setup
supervisor.runtime.autoreload = False

# Status LED setup (NeoPixel onboard)
status_led = digitalio.DigitalInOut(board.NEOPIXEL)
status_led.direction = digitalio.Direction.OUTPUT

def blink_led(count, on_time=0.1, off_time=0.1):
    for _ in range(count):
        status_led.value = True
        time.sleep(on_time)
        status_led.value = False
        time.sleep(off_time)

# Blink twice to show boot started
blink_led(2)

# CRITICAL FIX: Always check safe mode before operations
if supervisor.runtime.safe_mode:
    print("⚠️ Safe mode detected, skipping remount and file setup.")
    blink_led(10, 0.05, 0.05)  # Fast blink to indicate safe mode
else:
    # === Remount the filesystem as writable - CRITICAL for image saving
    try:
        storage.remount("/", readonly=False)
        print("✅ Filesystem remounted writable")
        # Blink once to confirm remount success
        blink_led(1, 0.2, 0.1)
    except Exception as e:
        print(f"⚠️ Could not remount filesystem: {e}")
        # Blink error pattern
        blink_led(3, 0.1, 0.3)

    # === Ensure essential directories exist (including /images for logo storage)
    required_dirs = ["lib", "sd", "fonts", "images", "data", "sounds"]
    for d in required_dirs:
        try:
            os.makedirs(d, exist_ok=True)
            print(f"✓ Directory /{d} ready")
        except Exception as e:
            print(f"⚠️ Couldn't create /{d}: {e}")
    
    # Verify images directory specifically - critical for our application
    if os.path.exists("/images"):
        print("✅ Confirmed /images directory exists")
    else:
        print("❌ Critical error: /images directory missing")

    # === Ensure settings.toml exists
    if not os.path.exists("settings.toml"):
        try:
            with open("settings.toml", "w") as f:
                f.write("CIRCUITPY_WIFI_SSID=\"YourSSID\"\n")
                f.write("CIRCUITPY_WIFI_PASSWORD=\"YourPassword\"\n")
                f.write("CIRCUITPY_USB_WRITE_PROTECT=false\n")
            print("✅ settings.toml created")
        except Exception as e:
            print(f"⚠️ Couldn't create settings.toml: {e}")

    # Final blink to show success
    blink_led(1, 0.5, 0)
    print("✅ Boot complete, ready for code.py")

