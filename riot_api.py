import requests


def get_account_info(gamertag):
    req = requests.get('http://localhost:5000/')