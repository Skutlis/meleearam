import db.data_handler as dh


class riot_account:

    def __init__(self, disc_id):
        self.gamertag = disc_id
        self.load_owned_champions()
        self.selected_champs = []

       

    def set_gamertag(self, disc_id, gamertag):
        self.gamertag = gamertag

    def load_owned_champions(self):
        """
        Fetch the list of champions that the user owns with the riot api. 
        """
        if self.gamertag == "admin":
            self.owned_champs == []
        pass

    def select_champions(self, unavailable_champions):
        pass
