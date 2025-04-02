# Simple test script to verify settings and debug configuration

import supervisor
import time
import sys
import gc

print("\n===== DEBUG TEST =====")
print(f"CircuitPython: {sys.implementation.version[0]}.{sys.implementation.version[1]}.{sys.implementation.version[2]}")

try:
    import toml
    with open("/settings.toml", "r") as f:
        settings = toml.load(f)
    print("Settings loaded successfully:")
    for section in settings:
        print(f"  [{section}]")
        for key, value in settings[section].items():
            print(f"    {key} = {value}")
except Exception as e:
    print(f"Error loading settings: {e}")

print("\nMemory usage:")
gc.collect()
print(f"Free: {gc.mem_free()} bytes")
print(f"Used: {gc.mem_alloc()} bytes")
