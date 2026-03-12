from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any, List
from bson import ObjectId
from app.database import database
import re

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# --- Pydantic Schemas ---

class DoctorLeave(BaseModel):
    doctor_id: str
    leave_date: str   # YYYY-MM-DD
    reason: str

    @field_validator("leave_date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        if not _DATE_RE.match(v):
            raise ValueError("leave_date must be in YYYY-MM-DD format")
        return v


class LeaveResponse(BaseModel):
    id: str
    doctor_id: str
    leave_date: str
    reason: str


# --- MongoDB Model ---

class LeaveModel:

    @staticmethod
    def create(leave_data: Dict[str, Any]) -> str:
        """Insert a new leave record and return its id."""
        result = database.leaves.insert_one(leave_data)
        return str(result.inserted_id)

    @staticmethod
    def get_by_doctor(doctor_id: str) -> List[Dict[str, Any]]:
        """Return all leaves for a doctor, sorted by date ascending."""
        leaves = list(
            database.leaves
            .find({"doctor_id": doctor_id})
            .sort("leave_date", 1)
        )
        for lv in leaves:
            lv["_id"] = str(lv["_id"])
        return leaves

    @staticmethod
    def get_by_doctor_date(doctor_id: str, date: str) -> Optional[Dict[str, Any]]:
        """Check if a leave exists for a specific date (used by slot generation)."""
        return database.leaves.find_one({"doctor_id": doctor_id, "leave_date": date})

    @staticmethod
    def get_by_doctor_month(doctor_id: str, month: str) -> List[Dict[str, Any]]:
        """Return leaves for a doctor in a given month prefix (YYYY-MM)."""
        leaves = list(database.leaves.find({
            "doctor_id": doctor_id,
            "leave_date": {"$regex": f"^{month}"}
        }).limit(31))
        return leaves

    @staticmethod
    def delete(leave_id: str) -> bool:
        try:
            result = database.leaves.delete_one({"_id": ObjectId(leave_id)})
            return result.deleted_count > 0
        except Exception:
            return False
