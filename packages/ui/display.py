# Display initialization (formerly matrix.py)
"""
Matrix display manager for MLB Scoreboard
=======================================
Handles matrix display and screen management.
"""

import time
import board
import busio
import gc
import displayio
import terminalio
from adafruit_display_text import label
from packages.utils.logger import Logger

class Matrix:
    """RGB Matrix wrapper with initialization and configuration."""
    
    def __init__(self, width=64, height=32, bit_depth=6, serpentine=True, tile_rows=1):
        """Initialize RGB Matrix.
        
        Args:
            width: Matrix width in pixels
            height: Matrix height in pixels
            bit_depth: Color bit depth
            serpentine: Whether the pixels are in serpentine arrangement
            tile_rows: Number of rows in a tiled configuration
        """
        self.width = width
        self.height = height
        self.bit_depth = bit_depth
        self.serpentine = serpentine
        self.tile_rows = tile_rows
        
    def begin(self):
        """Initialize the matrix display hardware.
        
        Returns:
            The initialized display object
        """
        # This is the method that should be called instead of init_display
        # Implement actual hardware initialization here
        # For now, return self as a placeholder
        return self


class DisplayManager:
    """Manages display screens and transitions."""
    
    def __init__(self, matrix, root_group, rotation=0, debug=False):
        """Initialize display manager.
        
        Args:
            matrix: Matrix instance
            root_group: Root DisplayIO group
            rotation: Display rotation (0, 90, 180, or 270 degrees)
            debug: Enable debug logging
        """
        self.matrix = matrix
        # Fix: Call begin() instead of init_display() which doesn't exist
        self.display = matrix.begin()
        self.root_group = root_group
        self.debug = debug
        self.log = Logger("Display", debug=debug)
        
        # Set up display
        self.display.rotation = rotation
        self.width = self.display.width
        self.height = self.display.height
        
        # Set display parameters
        self.display.auto_refresh = True
        
        # Update: Use root_group instead of show()
        self.display.root_group = self.root_group
        
        # Current screen
        self.current_screen = None
        
        self.log.info(f"Display initialized ({self.width}x{self.height})")
    
    def show(self, screen, transition=None):
        """Show a screen on the display.
        
        Args:
            screen: Screen to show
            transition: Optional transition effect
        """
        # Remove current screen from root group if exists
        while len(self.root_group) > 0:
            self.root_group.pop()
        
        try:
            # Add the new screen's group to the root group
            self.root_group.append(screen.group)
            self.current_screen = screen
            self.log.debug(f"Showing screen: {screen.__class__.__name__}")
            
            # Perform garbage collection to free memory
            gc.collect()
            
        except Exception as e:
            self.log.error(f"Error showing screen: {e}")
    
    def create_text_label(self, text, x, y, scale=1, color=0xFFFFFF, background=None, 
                         font=terminalio.FONT, line_spacing=1.25, padding=0):
        """Create a text label.
        
        Args:
            text: Label text
            x: X position
            y: Y position
            scale: Text scale factor
            color: Text color (default: white)
            background: Background color (default: transparent)
            font: Font to use
            line_spacing: Line spacing factor
            padding: Text padding
            
        Returns:
            Label object
        """
        return label.Label(
            font=font,
            text=text,
            x=x,
            y=y,
            color=color,
            background_color=background,
            scale=scale,
            line_spacing=line_spacing,
            padding_top=padding,
            padding_bottom=padding,
            padding_left=padding,
            padding_right=padding
        )
    
    def create_color_bitmap(self, width, height, color=0):
        """Create a solid color bitmap.
        
        Args:
            width: Bitmap width
            height: Bitmap height
            color: Bitmap color (default: black)
            
        Returns:
            Bitmap and TileGrid objects
        """
        # Create a bitmap
        bitmap = displayio.Bitmap(width, height, 1)
        
        # Fill with color
        bitmap.fill(0)
        
        # Create a palette with the color
        palette = displayio.Palette(1)
        palette[0] = color
        
        # Create a TileGrid
        tilegrid = displayio.TileGrid(bitmap, pixel_shader=palette)
        
        return bitmap, tilegrid
        
    def create_rect(self, x, y, width, height, color=0xFFFFFF, outline=None, stroke=1):
        """Create a rectangle.
        
        Args:
            x: X position
            y: Y position
            width: Rectangle width
            height: Rectangle height
            color: Rectangle color
            outline: Outline color (default: no outline)
            stroke: Outline stroke width
            
        Returns:
            Rectangle group
        """
        rect_group = displayio.Group()
        
        if outline is not None:
            # Create outline
            outline_bitmap, outline_grid = self.create_color_bitmap(width, height, outline)
            outline_grid.x = x
            outline_grid.y = y
            rect_group.append(outline_grid)
            
            # Create inner rectangle
            inner_bitmap, inner_grid = self.create_color_bitmap(
                width - stroke * 2, 
                height - stroke * 2, 
                color
            )
            inner_grid.x = x + stroke
            inner_grid.y = y + stroke
            rect_group.append(inner_grid)
        else:
            # Create single rectangle
            rect_bitmap, rect_grid = self.create_color_bitmap(width, height, color)
            rect_grid.x = x
            rect_grid.y = y
            rect_group.append(rect_grid)
        
        return rect_group

class Display:
    def __init__(self, width=64, height=32, chain_length=1, parallel=1):
        """Initialize the display with given dimensions."""
        self.width = width
        self.height = height
        self.log = Logger("Display", debug=False)
        
        # Initialize the matrix
        from packages.hardware.matrix import Matrix
        try:
            self.matrix = Matrix(
                width=width,
                height=height,
                chain_length=chain_length,
                parallel=parallel
            )
            
            # Initialize the matrix hardware
            self.matrix.setup()
            
            # Set initial brightness
            self.brightness = 100
            self.matrix.brightness(self.brightness)
            
            # Create an offscreen buffer for drawing
            self.canvas = self.matrix.create_canvas()
            
            self.log.info(f"Display initialized ({width}x{height})")
        except Exception as e:
            self.log.error(f"Error initializing display: {str(e)}")
            raise
        
    def show(self, screen):
        """Show the given screen on the display."""
        try:
            if hasattr(screen, 'group'):
                # If the screen has a displayio group, show it
                if self.matrix and self.matrix.display:
                    # Use root_group property instead of show() method
                    self.matrix.display.root_group = screen.group
            else:
                self.log.error("Screen has no 'group' attribute")
        except Exception as e:
            self.log.error(f"Error showing screen: {str(e)}")
    
    def refresh(self):
        """Refresh the display."""
        # Most displays with auto_refresh=True don't need explicit refreshing
        # This method is here for compatibility
        pass
