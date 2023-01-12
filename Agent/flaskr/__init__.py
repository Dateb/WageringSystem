from flask import Flask
from flask_cors import CORS

from Agent.flaskr.ExchangeMonitor import ExchangeMonitor


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    exchange_monitor = ExchangeMonitor()

    @app.route("/monitor_data/<event_id>/<market_id>")
    def serve_betting_slip(event_id: str, market_id: str):
        monitor_data = exchange_monitor.serve_monitor_data(event_id, market_id)
        return monitor_data.json

    @app.route("/skip_race")
    def skip_race():
        exchange_monitor.skip_race()
        return {"Okay": "okay"}

    return app
