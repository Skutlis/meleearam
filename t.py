from db.data_handler import dataHandler
import pandas as pd

from riot_api import Riot_Api 



ra = Riot_Api()
ra.get_champion_to_id()

# Get the tag for each champion
champ_info = ra.champion_info
all_tags = []
champ_tag = {}
for champ in champ_info:
    tags = champ_info[champ]["tags"]
    champ_tag[champ] = tags
    for tag in tags:
        if tag not in all_tags:
            all_tags.append(tag)
    
print(all_tags)


dh = dataHandler()

# 
melee = pd.read_csv("db\\melee_champs.csv")
melee_list = melee["Champion"].tolist()

database_data_list = []

print(champ_tag.keys())
for champ in champ_tag.keys():
    champion_data_dict = {}

    attack = "ranged"
    if champ in melee_list:
        attack = "melee"

    name = champ.replace("'", " ")

    champion_data_dict["name"] = name
    champion_data_dict["attack"] = attack
    champion_data_dict["tag"] = ",".join(champ_tag[champ])
    champion_data_dict["is_available"] = True
    database_data_list.append(champion_data_dict)

print(database_data_list)


