import pandas as pd
import psycopg2

conn = psycopg2.connect(
    dbname="imdb",
    user="postgres",
    password="yourpassword",
    host="localhost"
)
cur = conn.cursor()

#------ LOAD IMDb TSV files -------
titles = pd.read_csv("title.basics.tsv", sep="\t", na_values="\\N")
ratings = pd.read_csv("title.ratings.tsv", sep="\t", na_values="\\N")
principals = pd.read_csv("title.principals.tsv", sep="\t",na_values="\\N")
names = pd.read_csv("names.basics.tsv", sep="\t", na_values="\\N")

#------ FILTER MOVIES ONLY -------
movies = titles[titles["titleType"] == "movie"]

#------ MERGE RATINGS ------
movies = movies.merge(ratings, on="tconst", how="left")

#------ INSERT MOVIES ------
for _, row in movies.iterrows():
    cur.execute("""
    INSERT INTO Movies (movie_id, title, year, runtime, rating)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (movie_id) DO NOTHING
    """, (
        row["tconst"],
        row["primaryTitle"],
        row["startYear"],
        row["runtimeMinutes"],
        row["averageRating"]
    )
)

#------ GENRES ------
genre_map = {}
for _, row in movies.iterrows():
    if pd.isna(row["genres"]):
        continue
    for g in row["genres"].split(","):
        if g not in genre_map:
            cur.execute("INSERT INTO Genres (genre_name) VALUES(%s) RETURNING genre_id;",(g,))
            genre_map[g] = cur.fetchone()[0]
        cur.execute("""
            INSERT INTO Movie_Genres (movie_id, genre_id)
            VALUES ( %s, %s)
            ON CONFLICT DO NOTHING;
            """, (row["tconst"], genre_map[g]))
        
#------ ACTORS & DIRECTORS
for _, row in principals.iterrows():
    pid = row["nconst"]
    mid = row["tconst"]
    category = row["category"]

    #--- INSERT PERSON ---
    name_row = names[names["nconst"] == pid]
    if not name_row.empty:
        cur.execute("""
            INSERT INTO Actors (actor_id, actor_name)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
            """, (pid, name_row.iloc[0]["primaryName"]))

        cur.execute("""
            INSERT INTO Directors (director_id, director_name)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
            """, (pid, name_row.iloc[0]["primaryName"]))

    #--- LINK TO MOVIE ---
    if category == "actor" or category =="actress":
        cur.execute("""
            INSERT INTO Movie_Actors (movie_id, actor_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
            """, (mid,pid))

    if category == "director":
        cur.execute("""
            INSERT INTO Movie_Directors (movie_id, director_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
            """, (mid, pid))
conn.commit()
cur.close()
conn.close()