from account import account
import pandas as pd
from db.data_handler import dataHandler
import random
from datetime import datetime


class game_lobby:

    def __init__(self):
        self.lobby = []
        self.team = []

        self.dh = dataHandler()

    def register_player(self, disc_id, gamertag, tagline):
        """
        Register a player in the lobby.
        """
        return self.dh.register_player(gamertag, tagline, disc_id)

    def add_player(self, disc_id):
        """
        Add a player to the lobby.
        """
        if self.dh.player_is_registered(disc_id):
            if account(disc_id, "", []) in self.lobby:
                return True
            
            #Get all champions that an account has mastery points on
            status, champs = self.dh.get_champs_with_mastery(disc_id)
            
            if status == False: #An error has occured
                return False
            
            
            #Add player
            gamertag = self.dh.get_gamertag(disc_id)  # Get gamertag from riot account
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

    def roll_champs(self, gamemode):
        """
        Roll champions for a list of players.
        """
        # Sort players on number of champions
        self.lobby.sort(key=lambda x: x.num_champs)
        available_champs = self.dh.get_champs_for_gamemode(gamemode)
        selected_champs = []
        for player in self.lobby:
            selected_champs += player.select_champions(selected_champs, available_champs)

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

    def start(self, disc_ids, gamemode):
        """
        Start the game.
        """
        status, unreg_players = self.new_lobby(disc_ids)
        if status == False:
            return False, unreg_players
        self.roll_champs(gamemode)
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

    def get_champs_for_gamemode(self, gamemode):
        """
        Get all champions for a specific gamemode.
        """
        return self.dh.get_champs_for_gamemode(gamemode)

