from account import riot_account
import pandas as pd


class game_lobby():
    
    def __init__(self):
        self.lobby = []
        self.melee_champs = pd.read_csv('melee_champs.csv')
        print(self.melee_champs.head())
        
    def add_player(self, gamertag):
        self.lobby.append(riot_account(gamertag))
        
    
    

lobby = game_lobby()
