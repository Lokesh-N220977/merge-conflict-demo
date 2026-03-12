from flask import Blueprint, request, jsonify
from services.admin_service import AdminService
from utils.auth_utils import decode_access_token

admin_bp = Blueprint('admin', __name__)

def verify_admin(req):
    """Helper to verify if the requester is an admin."""
    auth_header = req.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return False, "Missing or invalid authorization token"
        
    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        return False, "Invalid token"
        
    if payload.get("role") != "admin":
        return False, "Unauthorized access. Admin privileges required."
        
    return True, None

@admin_bp.route('/api/admin/add-doctor', methods=['POST'])
def add_doctor():
    is_admin, error = verify_admin(request)
    if not is_admin:
        return jsonify({"message": error}), 403
        
    data = request.get_json()
    doctor_id, error = AdminService.add_doctor(data)
    
    if error:
        return jsonify({"message": error}), 400
        
    return jsonify({"message": "Doctor added successfully", "doctor_id": doctor_id}), 201

@admin_bp.route('/api/admin/remove-doctor', methods=['DELETE'])
def remove_doctor():
    is_admin, error = verify_admin(request)
    if not is_admin:
        return jsonify({"message": error}), 403
        
    data = request.get_json()
    if not data or not data.get("doctor_id"):
        return jsonify({"message": "Missing doctor_id"}), 400
        
    success, error = AdminService.remove_doctor(data.get("doctor_id"))
    
    if error:
        return jsonify({"message": error}), 400
        
    return jsonify({"message": "Doctor removed successfully"}), 200

@admin_bp.route('/api/admin/all-appointments', methods=['GET'])
def get_all_appointments():
    is_admin, error = verify_admin(request)
    if not is_admin:
        return jsonify({"message": error}), 403
        
    appointments, error = AdminService.get_all_appointments()
    
    if error:
        return jsonify({"message": error}), 500
        
    return jsonify(appointments), 200

@admin_bp.route('/api/admin/dashboard-stats', methods=['GET'])
def get_dashboard_stats():
    is_admin, error = verify_admin(request)
    if not is_admin:
        return jsonify({"message": error}), 403
        
    stats, error = AdminService.get_dashboard_stats()
    
    if error:
        return jsonify({"message": error}), 500
        
    return jsonify(stats), 200
