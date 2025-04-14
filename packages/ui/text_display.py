# utils/text_display.py - Text display utilities for Matrix Portal S3

import time
import displayio
import terminalio
from adafruit_display_text.bitmap_label import Label
from adafruit_display_text.scrolling_label import ScrollingLabel

class TextDisplay:
    """
    Text display utilities for Matrix Portal S3.
    Manages text rendering and animation on the display.
    """
    
    def __init__(self, display_group, width=64, height=32, font=None):
        """
        Initialize the text display utilities.
        
        Args:
            display_group: The displayio.Group to add text elements to
            width: Display width in pixels
            height: Display height in pixels
            font: Font to use (defaults to built-in terminal font)
        """
        self.display_group = display_group
        self.width = width
        self.height = height
        self.font = font or terminalio.FONT
        self.text_elements = {}
    
    def add_text(self, text, name, color=0xFFFFFF, x=0, y=None, background_color=None, scrolling=False, scroll_delay=0.03):
        """
        Add a text element to the display.
        
        Args:
            text: The text string to display
            name: A unique name for this text element
            color: Text color as 24-bit RGB hex
            x: X position (pixels from left)
            y: Y position (pixels from top, default to centered)
            background_color: Optional background color
            scrolling: Whether the text should scroll horizontally
            scroll_delay: Delay between scroll steps (seconds)
        
        Returns:
            The added text element object
        """
        # Position text in the middle of the display if Y not specified
        if y is None:
            y = self.height // 2
        
        # Create the appropriate label type based on scrolling flag
        if scrolling:
            text_element = ScrollingLabel(
                self.font,
                text=text,
                color=color,
                background_color=background_color,
                x=x,
                y=y,
                max_width=self.width - x,
                scroll_delay=scroll_delay,
            )
        else:
            text_element = Label(
                self.font,
                text=text,
                color=color,
                background_color=background_color,
                x=x,
                y=y,
            )
        
        # Add the text element to the display group
        self.display_group.append(text_element)
        
        # Store a reference by name for later updates
        self.text_elements[name] = text_element
        
        return text_element
    
    def update_text(self, name, new_text):
        """
        Update the text content of a named text element.
        
        Args:
            name: The name of the text element to update
            new_text: The new text content
        
        Returns:
            True if successful, False if element not found
        """
        if name in self.text_elements:
            self.text_elements[name].text = new_text
            return True
        return False
    
    def remove_text(self, name):
        """
        Remove a text element from the display.
        
        Args:
            name: The name of the text element to remove
        
        Returns:
            True if successful, False if element not found
        """
        if name in self.text_elements:
            self.display_group.remove(self.text_elements[name])
            del self.text_elements[name]
            return True
        return False
    
    def scroll_all(self):
        """
        Update all scrolling text elements to perform one scroll step.
        """
        for element in self.text_elements.values():
            if isinstance(element, ScrollingLabel):
                element.update()
    
    def preload_font(self, name, characters):
        """
        Preload font characters to improve rendering performance.
        
        Args:
            name: Name of the text element that uses this font
            characters: String or bytes of characters to preload
        """
        if name in self.text_elements:
            element = self.text_elements[name]
            element.text = "".join(chr(c) if isinstance(c, int) else c for c in characters)
            element.text = ""  # Clear after preloading
    
    def create_text_transform(self, prefix="", suffix="", formatter=None):
        """
        Create a text transformation function for formatted display.
        
        Args:
            prefix: String to add before the value
            suffix: String to add after the value
            formatter: Optional function to format the value
        
        Returns:
            A transform function to pass to add_text
        """
        def transform(value):
            if formatter:
                value = formatter(value)
            return f"{prefix}{value}{suffix}"
        
        return transform