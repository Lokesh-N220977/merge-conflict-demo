from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from bson import ObjectId
from app.database import database

# Projection: only expose safe, public fields from doctors collection
_PUBLIC_PROJECTION = {
    "password": 0  # exclude sensitive field; all others are included
}

# --- Pydantic Schemas ---
class DoctorCreate(BaseModel):
    name: str
    email: str
    phone: str
    password: str
    specialization: str
    experience: int
    consultation_fee: Optional[float] = None
    available_days: list[str]
    operating_hours: str
    start_time: str = "09:00"
    end_time: str = "17:00"
    slot_duration: int = 30
    break_start: Optional[str] = "13:00"
    break_end: Optional[str] = "14:00"
    profilePic: Optional[str] = None


class DoctorResponse(BaseModel):
    """Typed response schema for public doctor data."""
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    specialization: str
    experience: int
    consultation_fee: Optional[float] = None
    available_days: Optional[List[str]] = None
    operating_hours: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    slot_duration: Optional[int] = None
    break_start: Optional[str] = None
    break_end: Optional[str] = None
    profilePic: Optional[str] = None

# --- MongoDB Model ---
class DoctorModel:
    
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        doctors = []
        for doctor in database.doctors.find({}, _PUBLIC_PROJECTION):
            doctor["_id"] = str(doctor["_id"])
            # Normalise 'fee' -> 'consultation_fee' for legacy seed data
            if "fee" in doctor and "consultation_fee" not in doctor:
                doctor["consultation_fee"] = doctor.pop("fee")
            doctors.append(doctor)
        return doctors

    @staticmethod
    def get_by_id(doctor_id: str) -> Optional[Dict[str, Any]]:
        try:
            doctor = database.doctors.find_one(
                {"_id": ObjectId(doctor_id)}, _PUBLIC_PROJECTION
            )
            if doctor:
                doctor["_id"] = str(doctor["_id"])
                # Normalise 'fee' -> 'consultation_fee' for legacy seed data
                if "fee" in doctor and "consultation_fee" not in doctor:
                    doctor["consultation_fee"] = doctor.pop("fee")
            return doctor
        except Exception:
            return None

    @staticmethod
    def get_by_user_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Find doctor record by their associated user account ID."""
        try:
            doctor = database.doctors.find_one(
                {"user_id": user_id}, _PUBLIC_PROJECTION
            )
            if doctor:
                doctor["_id"] = str(doctor["_id"])
                if "fee" in doctor and "consultation_fee" not in doctor:
                    doctor["consultation_fee"] = doctor.pop("fee")
            return doctor
        except Exception:
            return None

    @staticmethod
    def create(doctor_data: Dict[str, Any]) -> str:
        result = database.doctors.insert_one(doctor_data)
        return str(result.inserted_id)

    @staticmethod
    def delete(doctor_id: str) -> bool:
        try:
            result = database.doctors.delete_one({"_id": ObjectId(doctor_id)})
            return result.deleted_count > 0
        except Exception:
            return False
