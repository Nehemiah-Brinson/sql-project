import pandas as pd
import psycopg2
from tqdm import tqdm

NEON_URL = "postgresql://neondb_owner:npg_J8CrvlmuSiF0@ep-still-moon-b5ikt14z-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
BATCH_SIZE = 500

def batch_insert(cur, query, data, template):
    if not data:
        return
    args_str = ",".join(cur.mogrify(template, row).decode("utf-8") for row in data)
    cur.execute(query + args_str)

conn = psycopg2.connect(NEON_URL)
cur = conn.cursor()

print("Loading CSV files...")
titles = pd.read_csv("imdb_data/title.basics.csv", low_memory=False)
ratings = pd.read_csv("imdb_data/title.ratings.csv", low_memory=False)

movies = titles[titles["titleType"] == "movie"]
movies = movies.merge(ratings, on="tconst", how="left")

print("Inserting movies...")
cur.execute("SELECT movie_id FROM Movies;")
existing_movies = {row[0] for row in cur.fetchall()}

movie_batch = []

for _, row in tqdm(movies.iterrows(), total=len(movies), desc="Movies"):
    movie_id = row["tconst"]
    if movie_id in existing_movies:
        continue

    try: year = int(row["startYear"])
    except: year = None

    try: runtime = int(row["runtimeMinutes"])
    except: runtime = None

    try: rating = float(row["averageRating"])
    except: rating = None

    movie_batch.append((movie_id, row["primaryTitle"], year, runtime, rating))
    existing_movies.add(movie_id)

    if len(movie_batch) >= BATCH_SIZE:
        batch_insert(cur,
            "INSERT INTO Movies (movie_id, title, year, runtime, rating) VALUES ",
            movie_batch,
            "(%s,%s,%s,%s,%s)"
        )
        movie_batch = []
        conn.commit()

batch_insert(cur,
    "INSERT INTO Movies (movie_id, title, year, runtime, rating) VALUES ",
    movie_batch,
    "(%s,%s,%s,%s,%s)"
)
conn.commit()

print("Movies inserted.")

print("Inserting genres...")
cur.execute("SELECT movie_id, genre_id FROM Movie_Genres;")
existing_movie_genres = {(row[0], row[1]) for row in cur.fetchall()}

genre_map = {}
genre_batch = []

for _, row in tqdm(movies.iterrows(), total=len(movies), desc="Genres"):
    movie_id = row["tconst"]
    if movie_id not in existing_movies:
        continue
    if pd.isna(row["genres"]):
        continue

    for g in row["genres"].split(","):
        if g not in genre_map:
            cur.execute("INSERT INTO Genres (genre_name) VALUES (%s) RETURNING genre_id;", (g,))
            genre_map[g] = cur.fetchone()[0]

        genre_id = genre_map[g]

        if (movie_id, genre_id) in existing_movie_genres:
            continue

        genre_batch.append((movie_id, genre_id))
        existing_movie_genres.add((movie_id, genre_id))

        if len(genre_batch) >= BATCH_SIZE:
            batch_insert(cur,
                "INSERT INTO Movie_Genres (movie_id, genre_id) VALUES ",
                genre_batch,
                "(%s,%s)"
            )
            genre_batch = []
            conn.commit()

batch_insert(cur,
    "INSERT INTO Movie_Genres (movie_id, genre_id) VALUES ",
    genre_batch,
    "(%s,%s)"
)
conn.commit()

cur.close()
conn.close()

print("Movies + Genres ETL complete.")
