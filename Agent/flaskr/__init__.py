from flask import Flask
from flask_cors import CORS

from Agent.flaskr.ExchangeMonitor import ExchangeMonitor


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)
    exchange_monitor = ExchangeMonitor()

    @app.route("/open_race/<customer_id>/<event_id>/<market_id>")
    def open_race(customer_id, event_id: str, market_id: str):
        exchange_monitor.open_race(customer_id, event_id, market_id)
        return exchange_monitor.current_full_race_card.json

    @app.route("/get_monitor_data/")
    def get_monitor_data():
        monitor_data = exchange_monitor.serve_monitor_data()
        return monitor_data.json

    return app
