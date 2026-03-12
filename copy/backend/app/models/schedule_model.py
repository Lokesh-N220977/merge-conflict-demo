from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any, List, Tuple
from bson import ObjectId
from app.database import database

_VALID_DAYS = {"monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"}

# --- Pydantic Schemas ---

class ScheduleSet(BaseModel):
    """Payload for creating or updating a doctor's schedule."""
    doctor_id: str
    working_days: List[str]
    start_time: str        # "HH:MM" 24-hr
    end_time: str          # "HH:MM" 24-hr
    slot_duration: int     # minutes, e.g. 30
    break_start: Optional[str] = None   # "HH:MM" or None
    break_end: Optional[str] = None     # "HH:MM" or None

    @field_validator("working_days")
    @classmethod
    def validate_days(cls, days: List[str]) -> List[str]:
        normalised = [d.strip().lower() for d in days]
        invalid = [d for d in normalised if d not in _VALID_DAYS]
        if invalid:
            raise ValueError(f"Invalid day(s): {invalid}. Must be full English day names.")
        return normalised

    @field_validator("slot_duration")
    @classmethod
    def validate_duration(cls, v: int) -> int:
        if v <= 0 or v > 480:
            raise ValueError("slot_duration must be between 1 and 480 minutes.")
        return v


class ScheduleResponse(BaseModel):
    """Public representation of a stored schedule."""
    id: str
    doctor_id: str
    working_days: List[str]
    start_time: str
    end_time: str
    slot_duration: int
    break_start: Optional[str] = None
    break_end: Optional[str] = None


# --- MongoDB Model ---

class ScheduleModel:

    @staticmethod
    def upsert(doctor_id: str, schedule_data: Dict[str, Any]) -> str:
        """
        Insert or replace the schedule for a doctor.
        Only one schedule document per doctor is kept.
        Returns the document _id as a string.
        """
        result = database.schedules.find_one_and_replace(
            {"doctor_id": doctor_id},
            schedule_data,
            upsert=True,
            return_document=True,    # return the document AFTER the operation
        )
        # find_one_and_replace with return_document=True returns the updated doc
        return str(result["_id"])

    @staticmethod
    def get_by_doctor(doctor_id: str) -> Optional[Dict[str, Any]]:
        doc = database.schedules.find_one({"doctor_id": doctor_id})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    @staticmethod
    def delete_by_doctor(doctor_id: str) -> bool:
        result = database.schedules.delete_one({"doctor_id": doctor_id})
        return result.deleted_count > 0
