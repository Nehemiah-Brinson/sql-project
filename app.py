from flask import Flask, jsonify
import psycopg2
import hashlib
import os
import platform
import uuid

app = Flask(__name__)

# Your Neon connection string
NEON_URL = "postgresql://neondb_owner:npg_J8CrvlmuSiF0@ep-still-moon-b5ikt14z-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def generate_unique_user_id():
    # 1. Get the MAC address (Hardware ID)
    # uuid.getnode() returns a 48-bit integer representing the MAC address
    mac = str(uuid.getnode())

    # 2. Get the Computer/Host Name
    node_name = platform.node()

    # 3. Get the Operating System details
    os_info = platform.platform()

    # 4. Combine them into a single string fingerprint
    fingerprint = f"{mac}:{node_name}:{os_info}"

    # 5. Hash the fingerprint using SHA-256 to create a clean, fixed-length ID
    user_id = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()

    return user_id

def db():
    return psycopg2.connect(NEON_URL)

# -----------------------------
# MOVIE SEARCH
# -----------------------------
@app.get("/movie/<title>")
def movie(title):
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT movie_id, title, year, runtime, rating
        FROM Movies
        WHERE LOWER(title) = LOWER(%s)
        LIMIT 50;
    """, (title,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify([
        {
            "movie_id": r[0],
            "title": r[1],
            "year": r[2],
            "runtime": r[3],
            "rating": r[4]
        }
        for r in rows
    ])

# -----------------------------
# ACTOR SEARCH
# -----------------------------
@app.get("/actor/<name>")
def actor(name):
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT movie_id, title, year, runtime, rating
        FROM (Actors natural join Movie_Actors) natural join Movies
        WHERE LOWER(actor_name) = LOWER(%s)
        LIMIT 50;
    """, (name,))
    
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify([
        {
            "movie_id": r[0],
            "title": r[1],
            "year": r[2],
            "runtime": r[3],
            "rating": r[4]
        }
        for r in rows
    ])
# -----------------------------
# DIRECTOR SEARCH
# -----------------------------
@app.get("/director/<name>")
def director(name):
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT movie_id, title, year, runtime, rating
        from movies natural join movie_directors
        WHERE director_id in (SELECT director_id
        FROM directors
        WHERE LOWER(director_name) = LOWER(%s))
        LIMIT 50;
    """, (name,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify([
        {
            "movie_id": r[0],
            "title": r[1],
            "year": r[2],
            "runtime": r[3],
            "rating": r[4]
        }
        for r in rows
    ])

# -----------------------------
# GENRE SEARCH
# -----------------------------
@app.get("/genre/<genre>")
def genre(genre):
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT m.movie_id, m.title, m.year, m.rating
        FROM Movies m
        JOIN Movie_Genres mg ON m.movie_id = mg.movie_id
        JOIN Genres g ON mg.genre_id = g.genre_id
        WHERE LOWER(g.genre_name) = LOWER(%s)
        LIMIT 100;
    """, (genre,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify([
        {
            "movie_id": r[0],
            "title": r[1],
            "year": r[2],
            "rating": r[3]
        }
        for r in rows
    ])

# -----------------------------
# HOME PAGE (optional)
# -----------------------------
@app.get("/")
def home():
    return {
        "message": "IMDb API is running. Try /movie/Inception or /actor/Leonardo DiCaprio"
    }

# -----------------------------
# actor + genre SEARCH
# -----------------------------
@app.get("/genreActor/<actor>/<genre>")
def genreActor(actor,genre):
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT m.movie_id, m.title, m.year, m.rating
        FROM Movies m
        JOIN Movie_Genres mg ON m.movie_id = mg.movie_id
        JOIN Genres g ON mg.genre_id = g.genre_id
        WHERE LOWER(g.genre_name) = LOWER(%s) and  m.movie_id in (
        SELECT movie_id
        FROM (Actors natural join Movie_Actors) natural join Movies
        WHERE LOWER(actor_name) = LOWER(%s))
    """, (genre,actor,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify([
        {
            "movie_id": r[0],
            "title": r[1],
            "year": r[2],
            "rating": r[3]
        }
        for r in rows
    ])

# -----------------------------
# actor + genre SEARCH
# -----------------------------
@app.get("/actorGenre/<genre>/<actor>")
def actorGenre(genre,actor):
    return genreActor(actor,genre)

# -----------------------------
# genre + director SEARCH
# -----------------------------
@app.get("/genreDirector/<genre>/<director>")
def genreDirector(genre, director):
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT m.movie_id, m.title, m.year, m.rating
        FROM Movies AS m
        JOIN Movie_Genres AS mg ON m.movie_id = mg.movie_id
        JOIN Genres AS g ON mg.genre_id = g.genre_id
        JOIN Movie_Directors AS md ON m.movie_id = md.movie_id
        JOIN Directors AS d ON md.director_id = d.director_id
        WHERE LOWER(g.genre_name) = LOWER(%s)
          AND LOWER(d.director_name) = LOWER(%s)
        LIMIT 100;
    """, (genre, director))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify([
        {
            "movie_id": r[0],
            "title": r[1],
            "year": r[2],
            "rating": r[3]
        }
        for r in rows
    ])

# -----------------------------
# actor + director SEARCH
# -----------------------------
@app.get("/actorDirector/<actor>/<director>")
def actorDirector(actor, director):
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT m.movie_id, m.title, m.year, m.rating
        FROM Movies AS m
        JOIN Movie_Actors AS ma ON m.movie_id = ma.movie_id
        JOIN Actors AS a ON ma.actor_id = a.actor_id
        JOIN Movie_Directors AS md ON m.movie_id = md.movie_id
        JOIN Directors AS d ON md.director_id = d.director_id
        WHERE LOWER(a.actor_name) = LOWER(%s)
          AND LOWER(d.director_name) = LOWER(%s)
        LIMIT 100;
    """, (actor, director))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify([
        {
            "movie_id": r[0],
            "title": r[1],
            "year": r[2],
            "rating": r[3]
        }
        for r in rows
    ])

#-------------------------------
#actor + genre + director
#------------------------------
@app.get("/actorGenreDirector/<actor>/<genre>/<director>")
def actorGenreDirector(actor,genre,director):
    conn = db()
    cur = conn.cursor()
    cur.execute("""
      SELECT DISTINCT m.movie_id, m.title, m.year, m.rating
    FROM Movies AS m
    JOIN Movie_Genres AS mg
    ON m.movie_id = mg.movie_id
    JOIN Genres AS g
    ON mg.genre_id = g.genre_id
    WHERE LOWER(g.genre_name) = LOWER(%s)
  AND m.movie_id IN (
      SELECT ma.movie_id
      FROM Actors AS a
      JOIN Movie_Actors AS ma
          ON a.actor_id = ma.actor_id
      WHERE LOWER(a.actor_name) = LOWER(%s)
  )
  AND m.movie_id IN (
      SELECT md.movie_id
      FROM Movie_Directors AS md
      JOIN Directors AS d
          ON md.director_id = d.director_id
      WHERE LOWER(d.director_name) = LOWER(%s)
  )
    """, (genre,actor,director,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify([
        {
            "movie_id": r[0],
            "title": r[1],
            "year": r[2],
            "rating": r[3]
        }
        for r in rows
    ])
    


# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    unique_id = generate_unique_user_id()
    app.run(debug=True)
