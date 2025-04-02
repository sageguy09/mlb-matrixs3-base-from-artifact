# Screen implementations
"""
Screen classes for MLB Scoreboard
===============================
Defines screen layouts and behaviors for the application.
"""

import time
import gc
import displayio
import terminalio
from adafruit_display_text import label
from packages.utils.logger import Logger
from packages.ui.colors import get_team_color, get_game_state_color, UI_COLORS, GAME_STATE_COLORS

class BaseScreen:
    """Base class for all screens."""
    
    def __init__(self, display, debug=False):
        """Initialize the screen.
        
        Args:
            display: Display instance
            debug: Enable debug logging
        """
        self.display = display
        self.debug = debug
        self.log = Logger(self.__class__.__name__, debug=debug)
        
        # Create a displayio group
        self.group = displayio.Group()
        
        # Initialize the screen
        self._init_screen()
        
        self.log.debug("Screen initialized")
    
    def _init_screen(self):
        """Initialize screen elements (to be overridden by subclasses)."""
        pass
    
    def update(self, *args, **kwargs):
        """Update screen content (to be overridden by subclasses)."""
        pass
    
    def update_animations(self):
        """Update any animations on the screen (to be overridden by subclasses)."""
        pass


class SplashScreen(BaseScreen):
    """Splash screen shown at startup."""
    
    def _init_screen(self):
        """Initialize splash screen elements."""
        # Add a title
        title = label.Label(
            terminalio.FONT,
            text="MLB Scoreboard",
            color=0xFFFFFF,
            scale=1
        )
        title.x = (self.display.width // 2) - (title.width // 2)
        title.y = self.display.height // 3
        self.group.append(title)
        
        # Add a subtitle
        subtitle = label.Label(
            terminalio.FONT,
            text="Loading...",
            color=0xAAAAAA,
            scale=1
        )
        subtitle.x = (self.display.width // 2) - (subtitle.width // 2)
        subtitle.y = (self.display.height * 2) // 3
        self.group.append(subtitle)


class GameScreen(BaseScreen):
    """Game information screen."""
    
    def _init_screen(self):
        """Initialize game screen elements."""
        # Add a title
        self.title = label.Label(
            terminalio.FONT,
            text="Game",
            color=0xFFFFFF,
            scale=1
        )
        self.title.x = 2
        self.title.y = 8
        self.group.append(self.title)
        
        # Add team labels
        self.away_team = label.Label(
            terminalio.FONT,
            text="AWAY",
            color=0xFFFFFF,
            scale=1
        )
        self.away_team.x = 2
        self.away_team.y = 20
        self.group.append(self.away_team)
        
        self.home_team = label.Label(
            terminalio.FONT,
            text="HOME",
            color=0xFFFFFF,
            scale=1
        )
        self.home_team.x = 2
        self.home_team.y = 30
        self.group.append(self.home_team)
    
    def update(self, games, favorite_game=None):
        """Update game information.
        
        Args:
            games: List of games
            favorite_game: Favorite team's game
        """
        if favorite_game:
            # Update with favorite game
            self.title.text = f"{favorite_game['status']}"
            self.away_team.text = f"{favorite_game['away_team']}: {favorite_game.get('away_score', 0)}"
            self.home_team.text = f"{favorite_game['home_team']}: {favorite_game.get('home_score', 0)}"
        elif games and len(games) > 0:
            # Show first game if no favorite
            game = games[0]
            self.title.text = f"{game['status']}"
            self.away_team.text = f"{game['away_team']}: {game.get('away_score', 0)}"
            self.home_team.text = f"{game['home_team']}: {game.get('home_score', 0)}"
        else:
            # No games
            self.title.text = "No games today"
            self.away_team.text = ""
            self.home_team.text = ""


class StandingsScreen(BaseScreen):
    """Team standings screen."""
    
    def _init_screen(self):
        """Initialize standings screen elements."""
        self.title = label.Label(
            terminalio.FONT,
            text="Standings",
            color=0xFFFFFF,
            scale=1
        )
        self.title.x = 2
        self.title.y = 8
        self.group.append(self.title)
        
        self.standings_text = label.Label(
            terminalio.FONT,
            text="Loading...",
            color=0xFFFFFF,
            scale=1
        )
        self.standings_text.x = 2
        self.standings_text.y = 20
        self.group.append(self.standings_text)
    
    def update(self, standings):
        """Update standings information.
        
        Args:
            standings: Standings data
        """
        if standings and len(standings) > 0:
            # Show division leader
            division = standings[0]
            self.title.text = f"{division['division_name']}"
            
            # Create standings text for top 3 teams
            standings_str = ""
            for i, team in enumerate(division['teams'][:3]):
                standings_str += f"{i+1}. {team['team_abbrev']} {team['w']}-{team['l']}\n"
            
            self.standings_text.text = standings_str
        else:
            self.title.text = "Standings"
            self.standings_text.text = "No data"


class ScheduleScreen(BaseScreen):
    """Team schedule screen."""
    
    def __init__(self, display, favorite_team="NYY", debug=False):
        """Initialize schedule screen.
        
        Args:
            display: Display instance
            favorite_team: Favorite team abbreviation
            debug: Enable debug logging
        """
        self.favorite_team = favorite_team
        super().__init__(display, debug)
    
    def _init_screen(self):
        """Initialize schedule screen elements."""
        self.title = label.Label(
            terminalio.FONT,
            text=f"{self.favorite_team} Schedule",
            color=0xFFFFFF,
            scale=1
        )
        self.title.x = 2
        self.title.y = 8
        self.group.append(self.title)
        
        self.schedule_text = label.Label(
            terminalio.FONT,
            text="Loading...",
            color=0xFFFFFF,
            scale=1
        )
        self.schedule_text.x = 2
        self.schedule_text.y = 20
        self.group.append(self.schedule_text)
    
    def update(self, schedule):
        """Update schedule information.
        
        Args:
            schedule: Schedule data
        """
        if schedule and len(schedule) > 0:
            schedule_str = ""
            for i, game in enumerate(schedule[:3]):  # Show next 3 games
                opponent = game['opponent']
                date = game['date']
                schedule_str += f"{date}: vs {opponent}\n"
            
            self.schedule_text.text = schedule_str
        else:
            self.schedule_text.text = "No upcoming games"


class ErrorScreen(BaseScreen):
    """Error message screen."""
    
    def _init_screen(self):
        """Initialize error screen elements."""
        self.title = label.Label(
            terminalio.FONT,
            text="Error",
            color=0xFF0000,
            scale=1
        )
        self.title.x = 2
        self.title.y = 8
        self.group.append(self.title)
        
        self.message = label.Label(
            terminalio.FONT,
            text="",
            color=0xFFFFFF,
            scale=1
        )
        self.message.x = 2
        self.message.y = 20
        self.group.append(self.message)
    
    def update(self, title="Error", message="An error occurred"):
        """Update error message.
        
        Args:
            title: Error title
            message: Error message
        """
        self.title.text = title
        
        # Truncate message if too long
        if len(message) > 100:
            message = message[:97] + "..."
        
        # Format multiline messages
        if "\n" in message:
            lines = message.split("\n")
            # Take just first two lines
            if len(lines) > 2:
                message = lines[0] + "\n" + lines[1]
        
        self.message.text = message
