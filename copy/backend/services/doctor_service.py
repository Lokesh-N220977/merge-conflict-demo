from models.doctor_model import DoctorModel
from models.schedule_model import ScheduleModel
from models.leave_model import LeaveModel

class DoctorService:
    
    @staticmethod
    def get_all_doctors():
        doctors = DoctorModel.find()
        # Optionally, remove unnecessary fields if needed
        return doctors, None

    @staticmethod
    def get_doctor_by_id(doctor_id: str):
        try:
            doctor = DoctorModel.find_by_id(doctor_id)
            if not doctor:
                return None, "Doctor not found"
            return doctor, None
        except Exception:
            return None, "Invalid doctor ID"

    @staticmethod
    def get_doctor_schedule(doctor_id: str):
        try:
            schedules = ScheduleModel.find({"doctor_id": doctor_id})
            leaves = LeaveModel.find({"doctor_id": doctor_id})
            return {"schedules": schedules, "leaves": leaves}, None
        except Exception:
            return None, "Error fetching schedule"

    @staticmethod
    def set_doctor_schedule(data: dict):
        if not data.get("doctor_id") or not data.get("available_times"):
            return None, "Missing required fields"

        # Typically, a schedule has doctor_id, date, available_times
        # If schedule already exists for this date, we could update it, 
        # but for simplicity, we insert a new one or update an existing one based on doctor_id and date.
        query = {
            "doctor_id": data.get("doctor_id"),
            "date": data.get("date")
        }
        
        # Ensure it exists
        existing = ScheduleModel.find(query)
        if existing:
            # Update existing
            sched_id = str(existing[0]["_id"])
            success = ScheduleModel.update(sched_id, data)
            if success:
                return sched_id, None
            return None, "Failed to update schedule"
        else:
            # Create new
            sched_id = ScheduleModel.create(data)
            return sched_id, None

    @staticmethod
    def set_doctor_leave(data: dict):
        if not data.get("doctor_id") or not data.get("start_date") or not data.get("end_date"):
            return None, "Missing required fields"
            
        leave_id = LeaveModel.create(data)
        return leave_id, None

    @staticmethod
    def get_today_appointments(doctor_id: str):
        from datetime import date
        from models.appointment_model import AppointmentModel
        today = date.today().strftime("%Y-%m-%d")
        
        try:
            appointments = AppointmentModel.find({
                "doctor_id": doctor_id, 
                "date": today
            })
            return appointments, None
        except Exception:
            return None, "Error fetching today's appointments"
            
    @staticmethod
    def get_upcoming_appointments(doctor_id: str):
        from datetime import date
        from models.appointment_model import AppointmentModel
        today = date.today().strftime("%Y-%m-%d")
        
        try:
            # Fetch appointments greater than today
            appointments = AppointmentModel.find({
                "doctor_id": doctor_id, 
                "date": {"$gt": today}
            })
            return appointments, None
        except Exception:
            return None, "Error fetching upcoming appointments"

