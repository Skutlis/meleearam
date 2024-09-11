from account import account
import pandas as pd
from db.data_handler import dataHandler
from riot_api import Riot_Api as ra
import random
from datetime import datetime


class game_lobby:

    def __init__(self):
        self.lobby = []
        self.team = []

        self.api = ra()
        self.dh = dataHandler()

    def register_player(self, disc_id, gamertag, tagline):
        """
        Register a player in the lobby.
        """
        status, puuid = self.api.get_puuid(gamertag, tagline)
        if status == True:
            success = self.dh.set_player_info(disc_id, puuid, gamertag)
            return success
        return False

    def add_player(self, disc_id):
        """
        Add a player to the lobby.
        """
        if self.dh.player_is_registered(disc_id):
            if account(disc_id, "", []) in self.lobby:
                return True
            puuid = self.dh.get_puuid(disc_id)  # Get puuid from riot account
            gamertag = self.dh.get_gamertag(disc_id)  # Get gamertag from riot account
            status, champs = self.api.get_champs(
                puuid
            )  # Get all champs that the player has played
            if status == False:
                return False
            champs = self.dh.filter_out_banned_champs(
                champs
            )  # Filter out banned champs
            if status == True:
                acc = account(disc_id, gamertag, champs)
                self.lobby.append(acc)
                return True
        return False

    def add_players(self, players: list):
        """
        Add a list of players to the lobby.
        """
        unregistered_players = []
        for player in players:
            player_added = self.add_player(player)
            if not player_added:
                unregistered_players.append(player)

        if len(unregistered_players) > 0:
            return False, unregistered_players
        return True, []

    def get_players(self):
        """
        Get the players in the lobby.
        """
        return [player.gamertag for player in self.lobby]

    def roll_champs(self):
        """
        Roll champions for a list of players.
        """
        # Sort players on number of champions
        self.lobby.sort(key=lambda x: x.num_champs)
        selected_champs = []
        for player in self.lobby:
            selected_champs += player.select_champions(selected_champs)

    def divide_teams(self):
        """
        Divide the players in the lobby into two randomly selected teams.
        """
        random.shuffle(self.lobby)
        self.team = [[], []]
        for i, player in enumerate(self.lobby):
            self.team[i % 2].append(player)

    def new_lobby(self, disc_ids):
        """
        Create a lobby with a list of players.
        """
        self.lobby = []
        status, unreg_players = self.add_players(disc_ids)
        if status == False:
            return False, unreg_players
        return True, []

    def start(self, disc_ids):
        """
        Start the game.
        """
        status, unreg_players = self.new_lobby(disc_ids)
        if status == False:
            return False, unreg_players
        self.roll_champs()
        self.divide_teams()

        # Convert gameinfo to a string
        gameinfo = ""
        for i, team in enumerate(self.team):

            gameinfo += f"Team {i+1}: " + "\n"
            for player in team:
                gameinfo += (
                    f"{player.gamertag}: " + ", ".join(player.selected_champs) + "\n"
                )

        return True, gameinfo

    def get_lobby(self):
        """
        Get the lobby.
        """
        return [player.gamertag for player in self.lobby]

    def ban_champ(self, champ):
        """
        Ban a champion from the game.
        """
        return self.dh.ban_champ(champ)

    def unban_champ(self, champ):
        """
        Unban a champion from the game.
        """
        return self.dh.unban_champ(champ)

    def list_banned_champs(self):
        """
        List all banned champions.
        """
        return self.dh.get_banned_champs()
