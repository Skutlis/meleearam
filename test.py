import pandas as pd
from db.data_handler import dataHandler


m = pd.read_csv("melee_champs.csv")

print(m.head())

champs = m["Champion"].tolist()

dh = dataHandler()

for champ in champs:
    if "'" in champ:
        champ = champ.replace("'", " ")
    dh.add_champ(champ)
