
from datetime import datetime
from flask import Blueprint, request, jsonify, g

from extensions import db
from models.user import User
from utils.auth_utils import hash_password, verify_password, issue_jwt, login_required
from extensions import db, limiter   # add limiter to this existing import



auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    dob_str = data.get("dob")
    height_cm = data.get("height_cm")
    weight_kg = data.get("weight_kg")

    # --- Validation (Part 27) ---
    if not username or len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 422
    if not password or len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 422
    if not dob_str:
        return jsonify({"error": "Date of birth is required"}), 422
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "dob must be in YYYY-MM-DD format"}), 422
    try:
        height_cm = float(height_cm)
        weight_kg = float(weight_kg)
    except (TypeError, ValueError):
        return jsonify({"error": "height_cm and weight_kg must be numbers"}), 422
    if not (100 <= height_cm <= 250):
        return jsonify({"error": "height_cm out of realistic range (100-250)"}), 422
    if not (25 <= weight_kg <= 300):
        return jsonify({"error": "weight_kg out of realistic range (25-300)"}), 422

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 409

    user = User(
        username=username,
        password_hash=hash_password(password),
        dob=dob,
        height_cm=height_cm,
        weight_kg=weight_kg,
    )
    db.session.add(user)
    db.session.commit()

    token = issue_jwt(user.id)
    return jsonify({"token": token, "user": user.to_public_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    user = User.query.filter_by(username=username).first()

    if user is None or not verify_password(password, user.password_hash):
        return jsonify({"error": "Invalid username or password"}), 401

    token = issue_jwt(user.id)
    return jsonify({"token": token, "user": user.to_public_dict()}), 200


@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    return jsonify(g.current_user.to_public_dict()), 200
