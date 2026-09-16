"""
utils/auth_utils.py
--------------------
WHAT is authentication vs authorization (asked for explicitly):
  AUTHENTICATION = "Who are you?"   -> proven by: correct password at login
  AUTHORIZATION  = "What are you allowed to see?" -> proven by: your user_id
                    matching the owner of the row you're asking for

This file implements both halves used throughout the app:

1. PASSWORD HASHING
   We use werkzeug.security (already a Flask dependency, no new library
   needed). `generate_password_hash` applies a slow, salted hash
   (PBKDF2-SHA256 by default). "Salted" means a random value is mixed in
   per-user, so two users with the same password get different hashes,
   and "slow" means brute-forcing many guesses is expensive. We NEVER
   store or compare raw passwords.

2. JWT (JSON Web Token)
   WHAT: A JWT is a signed, self-contained token. It looks like
         xxxxx.yyyyy.zzzzz -- header.payload.signature. The payload
         carries claims we choose, e.g. {"user_id": 7, "exp": ...}.
   WHY:  After login, the frontend needs proof of identity to attach to
         every future request, without re-sending the password each time.
         Flask itself is stateless per-request; the server doesn't
         remember who's logged in between requests unless something
         carries that identity. Two common options: server-side sessions
         (server keeps a session table/cookie) or JWT (server signs a
         token, keeps NO record of it, and just re-verifies the signature
         on each request). JWT is used here because it needs no extra
         session storage/table, and it's the same mechanism you'll be
         asked about by name in almost any backend interview.
   HOW:  We sign the payload with JWT_SECRET (config.py). Only someone
         who knows that secret (i.e. our server) could have produced a
         signature that verifies correctly. A client can *read* the
         payload (JWTs are base64, not encrypted) but cannot forge a new
         one without the secret -- so we never put secrets IN the
         payload, only non-sensitive identifiers like user_id.
   WHERE: Issued in routes/auth.py on login. Verified by the
          @login_required decorator below, used on every protected route.
"""
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
