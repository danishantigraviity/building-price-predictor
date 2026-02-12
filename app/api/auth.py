from flask import Blueprint, request, jsonify
from .. import db, bcrypt
from ..models import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..utils import send_email

auth_bp = Blueprint('auth_api', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "No input data provided"}), 400
        
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({"msg": "Missing requirements"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "Username taken"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email taken"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(username=username, email=email, password=hashed_password)
    db.session.add(user)
    db.session.commit()
    
    # Send Welcome Email
    try:
        send_email("Welcome to Civil Estimator", user.email, 
                   body=f"Hi {user.username},\n\nWelcome to Civil Material Estimator! We are glad to have you.\n\nBest Regards,\nTeam")
    except Exception as e:
        print(f"Email failed: {e}")

    access_token = create_access_token(identity=str(user.id))
    return jsonify(access_token=access_token, user={"id": user.id, "username": user.username, "email": user.email, "is_admin": user.is_admin}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=str(user.id))
        
        # Send Login Notification
        try:
            send_email("Login Notification", user.email, 
                       body=f"Hi {user.username},\n\nYou just logged in via API. If this wasn't you, contact support.")
        except:
            pass
            
        return jsonify(access_token=access_token, user={"id": user.id, "username": user.username, "email": user.email, "is_admin": user.is_admin}), 200
    
    return jsonify({"msg": "Bad username or password"}), 401

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    return jsonify(id=user.id, username=user.username, email=user.email, is_admin=user.is_admin), 200
@auth_bp.route('/update', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    data = request.get_json()
    new_username = data.get('username')
    new_email = data.get('email')
    
    if new_username:
        user.username = new_username
    if new_email:
        # Check if email taken by another user
        existing = User.query.filter_by(email=new_email).first()
        if existing and existing.id != user.id:
            return jsonify({"msg": "Email already in use"}), 400
        user.email = new_email
        
    db.session.commit()
    return jsonify({"msg": "Profile updated", "user": {"id": user.id, "username": user.username, "email": user.email, "is_admin": user.is_admin}}), 200

