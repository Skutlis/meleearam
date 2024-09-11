from db.data_handler import dataHandler

dh = dataHandler()

champ = "chogath"


print(dh.find_champ(champ))
