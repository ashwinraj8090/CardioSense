
from flask import Blueprint, request, jsonify, g

from models.session import MonitoringSession
from models.prediction import RiskPrediction
from utils.auth_utils import login_required

predictions_bp = Blueprint("predictions", __name__, url_prefix="/api/predictions")


@predictions_bp.route("/history", methods=["GET"])
@login_required
def prediction_history():
    limit = min(int(request.args.get("limit", 100)), 500)
    session_ids = [
        s.id for s in MonitoringSession.query.filter_by(user_id=g.current_user.id).all()
    ]
    predictions = (
        RiskPrediction.query.filter(RiskPrediction.session_id.in_(session_ids))
        .order_by(RiskPrediction.timestamp.desc())
        .limit(limit)
        .all()
    )
    return jsonify([p.to_public_dict() for p in reversed(predictions)]), 200
