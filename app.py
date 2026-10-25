from flask import Flask, jsonify, request
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

# -----------------------------
# MOVIE RECOMMENDATIONS
# -----------------------------
@app.get("/recomendation") 
def get_recommendations():
    #Recommend movies from the user's recent and repeated search interests.
    #User_Query_History.id is treated as the user identifier.  
    conn = db()
    cur = conn.cursor()
    user_id = request.args.get("user_id", generate_unique_user_id())
    limit = min(max(request.args.get("limit", default=20, type=int), 1), 100)

    cur.execute("""
        WITH history AS (
            SELECT LOWER(TRIM(query_value)) AS query_value,
                   LOWER(TRIM(query_type)) AS query_type,
                   "TimeStamp", NOW() AS searched_at
            FROM user_query_history
            WHERE id = %s
              AND query_value IS NOT NULL
            ORDER BY "TimeStamp" DESC
            LIMIT 100
        ),
        matches AS (
            SELECT m.movie_id, m.title, m.year, m.runtime, m.rating,
                   1.0
                   * EXP(-EXTRACT(EPOCH FROM (NOW() - h.searched_at))
                         / 2592000.0) AS score
            FROM history h
            JOIN Movies m
              ON h.query_type IN ('movie', 'movies', 'title')
             AND LOWER(m.title) = h.query_value

            UNION ALL

            SELECT m.movie_id, m.title, m.year, m.runtime, m.rating,
                   2.0
                   * EXP(-EXTRACT(EPOCH FROM (NOW() - h.searched_at))
                         / 2592000.0)
            FROM history h
            JOIN Movie_Genres mg ON h.query_type IN ('genre', 'genres')
            JOIN Genres g
              ON g.genre_id = mg.genre_id
             AND LOWER(g.genre_name) = h.query_value
            JOIN Movies m ON m.movie_id = mg.movie_id

            UNION ALL

            SELECT m.movie_id, m.title, m.year, m.runtime, m.rating,
                   2.0
                   * EXP(-EXTRACT(EPOCH FROM (NOW() - h.searched_at))
                         / 2592000.0)
            FROM history h
            JOIN Actors a
              ON h.query_type IN ('actor', 'actors')
             AND LOWER(a.actor_name) = h.query_value
            JOIN Movie_Actors ma ON ma.actor_id = a.actor_id
            JOIN Movies m ON m.movie_id = ma.movie_id

            UNION ALL

            SELECT m.movie_id, m.title, m.year, m.runtime, m.rating,
                   2.0
                   * EXP(-EXTRACT(EPOCH FROM (NOW() - h.searched_at))
                         / 2592000.0)
            FROM history h
            JOIN Directors d
              ON h.query_type IN ('director', 'directors')
             AND LOWER(d.director_name) = h.query_value
            JOIN Movie_Directors md ON md.director_id = d.director_id
            JOIN Movies m ON m.movie_id = md.movie_id
        ),
        searched_titles AS (
            SELECT DISTINCT m.movie_id
            FROM history h
            JOIN Movies m
              ON h.query_type IN ('movie', 'movies', 'title')
             AND LOWER(m.title) = h.query_value
        )
        SELECT movie_id, title, year, runtime, rating,
               SUM(score) AS recommendation_score
        FROM matches
        WHERE movie_id NOT IN (SELECT movie_id FROM searched_titles)
        GROUP BY movie_id, title, year, runtime, rating
        ORDER BY recommendation_score DESC, rating DESC NULLS LAST, title
        LIMIT %s;
    """, (user_id, limit))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify([
        {
            "movie_id": r[0],
            "title": r[1],
            "year": r[2],
            "runtime": r[3],
            "rating": r[4],
            "recommendation_score": round(float(r[5]), 4)
        }
        for r in rows
    ])

def db():
    conn = psycopg2.connect(NEON_URL)
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_query_history (
                id VARCHAR(64) NOT NULL,
                query_value VARCHAR(255) NOT NULL,
                query_type VARCHAR(30) NOT NULL,
                "TimeStamp" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
        """)
    conn.commit()
    return conn

def record_query_history(cur, query_type, query_value):
    cur.execute("""
        INSERT INTO user_query_history (id, query_value, query_type)
        VALUES (%s, %s, %s);
    """, (
        request.args.get("user_id", generate_unique_user_id()),
        query_value,
        query_type,
    ))

# -----------------------------
# MOVIE SEARCH
# -----------------------------
@app.get("/movie/<title>")
def movie(title):
    conn = db()
    cur = conn.cursor()
    record_query_history(cur, "movie", title)

    cur.execute("""
        SELECT movie_id, title, year, runtime, rating
        FROM Movies
        WHERE LOWER(title) = LOWER(%s)
        LIMIT 50;
    """, (title,))

    rows = cur.fetchall()
    conn.commit()
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
    record_query_history(cur, "actor", name)

    cur.execute("""
        SELECT movie_id, title, year, runtime, rating
        FROM (Actors natural join Movie_Actors) natural join Movies
        WHERE LOWER(actor_name) = LOWER(%s)
        LIMIT 50;
    """, (name,))
    
    rows = cur.fetchall()
    conn.commit()
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
@app.get("/directors/<name>")
@app.get("/director/<name>")
def director(name):
    conn = db()
    cur = conn.cursor()
    record_query_history(cur, "director", name)

    cur.execute("""
        SELECT movie_id, title, year, runtime, rating
        from movies natural join movie_directors
        WHERE director_id in (SELECT director_id
        FROM directors
        WHERE LOWER(director_name) = LOWER(%s))
        LIMIT 50;
    """, (name,))

    rows = cur.fetchall()
    conn.commit()
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
    record_query_history(cur, "genre", genre)

    cur.execute("""
        SELECT m.movie_id, m.title, m.year, m.rating
        FROM Movies m
        JOIN Movie_Genres mg ON m.movie_id = mg.movie_id
        JOIN Genres g ON mg.genre_id = g.genre_id
        WHERE LOWER(g.genre_name) = LOWER(%s)
        LIMIT 100;
    """, (genre,))

    rows = cur.fetchall()
    conn.commit()
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
        "message": (
            "IMDb API is running. Try /movie/Inception, "
            "/actor/Leonardo DiCaprio," 
            "/genre/Action, "
            "/genreActor/Horror/Leona Anderson, "
            "/actorGenreDirector/Leona Anderson/horror/Kasper Barfoed"
        )
    }

# -----------------------------
# actor + genre SEARCH
# -----------------------------
@app.get("/genreActor/<genre>/<actor>")
def genreActor(genre,actor):
    conn = db()
    cur = conn.cursor()
    record_query_history(cur, "actor", actor)
    record_query_history(cur, "genre", genre)

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
    conn.commit()
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
@app.get("/actorGenre/<actor>/<genre>")
def actorGenre(actor,genre):
    return genreActor(actor,genre)

# -----------------------------
# genre + director SEARCH
# -----------------------------
@app.get("/directorGenre/<director>/<genre>")
@app.get("/genreDirector/<genre>/<director>")
def genreDirector(genre, director):
    conn = db()
    cur = conn.cursor()
    record_query_history(cur, "genre", genre)
    record_query_history(cur, "director", director)

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
    conn.commit()
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
@app.get("/directorActor/<director>/<actor>")
@app.get("/actorDirector/<actor>/<director>")
def actorDirector(actor, director):
    conn = db()
    cur = conn.cursor()
    record_query_history(cur, "actor", actor)
    record_query_history(cur, "director", director)

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
    conn.commit()
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
@app.get("/directorGenreActor/<director>/<genre>/<actor>")
@app.get("/directorActorGenre/<director>/<actor>/<genre>")
@app.get("/actorDirectorGenre/<actor>/<director>/<genre>")
@app.get("/genreDirectorActor/<genre>/<director>/<Actor>")
@app.get("/genreActorDirector/<genre>/<actor>/<director>")
@app.get("/actorGenreDirector/<actor>/<genre>/<director>")
def actorGenreDirector(actor,genre,director):
    conn = db()
    cur = conn.cursor()
    record_query_history(cur, "actor", actor)
    record_query_history(cur, "genre", genre)
    record_query_history(cur, "director", director)

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
    conn.commit()
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
    app.run(debug=True)
