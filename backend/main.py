import Millennium, PluginUtils  # type: ignore
import requests
import json
import shutil
import os

# API Headers for FaceIt requests (Public Key)
HEADERS = {
    "Accept": "application/json",
    "Authorization": "Bearer 8f9985f3-3cf5-43de-970c-dfe244a57fb0"
}

HEADERS_LEETIFY= {
    "Accept": "application/json",
}

# Logger setup
LOGGER = PluginUtils.Logger()

DEBUG = False

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

def get_aim_rating(steamId):
    """Fetches aim rating from Leetify API."""
    url = f"https://api.cs-prod.leetify.com/api/profile/id/{steamId}"
        
    try:
        response = requests.get(url, headers=HEADERS_LEETIFY)
        response.raise_for_status()
        data = response.json()
        aim_rating = data.get("recentGameRatings", {}).get("aim", 0.0)
        return round(aim_rating)
    except requests.RequestException as e:
        print(f"Failed to fetch aim rating: {e}")
        return None

def GetPluginDir():
    return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..'))

class Plugin:
    def copy_frontend_files(self):
        css_source = os.path.join(GetPluginDir(), 'static', 'faceit_stats.css')
        static_source = os.path.join(GetPluginDir(), 'static')
        png_source = [f for f in os.listdir(static_source) if f.endswith('.png')]
        
        steamui_dest = os.path.join(Millennium.steam_path(), 'steamui')
        faceit_finder_dest = os.path.join(steamui_dest, 'FaceItFinder')
        os.makedirs(faceit_finder_dest, exist_ok=True)
        
        try:
            if os.path.exists(css_source):
                shutil.copy(css_source, steamui_dest)
                print(f'Copied {css_source} to {steamui_dest}')
            else:
                print(f'File not found: {css_source}')
            
            for png_file in png_source:
                png_file_path = os.path.join(static_source, png_file)
                if os.path.exists(png_file_path):
                    shutil.copy(png_file_path, faceit_finder_dest)
                    print(f'Copied {png_file_path} to {faceit_finder_dest}')
                else:
                    print(f'File not found: {png_file_path}')
                    
        except Exception as e:
            print(f'Error: {e}')
    
    def _front_end_loaded(self):
        LOGGER.log("The front end has loaded!")

    def _load(self):     
        """Initializes the plugin."""
        LOGGER.log(f"Bootstrapping FaceItStats, Millennium {Millennium.version()}")
        
        self.copy_frontend_files()
        
        Millennium.add_browser_css("faceit_stats.css")
        Millennium.ready()

    def _unload(self):
        LOGGER.log("Unloading")
