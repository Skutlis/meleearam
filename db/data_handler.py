from db.DBManager import dbManager
import json
import pandas as pd


class dataHandler:

    def __init__(self):
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
        m = pd.read_csv("melee_champs.csv")

        champs = m["Champion"].tolist()

        for champ in champs:
            if "'" in champ:
                champ = champ.replace("'", " ")
            self.add_champ(champ)

    def format_text_field(self, text):
        """
        Format a text field for the database.
        """
        return "'" + text + "'"

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
        for champ, availability in all_champs:
            if availability:
                available_champs.append(champ)

        return available_champs

    def get_banned_champs(self):
        """
        Get all champions that are banned.
        """
        banned_champs = []
        all_champs = self.get_all_champions()
        for champ, availability in all_champs:
            if not availability:
                banned_champs.append(champ)

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

    def add_champ(self, champ, is_available="True"):
        """
        Add a champion to the database.
        """
        champ = self.format_text_field(champ)
        self.db.add_row(
            self.melee_champs_table_name, {"name": champ, "is_available": is_available}
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
        return self.db.get_row(self.player_table_name, {"disc_id": disc_id})[2]

    def get_puuid(self, disc_id):
        """
        Get the puuid of a player from the database.
        """
        # disc_id = self.format_text_field(disc_id)
        return self.db.get_row(self.player_table_name, {"disc_id": disc_id})[1]

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
        info = self.db.get_row(self.player_table_name, {"gamertag": gamertag})
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
