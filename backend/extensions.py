"""
extensions.py
-------------
WHAT: Holds the single SQLAlchemy `db` object.
WHY:  Flask apps commonly hit circular-import problems if each model file
      creates its own `db = SQLAlchemy()`. Instead, one shared instance is
      created here with no app attached yet, and every model/route file
      imports THIS object. `db.init_app(app)` (in app.py) binds it to the
      real Flask app at startup. This is the standard Flask "app factory"
      pattern.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address)