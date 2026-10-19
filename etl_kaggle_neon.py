import pandas as pd
import psycopg2
import os

NEON_DB_URL = os.getenv(
    "NEON_DB_URL",
    "postgresql://neondb_owner:YOUR_PASSWORD@ep-still-moon-b5ikt14z.us-east-2.aws.neon.tech/neondb"
)

conn = psycopg2.connect(NEON_DB_URL)
cur = conn.cursor()

# Load Kaggle CSV files (adjust paths if needed)
titles = pd.read_csv("imdb_data/title.basics.csv")
ratings = pd.read_csv("imdb_data/title.ratings.csv")
principals = pd.read_csv("imdb_data/title.principals.csv")
names = pd.read_csv("imdb_data/name.basics.csv")

movies = titles[titles["titleType"] == "movie"]
movies = movies.merge(ratings, on="tconst", how="left")

for _, row in movies.iterrows():
    cur.execute("""
        INSERT INTO Movies (movie_id, title, year, runtime, rating)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (movie_id) DO NOTHING;
    """, (
        row["tconst"],
        row["primaryTitle"],
        row["startYear"],
        row["runtimeMinutes"],
        row["averageRating"]
    ))

genre_map = {}
for _, row in movies.iterrows():
    if pd.isna(row["genres"]):
        continue
    for g in row["genres"].split(","):
        if g not in genre_map:
            cur.execute("INSERT INTO Genres (genre_name) VALUES (%s) RETURNING genre_id;", (g,))
            genre_map[g] = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO Movie_Genres (movie_id, genre_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
        """, (row["tconst"], genre_map[g]))

for _, row in principals.iterrows():
    pid = row["nconst"]
    mid = row["tconst"]
    category = row["category"]

    name_row = names[names["nconst"] == pid]
    if name_row.empty:
        continue

    person_name = name_row.iloc[0]["primaryName"]

    if category in ["actor", "actress"]:
        cur.execute("""
            INSERT INTO Actors (actor_id, actor_name)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
        """, (pid, person_name))

        cur.execute("""
            INSERT INTO Movie_Actors (movie_id, actor_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
        """, (mid, pid))

    if category == "director":
        cur.execute("""
            INSERT INTO Directors (director_id, director_name)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
        """, (pid, person_name))

        cur.execute("""
            INSERT INTO Movie_Directors (movie_id, director_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
        """, (mid, pid))

conn.commit()
cur.close()
conn.close()

print("Loaded Kaggle IMDb data into Neon PostgreSQL.")
