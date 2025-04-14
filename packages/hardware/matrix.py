# hardware/matrix_s3.py - Hardware configuration for Matrix Portal S3

import board
import digitalio
import busio
import time
from adafruit_matrixportal.matrix import Matrix

class Matrix:
    """
    Hardware abstraction for the Adafruit Matrix Portal S3
    connected to a 32x64 RGB LED matrix panel.
    """
    
    def __init__(self, width=64, height=32, bit_depth=6):
        """
        Initialize the Matrix Portal S3 hardware.
        
        Args:
            width (int): Width of the matrix in pixels
            height (int): Height of the matrix in pixels
            bit_depth (int): Color bit depth (higher = more colors, more memory)
        """
        self.width = width
        self.height = height
        self.bit_depth = bit_depth
        
        # Initialize the matrix with specific S3 configuration
        self.matrix = Matrix(
            width=width,
            height=height,
            bit_depth=bit_depth,
            tile_rows=1,
        )
        
        # Get the display object
        self.display = self.matrix.display
        
        # Set up status LED
        self.status_led = digitalio.DigitalInOut(board.NEOPIXEL)
        self.status_led.direction = digitalio.Direction.OUTPUT
        self.status_led.value = False
    
    def set_brightness(self, brightness):
        """Set the brightness of the display (0-1.0)"""
        if 0 <= brightness <= 1.0:
            self.display.brightness = brightness
    
    def status_flash(self, count=1, on_time=0.1, off_time=0.1):
        """Flash the status LED a specified number of times"""
        for _ in range(count):
            self.status_led.value = True
            time.sleep(on_time)
            self.status_led.value = False
            time.sleep(off_time)
    
    def get_display_group(self):
        """Create and return a display group for rendering"""
        import displayio
        group = displayio.Group()
        self.display.root_group = group
        return group
    
    def show_test_pattern(self):
        """Show a simple test pattern to verify the matrix is working"""
        import displayio
        
        # Create a test bitmap with three color blocks
        bitmap = displayio.Bitmap(self.width, self.height, 3)
        palette = displayio.Palette(3)
        palette[0] = 0xFF0000  # Red
        palette[1] = 0x00FF00  # Green
        palette[2] = 0x0000FF  # Blue
        
        # Fill the bitmap with color blocks
        for x in range(self.width):
            for y in range(self.height):
                if x < self.width // 3:
                    bitmap[x, y] = 0
                elif x < 2 * (self.width // 3):
                    bitmap[x, y] = 1
                else:
                    bitmap[x, y] = 2
        
        # Create a TileGrid using the bitmap and palette
        tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
        
        # Create a Group and add the TileGrid
        group = displayio.Group()
        group.append(tile_grid)
        
        # Show the Group
        self.display.root_group = group
        
        return group