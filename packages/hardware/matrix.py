"""Matrix hardware interface module."""

import board
import displayio
from adafruit_matrixportal.matrix import Matrix as AdafruitMatrix

class Matrix:
    """Class to interface with the RGB LED matrix hardware."""
    
    def __init__(self, width=64, height=32, chain_length=1, parallel=1):
        """Initialize the Matrix object.
        
        Args:
            width: Width of the matrix in pixels
            height: Height of the matrix in pixels
            chain_length: Number of matrices chained together
            parallel: Number of parallel chains
        """
        self.width = width
        self.height = height
        self.chain_length = chain_length
        self.parallel = parallel
        self.matrix = None
        self.display = None
    
    def setup(self):
        """Set up the matrix hardware."""
        # Create the matrix object - removing 'tile' parameter which is causing the error
        self.matrix = AdafruitMatrix(
            width=self.width, 
            height=self.height,
            bit_depth=6,
            serpentine=True
        )
        
        # Get the framebuffer display
        self.display = self.matrix.display
        
        # Set basic display parameters
        self.display.auto_refresh = True
        
        return self
    
    def brightness(self, value):
        """Set the brightness of the matrix.
        
        Args:
            value: Brightness value (0-100)
        """
        if self.display:
            # Convert 0-100 to 0.0-1.0
            brightness_float = max(0.0, min(1.0, value / 100.0))
            self.display.brightness = brightness_float
    
    def create_canvas(self):
        """Create and return a canvas for drawing."""
        if self.display:
            # Create a root displayio group to use as our "canvas"
            canvas = displayio.Group()
            # Use root_group instead of show() which has been removed
            self.display.root_group = canvas
            return canvas
        raise RuntimeError("Matrix not initialized. Call setup() first.")
