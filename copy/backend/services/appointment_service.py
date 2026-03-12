from models.appointment_model import AppointmentModel
from services.slot_service import SlotService

class AppointmentService:
    
    @staticmethod
    def book_appointment(data: dict):
        required_fields = ["patient_id", "doctor_id", "date", "time"]
        for field in required_fields:
            if not data.get(field):
                return None, f"Missing required field: {field}"

        # To prevent double booking, we should verify the slot is available
        # using the dynamic generation we previously built
        slots_data = SlotService.generate_slots(data.get("doctor_id"), data.get("date"))
        if "error" in slots_data:
            return None, slots_data["error"]
            
        available_slots = slots_data.get("slots", [])
        if data.get("time") not in available_slots:
            return None, "Slot is no longer available"

        # Default status for a new appointment
        data["status"] = "pending"
        
        appointment_id = AppointmentModel.create(data)
        return appointment_id, None

    @staticmethod
    def get_patient_appointments(patient_id: str):
        try:
            appointments = AppointmentModel.find({"patient_id": patient_id})
            return appointments, None
        except Exception:
            return None, "Error fetching appointments"

    @staticmethod
    def get_doctor_appointments(doctor_id: str):
        try:
            appointments = AppointmentModel.find({"doctor_id": doctor_id})
            return appointments, None
        except Exception:
            return None, "Error fetching appointments"

    @staticmethod
    def cancel_appointment(appointment_id: str):
        try:
            apt = AppointmentModel.find_by_id(appointment_id)
            if not apt:
                return False, "Appointment not found"
                
            if apt.get("status") == "cancelled":
                return False, "Appointment is already cancelled"
                
            success = AppointmentModel.update(appointment_id, {"status": "cancelled"})
            if success:
                return True, None
            return False, "Failed to cancel appointment"
        except Exception:
            return False, "Error processing request"

    @staticmethod
    def confirm_appointment(appointment_id: str):
        try:
            apt = AppointmentModel.find_by_id(appointment_id)
            if not apt:
                return False, "Appointment not found"
                
            if apt.get("status") == "cancelled":
                return False, "Cannot confirm a cancelled appointment"
                
            success = AppointmentModel.update(appointment_id, {"status": "confirmed"})
            if success:
                return True, None
            return False, "Failed to confirm appointment"
        except Exception:
            return False, "Error processing request"

    @staticmethod
    def reschedule_appointment(data: dict):
        appointment_id = data.get("appointment_id")
        new_date = data.get("date")
        new_time = data.get("time")
        
        if not appointment_id or not new_date or not new_time:
            return False, "Missing appointment_id, date, or time"
            
        try:
            apt = AppointmentModel.find_by_id(appointment_id)
            if not apt:
                return False, "Appointment not found"
                
            if apt.get("status") == "cancelled":
                return False, "Cannot reschedule a cancelled appointment"

            # Check if new slot is available
            slots_data = SlotService.generate_slots(apt.get("doctor_id"), new_date)
            if "error" in slots_data:
                return False, slots_data["error"]
                
            available_slots = slots_data.get("slots", [])
            if new_time not in available_slots:
                return False, "New slot is not available"

            # Update appointment
            update_data = {
                "date": new_date,
                "time": new_time,
                "status": "rescheduled"
            }
            
            success = AppointmentModel.update(appointment_id, update_data)
            if success:
                return True, None
            return False, "Failed to reschedule appointment"
            
        except Exception:
            return False, "Error processing request"
