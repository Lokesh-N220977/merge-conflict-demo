from flask import Blueprint, request, jsonify
from services.auth_service import AuthService
from utils.auth_utils import decode_access_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password") or not data.get("name"):
        return jsonify({"message": "Missing required fields"}), 400

    user_id, error = AuthService.register_user(data)
    
    if error:
        return jsonify({"message": error}), 400
        
    return jsonify({"message": "User registered successfully", "user_id": user_id}), 201

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"message": "Email and password are required"}), 400
        
    auth_data, error = AuthService.login_user(data.get("email"), data.get("password"))
    
    if error:
        return jsonify({"message": error}), 401
        
    return jsonify(auth_data), 200

@auth_bp.route('/api/profile', methods=['GET'])
def profile():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"message": "Missing or invalid authorization token"}), 401
        
    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)
    
    if not payload or not payload.get("sub"):
        return jsonify({"message": "Invalid or expired token"}), 401
        
    user_id = payload.get("sub")
    user, error = AuthService.get_user_profile(user_id)
    
    if error:
        return jsonify({"message": error}), 404
        
    return jsonify(user), 200
