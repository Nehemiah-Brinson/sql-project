def get_overview_counts(cur):

    cur.execute("""
        SELECT
            (SELECT COUNT(*) FROM Movies),
            (SELECT COUNT(*) FROM Actors),
            (SELECT COUNT(*) FROM Directors),
            (SELECT COUNT(*) FROM Genres)
    """)

    row = cur.fetchone()

    return {
        "movies": row[0],
        "actors": row[1],
        "directors": row[2],
        "genres": row[3]
    }


def get_top_genres(cur):

    cur.execute("""
        SELECT
            g.genre_name,
            COUNT(*) AS total_movies
        FROM Genres g
        JOIN Movie_Genres mg
            ON g.genre_id = mg.genre_id
        GROUP BY g.genre_name
        ORDER BY total_movies DESC
        LIMIT 10
    """)

    rows = cur.fetchall()

    return [
        {
            "genre": row[0],
            "count": row[1]
        }
        for row in rows
    ]