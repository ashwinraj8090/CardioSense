
import logging
from flask import Flask
from flask_cors import CORS

from config import Config
from extensions import db
from extensions import db, limiter 


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    limiter.init_app(app)
    app.config["RATELIMIT_DEFAULT"] = "60 per minute"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

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
   
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
