from flask import Blueprint, request, jsonify
from services.doctor_service import DoctorService
from utils.auth_utils import decode_access_token

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/api/doctors', methods=['GET'])
def get_doctors():
    doctors, error = DoctorService.get_all_doctors()
    if error:
        return jsonify({"message": error}), 500
    return jsonify(doctors), 200

@doctor_bp.route('/api/doctor/<doctor_id>', methods=['GET'])
def get_doctor(doctor_id):
    doctor, error = DoctorService.get_doctor_by_id(doctor_id)
    if error:
        return jsonify({"message": error}), 404
    return jsonify(doctor), 200

@doctor_bp.route('/api/doctor/<doctor_id>/schedule', methods=['GET'])
def get_schedule(doctor_id):
    schedule, error = DoctorService.get_doctor_schedule(doctor_id)
    if error:
        return jsonify({"message": error}), 400
    return jsonify(schedule), 200

@doctor_bp.route('/api/doctor/set-schedule', methods=['POST'])
def set_schedule():
    # Only authenticated users should set schedule (ideally check if they are the doctor)
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"message": "Missing or invalid authorization token"}), 401
        
    data = request.get_json()
    schedule_id, error = DoctorService.set_doctor_schedule(data)
    
    if error:
        return jsonify({"message": error}), 400
        
    return jsonify({"message": "Schedule set successfully", "schedule_id": schedule_id}), 201

@doctor_bp.route('/api/doctor/set-leave', methods=['POST'])
def set_leave():
    # Authentication required
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"message": "Missing or invalid authorization token"}), 401
        
    data = request.get_json()
    leave_id, error = DoctorService.set_doctor_leave(data)
    
    if error:
        return jsonify({"message": error}), 400
        
    return jsonify({"message": "Leave set successfully", "leave_id": leave_id}), 201

@doctor_bp.route('/api/doctor/today-appointments', methods=['GET'])
def get_today_appointments():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"message": "Missing or invalid authorization token"}), 401
        
    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        return jsonify({"message": "Invalid token"}), 401
        
    doctor_id = payload.get("sub")
    appointments, error = DoctorService.get_today_appointments(doctor_id)
    
    if error:
        return jsonify({"message": error}), 500
    return jsonify(appointments), 200

@doctor_bp.route('/api/doctor/upcoming-appointments', methods=['GET'])
def get_upcoming_appointments():
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"message": "Missing or invalid authorization token"}), 401
        
    token = auth_header.split(" ")[1]
    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        return jsonify({"message": "Invalid token"}), 401
        
    doctor_id = payload.get("sub")
    appointments, error = DoctorService.get_upcoming_appointments(doctor_id)
    
    if error:
        return jsonify({"message": error}), 500
    return jsonify(appointments), 200

@doctor_bp.route('/api/doctor/confirm-appointment', methods=['POST'])
def confirm_appointment():
    # Verify auth
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"message": "Missing or invalid authorization token"}), 401
        
    data = request.get_json()
    if not data or not data.get("appointment_id"):
        return jsonify({"message": "Missing appointment_id"}), 400
        
    from services.appointment_service import AppointmentService
    success, error = AppointmentService.confirm_appointment(data.get("appointment_id"))
    
    if error:
        return jsonify({"message": error}), 400
        
    return jsonify({"message": "Appointment confirmed successfully"}), 200

@doctor_bp.route('/api/doctor/cancel-appointment', methods=['POST'])
def cancel_appointment():
    # Verify auth
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"message": "Missing or invalid authorization token"}), 401
        
    data = request.get_json()
    if not data or not data.get("appointment_id"):
        return jsonify({"message": "Missing appointment_id"}), 400
        
    from services.appointment_service import AppointmentService
    success, error = AppointmentService.cancel_appointment(data.get("appointment_id"))
    
    if error:
        return jsonify({"message": error}), 400
        
    return jsonify({"message": "Appointment cancelled successfully"}), 200

