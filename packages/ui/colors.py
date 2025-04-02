# Team & UI colors
"""
MLB Team Colors for the MLB Scoreboard
====================================
Defines the primary and secondary colors for all MLB teams.
"""

# RGB color definitions for all MLB teams
TEAM_COLORS = {
    # AL East
    "BAL": {
        "primary": 0xDF4601,    # Orange
        "secondary": 0x000000,  # Black
        "text": 0xFFFFFF        # White
    },
    "BOS": {
        "primary": 0xBD3039,    # Red
        "secondary": 0x0C2340,  # Navy Blue
        "text": 0xFFFFFF        # White
    },
    "NYY": {
        "primary": 0x003087,    # Navy Blue
        "secondary": 0xC4CED4,  # Grey
        "text": 0xFFFFFF        # White
    },
    "TB": {
        "primary": 0x092C5C,    # Navy Blue
        "secondary": 0x8FBCE6,  # Light Blue
        "text": 0xFFFFFF        # White
    },
    "TOR": {
        "primary": 0x134A8E,    # Blue
        "secondary": 0xE8291C,  # Red
        "text": 0xFFFFFF        # White
    },
    
    # AL Central
    "CWS": {
        "primary": 0x000000,    # Black
        "secondary": 0xC4CED4,  # Silver
        "text": 0xFFFFFF        # White
    },
    "CLE": {
        "primary": 0xE31937,    # Red
        "secondary": 0x00295D,  # Navy Blue
        "text": 0xFFFFFF        # White
    },
    "DET": {
        "primary": 0x0C2340,    # Navy Blue
        "secondary": 0xFA4616,  # Orange
        "text": 0xFFFFFF        # White
    },
    "KC": {
        "primary": 0x004687,    # Blue
        "secondary": 0xBD9B60,  # Gold
        "text": 0xFFFFFF        # White
    },
    "MIN": {
        "primary": 0x002B5C,    # Navy Blue
        "secondary": 0xD31145,  # Red
        "text": 0xFFFFFF        # White
    },
    
    # AL West
    "HOU": {
        "primary": 0xEB6E1F,    # Orange
        "secondary": 0x002D62,  # Navy Blue
        "text": 0xFFFFFF        # White
    },
    "LAA": {
        "primary": 0xBA0021,    # Red
        "secondary": 0x003263,  # Navy Blue
        "text": 0xFFFFFF        # White
    },
    "OAK": {
        "primary": 0x003831,    # Green
        "secondary": 0xEFB21E,  # Gold
        "text": 0xFFFFFF        # White
    },
    "SEA": {
        "primary": 0x0C2C56,    # Navy Blue
        "secondary": 0x005C5C,  # Northwest Green
        "text": 0xFFFFFF        # White
    },
    "TEX": {
        "primary": 0xC0111F,    # Red
        "secondary": 0x003278,  # Blue
        "text": 0xFFFFFF        # White
    },
    
    # NL East
    "ATL": {
        "primary": 0xCE1141,    # Red
        "secondary": 0x13274F,  # Navy Blue
        "text": 0xFFFFFF        # White
    },
    "MIA": {
        "primary": 0x00A3E0,    # Blue
        "secondary": 0xEF3340,  # Red
        "text": 0xFFFFFF        # White
    },
    "NYM": {
        "primary": 0xFF5910,    # Orange
        "secondary": 0x002D72,  # Blue
        "text": 0xFFFFFF        # White
    },
    "PHI": {
        "primary": 0xE81828,    # Red
        "secondary": 0x002D72,  # Blue
        "text": 0xFFFFFF        # White
    },
    "WSH": {
        "primary": 0xAB0003,    # Red
        "secondary": 0x11225B,  # Navy Blue
        "text": 0xFFFFFF        # White
    },
    
    # NL Central
    "CHC": {
        "primary": 0x0E3386,    # Blue
        "secondary": 0xCC3433,  # Red
        "text": 0xFFFFFF        # White
    },
    "CIN": {
        "primary": 0xC6011F,    # Red
        "secondary": 0x000000,  # Black
        "text": 0xFFFFFF        # White
    },
    "MIL": {
        "primary": 0x0A2351,    # Navy Blue
        "secondary": 0xB6922E,  # Gold
        "text": 0xFFFFFF        # White
    },
    "PIT": {
        "primary": 0x000000,    # Black
        "secondary": 0xFDB827,  # Gold
        "text": 0xFFFFFF        # White
    },
    "STL": {
        "primary": 0xC41E3A,    # Red
        "secondary": 0x0C2340,  # Navy Blue
        "text": 0xFFFFFF        # White
    },
    
    # NL West
    "ARI": {
        "primary": 0xA71930,    # Red
        "secondary": 0x000000,  # Black
        "text": 0xFFFFFF        # White
    },
    "COL": {
        "primary": 0x333366,    # Purple
        "secondary": 0xC4CED4,  # Silver
        "text": 0xFFFFFF        # White
    },
    "LAD": {
        "primary": 0x005A9C,    # Blue
        "secondary": 0xA5ACAF,  # Silver
        "text": 0xFFFFFF        # White
    },
    "SD": {
        "primary": 0x2F241D,    # Brown
        "secondary": 0xFFC425,  # Gold
        "text": 0xFFFFFF        # White
    },
    "SF": {
        "primary": 0xFD5A1E,    # Orange
        "secondary": 0x000000,  # Black
        "text": 0xFFFFFF        # White
    }
}

# League colors
LEAGUE_COLORS = {
    "MLB": {
        "primary": 0x002D72,    # Blue
        "secondary": 0xE4002B,  # Red
        "text": 0xFFFFFF        # White
    },
    "AL": {
        "primary": 0xE4002B,    # Red
        "secondary": 0x002D72,  # Blue
        "text": 0xFFFFFF        # White
    },
    "NL": {
        "primary": 0x002D72,    # Blue
        "secondary": 0xE4002B,  # Red
        "text": 0xFFFFFF        # White
    }
}

# UI colors
UI_COLORS = {
    "background": 0x000000,     # Black
    "text": 0xFFFFFF,           # White
    "highlight": 0x00FF00,      # Green
    "warning": 0xFFFF00,        # Yellow
    "error": 0xFF0000,          # Red
    "info": 0x00FFFF,           # Cyan
    "border": 0x444444,         # Dark Gray
    "header": 0x222222,         # Very Dark Gray
    "footer": 0x222222,         # Very Dark Gray
    "button": 0x2222FF,         # Blue
    "button_text": 0xFFFFFF,    # White
    "inactive": 0x666666,       # Gray
    "active": 0x00FF00,         # Green
    "win": 0x00FF00,            # Green
    "loss": 0xFF0000,           # Red
    "tie": 0xFFFF00             # Yellow
}

# Game state colors
GAME_STATE_COLORS = {
    "scheduled": 0x2222FF,      # Blue
    "pre_game": 0x00FFFF,       # Cyan
    "in_progress": 0x00FF00,    # Green
    "delayed": 0xFFFF00,        # Yellow
    "postponed": 0xFF0000,      # Red
    "suspended": 0xFF00FF,      # Magenta
    "completed": 0x666666,      # Gray
    "final": 0x666666,          # Gray
    "game_over": 0x666666,      # Gray
    "cancelled": 0xFF0000       # Red
}

# Status indicator colors
STATUS_COLORS = {
    "startup": (0, 0, 128),      # Blue
    "connecting": (128, 128, 0), # Yellow
    "online": (0, 128, 0),       # Green
    "error": (128, 0, 0),        # Red
    "data_refresh": (0, 128, 128), # Cyan
    "data_error": (128, 64, 0),  # Orange
}

def get_team_color(team_abbr, type="primary"):
    """Get team color.
    
    Args:
        team_abbr: Team abbreviation (e.g., "NYY")
        type: Color type ("primary", "secondary", or "text")
        
    Returns:
        RGB color as hex integer
    """
    team = team_abbr.upper()
    if team in TEAM_COLORS:
        return TEAM_COLORS[team].get(type, TEAM_COLORS[team]["primary"])
    
    # Default to MLB colors if team not found
    return LEAGUE_COLORS["MLB"].get(type, LEAGUE_COLORS["MLB"]["primary"])

def get_game_state_color(state):
    """Get color for game state.
    
    Args:
        state: Game state string
        
    Returns:
        RGB color as hex integer
    """
    state_lower = state.lower().replace(" ", "_")
    
    # Map various states to our defined states
    if "progress" in state_lower or "live" in state_lower:
        state_key = "in_progress"
    elif "final" in state_lower or "over" in state_lower or "completed" in state_lower:
        state_key = "final"
    elif "delayed" in state_lower:
        state_key = "delayed"
    elif "postponed" in state_lower:
        state_key = "postponed"
    elif "suspended" in state_lower:
        state_key = "suspended"
    elif "cancelled" in state_lower:
        state_key = "cancelled"
    elif "pre" in state_lower or "warmup" in state_lower:
        state_key = "pre_game"
    else:
        state_key = "scheduled"
    
    return GAME_STATE_COLORS.get(state_key, UI_COLORS["text"])
