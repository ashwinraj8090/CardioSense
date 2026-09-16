
import jwt
import datetime
from functools import wraps
from flask import request, jsonify, g, current_app
from werkzeug.security import generate_password_hash, check_password_hash

from models.user import User


def hash_password(raw_password: str) -> str:
    return generate_password_hash(raw_password)


def verify_password(raw_password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, raw_password)


def issue_jwt(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow()
        + datetime.timedelta(minutes=current_app.config["JWT_EXPIRY_MINUTES"]),
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm="HS256")


def decode_jwt(token: str):
    """Returns the payload dict, or raises jwt exceptions on invalid/expired token."""
    return jwt.decode(token, current_app.config["JWT_SECRET"], algorithms=["HS256"])


def login_required(fn):
    """
    Route decorator: pulls 'Authorization: Bearer <token>' from the
    request, verifies it, loads the User row, and attaches it to
    flask.g.current_user so the route handler can use it. This is the
    ONLY place a request's identity is established -- routes never trust
    a user_id/username sent in the request body.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or malformed Authorization header"}), 401

        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_jwt(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Session expired, please log in again"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid authentication token"}), 401

        user = User.query.get(payload["user_id"])
        if user is None:
            return jsonify({"error": "User no longer exists"}), 401

        g.current_user = user
        return fn(*args, **kwargs)

    return wrapper
