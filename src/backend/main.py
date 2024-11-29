import Millennium, PluginUtils # type: ignore
import requests
import json

logger = PluginUtils.Logger("__faceit_stats__")

class FaceItUser:
    def __init__(self, id, nickname, country, avatar, cover_image_url, faceit_elo, skill_level):
        self.id = id
        self.nickname = nickname
        self.country = country
        self.avatar = avatar
        self.cover_image_url = cover_image_url
        self.faceit_elo = faceit_elo
        self.skill_level = skill_level
        self.stats = self.get_user_stats()

    class UserStats:
        def __init__(self, matches: int, avg_hs: float, avg_kd: float, avg_kr: float, winrate: float):
            self.matches = matches
            self.avg_hs = avg_hs
            self.avg_kd = avg_kd
            self.avg_kr = avg_kr
            self.winrate = winrate

        def __repr__(self):
            return (
                f"UserStats(matches={self.matches}, avg_hs={self.avg_hs}, "
                f"avg_kd={self.avg_kd}, avg_kr={self.avg_kr}, winrate={self.winrate})"
            )

    @staticmethod
    def get_user_by_steamId(steamId: int):
        search_url = f"https://www.faceit.com/api/search/v1?limit=3&query={steamId}"
        try:
            response = requests.get(search_url)
            response.raise_for_status()
            data = response.json()

            player_data = data.get("payload", {}).get("players", {}).get("results", [])
            if not player_data:
                print(f"No FaceIt user found for Steam ID {steamId}.")
                return None

            nickname = player_data[0]["nickname"]
            
            search_url = f"https://www.faceit.com/api/users/v1/nicknames/{nickname}"
            
            response = requests.get(search_url)
            response.raise_for_status()
            data = response.json()

            faceit_id = data["payload"]["id"]
            avatar = data["payload"].get('avatar', '')
            country = data["payload"]["country"]
            cover_image_url = data["payload"].get("cover_image_url", None)

            cs2_data = data["payload"]["games"].get("cs2", {})
            faceit_elo = cs2_data.get("faceit_elo")
            skill_level = cs2_data.get("skill_level")

            return FaceItUser(faceit_id, nickname, country, avatar, cover_image_url, faceit_elo, skill_level)
        
        except requests.RequestException as e:
            print(f"Failed to fetch FaceIt user data: {e}")
            return None

    def get_user_stats(self):
        stats_url = f"https://www.faceit.com/api/stats/v1/stats/users/{self.id}/games/cs2"
        try:
            response = requests.get(stats_url)
            response.raise_for_status()
            data = response.json()
            lifetime_stats = data.get("lifetime", {})
            matches = int(lifetime_stats.get("m1", 0))
            avg_hs = float(lifetime_stats.get("k8", 0.0))
            avg_kd = float(lifetime_stats.get("k5", 0.0))
            avg_kr = float(lifetime_stats.get("k9", 0.0))
            winrate = int(lifetime_stats.get("k6", 0))
            
            segments = data.get('segments', {})
            avg_kr = segments[0]['segments'][list(segments[0]['segments'].keys())[0]].get('k9', 0.0)

            return self.UserStats(matches, avg_hs, avg_kd, avg_kr, winrate)
        except requests.RequestException as e:
            print(f"Failed to fetch FaceIt stats: {e}")
            
        return None

    def __repr__(self):
        return f"FaceItUser(id={self.id}, nickname={self.nickname}, country={self.country}, faceit_elo={self.faceit_elo}, skill_level={self.skill_level})"

def get_user_by_steamId(steamId):
    user = FaceItUser.get_user_by_steamId(steamId) 
    if user:
        if user.stats:
            user.stats = user.stats.__dict__
        else:
            user.stats = None
        return json.dumps(user.__dict__)
    return None

class Plugin:

    def _front_end_loaded(self):
        logger.log("The front end has loaded!")

    def _load(self):     
        logger.log(f"bootstrapping FaceItStats, millennium {Millennium.version()}")
        Millennium.add_browser_css("faceit_stats.css")
        Millennium.ready()

    def _unload(self):
        logger.log("unloading")
