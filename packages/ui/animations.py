"""
Animation effects for MLB Scoreboard
==================================
Defines animations for screen transitions and effects.
"""

import time
import displayio
from packages.utils.logger import Logger
from packages.ui.colors import UI_COLORS

class Animation:
    """Base class for all animations."""
    
    def __init__(self, display_manager, duration=0.5, debug=False):
        """Initialize animation.
        
        Args:
            display_manager: DisplayManager instance
            duration: Animation duration in seconds
            debug: Enable debug logging
        """
        self.display = display_manager
        self.duration = duration
        self.log = Logger("Animation", debug=debug)
        self.debug = debug
        
        # Animation properties
        self.width = self.display.width
        self.height = self.display.height
        self.frames = int(duration * 30)  # 30fps target
        self.current_frame = 0
        
        # Create animation group that will be shown during animation
        self.animation_group = displayio.Group()
    
    def start(self, from_screen, to_screen):
        """Start animation between screens.
        
        Args:
            from_screen: Source screen
            to_screen: Destination screen
            
        Returns:
            True if animation completed, False otherwise
        """
        # Reset animation
        self.current_frame = 0
        
        # Prepare animation
        self._prepare(from_screen, to_screen)
        
        # Show animation group
        self.display.display.show(self.animation_group)
        
        # Run animation frames
        for frame in range(self.frames):
            frame_start = time.monotonic()
            
            # Update animation frame
            self._update_frame(frame, from_screen, to_screen)
            self.current_frame = frame
            
            # Calculate time to wait for next frame
            frame_time = time.monotonic() - frame_start
            frame_delay = max(0, (1 / 30) - frame_time)
            
            # Wait for next frame
            time.sleep(frame_delay)
        
        # Animation complete
        return True
    
    def _prepare(self, from_screen, to_screen):
        """Prepare animation (to be implemented by subclasses).
        
        Args:
            from_screen: Source screen
            to_screen: Destination screen
        """
        raise NotImplementedError("Subclass must implement abstract method")
    
    def _update_frame(self, frame, from_screen, to_screen):
        """Update animation frame (to be implemented by subclasses).
        
        Args:
            frame: Current frame number
            from_screen: Source screen
            to_screen: Destination screen
        """
        raise NotImplementedError("Subclass must implement abstract method")


class CrossFadeAnimation(Animation):
    """Cross-fade between two screens."""
    
    def __init__(self, display_manager, duration=0.5, debug=False):
        """Initialize cross-fade animation.
        
        Args:
            display_manager: DisplayManager instance
            duration: Animation duration in seconds
            debug: Enable debug logging
        """
        super().__init__(display_manager, duration, debug)
        
        # Animation properties
        self.fade_bitmap = None
        self.fade_grid = None
    
    def _prepare(self, from_screen, to_screen):
        """Prepare cross-fade animation.
        
        Args:
            from_screen: Source screen
            to_screen: Destination screen
        """
        # Clear animation group
        while len(self.animation_group) > 0:
            self.animation_group.pop()
        
        # Add source screen to animation group
        self.animation_group.append(from_screen.group)
        
        # Add destination screen on top (will be revealed by fade)
        self.animation_group.append(to_screen.group)
        
        # Create fade overlay
        self.fade_bitmap = displayio.Bitmap(self.width, self.height, 1)
        self.fade_bitmap.fill(0)
        
        # Create palette for fade
        fade_palette = displayio.Palette(1)
        fade_palette[0] = 0x000000  # Black
        
        # Create TileGrid for fade
        self.fade_grid = displayio.TileGrid(
            self.fade_bitmap,
            pixel_shader=fade_palette
        )
        
        # Add fade overlay to animation group
        self.animation_group.append(self.fade_grid)
    
    def _update_frame(self, frame, from_screen, to_screen):
        """Update cross-fade animation frame.
        
        Args:
            frame: Current frame number
            from_screen: Source screen
            to_screen: Destination screen
        """
        # Calculate alpha (opacity) based on frame
        alpha = frame / self.frames
        
        # Set overlay opacity
        self.fade_grid.hidden = True if frame == self.frames - 1 else False
        
        # For a true cross-fade, we would adjust opacity of both screens
        # However, DisplayIO doesn't support alpha blending directly
        # Instead, we're using a visibility toggle at a point
        if frame >= self.frames // 2:
            # After halfway point, hide the from_screen and show to_screen
            to_screen.group.hidden = False
            from_screen.group.hidden = True


class SlideAnimation(Animation):
    """Slide transition between screens."""
    
    def __init__(self, display_manager, direction="left", duration=0.5, debug=False):
        """Initialize slide animation.
        
        Args:
            display_manager: DisplayManager instance
            direction: Slide direction ("left", "right", "up", "down")
            duration: Animation duration in seconds
            debug: Enable debug logging
        """
        super().__init__(display_manager, duration, debug)
        
        # Animation properties
        self.direction = direction
    
    def _prepare(self, from_screen, to_screen):
        """Prepare slide animation.
        
        Args:
            from_screen: Source screen
            to_screen: Destination screen
        """
        # Clear animation group
        while len(self.animation_group) > 0:
            self.animation_group.pop()
        
        # Add both screens to animation group
        self.animation_group.append(from_screen.group)
        self.animation_group.append(to_screen.group)
        
        # Position the destination screen off-screen based on direction
        if self.direction == "left":
            # To screen starts at right edge
            to_screen.group.x = self.width
            to_screen.group.y = 0
        elif self.direction == "right":
            # To screen starts at left edge
            to_screen.group.x = -self.width
            to_screen.group.y = 0
        elif self.direction == "up":
            # To screen starts at bottom edge
            to_screen.group.x = 0
            to_screen.group.y = self.height
        elif self.direction == "down":
            # To screen starts at top edge
            to_screen.group.x = 0
            to_screen.group.y = -self.height
    
    def _update_frame(self, frame, from_screen, to_screen):
        """Update slide animation frame.
        
        Args:
            frame: Current frame number
            from_screen: Source screen
            to_screen: Destination screen
        """
        # Calculate progress (0.0 to 1.0)
        progress = frame / (self.frames - 1)
        
        # Update screen positions based on direction
        if self.direction == "left":
            # From screen moves left, to screen moves left from right edge
            from_screen.group.x = int(-self.width * progress)
            to_screen.group.x = int(self.width * (1 - progress))
        elif self.direction == "right":
            # From screen moves right, to screen moves right from left edge
            from_screen.group.x = int(self.width * progress)
            to_screen.group.x = int(-self.width * (1 - progress))
        elif self.direction == "up":
            # From screen moves up, to screen moves up from bottom edge
            from_screen.group.y = int(-self.height * progress)
            to_screen.group.y = int(self.height * (1 - progress))
        elif self.direction == "down":
            # From screen moves down, to screen moves down from top edge
            from_screen.group.y = int(self.height * progress)
            to_screen.group.y = int(-self.height * (1 - progress))
        
        # Reset positions at the end
        if frame == self.frames - 1:
            from_screen.group.x = 0
            from_screen.group.y = 0
            to_screen.group.x = 0
            to_screen.group.y = 0


class WipeAnimation(Animation):
    """Wipe transition between screens."""
    
    def __init__(self, display_manager, direction="left", duration=0.5, debug=False):
        """Initialize wipe animation.
        
        Args:
            display_manager: DisplayManager instance
            direction: Wipe direction ("left", "right", "up", "down")
            duration: Animation duration in seconds
            debug: Enable debug logging
        """
        super().__init__(display_manager, duration, debug)
        
        # Animation properties
        self.direction = direction
        self.wipe_bitmap = None
        self.wipe_palette = None
        self.wipe_grid = None
    
    def _prepare(self, from_screen, to_screen):
        """Prepare wipe animation.
        
        Args:
            from_screen: Source screen
            to_screen: Destination screen
        """
        # Clear animation group
        while len(self.animation_group) > 0:
            self.animation_group.pop()
        
        # Add both screens to animation group
        self.animation_group.append(from_screen.group)
        self.animation_group.append(to_screen.group)
        
        # Hide destination screen initially
        to_screen.group.hidden = True
        
        # Create wipe overlay
        if self.direction == "left" or self.direction == "right":
            # Horizontal wipe
            self.wipe_bitmap = displayio.Bitmap(self.width, self.height, 1)
        else:
            # Vertical wipe
            self.wipe_bitmap = displayio.Bitmap(self.width, self.height, 1)
        
        # Create palette for wipe
        self.wipe_palette = displayio.Palette(1)
        self.wipe_palette[0] = UI_COLORS["background"]
        
        # Create TileGrid for wipe
        self.wipe_grid = displayio.TileGrid(
            self.wipe_bitmap,
            pixel_shader=self.wipe_palette
        )
        
        # Fill wipe bitmap
        self.wipe_bitmap.fill(0)
        
        # Add wipe overlay to animation group
        self.animation_group.append(self.wipe_grid)
    
    def _update_frame(self, frame, from_screen, to_screen):
        """Update wipe animation frame.
        
        Args:
            frame: Current frame number
            from_screen: Source screen
            to_screen: Destination screen
        """
        # Calculate progress (0.0 to 1.0)
        progress = frame / (self.frames - 1)
        
        # At the middle of the animation, switch screens
        if frame == self.frames // 2:
            from_screen.group.hidden = True
            to_screen.group.hidden = False
        
        # Update wipe bitmap based on direction
        if self.direction == "left":
            # Wipe from left to right
            wipe_width = int(self.width * progress)
            for y in range(self.height):
                for x in range(wipe_width):
                    if x < self.width:
                        self.wipe_bitmap[x, y] = 0 if frame < self.frames // 2 else 1
        elif self.direction == "right":
            # Wipe from right to left
            wipe_width = int(self.width * progress)
            for y in range(self.height):
                for x in range(self.width - wipe_width, self.width):
                    if x >= 0:
                        self.wipe_bitmap[x, y] = 0 if frame < self.frames // 2 else 1
        elif self.direction == "up":
            # Wipe from top to bottom
            wipe_height = int(self.height * progress)
            for y in range(wipe_height):
                for x in range(self.width):
                    if y < self.height:
                        self.wipe_bitmap[x, y] = 0 if frame < self.frames // 2 else 1
        elif self.direction == "down":
            # Wipe from bottom to top
            wipe_height = int(self.height * progress)
            for y in range(self.height - wipe_height, self.height):
                for x in range(self.width):
                    if y >= 0:
                        self.wipe_bitmap[x, y] = 0 if frame < self.frames // 2 else 1
        
        # Make wipe invisible at the end
        if frame == self.frames - 1:
            self.wipe_grid.hidden = True


def create_animation(display_manager, type="slide", direction="left", duration=0.5, debug=False):
    """Create animation of specified type.
    
    Args:
        display_manager: DisplayManager instance
        type: Animation type ("slide", "wipe", "fade")
        direction: Animation direction ("left", "right", "up", "down")
        duration: Animation duration in seconds
        debug: Enable debug logging
        
    Returns:
        Animation instance
    """
    if type == "slide":
        return SlideAnimation(display_manager, direction, duration, debug)
    elif type == "wipe":
        return WipeAnimation(display_manager, direction, duration, debug)
    elif type == "fade":
        return CrossFadeAnimation(display_manager, duration, debug)
    else:
        # Default to slide animation
        return SlideAnimation(display_manager, direction, duration, debug)
