import pandas as pd
import pickle

print("Building name lookup dictionary...")

df = pd.read_csv("imdb_data/name.basics.csv", usecols=["nconst", "primaryName"])

lookup = {row["nconst"]: row["primaryName"] for _, row in df.iterrows()}

with open("name_lookup.pkl", "wb") as f:
    pickle.dump(lookup, f)

print("name_lookup.pkl created!")
