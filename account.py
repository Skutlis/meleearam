import db.data_handler as dh
import random


class account:

    def __init__(self, disc_id, gamertag, champs):
        self.id = disc_id
        self.game_tag = gamertag
        self.champs = champs
        self.num_champs = len(champs)
        self.selected_champs = []

    def __eq__(self, other):
        if isinstance(other, account):
            return self.id == other.id
        return False

    def select_champions(self, selected_champs):
        """
        Select 3 random champions for the player.
        """
        self.selected_champs = []
        champs = self.champs.copy()
        # remove already selected champs
        champs = [champ for champ in champs if champ not in selected_champs]
        # randomize champs
        random.shuffle(champs)
        # select 3 champs
        self.selected_champs = champs[:3]

        return self.selected_champs
