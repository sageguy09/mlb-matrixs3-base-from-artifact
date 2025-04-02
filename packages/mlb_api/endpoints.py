# API endpoints
"""
MLB Stats API endpoints
======================
Defines the endpoints for the MLB Stats API.
"""

# MLB Stats API endpoints
ENDPOINTS = {
    "BASE_URL": "https://statsapi.mlb.com/api/v1",
    "SCHEDULE": "/schedule",
    "STANDINGS": "/standings",
    "GAME_DETAIL": "/game/{game_id}/feed/live",
    "TEAM": "/teams/{team_id}",
    "DIVISION": "/divisions/{division_id}",
    "PLAYER": "/people/{player_id}",
}
