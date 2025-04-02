"""User interface package for MLB Scoreboard.

This package contains all the UI components, screens, and display handling code.
"""

# Import main classes that should be available directly from packages.ui
from .display import Display, DisplayManager, Matrix
from .screens import (
    BaseScreen,
    SplashScreen,
    GameScreen,
    StandingsScreen,
    ScheduleScreen,
    ErrorScreen
)

# Define what gets imported with wildcard imports
__all__ = [
    'Display',
    'DisplayManager',
    'Matrix',
    'BaseScreen',
    'SplashScreen',
    'GameScreen',
    'StandingsScreen',
    'ScheduleScreen',
    'ErrorScreen'
]
