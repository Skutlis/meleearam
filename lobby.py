from account import account
import pandas as pd
from db.data_handler import dataHandler
from riot_api import Riot_Api as ra
import random


class game_lobby:

    def __init__(self):
        self.lobby = []
        self.team = []

        self.api = ra()
        self.dh = dataHandler()

    def new_lobby(self):
        self.lobby = []

    def register_player(self, disc_id, gamertag, tagline):
        """
        Register a player in the lobby.
        """
        status, puuid = self.api.get_puuid(gamertag, tagline)
        if status == True:
            self.dh.set_player_info(disc_id, puuid)
            return True
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

    def remove_player(self, disc_id):
        """
        Remove a player from the lobby.
        """
        for player in self.lobby:
            if player.id == disc_id:
                self.lobby.remove(player)
                return True
        return False

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

    def start(self, disc_ids, keep_teams=False):
        """
        Start the game.
        """
        self.roll_champs()
        if not keep_teams and self.team != []:
            status, unreg_players = self.add_players(disc_ids)
            if status == False:
                return False, unreg_players
            self.divide_teams()

        # Convert gameinfo to a string
        gameinfo = ""
        for i, team in enumerate(self.team):
            gameinfo += f"Team {i+1}: " + "\n"
            for player in team:
                gameinfo += (
                    f"{player.gamertag}:" + ", ".join(player.selected_champs) + "\n"
                )

        return True, gameinfo
