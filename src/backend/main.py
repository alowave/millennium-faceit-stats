import Millennium, PluginUtils  # type: ignore
import requests
import json

# API Headers for FaceIt requests (Public Key)
HEADERS = {
    "Accept": "application/json",
    "Authorization": "Bearer 8f9985f3-3cf5-43de-970c-dfe244a57fb0"
}

# Logger setup
LOGGER = PluginUtils.Logger("__faceit_stats__")

class FaceItUser:
    def __init__(self, id: str, nickname: str, country: str, avatar: str, cover_image_url: str, faceit_elo: int, skill_level: int):
        self.id = id
        self.nickname = nickname
        self.country = country
        self.avatar = avatar
        self.cover_image_url = cover_image_url
        self.faceit_elo = faceit_elo
        self.skill_level = skill_level
        self.stats = self.get_user_stats()

    class UserStats:
        def __init__(self, matches: int, avg_hs: float, avg_kd: float, adr: float, winrate: float):
            self.matches = matches
            self.avg_hs = avg_hs
            self.avg_kd = avg_kd
            self.adr = adr
            self.winrate = winrate

        def __repr__(self):
            return (
                f"UserStats(matches={self.matches}, avg_hs={self.avg_hs}, "
                f"avg_kd={self.avg_kd}, adr={self.adr}, winrate={self.winrate})"
            )

    @staticmethod
    def get_user_by_steamId(steamId: str) -> "FaceItUser | None":
        """Fetches FaceIt user details by Steam ID."""
        url = f"https://open.faceit.com/data/v4/players?game=cs2&game_player_id={steamId}"
        
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching FaceIt user data: {e}")
            return None
        
        if response.status_code == 404:
            return None
        elif response.status_code != 200:
            raise Exception(f"Error fetching data: {response.status_code}")
        
        data = response.json()
        
        return FaceItUser(
            id=data.get("player_id", ""),
            nickname=data.get("nickname", "Unknown"),
            country=data.get("country", "Unknown"),
            avatar=data.get("avatar", ""),
            cover_image_url=data.get("cover_image", ""),
            faceit_elo=data.get("games", {}).get("cs2", {}).get("faceit_elo", 0),
            skill_level=data.get("games", {}).get("cs2", {}).get("skill_level", 0)
        )

    def get_user_stats(self):
        """Fetches user stats from FaceIt API."""
        stats_url = f"https://open.faceit.com/data/v4/players/{self.id}/stats/cs2"
        
        try:
            response = requests.get(stats_url, headers=HEADERS)
            response.raise_for_status()
            r = response.json()
            lifetime_stats = r.get("lifetime", {})
            
            return self.UserStats(
                matches=int(lifetime_stats.get("Matches", 0)),
                avg_hs=float(lifetime_stats.get("Average Headshots %", 0.0)),
                avg_kd=float(lifetime_stats.get("Average K/D Ratio", 0.0)),
                adr=float(lifetime_stats.get("ADR", 0.0)),
                winrate=float(lifetime_stats.get("Win Rate %", 0.0))
            )
        except requests.RequestException as e:
            print(f"Failed to fetch FaceIt stats: {e}")
        
        return None

    def __repr__(self):
        return (
            f"FaceItUser(id={self.id}, nickname={self.nickname}, country={self.country}, "
            f"faceit_elo={self.faceit_elo}, skill_level={self.skill_level})"
        )

# Function to get user data by Steam ID
def get_user_by_steamId(steamId):
    user = FaceItUser.get_user_by_steamId(steamId)
    if user:
        user.stats = user.stats.__dict__ if user.stats else None
        return json.dumps(user.__dict__)
    return None

class Plugin:
    def _front_end_loaded(self):
        """Logs when the front end has loaded."""
        LOGGER.log("The front end has loaded!")

    def _load(self):     
        """Initializes the plugin."""
        LOGGER.log(f"Bootstrapping FaceItStats, Millennium {Millennium.version()}")
        Millennium.add_browser_css("faceit_stats.css")
        Millennium.ready()

    def _unload(self):
        """Logs when the plugin is unloading."""
        LOGGER.log("Unloading")
