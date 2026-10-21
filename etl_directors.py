import pandas as pd
import psycopg2
import pickle
from tqdm import tqdm

NEON_URL = "postgresql://neondb_owner:npg_J8CrvlmuSiF0@ep-still-moon-b5ikt14z-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

CHUNK_SIZE = 50000
DIR_BATCH = 100
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

cur.execute("SELECT director_id FROM Directors;")
existing_directors = {row[0] for row in cur.fetchall()}

cur.execute("SELECT movie_id, director_id FROM Movie_Directors;")
existing_movie_directors = {(row[0], row[1]) for row in cur.fetchall()}

director_batch = []
rel_batch = []

print("Processing directors in chunks...")

for chunk in pd.read_csv("imdb_data/title.principals.csv", chunksize=CHUNK_SIZE, low_memory=False):
    for _, row in tqdm(chunk.iterrows(), total=len(chunk), desc="Directors"):
        pid = row["nconst"]
        mid = row["tconst"]
        category = row["category"]

        if category != "director":
            continue
        if mid not in existing_movies:
            continue

        # Fast name lookup
        person_name = name_lookup.get(pid)
        if not person_name:
            continue

        # Insert director
        if pid not in existing_directors:
            director_batch.append((pid, person_name))
            existing_directors.add(pid)

        # Insert relationship
        if (mid, pid) not in existing_movie_directors:
            rel_batch.append((mid, pid))
            existing_movie_directors.add((mid, pid))

        # STRICT ORDER: flush directors BEFORE relationships
        if len(director_batch) >= DIR_BATCH:
            batch_insert(cur,
                "INSERT INTO Directors (director_id, director_name) VALUES ",
                director_batch,
                "(%s,%s)"
            )
            conn.commit()
            director_batch = []

        if len(rel_batch) >= REL_BATCH:
            # Always flush directors first
            if director_batch:
                batch_insert(cur,
                    "INSERT INTO Directors (director_id, director_name) VALUES ",
                    director_batch,
                    "(%s,%s)"
                )
                conn.commit()
                director_batch = []

            batch_insert(cur,
                "INSERT INTO Movie_Directors (movie_id, director_id) VALUES ",
                rel_batch,
                "(%s,%s)"
            )
            conn.commit()
            rel_batch = []

# Final flush
if director_batch:
    batch_insert(cur,
        "INSERT INTO Directors (director_id, director_name) VALUES ",
        director_batch,
        "(%s,%s)"
    )

if rel_batch:
    batch_insert(cur,
        "INSERT INTO Movie_Directors (movie_id, director_id) VALUES ",
        rel_batch,
        "(%s,%s)"
    )

conn.commit()
cur.close()
conn.close()

print("Directors ETL complete (fast + chunked + strict order).")
