# MLB Stats API client
"""
MLB Stats API Client for CircuitPython
======================================
Handles all interactions with the MLB Stats API.
"""

import json
import time
import traceback
from packages.utils.logger import Logger
from packages.mlb_api.endpoints import ENDPOINTS

class StatsAPIClient:
    """MLB Stats API client for fetching baseball data."""
    
    def __init__(self, network, debug=False):
        """Initialize the MLB Stats API client.
        
        Args:
            network: Network instance for making HTTP requests
            debug: Enable debug logging
        """
        self.network = network
        self.log = Logger("StatsAPI", debug=debug)
        self.debug = debug
        self.cache = {}
        self.cache_expiry = {}
        
        # Clear any existing cache on initialization
        self.clear_cache()
        
        # Team ID mapping
        self.team_ids = {
            # AL East
            "BAL": 110, "BOS": 111, "NYY": 147, "TB": 139, "TOR": 141,
            # AL Central
            "CWS": 145, "CLE": 114, "DET": 116, "KC": 118, "MIN": 142,
            # AL West
            "HOU": 117, "LAA": 108, "OAK": 133, "SEA": 136, "TEX": 140,
            # NL East
            "ATL": 144, "MIA": 146, "NYM": 121, "PHI": 143, "WSH": 120,
            # NL Central
            "CHC": 112, "CIN": 113, "MIL": 158, "PIT": 134, "STL": 138,
            # NL West
            "ARI": 109, "COL": 115, "LAD": 119, "SD": 135, "SF": 137
        }
        
        # Reverse mapping of team IDs to abbreviations
        self.team_abbrev = {v: k for k, v in self.team_ids.items()}
    
    def clear_cache(self):
        """Clear the API response cache."""
        self.cache = {}
        self.cache_expiry = {}
        self.log.debug("Cache cleared")
    
    def _get_team_id(self, team_abbr):
        """Convert team abbreviation to MLB Stats API team ID."""
        return self.team_ids.get(team_abbr.upper())
    
    def _get_team_abbr(self, team_id):
        """Convert MLB Stats API team ID to team abbreviation."""
        return self.team_abbrev.get(team_id)
    
    def _make_request(self, endpoint, params=None, force_refresh=False):
        """Make an HTTP request to the MLB Stats API.
        
        Args:
            endpoint: The API endpoint (from endpoints.py)
            params: Dictionary of query parameters
            force_refresh: Skip cache and force a new request
            
        Returns:
            Parsed JSON response or None on error
        """
        # Construct the URL
        url = ENDPOINTS["BASE_URL"] + endpoint
        
        # Add parameters to the URL
        if params:
            url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
        
        # Check cache first if not forcing refresh
        cache_key = url
        if not force_refresh and cache_key in self.cache:
            if time.monotonic() < self.cache_expiry.get(cache_key, 0):
                self.log.debug(f"Using cached response for {url}")
                return self.cache.get(cache_key)
        
        try:
            self.log.info(f"Requesting: {url}")
            
            # Make the request
            response = self.network.fetch(url)
            
            # Parse the JSON response
            data = json.loads(response)
            
            # Cache the response (expire after 5 minutes)
            self.cache[cache_key] = data
            self.cache_expiry[cache_key] = time.monotonic() + 300  # 5 minutes
            
            return data
            
        except Exception as e:
            self.log.error(f"Request failed: {e}")
            if self.debug:
                self.log.error(traceback.format_exc())
            return None
    
    def get_games(self, date):
        """Get all MLB games for a specific date.
        
        Args:
            date: Date string in format YYYY-MM-DD
            
        Returns:
            List of game dictionaries
        """
        params = {
            "sportId": 1,
            "date": date,
            "hydrate": "team,linescore,broadcasts(all),game(content(summary)),probablePitcher,flags,seriesStatus"
        }
        
        response = self._make_request(ENDPOINTS["SCHEDULE"], params)
        
        if not response or "dates" not in response:
            self.log.warning(f"No games data available for {date}")
            return []
        
        games = []
        
        for date_data in response["dates"]:
            for game_data in date_data.get("games", []):
                game = self._parse_game_data(game_data)
                if game:
                    games.append(game)
        
        return games
    
    def _parse_game_data(self, game_data):
        """Parse game data from the API response.
        
        Args:
            game_data: Game data dictionary from API
            
        Returns:
            Parsed game dictionary
        """
        try:
            game_id = game_data.get("gamePk")
            
            # Get basic game info
            game = {
                "game_id": game_id,
                "date": game_data.get("officialDate", ""),
                "status": game_data.get("status", {}).get("abstractGameState", ""),
                "detailed_status": game_data.get("status", {}).get("detailedState", ""),
                "start_time": game_data.get("gameDate", ""),
                "home_team": game_data.get("teams", {}).get("home", {}).get("team", {}).get("abbreviation", ""),
                "away_team": game_data.get("teams", {}).get("away", {}).get("team", {}).get("abbreviation", ""),
                "home_team_id": game_data.get("teams", {}).get("home", {}).get("team", {}).get("id", 0),
                "away_team_id": game_data.get("teams", {}).get("away", {}).get("team", {}).get("id", 0),
                "home_score": game_data.get("teams", {}).get("home", {}).get("score", 0),
                "away_score": game_data.get("teams", {}).get("away", {}).get("score", 0),
                "inning": 0,
                "inning_state": "",
                "is_top": False,
                "outs": 0,
                "balls": 0,
                "strikes": 0,
                "on_first": False,
                "on_second": False,
                "on_third": False,
                "last_play": "",
                "series_summary": "",
                "home_pitcher": "",
                "away_pitcher": "",
            }
            
            # Fill in team abbreviations if not present
            if not game["home_team"] and game["home_team_id"]:
                game["home_team"] = self._get_team_abbr(game["home_team_id"])
            if not game["away_team"] and game["away_team_id"]:
                game["away_team"] = self._get_team_abbr(game["away_team_id"])
            
            # Add inning data if available
            linescore = game_data.get("linescore", {})
            game["inning"] = linescore.get("currentInning", 0)
            game["inning_state"] = linescore.get("inningState", "")
            game["is_top"] = game["inning_state"].lower() == "top"
            game["outs"] = linescore.get("outs", 0)
            
            # Add count data if available
            game["balls"] = linescore.get("balls", 0)
            game["strikes"] = linescore.get("strikes", 0)
            
            # Add baserunner data if available
            offense = linescore.get("offense", {})
            game["on_first"] = "first" in offense
            game["on_second"] = "second" in offense
            game["on_third"] = "third" in offense
            
            # Add series info if available
            series_status = game_data.get("seriesStatus", {})
            game["series_summary"] = series_status.get("description", "")
            
            # Add pitcher info if available
            pitchers = {}
            if "probablePitcher" in game_data.get("teams", {}).get("home", {}):
                home_pitcher = game_data["teams"]["home"]["probablePitcher"]
                pitchers["home"] = f"{home_pitcher.get('fullName', '')}"
            
            if "probablePitcher" in game_data.get("teams", {}).get("away", {}):
                away_pitcher = game_data["teams"]["away"]["probablePitcher"]
                pitchers["away"] = f"{away_pitcher.get('fullName', '')}"
            
            game["home_pitcher"] = pitchers.get("home", "")
            game["away_pitcher"] = pitchers.get("away", "")
            
            return game
            
        except Exception as e:
            self.log.error(f"Error parsing game data: {e}")
            if self.debug:
                self.log.error(traceback.format_exc())
            return None
    
    def get_team_game(self, team_abbr, date):
        """Get a specific team's game on a given date.
        
        Args:
            team_abbr: Team abbreviation (e.g., "NYY")
            date: Date string in format YYYY-MM-DD
            
        Returns:
            Game dictionary or None if no game
        """
        team_id = self._get_team_id(team_abbr)
        if not team_id:
            self.log.warning(f"Unknown team abbreviation: {team_abbr}")
            return None
        
        params = {
            "sportId": 1,
            "date": date,
            "teamId": team_id,
            "hydrate": "team,linescore,broadcasts(all),game(content(summary)),probablePitcher,flags,seriesStatus"
        }
        
        response = self._make_request(ENDPOINTS["SCHEDULE"], params)
        
        if not response or "dates" not in response:
            self.log.info(f"No game data available for {team_abbr} on {date}")
            return None
        
        for date_data in response["dates"]:
            for game_data in date_data.get("games", []):
                return self._parse_game_data(game_data)
        
        return None
    
    def get_standings(self):
        """Get current MLB standings.
        
        Returns:
            Dictionary of division standings
        """
        params = {
            "leagueId": "103,104",  # Both AL and NL
            "season": time.localtime()[0],  # Current year
            "standingsTypes": "regularSeason",
            "hydrate": "team,division,sport,league"
        }
        
        response = self._make_request(ENDPOINTS["STANDINGS"], params)
        
        if not response or "records" not in response:
            self.log.warning("No standings data available")
            return None
        
        standings = {}
        
        for record in response["records"]:
            division_name = record.get("division", {}).get("nameShort", "Unknown")
            team_records = []
            
            for team_record in record.get("teamRecords", []):
                team_data = {
                    "name": team_record.get("team", {}).get("abbreviation", ""),
                    "wins": team_record.get("wins", 0),
                    "losses": team_record.get("losses", 0),
                    "pct": team_record.get("winningPercentage", ""),
                    "gb": team_record.get("gamesBack", ""),
                    "streak": team_record.get("streak", {}).get("streakCode", ""),
                    "last_ten": f"{team_record.get('records', {}).get('splitRecords', [])[3].get('wins', 0)}-{team_record.get('records', {}).get('splitRecords', [])[3].get('losses', 0)}" if len(team_record.get('records', {}).get('splitRecords', [])) > 3 else "0-0",
                }
                
                if not team_data["name"] and "id" in team_record.get("team", {}):
                    team_data["name"] = self._get_team_abbr(team_record["team"]["id"])
                
                team_records.append(team_data)
            
            # Sort by wins
            team_records.sort(key=lambda x: x["wins"], reverse=True)
            standings[division_name] = team_records
        
        return standings
    
    def get_team_schedule(self, team_abbr, limit=5):
        """Get a team's upcoming schedule."""
        team_id = self._get_team_id(team_abbr)
        if not team_id:
            self.log.warning(f"Unknown team abbreviation: {team_abbr}")
            return None
        
        # Get current date in YYYY-MM-DD format using the safer method
        current_date = self.get_current_date_string()
        
        params = {
            "sportId": 1,
            "teamId": team_id,
            "startDate": current_date,
            "gameType": "R",  # Regular season
            "hydrate": "team,probablePitcher"
        }
        
        response = self._make_request(ENDPOINTS["SCHEDULE"], params)
        
        if not response or "dates" not in response:
            self.log.warning(f"No schedule data available for {team_abbr}")
            return None
        
        schedule = []
        count = 0
        
        for date_data in response["dates"]:
            for game_data in date_data.get("games", []):
                if count >= limit:
                    break
                    
                game = {
                    "date": game_data.get("officialDate", ""),
                    "home_team": game_data.get("teams", {}).get("home", {}).get("team", {}).get("abbreviation", ""),
                    "away_team": game_data.get("teams", {}).get("away", {}).get("team", {}).get("abbreviation", ""),
                    "home_team_id": game_data.get("teams", {}).get("home", {}).get("team", {}).get("id", 0),
                    "away_team_id": game_data.get("teams", {}).get("away", {}).get("team", {}).get("id", 0),
                    "status": game_data.get("status", {}).get("detailedState", ""),
                    "time": game_data.get("gameDate", ""),
                    "home_pitcher": "",
                    "away_pitcher": "",
                }
                
                # Fill in team abbreviations if not present
                if not game["home_team"] and game["home_team_id"]:
                    game["home_team"] = self._get_team_abbr(game["home_team_id"])
                if not game["away_team"] and game["away_team_id"]:
                    game["away_team"] = self._get_team_abbr(game["away_team_id"])
                
                # Add pitcher info if available
                if "probablePitcher" in game_data.get("teams", {}).get("home", {}):
                    home_pitcher = game_data["teams"]["home"]["probablePitcher"]
                    game["home_pitcher"] = home_pitcher.get("fullName", "")
                
                if "probablePitcher" in game_data.get("teams", {}).get("away", {}):
                    away_pitcher = game_data["teams"]["away"]["probablePitcher"]
                    game["away_pitcher"] = away_pitcher.get("fullName", "")
                
                schedule.append(game)
                count += 1
                
                if count >= limit:
                    break
            
            if count >= limit:
                break
        
        return schedule
    
    def get_game_detail(self, game_id):
        """Get detailed information for a specific game.
        
        Args:
            game_id: MLB game ID
            
        Returns:
            Detailed game dictionary
        """
        endpoint = ENDPOINTS["GAME_DETAIL"].replace("{game_id}", str(game_id))
        
        response = self._make_request(endpoint)
        
        if not response or "liveData" not in response:
            self.log.warning(f"No detailed game data available for game ID {game_id}")
            return None
        
        try:
            live_data = response["liveData"]
            game_data = response["gameData"]
            
            # Extract the detailed game information we need
            detail = {
                "game_id": game_id,
                "status": game_data.get("status", {}).get("abstractGameState", ""),
                "detailed_status": game_data.get("status", {}).get("detailedState", ""),
                "home_team": game_data.get("teams", {}).get("home", {}).get("abbreviation", ""),
                "away_team": game_data.get("teams", {}).get("away", {}).get("abbreviation", ""),
                "home_team_id": game_data.get("teams", {}).get("home", {}).get("id", 0),
                "away_team_id": game_data.get("teams", {}).get("away", {}).get("id", 0),
                "home_score": live_data.get("linescore", {}).get("teams", {}).get("home", {}).get("runs", 0),
                "away_score": live_data.get("linescore", {}).get("teams", {}).get("away", {}).get("runs", 0),
                "inning": live_data.get("linescore", {}).get("currentInning", 0),
                "inning_state": live_data.get("linescore", {}).get("inningState", ""),
                "is_top": live_data.get("linescore", {}).get("inningState", "").lower() == "top",
                "outs": live_data.get("linescore", {}).get("outs", 0),
                "balls": live_data.get("linescore", {}).get("balls", 0),
                "strikes": live_data.get("linescore", {}).get("strikes", 0),
                "last_play": "",
                "on_first": False,
                "on_second": False,
                "on_third": False,
                "home_pitcher": "",
                "away_pitcher": "",
                "batter": ""
            }
            
            # Fill in team abbreviations if not present
            if not detail["home_team"] and detail["home_team_id"]:
                detail["home_team"] = self._get_team_abbr(detail["home_team_id"])
            if not detail["away_team"] and detail["away_team_id"]:
                detail["away_team"] = self._get_team_abbr(detail["away_team_id"])
            
            # Add baserunner info
            offense = live_data.get("linescore", {}).get("offense", {})
            detail["on_first"] = "first" in offense
            detail["on_second"] = "second" in offense
            detail["on_third"] = "third" in offense
            
            # Add current players info when available
            if "plays" in live_data and "currentPlay" in live_data["plays"]:
                current_play = live_data["plays"]["currentPlay"]
                
                # Get last play description
                if "playEvents" in current_play and len(current_play["playEvents"]) > 0:
                    last_event = current_play["playEvents"][-1]
                    detail["last_play"] = last_event.get("details", {}).get("description", "")
                
                # Get current pitcher and batter
                if "matchup" in current_play:
                    matchup = current_play["matchup"]
                    if "pitcher" in matchup:
                        pitcher_name = matchup["pitcher"].get("fullName", "")
                        if detail["is_top"]:
                            detail["home_pitcher"] = pitcher_name
                        else:
                            detail["away_pitcher"] = pitcher_name
                    
                    if "batter" in matchup:
                        detail["batter"] = matchup["batter"].get("fullName", "")
            
            return detail
            
        except Exception as e:
            self.log.error(f"Error parsing game detail: {e}")
            if self.debug:
                self.log.error(traceback.format_exc())
            return None
            
    def get_current_date_string(self):
        """Get current date string in YYYY-MM-DD format even if time_util fails"""
        try:
            # Try to use a provided time_util if it exists
            if hasattr(self, 'time_util') and self.time_util is not None:
                return self.time_util.get_current_date()
            else:
                # Fallback to using raw time functions
                year, month, day = time.localtime()[:3]
                return f"{year}-{month:02d}-{day:02d}"
        except Exception as e:
            self.log.error(f"Error getting date: {e}")
            # Last resort fallback
            return time.strftime("%Y-%m-%d")
