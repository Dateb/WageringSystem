from flask import Flask
from flask_cors import CORS

from Agent.flaskr.ValueMonitor import ValueMonitor


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    value_monitor = ValueMonitor()

    @app.route("/next_race")
    def serve_monitor_data():
        monitor_data = value_monitor.serve_monitor_data()
        return monitor_data.json

    @app.route("/skip_race")
    def skip_race():
        value_monitor.skip_race()
        return {"Okay": "okay"}

    return app
