from flask import render_template, jsonify
from analytics.analytics_queries import (
    get_overview_counts,
    get_top_genres
)

def register_analytics_routes(app, db_function):

    @app.route("/analytics")
    def analytics_dashboard():
        return render_template("analytics.html")

    @app.route("/analytics/overview")
    def analytics_overview():

        conn = db_function()
        cur = conn.cursor()

        data = get_overview_counts(cur)

        cur.close()
        conn.close()

        return jsonify(data)

    @app.route("/analytics/top-genres")
    def analytics_top_genres():

        conn = db_function()
        cur = conn.cursor()

        data = get_top_genres(cur)

        cur.close()
        conn.close()

        return jsonify(data)