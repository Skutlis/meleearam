from account import riot_account



class game_lobby():
    
    def __init__(self):
        self.lobby = []
        
    def add_player(self, gamertag):
        self.lobby.append(riot_account(gamertag))
        
    def 