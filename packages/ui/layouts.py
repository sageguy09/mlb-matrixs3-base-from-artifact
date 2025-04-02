# Screen layouts
"""
Screen layouts for MLB Scoreboard
==============================
Layout helpers for different display screens.
"""

import displayio
from packages.utils.logger import Logger
from packages.ui.colors import UI_COLORS, get_team_color

class Layout:
    """Base class for screen layouts."""
    
    def __init__(self, display_manager, debug=False):
        """Initialize layout.
        
        Args:
            display_manager: DisplayManager instance
            debug: Enable debug logging
        """
        self.display = display_manager
        self.log = Logger("Layout", debug=debug)
        self.debug = debug
        
        # Display dimensions
        self.width = self.display.width
        self.height = self.display.height
    
    def create_header(self, title, color=UI_COLORS["text"]):
        """Create a header bar with title.
        
        Args:
            title: Header title
            color: Header text color
            
        Returns:
            Group containing header elements
        """
        header_group = displayio.Group()
        
        # Header background
        header_rect = self.display.create_rect(
            x=0,
            y=0,
            width=self.width,
            height=10,
            color=UI_COLORS["header"]
        )
        header_group.append(header_rect)
        
        # Header title
        title_label = self.display.create_text_label(
            text=title,
            x=2,
            y=2,
            color=color
        )
        header_group.append(title_label)
        
        return header_group
    
    def create_footer(self, text, color=UI_COLORS["text"]):
        """Create a footer bar with text.
        
        Args:
            text: Footer text
            color: Footer text color
            
        Returns:
            Group containing footer elements
        """
        footer_group = displayio.Group()
        
        # Footer background
        footer_rect = self.display.create_rect(
            x=0,
            y=self.height - 8,
            width=self.width,
            height=8,
            color=UI_COLORS["footer"]
        )
        footer_group.append(footer_rect)
        
        # Footer text
        footer_label = self.display.create_text_label(
            text=text,
            x=2,
            y=self.height - 7,
            color=color
        )
        footer_group.append(footer_label)
        
        return footer_group


class ScoreboardLayout(Layout):
    """Layout for scoreboard screen."""
    
    def create_team_row(self, team_abbr, score, y_pos, is_batting=False):
        """Create a team score row.
        
        Args:
            team_abbr: Team abbreviation
            score: Team score
            y_pos: Y position
            is_batting: Whether team is currently batting
            
        Returns:
            Group containing team row elements
        """
        row_group = displayio.Group()
        
        # Team color
        team_color = get_team_color(team_abbr, "primary")
        
        # Team abbreviation background
        team_bg = self.display.create_rect(
            x=0,
            y=y_pos,
            width=25,
            height=9,
            color=team_color
        )
        row_group.append(team_bg)
        
        # Team abbreviation text
        team_label = self.display.create_text_label(
            text=team_abbr,
            x=2,
            y=y_pos + 1,
            color=UI_COLORS["text"]
        )
        row_group.append(team_label)
        
        # Score background
        score_bg = self.display.create_rect(
            x=25,
            y=y_pos,
            width=15,
            height=9,
            color=UI_COLORS["background"],
            outline=team_color,
            stroke=1
        )
        row_group.append(score_bg)
        
        # Score text
        score_label = self.display.create_text_label(
            text=str(score),
            x=32,
            y=y_pos + 1,
            color=team_color
        )
        score_label.anchor_point = (0.5, 0)
        score_label.anchored_position = (32, y_pos + 1)
        row_group.append(score_label)
        
        # Batting indicator
        if is_batting:
            batting_indicator = self.display.create_rect(
                x=42,
                y=y_pos + 3,
                width=3,
                height=3,
                color=UI_COLORS["active"]
            )
            row_group.append(batting_indicator)
        
        return row_group
    
    def create_inning_display(self, inning, is_top, outs):
        """Create inning and outs display.
        
        Args:
            inning: Current inning number
            is_top: Whether it's the top of the inning
            outs: Number of outs
            
        Returns:
            Group containing inning display elements
        """
        inning_group = displayio.Group()
        
        # Inning background
        inning_bg = self.display.create_rect(
            x=0,
            y=self.height - 16,
            width=self.width,
            height=8,
            color=UI_COLORS["background"],
            outline=UI_COLORS["border"],
            stroke=1
        )
        inning_group.append(inning_bg)
        
        # Inning text
        inning_state = "Top" if is_top else "Bot"
        inning_label = self.display.create_text_label(
            text=f"{inning_state} {inning}",
            x=2,
            y=self.height - 15,
            color=UI_COLORS["text"]
        )
        inning_group.append(inning_label)
        
        # Outs
        outs_text = "Out" if outs == 1 else "Outs"
        outs_label = self.display.create_text_label(
            text=f"{outs} {outs_text}",
            x=self.width - 2,
            y=self.height - 15,
            color=UI_COLORS["warning"] if outs >= 2 else UI_COLORS["text"]
        )
        outs_label.anchor_point = (1, 0)
        outs_label.anchored_position = (self.width - 2, self.height - 15)
        inning_group.append(outs_label)
        
        return inning_group
    
    def create_count_display(self, balls, strikes):
        """Create count display.
        
        Args:
            balls: Number of balls
            strikes: Number of strikes
            
        Returns:
            Group containing count display elements
        """
        count_group = displayio.Group()
        
        # Count background
        count_bg = self.display.create_rect(
            x=0,
            y=self.height - 8,
            width=self.width,
            height=8,
            color=UI_COLORS["background"],
            outline=UI_COLORS["border"],
            stroke=1
        )
        count_group.append(count_bg)
        
        # Count text
        count_label = self.display.create_text_label(
            text=f"Count: {balls}-{strikes}",
            x=2,
            y=self.height - 7,
            color=UI_COLORS["warning"] if strikes >= 2 else UI_COLORS["text"]
        )
        count_group.append(count_label)
        
        return count_group
    
    def create_diamond_display(self, on_first=False, on_second=False, on_third=False):
        """Create baseball diamond display.
        
        Args:
            on_first: Whether there's a runner on first
            on_second: Whether there's a runner on second
            on_third: Whether there's a runner on third
            
        Returns:
            Group containing diamond display elements
        """
        diamond_group = displayio.Group()
        diamond_group.x = self.width - 18
        diamond_group.y = 10
        
        # Create diamond outline
        diamond_outline = displayio.Group()
        
        # First to second line
        first_second = self.display.create_rect(
            x=3,
            y=3,
            width=8,
            height=1,
            color=UI_COLORS["border"]
        )
        diamond_outline.append(first_second)
        
        # Second to third line
        second_third = self.display.create_rect(
            x=3,
            y=3,
            width=1,
            height=8,
            color=UI_COLORS["border"]
        )
        diamond_outline.append(second_third)
        
        # Third to home line
        third_home = self.display.create_rect(
            x=0,
            y=10,
            width=8,
            height=1,
            color=UI_COLORS["border"]
        )
        diamond_outline.append(third_home)
        
        # Home to first line
        home_first = self.display.create_rect(
            x=7,
            y=3,
            width=1,
            height=8,
            color=UI_COLORS["border"]
        )
        diamond_outline.append(home_first)
        
        diamond_group.append(diamond_outline)
        
        # Add bases
        # First base
        first_base = self.display.create_rect(
            x=10,
            y=5,
            width=3,
            height=3,
            color=UI_COLORS["active"] if on_first else UI_COLORS["inactive"]
        )
        diamond_group.append(first_base)
        
        # Second base
        second_base = self.display.create_rect(
            x=5,
            y=0,
            width=3,
            height=3,
            color=UI_COLORS["active"] if on_second else UI_COLORS["inactive"]
        )
        diamond_group.append(second_base)
        
        # Third base
        third_base = self.display.create_rect(
            x=0,
            y=5,
            width=3,
            height=3,
            color=UI_COLORS["active"] if on_third else UI_COLORS["inactive"]
        )
        diamond_group.append(third_base)
        
        # Home plate
        home_plate = self.display.create_rect(
            x=5,
            y=10,
            width=3,
            height=3,
            color=UI_COLORS["text"]
        )
        diamond_group.append(home_plate)
        
        return diamond_group


class StandingsLayout(Layout):
    """Layout for standings screen."""
    
    def create_standings_header(self, division_name):
        """Create standings header with division name.
        
        Args:
            division_name: Division name
            
        Returns:
            Group containing standings header elements
        """
        header_group = displayio.Group()
        
        # Header background
        header_bg = self.display.create_rect(
            x=0,
            y=0,
            width=self.width,
            height=10,
            color=UI_COLORS["header"]
        )
        header_group.append(header_bg)
        
        # Division name
        division_label = self.display.create_text_label(
            text=division_name,
            x=2,
            y=2,
            color=UI_COLORS["text"]
        )
        header_group.append(division_label)
        
        # Column headers
        headers_group = displayio.Group()
        headers_group.y = 10
        
        # Team header
        team_header = self.display.create_text_label(
            text="Team",
            x=2,
            y=1,
            color=UI_COLORS["info"]
        )
        headers_group.append(team_header)
        
        # Record header
        record_header = self.display.create_text_label(
            text="W-L",
            x=30,
            y=1,
            color=UI_COLORS["info"]
        )
        headers_group.append(record_header)
        
        # GB header
        gb_header = self.display.create_text_label(
            text="GB",
            x=self.width - 2,
            y=1,
            color=UI_COLORS["info"]
        )
        gb_header.anchor_point = (1, 0)
        gb_header.anchored_position = (self.width - 2, 1)
        headers_group.append(gb_header)
        
        header_group.append(headers_group)
        
        return header_group
    
    def create_team_standing_row(self, team_abbr, wins, losses, gb, y_pos):
        """Create team standing row.
        
        Args:
            team_abbr: Team abbreviation
            wins: Team wins
            losses: Team losses
            gb: Games behind
            y_pos: Y position
            
        Returns:
            Group containing team standing row elements
        """
        row_group = displayio.Group()
        row_group.y = y_pos
        
        # Team name
        team_label = self.display.create_text_label(
            text=team_abbr,
            x=2,
            y=0,
            color=get_team_color(team_abbr, "primary")
        )
        row_group.append(team_label)
        
        # Record
        record_label = self.display.create_text_label(
            text=f"{wins}-{losses}",
            x=30,
            y=0,
            color=UI_COLORS["text"]
        )
        row_group.append(record_label)
        
        # Games behind
        gb_text = "--" if gb == "0.0" else gb
        gb_label = self.display.create_text_label(
            text=gb_text,
            x=self.width - 2,
            y=0,
            color=UI_COLORS["text"]
        )
        gb_label.anchor_point = (1, 0)
        gb_label.anchored_position = (self.width - 2, 0)
        row_group.append(gb_label)
        
        return row_group


class ScheduleLayout(Layout):
    """Layout for schedule screen."""
    
    def create_schedule_header(self, team_abbr):
        """Create schedule header with team name.
        
        Args:
            team_abbr: Team abbreviation
            
        Returns:
            Group containing schedule header elements
        """
        header_group = displayio.Group()
        
        # Header background
        header_bg = self.display.create_rect(
            x=0,
            y=0,
            width=self.width,
            height=10,
            color=get_team_color(team_abbr, "primary")
        )
        header_group.append(header_bg)
        
        # Team name
        team_label = self.display.create_text_label(
            text=f"{team_abbr} SCHEDULE",
            x=2,
            y=2,
            color=UI_COLORS["text"]
        )
        header_group.append(team_label)
        
        return header_group
    
    def create_game_row(self, date, opponent, home_away, time, y_pos):
        """Create game schedule row.
        
        Args:
            date: Game date (MM/DD)
            opponent: Opponent team abbreviation
            home_away: "vs" or "@"
            time: Game time
            y_pos: Y position
            
        Returns:
            Group containing game schedule row elements
        """
        row_group = displayio.Group()
        row_group.y = y_pos
        
        # Date/time background
        date_bg = self.display.create_rect(
            x=0,
            y=0,
            width=self.width,
            height=6,
            color=UI_COLORS["background"],
            outline=UI_COLORS["border"],
            stroke=1
        )
        row_group.append(date_bg)
        
        # Date
        date_label = self.display.create_text_label(
            text=date,
            x=2,
            y=1,
            color=UI_COLORS["text"]
        )
        row_group.append(date_label)
        
        # Time
        time_label = self.display.create_text_label(
            text=time,
            x=self.width - 2,
            y=1,
            color=UI_COLORS["info"]
        )
        time_label.anchor_point = (1, 0)
        time_label.anchored_position = (self.width - 2, 1)
        row_group.append(time_label)
        
        # Opponent
        opponent_text = f"{home_away} {opponent}"
        opponent_label = self.display.create_text_label(
            text=opponent_text,
            x=2,
            y=8,
            color=get_team_color(opponent, "primary")
        )
        row_group.append(opponent_label)
        
        return row_group
