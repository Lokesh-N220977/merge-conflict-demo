from models.doctor_model import DoctorModel
from models.user_model import UserModel
from models.appointment_model import AppointmentModel
from models.patient_model import PatientModel
from utils.auth_utils import get_password_hash

class AdminService:
    
    @staticmethod
    def add_doctor(data: dict):
        required_fields = ["name", "email", "password", "specialty", "experience"]
        for field in required_fields:
            if not data.get(field):
                return None, f"Missing required field: {field}"

        # 1. Check if email exists in users
        existing_user = UserModel.find({"email": data.get("email")})
        if existing_user:
            return None, "Email already registered"

        # 2. Create user account for doctor
        hashed_password = get_password_hash(data.get("password"))
        user_data = {
            "name": data.get("name"),
            "email": data.get("email"),
            "password": hashed_password,
            "role": "doctor",
            "isActive": True
        }
        
        user_id = UserModel.create(user_data)

        # 3. Create doctor profile
        doctor_data = {
            "user_id": user_id,
            "name": data.get("name"),
            "email": data.get("email"),
            "specialty": data.get("specialty"),
            "experience": data.get("experience"),
            "about": data.get("about", ""),
            "fees": data.get("fees", 0)
        }
        
        doctor_id = DoctorModel.create(doctor_data)
        
        return doctor_id, None

    @staticmethod
    def remove_doctor(doctor_id: str):
        try:
            doc = DoctorModel.find_by_id(doctor_id)
            if not doc:
                return False, "Doctor not found"
                
            # Remove from doctors collection
            DoctorModel.delete(doctor_id)
            
            # Remove corresponding user account
            if doc.get("user_id"):
                UserModel.delete(str(doc.get("user_id")))
                
            return True, None
        except Exception:
            return False, "Error removing doctor"

    @staticmethod
    def get_all_appointments():
        try:
            appointments = AppointmentModel.find()
            return appointments, None
        except Exception:
            return None, "Error fetching appointments"

    @staticmethod
    def get_dashboard_stats():
        try:
            # Simple count stats; in production we'd use MongoDB aggregations
            doctors_count = len(DoctorModel.find())
            patients_count = len(PatientModel.find())
            appointments_count = len(AppointmentModel.find())
            
            # Revenue calculation (assuming an amount field exists)
            # Or deriving from completed appointments
            appointments = AppointmentModel.find()
            revenue = sum([apt.get("amount", 0) for apt in appointments if apt.get("status") == "completed"])
            
            stats = {
                "total_doctors": doctors_count,
                "total_patients": patients_count,
                "total_appointments": appointments_count,
                "revenue": revenue
            }
            return stats, None
            
        except Exception as e:
            return None, "Error calculating stats"
