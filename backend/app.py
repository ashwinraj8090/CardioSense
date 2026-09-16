"""
app.py
------
WHAT: The application entry point. Creates the Flask app, wires up the
      database, CORS, and every route blueprint.
"""
import logging
from flask import Flask
from flask_cors import CORS

from config import Config
from extensions import db
from extensions import db, limiter 


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # CORS: in the old app.py, CORS(app) allowed every origin. For a
    # student project served from a single known frontend origin, we
    # restrict it explicitly instead of leaving it wide open (Part 23).
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    # NOTE: "*" kept here only because the frontend is opened as a local
    # file / localhost during development with no fixed origin. In a real
    # deployment, replace "*" with your actual frontend URL, e.g.
    # {"origins": "https://cardiosense.yourdomain.com"}.

    db.init_app(app)
    limiter.init_app(app)
    app.config["RATELIMIT_DEFAULT"] = "60 per minute"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    # Deliberately never log request bodies here -- passwords/device
    # secrets pass through some of these routes (Part 28).

    with app.app_context():
        from models import User, Device, MonitoringSession, VitalReading, RiskPrediction  # noqa
        db.create_all()

    from routes.auth import auth_bp
    from routes.devices import devices_bp
    from routes.sessions import sessions_bp
    from routes.readings import readings_bp
    from routes.predictions import predictions_bp
    from routes.chat import chat_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(readings_bp)
    app.register_blueprint(predictions_bp)
    app.register_blueprint(chat_bp)

    @app.route("/")
    def home():
        return {"status": "CardioSense backend running"}

    return app


app = create_app()

if __name__ == "__main__":
    # debug=False by default now (Config.DEBUG reads FLASK_DEBUG env var).
    # The old app.py had debug=True hardcoded, which leaks stack traces
    # (including internal file paths) to any visitor on error (Part 23).
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
