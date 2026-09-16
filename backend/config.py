"""
config.py
---------
WHAT: Central place that reads configuration from environment variables.
WHY:  Secrets (API keys, DB location, JWT signing key) must never be
      hardcoded in source files, because source files end up on GitHub.
      Anyone reading your repo should see *names* of settings, never values.
HOW:  python-dotenv loads a local .env file (which is git-ignored) into
      the process environment when running locally. In production, the
      real host (e.g. Render/Railway/a VM) sets these as real env vars,
      and .env is not needed at all.
"""
import os
from dotenv import load_dotenv

load_dotenv()  # reads .env in the current directory, if present


class Config:
    # Flask's own secret, used to sign session cookies (we don't use
    # cookie sessions for API auth, but Flask wants one set anyway).
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")

    # Signing key for our JWTs (see utils/auth_utils.py). This is
    # DIFFERENT from SECRET_KEY conceptually even if the value overlaps.
    JWT_SECRET = os.environ.get("JWT_SECRET", "dev-only-change-me-too")
    JWT_EXPIRY_MINUTES = int(os.environ.get("JWT_EXPIRY_MINUTES", "120"))

    # SQLite for development (zero setup, a single file). The code uses
    # SQLAlchemy, so switching to Postgres later is a one-line change:
    # DATABASE_URL=postgresql://user:pass@host/dbname
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or (
    "sqlite:///" + os.path.join(os.path.dirname(__file__), "cardiosense.db"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
