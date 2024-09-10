from db.DBManager import dbManager
import json


class dataHandler:

    def __init__(self):
        self.db = dbManager()
        # Load configs from file
        with open("table_config.json", "r") as json_file:
            configs = json.load(open("table_config.json"))

        # Set the table names and columns
        self.melee_champs_table_name = configs["melee_champs_table_name"]
        self.melee_champs_columns = configs["melee_champs_columns"]
        self.player_table_name = configs["player_table_name"]
        self.player_columns = configs["player_columns"]

        # Set up tables if they don't exist
        if not self.db.table_exists(self.melee_champs_table_name):
            self.db.create_table(
                self.melee_champs_table_name,  # table name
                ["name"],  # primary key
                self.melee_champs_columns,  # columns
            )

        if not self.db.table_exists(self.player_table_name):
            self.db.create_table(
                self.player_table_name,  # table name
                ["disc_id"],  # primary key
                self.player_columns,  # columns
            )

    def get_all_champions(self):
        """
        Get all champions from the database.
        """
        return self.db.list_rows(self.melee_champs_table_name)

    def get_all_available_champions(self):
        """
        Get all champions that are not banned
        """
        available_champs = []
        all_champs = self.get_all_champions()
        for champ in all_champs:
            if champ[1] == "True":
                available_champs.append(champ[0])

        return available_champs

    def get_banned_champs(self):
        """
        Get all champions that are banned.
        """
        banned_champs = []
        all_champs = self.get_all_champions()
        for champ in all_champs:
            if champ[1] == "False":
                banned_champs.append(champ[0])

        return banned_champs

    def add_champ(self, champ, is_available=True):
        """
        Add a champion to the database.
        """
        self.db.add_row(
            self.melee_champs_table_name, {"name": champ, "is_available": is_available}
        )

    def ban_champ(self, champ):
        """
        Ban a champion from the database.
        """
        self.db.update_row(
            self.melee_champs_table_name, {"name": champ}, {"is_available": False}
        )

    def unban_champ(self, champ):
        """
        Unban a champion from the database.
        """
        self.db.update_row(
            self.melee_champs_table_name, {"name": champ}, {"is_available": True}
        )

    def set_player_info(self, disc_id, puuid, gamertag):
        """
        Set the gamertag of a player in the database.
        """
        if self.db.exists(self.player_table_name, {"disc_id": disc_id}):
            self.db.update_row(
                self.player_table_name,
                {"disc_id": disc_id},
                {"disc_id": disc_id, "puuid": puuid, "gamertag": gamertag},
            )
        else:
            self.db.add_row(
                self.player_table_name,
                {"disc_id": disc_id, "puuid": puuid, "gamertag": gamertag},
            )

    def get_gamertag(self, disc_id):
        """
        Get the gamertag of a player from the database.
        """
        return self.db.get_row(self.player_table_name, {"disc_id": disc_id})[2]

    def get_puuid(self, disc_id):
        """
        Get the puuid of a player from the database.
        """
        return self.db.get_row(self.player_table_name, {"disc_id": disc_id})[1]

    def player_is_registered(self, disc_id):
        """
        Check if a player is registered in the database.
        """
        return self.db.exists(self.player_table_name, {"disc_id": disc_id})

    def get_player_info(self, gamertag):
        """
        Get the puuid of a gamertag.
        """
        info = self.db.get_row(self.player_table_name, {"gamertag": gamertag})
        gamertag = info[2]
        puuid = info[1]
        return gamertag, puuid

    def update_gamertag(self, disc_id, gamertag):
        """
        Update the gamertag of a player in the database.
        """
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
        banned_champs = self.get_all_available_champions()
        return [champ for champ in champs if champ in banned_champs]
