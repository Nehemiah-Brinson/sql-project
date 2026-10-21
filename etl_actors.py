import pandas as pd
import psycopg2
import pickle
from tqdm import tqdm

NEON_URL = "postgresql://neondb_owner:npg_J8CrvlmuSiF0@ep-still-moon-b5ikt14z-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

CHUNK_SIZE = 50000
ACTOR_BATCH = 100
REL_BATCH = 100

def batch_insert(cur, query, data, template):
    if not data:
        return
    args = ",".join(cur.mogrify(template, row).decode("utf-8") for row in data)
    cur.execute(query + args)

# Load name lookup dictionary
with open("name_lookup.pkl", "rb") as f:
    name_lookup = pickle.load(f)

conn = psycopg2.connect(NEON_URL)
cur = conn.cursor()

print("Loading existing DB state...")

cur.execute("SELECT movie_id FROM Movies;")
existing_movies = {row[0] for row in cur.fetchall()}

cur.execute("SELECT actor_id FROM Actors;")
existing_actors = {row[0] for row in cur.fetchall()}

cur.execute("SELECT movie_id, actor_id FROM Movie_Actors;")
existing_movie_actors = {(row[0], row[1]) for row in cur.fetchall()}

actor_batch = []
rel_batch = []

print("Processing actors in chunks...")

for chunk in pd.read_csv("imdb_data/title.principals.csv", chunksize=CHUNK_SIZE, low_memory=False):
    for _, row in tqdm(chunk.iterrows(), total=len(chunk), desc="Actors"):
        pid = row["nconst"]
        mid = row["tconst"]
        category = row["category"]

        if category not in ["actor", "actress"]:
            continue
        if mid not in existing_movies:
            continue

        # Fast name lookup
        person_name = name_lookup.get(pid)
        if not person_name:
            continue

        # Insert actor
        if pid not in existing_actors:
            actor_batch.append((pid, person_name))
            existing_actors.add(pid)

        # Insert relationship
        if (mid, pid) not in existing_movie_actors:
            rel_batch.append((mid, pid))
            existing_movie_actors.add((mid, pid))

        # STRICT ORDER: flush actors BEFORE relationships
        if len(actor_batch) >= ACTOR_BATCH:
            batch_insert(cur,
                "INSERT INTO Actors (actor_id, actor_name) VALUES ",
                actor_batch,
                "(%s,%s)"
            )
            conn.commit()
            actor_batch = []

        if len(rel_batch) >= REL_BATCH:
            # Always flush actors first
            if actor_batch:
                batch_insert(cur,
                    "INSERT INTO Actors (actor_id, actor_name) VALUES ",
                    actor_batch,
                    "(%s,%s)"
                )
                conn.commit()
                actor_batch = []

            batch_insert(cur,
                "INSERT INTO Movie_Actors (movie_id, actor_id) VALUES ",
                rel_batch,
                "(%s,%s)"
            )
            conn.commit()
            rel_batch = []

# Final flush
if actor_batch:
    batch_insert(cur,
        "INSERT INTO Actors (actor_id, actor_name) VALUES ",
        actor_batch,
        "(%s,%s)"
    )

if rel_batch:
    batch_insert(cur,
        "INSERT INTO Movie_Actors (movie_id, actor_id) VALUES ",
        rel_batch,
        "(%s,%s)"
    )

conn.commit()
cur.close()
conn.close()

print("Actors ETL complete (fast + chunked + strict order).")
