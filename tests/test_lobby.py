import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(parent_dir)
os.chdir(parent_dir)

from lobby import game_lobby


class TestLobby(unittest.TestCase):

    def setUp(self):
        self.lobby = game_lobby()

    def test_register_player(self):
        self.lobby.api.get_puuid = Mock(return_value=(True, "PUUID"))
        self.lobby.dh.set_player_info = Mock(return_value=True)
        self.assertTrue(self.lobby.register_player(1, "gamertag", "tagline"))

    def test_add_player(self):
        self.lobby.dh.player_is_registered = Mock(return_value=True)
        self.lobby.dh.get_puuid = Mock(return_value="PUUID")
        self.lobby.dh.get_gamertag = Mock(return_value="gamertag")
        self.lobby.api.get_champs = Mock(return_value=(True, [1, 2, 3]))
        self.lobby.dh.filter_out_banned_champs = Mock(return_value=[1, 2, 3])
        self.assertTrue(self.lobby.add_player(1))

    def test_add_players(self):
        self.lobby.add_player = Mock(return_value=True)
        self.assertTrue(self.lobby.add_players([1, 2, 3]))

    def test_add_players_unregistered(self):
        self.lobby.add_player = Mock(return_value=False)
        status, players = self.lobby.add_players([1, 2, 3])
        self.assertFalse(status)

    def test_start_does_not_start_if_not_all_player_registered(self):
        self.lobby.add_player = Mock(return_value=(False, [1, 2, 3]))
        print(self.lobby.start([1, 2, 3]))
        status, _ = self.assertTrue(self.lobby.start([1, 2, 3]))
        self.assertFalse(status)


if __name__ == "__main__":
    unittest.main()
