from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any, List
from bson import ObjectId
from app.database import database
from datetime import datetime
import re

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# --- Pydantic Schemas ---

class AppointmentCreate(BaseModel):
    """Legacy schema — kept for backward compatibility."""
    department: str
    doctor_id: str
    appointment_date: str
    appointment_time: str


class AppointmentBook(BaseModel):
    """Schema for the new POST /appointments/book endpoint."""
    doctor_id: str
    date: str        # YYYY-MM-DD
    time: str        # e.g. "09:30 AM"
    reason: Optional[str] = None
    department: Optional[str] = None

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        if not _DATE_RE.match(v):
            raise ValueError("date must be in YYYY-MM-DD format")
        return v


# --- MongoDB Model ---

class AppointmentModel:

    @staticmethod
    def create(data: Dict[str, Any]) -> str:
        result = database.appointments.insert_one(data)
        return str(result.inserted_id)

    @staticmethod
    def get_by_id(appointment_id: str) -> Optional[Dict[str, Any]]:
        try:
            doc = database.appointments.find_one({"_id": ObjectId(appointment_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
            return doc
        except Exception:
            return None

    @staticmethod
    def get_by_user(user_id: str) -> List[Dict[str, Any]]:
        appointments = []
        for app in database.appointments.find({"user_id": user_id}).sort("appointment_date", -1):
            app["_id"] = str(app["_id"])
            appointments.append(app)
        return appointments

    @staticmethod
    def get_upcoming_by_patient(user_id: str) -> List[Dict[str, Any]]:
        """Return future (today onwards) non-cancelled appointments for a patient."""
        today = datetime.now().strftime("%Y-%m-%d")
        appointments = []
        cursor = database.appointments.find({
            "user_id": user_id,
            "appointment_date": {"$gte": today},
            "status": {"$ne": "cancelled"},
        }).sort("appointment_date", 1)
        for app in cursor:
            app["_id"] = str(app["_id"])
            appointments.append(app)
        return appointments

    @staticmethod
    def get_by_doctor(doctor_id: str) -> List[Dict[str, Any]]:
        appointments = []
        for app in database.appointments.find({"doctor_id": doctor_id}).sort("appointment_date", -1):
            app["_id"] = str(app["_id"])
            appointments.append(app)
        return appointments

    @staticmethod
    def get_history(user_id: str) -> List[Dict[str, Any]]:
        appointments = []
        for app in database.appointments.find({"user_id": user_id, "status": "completed"}):
            app["_id"] = str(app["_id"])
            appointments.append(app)
        return appointments

    @staticmethod
    def find_one(query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return database.appointments.find_one(query)

    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        appointments = []
        for app in database.appointments.find():
            app["_id"] = str(app["_id"])
            appointments.append(app)
        return appointments

    @staticmethod
    def get_by_doctor_today(doctor_id: str) -> List[Dict[str, Any]]:
        """Return all non-cancelled appointments for a doctor on today's date."""
        today = datetime.now().strftime("%Y-%m-%d")
        rows = list(database.appointments.find({
            "doctor_id": doctor_id,
            "appointment_date": today,
            "status": {"$ne": "cancelled"},
        }).sort("appointment_time", 1))
        for row in rows:
            row["_id"] = str(row["_id"])
        return rows

    @staticmethod
    def get_by_doctor_date(doctor_id: str, date: str) -> List[Dict[str, Any]]:
        return list(database.appointments.find({
            "doctor_id": doctor_id,
            "appointment_date": date,
            "status": {"$ne": "cancelled"},
        }).limit(100))

    @staticmethod
    def update_status(appointment_id: str, status: str) -> bool:
        """Update the status field of an appointment. Returns True on success."""
        try:
            result = database.appointments.update_one(
                {"_id": ObjectId(appointment_id)},
                {"$set": {"status": status}},
            )
            return result.matched_count > 0
        except Exception:
            return False

    @staticmethod
    def aggregate_bookings(pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return list(database.appointments.aggregate(pipeline))

    @staticmethod
    def delete(appointment_id: str, user_id: Optional[str] = None) -> bool:
        query: Dict[str, Any] = {"_id": ObjectId(appointment_id)}
        if user_id:
            query["user_id"] = user_id
        try:
            result = database.appointments.delete_one(query)
            return result.deleted_count > 0
        except Exception:
            return False
