from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

# Your Neon connection string
NEON_URL = "postgresql://neondb_owner:npg_J8CrvlmuSiF0@ep-still-moon-b5ikt14z-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

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
        WHERE LOWER(actor_name) = LOWER(%s)
        )
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
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
