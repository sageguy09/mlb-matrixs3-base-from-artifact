"""
System sensor utilities for ESP32-S3 CircuitPython
Provides functions for reading system values like temperature, voltage, etc.
"""
import microcontroller
import gc
import os

def get_cpu_temperature():
    """
    Get the CPU temperature
    
    Returns:
        float: Temperature in Celsius or None if not supported
    """
    try:
        return microcontroller.cpu.temperature
    except (AttributeError, NotImplementedError):
        return None

def get_voltage():
    """
    Get the CPU voltage
    
    Returns:
        float: Voltage in volts or None if not supported
    """
    try:
        return microcontroller.cpu.voltage
    except (AttributeError, NotImplementedError):
        return None

def get_frequency():
    """
    Get the CPU frequency
    
    Returns:
        int: Frequency in Hz or None if not supported
    """
    try:
        return microcontroller.cpu.frequency
    except (AttributeError, NotImplementedError):
        return None

def get_memory_usage():
    """
    Get memory usage information
    
    Returns:
        dict: Memory usage information
    """
    gc.collect()
    
    try:
        mem_free = gc.mem_free()
        mem_alloc = gc.mem_alloc()
        
        return {
            "free": mem_free,
            "used": mem_alloc,
            "total": mem_free + mem_alloc,
            "percent_used": (mem_alloc / (mem_free + mem_alloc)) * 100
        }
    except:
        return {
            "free": 0,
            "used": 0,
            "total": 0,
            "percent_used": 0
        }

def get_storage_usage():
    """
    Get storage usage information
    
    Returns:
        dict: Storage usage information
    """
    try:
        fs_stat = os.statvfs("/")
        
        # Calculate storage information
        block_size = fs_stat[0]
        total_blocks = fs_stat[2]
        free_blocks = fs_stat[3]
        
        total_space = block_size * total_blocks
        free_space = block_size * free_blocks
        used_space = total_space - free_space
        
        return {
            "free": free_space,
            "used": used_space,
            "total": total_space,
            "percent_used": (used_space / total_space) * 100 if total_space > 0 else 0
        }
    except:
        return {
            "free": 0,
            "used": 0,
            "total": 0,
            "percent_used": 0
        }

def get_system_info():
    """
    Get comprehensive system information
    
    Returns:
        dict: System information including CPU, memory, and storage
    """
    return {
        "temperature": get_cpu_temperature(),
        "voltage": get_voltage(),
        "frequency": get_frequency(),
        "memory": get_memory_usage(),
        "storage": get_storage_usage(),
        "board_id": microcontroller.cpu.uid,
    }
