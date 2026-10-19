from flask import Flask, jsonify
import psycopg2

app = Flask(__name__)

NEON_DB_URL = os.getenv(
    "NEON_DB_URL",
    "postgresql://neondb_owner:YOUR_PASSWORD@ep-still-moon-b5ikt14z.us-east-2.aws.neon.tech/neondb"
)
# -----------------------------
# MOCK MODE TO RUN WITHOUT DATA
# -----------------------------
USE_MOCK = True

mock_movies = {
    "tt1375666": {"movie_id": "tt1375666", "title": "Inception", "year": 2010, "runtime": 148, "rating": 8.8},
    "tt0468569": {"movie_id": "tt0468569", "title": "The Dark Knight", "year": 2008, "runtime": 152, "rating": 9.0}
}

mock_actors = {
    "Leonardo DiCaprio": {"actor_id": "nm0000138", "actor_name": "Leonardo DiCaprio"},
    "Christian Bale": {"actor_id": "nm0000288", "actor_name": "Christian Bale"}
}

mock_genres = {
    "Action": ["Inception", "The Dark Knight"],
    "Drama": ["Inception"]
}

mock_recommendations = {
    "tt1375666": ["The Dark Knight"],
    "tt0468569": ["Inception"]
}

# -----------------------------
# REAL DATABASE CONNECTION
# -----------------------------
def db():
    return psycopg2.connect(
        dbname="imdb",
        user="postgres",
        password="yourpassword",
        host="localhost"
    )

# -----------------------------
# ENDPOINTS
# -----------------------------

@app.get("/movie/<title>")
def get_movie(title):
    if USE_MOCK:
        for m in mock_movies.values():
            if m["title"].lower() == title.lower():
                return jsonify(m)
        return jsonify({"error": "Movie not found (mock mode)"})

    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Movies WHERE LOWER(title)=LOWER(%s);", (title,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(result)


@app.get("/actor/<name>")
def get_actor(name):
    if USE_MOCK:
        return jsonify(mock_actors.get(name, {"error": "Actor not found (mock mode)"}))

    conn = db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Actors WHERE LOWER(actor_name)=LOWER(%s);", (name,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(result)


@app.get("/genre/<genre>")
def get_genre(genre):
    if USE_MOCK:
        return jsonify(mock_genres.get(genre, []))

    conn = db()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.title
        FROM Movies m
        JOIN Movie_Genres mg ON m.movie_id = mg.movie_id
        JOIN Genres g ON mg.genre_id = g.genre_id
        WHERE LOWER(g.genre_name)=LOWER(%s);
    """, (genre,))
    result = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(result)


@app.get("/recommend/<movie_id>")
def recommend(movie_id):
    if USE_MOCK:
        return jsonify(mock_recommendations.get(movie_id, []))

    conn = db()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.title
        FROM Movie_Genres mg
        JOIN Movies m ON mg.movie_id = m.movie_id
        WHERE mg.genre_id IN (
            SELECT genre_id FROM Movie_Genres WHERE movie_id=%s
        )
        AND m.movie_id != %s
        LIMIT 10;
    """, (movie_id, movie_id))
    result = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(result)


app.run(debug=True)
