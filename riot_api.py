import requests
import dotenv
import os


class Riot_Api:

    def __init__(self):
        dotenv.load_dotenv()

        self.api_key = os.getenv("RIOT_API_KEY")

        self.api_url_account = "https://europe.api.riotgames.com"
        self.api_url_mastery = "https://euw1.api.riotgames.com"

        self.load_champ_info()
        status, self.champ_to_id = self.get_champion_to_id()
        if status == False:
            self.champ_to_id = {}
        self.champ_to_id["62"] = "Wukong"

    
    def load_champ_info(self):
        """
        Load the champion info from the ddragon api.
        """
        req = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
        if req.status_code != 200:
            return False, {}
        latest = req.json()[0]
        ddragon = requests.get(
            f"https://ddragon.leagueoflegends.com/cdn/{latest}/data/en_US/champion.json"
        )
        if ddragon.status_code != 200:
            return
        self.champion_info = ddragon.json()["data"]
        

    def get_champion_to_id(self):
        """
        Create a dictionary that maps the champion name to the champion id.
        """
        if not self.champion_info:
            return False, {}
        champ_to_id = {}
        for key in self.champion_info.keys():
            champ_to_id[self.champion_info[key]["key"]] = self.champion_info[key]["id"]

        return True, champ_to_id


    def get_puuid(self, gamertag, tagLine):
        """
        Get the puuid of a gamertag.
        """
        endpoint = f"/riot/account/v1/accounts/by-riot-id/{gamertag}/{tagLine}"
        req = requests.get(self.api_url_account + endpoint + f"?api_key={self.api_key}")
        if req.status_code != 200:
            return False, ""
        return True, req.json()["puuid"]

    def get_champ_mastery(self, puuid):
        """
        Get the champion mastery of a player.
        """
        endpoint = f"/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
        req = requests.get(self.api_url_mastery + endpoint + f"?api_key={self.api_key}")
        if req.status_code != 200:
            return False, []

        return True, req.json()

    def get_champs(self, puuid):
        """
        Get the champion mastery of a player.

        """
        status, masteries = self.get_champ_mastery(puuid)
        if status == True:
            champ_ids = []
            for mastery in masteries:
                champ_ids.append(mastery["championId"])
            champs = [self.champ_to_id[str(champ_id)] for champ_id in champ_ids]
            champs = [champ.replace("'", "") for champ in champs]
            return True, champs
        return False, []


