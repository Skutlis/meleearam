from db.DBManager import dbManager
from db.data_handler import dataHandler

handler= dataHandler()

m1 = handler.get_champs_for_gamemode("melee")

handler.ban_champ("Aatrox")

m2 = handler.get_champs_for_gamemode("melee")

banned = handler.get_banned_champs()


print("First")
print(m1)
print("second")
print(m2)
print("Banned")
print(banned)

