import requests
import dotenv
import os

dotenv.load_dotenv()

api_key = os.getenv('RIOT_API_KEY')


def get_account_info(gamertag):
    req = requests.get('http://localhost:5000/')