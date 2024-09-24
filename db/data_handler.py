from db.DBManager import dbManager
import json
import pandas as pd

import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(parent_dir)
        
from riot_api import Riot_Api


class dataHandler:

    def __init__(self):
        self.riot_api = Riot_Api() #Init the riot api
        # Load configs from file
        with open("db\\table_config.json", "r") as json_file:
            configs = json.load(json_file)

        # Set the table names and columns
        self.melee_champs_table_name = configs["melee_champs_table_name"]
        self.melee_champs_columns = configs["melee_champs_columns"]
        self.player_table_name = configs["player_table_name"]
        self.player_columns = configs["player_columns"]
        with open("db\\MA_dbconfig.json", "r") as json_file:
            db_conf = json.load(json_file)

        # Initialize the database manager
        self.db = dbManager(db_conf)
        self.db.setUpLogger()

        tables = self.db.list_tables()
        # Set up tables if they don't exist
        if not self.melee_champs_table_name in tables:
            self.db.create_table(
                self.melee_champs_table_name,  # table name
                ["name"],  # primary key
                self.melee_champs_columns,  # columns
            )
            self.fill_champions_table()

        if not self.player_table_name in tables:
            self.db.create_table(
                self.player_table_name,  # table name
                ["disc_id"],  # primary key
                self.player_columns,  # columns
            )

        

    def fill_champions_table(self):

        # Get the tag for each champion
        champ_info = self.riot_api.champion_info
        champ_tag = {}
        for champ in champ_info.keys():
            tags = champ_info[champ]["tags"]
            champ_tag[champ_info[champ]["name"]] = tags
        
        print(champ_tag)
        # Get the melee champions
        melee = pd.read_csv("db\\melee_champs.csv")
        melee_list = melee["Champion"].tolist()
        melee_list = [champ.lower() for champ in melee_list]
        

        database_data_list = []
        
        for champ in champ_tag.keys():
            
            champion_data_dict = {}

            #Asssign attack type
            attack = "ranged"
            if champ.lower() in melee_list or champ.lower().split(" ")[0] in melee_list:
                attack = "melee"

     

            champion_data_dict["name"] = self.format_text_field(champ.replace("'", " "))
            champion_data_dict["attack"] = self.format_text_field(attack)
            champion_data_dict["tag"] = self.format_text_field(" ".join(champ_tag[champ]))
            champion_data_dict["is_available"] = "True"
            database_data_list.append(champion_data_dict)

        for champ_data in database_data_list:
            self.add_champ(champ_data)
        

    def format_text_field(self, text):
        """
        Format a text field for the database.
        """
        return "'" + text + "'"

    def list_champion_database(self):
        """
        Get all champions from the database.
        """
        return self.db.list_rows(self.melee_champs_table_name)

    def get_all_available_champions(self):
        """
        Get all champions that are not banned
        """
        available_champs = []
        all_champs = self.list_champion_database()
        for champ_data in all_champs:
            if champ_data[2]:
                available_champs.append(champ_data[0])

        return available_champs

    def get_banned_champs(self):
        """
        Get all champions that are banned.
        """
        banned_champs = []
        all_champs = self.list_champion_database()
        for champ_info in all_champs:
            if not champ_info[1]:
                banned_champs.append(champ_info[0])

        return banned_champs

    def find_champ(self, champ):
        """
        Find a champion in the database.
        """
        champ_l = champ.lower()
        champs = [row[0] for row in self.db.list_rows(self.melee_champs_table_name)]
        for c in champs:
            if champ_l in c.split(" ")[0].lower():
                return c

            elif champ_l in c.lower():
                return c

        return champ

    def add_champ(self, champ_info_dict):
        """
        Add a champion to the database.
        """
        self.db.add_row(
            self.melee_champs_table_name, champ_info_dict
        )

    def ban_champ(self, champ):
        """
        Ban a champion from the database.
        """
        champ = self.find_champ(champ)
        champ = self.format_text_field(champ)
        return self.db.update_row(
            self.melee_champs_table_name, {"name": champ}, {"is_available": False}
        )

    def unban_champ(self, champ):
        """
        Unban a champion from the database.
        """
        champ = self.find_champ(champ)
        champ = self.format_text_field(champ)
        return self.db.update_row(
            self.melee_champs_table_name, {"name": champ}, {"is_available": True}
        )

    def set_player_info(self, disc_id, puuid, gamertag):
        """
        Set the gamertag of a player in the database.
        """
        # disc_id = self.format_text_field(disc_id)
        puuid = self.format_text_field(puuid)
        gamertag = self.format_text_field(gamertag)

        success = False
        if self.db.exists(self.player_table_name, {"disc_id": disc_id}):
            success = self.db.update_row(
                self.player_table_name,
                {"disc_id": disc_id},
                {"disc_id": disc_id, "puuid": puuid, "gamertag": gamertag},
            )
        else:
            success = self.db.add_row(
                self.player_table_name,
                {"disc_id": disc_id, "puuid": puuid, "gamertag": gamertag},
            )

        return success

    def get_gamertag(self, disc_id):
        """
        Get the gamertag of a player from the database.
        """
        # disc_id = self.format_text_field(disc_id)
        return self.db.get_rows_by_criteria(self.player_table_name, {"disc_id": disc_id})[2]

    def get_puuid(self, disc_id):
        """
        Get the puuid of a player from the database.
        """
        # disc_id = self.format_text_field(disc_id)
        return self.db.get_rows_by_criteria(self.player_table_name, {"disc_id": disc_id})[1]

    def player_is_registered(self, disc_id):
        """
        Check if a player is registered in the database.
        """
        # disc_id = self.format_text_field(disc_id)
        return self.db.exists(self.player_table_name, {"disc_id": disc_id})

    def get_player_info(self, gamertag):
        """
        Get the puuid of a gamertag.
        """
        gamertag = self.format_text_field(gamertag)
        info = self.db.get_rows_by_criteria(self.player_table_name, {"gamertag": gamertag})
        gamertag = info[2]
        puuid = info[1]
        return gamertag, puuid

    def update_gamertag(self, disc_id, gamertag):
        """
        Update the gamertag of a player in the database.
        """
        # disc_id = self.format_text_field(disc_id)
        gamertag = self.format_text_field(gamertag)
        if self.db.exists(self.player_table_name, {"disc_id": disc_id}):
            self.db.update_row(
                self.player_table_name, {"disc_id": disc_id}, {"gamertag": gamertag}
            )
            return True
        return False

    def filter_out_banned_champs(self, champs):
        """
        Filter out banned champions from a list of champions.
        """
        available_champs = self.get_all_available_champions()
        return [champ for champ in champs if champ in available_champs]

    def register_player(self, gamertag, tagline, disc_id):
        """
        Register a player in the database.
        """
        status, puuid = self.riot_api.get_puuid(gamertag, tagline)
        if status == True:
            success = self.set_player_info(disc_id, puuid, gamertag)
            return success
        return False
            
    def get_champs_with_mastery(self, disc_id):
        
        puuid = self.get_puuid(disc_id)  # Get puuid from riot account
        
        status, champs = self.riot_api.get_champs(
            puuid
        )  # Get all champs that the player has played (has mastery points on)

        return status, champs


    def get_champs_for_gamemode(self, gamemode):
        """
        Get all available champions for a gamemode.
        """
        gamemode = gamemode.lower()
        champs = self.list_champion_database()

        if gamemode == "melee":
            return self.filter_out_banned_champs([champ[0] for champ in champs if champ[2] == "melee"])
        elif gamemode == "ranged":
            return self.filter_out_banned_champs([champ[0] for champ in champs if champ[2] == "ranged"])
        elif gamemode == "support":
            return self.filter_out_banned_champs([champ[0] for champ in champs if "Support" in champ[3].split(" ")])
        elif gamemode == "tank":
            return self.filter_out_banned_champs([champ[0] for champ in champs if "Tank" in champ[3].split(" ")])
        elif gamemode == "mage":
            return self.filter_out_banned_champs([champ[0] for champ in champs if "Mage" in champ[3].split(" ")])
        elif gamemode == "assassin":
            return self.filter_out_banned_champs([champ[0] for champ in champs if "Assassin" in champ[3].split(" ")])
        elif gamemode == "fighter":
            return self.filter_out_banned_champs([champ[0] for champ in champs if "Fighter" in champ[3].split(" ")])
        elif gamemode == "marksman":
            return self.filter_out_banned_champs([champ[0] for champ in champs if "Marksman" in champ[3].split(" ")])
        return []
