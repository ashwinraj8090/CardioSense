
import os
from dotenv import load_dotenv

load_dotenv() 

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    
    JWT_SECRET = os.environ.get("JWT_SECRET", "dev-only-change-me-too")
    JWT_EXPIRY_MINUTES = int(os.environ.get("JWT_EXPIRY_MINUTES", "120"))

    # SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or (
    "sqlite:///" + os.path.join(os.path.dirname(__file__), "cardiosense.db"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
