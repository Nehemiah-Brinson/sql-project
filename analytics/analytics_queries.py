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
