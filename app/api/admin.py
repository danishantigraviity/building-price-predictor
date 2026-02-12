from flask import Blueprint, jsonify
from ..models import User, Prediction, Estimation
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db

admin_bp = Blueprint('admin_api', __name__)

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def stats():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or not user.is_admin:
        return jsonify({"msg": "Admin access required"}), 403

    total_users = User.query.count()
    total_predictions = Prediction.query.count()
    total_estimations = Estimation.query.count()
    
    # Recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_users_data = [{"id": u.id, "username": u.username, "email": u.email, "joined": u.created_at.strftime('%Y-%m-%d')} for u in recent_users]

    return jsonify({
        "total_users": total_users,
        "total_predictions": total_predictions,
        "total_estimations": total_estimations,
        "recent_users": recent_users_data
    }), 200

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user.is_admin:
        return jsonify({"msg": "Admin access required"}), 403
        
    users = User.query.all()
    return jsonify([{"id": u.id, "username": u.username, "email": u.email, "is_admin": u.is_admin} for u in users]), 200
