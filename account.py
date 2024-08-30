


class riot_account():
    
    def __init__(self, gamertag):
        self.gamertag = gamertag
        self.load_owned_champions()
        
        """
        Fetch the list of champions that the user owns. 
        """
    def load_owned_champions(self):
        pass
    
    def select_champions(self, unavailable_champions):
        pass