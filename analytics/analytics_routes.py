from flask import render_template

def register_analytics_routes(app):

    @app.route("/analytics")
    def analytics_dashboard():
        return render_template("analytics.html")