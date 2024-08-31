import db.data_handler as dh


class riot_account:

    def __init__(self, disc_id):
        self.gamertag = disc_id
        self.load_owned_champions()
        self.selected_champs = []

        """
        Fetch the list of champions that the user owns. 
        """

    def set_gamertag(self, disc_id, gamertag):
        self.gamertag = gamertag

    def load_owned_champions(self):
        pass

    def select_champions(self, unavailable_champions):
        pass
