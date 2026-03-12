from flask import Blueprint, request, jsonify
from services.appointment_service import AppointmentService

appointment_bp = Blueprint('appointment', __name__)

@appointment_bp.route('/api/appointments/book', methods=['POST'])
def book_appointment():
    # In a real app, authorize user
    data = request.get_json()
    appointment_id, error = AppointmentService.book_appointment(data)
    
    if error:
        return jsonify({"message": error}), 400
        
    return jsonify({"message": "Appointment booked successfully", "appointment_id": appointment_id}), 201

@appointment_bp.route('/api/appointments/patient/<patient_id>', methods=['GET'])
def get_patient_appointments(patient_id):
    appointments, error = AppointmentService.get_patient_appointments(patient_id)
    if error:
        return jsonify({"message": error}), 500
    return jsonify(appointments), 200

@appointment_bp.route('/api/appointments/doctor/<doctor_id>', methods=['GET'])
def get_doctor_appointments(doctor_id):
    appointments, error = AppointmentService.get_doctor_appointments(doctor_id)
    if error:
        return jsonify({"message": error}), 500
    return jsonify(appointments), 200

@appointment_bp.route('/api/appointments/cancel', methods=['POST'])
def cancel_appointment():
    data = request.get_json()
    if not data or not data.get("appointment_id"):
        return jsonify({"message": "Missing appointment_id"}), 400
        
    success, error = AppointmentService.cancel_appointment(data.get("appointment_id"))
    
    if error:
        return jsonify({"message": error}), 400
        
    return jsonify({"message": "Appointment cancelled successfully"}), 200
    
@appointment_bp.route('/api/appointments/confirm', methods=['POST'])
def confirm_appointment():
    # Typically only doctors or admins can confirm
    data = request.get_json()
    if not data or not data.get("appointment_id"):
        return jsonify({"message": "Missing appointment_id"}), 400
        
    success, error = AppointmentService.confirm_appointment(data.get("appointment_id"))
    
    if error:
        return jsonify({"message": error}), 400
        
    return jsonify({"message": "Appointment confirmed successfully"}), 200

@appointment_bp.route('/api/appointments/reschedule', methods=['POST'])
def reschedule_appointment():
    data = request.get_json()
    success, error = AppointmentService.reschedule_appointment(data)
    
    if error:
        return jsonify({"message": error}), 400
        
    return jsonify({"message": "Appointment rescheduled successfully"}), 200
