import requests
import dotenv
import os

dotenv.load_dotenv()

api_key = os.getenv("RIOT_API_KEY")

api_url_account = "https://europe.api.riotgames.com"
api_url_mastery = "https://euw1.api.riotgames.com"


def get_champion_to_id():
    req = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
    if req.status_code != 200:
        return False, {}
    latest = req.json()[0]
    ddragon = requests.get(f"https://ddragon.leagueoflegends.com/cdn/{latest}/data/en_US/champion.json")
    if ddragon.status_code != 200:
        return False, {}
    champion_dict = ddragon.json()["data"]
    champ_to_id = {}
    for key in champion_dict.keys():
        champ_to_id[champion_dict[key]["key"]] = champion_dict[key]["id"]
    
    return True, champ_to_id

def get_account_info(gamertag):
    req = requests.get("http://localhost:5000/")
    
    
def get_puuid(gamertag, tagLine):
    """
    Get the puuid of a gamertag.
    """
    endpoint = f"/riot/account/v1/accounts/by-riot-id/{gamertag}/{tagLine}"
    req = requests.get(api_url_account + endpoint + f"?api_key={api_key}")
    if req.status_code != 200:
        return False, ""
    return True, req.json()["puuid"]

def get_champ_mastery(puuid):
    """
    Get the champion mastery of a player.
    """
    endpoint = f"/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
    req = requests.get(api_url_mastery + endpoint + f"?api_key={api_key}")
    if req.status_code != 200:
        return False, []
    return True, req.json()

def get_owned_champ_ids(puuid):
    """
    Get the champion mastery of a player.
    
    """
    status, masteries = get_champ_mastery(puuid)
    if status == True:
        champ_ids = []
        for mastery in masteries:
            champ_ids.append(mastery["championId"])
        return True, champ_ids
    return False, []


status, champs = get_champion_to_id() #get champions ids 
status, puuid = get_puuid("Skutlis", "EUW") #get puuid
print(puuid)
if status == True:
    status, champ_ids = get_owned_champ_ids(puuid) #get owned champions ids
    champs = [champs[str(champ_id)] for champ_id in champ_ids] #get owned champions names


    print(champs)

    